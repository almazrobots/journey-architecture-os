import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def run_installer(self, root, *args):
        return subprocess.run(
            [sys.executable, str(root / "scripts" / "install_skills.py"), *args],
            capture_output=True,
            text=True,
        )

    def copy_repo(self, tmp):
        copy = Path(tmp) / "repo"
        shutil.copytree(
            ROOT, copy, ignore=shutil.ignore_patterns(".git", "__pycache__")
        )
        return copy

    def test_installs_all_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            result = self.run_installer(ROOT, "--all", "--target", str(target))
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = {p.parent.name for p in target.glob("*/SKILL.md")}
            expected = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
            self.assertEqual(installed, expected)

    def test_unknown_skill_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_installer(ROOT, "--skill", "../../etc", "--target", tmp)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unknown skill", result.stderr)

    def test_existing_install_requires_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = ("--skill", "journey-metrics", "--target", tmp)
            self.assertEqual(self.run_installer(ROOT, *args).returncode, 0)
            self.assertNotEqual(self.run_installer(ROOT, *args).returncode, 0)
            self.assertEqual(self.run_installer(ROOT, *args, "--force").returncode, 0)

    def test_skill_containing_symlink_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.copy_repo(tmp)
            secret = Path(tmp) / "secret.txt"
            secret.write_text("outside the repository", encoding="utf-8")
            os.symlink(
                secret, repo / "skills" / "journey-metrics" / "assets" / "leak.txt"
            )
            target = Path(tmp) / "installed"
            result = self.run_installer(
                repo, "--skill", "journey-metrics", "--target", str(target)
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("is a symlink", result.stderr + result.stdout)
            self.assertFalse((target / "journey-metrics").exists())

    def test_symlinked_destination_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            elsewhere = Path(tmp) / "elsewhere"
            elsewhere.mkdir()
            target = Path(tmp) / "installed"
            target.mkdir()
            os.symlink(elsewhere, target / "journey-metrics")
            result = self.run_installer(
                ROOT, "--skill", "journey-metrics", "--target", str(target), "--force"
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(elsewhere.exists())

    def test_target_overlapping_source_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.copy_repo(tmp)
            for target in (repo / "skills", repo / "skills" / "nested", repo):
                result = self.run_installer(repo, "--skill", "journey-metrics", "--target", str(target), "--force")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("overlaps the source directory", result.stderr + result.stdout)
            self.assertTrue((repo / "skills" / "journey-metrics" / "SKILL.md").exists())

    def test_file_at_destination_gives_clear_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "journey-metrics").write_text("not a directory", encoding="utf-8")
            result = self.run_installer(ROOT, "--skill", "journey-metrics", "--target", tmp, "--force")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("is not a directory", result.stderr + result.stdout)
            self.assertNotIn("Traceback", result.stderr)

    def test_force_replaces_content_and_leaves_no_staging(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = ("--skill", "journey-metrics", "--target", tmp)
            self.assertEqual(self.run_installer(ROOT, *args).returncode, 0)
            stale = Path(tmp) / "journey-metrics" / "stale.txt"
            stale.write_text("old", encoding="utf-8")
            self.assertEqual(self.run_installer(ROOT, *args, "--force").returncode, 0)
            self.assertFalse(stale.exists())
            self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), ["journey-metrics"])


if __name__ == "__main__":
    unittest.main()
