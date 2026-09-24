#!/usr/bin/env python3
"""Install Journey Architecture OS skills into an agent's skills directory."""

from pathlib import Path
import argparse
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def assert_no_symlinks(src):
    """Refuse to install a skill that contains symlinks: copying would follow them outside the repository."""
    for path in [src, *src.rglob("*")]:
        if path.is_symlink():
            raise SystemExit(
                f"refusing to install {src.name}: {path.relative_to(SKILLS)} is a symlink"
            )


def assert_safe_target(target):
    """Refuse a target that is, contains, or sits inside the repository's own skills directory."""
    resolved = target.resolve()
    source = SKILLS.resolve()
    if resolved == source or source in resolved.parents or resolved in source.parents:
        raise SystemExit(
            f"refusing to install into {target}: it overlaps the source directory {SKILLS}"
        )


def install(src, dst, force):
    """Copy src to dst via a temporary sibling directory, then swap it into place."""
    if dst.is_symlink():
        raise SystemExit(f"{dst} is a symlink; refusing to replace it")
    if dst.exists() and not dst.is_dir():
        raise SystemExit(f"{dst} exists and is not a directory; remove it first")
    if dst.exists() and not force:
        raise SystemExit(f"{dst} exists; use --force to replace it")

    staging = Path(tempfile.mkdtemp(prefix=f".{dst.name}.", dir=dst.parent))
    try:
        staged = staging / dst.name
        shutil.copytree(src, staged, symlinks=True)
        if dst.exists():
            retired = staging / f"{dst.name}.old"
            dst.rename(retired)
        staged.rename(dst)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(
        description="Install Journey Architecture OS skills."
    )
    parser.add_argument(
        "--target", default=".agents/skills", help="Destination skills directory"
    )
    parser.add_argument(
        "--skill", action="append", default=[], help="Skill name; may be repeated"
    )
    parser.add_argument("--all", action="store_true", help="Install all skills")
    parser.add_argument("--list", action="store_true", help="List skills")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing installed skill"
    )
    args = parser.parse_args()

    available = sorted(
        p.name for p in SKILLS.iterdir() if p.is_dir() and (p / "SKILL.md").exists()
    )

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
    assert_safe_target(target)
    if target.exists() and not target.is_dir():
        raise SystemExit(f"{target} exists and is not a directory")
    target.mkdir(parents=True, exist_ok=True)

    for name in selected:
        src = SKILLS / name
        assert_no_symlinks(src)
        install(src, target / name, args.force)
        print(f"installed {name} -> {target / name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
