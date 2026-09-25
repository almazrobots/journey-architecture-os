#!/usr/bin/env python3
"""Validate Journey Architecture OS.

Checks, in order:

1. Skills: strict frontmatter, names, descriptions, skills.json in sync, no
   orphan or non-regular files, no unexpected entries, and every path written
   in SKILL.md, references/ or assets/ stays inside the skill.
2. Supply chain: no symbolic links under skills/, schemas/, or examples/.
3. Contract: the ID regexes, enumerations, and register columns in the
   journey-architecture ontology agree with this script and with the JSON
   Schemas in schemas/; the schemas use only the supported JSON Schema subset;
   register templates carry the exact schema header and nothing else; every
   skill's references/conventions.md equals its regenerated contract card.
4. Examples: every directory under examples/ holding a journey-registry.csv is
   a journey system, validated row by row, referentially, and for ID tokens in
   its Markdown/YAML views. Stand-alone examples/*.csv files are validated
   against the register whose header they carry.
5. ID hygiene: ID tokens in examples/*.md must match the grammar, and IDs in
   skill references and stand-alone examples must not reuse an ID defined by
   an example journey system.

Standard library only; Python 3.9 or newer.

Usage: python3 scripts/validate_repo.py [--root PATH]
"""

import argparse
import csv
import datetime
import importlib.util
import json
import os
import re
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_PATH = "skills/journey-architecture/references/ontology.md"
CONVENTIONS_SCRIPT = "scripts/sync_conventions.py"
CONVENTIONS_CARD = "references/conventions.md"
SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"
SCHEMA_ID_BASE = "https://raw.githubusercontent.com/almazrobots/journey-architecture-os/main/schemas/"

NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")  # used with fullmatch

# ---------------------------------------------------------------------------
# Contract constants. The ontology is the source of truth; these copies exist
# so the drift checks below can prove the two never diverge.
# ---------------------------------------------------------------------------

ID_PATTERNS = {
    "ACT": r"^ACT-[A-Z]{2,6}(-[A-Z][A-Z0-9]*)+-[0-9]{2}$",
    "DOM": r"^DOM(-[A-Z][A-Z0-9]*)+-[0-9]{3}$",
    "LFC": r"^LFC-[A-Z]{2,6}(-[A-Z][A-Z0-9]*)+-[0-9]{3}$",
    "JRN": r"^JRN-[A-Z]{2,6}(-[A-Z][A-Z0-9]*)+-[0-9]{3}$",
    "NOD": r"^NOD-[A-Z]{2,6}(-[A-Z][A-Z0-9]*)+-[0-9]{3}(-[0-9]{2})+$",
    "EVD": r"^EVD-[0-9]{4}-[0-9]{4}$",
    "MTM": r"^MTM-[0-9]{4}$",
    "MET": r"^MET-[0-9]{4}$",
    "OPP": r"^OPP-[0-9]{4}$",
    "INI": r"^INI-[0-9]{4}$",
    "CHG": r"^CHG-[0-9]{4}$",
}
ID_REGEXES = {prefix: re.compile(p) for prefix, p in ID_PATTERNS.items()}

# Any token that looks like an ID. A preceding hyphen is allowed on purpose so
# that legacy composites such as STG-JRN-... are caught, not skipped.
ID_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:ACT|DOM|LFC|JRN|NOD|EVD|MTM|MET|OPP|INI|CHG)-[A-Z0-9]+(?:-[A-Z0-9]+)*"
)

DATE_PATTERN = "^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
POSITIVE_INT_PATTERN = "^[1-9][0-9]*$"
COVERAGE_PATTERN = r"^(0(\.[0-9]{1,2})?|1(\.0{1,2})?)?$"
VALENCE_PATTERN = "^(-2|-1|0|1|2)$"

