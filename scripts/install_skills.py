#!/usr/bin/env python3
from pathlib import Path
import argparse
import shutil

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

def main():
    parser = argparse.ArgumentParser(description="Install Journey Architecture OS skills.")
    parser.add_argument("--target", default=".agents/skills", help="Destination skills directory")
    parser.add_argument("--skill", action="append", default=[], help="Skill name; may be repeated")
    parser.add_argument("--all", action="store_true", help="Install all skills")
    parser.add_argument("--list", action="store_true", help="List skills")
    parser.add_argument("--force", action="store_true", help="Replace an existing installed skill")
    args = parser.parse_args()

    available = sorted(p.name for p in SKILLS.iterdir() if p.is_dir() and (p / "SKILL.md").exists())

    if args.list:
        for name in available:
            print(name)
        return 0

    selected = available if args.all else args.skill
    if not selected:
        parser.error("use --all, --skill NAME, or --list")

    unknown = sorted(set(selected) - set(available))
    if unknown:
        parser.error("unknown skill(s): " + ", ".join(unknown))

    target = Path(args.target)
    target.mkdir(parents=True, exist_ok=True)

    for name in selected:
        src = SKILLS / name
        dst = target / name
        if dst.exists():
            if not args.force:
                raise SystemExit(f"{dst} exists; use --force to replace")
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"installed {name} -> {dst}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
