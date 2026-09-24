#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

def parse_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        raise ValueError("unterminated YAML frontmatter")
    fm = parts[1]
    data = {}
    for line in fm.splitlines():
        if line.startswith("  "):
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            data[m.group(1)] = m.group(2).strip().strip('"')
    return data, text

def main():
    errors = []
    descriptions = {}
    skill_dirs = sorted([p for p in SKILLS.iterdir() if p.is_dir()])
    for d in skill_dirs:
        f = d / "SKILL.md"
        if not f.exists():
            errors.append(f"{d.name}: missing SKILL.md")
            continue
        try:
            fm, text = parse_frontmatter(f)
        except Exception as e:
            errors.append(f"{d.name}: {e}")
            continue
        name = fm.get("name", "")
        desc = fm.get("description", "")
        if name != d.name:
            errors.append(f"{d.name}: frontmatter name must match directory")
        if not NAME_RE.fullmatch(name):
            errors.append(f"{d.name}: invalid name {name!r}")
        if not (1 <= len(name) <= 64):
            errors.append(f"{d.name}: name length invalid")
        if not (1 <= len(desc) <= 1024):
            errors.append(f"{d.name}: description length invalid ({len(desc)})")
        lines = len(text.splitlines())
        if lines > 500:
            errors.append(f"{d.name}: SKILL.md has {lines} lines; max 500 recommended")
        referenced = set(re.findall(r"[(`]((?:references|assets)/[^)`\s]+)[)`]", text))
        for rel in sorted(referenced):
            if not (d / rel).exists():
                errors.append(f"{d.name}: broken relative reference {rel}")
        for sub in ("references", "assets"):
            for extra in sorted((d / sub).glob("*")) if (d / sub).is_dir() else []:
                rel = f"{sub}/{extra.name}"
                if rel not in referenced:
                    errors.append(f"{d.name}: {rel} is not referenced from SKILL.md")
        descriptions[d.name] = desc

    registry_path = ROOT / "skills.json"
    if not registry_path.exists():
        errors.append("missing skills.json")
    else:
        reg = json.loads(registry_path.read_text(encoding="utf-8"))
        registered = {x["name"] for x in reg.get("skills", [])}
        for x in reg.get("skills", []):
            if x["name"] in descriptions and x.get("description") != descriptions[x["name"]]:
                errors.append(f"skills.json: description of {x['name']} differs from SKILL.md")
            if x.get("path") != f"skills/{x['name']}":
                errors.append(f"skills.json: path of {x['name']} must be skills/{x['name']}")
        actual = {d.name for d in skill_dirs}
        if registered != actual:
            errors.append(f"skills.json mismatch: registered={sorted(registered)} actual={sorted(actual)}")

    if errors:
        print("VALIDATION FAILED")
        for e in errors:
            print(" -", e)
        return 1

    print(f"OK: {len(skill_dirs)} skills validated")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