# Register name (schema file stem) -> CSV file name (ontology "File" column).
REGISTERS = {
    "actor": "actor-register.csv",
    "journey": "journey-registry.csv",
    "relation": "relation-register.csv",
    "node": "node-register.csv",
    "evidence": "evidence-register.csv",
    "moment": "moment-register.csv",
    "metric": "metric-register.csv",
    "metric-edge": "metric-edge-register.csv",
    "opportunity": "opportunity-register.csv",
    "initiative": "initiative-register.csv",
    "portfolio": "portfolio-register.csv",
    "governance": "governance-register.csv",
    "change-log": "change-log.csv",
    "experience": "experience-register.csv",
}
# Single-column identity of each keyed register.
PRIMARY_KEY = {
    "actor": "actor_id",
    "journey": "journey_id",
    "node": "node_id",
    "evidence": "evidence_id",
    "moment": "moment_id",
    "metric": "metric_id",
    "opportunity": "opportunity_id",
    "initiative": "initiative_id",
    "change-log": "change_id",
    "portfolio": "journey_id",
    "governance": "journey_id",
}
# Registers keyed by a journey-registry entry: their key is also a citation.
KEYED_BY_JOURNEY = ("portfolio", "governance")
# Columns whose combined values must be unique in each register.
KEY_COLUMNS = {name: (col,) for name, col in PRIMARY_KEY.items()}
KEY_COLUMNS["relation"] = ("from_id", "relation", "to_id")
KEY_COLUMNS["metric-edge"] = ("from_metric_id", "relation", "to_metric_id")
KEY_COLUMNS["experience"] = ("node_id", "row_type", "text")
# Endpoint columns of edge registers, which must differ.
EDGE_ENDS = {
    "relation": ("from_id", "to_id"),
    "metric-edge": ("from_metric_id", "to_metric_id"),
}
# Which register defines the IDs of each prefix.
PREFIX_REGISTER = {
    "ACT": "actor",
    "DOM": "journey",
    "LFC": "journey",
    "JRN": "journey",
    "NOD": "node",
    "EVD": "evidence",
    "MTM": "moment",
    "MET": "metric",
    "OPP": "opportunity",
    "INI": "initiative",
    "CHG": "change-log",
}
JOURNEY_PREFIXES = ("DOM", "LFC", "JRN")
PARENT_PREFIXES = ("DOM", "LFC")
ATTACH_PREFIXES = JOURNEY_PREFIXES + ("NOD",)
# (register, column) -> (allowed ID prefixes, list-valued)
ID_COLUMNS = {
    ("actor", "actor_id"): (("ACT",), False),
    ("journey", "journey_id"): (JOURNEY_PREFIXES, False),
    ("journey", "parent_id"): (PARENT_PREFIXES, False),
    ("journey", "actor_id"): (("ACT",), False),
    ("journey", "baseline_journey_id"): (("JRN",), False),
    ("relation", "from_id"): (ATTACH_PREFIXES, False),
    ("relation", "to_id"): (ATTACH_PREFIXES, False),
    ("relation", "evidence_ids"): (("EVD",), True),
    ("node", "node_id"): (("NOD",), False),
    ("node", "journey_id"): (("JRN",), False),
    ("node", "parent_node_id"): (("NOD",), False),
    ("node", "evidence_ids"): (("EVD",), True),
    ("evidence", "evidence_id"): (("EVD",), False),
    ("evidence", "journey_id"): (("JRN",), False),
    ("evidence", "node_id"): (("NOD",), False),
    ("moment", "moment_id"): (("MTM",), False),
    ("moment", "node_id"): (("NOD",), False),
    ("moment", "evidence_ids"): (("EVD",), True),
    ("moment", "metric_ids"): (("MET",), True),
    ("metric", "metric_id"): (("MET",), False),
    ("metric", "journey_or_node_id"): (ATTACH_PREFIXES, False),
    ("metric", "evidence_ids"): (("EVD",), True),
    ("metric-edge", "from_metric_id"): (("MET",), False),
    ("metric-edge", "to_metric_id"): (("MET",), False),
    ("metric-edge", "evidence_ids"): (("EVD",), True),
    ("opportunity", "opportunity_id"): (("OPP",), False),
    ("opportunity", "journey_id"): (("JRN",), False),
    ("opportunity", "node_id"): (("NOD",), False),
    ("opportunity", "moment_ids"): (("MTM",), True),
    ("opportunity", "metric_ids"): (("MET",), True),
    ("opportunity", "evidence_ids"): (("EVD",), True),
    ("initiative", "initiative_id"): (("INI",), False),
    ("initiative", "opportunity_ids"): (("OPP",), True),
    ("initiative", "expected_metric_ids"): (("MET",), True),
    ("portfolio", "journey_id"): (JOURNEY_PREFIXES, False),
    ("portfolio", "parent_id"): (PARENT_PREFIXES, False),
    ("portfolio", "actor_id"): (("ACT",), False),
    ("portfolio", "linked_opportunities"): (("OPP",), True),
    ("portfolio", "linked_initiatives"): (("INI",), True),
    ("governance", "journey_id"): (JOURNEY_PREFIXES, False),
    ("change-log", "change_id"): (("CHG",), False),
    ("change-log", "journey_id"): (JOURNEY_PREFIXES, False),
    ("change-log", "evidence_ids"): (("EVD",), True),
    ("change-log", "affected_node_ids"): (("NOD",), True),
    ("experience", "node_id"): (("NOD",), False),
    ("experience", "evidence_ids"): (("EVD",), True),
}
DATE_COLUMNS = {
    ("journey", "last_reviewed_at"),
    ("evidence", "collected_at"),
    ("portfolio", "last_reviewed_at"),
    ("governance", "last_reviewed_at"),
    ("governance", "next_review_due"),
    ("change-log", "changed_at"),
}
# (register, column) -> fixed pattern for non-ID columns with a grammar.
VALUE_PATTERNS = {
    ("node", "sequence"): POSITIVE_INT_PATTERN,
    ("portfolio", "metric_coverage"): COVERAGE_PATTERN,
    ("governance", "review_interval_days"): POSITIVE_INT_PATTERN,
    ("experience", "valence"): VALENCE_PATTERN,
}
VALUE_PATTERNS.update({col: DATE_PATTERN for col in DATE_COLUMNS})
# Ontology enumeration label -> the register columns it governs.
ENUM_COLUMNS = {
    "evidence_status": [
        ("relation", "evidence_status"),
        ("node", "evidence_status"),
        ("evidence", "evidence_status"),
        ("moment", "evidence_status"),
        ("metric", "evidence_status"),
        ("metric-edge", "evidence_status"),
        ("opportunity", "evidence_status"),
        ("opportunity", "root_cause_status"),
        ("experience", "evidence_status"),
    ],
    "level": [("journey", "level"), ("portfolio", "level")],
    "state": [("journey", "state"), ("portfolio", "state")],
    "status (journey)": [("journey", "status"), ("portfolio", "status")],
    "node_type": [("node", "node_type")],
    "actor_type": [("actor", "actor_type")],
    "source_type": [("evidence", "source_type")],
    "moment_type": [("moment", "moment_type")],
    "metric layer": [("metric", "layer")],
    "direction": [("metric", "direction")],
    "evidence_freshness": [("portfolio", "evidence_freshness")],
    "decision (opportunity)": [("opportunity", "decision")],
    "status (opportunity, initiative)": [
        ("opportunity", "status"),
        ("initiative", "status"),
    ],
    "relation": [("relation", "relation")],
    "metric relation": [("metric-edge", "relation")],
    "row_type (experience)": [("experience", "row_type")],
}
# Enumerations used as ';'-separated lists: (register, column) -> label.
ENUM_LIST_COLUMNS = {("governance", "review_triggers"): "review_trigger"}
# Enumerations-table rows that document a value grammar, not an enum.
PATTERN_ROWS = {"metric_coverage": COVERAGE_PATTERN, "valence (experience)": VALENCE_PATTERN}
# Level implied by each journey-registry prefix. L3/L4 are nodes and live in
# the node register, so journey-registry and portfolio levels are L0-L2 only.
PREFIX_LEVEL = {"DOM": "L0", "LFC": "L1", "JRN": "L2"}
ENUM_RESTRICTED_TO_PREFIX_LEVELS = {("journey", "level"), ("portfolio", "level")}
# stakeholder-input "can support hypothesis at most".
STAKEHOLDER_ALLOWED_STATUS = ("hypothesis", "unknown")
# Status of a claim -> statuses at least one cited evidence item must have.
CITATION_NEEDS = {"observed": ("observed",), "inferred": ("observed", "inferred")}
# Registers with evidence_ids, and the status columns that evidence supports.
EVIDENCED = {
    "relation": ("evidence_status",),
    "node": ("evidence_status",),
    "moment": ("evidence_status",),
    "metric": ("evidence_status",),
    "metric-edge": ("evidence_status",),
    "opportunity": ("evidence_status", "root_cause_status"),
    "experience": ("evidence_status",),
}
# Sources that can show how someone felt; an emotion claim needs one of them.
EMOTION_SOURCES = ("interview", "observation", "diary", "survey", "usability-test")
# Status columns are always filled; `unknown` means not assessed.
STATUS_COLUMNS = ("evidence_status", "root_cause_status")
# Portfolio rows restate these journey-registry fields and must agree.
PORTFOLIO_MIRRORED = ("parent_id", "level", "actor_id", "state", "status")
# States of a journey version that must name its current baseline.
VERSION_STATES = ("target", "transitional")

# JSON Schema subset understood by this validator.
SCHEMA_ANNOTATIONS = {"$schema", "$id", "$comment", "title", "description"}
SCHEMA_KEYWORDS = {
    "type",
    "properties",
    "required",
    "enum",
    "pattern",
    "additionalProperties",
}
SCHEMA_TYPES = {"object", "string"}

SKILL_ENTRIES = {"SKILL.md", "references", "assets", "scripts"}
# Frontmatter keys allowed by the Agent Skills specification.
FRONTMATTER_KEYS = ("name", "description", "license", "compatibility", "metadata", "allowed-tools")
METADATA_ENTRY_RE = re.compile(r"( +)([A-Za-z0-9_-]+): (.+)")
MD_LINK_RE = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)")
BACKTICK_RE = re.compile(r"`([^`\s]+)`")
PATH_TOKEN_RE = re.compile(r"[\w.~/\\-]+")
REPO_FOLDERS = ("skills", "docs", "scripts", "schemas", "examples", "evals", "tests")
IGNORED_ENTRIES = {".DS_Store"}
SKILL_TEXT_SUFFIXES = (".md", ".csv", ".yaml", ".yml", ".json", ".txt")
REF_CANDIDATE_RE = re.compile(r"[(`]([^()`\s]*(?:references|assets)[/\\][^)`\s]*)[)`]")
PARENT_DIR_RE = re.compile(r"\.\.[/\\]")
REPO_PATH_RE = re.compile(
    r"(?<![\w./-])((?:skills|docs|scripts|schemas|examples|evals|tests)/[\w./-]*)"
)
SKILL_PATH_RE = re.compile(
    r"(?<![\w./-])([a-z0-9]+(?:-[a-z0-9]+)*)/(?:assets|references|scripts)/"
)
PLAIN_SCALAR_BAD_START = set("-?:,[]{}#&*!|>'\"%@`")
TEXT_SUFFIXES = (".md", ".yaml", ".yml")


def read_text(path, report=None):
    """Read a UTF-8 text file (a byte-order mark is tolerated); report, never raise."""
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as e:
        if report is not None:
            report.error(path, None, f"not UTF-8 (byte {e.start}); save the file as UTF-8")
        return None


_ECMA_CACHE = {}


def ecma_search(pattern, value):
    """re.search with ECMA-262 semantics for '$' (end of input only), as JSON
    Schema validators apply it; Python's '$' also matches before a final newline."""
    compiled = _ECMA_CACHE.get(pattern)
    if compiled is None:
        compiled = re.compile(re.sub(r"(?<!\\)\$", r"\\Z", pattern))
        _ECMA_CACHE[pattern] = compiled
    return compiled.search(value)


class Report:
    def __init__(self, root):
        self.root = root
        self.errors = []
        self.notices = []

    def rel(self, path):
        try:
            return Path(path).relative_to(self.root).as_posix()
        except ValueError:
            return str(path)

    def error(self, path, line, message):
        where = self.rel(path)
        if line:
            where = f"{where}:{line}"
        self.errors.append(f"{where}: {message}")

    def notice(self, message):
        self.notices.append(message)


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------


