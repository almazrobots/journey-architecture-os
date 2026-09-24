"""Rule-by-rule tests for scripts/validate_repo.py.

Each test copies the repository (without examples/) into a temporary root,
installs tests/fixtures/minimal-system as the only journey system, applies
one defect, and asserts that the validator rejects it with a precise message.
"""

import contextlib
import csv
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "minimal-system"
ONTOLOGY = ROOT / "skills" / "journey-architecture" / "references" / "ontology.md"


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_repo", ROOT / "scripts" / "validate_repo.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_validator()

JOURNEY = "JRN-CUST-SAAS-ONBOARD-001"
LIFECYCLE = "LFC-CUST-RELATIONSHIP-001"
STAGE1 = "NOD-CUST-SAAS-ONBOARD-001-01"
STAGE2 = "NOD-CUST-SAAS-ONBOARD-001-02"
EPISODE = "NOD-CUST-SAAS-ONBOARD-001-02-01"
SYS = "examples/minimal-system"


class SandboxTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "repo"
        shutil.copytree(
            ROOT,
            self.root,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", "examples", "tests", "evals", ".agents"
            ),
        )
        (self.root / "examples").mkdir()
        self.system = self.root / SYS
        shutil.copytree(FIXTURE, self.system)

    def tearDown(self):
        self._tmp.cleanup()

    # -- helpers -----------------------------------------------------------

    def run_validator(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = V.main(["--root", str(self.root)])
        return code, buf.getvalue()

    def assertPasses(self):
        code, out = self.run_validator()
        self.assertEqual(code, 0, out)
        self.assertIn("OK:", out)
        return out

    def assertFails(self, *fragments):
        code, out = self.run_validator()
        self.assertEqual(code, 1, out)
        self.assertIn("VALIDATION FAILED\n - ", out)
        for fragment in fragments:
            self.assertIn(fragment, out)
        return out

    def read_csv(self, path):
        with open(path, newline="", encoding="utf-8") as fh:
            return list(csv.reader(fh))

    def write_csv(self, path, rows):
        with open(path, "w", newline="", encoding="utf-8") as fh:
            csv.writer(fh, lineterminator="\n").writerows(rows)

    def set_cell(self, filename, row, column, value, base=None):
        path = (base or self.system) / filename
        rows = self.read_csv(path)
        rows[row + 1][rows[0].index(column)] = value
        self.write_csv(path, rows)

    def append_row(self, filename, values, base=None):
        path = (base or self.system) / filename
        rows = self.read_csv(path)
        rows.append([values.get(col, "") for col in rows[0]])
        self.write_csv(path, rows)

    def edit_text(self, rel, old, new):
        path = self.root / rel
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def append_text(self, rel, extra):
        path = self.root / rel
        path.write_text(path.read_text(encoding="utf-8") + extra, encoding="utf-8")

    def edit_schema(self, name, change):
        path = self.root / "schemas" / f"{name}.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        change(schema)
        path.write_text(json.dumps(schema, indent=2), encoding="utf-8")


class FixtureTests(SandboxTest):
    def test_fixture_passes(self):
        out = self.assertPasses()
        self.assertIn("OK: 15 skills, 13 schemas, 1 journey system validated", out)

    def test_fixture_is_complete(self):
        names = sorted(p.name for p in FIXTURE.glob("*.csv"))
        self.assertEqual(names, sorted(V.REGISTERS.values()))

    def test_command_line_entry_point(self):
        (self.system / "journey-view.md").write_text("MTM-0999\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate_repo.py"),
                "--root",
                str(self.root),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            f"{SYS}/journey-view.md:1: MTM-0999 does not resolve", result.stdout
        )


class RowSchemaTests(SandboxTest):
    def test_bad_id_pattern(self):
        self.set_cell("actor-register.csv", 0, "actor_id", "ACT-cust-01")
        self.assertFails(
            f"{SYS}/actor-register.csv:2: column 'actor_id': 'ACT-cust-01' does not match"
        )

    def test_bad_list_pattern_with_space(self):
        self.set_cell(
            "node-register.csv", 1, "evidence_ids", "EVD-2026-0002; EVD-2026-0003"
        )
        self.assertFails(f"{SYS}/node-register.csv:3: column 'evidence_ids'")

    def test_bad_enum(self):
        self.set_cell("actor-register.csv", 0, "actor_type", "robot")
        self.assertFails(
            f"{SYS}/actor-register.csv:2: column 'actor_type': 'robot' is not one of: customer"
        )

    def test_level_outside_hierarchy_registers(self):
        self.set_cell("journey-registry.csv", 1, "level", "L3")
        self.assertFails(
            f"{SYS}/journey-registry.csv:3: column 'level': 'L3' is not one of: L0, L1, L2"
        )

    def test_missing_required(self):
        self.set_cell("node-register.csv", 0, "name", "")
        self.assertFails(f"{SYS}/node-register.csv:2: required column 'name' is empty")

    def test_bad_date_pattern(self):
        self.set_cell("evidence-register.csv", 0, "collected_at", "14/05/2026")
        self.assertFails(f"{SYS}/evidence-register.csv:2: column 'collected_at'")

    def test_impossible_calendar_date(self):
        self.set_cell("journey-registry.csv", 0, "last_reviewed_at", "2026-02-30")
        self.assertFails(
            f"{SYS}/journey-registry.csv:2: column 'last_reviewed_at': '2026-02-30' is not a calendar date"
        )

    def test_bad_sequence(self):
        self.set_cell("node-register.csv", 0, "sequence", "0")
        self.assertFails(f"{SYS}/node-register.csv:2: column 'sequence'")

    def test_bad_metric_coverage(self):
        self.set_cell("portfolio-register.csv", 1, "metric_coverage", "1.5")
        self.assertFails(f"{SYS}/portfolio-register.csv:3: column 'metric_coverage'")

    def test_valid_metric_coverage_values(self):
        schema = json.loads((self.root / "schemas" / "portfolio.schema.json").read_text(encoding="utf-8"))
        pattern = schema["properties"]["metric_coverage"]["pattern"]
        for value in ("0", "0.75", "1", "1.00", "0.5"):
            self.assertTrue(V.ecma_search(pattern, value), value)
        for value in ("1.5", "0.123", "2", "1\n"):
            self.assertFalse(V.ecma_search(pattern, value), value)

    def test_duplicate_id(self):
        rows = self.read_csv(self.system / "evidence-register.csv")
        rows.append(rows[1])
        self.write_csv(self.system / "evidence-register.csv", rows)
        self.assertFails(
            f"{SYS}/evidence-register.csv:5: duplicate evidence_id EVD-2026-0001 (first on line 2)"
        )

    def test_duplicate_portfolio_entry(self):
        rows = self.read_csv(self.system / "portfolio-register.csv")
        rows.append(rows[2])
        self.write_csv(self.system / "portfolio-register.csv", rows)
        self.assertFails(f"duplicate journey_id {JOURNEY} (first on line 3)")

    def test_wrong_cell_count(self):
        path = self.system / "actor-register.csv"
        path.write_text(
            path.read_text(encoding="utf-8") + "ACT-CUST-OTHER-02,Other,customer\n",
            encoding="utf-8",
        )
        self.assertFails(f"{SYS}/actor-register.csv:3: row has 3 cells, header has 5")

    def test_multiline_cell_reports_start_line(self):
        rows = self.read_csv(self.system / "actor-register.csv")
        rows[1][4] = "line one\nline two"
        rows.append(["ACT-bad", "X", "customer", "", ""])
        self.write_csv(self.system / "actor-register.csv", rows)
        self.assertFails(f"{SYS}/actor-register.csv:4: column 'actor_id'")

    def test_header_drift_in_system_register(self):
        rows = self.read_csv(self.system / "metric-register.csv")
        rows[0][2] = "metric_layer"
        self.write_csv(self.system / "metric-register.csv", rows)
        self.assertFails(
            f"{SYS}/metric-register.csv:1: header does not match schemas/metric.schema.json"
        )

    def test_empty_register_file(self):
        (self.system / "moment-register.csv").write_text("", encoding="utf-8")
        self.assertFails(f"{SYS}/moment-register.csv: empty file")

    def test_unreadable_csv(self):
        (self.system / "actor-register.csv").write_bytes(b"actor_id,name\n\xff\xfe\n")
        self.assertFails(f"{SYS}/actor-register.csv: not UTF-8 (byte 14); save the register as UTF-8")

    def test_unknown_register_file(self):
        (self.system / "touchpoints.csv").write_text("a,b\n", encoding="utf-8")
        self.assertFails(f"{SYS}/touchpoints.csv: unknown register file")

    def test_blank_lines_are_ignored(self):
        path = self.system / "actor-register.csv"
        path.write_text(path.read_text(encoding="utf-8") + "\n\n", encoding="utf-8")
        self.assertPasses()


# (file, row, column, dangling value, expected fragment)
DANGLING = [
    (
        "journey-registry.csv",
        1,
        "parent_id",
        "LFC-CUST-OTHER-001",
        "parent_id LFC-CUST-OTHER-001 is not in journey-registry.csv",
    ),
    (
        "journey-registry.csv",
        0,
        "actor_id",
        "ACT-CUST-GHOST-01",
        "actor_id cites ACT-CUST-GHOST-01, which is not in actor-register.csv",
    ),
    (
        "node-register.csv",
        0,
        "journey_id",
        "JRN-CUST-OTHER-001",
        "journey_id cites JRN-CUST-OTHER-001, which is not in journey-registry.csv",
    ),
    (
        "node-register.csv",
        2,
        "parent_node_id",
        "NOD-CUST-SAAS-ONBOARD-001-03",
        "parent_node_id cites NOD-CUST-SAAS-ONBOARD-001-03, which is not in node-register.csv",
    ),
    (
        "node-register.csv",
        2,
        "evidence_ids",
        "EVD-2026-0003;EVD-2026-0404",
        "evidence_ids cites EVD-2026-0404, which is not in evidence-register.csv",
    ),
    (
        "evidence-register.csv",
        0,
        "journey_id",
        "JRN-CUST-OTHER-001",
        "journey_id cites JRN-CUST-OTHER-001",
    ),
    (
        "evidence-register.csv",
        0,
        "node_id",
        "NOD-CUST-SAAS-ONBOARD-001-09",
        "node_id cites NOD-CUST-SAAS-ONBOARD-001-09, which is not in node-register.csv",
    ),
    (
        "moment-register.csv",
        0,
        "node_id",
        "NOD-CUST-SAAS-ONBOARD-001-09",
        "node_id cites NOD-CUST-SAAS-ONBOARD-001-09",
    ),
    (
        "moment-register.csv",
        0,
        "evidence_ids",
        "EVD-2026-0002;EVD-2026-0404",
        "evidence_ids cites EVD-2026-0404",
    ),
    (
        "moment-register.csv",
        0,
        "metric_ids",
        "MET-0001;MET-0404",
        "metric_ids cites MET-0404, which is not in metric-register.csv",
    ),
    (
        "metric-register.csv",
        0,
        "journey_or_node_id",
        "JRN-CUST-OTHER-001",
        "journey_or_node_id cites JRN-CUST-OTHER-001",
    ),
    (
        "metric-register.csv",
        1,
        "journey_or_node_id",
        "NOD-CUST-SAAS-ONBOARD-001-09",
        "journey_or_node_id cites NOD-CUST-SAAS-ONBOARD-001-09",
    ),
    (
        "opportunity-register.csv",
        0,
        "journey_id",
        "JRN-CUST-OTHER-001",
        "journey_id cites JRN-CUST-OTHER-001",
    ),
    (
        "opportunity-register.csv",
        0,
        "node_id",
        "NOD-CUST-SAAS-ONBOARD-001-09",
        "node_id cites NOD-CUST-SAAS-ONBOARD-001-09",
    ),
    (
        "opportunity-register.csv",
        0,
        "evidence_ids",
        "EVD-2026-0002;EVD-2026-0404",
        "evidence_ids cites EVD-2026-0404",
    ),
    (
        "initiative-register.csv",
        0,
        "opportunity_ids",
        "OPP-0001;OPP-0404",
        "opportunity_ids cites OPP-0404, which is not in opportunity-register.csv",
    ),
    (
        "initiative-register.csv",
        0,
        "expected_metric_ids",
        "MET-0404",
        "expected_metric_ids cites MET-0404",
    ),
    (
        "portfolio-register.csv",
        1,
        "journey_id",
        "JRN-CUST-OTHER-001",
        "journey_id cites JRN-CUST-OTHER-001",
    ),
    (
        "portfolio-register.csv",
        1,
        "parent_id",
        "LFC-CUST-OTHER-001",
        "parent_id cites LFC-CUST-OTHER-001",
    ),
    (
        "portfolio-register.csv",
        1,
        "actor_id",
        "ACT-CUST-GHOST-01",
        "actor_id cites ACT-CUST-GHOST-01",
    ),
    (
        "portfolio-register.csv",
        1,
        "linked_opportunities",
        "OPP-0404",
        "linked_opportunities cites OPP-0404",
    ),
    (
        "portfolio-register.csv",
        1,
        "linked_initiatives",
        "INI-0404",
        "linked_initiatives cites INI-0404, which is not in initiative-register.csv",
    ),
    ("metric-register.csv", 0, "evidence_ids", "EVD-2026-0002;EVD-2026-0404", "evidence_ids cites EVD-2026-0404"),
    ("relation-register.csv", 0, "from_id", "NOD-CUST-SAAS-ONBOARD-001-09", "from_id cites NOD-CUST-SAAS-ONBOARD-001-09, which is not in node-register.csv"),
    ("relation-register.csv", 0, "to_id", "JRN-CUST-OTHER-001", "to_id cites JRN-CUST-OTHER-001, which is not in journey-registry.csv"),
    ("relation-register.csv", 0, "evidence_ids", "EVD-2026-0404", "evidence_ids cites EVD-2026-0404"),
    ("opportunity-register.csv", 0, "moment_ids", "MTM-0404", "moment_ids cites MTM-0404, which is not in moment-register.csv"),
    ("opportunity-register.csv", 0, "metric_ids", "MET-0001;MET-0404", "metric_ids cites MET-0404"),
    ("metric-edge-register.csv", 0, "from_metric_id", "MET-0404", "from_metric_id cites MET-0404"),
    ("metric-edge-register.csv", 0, "to_metric_id", "MET-0404", "to_metric_id cites MET-0404"),
    ("metric-edge-register.csv", 0, "evidence_ids", "EVD-2026-0002;EVD-2026-0404", "evidence_ids cites EVD-2026-0404"),
    ("governance-register.csv", 0, "journey_id", "JRN-CUST-OTHER-001", "journey_id cites JRN-CUST-OTHER-001, which is not in journey-registry.csv"),
    ("change-log.csv", 0, "journey_id", "JRN-CUST-OTHER-001", "journey_id cites JRN-CUST-OTHER-001"),
    ("change-log.csv", 0, "evidence_ids", "EVD-2026-0404", "evidence_ids cites EVD-2026-0404"),
    ("change-log.csv", 0, "affected_node_ids", "NOD-CUST-SAAS-ONBOARD-001-09", "affected_node_ids cites NOD-CUST-SAAS-ONBOARD-001-09"),
]


