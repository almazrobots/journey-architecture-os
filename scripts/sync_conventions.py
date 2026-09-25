#!/usr/bin/env python3
"""Generate each skill's references/conventions.md from the ontology.

A skill may be installed on its own, without the journey-architecture skill
that holds the full contract. Each skill therefore ships a contract card: the
ID grammar, the evidence statuses, and only the registers, enumerations and
rules that the skill produces or consumes. The cards are generated from
skills/journey-architecture/references/ontology.md and must not be edited by
hand; scripts/validate_repo.py fails when a card differs from this output.

Usage:
  python3 scripts/sync_conventions.py          # write every card
  python3 scripts/sync_conventions.py --check  # exit 1 if any card is stale
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "skills" / "journey-architecture" / "references" / "ontology.md"
CARD = Path("references") / "conventions.md"

ACTOR = "actor-register.csv"
JOURNEY = "journey-registry.csv"
RELATION = "relation-register.csv"
NODE = "node-register.csv"
EVIDENCE = "evidence-register.csv"
MOMENT = "moment-register.csv"
METRIC = "metric-register.csv"
EDGE = "metric-edge-register.csv"
OPPORTUNITY = "opportunity-register.csv"
INITIATIVE = "initiative-register.csv"
PORTFOLIO = "portfolio-register.csv"
GOVERNANCE = "governance-register.csv"
CHANGES = "change-log.csv"
EXPERIENCE = "experience-register.csv"
ALL = (
    ACTOR,
    JOURNEY,
    RELATION,
    NODE,
    EVIDENCE,
    MOMENT,
    METRIC,
    EDGE,
    OPPORTUNITY,
    INITIATIVE,
    PORTFOLIO,
    GOVERNANCE,
    CHANGES,
    EXPERIENCE,
)

# Registers each skill produces or consumes.
SKILL_REGISTERS = {
    "experience-architecture": ALL,
    "journey-architecture": ALL,
    "journey-research": (ACTOR, JOURNEY, NODE, EVIDENCE),
    "customer-journey-mapping": (ACTOR, JOURNEY, RELATION, NODE, EVIDENCE, MOMENT, EXPERIENCE),
    "employee-journey-mapping": (ACTOR, JOURNEY, RELATION, NODE, EVIDENCE, MOMENT, EXPERIENCE),
    "jobs-and-outcomes": (ACTOR, JOURNEY, NODE, EVIDENCE, METRIC),
    "service-blueprinting": (JOURNEY, RELATION, NODE, EVIDENCE, OPPORTUNITY),
    "moments-that-matter": (JOURNEY, NODE, EVIDENCE, MOMENT, METRIC),
    "journey-metrics": (JOURNEY, NODE, EVIDENCE, MOMENT, METRIC, EDGE),
    "experience-opportunity-prioritization": (
        JOURNEY,
        NODE,
        EVIDENCE,
        MOMENT,
        METRIC,
        OPPORTUNITY,
        INITIATIVE,
    ),
    "target-experience-design": (
        JOURNEY,
        RELATION,
        NODE,
        EVIDENCE,
        METRIC,
        OPPORTUNITY,
        INITIATIVE,
    ),
    "journey-governance": (JOURNEY, NODE, EVIDENCE, METRIC, GOVERNANCE, CHANGES),
    "journey-portfolio-management": (
        ACTOR,
        JOURNEY,
        RELATION,
        NODE,
        METRIC,
        OPPORTUNITY,
        INITIATIVE,
        PORTFOLIO,
        GOVERNANCE,
    ),
    "journey-workshop-facilitation": (JOURNEY, NODE, EVIDENCE, MOMENT, OPPORTUNITY),
    "journey-quality-audit": ALL,
}

# Enumeration label -> registers that use it.
ENUM_REGISTERS = {
    "evidence_status": ALL,
    "level": (JOURNEY, PORTFOLIO),
    "state": (JOURNEY, PORTFOLIO),
    "status (journey)": (JOURNEY, PORTFOLIO),
    "node_type": (NODE,),
    "actor_type": (ACTOR,),
    "source_type": (EVIDENCE,),
    "moment_type": (MOMENT,),
    "metric layer": (METRIC,),
    "direction": (METRIC,),
    "evidence_freshness": (PORTFOLIO,),
    "decision (opportunity)": (OPPORTUNITY,),
    "status (opportunity, initiative)": (OPPORTUNITY, INITIATIVE),
    "relation": (RELATION,),
    "metric relation": (EDGE,),
    "review_trigger": (GOVERNANCE,),
    "metric_coverage": (PORTFOLIO,),
    "row_type (experience)": (EXPERIENCE,),
    "valence (experience)": (EXPERIENCE,),
}

# Bullet opening -> registers it concerns (column clarifications and rules).
BULLET_REGISTERS = (
    ("In `journey-registry` and `portfolio-register`", (JOURNEY, PORTFOLIO)),
    ("`parent_id` points", (JOURNEY, PORTFOLIO)),
    ("`actor_id` may be empty", (JOURNEY, PORTFOLIO)),
    ("`baseline_journey_id` links", (JOURNEY,)),
    ("Node depth", (NODE,)),
    ("`metric_coverage` applies", (PORTFOLIO,)),
    ("A metric attaches", (METRIC,)),
    ("On a metric row", (METRIC,)),
    ("Causal claims between metrics", (METRIC, EDGE)),
    ("Every `JRN` that has metrics", (METRIC, EDGE)),
    ("On an opportunity row", (OPPORTUNITY,)),
    ("In the governance register", (GOVERNANCE, CHANGES)),
    ("On an evidence row", (EVIDENCE,)),
    ("The relation register", (RELATION,)),
    ("The experience register holds", (EXPERIENCE,)),
    ("An `emotion` row", (EXPERIENCE,)),
    ("`node_id` must start", (NODE,)),
    ("`parent_node_id` equals", (NODE,)),
    ("Every ID cited", ALL),
    ("A parent sits", (JOURNEY, PORTFOLIO)),
    ("A row with `evidence_status = observed`", ALL),
    ("The actor code", (ACTOR, JOURNEY)),
    ("A portfolio row's `linked_opportunities`", (PORTFOLIO,)),
    ("Metric edges never", (EDGE,)),
    ("`stakeholder-input` evidence has", ALL),
    ("When a row cites both", (EVIDENCE, OPPORTUNITY, CHANGES)),
    ("Links stay inside", (MOMENT, METRIC, OPPORTUNITY, INITIATIVE)),
    ("A portfolio row agrees", (PORTFOLIO,)),
    ("A relation never", (RELATION,)),
)

HEADER = (
    "<!-- Generated from the ontology of the journey-architecture skill. "
    "Do not edit by hand: change the ontology and regenerate the cards. -->\n"
)


def sections(text):
    """Split the ontology into {'## heading': body}."""
    out, current, lines = {}, None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if current:
                out[current] = "\n".join(lines).strip("\n")
            current, lines = line[3:].strip(), []
        elif current:
            lines.append(line)
    if current:
        out[current] = "\n".join(lines).strip("\n")
    return out


def bullets_after(body, marker):
    """The '- ' bullets that follow `marker` in `body`."""
    tail = body.split(marker, 1)[1] if marker else body
    items = []
    for line in tail.splitlines():
        if line.startswith("- "):
            items.append(line[2:])
        elif items and line.strip():
            break  # the list ends at the first non-bullet text; blank lines inside it are tolerated
    return items


def owner_of(bullet):
    for opening, registers in BULLET_REGISTERS:
        if bullet.startswith(opening):
            return registers
    raise ValueError(f"ontology bullet not mapped in sync_conventions: {bullet[:60]!r}")


def render(ontology_text, skill):
    """Return the contract card for `skill`."""
    used = set(SKILL_REGISTERS[skill])
    sec = sections(ontology_text)
    grammar = sec["ID grammar"].split("Regular expressions", 1)[0].rstrip()
    rules = sec["ID grammar"].split("Rules:", 1)[1].strip()
    enums_body = sec["Enumerations"]
    table, meanings = enums_body.split("\n\n", 1)
    registers_body = sec["Registers"]

    out = [HEADER, "# Conventions", ""]
    out.append(
        "This card is the part of the Journey Architecture OS contract that this skill "
        "uses: identifiers, evidence statuses, and the registers the skill produces or "
        "consumes. The journey-architecture skill holds the full contract."
    )
    out += ["", "## Identifiers", "", grammar, ""]
    out.append(
        "Use these patterns exactly, zero-padded. Never invent short forms such as "
        "`EVD-001`, `O1`, or `Stage 3`: give a new item the next free number in its "
        "register, or describe it in prose until it has a row."
    )
    out += ["", rules, "", "## Evidence status", "", meanings.strip(), ""]

    rows = []
    for line in registers_body.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 4 and cells[2].strip("`") in used:
            owner = cells[1].strip("`")
            where = "this skill" if owner == skill else f"`{owner}` skill"
            rows.append(f"| {cells[0]} | {cells[2]} | {where} | {cells[3]} |")
    out += ["## Registers", ""]
    out.append(
        "Registers are CSV files, one per register. List-valued cells separate IDs "
        "with `;` and no spaces."
    )
    out += ["", "| Register | File | Template in | Columns |", "|---|---|---|---|"]
    out += rows
    dates = [p for p in registers_body.split("\n\n") if p.startswith("Dates use")]
    out += ["", dates[0].strip() if dates else "", ""]

    enum_rows = []
    for line in table.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 2 and cells[0].startswith("`"):
            label = cells[0].replace("`", "").strip()
            if label not in ENUM_REGISTERS:
                raise ValueError(
                    f"enumeration not mapped in sync_conventions: {label!r}"
                )
            if used & set(ENUM_REGISTERS[label]):
                enum_rows.append(line)
    out += ["## Enumerations", "", "| Field | Allowed values |", "|---|---|"]
    out += enum_rows + [""]

    clar = [
        b
        for b in bullets_after(registers_body, "Column clarifications:")
        if used & set(owner_of(b))
    ]
    if clar:
        out += ["## Column rules", ""] + [f"- {b}" for b in clar] + [""]
    refs = [
        b
        for b in bullets_after(sec["Referential rules"], None)
        if used & set(owner_of(b))
    ]
    out += ["## Referential rules", ""] + [f"- {b}" for b in refs]
    return "\n".join(out).rstrip() + "\n"


def expected_cards(root):
    text = (root / ONTOLOGY.relative_to(ROOT)).read_text(encoding="utf-8")
    cards = {}
    for skill_dir in sorted((root / "skills").iterdir()):
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").is_file():
            cards[skill_dir / CARD] = render(text, skill_dir.name)
    return cards


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate skill contract cards.")
    parser.add_argument(
        "--check", action="store_true", help="report stale cards, write nothing"
    )
    args = parser.parse_args(argv)
    stale = []
    for path, text in expected_cards(ROOT).items():
        current = path.read_text(encoding="utf-8") if path.is_file() else None
        if current == text:
            continue
        stale.append(path)
        if not args.check:
            path.parent.mkdir(exist_ok=True)
            path.write_text(text, encoding="utf-8")
    for path in stale:
        print(("stale: " if args.check else "wrote: ") + str(path.relative_to(ROOT)))
    return 1 if args.check and stale else 0


if __name__ == "__main__":
    sys.exit(main())