def parse_plain_or_quoted(raw):
    """Return the value of a single-line YAML scalar or raise ValueError."""
    if raw == "":
        raise ValueError("must be a single-line scalar, found an empty value")
    if raw[0] == '"':
        inner = raw[1:-1]
        if len(raw) < 2 or raw[-1] != '"' or '"' in inner or "\\" in inner:
            raise ValueError(
                'double-quoted value must be one simple "..." string without escapes'
            )
        return inner
    if raw[0] == "'":
        inner = raw[1:-1]
        if len(raw) < 2 or raw[-1] != "'" or "'" in inner:
            raise ValueError("single-quoted value must be one simple '...' string")
        return inner
    if raw[0] in PLAIN_SCALAR_BAD_START:
        raise ValueError(f"plain value must not start with {raw[0]!r}; quote it")
    if ": " in raw or " #" in raw or raw.endswith(":"):
        raise ValueError("plain value must not contain ': ' or ' #'; quote it")
    return raw


def parse_frontmatter(text):
    """Strictly parse SKILL.md frontmatter.

    Returns (fields, lines, nested): fields maps each top-level key to its raw
    value, lines maps each key to its 1-based line number, and nested maps a
    key with an empty value to its indented (lineno, line) entries. Raises
    ValueError with a line number when the block could be read differently by
    a YAML parser.
    """
    if not text.startswith("---\n"):
        raise ValueError("1: frontmatter must be the first block and start with '---'")
    end = text.find("\n---\n", 3)
    if end == -1:
        raise ValueError("1: unterminated frontmatter (no closing '---' line)")
    fields, lines, nested = {}, {}, {}
    nested_ok = False
    current = "(no key yet)"
    for lineno, line in enumerate(text[4 : end + 1].splitlines(), start=2):
        if "\t" in line:
            raise ValueError(f"{lineno}: tab characters are not allowed in frontmatter")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0] == " ":
            if not nested_ok:
                raise ValueError(
                    f"{lineno}: indented line continues the value of '{current}'; "
                    "multi-line values are not allowed"
                )
            nested[current].append((lineno, line))
            continue
        m = re.match(r"([A-Za-z0-9_-]+):(?: (.*))?$", line)
        if not m:
            raise ValueError(f"{lineno}: expected 'key: value' at top level")
        key, raw = m.group(1), (m.group(2) or "").strip()
        if key in fields:
            raise ValueError(
                f"{lineno}: duplicate top-level key '{key}' (first on line {lines[key]})"
            )
        if raw[:1] in ("|", ">"):
            raise ValueError(
                f"{lineno}: block scalar indicator in '{key}' is not allowed"
            )
        fields[key] = raw
        lines[key] = lineno
        current = key
        nested_ok = raw == ""
        if nested_ok:
            nested[key] = []
    return fields, lines, nested


def check_frontmatter_keys(f, fm, key_lines, nested, report):
    """Only the Agent Skills keys; metadata maps strings to strings."""
    for key in fm:
        if key not in FRONTMATTER_KEYS:
            report.error(
                f, key_lines[key], f"frontmatter key '{key}' is not allowed (allowed: {', '.join(FRONTMATTER_KEYS)})"
            )
    for key in ("license", "compatibility", "allowed-tools"):
        if key in fm:
            try:
                parse_plain_or_quoted(fm[key])
            except ValueError as e:
                report.error(f, key_lines[key], f"{key}: {e}")
    if "metadata" not in fm:
        return
    entries = nested.get("metadata")
    if not entries:
        report.error(f, key_lines["metadata"], "metadata must be a map of string keys to string values")
        return
    seen, indent = set(), None
    for lineno, line in entries:
        m = METADATA_ENTRY_RE.fullmatch(line)
        if not m or m.group(1) != (indent or m.group(1)):
            report.error(f, lineno, "metadata entries must be 'key: value' strings at one indentation")
            continue
        indent = m.group(1)
        key, value = m.group(2), m.group(3)
        if key in seen:
            report.error(f, lineno, f"duplicate metadata key '{key}'")
        seen.add(key)
        try:
            parse_plain_or_quoted(value)
        except ValueError as e:
            report.error(f, lineno, f"metadata {key}: {e}")


def link_targets(line):
    """Markdown link targets and path-like backticked tokens on one line."""
    found = list(MD_LINK_RE.findall(line)) + REF_CANDIDATE_RE.findall(line)
    for token in BACKTICK_RE.findall(line):
        # A backticked token is a path when it has a folder separator and ends in
        # a file name with an extension or in '/'; `n/a` or `L3/L4` are not.
        last = re.split(r"[/\\]", token)[-1]
        if PATH_TOKEN_RE.fullmatch(token) and (
            token.startswith("~") or (("/" in token or "\\" in token) and (last == "" or "." in last))
        ):
            found.append(token)
    return list(dict.fromkeys(found))


def check_skill_paths(d, path, text, skill_names, report):
    """Every path written in a skill file must stay inside the skill.

    Returns the references/ and assets/ files the file cites.
    """
    cited = set()
    base = d.resolve()
    for lineno, line in enumerate(text.splitlines(), start=1):
        if PARENT_DIR_RE.search(line):
            report.error(path, lineno, "path climbs out of the skill with '..'")
        for token in REPO_PATH_RE.findall(line):
            report.error(
                path,
                lineno,
                f"path {token} points outside the skill; installed skills see only their own files",
            )
        for name in SKILL_PATH_RE.findall(line):
            if name in skill_names:
                report.error(
                    path,
                    lineno,
                    f"path into the {name} skill; refer to this skill's own references/ or assets/",
                )
        for raw in link_targets(line):
            target = raw.split("#", 1)[0].split("?", 1)[0]
            if not target or "://" in raw or raw.startswith("mailto:"):
                continue
            if target.startswith(("/", "~")) or "\\" in target or ".." in target:
                report.error(
                    path,
                    lineno,
                    f"unsafe relative reference {raw} (no '..', '\\', '~', or leading '/')",
                )
                continue
            if target.split("/", 1)[0] in REPO_FOLDERS or target.split("/", 1)[0] in skill_names:
                continue  # already reported as a path outside the skill
            resolved = [
                p for p in ((path.parent / target).resolve(), (d / target).resolve())
                if p.is_relative_to(base) and p.is_file()
            ]
            if not resolved:
                report.error(path, lineno, f"broken relative reference {raw}")
                continue
            cited.add(resolved[0].relative_to(base).as_posix())
    return cited


def check_skill(d, report, descriptions, skill_names):
    f = d / "SKILL.md"
    if f.is_symlink() or not f.is_file():
        report.error(d, None, "missing SKILL.md (must be a regular file)")
        return
    for entry in sorted(d.iterdir()):
        if entry.name in IGNORED_ENTRIES:
            continue
        if entry.name not in SKILL_ENTRIES:
            report.error(
                entry,
                None,
                "unexpected entry in skill directory (allowed: SKILL.md, references/, assets/, scripts/)",
            )
        elif entry.name != "SKILL.md" and (entry.is_symlink() or not entry.is_dir()):
            report.error(entry, None, "must be a directory")
    if (d / "scripts").is_dir() and not (d / "scripts").is_symlink():
        report.notice(
            f"{report.rel(d / 'scripts')}/ ships executable content; review it before installing"
        )
    text = read_text(f, report)
    if text is None:
        return
    try:
        fm, key_lines, nested = parse_frontmatter(text)
    except ValueError as e:
        line, _, msg = str(e).partition(": ")
        report.error(f, line, msg)
        return
    check_frontmatter_keys(f, fm, key_lines, nested, report)
    values = {}
    for key in ("name", "description"):
        if key not in fm:
            report.error(f, None, f"frontmatter requires '{key}'")
            values[key] = ""
            continue
        try:
            values[key] = parse_plain_or_quoted(fm[key])
        except ValueError as e:
            report.error(f, key_lines[key], f"{key}: {e}")
            values[key] = ""
    name, desc = values["name"], values["description"]
    if name != d.name:
        report.error(
            f, key_lines.get("name"), f"{d.name}: frontmatter name must match directory"
        )
    if not NAME_RE.fullmatch(name):
        report.error(f, key_lines.get("name"), f"invalid name {name!r}")
    if not (1 <= len(name) <= 64):
        report.error(f, key_lines.get("name"), "name length invalid")
    if not (1 <= len(desc) <= 1024):
        report.error(
            f, key_lines.get("description"), f"description length invalid ({len(desc)})"
        )
    n_lines = len(text.splitlines())
    if n_lines > 500:
        report.error(f, None, f"SKILL.md has {n_lines} lines; max 500 recommended")
    referenced = check_skill_paths(d, f, text, skill_names, report)
    for sub in ("references", "assets"):
        folder = d / sub
        if folder.is_symlink() or not folder.is_dir():
            continue
        for extra in sorted(folder.iterdir()):
            if extra.name in IGNORED_ENTRIES:
                continue
            rel = f"{sub}/{extra.name}"
            if extra.is_symlink() or not extra.is_file():
                report.error(extra, None, "must be a regular file")
                continue
            if rel not in referenced:
                report.error(f, None, f"{rel} is not referenced from SKILL.md")
            if extra.suffix in SKILL_TEXT_SUFFIXES:
                content = read_text(extra, report)
                if content is not None:
                    check_skill_paths(d, extra, content, skill_names, report)
    descriptions[d.name] = desc