class ReferentialTests(SandboxTest):
    def test_dangling_references(self):
        for filename, row, column, value, fragment in DANGLING:
            with self.subTest(file=filename, column=column):
                self.tearDown()
                self.setUp()
                self.set_cell(filename, row, column, value)
                self.assertFails(f"{SYS}/{filename}:{row + 2}: {fragment}")

    def test_dangling_list_reports_every_missing_id(self):
        self.set_cell(
            "initiative-register.csv",
            0,
            "opportunity_ids",
            "OPP-0404;OPP-0001;OPP-0405",
        )
        out = self.assertFails("cites OPP-0404", "cites OPP-0405")
        self.assertNotIn("cites OPP-0001", out)

    def test_missing_register_makes_citations_dangle(self):
        (self.system / "metric-register.csv").unlink()
        self.assertFails(
            "metric_ids cites MET-0001, which is not in metric-register.csv"
        )

    def test_prefix_level_coherence(self):
        self.set_cell("journey-registry.csv", 1, "level", "L1")
        self.set_cell("portfolio-register.csv", 1, "level", "L1")
        self.assertFails(
            f"{SYS}/journey-registry.csv:3: {JOURNEY} is a JRN and must be level L2, found L1",
            f"{SYS}/portfolio-register.csv:3: {JOURNEY} is a JRN and must be level L2, found L1",
        )

    def test_parent_level_must_be_lower(self):
        self.append_row(
            "journey-registry.csv",
            {
                "journey_id": "LFC-CUST-NESTED-001",
                "level": "L1",
                "parent_id": LIFECYCLE,
                "name": "Nested lifecycle",
                "state": "current",
                "status": "draft",
            },
        )
        self.assertFails(
            f"{SYS}/journey-registry.csv:4: parent_id {LIFECYCLE} is level L1; a parent must have a lower level number than L1"
        )

    def test_domain_parent_accepted(self):
        self.append_row(
            "journey-registry.csv",
            {
                "journey_id": "DOM-CUSTOMER-RELATIONSHIP-001",
                "level": "L0",
                "name": "Customer relationship",
                "state": "current",
                "status": "active",
            },
        )
        self.set_cell(
            "journey-registry.csv", 0, "parent_id", "DOM-CUSTOMER-RELATIONSHIP-001"
        )
        self.set_cell(
            "portfolio-register.csv", 0, "parent_id", "DOM-CUSTOMER-RELATIONSHIP-001"
        )
        self.assertPasses()

    def test_node_prefix_mismatch(self):
        self.append_row(
            "journey-registry.csv",
            {
                "journey_id": "JRN-CUST-SUPPORT-001",
                "level": "L2",
                "parent_id": LIFECYCLE,
                "name": "Resolve a problem",
                "state": "current",
                "status": "draft",
            },
        )
        self.set_cell("node-register.csv", 0, "journey_id", "JRN-CUST-SUPPORT-001")
        self.assertFails(
            f"{SYS}/node-register.csv:2: node_id {STAGE1} must start with NOD-CUST-SUPPORT-001- (NOD- + key of JRN-CUST-SUPPORT-001)"
        )

    def test_node_prefix_rejects_longer_journey_key(self):
        # Shares a string prefix with the journey key, but names another journey.
        node = "NOD-CUST-SAAS-ONBOARD-V2-001-01"
        self.append_row("node-register.csv", {
            "node_id": node, "journey_id": JOURNEY, "node_type": "stage",
            "sequence": "5", "name": "X", "evidence_status": "unknown",
        })
        self.assertFails(f"{SYS}/node-register.csv:5: node_id {node} must start with NOD-CUST-SAAS-ONBOARD-001-")

    def test_malformed_node_id_is_reported_once(self):
        self.set_cell("node-register.csv", 0, "node_id", "NOD-bad")
        self.set_cell("node-register.csv", 1, "journey_id", "JRN-bad")
        out = self.assertFails(
            f"{SYS}/node-register.csv:2: column 'node_id': 'NOD-bad' does not match",
            f"{SYS}/node-register.csv:3: column 'journey_id': 'JRN-bad' does not match",
        )
        self.assertNotIn("must start with", out)

    def test_stage_node_must_not_have_parent(self):
        self.set_cell("node-register.csv", 1, "parent_node_id", STAGE1)
        self.assertFails(
            f"{SYS}/node-register.csv:3: parent_node_id of {STAGE2} must be empty (stage-level node), found {STAGE1}"
        )

    def test_child_node_parent_must_be_prefix(self):
        self.set_cell("node-register.csv", 2, "parent_node_id", STAGE1)
        self.assertFails(
            f"{SYS}/node-register.csv:4: parent_node_id of {EPISODE} must be {STAGE2}, found {STAGE1}"
        )

    def test_child_node_parent_must_not_be_empty(self):
        self.set_cell("node-register.csv", 2, "parent_node_id", "")
        self.assertFails(f"parent_node_id of {EPISODE} must be {STAGE2}, found empty")

    def test_node_of_other_journey_cited_with_journey(self):
        self.append_row(
            "journey-registry.csv",
            {
                "journey_id": "JRN-CUST-SUPPORT-001",
                "level": "L2",
                "parent_id": LIFECYCLE,
                "name": "Resolve a problem",
                "state": "current",
                "status": "draft",
            },
        )
        self.set_cell("evidence-register.csv", 0, "journey_id", "JRN-CUST-SUPPORT-001")
        self.set_cell(
            "opportunity-register.csv", 0, "journey_id", "JRN-CUST-SUPPORT-001"
        )
        self.assertFails(
            f"{SYS}/evidence-register.csv:2: node_id {STAGE1} belongs to {JOURNEY}, not JRN-CUST-SUPPORT-001",
            f"{SYS}/opportunity-register.csv:2: node_id {STAGE2} belongs to {JOURNEY}, not JRN-CUST-SUPPORT-001",
        )

    def test_portfolio_mirrors_journey_registry(self):
        self.set_cell("portfolio-register.csv", 1, "status", "active")
        self.set_cell("portfolio-register.csv", 0, "actor_id", "")
        self.assertFails(
            f"{SYS}/portfolio-register.csv:3: status of {JOURNEY} is active here but validated in journey-registry.csv",
            f"{SYS}/portfolio-register.csv:2: actor_id of {LIFECYCLE} is empty here but ACT-CUST-SMB-ADMIN-01 in journey-registry.csv",
        )

    def test_portfolio_mirror_every_field(self):
        changes = {"parent_id": "", "state": "target"}
        for column, value in changes.items():
            with self.subTest(column=column):
                self.tearDown()
                self.setUp()
                self.set_cell("portfolio-register.csv", 1, column, value)
                self.assertFails(f"{column} of {JOURNEY} is {value or 'empty'} here")


TARGET = "JRN-CUST-SAAS-ONBOARD-002"


class ContractV2Tests(SandboxTest):
    def add_version(self, state="target", baseline=JOURNEY, **extra):
        values = {
            "journey_id": TARGET, "level": "L2", "parent_id": LIFECYCLE,
            "actor_id": "ACT-CUST-SMB-ADMIN-01", "name": "Start using the service (target)",
            "state": state, "baseline_journey_id": baseline, "status": "draft",
        }
        values.update(extra)
        self.append_row("journey-registry.csv", values)

    # -- slug tokens start with a letter -----------------------------------

    def test_all_numeric_slug_token_rejected(self):
        self.set_cell("actor-register.csv", 0, "actor_id", "ACT-CUST-100-01")
        self.assertFails(f"{SYS}/actor-register.csv:2: column 'actor_id': 'ACT-CUST-100-01' does not match")

    def test_all_numeric_slug_in_view_rejected(self):
        self.append_text(f"{SYS}/journey-view.md", "\nOld JRN-CUST-A-100-001.\n")
        self.assertFails(f"{SYS}/journey-view.md:13: JRN-CUST-A-100-001 does not match the JRN ID grammar")

    def test_slug_grammar(self):
        for prefix, good, bad in (
            ("ACT", "ACT-CUST-V2-01", "ACT-CUST-2V-01"),
            ("DOM", "DOM-CUSTOMER-001", "DOM-2024-001"),
            ("LFC", "LFC-CUST-A1-001", "LFC-CUST-100-001"),
            ("JRN", "JRN-CUST-SAAS-V2-001", "JRN-CUST-A-100-001"),
            ("NOD", "NOD-CUST-SAAS-001-01", "NOD-CUST-A-100-001-01"),
        ):
            self.assertRegex(good, V.ID_PATTERNS[prefix])
            self.assertNotRegex(bad, V.ID_PATTERNS[prefix])

    # -- metrics cite evidence ---------------------------------------------

    def test_observed_metric_needs_observed_evidence(self):
        self.set_cell("metric-register.csv", 0, "evidence_status", "observed")
        self.set_cell("metric-register.csv", 0, "evidence_ids", "EVD-2026-0003")
        self.assertFails(f"{SYS}/metric-register.csv:2: evidence_status is observed but no cited evidence ID is observed")

    def test_observed_metric_with_observed_evidence_passes(self):
        self.set_cell("metric-register.csv", 0, "evidence_status", "observed")
        self.assertPasses()

    # -- journey versions --------------------------------------------------

    def test_target_version_passes(self):
        self.add_version()
        self.add_version(state="transitional", journey_id="JRN-CUST-SAAS-ONBOARD-003")
        self.assertPasses()

    def test_target_requires_baseline(self):
        self.add_version(baseline="")
        self.assertFails(f"{SYS}/journey-registry.csv:4: {TARGET} is target and must name its current journey in baseline_journey_id")

    def test_transitional_requires_baseline(self):
        self.add_version(state="transitional", baseline="")
        self.assertFails(f"{TARGET} is transitional and must name its current journey")

    def test_current_must_not_have_baseline(self):
        self.add_version()
        self.set_cell("journey-registry.csv", 1, "baseline_journey_id", TARGET)
        self.assertFails(
            f"{SYS}/journey-registry.csv:3: baseline_journey_id must be empty for a L2 current entry; only L2 target or transitional journeys name a baseline"
        )

    def test_lifecycle_must_not_have_baseline(self):
        self.set_cell("journey-registry.csv", 0, "state", "target")
        self.set_cell("portfolio-register.csv", 0, "state", "target")
        self.set_cell("journey-registry.csv", 0, "baseline_journey_id", JOURNEY)
        self.assertFails(f"{SYS}/journey-registry.csv:2: baseline_journey_id must be empty for a L1 target entry")

    def test_lifecycle_target_needs_no_baseline(self):
        self.set_cell("journey-registry.csv", 0, "state", "target")
        self.set_cell("portfolio-register.csv", 0, "state", "target")
        self.assertPasses()

    def test_baseline_must_be_current(self):
        self.add_version()
        self.add_version(state="transitional", journey_id="JRN-CUST-SAAS-ONBOARD-003", baseline=TARGET)
        self.assertFails(f"{SYS}/journey-registry.csv:5: baseline_journey_id {TARGET} must be an L2 journey with state current, found L2 target")

    def test_baseline_must_exist(self):
        self.add_version(baseline="JRN-CUST-SAAS-ONBOARD-009")
        out = self.assertFails(f"{SYS}/journey-registry.csv:4: baseline_journey_id cites JRN-CUST-SAAS-ONBOARD-009, which is not in journey-registry.csv")
        self.assertNotIn("must be an L2 journey", out)

    def test_baseline_rules_skip_rows_with_invalid_state(self):
        self.add_version(state="future")
        out = self.assertFails(f"{SYS}/journey-registry.csv:4: column 'state'")
        self.assertNotIn("baseline_journey_id must be empty", out)

    # -- actors ------------------------------------------------------------

    def test_journey_and_lifecycle_need_an_actor(self):
        self.set_cell("journey-registry.csv", 0, "actor_id", "")
        self.set_cell("portfolio-register.csv", 0, "actor_id", "")
        self.assertFails(
            f"{SYS}/journey-registry.csv:2: {LIFECYCLE} must name its actor_id; only DOM rows may leave it empty",
            f"{SYS}/portfolio-register.csv:2: {LIFECYCLE} must name its actor_id",
        )

    # -- metric coverage -----------------------------------------------------

    def test_metric_coverage_must_match_nodes(self):
        self.set_cell("portfolio-register.csv", 1, "metric_coverage", "1")
        self.assertFails(
            f"{SYS}/portfolio-register.csv:3: metric_coverage of {JOURNEY} is 1, but 1 of 2 stage-level nodes have a metric (0.5)"
        )

    def test_metric_on_descendant_covers_stage(self):
        self.set_cell("metric-register.csv", 1, "journey_or_node_id", EPISODE)
        self.assertPasses()

    def test_journey_level_metric_does_not_cover(self):
        self.set_cell("metric-register.csv", 1, "journey_or_node_id", JOURNEY)
        self.assertFails(f"metric_coverage of {JOURNEY} is 0.5, but 0 of 2 stage-level nodes have a metric (0)")
        self.set_cell("portfolio-register.csv", 1, "metric_coverage", "0")
        self.assertPasses()

    def test_metric_on_other_node_prefix_does_not_cover(self):
        # NOD-...-01 must not be counted as covered by a metric on NOD-...-010-like siblings.
        self.set_cell("metric-register.csv", 1, "journey_or_node_id", STAGE1)
        self.set_cell("portfolio-register.csv", 1, "metric_coverage", "0.5")
        self.assertPasses()
        self.set_cell("portfolio-register.csv", 1, "metric_coverage", "1.00")
        self.assertFails("but 1 of 2 stage-level nodes")

    def test_coverage_of_journey_without_nodes_must_be_empty(self):
        self.add_version()
        self.append_row("portfolio-register.csv", {
            "journey_id": TARGET, "parent_id": LIFECYCLE, "level": "L2", "actor_id": "ACT-CUST-SMB-ADMIN-01",
            "name": "Start using the service (target)", "state": "target", "status": "draft",
            "evidence_freshness": "unknown", "metric_coverage": "0.25",
        })
        self.assertFails(f"{SYS}/portfolio-register.csv:4: metric_coverage of {TARGET} must be empty: it has no stage-level nodes")
        self.set_cell("portfolio-register.csv", 2, "metric_coverage", "")
        self.assertPasses()

    # -- relations -----------------------------------------------------------

    def test_observed_relation_needs_observed_evidence(self):
        self.set_cell("relation-register.csv", 1, "evidence_status", "observed")
        self.assertFails(f"{SYS}/relation-register.csv:3: evidence_status is observed but no cited evidence ID is observed")
        self.set_cell("relation-register.csv", 1, "evidence_ids", "EVD-2026-0003;EVD-2026-0001")
        self.assertPasses()

    def test_self_relation(self):
        self.set_cell("relation-register.csv", 0, "to_id", "NOD-CUST-SAAS-ONBOARD-001-02")
        self.assertFails(f"{SYS}/relation-register.csv:2: relation from NOD-CUST-SAAS-ONBOARD-001-02 to itself")

    def test_duplicate_relation(self):
        rows = self.read_csv(self.system / "relation-register.csv")
        rows.append(list(rows[1][:3]) + ["", "hypothesis", "again"])
        self.write_csv(self.system / "relation-register.csv", rows)
        self.assertFails(
            f"{SYS}/relation-register.csv:4: duplicate from_id+relation+to_id NOD-CUST-SAAS-ONBOARD-001-02 depends_on NOD-CUST-SAAS-ONBOARD-001-01 (first on line 2)"
        )

    def test_same_pair_different_relation_passes(self):
        self.append_row("relation-register.csv", {
            "from_id": "NOD-CUST-SAAS-ONBOARD-001-02", "relation": "can_follow",
            "to_id": "NOD-CUST-SAAS-ONBOARD-001-01", "evidence_status": "hypothesis",
        })
        self.assertPasses()

    def test_parent_of_is_not_a_relation(self):
        self.set_cell("relation-register.csv", 0, "relation", "parent_of")
        self.assertFails(f"{SYS}/relation-register.csv:2: column 'relation': 'parent_of' is not one of: precedes")

    def test_relation_endpoints_are_hierarchy_or_nodes(self):
        self.set_cell("relation-register.csv", 0, "to_id", "MET-0001")
        self.assertFails(f"{SYS}/relation-register.csv:2: column 'to_id': 'MET-0001' does not match")

    def test_relation_key_columns_required(self):
        self.edit_schema("relation", lambda s: s["required"].remove("relation"))
        self.assertFails("schemas/relation.schema.json: primary key 'relation' must be required")

    def test_ontology_level_note_is_not_a_value(self):
        onto = V.parse_ontology((self.root / V.ONTOLOGY_PATH).read_text(encoding="utf-8"))
        self.assertEqual(onto["enums"]["level"], ["L0", "L1", "L2", "L3", "L4"])
        self.assertIn("metric_coverage", onto["enums"])
        self.assertIn("relation", onto["enums"])


