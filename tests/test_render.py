"""Tests for scripts/render_map.py: determinism, self-containment, escaping, and honest gaps."""

import csv
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render_map.py"
FIXTURE = ROOT / "tests" / "fixtures" / "minimal-system"
EXAMPLE = ROOT / "examples" / "saas-onboarding"
PAYLOAD = "<img src=x onerror=alert(1)>"
# Columns that hold IDs, enumerations, numbers or dates; everything else is free text.
STRUCTURED = (
    "_id",
    "ids",
    "status",
    "level",
    "state",
    "layer",
    "relation",
    "decision",
    "type",
    "sequence",
    "direction",
    "_at",
    "version",
    "coverage",
    "days",
    "due",
    "triggers",
    "freshness",
    "valence",
)

spec = importlib.util.spec_from_file_location("render_map", SCRIPT)
render_map = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render_map)


def render(path, lang="en"):
    return render_map.render(path, lang)


def copy_system(src, tmp):
    dst = Path(tmp) / "system"
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("*.md"))
    return dst


def rewrite(path, fn):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    rows = fn(rows)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerows(rows)


class RenderTests(unittest.TestCase):
    def test_renders_fixture_and_example(self):
        for system in (FIXTURE, EXAMPLE):
            page = render(system)
            self.assertTrue(page.startswith("<!doctype html>"), system)
            self.assertIn("</html>", page)

    def test_deterministic(self):
        for system in (FIXTURE, EXAMPLE):
            self.assertEqual(render(system), render(system), system)
            self.assertEqual(render(system, "ru"), render(system, "ru"), system)

    def test_no_external_urls(self):
        for system in (FIXTURE, EXAMPLE):
            urls = set(re.findall(r"https?://[^\s\"'<>)]+", render(system)))
            self.assertLessEqual(urls, {"http://www.w3.org/2000/svg"}, system)

    def test_cli_writes_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "map.html"
            res = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(FIXTURE),
                    "-o",
                    str(out),
                    "--lang",
                    "ru",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn('<html lang="ru">', out.read_text(encoding="utf-8"))

    def test_escaping_fuzz(self):
        with tempfile.TemporaryDirectory() as tmp:
            dst = copy_system(EXAMPLE, tmp)

            def poison(rows):
                header = rows[0]
                for row in rows[1:]:
                    for i, col in enumerate(header):
                        if (
                            i < len(row)
                            and row[i]
                            and not any(k in col for k in STRUCTURED)
                        ):
                            row[i] += PAYLOAD
                return rows

            for path in dst.glob("*.csv"):
                rewrite(path, poison)
            page = render(dst)
            self.assertIn("&lt;img src=x onerror=alert(1)&gt;", page)
            self.assertNotIn(PAYLOAD, page)
            self.assertNotIn("<img", page)
            title = render_map.render(dst, "en", title=PAYLOAD)
            self.assertNotIn(PAYLOAD, title)

    def test_without_experience_register(self):
        with tempfile.TemporaryDirectory() as tmp:
            dst = copy_system(EXAMPLE, tmp)
            (dst / "experience-register.csv").unlink(missing_ok=True)
            page = render(dst)
            self.assertIn("has no experience-register.csv", page)
            self.assertIn("not measured", page)
            self.assertNotIn('class="c-solid"', page)
            self.assertNotIn('class="c-dash"', page)

    def test_emotion_curve_never_bridges_a_gap(self):
        """Stages 1 and 3 have emotion rows, stage 2 has none: no segment may cross stage 2."""
        with tempfile.TemporaryDirectory() as tmp:
            dst = copy_system(FIXTURE, tmp)
            rewrite(
                dst / "node-register.csv",
                lambda rows: (
                    rows
                    + [
                        [
                            "NOD-CUST-SAAS-ONBOARD-001-03",
                            "JRN-CUST-SAAS-ONBOARD-001",
                            "",
                            "stage",
                            "3",
                            "Work in the service",
                            "Use it every day",
                            "",
                            "hypothesis",
                        ]
                    ]
                ),
            )
            rows = [
                [
                    "node_id",
                    "row_type",
                    "text",
                    "evidence_ids",
                    "evidence_status",
                    "valence",
                ],
                [
                    "NOD-CUST-SAAS-ONBOARD-001-01",
                    "emotion",
                    "Relieved",
                    "EVD-2026-0001",
                    "observed",
                    "1",
                ],
                [
                    "NOD-CUST-SAAS-ONBOARD-001-01",
                    "emotion",
                    "Unsure",
                    "",
                    "hypothesis",
                    "-1",
                ],
                [
                    "NOD-CUST-SAAS-ONBOARD-001-03",
                    "emotion",
                    "Confident",
                    "",
                    "hypothesis",
                    "2",
                ],
                ["NOD-CUST-SAAS-ONBOARD-001-03", "pain", "Slow", "", "hypothesis", ""],
            ]
            with open(
                dst / "experience-register.csv", "w", encoding="utf-8", newline=""
            ) as fh:
                csv.writer(fh, lineterminator="\n").writerows(rows)
            page = render(dst)
            col = 248
            segs = re.findall(
                r'<line x1="([\d.]+)" y1="[\d.]+" x2="([\d.]+)" y2="[\d.]+" class="(c-solid|c-dash)"/>',
                page,
            )
            self.assertTrue(segs)
            for x1, x2, _ in segs:
                lo, hi = sorted((float(x1), float(x2)))
                self.assertFalse(
                    lo < 2 * col and hi > col,
                    "segment %s-%s crosses the unmeasured stage" % (x1, x2),
                )
            # observed -> hypothesis inside stage 1 must be dashed, never solid
            self.assertNotIn('class="c-solid"', page)
            self.assertIn("not measured", page)
            self.assertIn("Slow", page)

    def test_invalid_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            dst = copy_system(FIXTURE, tmp)

            def break_status(rows):
                i = rows[0].index("evidence_status")
                rows[1][i] = "confirmed"
                return rows

            rewrite(dst / "node-register.csv", break_status)
            res = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(dst),
                    "-o",
                    str(Path(tmp) / "m.html"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 2)
            self.assertIn("confirmed", res.stderr)


if __name__ == "__main__":
    unittest.main()