def check_skills(root, report):
    skills_dir = root / "skills"
    skill_dirs = sorted(
        p for p in skills_dir.iterdir() if p.is_dir() and not p.is_symlink()
    )
    skill_names = {d.name for d in skill_dirs}
    descriptions = {}
    for d in skill_dirs:
        check_skill(d, report, descriptions, skill_names)
    registry_path = root / "skills.json"
    if not registry_path.is_file():
        report.error(registry_path, None, "missing skills.json")
        return skill_dirs
    try:
        reg = json.loads(read_text(registry_path, report) or "")
        entries = reg["skills"]
        registered = {x["name"] for x in entries}
    except (ValueError, KeyError, TypeError) as e:
        report.error(registry_path, None, f"malformed skills.json ({e})")
        return skill_dirs
    for x in entries:
        if (
            x["name"] in descriptions
            and x.get("description") != descriptions[x["name"]]
        ):
            report.error(
                registry_path, None, f"description of {x['name']} differs from SKILL.md"
            )
        if x.get("path") != f"skills/{x['name']}":
            report.error(
                registry_path, None, f"path of {x['name']} must be skills/{x['name']}"
            )
    if registered != skill_names:
        report.error(
            registry_path,
            None,
            f"skills.json mismatch: registered={sorted(registered)} actual={sorted(skill_names)}",
        )
    return skill_dirs


def check_symlinks(root, report):
    for top in ("skills", "schemas", "examples"):
        base = root / top
        if not base.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(base, followlinks=False):
            for name in dirnames + filenames:
                p = Path(dirpath) / name
                if p.is_symlink():
                    report.error(p, None, "symbolic links are not allowed")


# ---------------------------------------------------------------------------
# Ontology
# ---------------------------------------------------------------------------


def parse_ontology(text):
    """Extract ID regexes, enumerations, and registers from the ontology."""
    regexes = {}
    block = re.search(r"```text\n(.*?)```", text, re.S)
    if block:
        for line in block.group(1).splitlines():
            m = re.match(r"([A-Z]{3})\s+(\S+)$", line.strip())
            if m:
                regexes[m.group(1)] = m.group(2)
    enums, registers = {}, {}
    section = None
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if section == "Enumerations" and len(cells) == 2 and cells[0].startswith("`"):
            label = cells[0].replace("`", "").strip()
            # Values are the backticked tokens before any parenthetical note.
            enums[label] = re.findall(r"`([^`]+)`", cells[1].split(" (")[0])
        elif section == "Registers" and len(cells) == 4:
            skill = re.findall(r"`([^`]+)`", cells[1])
            filename = re.findall(r"`([^`]+)`", cells[2])
            cols = re.findall(r"`([^`]+)`", cells[3])
            if skill and filename and cols:
                registers[filename[0]] = (skill[0], cols[0].split(","))
    return {"regexes": regexes, "enums": enums, "registers": registers}


def check_ontology(root, report):
    path = root / ONTOLOGY_PATH
    if not path.is_file():
        report.error(path, None, "ontology is missing")
        return None
    text = read_text(path, report)
    if text is None:
        return None
    onto = parse_ontology(text)
    for prefix in sorted(set(onto["regexes"]) | set(ID_PATTERNS)):
        if onto["regexes"].get(prefix) != ID_PATTERNS.get(prefix):
            report.error(
                path,
                None,
                f"ID regex drift for {prefix}: ontology={onto['regexes'].get(prefix)!r} "
                f"validator={ID_PATTERNS.get(prefix)!r}",
            )
    known = set(ENUM_COLUMNS) | set(PATTERN_ROWS) | set(ENUM_LIST_COLUMNS.values())
    for label in onto["enums"]:
        if label not in known:
            report.error(
                path,
                None,
                f"enumeration '{label}' is not mapped to any register column in the validator",
            )
    for label in known:
        if label not in onto["enums"]:
            report.error(
                path,
                None,
                f"enumeration '{label}' expected by the validator is missing from the ontology",
            )
    for filename in REGISTERS.values():
        if filename not in onto["registers"]:
            report.error(
                path, None, f"register {filename} is missing from the Registers table"
            )
    return onto


# ---------------------------------------------------------------------------
# JSON Schema subset
# ---------------------------------------------------------------------------


def check_schema_keywords(schema, where, report, path):
    """Reject keywords outside the supported subset so schemas stay portable."""
    if not isinstance(schema, dict):
        report.error(path, None, f"{where}: schema must be an object")
        return
    for key, value in schema.items():
        if key in SCHEMA_ANNOTATIONS:
            continue
        if key not in SCHEMA_KEYWORDS:
            report.error(
                path, None, f"{where}: unsupported JSON Schema keyword '{key}'"
            )
        elif key == "type" and value not in SCHEMA_TYPES:
            report.error(path, None, f"{where}: unsupported type {value!r}")
        elif key == "properties":
            if not isinstance(value, dict):
                report.error(path, None, f"{where}: 'properties' must be an object")
                continue
            for name, sub in value.items():
                check_schema_keywords(sub, f"{where}/properties/{name}", report, path)
        elif key == "required" and not (
            isinstance(value, list)
            and all(k in schema.get("properties", {}) for k in value)
        ):
            report.error(
                path, None, f"{where}: 'required' must list declared properties"
            )
        elif key == "enum" and not (isinstance(value, list) and value):
            report.error(path, None, f"{where}: 'enum' must be a non-empty list")
        elif key == "additionalProperties" and not isinstance(value, bool):
            report.error(
                path, None, f"{where}: 'additionalProperties' must be a boolean"
            )
        elif key == "pattern":
            try:
                re.compile(value)
            except (re.error, TypeError) as e:
                report.error(path, None, f"{where}: invalid pattern ({e})")


def validate_instance(instance, schema):
    """Validate against the supported subset. Returns [(property, message)]."""
    errors = []
    kind = schema.get("type")
    if kind == "object" and not isinstance(instance, dict):
        return [(None, "expected an object")]
    if kind == "string" and not isinstance(instance, str):
        return [(None, "expected a string")]
    props = schema.get("properties", {})
    for key in schema.get("required", []):
        if key not in instance:
            errors.append((key, f"required column '{key}' is empty"))
    if schema.get("additionalProperties") is False:
        for key in instance:
            if key not in props:
                errors.append((key, f"unexpected column '{key}'"))
    if isinstance(instance, dict):
        for key, value in instance.items():
            if key in props:
                for _, msg in validate_instance(value, props[key]):
                    errors.append((key, f"column '{key}': {msg}"))
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(
            (None, f"{instance!r} is not one of: {', '.join(schema['enum'])}")
        )
    if "pattern" in schema and not ecma_search(schema["pattern"], instance):
        errors.append((None, f"{instance!r} does not match {schema['pattern']}"))
    return errors