OTHER = "JRN-CUST-SUPPORT-001"
CONVENTIONS = "skills/journey-metrics/references/conventions.md"


class ContractV3Tests(SandboxTest):
    def add_other_journey(self):
        self.append_row("journey-registry.csv", {
            "journey_id": OTHER, "level": "L2", "parent_id": LIFECYCLE, "actor_id": "ACT-CUST-SMB-ADMIN-01",
            "name": "Resolve a problem", "state": "current", "status": "draft",
        })

    def add_metric(self, metric_id, target, layer, **extra):
        values = {"metric_id": metric_id, "journey_or_node_id": target, "layer": layer,
                  "name": "M", "definition": "D", "direction": "increase", "evidence_status": "unknown"}
        values.update(extra)
        self.append_row("metric-register.csv", values)

    def add_edge(self, source, relation, target, **extra):
        values = {"from_metric_id": source, "relation": relation, "to_metric_id": target,
                  "evidence_status": "hypothesis"}
        values.update(extra)
        self.append_row("metric-edge-register.csv", values)

    # -- nodes ---------------------------------------------------------------

    def test_top_level_node_must_be_stage(self):
        self.set_cell("node-register.csv", 0, "node_type", "interaction")
        self.assertFails(f"{SYS}/node-register.csv:2: {STAGE1} has no parent, so it is a stage (L3), not interaction")

    def test_child_node_must_not_be_stage(self):
        self.set_cell("node-register.csv", 2, "node_type", "stage")
        self.assertFails(f"{SYS}/node-register.csv:4: {EPISODE} sits inside {STAGE2}, so it is an episode, step, or interaction (L4), not a stage")

    def test_child_node_types(self):
        for node_type in ("step", "interaction"):
            self.set_cell("node-register.csv", 2, "node_type", node_type)
            self.assertPasses()

    def test_sequence_equals_last_segment(self):
        self.set_cell("node-register.csv", 1, "sequence", "3")
        self.assertFails(f"{SYS}/node-register.csv:3: sequence of {STAGE2} must be 2 (its last ID segment), found 3")

    # -- cells ---------------------------------------------------------------

    def test_whitespace_only_required_cell(self):
        self.set_cell("actor-register.csv", 0, "name", "   ")
        self.assertFails(
            f"{SYS}/actor-register.csv:2: column 'name' holds only whitespace",
            f"{SYS}/actor-register.csv:2: required column 'name' is empty",
        )

    def test_whitespace_only_optional_cell(self):
        self.set_cell("actor-register.csv", 0, "segment", " ")
        self.assertFails(f"{SYS}/actor-register.csv:2: column 'segment' holds only whitespace")

    def test_template_with_data_row(self):
        path = self.root / "skills" / "journey-architecture" / "assets" / "actor-register.csv"
        path.write_text(path.read_text(encoding="utf-8") + "ACT-CUST-SHOP-OWNER-01,Owner,customer,,\n", encoding="utf-8")
        self.assertFails("skills/journey-architecture/assets/actor-register.csv:2: a register template holds the header row only")

    # -- actor codes ---------------------------------------------------------

    def test_journey_actor_code_matches_actor(self):
        self.append_row("actor-register.csv", {"actor_id": "ACT-EMP-SPECIALIST-01", "name": "Specialist", "actor_type": "employee"})
        self.set_cell("journey-registry.csv", 1, "actor_id", "ACT-EMP-SPECIALIST-01")
        self.set_cell("portfolio-register.csv", 1, "actor_id", "ACT-EMP-SPECIALIST-01")
        self.assertFails(
            f"{SYS}/journey-registry.csv:3: actor code of {JOURNEY} differs from its actor_id ACT-EMP-SPECIALIST-01",
            f"{SYS}/portfolio-register.csv:3: actor code of {JOURNEY} differs from its actor_id",
        )

    def test_journey_actor_code_matches_parent_lifecycle(self):
        self.append_row("actor-register.csv", {"actor_id": "ACT-EMP-SPECIALIST-01", "name": "Specialist", "actor_type": "employee"})
        self.append_row("journey-registry.csv", {
            "journey_id": "JRN-EMP-SETUP-001", "level": "L2", "parent_id": LIFECYCLE,
            "actor_id": "ACT-EMP-SPECIALIST-01", "name": "Set up accounts", "state": "current", "status": "draft",
        })
        out = self.assertFails(f"{SYS}/journey-registry.csv:4: actor code of JRN-EMP-SETUP-001 differs from its parent lifecycle {LIFECYCLE}")
        self.assertNotIn("differs from its actor_id", out)

    def test_domain_parent_has_no_actor_code(self):
        self.append_row("journey-registry.csv", {
            "journey_id": "DOM-CUSTOMER-RELATIONSHIP-001", "level": "L0",
            "name": "Customer relationship", "state": "current", "status": "active",
        })
        self.set_cell("journey-registry.csv", 0, "parent_id", "DOM-CUSTOMER-RELATIONSHIP-001")
        self.set_cell("portfolio-register.csv", 0, "parent_id", "DOM-CUSTOMER-RELATIONSHIP-001")
        self.assertPasses()

    # -- portfolio links ------------------------------------------------------

    def add_other_opportunity(self):
        self.add_other_journey()
        self.append_row("opportunity-register.csv", {
            "opportunity_id": "OPP-0002", "journey_id": OTHER, "problem": "P", "root_cause_status": "unknown", "evidence_status": "hypothesis", "status": "draft",
        })
        self.append_row("initiative-register.csv", {
            "initiative_id": "INI-0002", "opportunity_ids": "OPP-0002", "hypothesis": "H", "change": "C", "status": "draft",
        })

    def test_portfolio_links_another_journeys_opportunity(self):
        self.add_other_opportunity()
        self.set_cell("portfolio-register.csv", 1, "linked_opportunities", "OPP-0001;OPP-0002")
        self.set_cell("portfolio-register.csv", 1, "linked_initiatives", "INI-0001;INI-0002")
        self.assertFails(
            f"{SYS}/portfolio-register.csv:3: linked_opportunities cites OPP-0002, which belongs to {OTHER}, not to {JOURNEY} or a journey below it",
            f"{SYS}/portfolio-register.csv:3: linked_initiatives cites INI-0002, which addresses none of the opportunities of {JOURNEY}",
        )

    def test_lifecycle_links_opportunities_of_journeys_below(self):
        self.add_other_opportunity()
        self.set_cell("portfolio-register.csv", 0, "linked_opportunities", "OPP-0001;OPP-0002")
        self.set_cell("portfolio-register.csv", 0, "linked_initiatives", "INI-0001;INI-0002")
        self.assertPasses()

    def test_target_journey_links_baseline_opportunities(self):
        self.append_row("journey-registry.csv", {
            "journey_id": "JRN-CUST-SAAS-ONBOARD-002", "level": "L2", "parent_id": LIFECYCLE,
            "actor_id": "ACT-CUST-SMB-ADMIN-01", "name": "Start using the service (target)",
            "state": "target", "baseline_journey_id": JOURNEY, "status": "draft",
        })
        self.append_row("portfolio-register.csv", {
            "journey_id": "JRN-CUST-SAAS-ONBOARD-002", "parent_id": LIFECYCLE, "level": "L2",
            "actor_id": "ACT-CUST-SMB-ADMIN-01", "name": "Start using the service (target)",
            "state": "target", "status": "draft", "evidence_freshness": "unknown",
            "linked_opportunities": "OPP-0001", "linked_initiatives": "INI-0001",
        })
        self.assertPasses()
        self.add_other_opportunity()
        self.set_cell("portfolio-register.csv", 2, "linked_opportunities", "OPP-0001;OPP-0002")
        self.assertFails(f"{SYS}/portfolio-register.csv:4: linked_opportunities cites OPP-0002, which belongs to {OTHER}")

    def test_journeys_under_handles_parent_cycles(self):
        self.set_cell("journey-registry.csv", 0, "parent_id", "LFC-CUST-LOOP-001")
        self.append_row("journey-registry.csv", {
            "journey_id": "LFC-CUST-LOOP-001", "level": "L1", "parent_id": LIFECYCLE,
            "actor_id": "ACT-CUST-SMB-ADMIN-01", "name": "Loop", "state": "current", "status": "draft",
        })
        self.set_cell("portfolio-register.csv", 0, "parent_id", "LFC-CUST-LOOP-001")
        self.assertFails("parent_id LFC-CUST-LOOP-001 is level L1; a parent must have a lower level number than L1")

    # -- evidence --------------------------------------------------------------

    def test_inferred_without_supporting_evidence(self):
        self.set_cell("node-register.csv", 2, "evidence_status", "inferred")
        self.assertFails(f"{SYS}/node-register.csv:4: evidence_status is inferred but no cited evidence ID is observed or inferred")

    def test_inferred_citing_inferred_evidence_passes(self):
        self.set_cell("evidence-register.csv", 1, "evidence_status", "inferred")
        self.set_cell("node-register.csv", 1, "evidence_status", "inferred")
        self.set_cell("moment-register.csv", 0, "evidence_status", "inferred")
        self.set_cell("opportunity-register.csv", 0, "evidence_status", "inferred")
        self.set_cell("node-register.csv", 2, "evidence_ids", "EVD-2026-0002")
        self.set_cell("node-register.csv", 2, "evidence_status", "inferred")
        self.assertPasses()

    def test_root_cause_status_needs_evidence(self):
        self.set_cell("opportunity-register.csv", 0, "root_cause_status", "observed")
        self.set_cell("opportunity-register.csv", 0, "evidence_ids", "EVD-2026-0003")
        self.set_cell("opportunity-register.csv", 0, "evidence_status", "hypothesis")
        self.assertFails(f"{SYS}/opportunity-register.csv:2: root_cause_status is observed but no cited evidence ID is observed")

    def test_root_cause_status_needs_a_stated_cause(self):
        for cause in ("unknown", "Unknown", ""):
            with self.subTest(cause=cause):
                self.tearDown()
                self.setUp()
                self.set_cell("opportunity-register.csv", 0, "root_cause", cause)
                self.set_cell("opportunity-register.csv", 0, "root_cause_status", "inferred")
                self.assertFails(f"{SYS}/opportunity-register.csv:2: root_cause_status is inferred but root_cause is not stated")

    def test_unknown_root_cause_may_be_unknown(self):
        self.set_cell("opportunity-register.csv", 0, "root_cause", "unknown")
        self.set_cell("opportunity-register.csv", 0, "root_cause_status", "unknown")
        self.assertPasses()

    # -- metric edges and the metric tree --------------------------------------

    def test_metric_edge_to_itself(self):
        self.set_cell("metric-edge-register.csv", 0, "to_metric_id", "MET-0002")
        self.assertFails(f"{SYS}/metric-edge-register.csv:2: metric-edge from MET-0002 to itself")

    def test_duplicate_metric_edge(self):
        self.add_edge("MET-0002", "drives", "MET-0001")
        self.assertFails(f"{SYS}/metric-edge-register.csv:3: duplicate from_metric_id+relation+to_metric_id MET-0002 drives MET-0001 (first on line 2)")

    def test_drives_cycle(self):
        self.add_edge("MET-0001", "drives", "MET-0002")
        self.assertFails(
            f"{SYS}/metric-edge-register.csv:2: drives edge MET-0002 -> MET-0001 closes a cycle",
            f"{SYS}/metric-edge-register.csv:3: drives edge MET-0001 -> MET-0002 closes a cycle",
        )

    def test_protects_edges_do_not_form_cycles(self):
        self.add_metric("MET-0003", JOURNEY, "guardrail")
        self.add_edge("MET-0003", "protects", "MET-0001")
        self.add_edge("MET-0001", "protects", "MET-0003")
        self.assertPasses()

    def test_observed_metric_edge_needs_observed_evidence(self):
        self.set_cell("metric-edge-register.csv", 0, "evidence_status", "observed")
        self.set_cell("metric-edge-register.csv", 0, "evidence_ids", "EVD-2026-0003")
        self.assertFails(f"{SYS}/metric-edge-register.csv:2: evidence_status is observed but no cited evidence ID is observed")

    def test_journey_needs_exactly_one_root(self):
        self.set_cell("metric-register.csv", 0, "layer", "behavior")
        self.assertFails(f"{SYS}/metric-register.csv:2: {JOURNEY} has 0 actor-outcome metrics attached to the journey itself; its metric tree needs exactly one root")
        self.set_cell("metric-register.csv", 0, "layer", "actor-outcome")
        self.add_metric("MET-0003", JOURNEY, "actor-outcome")
        self.assertFails(f"{JOURNEY} has 2 actor-outcome metrics attached to the journey itself")

    def test_actor_outcome_on_a_node_is_not_a_root(self):
        self.add_metric("MET-0003", STAGE1, "actor-outcome")
        self.set_cell("portfolio-register.csv", 1, "metric_coverage", "1")
        self.assertFails(f"{SYS}/metric-register.csv:4: MET-0003 does not reach the root MET-0001 through drives edges")
        self.add_edge("MET-0003", "drives", "MET-0002")
        self.assertPasses()

    def test_metric_must_reach_root(self):
        self.set_cell("metric-edge-register.csv", 0, "relation", "protects")
        self.assertFails(f"{SYS}/metric-register.csv:3: MET-0002 does not reach the root MET-0001 through drives edges")

    def test_business_metric_driven_by_root(self):
        self.add_metric("MET-0003", JOURNEY, "business")
        self.assertFails(f"{SYS}/metric-register.csv:4: business metric MET-0003 must be driven by the root MET-0001")
        self.add_edge("MET-0001", "drives", "MET-0003")
        self.assertPasses()

    def test_guardrail_must_protect(self):
        self.add_metric("MET-0003", STAGE2, "guardrail")
        self.assertFails(f"{SYS}/metric-register.csv:4: guardrail MET-0003 must protect a metric")
        self.add_edge("MET-0003", "protects", "MET-0002")
        self.assertPasses()

    def test_lifecycle_metrics_are_outside_journey_trees(self):
        self.add_metric("MET-0003", LIFECYCLE, "business")
        self.assertPasses()

    def test_metric_on_unknown_node_is_only_a_dangling_reference(self):
        self.add_metric("MET-0003", "NOD-CUST-SAAS-ONBOARD-001-09", "behavior")
        out = self.assertFails("journey_or_node_id cites NOD-CUST-SAAS-ONBOARD-001-09")
        self.assertNotIn("does not reach the root", out)

    def test_rows_with_invalid_layer_are_skipped_in_tree(self):
        self.set_cell("metric-register.csv", 1, "layer", "vanity")
        out = self.assertFails(f"{SYS}/metric-register.csv:3: column 'layer'")
        self.assertNotIn("does not reach", out)

    # -- governance --------------------------------------------------------------

    def test_next_review_before_last_review(self):
        self.set_cell("governance-register.csv", 0, "next_review_due", "2026-06-30")
        self.assertFails(f"{SYS}/governance-register.csv:2: next_review_due 2026-06-30 is before last_reviewed_at 2026-07-01")

    def test_next_review_on_last_review_day_passes(self):
        self.set_cell("governance-register.csv", 0, "next_review_due", "2026-07-01")
        self.assertPasses()

    def test_review_triggers_are_enumerated(self):
        self.set_cell("governance-register.csv", 0, "review_triggers", "policy-change;whim")
        self.assertFails(f"{SYS}/governance-register.csv:2: column 'review_triggers'")

    def test_review_interval_is_positive(self):
        self.set_cell("governance-register.csv", 0, "review_interval_days", "0")
        self.assertFails(f"{SYS}/governance-register.csv:2: column 'review_interval_days'")

    def test_change_log_affected_node_of_other_journey(self):
        self.add_other_journey()
        self.set_cell("change-log.csv", 0, "journey_id", OTHER)
        self.assertFails(f"{SYS}/change-log.csv:2: affected_node_ids {STAGE2} belongs to {JOURNEY}, not {OTHER}")

    def test_unresolved_change_in_view(self):
        self.append_text(f"{SYS}/journey-view.md", "\nAlso CHG-0404.\n")
        self.assertFails(f"{SYS}/journey-view.md:13: CHG-0404 does not resolve to a row in change-log.csv")

    # -- skill paths ---------------------------------------------------------------

    def test_parent_dir_in_reference_file(self):
        self.append_text("skills/journey-metrics/references/metric-tree-method.md", "\nSee ../README.md.\n")
        self.assertFails("skills/journey-metrics/references/metric-tree-method.md:", "path climbs out of the skill with '..'")

    def test_repo_path_in_skill(self):
        self.append_text(SKILL, "\nSee docs/data-model.md and `schemas/metric.schema.json`.\n")
        self.assertFails("path docs/data-model.md points outside the skill", "path schemas/metric.schema.json points outside the skill")

    def test_other_skill_path_in_asset(self):
        self.append_text("skills/journey-metrics/assets/metric-tree-template.md", "\nFrom journey-research/assets/evidence-register.csv.\n")
        self.assertFails("skills/journey-metrics/assets/metric-tree-template.md:", "path into the journey-research skill")

    def test_unknown_name_before_assets_is_not_a_skill(self):
        self.append_text(SKILL, "\nA folder like shop/assets/ is fine.\n")
        self.assertPasses()

    def test_broken_reference_in_reference_file(self):
        self.append_text("skills/journey-metrics/references/metric-tree-method.md", "\nUse `assets/missing.csv`.\n")
        self.assertFails("skills/journey-metrics/references/metric-tree-method.md:", "broken relative reference assets/missing.csv")

    def test_reference_files_may_cite_own_assets(self):
        self.append_text("skills/journey-metrics/references/metric-tree-method.md", "\nUse `assets/metric-register.csv`.\n")
        self.assertPasses()

    def test_reference_from_reference_file_does_not_count_as_referenced(self):
        (self.root / "skills" / "journey-metrics" / "references" / "extra.md").write_text("x\n", encoding="utf-8")
        self.append_text("skills/journey-metrics/references/metric-tree-method.md", "\nSee `references/extra.md`.\n")
        self.assertFails("references/extra.md is not referenced from SKILL.md")

    def test_binary_asset_is_not_scanned(self):
        (self.root / "skills" / "journey-metrics" / "assets" / "logo.png").write_bytes(b"\xff\xfe../docs/")
        self.append_text(SKILL, "\nUse `assets/logo.png`.\n")
        self.assertPasses()

    # -- contract cards ------------------------------------------------------------

    def test_contract_card_drift(self):
        self.append_text(CONVENTIONS, "\nLocal note.\n")
        self.assertFails(f"{CONVENTIONS}: contract card is missing or out of date; run make conventions")

    def test_contract_card_missing(self):
        (self.root / CONVENTIONS).unlink()
        self.assertFails(f"{CONVENTIONS}: contract card is missing or out of date")

    def test_contract_card_follows_ontology(self):
        self.edit_text(V.ONTOLOGY_PATH, "`direction` | `increase`, `decrease`, `maintain` |", "`direction` | `increase`, `decrease`, `maintain`, `hold` |")
        self.assertFails(f"{CONVENTIONS}: contract card is missing or out of date")

    def test_unmapped_ontology_bullet(self):
        self.edit_text(V.ONTOLOGY_PATH, "- On an evidence row,", "- A brand-new rule nobody mapped.\n- On an evidence row,")
        self.assertFails(f"{CONVENTIONS}: cannot generate contract card (", "not mapped in sync_conventions")

    def test_generator_missing(self):
        (self.root / "scripts" / "sync_conventions.py").unlink()
        self.assertFails("scripts/sync_conventions.py: cannot check contract cards")

    def test_sync_conventions_cli(self):
        script = self.root / "scripts" / "sync_conventions.py"
        run = lambda *a: subprocess.run([sys.executable, str(script), *a], capture_output=True, text=True)
        self.assertEqual(run("--check").returncode, 0)
        self.append_text(CONVENTIONS, "\nLocal note.\n")
        result = run("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"stale: {CONVENTIONS}", result.stdout)
        result = run()
        self.assertEqual(result.returncode, 0)
        self.assertIn(f"wrote: {CONVENTIONS}", result.stdout)
        self.assertPasses()

    # -- ID namespaces ---------------------------------------------------------------

    def test_guide_reuses_example_id(self):
        self.append_text("skills/journey-metrics/references/metric-tree-method.md", f"\nFor example {JOURNEY}.\n")
        self.assertFails(
            f"skills/journey-metrics/references/metric-tree-method.md:",
            f"{JOURNEY} is defined by the example system {SYS}; use an ID of your own here",
        )

    def test_standalone_example_reuses_example_id(self):
        (self.root / "examples" / "sketch.md").write_text("Uses MET-0001.\n", encoding="utf-8")
        self.assertFails(f"examples/sketch.md:1: MET-0001 is defined by the example system {SYS}")

    def test_own_ids_in_guides_pass(self):
        self.append_text("skills/journey-metrics/references/metric-tree-method.md", "\nFor example MET-0999 and JRN-CUST-GUIDE-001.\n")
        self.assertPasses()


class EvidenceDisciplineTests(SandboxTest):
    def test_observed_node_without_observed_evidence(self):
        self.set_cell("node-register.csv", 0, "evidence_ids", "EVD-2026-0003")
        self.assertFails(
            f"{SYS}/node-register.csv:2: evidence_status is observed but no cited evidence ID is observed"
        )

    def test_observed_node_without_any_evidence(self):
        self.set_cell("node-register.csv", 0, "evidence_ids", "")
        self.assertFails(
            f"{SYS}/node-register.csv:2: evidence_status is observed but no cited"
        )

    def test_observed_moment_and_opportunity_need_observed_evidence(self):
        self.set_cell("moment-register.csv", 0, "evidence_ids", "EVD-2026-0003")
        self.set_cell("opportunity-register.csv", 0, "evidence_ids", "EVD-2026-0003")
        self.assertFails(
            f"{SYS}/moment-register.csv:2: evidence_status is observed",
            f"{SYS}/opportunity-register.csv:2: evidence_status is observed",
        )

    def test_observed_rule_ignores_dangling_citation(self):
        self.set_cell("node-register.csv", 0, "evidence_ids", "EVD-2026-0404")
        self.assertFails(
            f"{SYS}/node-register.csv:2: evidence_status is observed but no cited"
        )

    def test_non_observed_rows_need_no_observed_evidence(self):
        self.set_cell("node-register.csv", 0, "evidence_ids", "EVD-2026-0003")
        self.set_cell("node-register.csv", 0, "evidence_status", "hypothesis")
        self.assertPasses()
        self.set_cell("node-register.csv", 0, "evidence_ids", "")
        self.set_cell("node-register.csv", 0, "evidence_status", "unknown")
        self.assertPasses()

    def test_stakeholder_input_cannot_be_observed(self):
        self.set_cell("evidence-register.csv", 2, "evidence_status", "observed")
        self.assertFails(
            f"{SYS}/evidence-register.csv:4: stakeholder-input evidence can support hypothesis at most; evidence_status is observed"
        )

    def test_stakeholder_input_cannot_be_inferred(self):
        self.set_cell("evidence-register.csv", 2, "evidence_status", "inferred")
        self.assertFails(
            "stakeholder-input evidence can support hypothesis at most; evidence_status is inferred"
        )

    def test_stakeholder_input_may_be_unknown(self):
        self.set_cell("evidence-register.csv", 2, "evidence_status", "unknown")
        self.assertPasses()

    def test_other_sources_may_be_inferred(self):
        self.set_cell("evidence-register.csv", 1, "evidence_status", "inferred")
        self.set_cell("node-register.csv", 1, "evidence_status", "inferred")
        self.set_cell("moment-register.csv", 0, "evidence_status", "inferred")
        self.set_cell("opportunity-register.csv", 0, "evidence_status", "inferred")
        self.assertPasses()


class ViewTests(SandboxTest):
    def test_unresolved_id_in_markdown(self):
        self.append_text(f"{SYS}/journey-view.md", "\nSee OPP-0404.\n")
        self.assertFails(
            f"{SYS}/journey-view.md:13: OPP-0404 does not resolve to a row in opportunity-register.csv"
        )

    def test_malformed_id_in_markdown(self):
        self.append_text(
            f"{SYS}/journey-view.md", "\nLegacy STG-JRN-CUST-ONBOARD-001-03.\n"
        )
        self.assertFails(
            f"{SYS}/journey-view.md:13: JRN-CUST-ONBOARD-001-03 does not match the JRN ID grammar"
        )

    def test_unresolved_id_in_yaml_view(self):
        (self.system / "notes").mkdir()
        (self.system / "notes" / "governance.yaml").write_text(
            f"journey_id: {JOURNEY}\nmetric_ids:\n  - MET-0404\n", encoding="utf-8"
        )
        self.assertFails(
            f"{SYS}/notes/governance.yaml:3: MET-0404 does not resolve to a row in metric-register.csv"
        )

    def test_every_prefix_resolves(self):
        tokens = [
            "ACT-CUST-SMB-ADMIN-01",
            LIFECYCLE,
            JOURNEY,
            EPISODE,
            "EVD-2026-0003",
            "CHG-0001",
            "MTM-0001",
            "MET-0002",
            "OPP-0001",
            "INI-0001",
        ]
        self.append_text(f"{SYS}/journey-view.md", "\n" + " ".join(tokens) + "\n")
        self.assertPasses()

    def test_example_markdown_grammar(self):
        (self.root / "examples" / "legacy.md").write_text(
            "Journey JRN-CUST-001 and MET-0999.\n", encoding="utf-8"
        )
        out = self.assertFails(
            "examples/legacy.md:1: JRN-CUST-001 does not match the JRN ID grammar"
        )
        self.assertNotIn("MET-0999", out)

    def test_placeholders_outside_examples_are_ignored(self):
        self.append_text("docs/glossary.md", "\nPlaceholder EVD-YYYY-NNNN.\n")
        self.assertPasses()


class SingleFileExampleTests(SandboxTest):
    def setUp(self):
        super().setUp()
        self.single = self.root / "examples" / "portfolio.csv"
        shutil.copy(self.system / "portfolio-register.csv", self.single)

    def test_single_portfolio_passes(self):
        self.assertPasses()

    def test_single_portfolio_parent_must_be_in_file(self):
        self.set_cell(
            "portfolio.csv",
            0,
            "journey_id",
            "LFC-CUST-OTHER-001",
            base=self.root / "examples",
        )
        self.assertFails(
            f"examples/portfolio.csv:3: parent_id {LIFECYCLE} is not in this file"
        )

    def test_single_portfolio_parent_level(self):
        self.set_cell("portfolio.csv", 0, "level", "L2", base=self.root / "examples")
        self.assertFails(
            f"examples/portfolio.csv:2: {LIFECYCLE} is a LFC and must be level L1, found L2",
            f"examples/portfolio.csv:3: parent_id {LIFECYCLE} is level L2",
        )

    def test_single_portfolio_row_schema(self):
        self.set_cell(
            "portfolio.csv",
            1,
            "evidence_freshness",
            "fresh",
            base=self.root / "examples",
        )
        self.assertFails("examples/portfolio.csv:3: column 'evidence_freshness'")

    def test_single_file_unknown_header(self):
        self.single.write_text(
            "journey_id,actor\nJRN-CUST-X-001,customer\n", encoding="utf-8"
        )
        self.assertFails("examples/portfolio.csv:1: header matches no register schema")

    def test_single_file_other_register(self):
        shutil.copy(self.system / "node-register.csv", self.single)
        self.assertPasses()


class ContractTests(SandboxTest):
    def test_template_header_drift(self):
        path = (
            self.root / "skills" / "journey-metrics" / "assets" / "metric-register.csv"
        )
        path.write_text("metric_id,journey_id,layer\n", encoding="utf-8")
        self.assertFails(
            "skills/journey-metrics/assets/metric-register.csv:1: header does not match schemas/metric.schema.json"
        )

    def test_template_rows_are_validated(self):
        path = (
            self.root
            / "skills"
            / "journey-research"
            / "assets"
            / "evidence-register.csv"
        )
        path.write_text(
            path.read_text(encoding="utf-8") + "EVD-26-1,,,,,,,,,\n", encoding="utf-8"
        )
        self.assertFails(
            "skills/journey-research/assets/evidence-register.csv:2: column 'evidence_id'"
        )

    def test_template_missing(self):
        (
            self.root
            / "skills"
            / "moments-that-matter"
            / "assets"
            / "moment-register.csv"
        ).unlink()
        self.edit_text(
            "skills/moments-that-matter/SKILL.md",
            "assets/moment-register.csv",
            "the moment register",
        )
        self.assertFails(
            "skills/moments-that-matter/assets/moment-register.csv: register template named in the ontology is missing"
        )

    def test_unsupported_schema_keyword(self):
        self.edit_schema("actor", lambda s: s["properties"]["name"].update(minLength=1))
        self.assertFails(
            "schemas/actor.schema.json: #/properties/name: unsupported JSON Schema keyword 'minLength'"
        )

    def test_unsupported_root_keyword(self):
        self.edit_schema("actor", lambda s: s.update(allOf=[]))
        self.assertFails(
            "schemas/actor.schema.json: #: unsupported JSON Schema keyword 'allOf'"
        )

    def test_unsupported_type(self):
        self.edit_schema(
            "node", lambda s: s["properties"]["sequence"].update(type="integer")
        )
        self.assertFails(
            "#/properties/sequence: unsupported type 'integer'",
            "property 'sequence' must be type string",
        )

    def test_malformed_subset_keywords(self):
        cases = {
            "required": (
                lambda s: s.update(required=["actor_id", "nickname"]),
                "#: 'required' must list declared properties",
            ),
            "enum": (
                lambda s: s["properties"]["actor_type"].update(enum=[]),
                "#/properties/actor_type: 'enum' must be a non-empty list",
            ),
            "additionalProperties": (
                lambda s: s.update(additionalProperties={}),
                "#: 'additionalProperties' must be a boolean",
            ),
            "pattern": (
                lambda s: s["properties"]["name"].update(pattern="(["),
                "#/properties/name: invalid pattern",
            ),
            "properties": (
                lambda s: s.update(properties=[]),
                "#: 'properties' must be an object",
            ),
            "subschema": (
                lambda s: s["properties"].update(name="text"),
                "schemas/actor.schema.json: #/properties/name: schema must be an object",
            ),
        }
        for label, (change, fragment) in cases.items():
            with self.subTest(keyword=label):
                self.tearDown()
                self.setUp()
                self.edit_schema("actor", change)
                self.assertFails(
                    fragment if label == "subschema" else f"schemas/actor.schema.json: {fragment}"
                )

    def test_schema_pattern_drift(self):
        self.edit_schema(
            "moment",
            lambda s: s["properties"]["metric_ids"].update(pattern="^MET-[0-9]+$"),
        )
        self.assertFails(
            "schemas/moment.schema.json: property 'metric_ids' pattern must be"
        )

    def test_schema_value_pattern_drift(self):
        self.edit_schema(
            "portfolio", lambda s: s["properties"]["last_reviewed_at"].pop("pattern")
        )
        self.assertFails(
            "schemas/portfolio.schema.json: property 'last_reviewed_at' pattern must be"
        )

    def test_schema_enum_drift(self):
        self.edit_schema(
            "evidence",
            lambda s: s["properties"]["source_type"]["enum"].append("gossip"),
        )
        self.assertFails(
            "schemas/evidence.schema.json: property 'source_type' enum must be"
        )

    def test_schema_level_enum_restricted(self):
        self.edit_schema(
            "journey", lambda s: s["properties"]["level"]["enum"].append("L3")
        )
        self.assertFails(
            "schemas/journey.schema.json: property 'level' enum must be ['L0', 'L1', 'L2']"
        )

    def test_schema_stray_enum(self):
        self.edit_schema(
            "actor", lambda s: s["properties"]["segment"].update(enum=["SMB"])
        )
        self.assertFails(
            "schemas/actor.schema.json: property 'segment' has an enum the ontology does not define"
        )

    def test_schema_column_order_drift(self):
        def swap(s):
            items = list(s["properties"].items())
            items[1], items[2] = items[2], items[1]
            s["properties"] = dict(items)

        self.edit_schema("actor", swap)
        self.assertFails(
            "schemas/actor.schema.json: properties ['actor_id', 'actor_type', 'name'"
        )

    def test_schema_primary_key_required(self):
        self.edit_schema("metric", lambda s: s["required"].remove("metric_id"))
        self.assertFails(
            "schemas/metric.schema.json: primary key 'metric_id' must be required"
        )

    def test_schema_header(self):
        cases = [
            (
                lambda s: s.update(
                    {"$schema": "http://json-schema.org/draft-07/schema#"}
                ),
                "$schema must be https://json-schema.org/draft/2020-12/schema",
            ),
            (
                lambda s: s.update({"$id": "actor.json"}),
                "$id must be https://raw.githubusercontent.com/almazrobots/journey-architecture-os/main/schemas/actor.schema.json",
            ),
            (
                lambda s: s.update(additionalProperties=True),
                "a register row must be type object with additionalProperties false",
            ),
            (
                lambda s: s.update(type="string"),
                "a register row must be type object with additionalProperties false",
            ),
            (lambda s: s.pop("description"), "description must explain the row"),
        ]
        for change, fragment in cases:
            with self.subTest(fragment=fragment):
                self.tearDown()
                self.setUp()
                self.edit_schema("actor", change)
                self.assertFails(f"schemas/actor.schema.json: {fragment}")

    def test_schema_missing_or_invalid(self):
        (self.root / "schemas" / "initiative.schema.json").unlink()
        (self.root / "schemas" / "actor.schema.json").write_text("{", encoding="utf-8")
        self.assertFails(
            "schemas/initiative.schema.json: schema is missing",
            "schemas/actor.schema.json: invalid JSON",
        )

    def test_ontology_regex_drift(self):
        self.edit_text(V.ONTOLOGY_PATH, "MTM  ^MTM-[0-9]{4}$", "MTM  ^MTM-[0-9]{5}$")
        self.assertFails(
            "ID regex drift for MTM: ontology='^MTM-[0-9]{5}$' validator='^MTM-[0-9]{4}$'"
        )

    def test_ontology_regex_removed(self):
        self.edit_text(V.ONTOLOGY_PATH, "INI  ^INI-[0-9]{4}$\n", "")
        out = self.assertFails("ID regex drift for INI: ontology=None")
        self.assertNotIn("drift for MTM", out)

    def test_ontology_enum_value_drift(self):
        self.edit_text(V.ONTOLOGY_PATH, "`maintain` |", "`maintain`, `stabilize` |")
        self.assertFails(
            "schemas/metric.schema.json: property 'direction' enum must be ['increase', 'decrease', 'maintain', 'stabilize']"
        )

    def test_ontology_new_enum_must_be_mapped(self):
        self.edit_text(
            V.ONTOLOGY_PATH,
            "| `direction` |",
            "| `channel` | `web`, `app` |\n| `direction` |",
        )
        self.assertFails("enumeration 'channel' is not mapped to any register column")

    def test_ontology_enum_removed(self):
        self.edit_text(V.ONTOLOGY_PATH, "| `moment_type` |", "| `moment_kind` |")
        self.assertFails(
            "enumeration 'moment_type' expected by the validator is missing from the ontology"
        )

    def test_ontology_column_drift(self):
        self.edit_text(
            V.ONTOLOGY_PATH,
            "`actor_id,name,actor_type,segment,context`",
            "`actor_id,name,actor_type,segment,context,region`",
        )
        self.assertFails(
            "schemas/actor.schema.json: properties ['actor_id', 'name', 'actor_type', 'segment', 'context'] differ from ontology columns"
        )

    def test_ontology_register_removed(self):
        text = (self.root / V.ONTOLOGY_PATH).read_text(encoding="utf-8")
        text = "\n".join(
            line for line in text.splitlines() if not line.startswith("| Initiatives |")
        )
        (self.root / V.ONTOLOGY_PATH).write_text(text, encoding="utf-8")
        self.assertFails(
            "register initiative-register.csv is missing from the Registers table"
        )

    def test_ontology_missing(self):
        (self.root / V.ONTOLOGY_PATH).unlink()
        self.edit_text(
            "skills/journey-architecture/SKILL.md",
            "references/ontology.md",
            "the ontology",
        )
        self.assertFails(
            "skills/journey-architecture/references/ontology.md: ontology is missing"
        )


class BoundaryTests(SandboxTest):
    def rename_skill(self, new):
        old = "jobs-and-outcomes"
        shutil.move(str(self.root / "skills" / old), str(self.root / "skills" / new))
        self.edit_text(f"skills/{new}/SKILL.md", f"name: {old}", f"name: {new}")
        reg_path = self.root / "skills.json"
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
        for item in reg["skills"]:
            if item["name"] == old:
                item["name"], item["path"] = new, f"skills/{new}"
        reg_path.write_text(json.dumps(reg), encoding="utf-8")
        # A new skill needs its own contract-card mapping.
        self.edit_text("scripts/sync_conventions.py", f'"{old}":', f'"{new}":')

    def set_description(self, desc):
        path = self.root / SKILL
        text = re.sub(r"^description: .*$", "description: " + desc, path.read_text(encoding="utf-8"), count=1, flags=re.M)
        path.write_text(text, encoding="utf-8")
        reg_path = self.root / "skills.json"
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
        for item in reg["skills"]:
            if item["name"] == "journey-metrics":
                item["description"] = desc
        reg_path.write_text(json.dumps(reg), encoding="utf-8")

    def test_name_of_64_characters_passes(self):
        self.rename_skill("a" * 64)
        self.assertPasses()

    def test_name_of_one_character_passes(self):
        self.rename_skill("a")
        self.assertPasses()

    def test_description_of_one_character_passes(self):
        self.set_description("x")
        self.assertPasses()

    def test_exactly_500_lines_passes(self):
        path = self.root / SKILL
        lines = path.read_text(encoding="utf-8").splitlines()
        path.write_text("\n".join(lines + [""] * (500 - len(lines))) + "\n", encoding="utf-8")
        self.assertEqual(len(path.read_text(encoding="utf-8").splitlines()), 500)
        self.assertPasses()

    def test_indented_first_frontmatter_line(self):
        path = self.root / SKILL
        path.write_text(path.read_text(encoding="utf-8").replace("---\n", "---\n  stray: x\n", 1), encoding="utf-8")
        self.assertFails(f"{SKILL}:2: indented line continues the value of '(no key yet)'")

    def test_scripts_file_is_not_a_directory(self):
        (self.root / "skills" / "journey-metrics" / "scripts").write_text("x", encoding="utf-8")
        out = self.assertFails("skills/journey-metrics/scripts: must be a directory")
        self.assertNotIn("NOTICE", out)

    def test_plain_file_in_skills_root_is_not_a_skill(self):
        (self.root / "skills" / "README.md").write_text("Index\n", encoding="utf-8")
        self.assertPasses()

    def test_symlinks_are_not_followed(self):
        os.symlink(self.root / "README.md", self.system / "inner-link.md")
        os.symlink(self.system, self.root / "skills" / "journey-metrics" / "assets" / "link-dir")
        out = self.assertFails(
            "skills/journey-metrics/assets/link-dir: symbolic links are not allowed",
            f"{SYS}/inner-link.md: symbolic links are not allowed",
        )
        self.assertNotIn("link-dir/inner-link.md", out)

    def test_impossible_collected_at_date(self):
        self.set_cell("evidence-register.csv", 0, "collected_at", "2026-02-30")
        self.assertFails(f"{SYS}/evidence-register.csv:2: column 'collected_at': '2026-02-30' is not a calendar date")

    def test_malformed_csv_quoting(self):
        (self.system / "actor-register.csv").write_text('actor_id,name,actor_type,segment,context\n"ACT"x,y,customer,,\n', encoding="utf-8")
        self.assertFails(f"{SYS}/actor-register.csv: unreadable CSV")


class MutationGapTests(SandboxTest):
    """Tests added to kill mutants that survived earlier runs."""

    def test_comment_annotation_is_supported(self):
        self.edit_schema("actor", lambda s: s.update({"$comment": "note"}))
        self.assertPasses()

    def test_paths_checked_in_every_text_asset_type(self):
        for suffix in (".csv", ".yaml", ".yml", ".json", ".txt"):
            with self.subTest(suffix=suffix):
                self.tearDown()
                self.setUp()
                name = f"extra{suffix}"
                (self.root / "skills" / "journey-metrics" / "assets" / name).write_text("see docs/x.md\n", encoding="utf-8")
                self.append_text(SKILL, f"\nUse `assets/{name}`.\n")
                self.assertFails(f"skills/journey-metrics/assets/{name}:1: path docs/x.md points outside the skill")

    def test_path_line_numbers_in_reference_file(self):
        (self.root / "skills" / "journey-metrics" / "references" / "extra.md").write_text("x\ndocs/y.md\n", encoding="utf-8")
        self.append_text(SKILL, "\nRead `references/extra.md`.\n")
        self.assertFails("skills/journey-metrics/references/extra.md:2: path docs/y.md points outside the skill")

    def test_unresolved_id_in_yml_view(self):
        (self.system / "notes.yml").write_text("metric: MET-0404\n", encoding="utf-8")
        self.assertFails(f"{SYS}/notes.yml:1: MET-0404 does not resolve")

    def test_empty_frontmatter_block(self):
        path = self.root / SKILL
        text = path.read_text(encoding="utf-8")
        body = text.split("\n---\n", 1)[1]
        path.write_text("---\n---\n" + body, encoding="utf-8")
        self.assertFails(f"{SKILL}: frontmatter requires 'name'")

    def test_block_scalar_with_chomping_indicator(self):
        self.edit_text(SKILL, "license: MIT", "license: >-\n  MIT")
        self.assertFails(f"{SKILL}:4: block scalar indicator in 'license' is not allowed")

    def test_one_space_nested_mapping_passes(self):
        path = self.root / SKILL
        text = path.read_text(encoding="utf-8")
        head, body = text.split("\n---\n", 1)
        path.write_text(head.replace("\n  ", "\n ") + "\n---\n" + body, encoding="utf-8")
        self.assertPasses()

    def test_name_errors_carry_line_numbers(self):
        self.edit_text(SKILL, "name: journey-metrics", "name: Journey_Metrics")
        self.assertFails(
            f"{SKILL}:2: journey-metrics: frontmatter name must match directory",
            f"{SKILL}:2: invalid name 'Journey_Metrics'",
        )

    def test_name_length_carries_line_number(self):
        long_name = "a" * 65
        self.edit_text(SKILL, "name: journey-metrics", f"name: {long_name}")
        self.assertFails(f"{SKILL}:2: name length invalid")

    def test_501_lines_fail(self):
        path = self.root / SKILL
        lines = path.read_text(encoding="utf-8").splitlines()
        path.write_text("\n".join(lines + [""] * (501 - len(lines))) + "\n", encoding="utf-8")
        self.assertFails(f"{SKILL}: SKILL.md has 501 lines; max 500 recommended")

    def test_description_of_1025_characters_fails(self):
        path = self.root / SKILL
        text = re.sub(r"^description: .*$", "description: " + "x" * 1025, path.read_text(encoding="utf-8"), count=1, flags=re.M)
        path.write_text(text, encoding="utf-8")
        self.assertFails(f"{SKILL}:3: description length invalid (1025)")

    def test_symlink_outside_checked_trees_is_not_reported(self):
        os.symlink(self.root / "README.md", self.root / "docs" / "readme-link.md")
        self.assertPasses()

    def test_symlinked_scripts_directory_has_no_notice(self):
        target = self.root / "outside-scripts"
        target.mkdir()
        os.symlink(target, self.root / "skills" / "journey-metrics" / "scripts")
        out = self.assertFails("skills/journey-metrics/scripts: must be a directory")
        self.assertNotIn("NOTICE", out)

    def test_invalid_metric_edge_endpoint(self):
        self.add_rows_for_edges()
        self.set_cell("metric-edge-register.csv", 0, "from_metric_id", "MET-2")
        out = self.assertFails(f"{SYS}/metric-edge-register.csv:2: column 'from_metric_id'")
        self.assertNotIn("Traceback", out)

    def add_rows_for_edges(self):
        self.append_row("metric-register.csv", {"metric_id": "MET-0003", "journey_or_node_id": STAGE1, "layer": "behavior",
                                                 "name": "M", "definition": "D", "direction": "increase", "evidence_status": "unknown"})
        self.append_row("metric-edge-register.csv", {"from_metric_id": "MET-0003", "relation": "drives",
                                                      "to_metric_id": "MET-0001", "evidence_status": "hypothesis"})

    def test_coverage_rounds_to_two_decimals(self):
        self.append_row("node-register.csv", {
            "node_id": "NOD-CUST-SAAS-ONBOARD-001-03", "journey_id": JOURNEY, "node_type": "stage",
            "sequence": "3", "name": "Work as a team", "evidence_status": "unknown",
        })
        self.set_cell("portfolio-register.csv", 1, "metric_coverage", "0.33")
        self.assertPasses()

    def test_invalid_node_type_is_not_rechecked(self):
        self.set_cell("node-register.csv", 0, "node_type", "phase")
        out = self.assertFails(f"{SYS}/node-register.csv:2: column 'node_type'")
        self.assertNotIn("so it is a stage", out)

    def test_impossible_date_is_not_compared(self):
        self.set_cell("governance-register.csv", 0, "last_reviewed_at", "2026-09-31")
        self.set_cell("governance-register.csv", 0, "next_review_due", "2026-09-30")
        out = self.assertFails(f"{SYS}/governance-register.csv:2: column 'last_reviewed_at': '2026-09-31' is not a calendar date")
        self.assertNotIn("is before last_reviewed_at", out)

    def test_byte_order_mark_is_accepted(self):
        for name in ("actor-register.csv", "journey-registry.csv"):
            path = self.system / name
            path.write_bytes(b"\xef\xbb\xbf" + path.read_bytes())
        self.assertPasses()

    def test_non_utf8_register_is_one_clear_error(self):
        path = self.system / "moment-register.csv"
        path.write_bytes(path.read_bytes().replace(b"Team adoption", "Équipe".encode("latin-1")))
        self.assertFails(f"{SYS}/moment-register.csv: not UTF-8 (byte")

    def test_malformed_csv_is_unreadable(self):
        (self.system / "moment-register.csv").write_text('moment_id,node_id\n"MTM"x,y\n', encoding="utf-8")
        self.assertFails(f"{SYS}/moment-register.csv: unreadable CSV")

    def test_status_columns_are_required(self):
        for filename, row, column in (
            ("node-register.csv", 0, "evidence_status"),
            ("relation-register.csv", 1, "evidence_status"),
            ("evidence-register.csv", 0, "evidence_status"),
            ("moment-register.csv", 0, "evidence_status"),
            ("metric-register.csv", 1, "evidence_status"),
            ("metric-edge-register.csv", 0, "evidence_status"),
            ("opportunity-register.csv", 0, "evidence_status"),
            ("opportunity-register.csv", 0, "root_cause_status"),
        ):
            with self.subTest(file=filename, column=column):
                self.tearDown()
                self.setUp()
                self.set_cell(filename, row, column, "")
                self.assertFails(f"{SYS}/{filename}:{row + 2}: required column '{column}' is empty")

    def test_schema_must_require_status_columns(self):
        self.edit_schema("opportunity", lambda s: s["required"].remove("root_cause_status"))
        self.assertFails("schemas/opportunity.schema.json: status column 'root_cause_status' must be required (use unknown when not assessed)")
        self.edit_schema("opportunity", lambda s: s["required"].remove("evidence_status"))
        self.assertFails("schemas/opportunity.schema.json: status column 'evidence_status' must be required")

    # -- journey scope of cited moments and metrics --------------------------

    def add_other_scope(self):
        self.append_row("journey-registry.csv", {
            "journey_id": "JRN-CUST-SUPPORT-001", "level": "L2", "parent_id": LIFECYCLE, "actor_id": "ACT-CUST-SMB-ADMIN-01",
            "name": "Resolve a problem", "state": "current", "status": "draft",
        })
        self.append_row("node-register.csv", {
            "node_id": "NOD-CUST-SUPPORT-001-01", "journey_id": "JRN-CUST-SUPPORT-001", "node_type": "stage",
            "sequence": "1", "name": "Report it", "evidence_status": "unknown",
        })
        self.append_row("moment-register.csv", {
            "moment_id": "MTM-0002", "node_id": "NOD-CUST-SUPPORT-001-01", "moment_type": "recovery",
            "outcome_at_stake": "Trust", "evidence_status": "unknown",
        })
        for mid, target, layer in (("MET-0003", "JRN-CUST-SUPPORT-001", "actor-outcome"), ("MET-0004", LIFECYCLE, "business"),
                                   ("MET-0005", "NOD-CUST-SUPPORT-001-01", "behavior")):
            self.append_row("metric-register.csv", {"metric_id": mid, "journey_or_node_id": target, "layer": layer, "name": "M",
                                                     "definition": "D", "direction": "increase", "evidence_status": "unknown"})
        self.append_row("metric-edge-register.csv", {"from_metric_id": "MET-0005", "relation": "drives",
                                                      "to_metric_id": "MET-0003", "evidence_status": "unknown"})

    def test_scoped_links_pass(self):
        self.add_other_scope()
        # a lifecycle-level metric is inside every journey's scope below it
        self.set_cell("opportunity-register.csv", 0, "metric_ids", "MET-0001;MET-0004")
        self.set_cell("moment-register.csv", 0, "metric_ids", "MET-0002;MET-0004")
        self.set_cell("initiative-register.csv", 0, "expected_metric_ids", "MET-0002;MET-0004")
        self.assertPasses()

    def test_opportunity_moment_of_other_journey(self):
        self.add_other_scope()
        self.set_cell("opportunity-register.csv", 0, "moment_ids", "MTM-0001;MTM-0002")
        self.assertFails(f"{SYS}/opportunity-register.csv:2: moment_ids cites MTM-0002, a moment of JRN-CUST-SUPPORT-001, not of {JOURNEY}")

    def test_opportunity_metric_of_other_journey(self):
        self.add_other_scope()
        self.set_cell("opportunity-register.csv", 0, "metric_ids", "MET-0001;MET-0005;MET-0003")
        self.assertFails(
            f"{SYS}/opportunity-register.csv:2: metric_ids cites MET-0005, which is outside the scope of {JOURNEY}",
            f"{SYS}/opportunity-register.csv:2: metric_ids cites MET-0003, which is outside the scope of {JOURNEY}",
        )

    def test_moment_metric_of_other_journey(self):
        self.add_other_scope()
        self.set_cell("moment-register.csv", 0, "metric_ids", "MET-0003")
        self.assertFails(f"{SYS}/moment-register.csv:2: metric_ids cites MET-0003, which is outside the scope of {JOURNEY}")

    def test_initiative_metric_of_other_journey(self):
        self.add_other_scope()
        self.set_cell("initiative-register.csv", 0, "expected_metric_ids", "MET-0005")
        self.assertFails(f"{SYS}/initiative-register.csv:2: expected_metric_ids cites MET-0005, which is outside the scope of {JOURNEY}")

    def test_initiative_scope_covers_all_its_opportunities(self):
        self.add_other_scope()
        self.append_row("opportunity-register.csv", {"opportunity_id": "OPP-0002", "journey_id": "JRN-CUST-SUPPORT-001",
                                                      "problem": "P", "root_cause_status": "unknown", "evidence_status": "unknown", "status": "draft"})
        self.set_cell("initiative-register.csv", 0, "opportunity_ids", "OPP-0001;OPP-0002")
        self.set_cell("initiative-register.csv", 0, "expected_metric_ids", "MET-0001;MET-0005")
        self.assertPasses()

    def test_opportunity_on_target_journey(self):
        self.append_row("journey-registry.csv", {
            "journey_id": "JRN-CUST-SAAS-ONBOARD-002", "level": "L2", "parent_id": LIFECYCLE, "actor_id": "ACT-CUST-SMB-ADMIN-01",
            "name": "Target", "state": "target", "baseline_journey_id": JOURNEY, "status": "draft",
        })
        self.append_row("opportunity-register.csv", {"opportunity_id": "OPP-0002", "journey_id": "JRN-CUST-SAAS-ONBOARD-002",
                                                      "problem": "P", "root_cause_status": "unknown", "evidence_status": "unknown", "status": "draft"})
        self.assertFails(f"{SYS}/opportunity-register.csv:3: JRN-CUST-SAAS-ONBOARD-002 is target; opportunities belong to current journeys")

    def test_scope_skips_unknown_citations(self):
        self.set_cell("moment-register.csv", 0, "metric_ids", "MET-0404")
        self.set_cell("opportunity-register.csv", 0, "moment_ids", "MTM-0404")
        out = self.assertFails("metric_ids cites MET-0404, which is not in", "moment_ids cites MTM-0404, which is not in")
        self.assertNotIn("outside the scope", out)

    def test_single_file_journey_registry(self):
        shutil.copy(self.system / "journey-registry.csv", self.root / "examples" / "journeys.csv")
        self.set_cell("journeys.csv", 1, "level", "L1", base=self.root / "examples")
        self.assertFails(f"examples/journeys.csv:3: {JOURNEY} is a JRN and must be level L2, found L1")


class ReviewGapTests(SandboxTest):
    """Engineering review: examples coverage, link escape, frontmatter keys, and more."""

    # -- M2 examples coverage ------------------------------------------------

    def test_csv_outside_any_system(self):
        (self.root / "examples" / "sketches").mkdir()
        (self.root / "examples" / "sketches" / "notes.csv").write_text("a,b\n", encoding="utf-8")
        out = self.assertFails("examples/sketches/notes.csv: CSV outside any journey system")
        self.assertNotIn("holds register files", out)

    def test_register_files_without_registry(self):
        other = self.root / "examples" / "half-system"
        other.mkdir()
        shutil.copy(self.system / "actor-register.csv", other)
        shutil.copy(self.system / "node-register.csv", other)
        out = self.assertFails(
            "examples/half-system/actor-register.csv: CSV outside any journey system",
            "examples/half-system: holds register files but no journey-registry.csv",
        )
        self.assertEqual(out.count("holds register files"), 1)

    def test_csv_in_system_subfolder(self):
        (self.system / "old").mkdir()
        shutil.copy(self.system / "actor-register.csv", self.system / "old")
        out = self.assertFails(f"{SYS}/old/actor-register.csv: unknown register file; expected one of")
        self.assertNotIn("CSV outside any journey system", out)

    def test_two_systems_plural(self):
        shutil.copytree(self.system, self.root / "examples" / "second")
        # the second system redefines the same IDs, which its views may cite
        out = self.run_validator()[1]
        self.assertIn("2 journey systems validated", out)

    # -- M3 link escape ----------------------------------------------------------

    def test_missing_link_target(self):
        self.append_text(SKILL, "\nSee [the readme](README.md).\n")
        self.assertFails(f"{SKILL}:", "broken relative reference README.md")

    def test_absolute_link_to_repo_docs(self):
        self.append_text(SKILL, "\nSee [model](/docs/data-model.md).\n")
        self.assertFails("unsafe relative reference /docs/data-model.md")

    def test_home_path(self):
        self.append_text(SKILL, "\nRun `~/bin/tool.py`.\n")
        self.assertFails("unsafe relative reference ~/bin/tool.py")

    def test_links_with_fragments_urls_mail_and_anchors(self):
        self.append_text(
            SKILL,
            "\nSee [method](references/metric-tree-method.md#targets), [top](#goal), "
            "[mail](mailto:a@example.org), [site](https://example.org/x.md) and `n/a` or `L3/L4`.\n",
        )
        self.assertPasses()

    def test_link_counts_as_reference(self):
        (self.root / "skills" / "journey-metrics" / "references" / "extra.md").write_text("x\n", encoding="utf-8")
        self.append_text(SKILL, "\nSee [extra](references/extra.md).\n")
        self.assertPasses()

    def test_sibling_link_inside_references(self):
        self.append_text("skills/journey-metrics/references/metric-tree-method.md", "\nSee [card](conventions.md).\n")
        self.assertPasses()

    def test_backticked_file_path_must_exist(self):
        self.append_text(SKILL, "\nUse `templates/missing.md`.\n")
        self.assertFails("broken relative reference templates/missing.md")

    def test_backticked_bare_file_name_is_not_a_path(self):
        self.append_text(SKILL, "\nThe register `metric-register.csv` and `journey-registry.csv`.\n")
        self.assertPasses()

    def test_link_to_repo_folder_reported_once(self):
        for folder in ("skills", "docs", "scripts", "schemas", "examples", "evals", "tests"):
            with self.subTest(folder=folder):
                self.tearDown()
                self.setUp()
                self.append_text(SKILL, f"\nSee [x]({folder}/x.md).\n")
                out = self.assertFails(f"path {folder}/x.md points outside the skill")
                self.assertNotIn("broken relative reference", out)

    def test_link_into_other_skill_reported_once(self):
        self.append_text(SKILL, "\nSee [o](journey-architecture/references/ontology.md).\n")
        out = self.assertFails("path into the journey-architecture skill")
        self.assertNotIn("broken relative reference", out)

    # -- M4 frontmatter allow-list --------------------------------------------

    def test_unknown_frontmatter_key(self):
        self.edit_text(SKILL, "license: MIT", "license: MIT\nversion: 2")
        self.assertFails(f"{SKILL}:5: frontmatter key 'version' is not allowed (allowed: name, description, license, compatibility, metadata, allowed-tools)")

    def test_allowed_optional_keys(self):
        self.edit_text(SKILL, "license: MIT", "license: MIT\ncompatibility: Any agent client\nallowed-tools: Read Grep")
        self.assertPasses()

    def test_optional_keys_must_be_strings(self):
        for key in ("license", "compatibility", "allowed-tools"):
            with self.subTest(key=key):
                self.tearDown()
                self.setUp()
                self.edit_text(SKILL, "license: MIT", f"{key}:\n  - a")
                self.assertFails(f"{SKILL}:4: {key}: must be a single-line scalar")

    def test_metadata_must_be_a_map(self):
        self.edit_text(SKILL, "metadata:\n", "metadata: flat\nx-metadata:\n")
        self.assertFails(f"{SKILL}:5: metadata must be a map of string keys to string values")

    def test_metadata_entries_are_strings(self):
        self.edit_text(SKILL, "  author:", "  - listed\n  author:")
        self.assertFails(f"{SKILL}:6: metadata entries must be 'key: value' strings at one indentation")

    def test_metadata_nested_map_rejected(self):
        self.edit_text(SKILL, "  author:", "  owner:\n    team: x\n  author:")
        self.assertFails(f"{SKILL}:6: metadata entries must be 'key: value' strings")

    def test_metadata_mixed_indentation(self):
        self.edit_text(SKILL, "  author:", "   extra: x\n  author:")
        self.assertFails(f"{SKILL}:7: metadata entries must be 'key: value' strings at one indentation")

    def test_metadata_duplicate_key(self):
        self.edit_text(SKILL, "  author:", "  author: a\n  author:")
        self.assertFails(f"{SKILL}:7: duplicate metadata key 'author'")

    def test_metadata_value_must_be_simple(self):
        self.edit_text(SKILL, "  author:", "  note: a: b\n  author:")
        self.assertFails(f"{SKILL}:6: metadata note: plain value must not contain")

    # -- m1 ECMA end-of-input ----------------------------------------------------

    def test_trailing_newline_in_id_cell(self):
        self.set_cell("actor-register.csv", 0, "actor_id", "ACT-CUST-SMB-ADMIN-01\n")
        self.assertFails(f"{SYS}/actor-register.csv:2: column 'actor_id'")

    def test_trailing_newline_in_sequence(self):
        self.set_cell("node-register.csv", 0, "sequence", "1\n")
        self.assertFails(f"{SYS}/node-register.csv:2: column 'sequence'")

    def test_ecma_dollar_only_at_end(self):
        self.assertTrue(V.ecma_search("^a$", "a"))
        self.assertFalse(V.ecma_search("^a$", "a\n"))
        self.assertTrue(V.ecma_search(r"^a\$$", "a$"))

    # -- m2 non-UTF-8 text ---------------------------------------------------------

    def test_non_utf8_text_files_are_clean_errors(self):
        cases = [
            SKILL,
            "skills/journey-metrics/references/metric-tree-method.md",
            f"{SYS}/journey-view.md",
            "schemas/actor.schema.json",
            V.ONTOLOGY_PATH,
            "skills.json",
        ]
        for rel in cases:
            with self.subTest(file=rel):
                self.tearDown()
                self.setUp()
                path = self.root / rel
                path.write_bytes(path.read_bytes() + "\nÉ\n".encode("latin-1"))
                out = self.assertFails(f"{rel}: not UTF-8 (byte")
                self.assertNotIn("Traceback", out)

    def test_only_markdown_and_yaml_views_are_scanned(self):
        (self.system / "notes.txt").write_text("MET-0404\n", encoding="utf-8")
        (self.system / "draft.md").mkdir()
        self.assertPasses()

    def test_non_utf8_standalone_example(self):
        (self.root / "examples" / "sketch.md").write_bytes("É".encode("latin-1"))
        self.assertFails("examples/sketch.md: not UTF-8 (byte 0)")

    # -- m3 ------------------------------------------------------------------------

    def test_lifecycle_metric_must_be_business(self):
        self.append_row("metric-register.csv", {"metric_id": "MET-0003", "journey_or_node_id": LIFECYCLE, "layer": "guardrail",
                                                 "name": "M", "definition": "D", "direction": "increase", "evidence_status": "unknown"})
        self.assertFails(f"{SYS}/metric-register.csv:4: MET-0003 is attached to {LIFECYCLE}; metrics above journey level must be business, not guardrail")

    def test_version_actor_matches_baseline(self):
        self.append_row("actor-register.csv", {"actor_id": "ACT-CUST-SMB-OWNER-01", "name": "Owner", "actor_type": "customer"})
        self.append_row("journey-registry.csv", {
            "journey_id": "JRN-CUST-SAAS-ONBOARD-002", "level": "L2", "parent_id": LIFECYCLE, "actor_id": "ACT-CUST-SMB-OWNER-01",
            "name": "Target", "state": "target", "baseline_journey_id": JOURNEY, "status": "draft",
        })
        self.assertFails(
            f"{SYS}/journey-registry.csv:4: actor_id of JRN-CUST-SAAS-ONBOARD-002 is ACT-CUST-SMB-OWNER-01, but its baseline {JOURNEY} is for ACT-CUST-SMB-ADMIN-01"
        )

    def test_coverage_only_on_journey_rows(self):
        self.set_cell("portfolio-register.csv", 0, "metric_coverage", "0.5")
        out = self.assertFails(f"{SYS}/portfolio-register.csv:2: metric_coverage applies to JRN rows only; leave it empty for {LIFECYCLE}")
        self.assertNotIn("no stage-level nodes", out)

    def test_coverage_only_on_journey_rows_in_single_file(self):
        shutil.copy(self.system / "portfolio-register.csv", self.root / "examples" / "portfolio.csv")
        self.set_cell("portfolio.csv", 0, "metric_coverage", "1", base=self.root / "examples")
        self.assertFails("examples/portfolio.csv:2: metric_coverage applies to JRN rows only")


class OntologySingleSourceTests(unittest.TestCase):
    """The ontology's regex block is the single source of truth."""

    def ontology_block(self):
        text = ONTOLOGY.read_text(encoding="utf-8")
        block = re.search(r"Regular expressions[^\n]*\n\n```text\n(.*?)```", text, re.S)
        self.assertIsNotNone(block, "ontology.md must contain the ```text regex block")
        pairs = [line.split(None, 1) for line in block.group(1).strip().splitlines()]
        return {prefix: regex.strip() for prefix, regex in pairs}

    def test_validator_regexes_equal_ontology_block(self):
        self.assertEqual(self.ontology_block(), V.ID_PATTERNS)

    def test_validator_parser_reads_the_same_block(self):
        onto = V.parse_ontology(ONTOLOGY.read_text(encoding="utf-8"))
        self.assertEqual(onto["regexes"], self.ontology_block())

    def test_schema_patterns_are_derived_from_ontology(self):
        block = self.ontology_block()
        for (register, column), (prefixes, is_list) in V.ID_COLUMNS.items():
            schema = json.loads(
                (ROOT / "schemas" / f"{register}.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            pattern = schema["properties"][column]["pattern"]
            for prefix in prefixes:
                self.assertIn(block[prefix][1:-1], pattern, (register, column))

    def test_ontology_examples_match_grammar(self):
        text = ONTOLOGY.read_text(encoding="utf-8")
        examples = dict(re.findall(r"^\| [A-Za-z ]+ \| `([A-Z]{3})-\{[^|]*\| `([^`]+)` \|$", text, re.M))
        self.assertEqual(set(examples), set(V.ID_PATTERNS))
        for prefix, example in examples.items():
            self.assertRegex(example, V.ID_PATTERNS[prefix])
            self.assertEqual(V.ID_TOKEN_RE.findall(f"see {example}."), [example])


class UnitTests(unittest.TestCase):
    def test_id_pattern_single_and_list(self):
        self.assertEqual(V.id_pattern(("MET",), False), V.ID_PATTERNS["MET"])
        pattern = V.id_pattern(("MET",), True)
        self.assertRegex("MET-0001;MET-0002", pattern)
        for bad in (
            "MET-0001;",
            ";MET-0001",
            "MET-0001,MET-0002",
            "MET-0001; MET-0002",
            "OPP-0001",
        ):
            self.assertNotRegex(bad, pattern)

    def test_id_pattern_alternation(self):
        pattern = V.id_pattern(("DOM", "LFC", "JRN"), False)
        for good in ("DOM-CUSTOMER-001", "LFC-CUST-LIFE-001", "JRN-CUST-SAAS-001"):
            self.assertRegex(good, pattern)
        for bad in ("NOD-CUST-SAAS-001-01", "JRN-CUST-SAAS-001x", "xLFC-CUST-LIFE-001"):
            self.assertNotRegex(bad, pattern)

    def test_validate_instance_subset(self):
        schema = {
            "type": "object",
            "required": ["a"],
            "additionalProperties": False,
            "properties": {
                "a": {"type": "string", "pattern": "^x+$"},
                "b": {"type": "string", "enum": ["p", "q"]},
            },
        }
        self.assertEqual(V.validate_instance({"a": "xx", "b": "q"}, schema), [])
        self.assertEqual(
            V.validate_instance([], schema), [(None, "expected an object")]
        )
        self.assertEqual(
            V.validate_instance(5, {"type": "string"}), [(None, "expected a string")]
        )
        errors = dict(V.validate_instance({"b": "r", "c": "1"}, schema))
        self.assertEqual(errors["a"], "required column 'a' is empty")
        self.assertEqual(errors["c"], "unexpected column 'c'")
        self.assertIn("'r' is not one of: p, q", errors["b"])
        self.assertEqual(
            V.validate_instance(
                {"c": "1"}, {"type": "object", "additionalProperties": True}
            ),
            [],
        )
        self.assertEqual(len(V.validate_instance({"a": "xy"}, schema)), 1)

    def test_scalar_parser(self):
        self.assertEqual(V.parse_plain_or_quoted("plain value"), "plain value")
        self.assertEqual(V.parse_plain_or_quoted('"quoted: yes"'), "quoted: yes")
        self.assertEqual(V.parse_plain_or_quoted("'single # ok'"), "single # ok")
        self.assertEqual(V.parse_plain_or_quoted("a-b"), "a-b")
        for bad in (
            "",
            '"',
            "'",
            '"a\\nb"',
            '"a"b"',
            "'it''s'",
            "'open",
            '"open',
            "- item",
            "[a]",
            "a: b",
            "a #c",
            "trailing:",
            "*alias",
            "&anchor x",
        ):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    V.parse_plain_or_quoted(bad)

    def test_frontmatter_parser(self):
        fields, lines, nested = V.parse_frontmatter(
            "---\nname: x\n# note\n\nmetadata:\n  author: y\n  name: z\ndescription: d\n---\nbody\n"
        )
        self.assertEqual(fields, {"name": "x", "metadata": "", "description": "d"})
        self.assertEqual(lines, {"name": 2, "metadata": 5, "description": 8})
        self.assertEqual(nested, {"metadata": [(6, "  author: y"), (7, "  name: z")]})

    def test_ontology_parser_reads_only_its_tables(self):
        text = (
            "## Other\n| `x` | `y` |\n| `a` | `b` | `c` |\n"
            "## Enumerations\n| Field | Allowed values |\n| `level` | `L0`, `L1` (only `L0` here) |\n"
            "## Registers\n| Register | Skill | File | Columns |\n"
            "| Actors | `p` | `actor-register.csv` | `a,b` |\n| Broken | `p` | `broken.csv` | none |\n"
            "| NoSkill | none | `x.csv` | `a` |\n| NoFile | `p` | none | `a` |\n"
        )
        onto = V.parse_ontology(text)
        self.assertEqual(onto["enums"], {"level": ["L0", "L1"]})
        self.assertEqual(onto["registers"], {"actor-register.csv": ("p", ["a", "b"])})
        self.assertEqual(onto["regexes"], {})

    def test_ontology_parser_ignores_look_alikes(self):
        text = (
            "```text\nACT  ^A$ trailing\n```\n"
            "## Other\n| a | `s` | `f.csv` | `c` |\n"
            "## Enumerations\n`level` | `L0` |\n"
        )
        onto = V.parse_ontology(text)
        self.assertEqual(onto, {"regexes": {}, "enums": {}, "registers": {}})

    def test_single_quoted_error_message(self):
        with self.assertRaisesRegex(ValueError, "single-quoted value must be one simple"):
            V.parse_plain_or_quoted("'a'b'")

    def test_empty_quoted_scalars(self):
        self.assertEqual(V.parse_plain_or_quoted('""'), "")
        self.assertEqual(V.parse_plain_or_quoted("''"), "")

    def test_level_number(self):
        self.assertEqual(V.level_number("L0"), 0)
        self.assertEqual(V.level_number("L2"), 2)

    def test_report_paths(self):
        report = V.Report(Path("/repo"))
        report.error(Path("/repo/a/b.csv"), 3, "bad")
        report.error(Path("/elsewhere/c.csv"), None, "worse")
        self.assertEqual(report.errors, ["a/b.csv:3: bad", "/elsewhere/c.csv: worse"])


SKILL = "skills/journey-metrics/SKILL.md"


class SkillSecurityTests(SandboxTest):
    def replace_frontmatter_line(self, old, new):
        self.edit_text(SKILL, old, new)

    def test_block_scalar_description(self):
        self.replace_frontmatter_line("description: ", "description: >\n  ")
        self.assertFails(
            f"{SKILL}:3: block scalar indicator in 'description' is not allowed"
        )

    def test_literal_block_scalar(self):
        self.replace_frontmatter_line("license: MIT", "license: |\n  MIT")
        self.assertFails(
            f"{SKILL}:4: block scalar indicator in 'license' is not allowed"
        )

    def test_duplicate_key(self):
        self.replace_frontmatter_line(
            "license: MIT", "license: MIT\nname: journey-kpis"
        )
        self.assertFails(f"{SKILL}:5: duplicate top-level key 'name' (first on line 2)")

    def test_multiline_plain_continuation(self):
        self.replace_frontmatter_line("license: MIT", "license: MIT\n  continued")
        self.assertFails(f"{SKILL}:5: indented line continues the value of 'license'")

    def test_nested_name_is_not_top_level(self):
        self.replace_frontmatter_line("  author:", "  name: journey-kpis\n  author:")
        self.assertPasses()

    def test_quoted_description_with_escape(self):
        path = self.root / SKILL
        text = path.read_text(encoding="utf-8")
        text = re.sub(
            r"^description: (.*)$",
            lambda m: 'description: "' + m.group(1) + '\\n"',
            text,
            count=1,
            flags=re.M,
        )
        path.write_text(text, encoding="utf-8")
        self.assertFails(
            f"{SKILL}:3: description: double-quoted value must be one simple"
        )

    def test_simple_quoted_values_accepted(self):
        path = self.root / SKILL
        text = path.read_text(encoding="utf-8").replace(
            "name: journey-metrics", "name: 'journey-metrics'", 1
        )
        path.write_text(text, encoding="utf-8")
        self.assertPasses()

    def test_plain_value_with_comment(self):
        self.replace_frontmatter_line(
            "name: journey-metrics", "name: journey-metrics # kpis"
        )
        self.assertFails(f"{SKILL}:2: name: plain value must not contain")

    def test_frontmatter_not_first(self):
        path = self.root / SKILL
        path.write_text("\n" + path.read_text(encoding="utf-8"), encoding="utf-8")
        self.assertFails(f"{SKILL}:1: frontmatter must be the first block")

    def test_unterminated_frontmatter(self):
        (self.root / SKILL).write_text("---\nname: journey-metrics\n", encoding="utf-8")
        self.assertFails(f"{SKILL}:1: unterminated frontmatter")

    def test_tab_in_frontmatter(self):
        self.replace_frontmatter_line("license: MIT", "license:\tMIT")
        self.assertFails(f"{SKILL}:4: tab characters are not allowed")

    def test_non_mapping_line(self):
        self.replace_frontmatter_line("license: MIT", "license:MIT")
        self.assertFails(f"{SKILL}:4: expected 'key: value' at top level")

    def test_missing_description(self):
        path = self.root / SKILL
        text = re.sub(
            r"^description: .*\n",
            "",
            path.read_text(encoding="utf-8"),
            count=1,
            flags=re.M,
        )
        path.write_text(text, encoding="utf-8")
        self.assertFails(
            f"{SKILL}: frontmatter requires 'description'",
            "description length invalid (0)",
        )

    def test_invalid_name(self):
        for bad, fragment in (
            ("Journey_Metrics", "invalid name 'Journey_Metrics'"),
            ("", "name: must be a single-line scalar"),
        ):
            with self.subTest(name=bad):
                self.tearDown()
                self.setUp()
                self.replace_frontmatter_line(
                    "name: journey-metrics", f"name: {bad}".rstrip()
                )
                self.assertFails(fragment)

    def test_name_length(self):
        long_name = "a" * 65
        shutil.move(
            str(self.root / "skills" / "journey-metrics"),
            str(self.root / "skills" / long_name),
        )
        self.edit_text(
            f"skills/{long_name}/SKILL.md",
            "name: journey-metrics",
            f"name: {long_name}",
        )
        self.assertFails("name length invalid")

    def test_description_too_long(self):
        self.replace_frontmatter_line("description: ", "description: " + "x" * 1025)
        self.assertFails(f"{SKILL}:3: description length invalid")

    def test_description_at_limit(self):
        path = self.root / SKILL
        text = re.sub(
            r"^description: .*$",
            "description: " + "x" * 1024,
            path.read_text(encoding="utf-8"),
            count=1,
            flags=re.M,
        )
        path.write_text(text, encoding="utf-8")
        reg = json.loads((self.root / "skills.json").read_text(encoding="utf-8"))
        for item in reg["skills"]:
            if item["name"] == "journey-metrics":
                item["description"] = "x" * 1024
        (self.root / "skills.json").write_text(json.dumps(reg), encoding="utf-8")
        self.assertPasses()

    def test_too_many_lines(self):
        self.append_text(SKILL, "\n" * 500)
        self.assertFails("SKILL.md has")

    def test_missing_skill_file(self):
        (self.root / SKILL).unlink()
        self.assertFails("skills/journey-metrics: missing SKILL.md")

    def test_parent_traversal_reference(self):
        self.append_text(SKILL, "\nRead `references/../../../README.md`.\n")
        self.assertFails("unsafe relative reference references/../../../README.md")

    def test_absolute_and_backslash_references(self):
        self.append_text(
            SKILL, "\nRead (/etc/assets/passwd) and `assets\\metric-register.csv`.\n"
        )
        self.assertFails(
            "unsafe relative reference /etc/assets/passwd",
            "unsafe relative reference assets\\metric-register.csv",
        )

    def test_urls_are_not_references(self):
        self.append_text(SKILL, "\nSee (https://example.org/assets/x.png) and https://example.org/docs/y.md.\n")
        self.assertPasses()

    def test_cross_skill_mention_is_rejected(self):
        self.append_text(SKILL, "\nSee `journey-architecture/references/ontology.md`.\n")
        out = self.assertFails(f"{SKILL}:", "path into the journey-architecture skill")
        self.assertNotIn("broken relative reference", out)

    def test_reference_to_directory_is_broken(self):
        self.append_text(SKILL, "\nSee `assets/`.\n")
        self.assertFails("broken relative reference assets/")

    def test_symlink_in_skill_is_rejected(self):
        link = self.root / "skills" / "journey-metrics" / "assets" / "linked.md"
        os.symlink(self.root / "README.md", link)
        self.append_text(SKILL, "\nSee `assets/linked.md`.\n")
        self.assertFails(
            "skills/journey-metrics/assets/linked.md: symbolic links are not allowed",
            "assets/linked.md: must be a regular file",
        )

    def test_symlinked_skill_directory_is_rejected(self):
        os.symlink(
            self.root / "skills" / "journey-metrics",
            self.root / "skills" / "journey-kpis",
        )
        self.assertFails("skills/journey-kpis: symbolic links are not allowed")

    def test_symlink_in_example_system_is_rejected(self):
        os.symlink(self.root / "README.md", self.system / "readme-link.md")
        self.assertFails(f"{SYS}/readme-link.md: symbolic links are not allowed")

    def test_unexpected_entry_in_skill(self):
        (self.root / "skills" / "journey-metrics" / "hooks.sh").write_text(
            "echo", encoding="utf-8"
        )
        self.assertFails(
            "skills/journey-metrics/hooks.sh: unexpected entry in skill directory"
        )

    def test_assets_must_be_directory(self):
        shutil.rmtree(self.root / "skills" / "jobs-and-outcomes", ignore_errors=True)
        folder = self.root / "skills" / "journey-quality-audit"
        shutil.rmtree(folder / "assets")
        (folder / "assets").write_text("x", encoding="utf-8")
        self.assertFails("skills/journey-quality-audit/assets: must be a directory")

    def test_nested_directory_in_assets(self):
        (self.root / "skills" / "journey-metrics" / "assets" / "nested").mkdir()
        self.assertFails("skills/journey-metrics/assets/nested: must be a regular file")

    def test_scripts_directory_is_flagged(self):
        scripts = self.root / "skills" / "journey-metrics" / "scripts"
        scripts.mkdir()
        (scripts / "run.py").write_text("print(1)\n", encoding="utf-8")
        out = self.assertPasses()
        self.assertIn(
            "NOTICE: skills/journey-metrics/scripts/ ships executable content", out
        )

    def test_ds_store_is_ignored(self):
        (self.root / "skills" / "journey-metrics" / ".DS_Store").write_bytes(b"\0")
        (self.root / "skills" / "journey-metrics" / "assets" / ".DS_Store").write_bytes(
            b"\0"
        )
        self.assertPasses()

    def test_registry_problems(self):
        reg_path = self.root / "skills.json"
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
        reg["skills"][0]["path"] = "elsewhere"
        reg["skills"].pop()
        reg_path.write_text(json.dumps(reg), encoding="utf-8")
        self.assertFails("must be skills/", "skills.json mismatch")

    def test_registry_missing_or_malformed(self):
        reg_path = self.root / "skills.json"
        reg_path.write_text("{}", encoding="utf-8")
        self.assertFails("skills.json: malformed skills.json")
        reg_path.unlink()
        self.assertFails("skills.json: missing skills.json")


if __name__ == "__main__":
    unittest.main()
