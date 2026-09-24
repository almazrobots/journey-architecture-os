import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class RepositoryTests(unittest.TestCase):
    def test_expected_core_skills_exist(self):
        expected = {
            "journey-architecture",
            "journey-research",
            "customer-journey-mapping",
            "employee-journey-mapping",
            "service-blueprinting",
            "journey-metrics",
            "journey-governance",
            "journey-quality-audit",
        }
        actual = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertTrue(expected.issubset(actual))

    def test_registry_paths_exist(self):
        reg = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))
        for item in reg["skills"]:
            self.assertTrue((ROOT / item["path"] / "SKILL.md").exists())

    def test_skill_frontmatter_names_match(self):
        for p in (ROOT / "skills").glob("*/SKILL.md"):
            text = p.read_text(encoding="utf-8")
            m = re.search(r"^name:\s*(.+)$", text, re.M)
            self.assertIsNotNone(m)
            self.assertEqual(m.group(1).strip(), p.parent.name)

    def test_skill_files_under_500_lines(self):
        for p in (ROOT / "skills").glob("*/SKILL.md"):
            self.assertLessEqual(len(p.read_text(encoding="utf-8").splitlines()), 500)

class ValidatorTests(unittest.TestCase):
    """The validator must reject the defects it exists to catch."""

    def run_validator_on_copy(self, mutate):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "repo"
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            mutate(copy)
            return subprocess.run(
                [sys.executable, str(copy / "scripts" / "validate_repo.py")],
                capture_output=True, text=True,
            )

    def test_clean_repository_passes(self):
        result = self.run_validator_on_copy(lambda repo: None)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_broken_reference_fails(self):
        def mutate(repo):
            f = repo / "skills" / "journey-metrics" / "SKILL.md"
            f.write_text(f.read_text(encoding="utf-8") + "\nRead `references/missing.md`.\n", encoding="utf-8")
        result = self.run_validator_on_copy(mutate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("broken relative reference references/missing.md", result.stdout)

    def test_unreferenced_asset_fails(self):
        def mutate(repo):
            (repo / "skills" / "journey-metrics" / "assets" / "orphan.md").write_text("x", encoding="utf-8")
        result = self.run_validator_on_copy(mutate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("assets/orphan.md is not referenced", result.stdout)

    def test_name_mismatch_fails(self):
        def mutate(repo):
            f = repo / "skills" / "journey-metrics" / "SKILL.md"
            f.write_text(f.read_text(encoding="utf-8").replace("name: journey-metrics", "name: journey-kpis", 1), encoding="utf-8")
        result = self.run_validator_on_copy(mutate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("frontmatter name must match directory", result.stdout)

    def test_registry_description_drift_fails(self):
        def mutate(repo):
            reg_path = repo / "skills.json"
            reg = json.loads(reg_path.read_text(encoding="utf-8"))
            reg["skills"][0]["description"] = "stale"
            reg_path.write_text(json.dumps(reg), encoding="utf-8")
        result = self.run_validator_on_copy(mutate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("differs from SKILL.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