def id_pattern(prefixes, is_list):
    """Schema pattern for an ID column, derived from ID_PATTERNS."""
    bodies = [ID_PATTERNS[p][1:-1] for p in prefixes]
    one = bodies[0] if len(bodies) == 1 else "(?:" + "|".join(bodies) + ")"
    if is_list:
        return f"^{one}(?:;{one})*$"
    return f"^{one}$"


def enum_list_pattern(values):
    """Schema pattern for a ';'-separated list of enumeration values."""
    one = "(?:" + "|".join(values) + ")"
    return f"^{one}(?:;{one})*$"


def expected_pattern(name, col, onto):
    if (name, col) in ID_COLUMNS:
        return id_pattern(*ID_COLUMNS[(name, col)])
    if (name, col) in ENUM_LIST_COLUMNS:
        values = (onto or {}).get("enums", {}).get(ENUM_LIST_COLUMNS[(name, col)])
        return enum_list_pattern(values) if values else None
    return VALUE_PATTERNS.get((name, col))


def load_schemas(root, report, onto):
    schemas = {}
    for name, filename in REGISTERS.items():
        path = root / "schemas" / f"{name}.schema.json"
        if not path.is_file():
            report.error(path, None, "schema is missing")
            continue
        try:
            schema = json.loads(read_text(path, report) or "")
        except ValueError as e:
            report.error(path, None, f"invalid JSON ({e})")
            continue
        before = len(report.errors)
        check_schema_keywords(schema, "#", report, path)
        if schema.get("$schema") != SCHEMA_DIALECT:
            report.error(path, None, f"$schema must be {SCHEMA_DIALECT}")
        if schema.get("$id") != f"{SCHEMA_ID_BASE}{name}.schema.json":
            report.error(path, None, f"$id must be {SCHEMA_ID_BASE}{name}.schema.json")
        if (
            schema.get("type") != "object"
            or schema.get("additionalProperties") is not False
        ):
            report.error(
                path,
                None,
                "a register row must be type object with additionalProperties false",
            )
        if not schema.get("description"):
            report.error(
                path,
                None,
                "description must explain the row and the required-column choice",
            )
        props = (
            schema.get("properties")
            if isinstance(schema.get("properties"), dict)
            else {}
        )
        for col in STATUS_COLUMNS:
            if col in props and col not in schema.get("required", []):
                report.error(path, None, f"status column '{col}' must be required (use unknown when not assessed)")
        for pk in KEY_COLUMNS[name]:
            if pk not in schema.get("required", []):
                report.error(path, None, f"primary key '{pk}' must be required")
        if onto and filename in onto["registers"]:
            columns = onto["registers"][filename][1]
            if list(props) != columns:
                report.error(
                    path,
                    None,
                    f"properties {list(props)} differ from ontology columns {columns}",
                )
        for col, sub in props.items():
            if not isinstance(sub, dict) or sub.get("type") != "string":
                report.error(
                    path,
                    None,
                    f"property '{col}' must be type string (CSV cells are text)",
                )
                continue
            expected = expected_pattern(name, col, onto)
            if sub.get("pattern") != expected:
                report.error(
                    path,
                    None,
                    f"property '{col}' pattern must be {expected!r}, found {sub.get('pattern')!r}",
                )
        if onto:
            for label, targets in ENUM_COLUMNS.items():
                for reg, col in targets:
                    if reg != name or col not in props:
                        continue
                    allowed = onto["enums"].get(label) or []
                    if (reg, col) in ENUM_RESTRICTED_TO_PREFIX_LEVELS:
                        allowed = [v for v in allowed if v in PREFIX_LEVEL.values()]
                    if props[col].get("enum") != allowed:
                        report.error(
                            path,
                            None,
                            f"property '{col}' enum must be {allowed} (ontology '{label}')",
                        )
            enum_cols = {
                c for targets in ENUM_COLUMNS.values() for r, c in targets if r == name
            }
            for col, sub in props.items():
                if isinstance(sub, dict) and "enum" in sub and col not in enum_cols:
                    report.error(
                        path,
                        None,
                        f"property '{col}' has an enum the ontology does not define",
                    )
        if len(report.errors) == before:
            schemas[name] = schema
    return schemas


# ---------------------------------------------------------------------------
# Registers
# ---------------------------------------------------------------------------


class Row:
    def __init__(self, line, data, bad):
        self.line = line
        self.data = data
        self.bad = bad  # columns that failed the schema

    def get(self, col):
        return None if col in self.bad else self.data.get(col)

    def ids(self, col):
        value = self.get(col)
        return value.split(";") if value else []


def read_csv(path, report):
    """Return (header, [(line, cells)]) or (None, []) on a parse error."""
    try:
        # utf-8-sig accepts the byte-order mark that spreadsheet tools write.
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.reader(fh, strict=True)
            header = next(reader, None)
            rows = []
            prev = reader.line_num
            for cells in reader:
                start = prev + 1
                prev = reader.line_num
                if cells:
                    rows.append((start, cells))
    except UnicodeDecodeError as e:
        report.error(path, None, f"not UTF-8 (byte {e.start}); save the register as UTF-8")
        return None, []
    except csv.Error as e:
        report.error(path, None, f"unreadable CSV ({e})")
        return None, []
    if header is None:
        report.error(path, None, "empty file; a register needs its header row")
    return header, rows


def load_register(path, name, schema, report):
    """Validate a register file. Returns its rows, or None if the header is wrong."""
    header, raw_rows = read_csv(path, report)
    if header is None:
        return None
    expected = list(schema["properties"])
    if header != expected:
        report.error(
            path,
            1,
            f"header does not match schemas/{name}.schema.json; expected: {','.join(expected)}",
        )
        return None
    rows = []
    for line, cells in raw_rows:
        if len(cells) != len(header):
            report.error(
                path, line, f"row has {len(cells)} cells, header has {len(header)}"
            )
            continue
        data, bad = {}, set()
        for key, value in zip(header, cells):
            if value and not value.strip():
                report.error(path, line, f"column '{key}' holds only whitespace")
            elif value:
                data[key] = value
        for col, msg in validate_instance(data, schema):
            report.error(path, line, msg)
            bad.add(col)
        for reg, col in sorted(DATE_COLUMNS):
            if reg == name and col in data and col not in bad:
                try:
                    datetime.date.fromisoformat(data[col])
                except ValueError:
                    report.error(
                        path,
                        line,
                        f"column '{col}': {data[col]!r} is not a calendar date",
                    )
                    bad.add(col)
        rows.append(Row(line, data, bad))
    cols = KEY_COLUMNS[name]
    seen = {}
    for row in rows:
        key = tuple(row.get(c) for c in cols)
        if None in key:
            continue
        if key in seen:
            report.error(
                path,
                row.line,
                f"duplicate {'+'.join(cols)} {' '.join(key)} (first on line {seen[key]})",
            )
        else:
            seen[key] = row.line
    return rows


def level_number(level):
    return int(level[1:])


def actor_code(identifier):
    return identifier.split("-")[1]


def check_journey_rows(path, rows, report):
    """Prefix/level coherence, actors, and actor codes for hierarchy rows."""
    for row in rows:
        jid, level = row.get("journey_id"), row.get("level")
        if not jid:
            continue
        if level and PREFIX_LEVEL[jid[:3]] != level:
            report.error(
                path,
                row.line,
                f"{jid} is a {jid[:3]} and must be level {PREFIX_LEVEL[jid[:3]]}, found {level}",
            )
        if jid[:3] != "JRN" and row.get("metric_coverage") is not None:
            report.error(
                path,
                row.line,
                f"metric_coverage applies to JRN rows only; leave it empty for {jid}",
            )
        if jid[:3] == "DOM":
            continue
        actor = row.get("actor_id")
        if "actor_id" not in row.data:
            report.error(
                path,
                row.line,
                f"{jid} must name its actor_id; only DOM rows may leave it empty",
            )
        elif actor and actor_code(actor) != actor_code(jid):
            report.error(
                path,
                row.line,
                f"actor code of {jid} differs from its actor_id {actor}",
            )
        parent = row.get("parent_id")
        if parent and parent[:3] == "LFC" and actor_code(parent) != actor_code(jid):
            report.error(
                path,
                row.line,
                f"actor code of {jid} differs from its parent lifecycle {parent}",
            )


