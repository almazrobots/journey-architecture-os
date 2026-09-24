import json
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_evals.py"
FAKE_CMD = f"{shlex.quote(sys.executable)} {shlex.quote(str(ROOT / 'tests' / 'fake_agent.py'))}"

sys.path.insert(0, str(ROOT / "scripts"))
import run_evals  # noqa: E402


def run(*args, env_state=None):
    env = None
    if env_state is not None:
        import os
        env = dict(os.environ, FAKE_AGENT_STATE=str(env_state))
    return subprocess.run([sys.executable, str(RUNNER), *args], capture_output=True, text=True, env=env)


ROUTING_CASES = [json.loads(line) for line in (ROOT / "evals" / "routing.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
BEHAVIOR_SCENARIOS = sorted((ROOT / "evals" / "behavior").glob("*.json"))


class CheckTests(unittest.TestCase):
    def test_repository_evals_pass_check(self):
        result = run("--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"{len(ROUTING_CASES)} routing cases", result.stdout)
        self.assertIn(f"{len(BEHAVIOR_SCENARIOS)} behavior scenarios", result.stdout)

    def _broken_copy(self, mutate):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        shutil.copytree(ROOT / "evals", tmp / "evals", ignore=shutil.ignore_patterns("results"))
        mutate(tmp / "evals")
        return run("--check", "--evals-dir", str(tmp / "evals"))

    def test_check_rejects_unknown_skill_duplicate_id_and_bad_regex(self):
        def mutate(evals):
            lines = (evals / "routing.jsonl").read_text(encoding="utf-8").splitlines()
            first = json.loads(lines[0])
            dup = dict(first, expected=["no-such-skill"], difficulty="medium")
            lines.append(json.dumps(dup))
            d = json.loads((evals / "distractors.json").read_text(encoding="utf-8"))
            d["skills"].append({"name": "journey-metrics", "description": "clash"})
            (evals / "distractors.json").write_text(json.dumps(d), encoding="utf-8")
            (evals / "routing.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
            path = sorted((evals / "behavior").glob("*.json"))[0]
            sc = json.loads(path.read_text(encoding="utf-8"))
            sc["assertions"].append({"id": "broken", "type": "regex", "category": "convention", "pattern": "(unclosed"})
            path.write_text(json.dumps(sc), encoding="utf-8")

        result = self._broken_copy(mutate)
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate id", result.stdout)
        self.assertIn("'no-such-skill' does not exist", result.stdout)
        self.assertIn("regex does not compile", result.stdout)
        self.assertIn("difficulty must be one of", result.stdout)
        self.assertIn("collides with a real skill", result.stdout)

    def test_check_requires_coverage_of_every_skill(self):
        def mutate(evals):
            kept = [l for l in (evals / "routing.jsonl").read_text(encoding="utf-8").splitlines()
                    if '"expected": ["journey-governance"]' not in l]
            (evals / "routing.jsonl").write_text("\n".join(kept) + "\n", encoding="utf-8")

        result = self._broken_copy(mutate)
        self.assertEqual(result.returncode, 1)
        self.assertIn("no case expects skill 'journey-governance'", result.stdout)
        self.assertIn("'journey-governance' has 0 hard cases (minimum 5)", result.stdout)


class DiscoveryTests(unittest.TestCase):
    def test_routing_prompt_lists_every_skill_from_frontmatter(self):
        skills = run_evals.load_skills()
        registry = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))["skills"]
        self.assertEqual({s["name"] for s in skills}, {e["name"] for e in registry})
        prompt = run_evals.routing_prompt(skills, "hello")
        for s in skills:
            self.assertTrue(s["description"])
            self.assertIn(f"<name>{s['name']}</name>\n<description>{s['description']}</description>", prompt)

    def test_frontmatter_parser_handles_folded_and_quoted_scalars(self):
        text = "---\nname: 'x-skill'\ndescription: >\n  Line one\n  line two.\nmetadata:\n  a: b\n---\nBody\n"
        fm, body = run_evals.parse_frontmatter(text)
        self.assertEqual(fm, {"name": "x-skill", "description": "Line one line two."})
        self.assertEqual(body.strip(), "Body")

    def test_with_skill_prompt_loads_referenced_files(self):
        skill = next(s for s in run_evals.load_skills() if s["name"] == "journey-research")
        scenario = {"prompt": "p", "input_material": "m"}
        prompt = run_evals.generation_prompt(scenario, skill)
        self.assertIn('<skill name="journey-research">', prompt)
        self.assertIn('<skill_file path="journey-research/references/evidence-model.md">', prompt)
        self.assertNotIn("<skill", run_evals.generation_prompt(scenario, None))

    def test_id_grammar_assertion(self):
        a = json.loads((ROOT / "evals" / "behavior" / "BH-01-research-returns.json").read_text())["assertions"][0]
        self.assertTrue(run_evals.grade_regex(a, "See EVD-2026-0001 and NOD-CUST-RETURN-001-02.")[0])
        self.assertFalse(run_evals.grade_regex(a, "See EVD-26-1.")[0])
        self.assertFalse(run_evals.grade_regex(a, "No identifiers at all.")[0])
        self.assertTrue(run_evals.grade_regex(a, "Change CHG-0904 cites EVD-2026-0001.")[0])
        self.assertFalse(run_evals.grade_regex(a, "Change CHG-12 cites EVD-2026-0001.")[0])

    def test_id_prefixes_come_from_the_ontology(self):
        text = (ROOT / "skills" / "journey-architecture" / "references" / "ontology.md").read_text(encoding="utf-8")
        prefixes = [p for p, _ in run_evals.ontology_id_patterns()]
        self.assertIn("CHG", prefixes)
        for prefix in prefixes:
            self.assertIn(f"`{prefix}`", text)
        self.assertEqual(run_evals.normalize_for_judge("CHG-0904 and INI-0007"), "[ID-1] and [ID-2]")
        self.assertEqual(run_evals.resolve_pattern("plain"), "plain")

    def test_model_runner_removes_its_temp_dir(self):
        runner = run_evals.ModelRunner("true", None, 5)
        cwd = Path(runner._cwd)
        self.assertTrue(cwd.is_dir())
        runner.close()
        self.assertFalse(cwd.exists())

    def test_help_points_to_documentation(self):
        out = run("--help").stdout
        self.assertIn("docs/evaluations.md", out)


class EndToEndTests(unittest.TestCase):
    """Full runner with a fake model command: no network."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.evals = self.tmp / "evals"
        (self.evals / "behavior").mkdir(parents=True)
        self.state = self.tmp / "state"
        self.state.mkdir()

    def _write_routing(self, cases, distractors=None):
        cases = [dict({"difficulty": "easy"}, **c) for c in cases]
        (self.evals / "routing.jsonl").write_text(
            "\n".join(json.dumps(c) for c in cases) + "\n", encoding="utf-8")
        if distractors is not None:
            (self.evals / "distractors.json").write_text(
                json.dumps({"skills": distractors}), encoding="utf-8")

    def _results(self, mode):
        files = list((self.tmp / "results").glob(f"*-{mode}*.json"))
        self.assertEqual(len(files), 1)
        md = files[0].with_suffix(".md")
        self.assertTrue(md.exists())
        return json.loads(files[0].read_text(encoding="utf-8")), md.read_text(encoding="utf-8")

    def test_routing_scoring_confusion_and_retry(self):
        self._write_routing([
            {"id": "c1", "prompt": "map it [[answer:customer-journey-mapping]]",
             "expected": ["customer-journey-mapping"], "acceptable": [], "notes": ""},
            {"id": "c2", "heldout": True, "prompt": "fix first [[answer:journey-metrics]]",
             "expected": ["experience-opportunity-prioritization"], "acceptable": ["journey-metrics"], "notes": ""},
            {"id": "c3", "prompt": "audit [[answer:service-blueprinting]] [[malformed-first]]",
             "expected": ["journey-quality-audit"], "acceptable": [], "notes": ""},
            {"id": "c4", "prompt": "sql tuning", "expected": ["none"], "acceptable": [], "notes": ""},
        ])
        result = run("--mode", "routing", "--cmd", FAKE_CMD, "--evals-dir", str(self.evals),
                     "--results-dir", str(self.tmp / "results"), "--jobs", "2", env_state=self.state)
        self.assertEqual(result.returncode, 0, result.stderr)
        data, md = self._results("routing")
        s = data["summary"]
        self.assertEqual(s["cases"], 4)
        self.assertEqual(s["exact_accuracy"], 0.5)        # c1, c4
        self.assertEqual(s["acceptable_accuracy"], 0.75)  # + c2
        self.assertEqual(s["errors"], 0)
        self.assertEqual(s["by_split"]["heldout"], {"cases": 1, "exact_accuracy": 0.0, "acceptable_accuracy": 1.0})
        self.assertEqual(s["by_split"]["development"]["cases"], 3)
        self.assertEqual(data["acceptable_not_exact"],
                         [{"id": "c2", "expected": "experience-opportunity-prioritization", "predicted": "journey-metrics"}])
        self.assertIn("### Acceptable but not the expected primary", md)
        self.assertIn("### Misses (neither expected nor acceptable)", md)
        self.assertIn("## Held-out vs development cases", md)
        c3 = next(c for c in data["cases"] if c["id"] == "c3")
        self.assertEqual(len(c3["attempts"]), 2)           # one malformed answer, one retry
        self.assertEqual(data["per_skill"]["journey-quality-audit"]["confusions"],
                         [{"id": "c3", "predicted": "service-blueprinting"}])
        self.assertEqual(data["meta"]["model_calls"], 5)
        self.assertIn("| 4 | 50.0% | 75.0% | 0 |", md)

    def test_routing_filters_and_dry_run(self):
        self._write_routing([
            {"id": f"c{i}", "prompt": f"p{i}", "expected": ["none"], "acceptable": [], "notes": ""} for i in range(5)
        ])
        dry = run("--mode", "routing", "--cmd", "false", "--evals-dir", str(self.evals), "--dry-run", "--case", "c3")
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertIn("===== c3 (seed ", dry.stdout)
        self.assertNotIn("===== c1 ", dry.stdout)
        self.assertFalse((self.evals / "results").exists())
        result = run("--mode", "routing", "--cmd", FAKE_CMD, "--evals-dir", str(self.evals),
                     "--results-dir", str(self.tmp / "results"), "--limit", "2", env_state=self.state)
        self.assertEqual(result.returncode, 0, result.stderr)
        data, _ = self._results("routing")
        self.assertEqual([c["id"] for c in data["cases"]], ["c0", "c1"])
        self.assertEqual(data["summary"]["exact_accuracy"], 1.0)

    def test_failing_command_is_reported_not_crashing(self):
        self._write_routing([{"id": "c1", "prompt": "p", "expected": ["none"], "acceptable": [], "notes": ""}])
        result = run("--mode", "routing", "--cmd", "false", "--evals-dir", str(self.evals),
                     "--results-dir", str(self.tmp / "results"), "--retries", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        data, _ = self._results("routing")
        self.assertEqual(data["cases"][0]["predicted"], "__error__")
        self.assertEqual(len(data["cases"][0]["attempts"]), 2)
        self.assertEqual(data["summary"]["errors"], 1)

    def test_behavior_grading_and_delta(self):
        self._write_routing([{"id": "c1", "prompt": "p", "expected": ["none"], "acceptable": [], "notes": ""}])
        scenario = {
            "id": "S1", "skill": "journey-research", "prompt": "Synthesize.", "input_material": "VP: customers love it.",
            "assertions": [
                {"id": "ids", "type": "regex", "category": "convention",
                 "pattern": r"\bEVD-[A-Z0-9]+(?:-[A-Z0-9]+)*", "every_match": r"EVD-[0-9]{4}-[0-9]{4}"},
                {"id": "statuses", "type": "regex", "category": "convention", "flags": "i",
                 "all_of": [r"\bobserved\b", r"\binferred\b", r"\bhypothesis\b", r"\bunknown\b"]},
                {"id": "no-love", "type": "regex", "category": "method", "pattern": r"customers love", "negate": True,
                 "flags": "i"},
                {"id": "judged", "type": "judge", "category": "method",
                 "question": "Is the VP claim labeled a hypothesis?", "pass_criteria": "PASS if labeled."},
            ],
        }
        (self.evals / "behavior" / "S1.json").write_text(json.dumps(scenario), encoding="utf-8")
        result = run("--mode", "behavior", "--cmd", FAKE_CMD, "--evals-dir", str(self.evals),
                     "--results-dir", str(self.tmp / "results"), env_state=self.state)
        self.assertEqual(result.returncode, 0, result.stderr)
        data, md = self._results("behavior")
        s = data["summary"]
        self.assertEqual(s["conditions"]["with_skill"]["pass_rate"], 1.0)
        self.assertEqual(s["conditions"]["baseline"]["pass_rate"], 0.0)
        self.assertEqual(s["delta_pp"], 100.0)
        self.assertEqual(s["delta_pp_by_category"], {"convention": 100.0, "method": 100.0})
        self.assertEqual(s["judge_errors"], 0)
        self.assertEqual(data["meta"]["model_calls"], 4)   # 2 generations + 2 judge calls
        baseline = data["scenarios"][0]["conditions"]["baseline"]
        rows = baseline["runs"][0]["assertions"]
        self.assertIn("invalid: ['EVD-26-1']", next(a for a in rows if a["id"] == "ids")["reason"])
        self.assertEqual({a["id"]: (a["passes"], a["n"]) for a in baseline["per_assertion"]},
                         {"ids": (0, 1), "statuses": (0, 1), "no-love": (0, 1), "judged": (0, 1)})
        self.assertIn("| All assertions | 100.0% | 0.0% | +100.0 pp |", md)
        self.assertEqual(s["significance"]["method"]["assertions_better"], 2)

    def test_behavior_repeats_counts_and_statistics(self):
        self._write_routing([{"id": "c1", "prompt": "p", "expected": ["none"], "acceptable": [], "notes": ""}])
        judged = {"id": "judged", "type": "judge", "category": "method",
                  "question": "Q?", "pass_criteria": "PASS if the token is present."}
        for i, material in enumerate(["stable", "[[flaky-baseline]]"]):
            sc = {"id": f"S{i}", "skill": "journey-research", "prompt": "Do it.", "input_material": material,
                  "notes": "SECRET-TRAP-NOTE", "assertions": [judged]}
            (self.evals / "behavior" / f"S{i}.json").write_text(json.dumps(sc), encoding="utf-8")
        dry = run("--mode", "behavior", "--evals-dir", str(self.evals), "--dry-run", "--repeats", "3")
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertIn("[with_skill] x3", dry.stdout)
        self.assertNotIn("SECRET-TRAP-NOTE", dry.stdout)      # trap notes never reach the model or judge
        result = run("--mode", "behavior", "--cmd", FAKE_CMD, "--evals-dir", str(self.evals),
                     "--results-dir", str(self.tmp / "results"), "--repeats", "3", "--jobs", "1",
                     env_state=self.state)
        self.assertEqual(result.returncode, 0, result.stderr)
        data, md = self._results("behavior")
        s = data["summary"]
        self.assertEqual(s["repeats"], 3)
        self.assertEqual(data["meta"]["model_calls"], 2 * 2 * 3 * 2)   # scenarios x conditions x repeats x (gen + judge)
        by_id = {sc["id"]: sc for sc in data["scenarios"]}
        self.assertEqual(by_id["S0"]["conditions"]["baseline"]["per_assertion"][0]["passes"], 0)
        self.assertEqual(by_id["S1"]["conditions"]["baseline"]["per_assertion"][0]["passes"], 2)   # flaky: 2/3
        self.assertEqual(by_id["S1"]["conditions"]["with_skill"]["per_assertion"][0]["passes"], 3)
        self.assertEqual(len(by_id["S1"]["conditions"]["baseline"]["runs"]), 3)
        self.assertEqual(s["conditions"]["with_skill"]["pass_rate"], 1.0)
        self.assertAlmostEqual(s["conditions"]["baseline"]["pass_rate"], 2 / 6, places=3)
        sig = s["significance"]["method"]
        self.assertEqual((sig["assertions_better"], sig["assertions_worse"], sig["assertions_tied"]), (2, 0, 0))
        self.assertEqual(sig["sign_test_p"], 0.5)
        self.assertAlmostEqual(sig["delta_pp"], 66.7, places=1)
        lo, hi = sig["ci95_pp"]
        self.assertTrue(33.3 - 0.1 <= lo <= hi <= 100.0 + 0.1)
        self.assertIn("| S1 | judged | method | 3/3 | 2/3 |", md)
        self.assertIn("## Is the difference real?", md)

    def test_sign_test(self):
        self.assertEqual(run_evals.sign_test_p(8, 0), 0.0078)
        self.assertEqual(run_evals.sign_test_p(3, 3), 1.0)
        self.assertIsNone(run_evals.sign_test_p(0, 0))

    def test_full_repository_suites_run_with_fake_agent(self):
        for mode in ("routing", "behavior"):
            result = run("--mode", mode, "--cmd", FAKE_CMD, "--results-dir", str(self.tmp / "results"),
                         "--jobs", "4", env_state=self.state)
            self.assertEqual(result.returncode, 0, result.stderr)
        routing, _ = self._results("routing")
        self.assertEqual(routing["summary"]["cases"], len(ROUTING_CASES))
        self.assertEqual(routing["summary"]["candidate_skills"], 15 + len(run_evals.load_distractors(ROOT / "evals")))
        none_cases = sum(1 for c in ROUTING_CASES if c["expected"] == ["none"])
        self.assertAlmostEqual(routing["summary"]["exact_accuracy"], none_cases / len(ROUTING_CASES), places=3)  # fake says "none"
        self.assertEqual(routing["summary"]["by_difficulty"]["easy"]["cases"]
                         + routing["summary"]["by_difficulty"]["hard"]["cases"], len(ROUTING_CASES))
        behavior, _ = self._results("behavior")
        self.assertEqual(behavior["summary"]["scenarios"], len(BEHAVIOR_SCENARIOS))
        self.assertEqual(behavior["summary"]["generation_errors"], 0)

    DISTRACTORS = [
        {"name": "process-mapping", "description": "Documents business processes in BPMN."},
        {"name": "incident-postmortem", "description": "Writes outage postmortems."},
    ]

    def test_distractors_steals_over_triggers_and_difficulty(self):
        self._write_routing([
            {"id": "d1", "difficulty": "hard", "prompt": "bpmn [[answer:process-mapping]]",
             "expected": ["process-mapping"], "acceptable": [], "notes": ""},
            {"id": "d2", "difficulty": "hard", "prompt": "outage [[answer:service-blueprinting]]",
             "expected": ["incident-postmortem"], "acceptable": [], "notes": ""},
            {"id": "d3", "difficulty": "hard", "prompt": "blueprint [[answer:process-mapping]]",
             "expected": ["service-blueprinting"], "acceptable": [], "notes": ""},
            {"id": "d4", "prompt": "cjm [[answer:customer-journey-mapping]]",
             "expected": ["customer-journey-mapping"], "acceptable": [], "notes": ""},
        ], distractors=self.DISTRACTORS)
        result = run("--mode", "routing", "--cmd", FAKE_CMD, "--evals-dir", str(self.evals),
                     "--results-dir", str(self.tmp / "results"), "--seed", "7", env_state=self.state)
        self.assertEqual(result.returncode, 0, result.stderr)
        data, md = self._results("routing")
        s = data["summary"]
        self.assertTrue(s["distractors"])
        self.assertEqual(s["candidate_skills"], 17)
        self.assertEqual(s["base_seed"], 7)
        self.assertEqual(s["exact_accuracy"], 0.5)                       # d1, d4
        self.assertEqual(s["by_difficulty"]["hard"], {"cases": 3, "exact_accuracy": 0.3333, "acceptable_accuracy": 0.3333})
        self.assertEqual(s["by_difficulty"]["easy"]["exact_accuracy"], 1.0)
        self.assertEqual(s["distractor_steals"], 1)                      # d3
        self.assertEqual(s["over_triggers"], 1)                          # d2
        self.assertEqual({(c["expected"], c["predicted"]) for c in data["confusion_pairs"]},
                         {("incident-postmortem", "service-blueprinting"), ("service-blueprinting", "process-mapping")})
        seeds = {c["id"]: c["seed"] for c in data["cases"]}
        self.assertEqual(seeds["d1"], run_evals.case_seed(7, "d1"))
        self.assertIn("## By difficulty", md)
        self.assertIn("## Non-exact cases", md)
        self.assertIn("(distractor steal)", md)

    def test_no_distractors_condition(self):
        self._write_routing([
            {"id": "d1", "prompt": "bpmn", "expected": ["process-mapping"], "acceptable": [], "notes": ""},
            {"id": "d2", "prompt": "x [[answer:journey-research]]", "expected": ["journey-research"],
             "acceptable": ["process-mapping"], "notes": ""},
        ], distractors=self.DISTRACTORS)
        dry = run("--mode", "routing", "--evals-dir", str(self.evals), "--dry-run", "--no-distractors")
        self.assertNotIn("<name>process-mapping</name>", dry.stdout)
        dry = run("--mode", "routing", "--evals-dir", str(self.evals), "--dry-run")
        self.assertIn("<name>process-mapping</name>", dry.stdout)
        result = run("--mode", "routing", "--cmd", FAKE_CMD, "--evals-dir", str(self.evals),
                     "--results-dir", str(self.tmp / "results"), "--no-distractors", env_state=self.state)
        self.assertEqual(result.returncode, 0, result.stderr)
        files = list((self.tmp / "results").glob("*-routing-no-distractors.json"))
        self.assertEqual(len(files), 1)
        data = json.loads(files[0].read_text(encoding="utf-8"))
        d1 = next(c for c in data["cases"] if c["id"] == "d1")
        self.assertEqual(d1["expected"], "none")      # distractor-expected case becomes "not ours"
        self.assertTrue(d1["exact"])
        d2 = next(c for c in data["cases"] if c["id"] == "d2")
        self.assertEqual(d2["acceptable"], [])
        self.assertEqual(data["summary"]["candidate_skills"], 15)

    def test_shuffle_is_deterministic_per_case_and_varies_across_cases(self):
        skills = [{"name": s["name"], "description": s["description"]} for s in run_evals.load_skills()]
        a1 = [s["name"] for s in run_evals.shuffled_listing(skills, run_evals.case_seed(0, "A"))]
        a2 = [s["name"] for s in run_evals.shuffled_listing(list(reversed(skills)), run_evals.case_seed(0, "A"))]
        b = [s["name"] for s in run_evals.shuffled_listing(skills, run_evals.case_seed(0, "B"))]
        self.assertEqual(a1, a2)
        self.assertNotEqual(a1, b)
        self.assertEqual(sorted(a1), sorted(s["name"] for s in skills))


class JudgeBlindnessTests(unittest.TestCase):
    def test_normalize_replaces_ids_consistently_and_skill_names(self):
        text = ("EVD-2026-0001 supports NOD-CUST-MOVE-001-02; see EVD-2026-0001 and MTM-0003. "
                "Route to `service-blueprinting`. The observed claim stays.")
        out = run_evals.normalize_for_judge(text)
        self.assertEqual(out, "[ID-1] supports [ID-2]; see [ID-1] and [ID-3]. Route to [SKILL]. The observed claim stays.")

    def test_method_judges_get_normalized_text_convention_judges_do_not(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        evals = tmp / "evals"
        (evals / "behavior").mkdir(parents=True)
        (evals / "routing.jsonl").write_text(json.dumps(
            {"id": "c1", "difficulty": "easy", "prompt": "p", "expected": ["none"], "acceptable": [], "notes": ""}) + "\n")
        sc = {"id": "S", "skill": "journey-research", "prompt": "Do it.", "input_material": "[[convention-judge]] m",
              "assertions": [
                  {"id": "m", "type": "judge", "category": "method", "question": "Q", "pass_criteria": "C"},
              ]}
        (evals / "behavior" / "S.json").write_text(json.dumps(sc))
        result = run("--mode", "behavior", "--cmd", FAKE_CMD, "--evals-dir", str(evals),
                     "--results-dir", str(tmp / "results"), env_state=tmp)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(next((tmp / "results").glob("*-behavior.json")).read_text())
        with_rows = data["scenarios"][0]["conditions"]["with_skill"]["runs"][0]["assertions"]
        self.assertTrue(with_rows[0]["passed"], with_rows[0]["reason"])   # IDs were masked before judging
        raw_output = data["scenarios"][0]["conditions"]["with_skill"]["runs"][0]["output"]
        self.assertIn("EVD-2026-0001", raw_output)                          # raw output is kept in results


class IntegrityTests(unittest.TestCase):
    """Results provenance: commit, dirty flag, file hashes, refusal to publish dirty results."""

    def setUp(self):
        if shutil.which("git") is None:
            self.skipTest("git not available")
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.repo = self.tmp / "repo"
        shutil.copytree(ROOT, self.repo, ignore=shutil.ignore_patterns(".git", "__pycache__", "results", ".venv"))
        routing = self.repo / "evals" / "routing.jsonl"
        routing.write_text("\n".join(routing.read_text().splitlines()[:3]) + "\n")
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", "snapshot")
        self.state = self.tmp / "state"
        self.state.mkdir()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True, text=True, check=True).stdout

    def run_copy(self, *args):
        import os
        env = dict(os.environ, FAKE_AGENT_STATE=str(self.state))
        return subprocess.run([sys.executable, str(self.repo / "scripts" / "run_evals.py"), "--mode", "routing",
                               "--cmd", FAKE_CMD, *args],
                              capture_output=True, text=True, env=env, cwd=self.repo)

    def results(self, pattern="*-routing*.json"):
        return sorted((self.repo / "evals" / "results").glob(pattern))

    def meta(self, path):
        return json.loads(path.read_text())["meta"]

    def test_clean_full_run_is_a_release_with_hashes_and_latest_pointer(self):
        result = self.run_copy()
        self.assertEqual(result.returncode, 0, result.stderr)
        [js] = self.results()
        self.assertRegex(js.name, r"^\d{4}-\d{2}-\d{2}T\d{4}-routing\.json$")
        meta = self.meta(js)
        self.assertEqual(meta["commit"], self.git("rev-parse", "HEAD").strip())
        self.assertFalse(meta["dirty"])
        self.assertFalse(meta["partial"])
        self.assertTrue(meta["release"])
        skill_md = "skills/journey-research/SKILL.md"
        self.assertEqual(meta["loaded_files"][skill_md], run_evals.file_sha256(self.repo / skill_md))
        self.assertIn("evals/distractors.json", meta["loaded_files"])
        md = js.with_suffix(".md").read_text()
        self.assertNotIn("DIRTY", md)
        self.assertNotIn("Partial run", md)
        latest = json.loads((self.repo / "evals" / "results" / "latest.json").read_text())
        self.assertEqual(latest["routing"]["file"], js.name)

        # a second run never overwrites the first, and results do not make the tree dirty
        again = self.run_copy()
        self.assertEqual(again.returncode, 0, again.stderr)
        files = self.results()
        self.assertEqual(len(files), 2)
        latest = json.loads((self.repo / "evals" / "results" / "latest.json").read_text())
        second = next(f for f in files if f.name != js.name)
        self.assertEqual(second.name, js.name.replace(".json", "-2.json"))
        self.assertEqual(latest["routing"]["file"], second.name)

    def test_filtered_run_is_not_a_release_and_does_not_move_latest(self):
        result = self.run_copy("--limit", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        [js] = self.results()
        self.assertTrue(js.name.endswith("-routing-limit1.json"), js.name)
        meta = self.meta(js)
        self.assertTrue(meta["partial"])
        self.assertFalse(meta["release"])
        self.assertIn("Partial run - not a release result", js.with_suffix(".md").read_text())
        self.assertFalse((self.repo / "evals" / "results" / "latest.json").exists())
        case = self.run_copy("--case", "RT-01-cjm-clear", "--no-distractors")
        self.assertEqual(case.returncode, 0, case.stderr)
        self.assertEqual(len(self.results("*-routing-no-distractors-case1.json")), 1)

    def test_dirty_tree_is_refused_unless_allowed_and_then_marked(self):
        path = self.repo / "skills" / "journey-research" / "SKILL.md"
        path.write_text(path.read_text() + "\nlocal edit\n")
        refused = self.run_copy()
        self.assertEqual(refused.returncode, 2)
        self.assertIn("dirty working tree", refused.stderr)
        self.assertEqual(self.results(), [])
        allowed = self.run_copy("--allow-dirty")
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        [js] = self.results()
        meta = self.meta(js)
        self.assertTrue(meta["dirty"])
        self.assertFalse(meta["release"])
        self.assertIn("skills/journey-research/SKILL.md", meta["changed_files"])
        self.assertIn("DIRTY - not a release result", js.with_suffix(".md").read_text())
        self.assertFalse((self.repo / "evals" / "results" / "latest.json").exists())

    def test_dirty_tree_may_write_elsewhere_but_is_still_marked(self):
        (self.repo / "scratch.txt").write_text("untracked")
        out = self.tmp / "elsewhere"
        result = self.run_copy("--results-dir", str(out))
        self.assertEqual(result.returncode, 0, result.stderr)
        md = next(out.glob("*-routing.md")).read_text()
        self.assertIn("DIRTY - not a release result", md)


if __name__ == "__main__":
    unittest.main()
