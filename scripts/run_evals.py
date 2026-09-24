#!/usr/bin/env python3
"""Evaluation runner for Journey Architecture OS.

Two suites:

* routing   -- does an agent pick the right skill from the name + description it
               sees at discovery time? (evals/routing.jsonl)
* behavior  -- does loading a skill make the agent's output measurably better
               than the same model without it? (evals/behavior/*.json)

The model is reached through a pluggable shell command that reads the prompt on
stdin and prints the answer on stdout (``--cmd``). Any agent CLI or a small
wrapper around an HTTP API works. Standard library only; Python >= 3.9.

Documentation: docs/evaluations.md (what is measured, isolation of the default
command, results integrity, how to add cases).

Examples:

    python3 scripts/run_evals.py --check
    python3 scripts/run_evals.py --mode routing --dry-run --limit 1
    python3 scripts/run_evals.py --mode routing
    python3 scripts/run_evals.py --mode behavior --case BH-02-cjm-move-home
    python3 scripts/run_evals.py --mode routing --cmd "my-agent --json" --model some-model
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as _dt
import functools
import hashlib
import json
import math
import random
import re
import shutil
import shlex
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVALS_DIR = ROOT / "evals"

NEUTRAL_SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the user's message directly and completely. "
    "Do not ask clarifying questions; state assumptions instead."
)

# Default model command: Claude Code in print mode, isolated from the local
# user's configuration as far as the CLI allows (see README "Evaluations").
#   --safe-mode                 no CLAUDE.md, skills, plugins, hooks, MCP servers,
#                               custom agents/commands, output styles
#   --setting-sources ""        load no user/project/local settings files
#   --strict-mcp-config         no MCP servers except those passed (none)
#   --disable-slash-commands    no skills resolvable by name
#   --tools ""                  no built-in tools: the answer is pure text
#   --system-prompt ...         replaces the coding-agent system prompt
#   --no-session-persistence    nothing written to session history
# The command also runs from an empty temporary directory, so no project
# CLAUDE.md or .claude/ directory can be discovered.
DEFAULT_CMD = (
    "claude -p --safe-mode --setting-sources '' --strict-mcp-config "
    "--disable-slash-commands --tools '' --no-session-persistence "
    "--system-prompt " + shlex.quote(NEUTRAL_SYSTEM_PROMPT)
)

ASSERTION_CATEGORIES = {"convention", "method"}
DIFFICULTIES = ("easy", "hard")
MIN_HARD_CASES_PER_SKILL = 5
REGEX_FLAG_MAP = {
    "i": re.IGNORECASE,
    "m": re.MULTILINE,
    "s": re.DOTALL,
    "x": re.VERBOSE,
}
ONTOLOGY_PATH = ROOT / "skills" / "journey-architecture" / "references" / "ontology.md"
# Sentinels usable in regex assertions; resolved from the ontology at run time so that
# eval files never carry their own copy of the ID grammar.
ONTOLOGY_FINDER_SENTINEL = "@ontology-id-finder"
ONTOLOGY_GRAMMAR_SENTINEL = "@ontology-id-grammar"
REFERENCE_EXTENSIONS = (".md", ".csv", ".yaml", ".yml", ".json", ".txt")
MAX_REFERENCED_FILE_CHARS = 60_000


# --------------------------------------------------------------------------
# Skill discovery (read from disk at runtime, never copied into eval files)
# --------------------------------------------------------------------------


def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    """Minimal YAML-frontmatter reader for top-level scalar keys.

    Supports plain, single/double-quoted, and folded/literal (``>``/``|``) scalars.
    Nested mappings (e.g. ``metadata:``) are skipped. Returns (fields, body).
    """
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    fields: Dict[str, str] = {}
    i = 1
    while i < end:
        line = lines[i]
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, value = m.group(1), m.group(2).rstrip()
        if value in (">", "|", ">-", "|-", ">+", "|+"):
            block: List[str] = []
            i += 1
            while i < end and (
                lines[i].startswith((" ", "\t")) or not lines[i].strip()
            ):
                block.append(lines[i].strip())
                i += 1
            if value.startswith(">"):
                fields[key] = " ".join(b for b in block if b)
            else:
                fields[key] = "\n".join(block).strip("\n")
            continue
        if value == "":
            # nested mapping or empty value: skip indented children
            i += 1
            while i < end and lines[i].startswith((" ", "\t")):
                i += 1
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
            if m.group(2).startswith("'"):
                value = value.replace("''", "'")
        # plain scalar may continue on indented lines
        i += 1
        while (
            i < end
            and lines[i].startswith((" ", "\t"))
            and not re.match(r"^\s+[\w-]+:", lines[i])
        ):
            value += " " + lines[i].strip()
            i += 1
        fields[key] = value
    body = "\n".join(lines[end + 1 :])
    return fields, body


def load_registry() -> List[Dict[str, Any]]:
    return json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))["skills"]


def load_skills() -> List[Dict[str, Any]]:
    """Return skills as an agent client sees them: name + description from SKILL.md."""
    skills = []
    for entry in load_registry():
        path = ROOT / entry["path"] / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        skills.append(
            {
                "name": fm.get("name", ""),
                "description": fm.get("description", ""),
                "dir": path.parent,
                "text": text,
                "body": body,
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()[:12],
            }
        )
    return sorted(skills, key=lambda s: s["name"])


def referenced_paths(skill: Dict[str, Any]) -> List[Path]:
    """Files a SKILL.md points to in backticks (e.g. `references/x.md`), resolved on disk."""
    found: List[Path] = []
    for token in re.findall(r"`([^`\s]+)`", skill["body"]):
        if not token.endswith(REFERENCE_EXTENSIONS):
            continue
        for base in (skill["dir"], ROOT):
            candidate = (base / token).resolve()
            try:
                candidate.relative_to(ROOT)
            except ValueError:
                continue
            if candidate.is_file():
                if candidate not in found:
                    found.append(candidate)
                break
    return found


def display_path(path: Path) -> str:
    for base in (ROOT / "skills", ROOT):
        try:
            return str(path.relative_to(base))
        except ValueError:
            continue
    return str(path)


def referenced_files(skill: Dict[str, Any]) -> List[Tuple[str, str]]:
    """(display path, content) for every file the skill references."""
    out = []
    for path in referenced_paths(skill):
        content = path.read_text(encoding="utf-8", errors="replace")
        if len(content) > MAX_REFERENCED_FILE_CHARS:
            content = content[:MAX_REFERENCED_FILE_CHARS] + "\n[truncated]\n"
        out.append((display_path(path), content))
    return out


# --------------------------------------------------------------------------
# Eval file loading and --check
# --------------------------------------------------------------------------


def load_routing(evals_dir: Path) -> List[Dict[str, Any]]:
    cases = []
    path = evals_dir / "routing.jsonl"
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                case = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name}:{n}: invalid JSON: {exc}") from exc
            case["_line"] = n
            cases.append(case)
    return cases


def load_distractors(evals_dir: Path) -> List[Dict[str, str]]:
    """Fictional neighbour skills listed next to ours in routing prompts (evals/distractors.json)."""
    path = evals_dir / "distractors.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        {"name": d.get("name", ""), "description": d.get("description", "")}
        for d in data.get("skills", [])
    ]


def load_behavior(evals_dir: Path) -> List[Dict[str, Any]]:
    scenarios = []
    for path in sorted((evals_dir / "behavior").glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"behavior/{path.name}: invalid JSON: {exc}") from exc
        data["_file"] = path.name
        scenarios.append(data)
    return scenarios


@functools.lru_cache(maxsize=None)
def ontology_id_patterns() -> Tuple[Tuple[str, str], ...]:
    """(prefix, anchored regex) pairs from the ontology's 'Regular expressions' block.

    The ontology is the single list of ID prefixes; nothing here repeats it.
    """
    text = ONTOLOGY_PATH.read_text(encoding="utf-8")
    pairs = tuple(
        (m.group(1), m.group(2))
        for m in re.finditer(r"^([A-Z]{3})\s+(\^\S+\$)\s*$", text, re.M)
    )
    if not pairs:
        raise ValueError(f"no ID regular expressions found in {ONTOLOGY_PATH}")
    return pairs


def ontology_id_finder() -> str:
    prefixes = "|".join(p for p, _ in ontology_id_patterns())
    return r"\b(?:" + prefixes + r")-[A-Z0-9]+(?:-[A-Z0-9]+)*"


def ontology_id_grammar() -> str:
    return "|".join("(?:" + rx[1:-1] + ")" for _, rx in ontology_id_patterns())


def resolve_pattern(pattern: str) -> str:
    if pattern == ONTOLOGY_FINDER_SENTINEL:
        return ontology_id_finder()
    if pattern == ONTOLOGY_GRAMMAR_SENTINEL:
        return ontology_id_grammar()
    return pattern


def compile_flags(flags: str) -> int:
    value = 0
    for ch in flags:
        if ch not in REGEX_FLAG_MAP:
            raise ValueError(f"unknown regex flag {ch!r}")
        value |= REGEX_FLAG_MAP[ch]
    return value


def check_evals(evals_dir: Path) -> List[str]:
    """Validate eval files without any model call. Returns a list of errors."""
    errors: List[str] = []
    skills = load_skills()
    names = {s["name"] for s in skills}
    registry_names = {e["name"] for e in load_registry()}
    for s in skills:
        where = f"{s['dir'].name}/SKILL.md"
        if not s["name"] or not s["description"]:
            errors.append(f"{where}: frontmatter must have name and description")
        if s["name"] not in registry_names:
            errors.append(f"{where}: name {s['name']!r} not in skills.json")

    # distractors
    try:
        distractors = load_distractors(evals_dir)
    except (OSError, ValueError, AttributeError) as exc:
        errors.append(f"distractors.json: {exc}")
        distractors = []
    distractor_names = set()
    for d in distractors:
        dn = d["name"]
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", dn or ""):
            errors.append(f"distractors.json: invalid name {dn!r}")
        if not d["description"].strip():
            errors.append(f"distractors.json: {dn!r} needs a description")
        if dn in names:
            errors.append(f"distractors.json: {dn!r} collides with a real skill")
        if dn in distractor_names:
            errors.append(f"distractors.json: duplicate name {dn!r}")
        distractor_names.add(dn)
    routable = names | distractor_names

    # routing
    try:
        cases = load_routing(evals_dir)
    except (OSError, ValueError) as exc:
        errors.append(f"routing: {exc}")
        cases = []
    seen_ids = set()
    covered = set()
    hard_counts: Dict[str, int] = {}
    required = {"id", "difficulty", "prompt", "expected", "acceptable", "notes"}
    for c in cases:
        where = f"routing.jsonl:{c['_line']}"
        missing = required - set(c)
        extra = set(c) - required - {"_line", "heldout"}
        if missing:
            errors.append(f"{where}: missing keys {sorted(missing)}")
            continue
        if not isinstance(c.get("heldout", False), bool):
            errors.append(f"{where}: heldout must be boolean")
        if extra:
            errors.append(f"{where}: unknown keys {sorted(extra)}")
        if not isinstance(c["id"], str) or not c["id"]:
            errors.append(f"{where}: id must be a non-empty string")
        elif c["id"] in seen_ids:
            errors.append(f"{where}: duplicate id {c['id']!r}")
        seen_ids.add(c["id"])
        if not isinstance(c["prompt"], str) or not c["prompt"].strip():
            errors.append(f"{where}: prompt must be a non-empty string")
        if not isinstance(c["notes"], str):
            errors.append(f"{where}: notes must be a string")
        if c["difficulty"] not in DIFFICULTIES:
            errors.append(f"{where}: difficulty must be one of {list(DIFFICULTIES)}")
        exp, acc = c["expected"], c["acceptable"]
        if not (isinstance(exp, list) and len(exp) == 1 and isinstance(exp[0], str)):
            errors.append(
                f"{where}: expected must be a list with exactly one skill name or 'none'"
            )
            continue
        if exp[0] != "none" and exp[0] not in routable:
            errors.append(f"{where}: expected skill {exp[0]!r} does not exist")
        covered.add(exp[0])
        if c["difficulty"] == "hard":
            hard_counts[exp[0]] = hard_counts.get(exp[0], 0) + 1
        if not isinstance(acc, list) or not all(isinstance(a, str) for a in acc):
            errors.append(f"{where}: acceptable must be a list of skill names")
            continue
        for a in acc:
            if a not in routable:
                errors.append(f"{where}: acceptable skill {a!r} does not exist")
        if exp[0] in acc:
            errors.append(f"{where}: expected skill repeated in acceptable")
        if exp[0] == "none" and acc:
            errors.append(f"{where}: negative case ('none') must have empty acceptable")
        if len(set(acc)) != len(acc):
            errors.append(f"{where}: duplicate acceptable entries")
    if cases:
        for name in sorted(names - covered):
            errors.append(f"routing.jsonl: no case expects skill {name!r}")
        if "none" not in covered:
            errors.append("routing.jsonl: no negative case (expected ['none'])")
        for name in sorted(names):
            if hard_counts.get(name, 0) < MIN_HARD_CASES_PER_SKILL:
                errors.append(
                    f"routing.jsonl: skill {name!r} has {hard_counts.get(name, 0)} hard cases "
                    f"(minimum {MIN_HARD_CASES_PER_SKILL})"
                )

    # behavior
    try:
        scenarios = load_behavior(evals_dir)
    except (OSError, ValueError) as exc:
        errors.append(f"behavior: {exc}")
        scenarios = []
    seen_ids = set()
    required = {"id", "skill", "prompt", "input_material", "assertions"}
    for s in scenarios:
        where = f"behavior/{s['_file']}"
        missing = required - set(s)
        extra = set(s) - required - {"_file", "notes"}
        if missing:
            errors.append(f"{where}: missing keys {sorted(missing)}")
            continue
        if extra:
            errors.append(f"{where}: unknown keys {sorted(extra)}")
        if s["id"] in seen_ids:
            errors.append(f"{where}: duplicate scenario id {s['id']!r}")
        seen_ids.add(s["id"])
        if s["skill"] not in names:
            errors.append(f"{where}: skill {s['skill']!r} does not exist")
        for key in ("prompt", "input_material"):
            if not isinstance(s[key], str) or not s[key].strip():
                errors.append(f"{where}: {key} must be a non-empty string")
        if not isinstance(s["assertions"], list) or not s["assertions"]:
            errors.append(f"{where}: assertions must be a non-empty list")
            continue
        a_ids = set()
        for a in s["assertions"]:
            errors.extend(_check_assertion(where, a, a_ids))
    return errors


def _check_assertion(where: str, a: Any, a_ids: set) -> List[str]:
    errs: List[str] = []
    if not isinstance(a, dict) or "id" not in a or "type" not in a:
        return [f"{where}: every assertion needs id and type"]
    w = f"{where}#{a['id']}"
    if a["id"] in a_ids:
        errs.append(f"{w}: duplicate assertion id")
    a_ids.add(a["id"])
    if a.get("category") not in ASSERTION_CATEGORIES:
        errs.append(f"{w}: category must be one of {sorted(ASSERTION_CATEGORIES)}")
    if a["type"] == "regex":
        allowed = {
            "id",
            "type",
            "category",
            "description",
            "pattern",
            "all_of",
            "every_match",
            "flags",
            "min_count",
            "negate",
        }
        extra = set(a) - allowed
        if extra:
            errs.append(f"{w}: unknown keys {sorted(extra)}")
        if ("pattern" in a) == ("all_of" in a):
            errs.append(f"{w}: regex assertion needs exactly one of pattern / all_of")
        if "every_match" in a and "pattern" not in a:
            errs.append(f"{w}: every_match requires pattern")
        try:
            flags = compile_flags(a.get("flags", ""))
        except ValueError as exc:
            errs.append(f"{w}: {exc}")
            flags = 0
        patterns = []
        if "pattern" in a:
            patterns.append(a["pattern"])
        if "all_of" in a:
            if not isinstance(a["all_of"], list) or not a["all_of"]:
                errs.append(f"{w}: all_of must be a non-empty list")
            else:
                patterns.extend(a["all_of"])
        if "every_match" in a:
            patterns.append(a["every_match"])
        for p in patterns:
            if not isinstance(p, str):
                errs.append(f"{w}: pattern must be a string")
                continue
            try:
                re.compile(resolve_pattern(p), flags)
            except (re.error, OSError, ValueError) as exc:
                errs.append(f"{w}: regex does not compile: {exc}")
        mc = a.get("min_count", 1)
        if not isinstance(mc, int) or isinstance(mc, bool) or mc < 1:
            errs.append(f"{w}: min_count must be a positive integer")
        if not isinstance(a.get("negate", False), bool):
            errs.append(f"{w}: negate must be boolean")
    elif a["type"] == "judge":
        extra = set(a) - {"id", "type", "category", "question", "pass_criteria"}
        if extra:
            errs.append(f"{w}: unknown keys {sorted(extra)}")
        for key in ("question", "pass_criteria"):
            if not isinstance(a.get(key), str) or not a.get(key, "").strip():
                errs.append(f"{w}: judge assertion needs non-empty {key}")
    else:
        errs.append(f"{w}: type must be 'regex' or 'judge'")
    return errs


# --------------------------------------------------------------------------
# Model access
# --------------------------------------------------------------------------


class ModelRunner:
    """Runs the configured shell command with the prompt on stdin."""

    def __init__(
        self, cmd: str, model: Optional[str], timeout: float, dry_run: bool = False
    ):
        self.argv = shlex.split(cmd)
        if model:
            if any("{model}" in part for part in self.argv):
                self.argv = [part.replace("{model}", model) for part in self.argv]
            else:
                self.argv += ["--model", model]
        self.timeout = timeout
        self.dry_run = dry_run
        self.calls = 0
        self._lock = threading.Lock()
        # An empty working directory: no project instructions can be discovered.
        self._cwd = tempfile.mkdtemp(prefix="jaos-eval-")

    def close(self) -> None:
        shutil.rmtree(self._cwd, ignore_errors=True)

    def __call__(self, prompt: str) -> Tuple[str, Optional[str]]:
        """Return (stdout, error). error is None on success."""
        with self._lock:
            self.calls += 1
        try:
            proc = subprocess.run(
                self.argv,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self._cwd,
            )
        except subprocess.TimeoutExpired:
            return "", f"timeout after {self.timeout}s"
        except OSError as exc:
            return "", f"could not start command: {exc}"
        if proc.returncode != 0:
            return proc.stdout, f"exit {proc.returncode}: {proc.stderr.strip()[:500]}"
        return proc.stdout, None


def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    """First JSON object in text; tolerates code fences and surrounding prose."""
    text = text.strip()
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    for m in re.finditer(r"\{", text):
        try:
            obj, _ = decoder.raw_decode(text[m.start() :])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def call_json(
    runner: ModelRunner,
    prompt: str,
    validate: Callable[[Dict[str, Any]], bool],
    retries: int = 2,
) -> Dict[str, Any]:
    """Call the model expecting a JSON object; retry malformed answers up to `retries` times."""
    attempts = []
    for _ in range(retries + 1):
        out, err = runner(prompt)
        obj = extract_json_object(out) if err is None else None
        ok = obj is not None and validate(obj)
        attempts.append(
            {
                "raw": out[-2000:],
                "error": err if err else (None if ok else "malformed JSON"),
            }
        )
        if ok:
            return {"ok": True, "value": obj, "attempts": attempts}
    return {"ok": False, "value": None, "attempts": attempts}


def run_parallel(fn: Callable[[Any], Any], items: List[Any], jobs: int) -> List[Any]:
    if jobs <= 1:
        return [fn(x) for x in items]
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        return list(pool.map(fn, items))


# --------------------------------------------------------------------------
# Routing
# --------------------------------------------------------------------------


def case_seed(base_seed: int, case_id: str) -> int:
    """Deterministic per-case shuffle seed: same case, same order, on every run and machine."""
    return int(
        hashlib.sha256(f"{base_seed}:{case_id}".encode("utf-8")).hexdigest()[:8], 16
    )


def shuffled_listing(
    candidates: List[Dict[str, Any]], seed: int
) -> List[Dict[str, Any]]:
    ordered = sorted(candidates, key=lambda s: s["name"])
    random.Random(seed).shuffle(ordered)
    return ordered


def routing_prompt(skills: List[Dict[str, Any]], request: str) -> str:
    listing = "\n".join(
        f"<skill>\n<name>{s['name']}</name>\n<description>{s['description']}</description>\n</skill>"
        for s in skills
    )
    return (
        "You are an AI agent. The skills below are available to you. Each is shown only by the "
        "name and description from its SKILL.md frontmatter, exactly as an agent sees them before "
        "deciding which skill to load.\n\n"
        f"<available_skills>\n{listing}\n</available_skills>\n\n"
        "Decide which ONE skill you would load first to handle the user request below. "
        'If none of the skills is relevant to the request, answer "none".\n\n'
        f"<request>\n{request}\n</request>\n\n"
        'Respond with only a JSON object and nothing else: {"skill": "<skill name>"} or {"skill": "none"}.'
    )


def effective_expectation(
    case: Dict[str, Any], ours: set, use_distractors: bool
) -> Tuple[str, List[str]]:
    """Expected answer under the current condition.

    Without distractors, a case whose right tool is a distractor expects "none"
    (the correct call is still "not one of our skills").
    """
    expected = case["expected"][0]
    acceptable = list(case["acceptable"])
    if not use_distractors:
        if expected not in ours:
            expected = "none"
        acceptable = [a for a in acceptable if a in ours]
    return expected, acceptable


def run_routing(
    args: argparse.Namespace, evals_dir: Path, runner: ModelRunner
) -> Optional[Dict[str, Any]]:
    skills = load_skills()
    ours = {s["name"] for s in skills}
    use_distractors = not args.no_distractors
    distractors = load_distractors(evals_dir) if use_distractors else []
    distractor_names = {d["name"] for d in distractors}
    candidates = [
        {"name": s["name"], "description": s["description"]} for s in skills
    ] + distractors
    valid_names = {c["name"] for c in candidates}
    cases = select(load_routing(evals_dir), args)

    def prompt_for(case: Dict[str, Any]) -> Tuple[int, str]:
        seed = case_seed(args.seed, case["id"])
        return seed, routing_prompt(shuffled_listing(candidates, seed), case["prompt"])

    if args.dry_run:
        for c in cases:
            seed, prompt = prompt_for(c)
            print(f"===== {c['id']} (seed {seed}) =====")
            print(prompt)
            print()
        return None

    def valid(obj: Dict[str, Any]) -> bool:
        return isinstance(obj.get("skill"), str) and (
            obj["skill"] in valid_names or obj["skill"] == "none"
        )

    def one(case: Dict[str, Any]) -> Dict[str, Any]:
        seed, prompt = prompt_for(case)
        res = call_json(runner, prompt, valid, args.retries)
        predicted = res["value"]["skill"] if res["ok"] else "__error__"
        expected, acceptable = effective_expectation(case, ours, use_distractors)
        return {
            "id": case["id"],
            "difficulty": case["difficulty"],
            "heldout": bool(case.get("heldout", False)),
            "seed": seed,
            "expected": expected,
            "acceptable": acceptable,
            "predicted": predicted,
            "exact": predicted == expected,
            "acceptable_hit": predicted == expected or predicted in acceptable,
            # one of our skills lost the case to a neighbour skill
            "distractor_steal": expected in ours and predicted in distractor_names,
            # one of our skills claimed a case that is not ours
            "over_trigger": expected not in ours and predicted in ours,
            "attempts": res["attempts"],
        }

    results = run_parallel(one, cases, args.jobs)

    def acc(rows: List[Dict[str, Any]], key: str) -> Optional[float]:
        return round(sum(r[key] for r in rows) / len(rows), 4) if rows else None

    per_skill: Dict[str, Dict[str, Any]] = {}
    for r in results:
        row = per_skill.setdefault(
            r["expected"], {"cases": 0, "exact": 0, "acceptable": 0, "confusions": []}
        )
        row["cases"] += 1
        row["exact"] += int(r["exact"])
        row["acceptable"] += int(r["acceptable_hit"])
        if not r["exact"]:
            row["confusions"].append({"id": r["id"], "predicted": r["predicted"]})
    pairs: Dict[Tuple[str, str], List[str]] = {}
    for r in results:
        if not r["acceptable_hit"]:
            pairs.setdefault((r["expected"], r["predicted"]), []).append(r["id"])
    confusion_pairs = [
        {"expected": e, "predicted": p, "count": len(ids), "cases": ids}
        for (e, p), ids in sorted(pairs.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    ]
    acceptable_not_exact = [
        {"id": r["id"], "expected": r["expected"], "predicted": r["predicted"]}
        for r in results if r["acceptable_hit"] and not r["exact"]
    ]
    predicted_counts: Dict[str, int] = {}
    for r in results:
        predicted_counts[r["predicted"]] = predicted_counts.get(r["predicted"], 0) + 1

    def subset(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {"cases": len(rows), "exact_accuracy": acc(rows, "exact"),
                "acceptable_accuracy": acc(rows, "acceptable_hit")}

    by_split = {
        "heldout": subset([r for r in results if r["heldout"]]),
        "development": subset([r for r in results if not r["heldout"]]),
    }
    by_difficulty = {}
    for d in DIFFICULTIES:
        rows = [r for r in results if r["difficulty"] == d]
        by_difficulty[d] = {
            "cases": len(rows),
            "exact_accuracy": acc(rows, "exact"),
            "acceptable_accuracy": acc(rows, "acceptable_hit"),
        }
    return {
        "summary": {
            "cases": len(results),
            "distractors": use_distractors,
            "candidate_skills": len(candidates),
            "distractor_skills": len(distractors),
            "base_seed": args.seed,
            "exact_accuracy": acc(results, "exact"),
            "acceptable_accuracy": acc(results, "acceptable_hit"),
            "by_difficulty": by_difficulty,
            "by_split": by_split,
            "distractor_steals": sum(r["distractor_steal"] for r in results),
            "over_triggers": sum(r["over_trigger"] for r in results),
            "errors": sum(r["predicted"] == "__error__" for r in results),
        },
        "per_skill": dict(sorted(per_skill.items())),
        "confusion_pairs": confusion_pairs,
        "acceptable_not_exact": acceptable_not_exact,
        "predicted_counts": dict(sorted(predicted_counts.items())),
        "cases": results,
    }


# --------------------------------------------------------------------------
# Behavior
# --------------------------------------------------------------------------


def task_block(scenario: Dict[str, Any]) -> str:
    return (
        f"Task:\n{scenario['prompt'].strip()}\n\n"
        f"Input material (fictional):\n<input_material>\n{scenario['input_material'].strip()}\n</input_material>\n\n"
        "Produce the deliverable directly, in Markdown. You cannot ask questions; state assumptions."
    )


def generation_prompt(scenario: Dict[str, Any], skill: Optional[Dict[str, Any]]) -> str:
    if skill is None:
        return task_block(scenario)
    parts = [
        "The following Agent Skill is loaded for this task. Follow its instructions.\n",
        f'<skill name="{skill["name"]}">\n{skill["text"].strip()}\n</skill>\n',
    ]
    for rel, content in referenced_files(skill):
        parts.append(f'<skill_file path="{rel}">\n{content.strip()}\n</skill_file>\n')
    parts.append(task_block(scenario))
    return "\n".join(parts)


def judge_prompt(
    scenario: Dict[str, Any], assertion: Dict[str, Any], response: str
) -> str:
    return (
        "You are a strict, impartial evaluator. Grade ONE yes/no assertion about the RESPONSE "
        "below. Judge only the response text against the pass criteria; ignore style, length, "
        "and formatting unless the criteria mention them. If the response does not clearly meet "
        "the criteria, the assertion fails. Generic caution (e.g. 'validate with more research', "
        "'the sample may be small', 'data quality should be checked') does not pass unless it names "
        "the specific issue the criteria describe.\n\n"
        f"<task_given_to_author>\n{scenario['prompt'].strip()}\n</task_given_to_author>\n\n"
        f"<input_material>\n{scenario['input_material'].strip()}\n</input_material>\n\n"
        f"<response>\n{response.strip()}\n</response>\n\n"
        f"Assertion question: {assertion['question']}\n"
        f"Pass criteria: {assertion['pass_criteria']}\n\n"
        'Respond with only a JSON object and nothing else: {"pass": true or false, "reason": "<one sentence>"}'
    )


OUR_SKILL_NAME_RE = None  # compiled lazily from skills.json


def normalize_for_judge(text: str) -> str:
    """Reduce tells of which condition produced an output before a method judge sees it.

    Ontology IDs (EVD-2026-0001, MTM-0003, ...) become [ID-1], [ID-2], ... consistently within
    the output, and the suite's skill names become [SKILL]. Both only appear when the skill
    was loaded, so leaving them in would let the judge guess the condition.
    """
    global OUR_SKILL_NAME_RE
    if OUR_SKILL_NAME_RE is None:
        names = sorted((e["name"] for e in load_registry()), key=len, reverse=True)
        OUR_SKILL_NAME_RE = re.compile(r"`?\b(?:" + "|".join(map(re.escape, names)) + r")\b`?")
    mapping: Dict[str, str] = {}

    def repl(m: "re.Match[str]") -> str:
        return mapping.setdefault(m.group(0), f"[ID-{len(mapping) + 1}]")

    text = re.sub(ontology_id_finder(), repl, text)
    return OUR_SKILL_NAME_RE.sub("[SKILL]", text)


def grade_regex(assertion: Dict[str, Any], text: str) -> Tuple[bool, str]:
    flags = compile_flags(assertion.get("flags", ""))
    min_count = assertion.get("min_count", 1)
    if "all_of" in assertion:
        missing = [p for p in assertion["all_of"] if not re.search(p, text, flags)]
        passed, reason = (
            not missing,
            ("all patterns found" if not missing else f"missing: {missing}"),
        )
    else:
        matches = [m.group(0) for m in re.finditer(resolve_pattern(assertion["pattern"]), text, flags)]
        if "every_match" in assertion:
            bad = sorted(
                {
                    m
                    for m in matches
                    if not re.fullmatch(resolve_pattern(assertion["every_match"]), m, flags)
                }
            )
            passed = len(matches) >= min_count and not bad
            reason = f"{len(matches)} matches" + (
                f"; invalid: {bad[:10]}" if bad else ""
            )
        else:
            passed = len(matches) >= min_count
            reason = f"{len(matches)} matches (need {min_count})"
    if assertion.get("negate"):
        passed = not passed
        reason = "negated: " + reason
    return passed, reason


CONDITIONS = ("with_skill", "baseline")
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 12345


def run_behavior(
    args: argparse.Namespace, evals_dir: Path, runner: ModelRunner
) -> Optional[Dict[str, Any]]:
    skills = {s["name"]: s for s in load_skills()}
    scenarios = select(load_behavior(evals_dir), args)
    repeats = args.repeats
    if args.dry_run:
        for sc in scenarios:
            for cond in CONDITIONS:
                print(f"===== {sc['id']} [{cond}] x{repeats} =====")
                print(generation_prompt(sc, skills[sc["skill"]] if cond == "with_skill" else None))
                print()
            judges = [a for a in sc["assertions"] if a["type"] == "judge"]
            if judges:
                print(f"===== {sc['id']} [judge prompt, first judge assertion] =====")
                print(judge_prompt(sc, judges[0], "<model response goes here>"))
                print()
        return None

    # Phase 1: generate N outputs per scenario and condition.
    gen_items = [(sc, cond, r) for sc in scenarios for cond in CONDITIONS for r in range(repeats)]

    def generate(item: Tuple[Dict[str, Any], str, int]) -> Dict[str, Any]:
        sc, cond, rep = item
        prompt = generation_prompt(sc, skills[sc["skill"]] if cond == "with_skill" else None)
        out, err = "", None
        for _ in range(args.retries + 1):
            out, err = runner(prompt)
            if err is None and out.strip():
                break
            err = err or "empty output"
        return {"scenario": sc["id"], "condition": cond, "repeat": rep, "output": out or "", "error": err}

    outputs = run_parallel(generate, gen_items, args.jobs)
    by_key = {(o["scenario"], o["condition"], o["repeat"]): o for o in outputs}

    # Phase 2: grade. Regex locally; judge assertions via separate, condition-blind calls.
    judge_items = []
    runs: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for sc in scenarios:
        for cond in CONDITIONS:
            for rep in range(repeats):
                gen = by_key[(sc["id"], cond, rep)]
                rows = []
                for a in sc["assertions"]:
                    row = {"id": a["id"], "type": a["type"], "category": a["category"]}
                    if gen["error"]:
                        row.update(passed=False, reason=f"generation failed: {gen['error']}")
                    elif a["type"] == "regex":
                        row["passed"], row["reason"] = grade_regex(a, gen["output"])
                    else:
                        judge_items.append((sc, a, gen["output"], row))
                    rows.append(row)
                runs.setdefault((sc["id"], cond), []).append(
                    {"repeat": rep, "error": gen["error"], "output": gen["output"], "assertions": rows}
                )

    def judge(item: Tuple[Dict[str, Any], Dict[str, Any], str, Dict[str, Any]]) -> None:
        sc, a, output, row = item
        graded = normalize_for_judge(output) if a["category"] == "method" else output
        res = call_json(
            runner,
            judge_prompt(sc, a, graded),
            lambda o: isinstance(o.get("pass"), bool) and isinstance(o.get("reason", ""), str),
            args.retries,
        )
        if res["ok"]:
            row["passed"] = res["value"]["pass"]
            row["reason"] = str(res["value"].get("reason", ""))[:500]
        else:
            row["passed"] = False
            row["reason"] = "judge error: " + str(res["attempts"][-1]["error"])
            row["judge_error"] = True

    run_parallel(judge, judge_items, args.jobs)

    # Aggregate.
    scenario_results = []
    all_rows: Dict[str, List[Dict[str, Any]]] = {c: [] for c in CONDITIONS}
    for sc in scenarios:
        entry: Dict[str, Any] = {"id": sc["id"], "skill": sc["skill"], "conditions": {}}
        for cond in CONDITIONS:
            cond_runs = runs[(sc["id"], cond)]
            rows = [r for run in cond_runs for r in run["assertions"]]
            all_rows[cond].extend(rows)
            per_assertion = []
            for a in sc["assertions"]:
                hits = [r["passed"] for run in cond_runs for r in run["assertions"] if r["id"] == a["id"]]
                per_assertion.append({"id": a["id"], "type": a["type"], "category": a["category"],
                                      "passes": sum(hits), "n": len(hits)})
            entry["conditions"][cond] = {"pass_rate": _rate(rows), "per_assertion": per_assertion, "runs": cond_runs}
        scenario_results.append(entry)

    summary: Dict[str, Any] = {"scenarios": len(scenarios), "repeats": repeats, "conditions": {}}
    for cond in CONDITIONS:
        rows = all_rows[cond]
        summary["conditions"][cond] = {
            "pass_rate": _rate(rows),
            "by_category": {cat: _rate([r for r in rows if r["category"] == cat]) for cat in sorted(ASSERTION_CATEGORIES)},
            "by_type": {t: _rate([r for r in rows if r["type"] == t]) for t in ("regex", "judge")},
            "graded_assertions": len(rows),
        }
    w, b = summary["conditions"]["with_skill"], summary["conditions"]["baseline"]
    summary["delta_pp"] = _delta(w["pass_rate"], b["pass_rate"])
    summary["delta_pp_by_category"] = {
        cat: _delta(w["by_category"][cat], b["by_category"][cat]) for cat in sorted(ASSERTION_CATEGORIES)
    }
    summary["significance"] = {
        "method": paired_statistics(scenario_results, "method"),
        "all": paired_statistics(scenario_results, None),
    }
    summary["judge_errors"] = sum(1 for c in CONDITIONS for r in all_rows[c] if r.get("judge_error"))
    summary["generation_errors"] = sum(1 for o in outputs if o["error"])
    return {"summary": summary, "scenarios": scenario_results}


def _rate(rows: List[Dict[str, Any]]) -> Optional[float]:
    return round(sum(bool(r["passed"]) for r in rows) / len(rows), 4) if rows else None


def sign_test_p(n_pos: int, n_neg: int) -> Optional[float]:
    """Two-sided exact sign test (binomial, p = 0.5); ties are dropped beforehand."""
    n = n_pos + n_neg
    if n == 0:
        return None
    k = min(n_pos, n_neg)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return round(min(1.0, 2 * tail), 4)


def paired_statistics(scenario_results: List[Dict[str, Any]], category: Optional[str]) -> Dict[str, Any]:
    """Paired with-skill vs baseline comparison over assertions.

    * sign test: unit = assertion; sign of (with passes - baseline passes) across repeats.
    * bootstrap: resample scenarios (assertions within a scenario share one output, so they
      are not independent), recompute the pooled pass-rate delta; percentile 95% CI.
    """
    per_scenario = []
    n_pos = n_neg = n_tie = 0
    for sc in scenario_results:
        wa = {a["id"]: a for a in sc["conditions"]["with_skill"]["per_assertion"]}
        ba = {a["id"]: a for a in sc["conditions"]["baseline"]["per_assertion"]}
        sw = sb = n = 0
        for aid, a in wa.items():
            if category and a["category"] != category:
                continue
            diff = a["passes"] - ba[aid]["passes"]
            n_pos += diff > 0
            n_neg += diff < 0
            n_tie += diff == 0
            sw += a["passes"]
            sb += ba[aid]["passes"]
            n += a["n"]
        if n:
            per_scenario.append((sw, sb, n))
    result: Dict[str, Any] = {
        "assertions_better": n_pos, "assertions_worse": n_neg, "assertions_tied": n_tie,
        "sign_test_p": sign_test_p(n_pos, n_neg),
        "delta_pp": None, "ci95_pp": None,
        "bootstrap": {"unit": "scenario", "resamples": BOOTSTRAP_RESAMPLES, "seed": BOOTSTRAP_SEED},
    }
    if not per_scenario:
        return result
    total_n = sum(n for _, _, n in per_scenario)
    result["delta_pp"] = round((sum(w for w, _, _ in per_scenario) - sum(b for _, b, _ in per_scenario)) / total_n * 100, 1)
    rng = random.Random(BOOTSTRAP_SEED)
    deltas = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        sample = [per_scenario[rng.randrange(len(per_scenario))] for _ in per_scenario]
        n = sum(x[2] for x in sample)
        deltas.append((sum(x[0] for x in sample) - sum(x[1] for x in sample)) / n * 100)
    deltas.sort()
    lo = deltas[int(0.025 * (len(deltas) - 1))]
    hi = deltas[int(0.975 * (len(deltas) - 1))]
    result["ci95_pp"] = [round(lo, 1), round(hi, 1)]
    return result


def _delta(a: Optional[float], b: Optional[float]) -> Optional[float]:
    return None if a is None or b is None else round((a - b) * 100, 1)


# --------------------------------------------------------------------------
# Reports
# --------------------------------------------------------------------------


def pct(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{x * 100:.1f}%"


def signed(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{x:+.1f} pp"


def dirty_banner(meta: Dict[str, Any]) -> List[str]:
    lines = []
    if meta["dirty"]:
        lines += ["> **DIRTY - not a release result.** Produced from a working tree with uncommitted "
                  "changes; the commit hash does not identify what was evaluated.", ""]
    if meta.get("partial"):
        lines += ["> **Partial run - not a release result.** Filtered with --case or --limit.", ""]
    return lines


def routing_markdown(meta: Dict[str, Any], res: Dict[str, Any]) -> str:
    s = res["summary"]
    cond = (
        f"incl. {s['distractor_skills']} distractor skills"
        if s["distractors"]
        else "no distractors"
    )
    lines = [
        f"# Routing eval: {meta['date']}",
        "",
        *dirty_banner(meta),
        _meta_block(meta),
        f"Condition: {s['candidate_skills']} candidate skills ({cond}), listing shuffled per case "
        f"with base seed {s['base_seed']}.",
        "",
        "| Cases | Exact primary | Primary or acceptable | Distractor steals | Over-triggers | Errors |",
        "|---:|---:|---:|---:|---:|---:|",
        f"| {s['cases']} | {pct(s['exact_accuracy'])} | {pct(s['acceptable_accuracy'])} | "
        f"{s['distractor_steals']} | {s['over_triggers']} | {s['errors']} |",
        "",
        "Distractor steal: one of the suite's skills was expected, a neighbour skill was picked. "
        "Over-trigger: the case is not ours (a neighbour skill or none), one of our skills was picked.",
        "",
        "## By difficulty",
        "",
        "| Difficulty | Cases | Exact primary | Primary or acceptable |",
        "|---|---:|---:|---:|",
    ]
    for d, row in s["by_difficulty"].items():
        lines.append(
            f"| {d} | {row['cases']} | {pct(row['exact_accuracy'])} | {pct(row['acceptable_accuracy'])} |"
        )
    lines += [
        "",
        "## Held-out vs development cases",
        "",
        "Held-out cases are never used to tune skill descriptions; their accuracy is the honest "
        "estimate of routing quality.",
        "",
        "| Split | Cases | Exact primary | Primary or acceptable |",
        "|---|---:|---:|---:|",
    ]
    for split, row in s["by_split"].items():
        lines.append(
            f"| {split} | {row['cases']} | {pct(row['exact_accuracy'])} | {pct(row['acceptable_accuracy'])} |"
        )
    lines += [
        "",
        "## Non-exact cases",
        "",
        "### Misses (neither expected nor acceptable)",
        "",
        "| Expected | Predicted | Count | Cases |",
        "|---|---|---:|---|",
    ]
    for cp in res["confusion_pairs"]:
        lines.append(
            f"| `{cp['expected']}` | `{cp['predicted']}` | {cp['count']} | {', '.join(cp['cases'])} |"
        )
    if not res["confusion_pairs"]:
        lines.append("| - | - | 0 | - |")
    lines += [
        "",
        "### Acceptable but not the expected primary",
        "",
        "| Case | Expected | Predicted |",
        "|---|---|---|",
    ]
    for c in res["acceptable_not_exact"]:
        lines.append(f"| {c['id']} | `{c['expected']}` | `{c['predicted']}` |")
    if not res["acceptable_not_exact"]:
        lines.append("| - | - | - |")
    lines += [
        "",
        "## Per expected skill",
        "",
        "| Expected | Cases | Exact | Acceptable | Misrouted to |",
        "|---|---:|---:|---:|---|",
    ]
    for skill, row in res["per_skill"].items():
        conf = (
            ", ".join(f"`{c['predicted']}` ({c['id']})" for c in row["confusions"])
            or "-"
        )
        lines.append(
            f"| `{skill}` | {row['cases']} | {row['exact']} | {row['acceptable']} | {conf} |"
        )
    lines += [
        "",
        "## Cases",
        "",
        "| Case | Difficulty | Held-out | Seed | Expected | Predicted | Result |",
        "|---|---|---|---:|---|---|---|",
    ]
    for c in res["cases"]:
        verdict = (
            "exact" if c["exact"] else ("acceptable" if c["acceptable_hit"] else "miss")
        )
        if c["distractor_steal"]:
            verdict += " (distractor steal)"
        if c["over_trigger"]:
            verdict += " (over-trigger)"
        lines.append(
            f"| {c['id']} | {c['difficulty']} | {'yes' if c['heldout'] else ''} | {c['seed']} | `{c['expected']}` | `{c['predicted']}` | {verdict} |"
        )
    return "\n".join(lines) + "\n"


def behavior_markdown(meta: Dict[str, Any], res: Dict[str, Any]) -> str:
    s = res["summary"]
    w, b = s["conditions"]["with_skill"], s["conditions"]["baseline"]
    n = s["repeats"]
    lines = [
        f"# Behavior eval: {meta['date']}",
        "",
        *dirty_banner(meta),
        _meta_block(meta),
        f"Each scenario ran {n} time(s) per condition. Pass rates are means over all graded assertions.",
        "",
        "| | With skill | Baseline | Delta |",
        "|---|---:|---:|---:|",
        f"| All assertions | {pct(w['pass_rate'])} | {pct(b['pass_rate'])} | {signed(s['delta_pp'])} |",
    ]
    for cat in sorted(ASSERTION_CATEGORIES):
        lines.append(
            f"| {cat} assertions | {pct(w['by_category'][cat])} | {pct(b['by_category'][cat])} | "
            f"{signed(s['delta_pp_by_category'][cat])} |"
        )
    lines += ["", "## Is the difference real?", "",
              "| Scope | Delta | 95% CI (bootstrap over scenarios) | Assertions better / worse / tied | Sign test p |",
              "|---|---:|---|---|---:|"]
    for scope, st in (("method", s["significance"]["method"]), ("all", s["significance"]["all"])):
        ci = "n/a" if st["ci95_pp"] is None else f"[{st['ci95_pp'][0]:+.1f}, {st['ci95_pp'][1]:+.1f}] pp"
        p = "n/a" if st["sign_test_p"] is None else f"{st['sign_test_p']:.4f}"
        lines.append(f"| {scope} | {signed(st['delta_pp'])} | {ci} | "
                     f"{st['assertions_better']} / {st['assertions_worse']} / {st['assertions_tied']} | {p} |")
    lines += [
        "",
        f"Generation errors: {s['generation_errors']}. Judge errors: {s['judge_errors']}.",
        "",
        "`convention` assertions check the suite's own conventions (ontology IDs, enum labels) and "
        "favour the with-skill condition by construction. `method` assertions check whether subtle "
        "traps in the input were caught; they are the measure of what a skill adds. The bootstrap "
        "resamples scenarios because assertions graded on the same output are not independent.",
        "",
        "## Per scenario",
        "",
        "| Scenario | Skill | With skill | Baseline | Delta |",
        "|---|---|---:|---:|---:|",
    ]
    for sc in res["scenarios"]:
        cw, cb = sc["conditions"]["with_skill"], sc["conditions"]["baseline"]
        lines.append(
            f"| {sc['id']} | `{sc['skill']}` | {pct(cw['pass_rate'])} | {pct(cb['pass_rate'])} | "
            f"{signed(_delta(cw['pass_rate'], cb['pass_rate']))} |"
        )
    lines += ["", "## Assertions (passes / runs)", "",
              "| Scenario | Assertion | Category | With skill | Baseline |", "|---|---|---|:-:|:-:|"]
    for sc in res["scenarios"]:
        rb = {a["id"]: a for a in sc["conditions"]["baseline"]["per_assertion"]}
        for a in sc["conditions"]["with_skill"]["per_assertion"]:
            o = rb[a["id"]]
            lines.append(f"| {sc['id']} | {a['id']} | {a['category']} | {a['passes']}/{a['n']} | {o['passes']}/{o['n']} |")
    return "\n".join(lines) + "\n"


def _mark(row: Dict[str, Any]) -> str:
    return "pass" if row.get("passed") else "fail"


def _meta_block(meta: Dict[str, Any]) -> str:
    return (
        f"- Command: `{meta['cmd']}`\n- Model: {meta['model'] or 'command default'}\n"
        f"- Filters: {meta['filters']}\n- Model calls: {meta['model_calls']}\n"
        f"- Repository commit: {meta['commit'] or 'unknown'}"
        f"{' (working tree DIRTY)' if meta['dirty'] else ''}\n"
        f"- Files loaded into prompts: {len(meta['loaded_files'])} (sha256 in the JSON)\n"
    )


def git_state() -> Dict[str, Any]:
    """HEAD commit and whether the working tree differs from it (evals/results/ ignored)."""
    def git(*cmd: str) -> Optional[str]:
        try:
            out = subprocess.run(["git", *cmd], cwd=ROOT, capture_output=True, text=True, timeout=20)
        except (OSError, subprocess.SubprocessError):
            return None
        return out.stdout if out.returncode == 0 else None

    head = git("rev-parse", "HEAD")
    status = git("status", "--porcelain", "--untracked-files=all")
    changed = []
    if status is not None:
        for line in status.splitlines():
            path = line[3:].split(" -> ")[-1].strip('"')
            if not path.startswith("evals/results/"):
                changed.append(path)
    return {
        "commit": head.strip() if head else None,
        "dirty": True if head is None or status is None else bool(changed),
        "changed_files": changed[:200],
    }


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def loaded_file_hashes(mode: str, evals_dir: Path, args: argparse.Namespace) -> Dict[str, str]:
    """sha256 of every skill file and eval file that went into the prompts."""
    files: List[Path] = []
    skills = {s["name"]: s for s in load_skills()}
    if mode == "routing":
        files += [s["dir"] / "SKILL.md" for s in skills.values()]
        files.append(evals_dir / "routing.jsonl")
        if not args.no_distractors and (evals_dir / "distractors.json").exists():
            files.append(evals_dir / "distractors.json")
    else:
        for sc in select(load_behavior(evals_dir), args):
            skill = skills[sc["skill"]]
            files.append(skill["dir"] / "SKILL.md")
            files += referenced_paths(skill)
            files.append(evals_dir / "behavior" / sc["_file"])
    out: Dict[str, str] = {}
    for f in files:
        f = f.resolve()
        try:
            key = str(f.relative_to(ROOT))
        except ValueError:
            key = str(f)
        out[key] = file_sha256(f)
    return dict(sorted(out.items()))


def select(
    items: List[Dict[str, Any]], args: argparse.Namespace
) -> List[Dict[str, Any]]:
    if args.case:
        wanted = set(args.case)
        unknown = wanted - {i["id"] for i in items}
        if unknown:
            raise SystemExit(f"unknown case id(s): {', '.join(sorted(unknown))}")
        items = [i for i in items if i["id"] in wanted]
    if args.limit is not None:
        items = items[: args.limit]
    return items


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "--check", action="store_true", help="validate eval files; no model calls"
    )
    p.add_argument("--mode", choices=("routing", "behavior"), help="suite to run")
    p.add_argument(
        "--cmd",
        default=DEFAULT_CMD,
        help="shell command that reads a prompt on stdin and prints the answer "
        "(default: isolated `claude -p`, see README)",
    )
    p.add_argument(
        "--model",
        help="model name; substituted for {model} in --cmd, else appended as --model",
    )
    p.add_argument(
        "--jobs", type=int, default=3, help="concurrent model calls (default 3)"
    )
    p.add_argument(
        "--timeout",
        type=float,
        default=300,
        help="per-call timeout in seconds (default 300)",
    )
    p.add_argument(
        "--retries",
        type=int,
        default=2,
        help="retries on malformed JSON or failed call (default 2)",
    )
    p.add_argument("--limit", type=int, help="run only the first N cases/scenarios")
    p.add_argument(
        "--case", action="append", help="run only this case/scenario ID (repeatable)"
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="print prompts; no model calls, no results",
    )
    p.add_argument(
        "--allow-dirty",
        action="store_true",
        help="allow writing into evals/results/ from a dirty tree (results marked DIRTY)",
    )
    p.add_argument(
        "--repeats",
        type=int,
        default=1,
        help="behavior: generations per scenario and condition (default 1)",
    )
    p.add_argument(
        "--no-distractors",
        action="store_true",
        help="routing: list only the suite's skills (default lists evals/distractors.json too)",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=0,
        help="routing: base seed for the per-case shuffle of the skill listing (default 0)",
    )
    p.add_argument(
        "--evals-dir", type=Path, default=DEFAULT_EVALS_DIR, help=argparse.SUPPRESS
    )
    p.add_argument(
        "--results-dir",
        type=Path,
        help="where to write results (default: <evals-dir>/results)",
    )
    args = p.parse_args(argv)

    evals_dir = args.evals_dir.resolve()
    if args.check:
        errors = check_evals(evals_dir)
        if errors:
            for e in errors:
                print(f"ERROR {e}")
            return 1
        n_routing = len(load_routing(evals_dir))
        n_behavior = len(load_behavior(evals_dir))
        print(f"evals OK: {n_routing} routing cases, {n_behavior} behavior scenarios")
        if not args.mode:
            return 0
    if not args.mode:
        p.error("choose --check and/or --mode")
    if args.jobs < 1 or args.repeats < 1 or args.retries < 0:
        p.error("--jobs and --repeats must be >= 1 and --retries >= 0")

    out_dir = (args.results_dir or evals_dir / "results").resolve()
    state = git_state()
    if not args.dry_run and state["dirty"] and not args.allow_dirty:
        release_dir = (ROOT / "evals" / "results").resolve()
        if out_dir == release_dir or release_dir in out_dir.parents:
            print(
                "refusing to write into evals/results/ from a dirty working tree "
                f"({len(state['changed_files'])} changed file(s), e.g. {state['changed_files'][:3]}). "
                "Commit first, write elsewhere with --results-dir, or pass --allow-dirty "
                "(results will be marked DIRTY - not a release result).",
                file=sys.stderr,
            )
            return 2
    hashes = loaded_file_hashes(args.mode, evals_dir, args)

    runner = ModelRunner(args.cmd, args.model, args.timeout, args.dry_run)
    started = _dt.datetime.now()
    try:
        result = (run_routing if args.mode == "routing" else run_behavior)(
            args, evals_dir, runner
        )
    finally:
        runner.close()
    if result is None:  # dry run
        return 0
    date = started.strftime("%Y-%m-%d")
    partial = bool(args.case or args.limit is not None)
    meta = {
        "date": date,
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "mode": args.mode,
        "cmd": " ".join(shlex.quote(a) for a in runner.argv),
        "model": args.model,
        "filters": {"case": args.case, "limit": args.limit, "repeats": args.repeats},
        "model_calls": runner.calls,
        "commit": state["commit"],
        "dirty": state["dirty"],
        "changed_files": state["changed_files"],
        "partial": partial,
        "release": not state["dirty"] and not partial,
        "loaded_files": hashes,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = out_dir / results_stem(started, args)
    json_path, md_path = stem.with_suffix(".json"), stem.with_suffix(".md")
    json_path.write_text(
        json.dumps({"meta": meta, **result}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    md = (
        routing_markdown(meta, result)
        if args.mode == "routing"
        else behavior_markdown(meta, result)
    )
    md_path.write_text(md, encoding="utf-8")
    if meta["release"]:
        update_latest_pointer(out_dir, result_kind(args), json_path.name, meta)
    print(md)
    print(f"wrote {json_path} and {md_path}")
    return 0


def result_kind(args: argparse.Namespace) -> str:
    if args.mode == "routing" and args.no_distractors:
        return "routing-no-distractors"
    return args.mode


def results_stem(started: _dt.datetime, args: argparse.Namespace) -> str:
    """<YYYY-MM-DDTHHMM>-<kind>[-rN][-limitN][-caseN]; never reuses an existing name."""
    parts = [started.strftime("%Y-%m-%dT%H%M"), result_kind(args)]
    if args.mode == "behavior" and args.repeats > 1:
        parts.append(f"r{args.repeats}")
    if args.limit is not None:
        parts.append(f"limit{args.limit}")
    if args.case:
        parts.append(f"case{len(args.case)}")
    base = "-".join(parts)
    out_dir = (args.results_dir or args.evals_dir / "results").resolve()
    name, n = base, 2
    while (out_dir / f"{name}.json").exists() or (out_dir / f"{name}.md").exists():
        name, n = f"{base}-{n}", n + 1
    return name


def update_latest_pointer(out_dir: Path, kind: str, filename: str, meta: Dict[str, Any]) -> None:
    """evals/results/latest.json: newest release result per kind (clean tree, no filters)."""
    path = out_dir / "latest.json"
    try:
        latest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        latest = {}
    latest[kind] = {"file": filename, "commit": meta["commit"], "started_at": meta["started_at"]}
    path.write_text(json.dumps(dict(sorted(latest.items())), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