def check_parents(path, rows, levels, report, source):
    """parent_id must exist in `levels` and sit at a lower level number."""
    for row in rows:
        parent, level = row.get("parent_id"), row.get("level")
        if not parent:
            continue
        if parent not in levels:
            report.error(path, row.line, f"parent_id {parent} is not in {source}")
        elif (
            level
            and levels[parent]
            and level_number(levels[parent]) >= level_number(level)
        ):
            report.error(
                path,
                row.line,
                f"parent_id {parent} is level {levels[parent]}; a parent must have a lower level number than {level}",
            )


class System:
    """The loaded registers of one journey system."""

    def __init__(self, directory, schemas, report):
        self.dir = directory
        self.report = report
        self.rows = {}
        for name, filename in REGISTERS.items():
            path = directory / filename
            if path.is_file() and name in schemas:
                self.rows[name] = load_register(path, name, schemas[name], report) or []
        known = set(REGISTERS.values())
        for csv_path in sorted(directory.rglob("*.csv")):
            if csv_path.name not in known or csv_path.parent != directory:
                report.error(
                    csv_path,
                    None,
                    f"unknown register file; expected one of {', '.join(sorted(known))} directly in {report.rel(directory)}",
                )
        self.ids = {name: {} for name in PREFIX_REGISTER.values()}
        for name in set(PREFIX_REGISTER.values()):
            for row in self.rows.get(name, []):
                key = row.get(PRIMARY_KEY[name])
                if key:
                    self.ids[name].setdefault(key, row)

    def get(self, name):
        return self.rows.get(name, [])

    def path(self, name):
        return self.dir / REGISTERS[name]

    def error(self, name, row, message):
        self.report.error(self.path(name), row.line, message)

    def lookup(self, identifier):
        return self.ids[PREFIX_REGISTER[identifier[:3]]].get(identifier)

    def journey_of(self, identifier):
        """The JRN a journey or node ID belongs to, if any."""
        if identifier.startswith("JRN-"):
            return identifier
        node = self.ids["node"].get(identifier)
        return node.get("journey_id") if node else None

    def journeys_under(self, entry):
        """Hierarchy entries at or below `entry` (including itself)."""
        found = set()
        for jid, row in self.ids["journey"].items():
            seen, current = set(), jid
            while current and current not in seen:
                if current == entry:
                    found.add(jid)
                    break
                seen.add(current)
                parent = self.ids["journey"].get(current)
                current = parent.get("parent_id") if parent else None
        return found


def check_references(sys_):
    """Every cited ID exists in its register."""
    for (name, col), _ in ID_COLUMNS.items():
        if col == PRIMARY_KEY.get(name) and name not in KEYED_BY_JOURNEY:
            continue
        for row in sys_.get(name):
            for cited in row.ids(col):
                if sys_.lookup(cited) is None:
                    target = PREFIX_REGISTER[cited[:3]]
                    sys_.error(
                        name,
                        row,
                        f"{col} cites {cited}, which is not in {REGISTERS[target]}",
                    )


def check_versions(sys_):
    """Target and transitional L2 journeys name their current baseline."""
    for row in sys_.get("journey"):
        jid, state, level = row.get("journey_id"), row.get("state"), row.get("level")
        if state is None or level is None:
            continue
        base = row.data.get("baseline_journey_id")
        versioned = state in VERSION_STATES and level == "L2"
        if base and not versioned:
            sys_.error(
                "journey",
                row,
                f"baseline_journey_id must be empty for a {level} {state} entry; only L2 target or transitional journeys name a baseline",
            )
        elif versioned and not base:
            sys_.error(
                "journey",
                row,
                f"{jid} is {state} and must name its current journey in baseline_journey_id",
            )
        elif versioned and base in sys_.ids["journey"]:
            baseline = sys_.ids["journey"][base]
            if baseline.get("level") != "L2" or baseline.get("state") != "current":
                sys_.error(
                    "journey",
                    row,
                    f"baseline_journey_id {base} must be an L2 journey with state current, found {baseline.get('level')} {baseline.get('state')}",
                )
            actor = row.get("actor_id")
            if actor and baseline.get("actor_id") and actor != baseline.get("actor_id"):
                sys_.error(
                    "journey",
                    row,
                    f"actor_id of {jid} is {actor}, but its baseline {base} is for {baseline.get('actor_id')}",
                )


def check_nodes(sys_):
    """Node prefix, parent, type by depth, and sequence by last segment."""
    for row in sys_.get("node"):
        nid, jid = row.get("node_id"), row.get("journey_id")
        if not nid or not jid:
            continue
        prefix = "NOD-" + jid[4:]
        # Slug tokens start with a letter, so a grammatical node ID that starts
        # with the journey key plus '-' continues with -NN segments only.
        if not nid.startswith(prefix + "-"):
            sys_.error(
                "node",
                row,
                f"node_id {nid} must start with {prefix}- (NOD- + key of {jid})",
            )
            continue
        depth = nid[len(prefix) :].count("-")
        expected_parent = nid.rsplit("-", 1)[0] if depth > 1 else None
        parent = row.data.get("parent_node_id")
        if parent != expected_parent:
            want = expected_parent or "empty (stage-level node)"
            sys_.error(
                "node",
                row,
                f"parent_node_id of {nid} must be {want}, found {parent or 'empty'}",
            )
        node_type = row.get("node_type")
        if depth == 1 and node_type not in (None, "stage"):
            sys_.error(
                "node",
                row,
                f"{nid} has no parent, so it is a stage (L3), not {node_type}",
            )
        elif depth > 1 and node_type == "stage":
            sys_.error(
                "node",
                row,
                f"{nid} sits inside {expected_parent}, so it is an episode, step, or interaction (L4), not a stage",
            )
        sequence, last = row.get("sequence"), nid.rsplit("-", 1)[1]
        if sequence is not None and int(sequence) != int(last):
            sys_.error(
                "node",
                row,
                f"sequence of {nid} must be {int(last)} (its last ID segment), found {sequence}",
            )


def check_node_journeys(sys_):
    """A node cited together with a journey belongs to that journey."""
    for name, col in (
        ("evidence", "node_id"),
        ("opportunity", "node_id"),
        ("change-log", "affected_node_ids"),
    ):
        for row in sys_.get(name):
            jid = row.get("journey_id")
            if not jid:
                continue
            for nid in row.ids(col):
                node = sys_.ids["node"].get(nid)
                if node is not None and node.get("journey_id") != jid:
                    sys_.error(
                        name,
                        row,
                        f"{col} {nid} belongs to {node.get('journey_id')}, not {jid}",
                    )


def check_scopes(sys_):
    """Moments and metrics cited by opportunities, moments and initiatives stay
    inside the scope of the citing row's journey: the journey, its nodes, and
    the lifecycle and domain above it."""

    def scope(jid):
        chain, current = set(), jid
        while current and current not in chain:
            chain.add(current)
            row = sys_.ids["journey"].get(current)
            current = row.get("parent_id") if row else None
        return chain

    def metric_in(mid, journeys):
        metric = sys_.ids["metric"].get(mid)
        target = metric.get("journey_or_node_id") if metric else None
        if target is None:
            return True  # dangling or invalid: reported elsewhere
        node = sys_.ids["node"].get(target)
        if node is not None:
            return node.get("journey_id") in journeys
        return any(target in scope(j) for j in journeys)

    for row in sys_.get("opportunity"):
        jid = row.get("journey_id")
        journey = sys_.ids["journey"].get(jid) if jid else None
        if journey is None:
            continue
        if journey.get("state") != "current":
            sys_.error("opportunity", row, f"{jid} is {journey.get('state')}; opportunities belong to current journeys")
        for mtm in row.ids("moment_ids"):
            moment = sys_.ids["moment"].get(mtm)
            node = sys_.ids["node"].get(moment.get("node_id") or "") if moment else None
            if node is not None and node.get("journey_id") != jid:
                sys_.error("opportunity", row, f"moment_ids cites {mtm}, a moment of {node.get('journey_id')}, not of {jid}")
        for mid in row.ids("metric_ids"):
            if not metric_in(mid, {jid}):
                sys_.error("opportunity", row, f"metric_ids cites {mid}, which is outside the scope of {jid}")
    for row in sys_.get("moment"):
        node = sys_.ids["node"].get(row.get("node_id") or "")
        if node is None or not node.get("journey_id"):
            continue
        jid = node.get("journey_id")
        for mid in row.ids("metric_ids"):
            if not metric_in(mid, {jid}):
                sys_.error("moment", row, f"metric_ids cites {mid}, which is outside the scope of {jid}")
    for row in sys_.get("initiative"):
        opps = [sys_.ids["opportunity"].get(o) for o in row.ids("opportunity_ids")]
        journeys = {o.get("journey_id") for o in opps if o is not None and o.get("journey_id")}
        if not journeys:
            continue
        for mid in row.ids("expected_metric_ids"):
            if not metric_in(mid, journeys):
                sys_.error(
                    "initiative", row,
                    f"expected_metric_ids cites {mid}, which is outside the scope of {', '.join(sorted(journeys))}",
                )


def check_evidence_discipline(sys_):
    for row in sys_.get("evidence"):
        status = row.get("evidence_status")
        if (
            row.get("source_type") == "stakeholder-input"
            and status not in STAKEHOLDER_ALLOWED_STATUS
        ):
            sys_.error(
                "evidence",
                row,
                f"stakeholder-input evidence can support hypothesis at most; evidence_status is {status}",
            )
    for name, status_columns in EVIDENCED.items():
        for row in sys_.get(name):
            cited = [sys_.ids["evidence"].get(e) for e in row.ids("evidence_ids")]
            statuses = {e.get("evidence_status") for e in cited if e is not None}
            for col in status_columns:
                status = row.get(col)
                if status in CITATION_NEEDS and not statuses & set(
                    CITATION_NEEDS[status]
                ):
                    sys_.error(
                        name,
                        row,
                        f"{col} is {status} but no cited evidence ID is {' or '.join(CITATION_NEEDS[status])}",
                    )
    for row in sys_.get("opportunity"):
        cause, status = row.get("root_cause"), row.get("root_cause_status")
        if status in CITATION_NEEDS and (cause is None or cause.lower() == "unknown"):
            sys_.error(
                "opportunity",
                row,
                f"root_cause_status is {status} but root_cause is not stated",
            )


def check_experience(sys_):
    """valence belongs to emotion rows only; felt emotions need first-hand sources."""
    for row in sys_.get("experience"):
        row_type = row.get("row_type")
        if row_type is None:
            continue
        has_valence = "valence" in row.data
        if row_type == "emotion" and not has_valence:
            sys_.error("experience", row, "an emotion row needs a valence from -2 to 2")
        elif row_type != "emotion" and has_valence:
            sys_.error("experience", row, f"valence belongs to emotion rows only, not {row_type}")
        if row_type == "emotion" and row.get("evidence_status") in CITATION_NEEDS:
            sources = {
                e.get("source_type")
                for e in (sys_.ids["evidence"].get(x) for x in row.ids("evidence_ids"))
                if e is not None
            }
            if not sources & set(EMOTION_SOURCES):
                sys_.error(
                    "experience",
                    row,
                    f"an {row.get('evidence_status')} emotion must cite an {', '.join(EMOTION_SOURCES)} source; documents, analytics and stakeholder input cannot show how someone felt",
                )


def check_edges(sys_):
    for name, (start, end) in EDGE_ENDS.items():
        for row in sys_.get(name):
            source = row.get(start)
            if source and source == row.get(end):
                sys_.error(name, row, f"{name} from {source} to itself")


def check_portfolio(sys_):
    journeys = sys_.ids["journey"]
    for row in sys_.get("portfolio"):
        jid = row.get("journey_id")
        journey = journeys.get(jid) if jid else None
        if journey is None:
            continue
        for col in PORTFOLIO_MIRRORED:
            if row.get(col) != journey.get(col):
                sys_.error(
                    "portfolio",
                    row,
                    f"{col} of {jid} is {row.get(col) or 'empty'} here but {journey.get(col) or 'empty'} in {REGISTERS['journey']}",
                )
        owned = sys_.journeys_under(jid)
        # A target or transitional journey realizes its baseline's opportunities.
        baseline = journey.get("baseline_journey_id")
        if baseline:
            owned.add(baseline)
        own_opps = {
            oid
            for oid, opp in sys_.ids["opportunity"].items()
            if opp.get("journey_id") in owned
        }
        for oid in row.ids("linked_opportunities"):
            opp = sys_.ids["opportunity"].get(oid)
            if opp is not None and oid not in own_opps:
                sys_.error(
                    "portfolio",
                    row,
                    f"linked_opportunities cites {oid}, which belongs to {opp.get('journey_id')}, not to {jid} or a journey below it",
                )
        for iid in row.ids("linked_initiatives"):
            ini = sys_.ids["initiative"].get(iid)
            if ini is not None and not set(ini.ids("opportunity_ids")) & own_opps:
                sys_.error(
                    "portfolio",
                    row,
                    f"linked_initiatives cites {iid}, which addresses none of the opportunities of {jid}",
                )
    check_journey_rows(sys_.path("portfolio"), sys_.get("portfolio"), sys_.report)


def check_coverage(sys_):
    """metric_coverage = share of stage-level nodes with a metric at or below them."""
    # Journey-level targets never equal or extend a stage ID, so they never count.
    measured = [m.get("journey_or_node_id") or "" for m in sys_.get("metric")]
    for row in sys_.get("portfolio"):
        jid, value = row.get("journey_id"), row.get("metric_coverage")
        if not jid or value is None or not jid.startswith("JRN-"):
            continue
        stages = [
            nid
            for nid, node in sys_.ids["node"].items()
            if node.get("journey_id") == jid and not node.data.get("parent_node_id")
        ]
        if not stages:
            sys_.error(
                "portfolio",
                row,
                f"metric_coverage of {jid} must be empty: it has no stage-level nodes",
            )
            continue
        covered = sum(
            1 for s in stages if any(m == s or m.startswith(s + "-") for m in measured)
        )
        expected = round(covered / len(stages), 2)
        if float(value) != expected:
            sys_.error(
                "portfolio",
                row,
                f"metric_coverage of {jid} is {value}, but {covered} of {len(stages)} stage-level nodes have a metric ({expected:g})",
            )


def reachable(start, edges):
    """All nodes reachable from `start` following `edges` (dict of sets)."""
    seen, stack = set(), [start]
    while stack:
        for nxt in edges.get(stack.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def check_metric_tree(sys_):
    drives, back, protects, edge_rows = {}, {}, set(), {}
    for row in sys_.get("metric-edge"):
        a, b, rel = (
            row.get("from_metric_id"),
            row.get("to_metric_id"),
            row.get("relation"),
        )
        if not a or not b:
            continue
        if rel == "drives":
            drives.setdefault(a, set()).add(b)
            back.setdefault(b, set()).add(a)
            edge_rows[(a, b)] = row
        elif rel == "protects":
            protects.add(a)
    # drives edges contain no cycle
    for (a, b), row in sorted(edge_rows.items()):
        if a in reachable(b, drives):
            sys_.error("metric-edge", row, f"drives edge {a} -> {b} closes a cycle")
    by_journey = {}
    for row in sys_.get("metric"):
        target = row.get("journey_or_node_id")
        layer = row.get("layer")
        if target and target[:3] in PARENT_PREFIXES and layer and layer != "business":
            sys_.error(
                "metric",
                row,
                f"{row.get('metric_id')} is attached to {target}; metrics above journey level must be business, not {layer}",
            )
        jid = sys_.journey_of(target) if target else None
        if jid:
            by_journey.setdefault(jid, []).append(row)
    for jid, metrics in sorted(by_journey.items()):
        roots = [
            m
            for m in metrics
            if m.get("journey_or_node_id") == jid and m.get("layer") == "actor-outcome"
        ]
        if len(roots) != 1:
            sys_.error(
                "metric",
                metrics[0],
                f"{jid} has {len(roots)} actor-outcome metrics attached to the journey itself; its metric tree needs exactly one root",
            )
            continue
        root = roots[0].get("metric_id")
        upstream, downstream = reachable(root, back), reachable(root, drives)
        for m in metrics:
            mid, layer = m.get("metric_id"), m.get("layer")
            if mid == root or not mid or not layer:
                continue
            if layer == "business":
                if mid not in downstream:
                    sys_.error(
                        "metric",
                        m,
                        f"business metric {mid} must be driven by the root {root}",
                    )
            elif layer == "guardrail":
                if mid not in protects:
                    sys_.error("metric", m, f"guardrail {mid} must protect a metric")
            elif mid not in upstream:
                sys_.error(
                    "metric",
                    m,
                    f"{mid} does not reach the root {root} through drives edges",
                )


def check_governance(sys_):
    for row in sys_.get("governance"):
        last, due = row.get("last_reviewed_at"), row.get("next_review_due")
        if last and due and due < last:
            sys_.error(
                "governance",
                row,
                f"next_review_due {due} is before last_reviewed_at {last}",
            )


def check_views(sys_):
    """ID tokens in a system's Markdown/YAML views resolve to register rows."""
    for view in sorted(
        p for p in sys_.dir.rglob("*") if p.suffix in TEXT_SUFFIXES and p.is_file()
    ):
        for lineno, token in scan_tokens(view, sys_.report):
            if sys_.lookup(token) is None:
                target = PREFIX_REGISTER[token[:3]]
                sys_.report.error(
                    view,
                    lineno,
                    f"{token} does not resolve to a row in {REGISTERS[target]}",
                )


def validate_system(directory, schemas, report):
    """Validate one journey system directory and return it."""
    sys_ = System(directory, schemas, report)
    check_references(sys_)
    journeys = sys_.get("journey")
    check_journey_rows(sys_.path("journey"), journeys, report)
    levels = {jid: row.get("level") for jid, row in sys_.ids["journey"].items()}
    check_parents(sys_.path("journey"), journeys, levels, report, REGISTERS["journey"])
    check_versions(sys_)
    check_nodes(sys_)
    check_node_journeys(sys_)
    check_scopes(sys_)
    check_evidence_discipline(sys_)
    check_experience(sys_)
    check_edges(sys_)
    check_portfolio(sys_)
    check_coverage(sys_)
    check_metric_tree(sys_)
    check_governance(sys_)
    check_views(sys_)
    return sys_


def scan_tokens(path, report=None):
    """Yield (line, token) for grammatical ID tokens; report malformed ones."""
    text = read_text(path, report)
    for lineno, line in enumerate((text or "").splitlines(), start=1):
        for token in ID_TOKEN_RE.findall(line):
            if ID_REGEXES[token[:3]].search(token):
                yield lineno, token
            elif report is not None:
                report.error(
                    path,
                    lineno,
                    f"{token} does not match the {token[:3]} ID grammar {ID_PATTERNS[token[:3]]}",
                )


def validate_single_csv(path, schemas, report):
    """A stand-alone example CSV is validated against the register whose header it carries."""
    header, _ = read_csv(path, report)
    if header is None:
        return
    for name, schema in schemas.items():
        if header == list(schema["properties"]):
            rows = load_register(path, name, schema, report) or []
            if name in ("journey", "portfolio"):
                check_journey_rows(path, rows, report)
                levels = {
                    r.get("journey_id"): r.get("level")
                    for r in rows
                    if r.get("journey_id")
                }
                check_parents(path, rows, levels, report, "this file")
            return
    report.error(path, 1, "header matches no register schema")


def check_templates(root, schemas, onto, report):
    for name, filename in REGISTERS.items():
        if name not in schemas:
            continue
        if onto and filename in onto["registers"]:
            asset = (
                root / "skills" / onto["registers"][filename][0] / "assets" / filename
            )
            if not asset.is_file():
                report.error(
                    asset, None, "register template named in the ontology is missing"
                )
        for path in sorted((root / "skills").glob(f"*/assets/{filename}")):
            rows = load_register(path, name, schemas[name], report)
            if rows:
                report.error(
                    path, rows[0].line, "a register template holds the header row only"
                )


def check_conventions(root, skill_dirs, report):
    """Each skill's contract card equals the card regenerated from the ontology."""
    script = root / CONVENTIONS_SCRIPT
    ontology = root / ONTOLOGY_PATH
    if not script.is_file() or not ontology.is_file():
        report.error(
            script, None, "cannot check contract cards: generator or ontology missing"
        )
        return
    spec = importlib.util.spec_from_file_location("sync_conventions", script)
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    text = read_text(ontology) or ""
    for d in skill_dirs:
        card = d / CONVENTIONS_CARD
        try:
            expected = gen.render(text, d.name)
        except (KeyError, ValueError) as e:
            report.error(card, None, f"cannot generate contract card ({e})")
            continue
        if not card.is_file() or read_text(card) != expected:
            report.error(
                card,
                None,
                "contract card is missing or out of date; run make conventions",
            )


def check_stray_csvs(examples, system_dirs, report):
    """Every CSV under examples/ is a stand-alone example or part of a system."""
    flagged = set()
    for path in sorted(examples.rglob("*.csv")):
        if path.parent == examples or any(path.is_relative_to(d) for d in system_dirs):
            continue
        report.error(path, None, "CSV outside any journey system; examples/*.csv or a directory with journey-registry.csv")
        if path.name in REGISTERS.values() and path.parent not in flagged:
            flagged.add(path.parent)
            report.error(path.parent, None, f"holds register files but no {REGISTERS['journey']}")


def check_example_views(examples, report):
    """ID tokens in stand-alone example views must at least match the grammar.

    Method guides and evals legitimately use placeholders such as MET-NNNN, so
    only examples/ is held to the grammar.
    """
    for path in sorted(examples.glob("*")):
        if path.suffix in TEXT_SUFFIXES and path.is_file() and not path.is_symlink():
            for _ in scan_tokens(path, report):
                pass


def check_namespaces(root, systems, report):
    """Guides and stand-alone examples must not reuse IDs of an example system."""
    defined = {}
    for sys_ in systems:
        for name, ids in sys_.ids.items():
            for identifier in ids:
                defined.setdefault(identifier, sys_.dir)
    files = sorted((root / "skills").glob("*/references/*.md"))
    files += sorted((root / "examples").glob("*.md"))
    for path in files:
        if path.is_symlink():
            continue
        for lineno, token in scan_tokens(path):
            if token in defined:
                report.error(
                    path,
                    lineno,
                    f"{token} is defined by the example system {report.rel(defined[token])}; use an ID of your own here",
                )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root", type=Path, default=DEFAULT_ROOT, help="repository root to validate"
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    report = Report(root)

    check_symlinks(root, report)
    skill_dirs = check_skills(root, report)
    onto = check_ontology(root, report)
    schemas = load_schemas(root, report, onto)
    check_templates(root, schemas, onto, report)
    check_conventions(root, skill_dirs, report)

    systems = []
    examples = root / "examples"
    if examples.is_dir():
        for directory in sorted(
            {p.parent for p in examples.rglob(REGISTERS["journey"])}
        ):
            systems.append(validate_system(directory, schemas, report))
        for path in sorted(examples.glob("*.csv")):
            validate_single_csv(path, schemas, report)
        check_stray_csvs(examples, [s.dir for s in systems], report)
        check_example_views(examples, report)
    check_namespaces(root, systems, report)

    for notice in report.notices:
        print("NOTICE:", notice)
    if report.errors:
        print("VALIDATION FAILED")
        for e in report.errors:
            print(" -", e)
        return 1
    noun = "journey system" if len(systems) == 1 else "journey systems"
    print(
        f"OK: {len(skill_dirs)} skills, {len(schemas)} schemas, "
        f"{len(systems)} {noun} validated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
