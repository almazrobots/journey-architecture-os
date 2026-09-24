#!/usr/bin/env python3
"""Mutation testing for scripts/validate_repo.py (standard library only).

Each mutant changes one AST node of the target, is written into a private
copy of the repository, and the validator test suite is run against it. A
mutant is killed when the suite fails or times out; it survives when the
suite still passes, which means no test notices that behaviour.

Operators:
  compare   ==/!=, </<=, >/>=, in/not in, is/is not
  boolop    and <-> or
  not       `not x` -> `x`
  return    `return 0` <-> `return 1`
  bool      True <-> False
  int       integer constant n -> n + 1
  string    non-empty string literal -> '' (docstrings and f-string parts excluded)
  regex     string literal starting with ^ / ending with $: drop the anchor
  delete    expression statement that is a call (report.error, append, ...) -> pass
  empty     non-empty list/set/dict/tuple literal or comprehension -> empty

Usage:
  python3 scripts/mutation_test.py                 # full run, threshold 90
  python3 scripts/mutation_test.py --report docs/quality/mutation-report.md
  python3 scripts/mutation_test.py --limit 10      # size a run first
  python3 scripts/mutation_test.py --list          # list mutants only
"""

import argparse
import ast
import os
import queue
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = "scripts/validate_repo.py"
DEFAULT_TESTS = ["tests.test_repository", "tests.test_validator"]

COMPARE_SWAP = {
    ast.Eq: ast.NotEq,
    ast.NotEq: ast.Eq,
    ast.Lt: ast.LtE,
    ast.LtE: ast.Lt,
    ast.Gt: ast.GtE,
    ast.GtE: ast.Gt,
    ast.In: ast.NotIn,
    ast.NotIn: ast.In,
    ast.Is: ast.IsNot,
    ast.IsNot: ast.Is,
}
SYMBOL = {
    ast.Eq: "==",
    ast.NotEq: "!=",
    ast.Lt: "<",
    ast.LtE: "<=",
    ast.Gt: ">",
    ast.GtE: ">=",
    ast.In: "in",
    ast.NotIn: "not in",
    ast.Is: "is",
    ast.IsNot: "is not",
}


def _skipped_constants(tree):
    """Constants that are docstrings, f-string parts, or handled elsewhere."""
    skip = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                skip.add(id(body[0].value))
        elif isinstance(node, ast.JoinedStr):
            skip.update(id(v) for v in ast.walk(node) if isinstance(v, ast.Constant))
        elif isinstance(node, ast.Return) and isinstance(node.value, ast.Constant):
            skip.add(id(node.value))
    return skip


def sites(tree):
    """Yield (node, op, label) for every mutation site in a stable order."""
    # Tuples used as dict keys or set members are identifiers, not collections.
    keys = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            keys.update(id(k) for k in node.keys if k is not None)
        elif isinstance(node, ast.Set):
            keys.update(id(e) for e in node.elts)
    skip = _skipped_constants(tree)
    docstring_exprs = {
        id(n.body[0])
        for n in ast.walk(tree)
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef))
        and n.body
        and isinstance(n.body[0], ast.Expr)
        and isinstance(n.body[0].value, ast.Constant)
    }
    for node in ast.walk(tree):
        if id(node) in keys and isinstance(node, ast.Tuple):
            continue
        if isinstance(node, ast.Compare):
            for i, op in enumerate(node.ops):
                if type(op) in COMPARE_SWAP:
                    new = COMPARE_SWAP[type(op)]
                    yield node, i, f"compare {SYMBOL[type(op)]} -> {SYMBOL[new]}"
        elif isinstance(node, ast.BoolOp):
            yield node, "boolop", "boolop and -> or" if isinstance(node.op, ast.And) else "boolop or -> and"
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            yield node, "not", "not removed"
        elif (
            isinstance(node, ast.Return)
            and isinstance(node.value, ast.Constant)
            and node.value.value in (0, 1)
            and not isinstance(node.value.value, bool)
        ):
            yield node, "return", f"return {node.value.value} -> {1 - node.value.value}"
        elif isinstance(node, ast.Constant) and isinstance(node.value, bool):
            yield node, "bool", f"{node.value} -> {not node.value}"
        elif isinstance(node, ast.Constant) and isinstance(node.value, int) and id(node) not in skip:
            yield node, "int", f"constant {node.value} -> {node.value + 1}"
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value and id(node) not in skip:
            yield node, "str-empty", f"string {node.value[:24]!r} -> ''"
            if node.value.startswith("^") and len(node.value) > 1:
                yield node, "regex-start", f"regex {node.value[:24]!r}: drop ^"
            if node.value.endswith("$") and len(node.value) > 1:
                yield node, "regex-end", f"regex {node.value[:24]!r}: drop $"
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and id(node) not in docstring_exprs:
            yield node, "delete", "statement deleted"
        elif (
            isinstance(node, (ast.List, ast.Set, ast.Tuple))
            and node.elts
            and isinstance(getattr(node, "ctx", ast.Load()), ast.Load)
        ):
            yield node, "empty", f"{type(node).__name__.lower()} literal -> empty"
        elif isinstance(node, ast.Dict) and node.keys:
            yield node, "empty", "dict literal -> empty"
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            yield node, "empty", f"{type(node).__name__} -> empty"


def apply(node, op):
    """Mutate `node` in place (or return a replacement node)."""
    if isinstance(node, ast.Compare):
        node.ops[op] = COMPARE_SWAP[type(node.ops[op])]()
        return node
    if op == "boolop":
        node.op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
        return node
    if op == "not":
        return node.operand
    if op == "return":
        node.value = ast.Constant(1 - node.value.value)
        return node
    if op == "bool":
        return ast.Constant(not node.value)
    if op == "int":
        return ast.Constant(node.value + 1)
    if op == "str-empty":
        return ast.Constant("")
    if op == "regex-start":
        return ast.Constant(node.value[1:])
    if op == "regex-end":
        return ast.Constant(node.value[:-1])
    if op == "delete":
        return ast.Pass()
    if isinstance(node, (ast.List, ast.ListComp)):
        return ast.List(elts=[], ctx=ast.Load())
    if isinstance(node, (ast.Set, ast.SetComp)):
        return ast.Call(func=ast.Name(id="set", ctx=ast.Load()), args=[], keywords=[])
    if isinstance(node, (ast.Dict, ast.DictComp)):
        return ast.Dict(keys=[], values=[])
    return ast.Tuple(elts=[], ctx=ast.Load())


class Replace(ast.NodeTransformer):
    def __init__(self, target, replacement):
        self.target, self.replacement = target, replacement

    def generic_visit(self, node):
        for field, old in ast.iter_fields(node):
            if isinstance(old, list):
                for i, item in enumerate(old):
                    if item is self.target:
                        old[i] = self.replacement
                    elif isinstance(item, ast.AST):
                        self.generic_visit(item)
            elif old is self.target:
                setattr(node, field, self.replacement)
            elif isinstance(old, ast.AST):
                self.generic_visit(old)
        return node


def enumerate_mutants(source):
    tree = ast.parse(source)
    return [(node.lineno, label) for node, _, label in sites(tree)]


def build_mutant(source, k):
    tree = ast.parse(source)
    for n, (node, index, _) in enumerate(sites(tree)):
        if n == k:
            replacement = apply(node, index)
            if replacement is not node:
                Replace(node, replacement).visit(tree)
            return ast.unparse(ast.fix_missing_locations(tree))
    raise IndexError(k)


def run_suite(repo, tests, timeout, failfast):
    cmd = (
        [sys.executable, "-m", "unittest", "-q"] + (["-f"] if failfast else []) + tests
    )
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        result = subprocess.run(
            cmd, cwd=repo, capture_output=True, text=True, timeout=timeout, env=env
        )
    except subprocess.TimeoutExpired:
        return "timeout"
    return "passed" if result.returncode == 0 else "failed"


# Surviving mutants reviewed as equivalent: (source line, label) -> reason.
EQUIVALENT = {
    (
        'PORTFOLIO_MIRRORED = ("parent_id", "level", "actor_id", "state", "status")',
        "string 'level' -> ''",
    ): "level is fixed by the journey_id prefix in both registers, so a level mismatch is already reported by the prefix/level rule",
    (
        'spec = importlib.util.spec_from_file_location("sync_conventions", script)',
        "string 'sync_conventions' -> ''",
    ): "the module name is only a label for the imported generator",
    (
        '"--root", type=Path, default=DEFAULT_ROOT, help="repository root to validate"',
        "string 'repository root to valid' -> ''",
    ): "help text only",
    (
        "parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])",
        "constant 0 -> 1",
    ): "help text only",
    (
        'target = raw.split("#", 1)[0].split("?", 1)[0]',
        "constant 1 -> 2",
    ): "maxsplit 1 or 2 yields the same first element",
    (
        'if target.split("/", 1)[0] in REPO_FOLDERS or target.split("/", 1)[0] in skill_names:',
        "constant 1 -> 2",
    ): "maxsplit 1 or 2 yields the same first element",
    (
        'if not nid.startswith(prefix + "-"):',
        "string '-' -> ''",
    ): "slug tokens start with a letter, so a grammatical node ID that starts with the journey key always continues with '-'",
    (
        "1 for s in stages if any(m == s or m.startswith(s + \"-\") for m in measured)",
        "string '-' -> ''",
    ): "node segments are exactly two digits, so no valid ID extends a stage ID without a '-'",
}


def write_report(path, args, mutants, selected, survived, lines, score):
    counts = {}
    for k in selected:
        op = mutants[k][1].split()[0]
        counts.setdefault(op, [0, 0])
        counts[op][0] += 1
        counts[op][1] += k in survived
    out = [
        "# Mutation report",
        "",
        f"Target: `{args.target}`. Tests: {', '.join(f'`{t}`' for t in args.tests)}. "
        f"Generated by `scripts/mutation_test.py` (`make mutation`); local only, not run in CI.",
        "",
        f"**Mutation score: {score:.1f}%** ({len(selected) - len(survived)} of {len(selected)} mutants killed, "
        f"{len(survived)} survived; threshold {args.threshold:.0f}%).",
        "",
        "A mutant is killed when the test suite fails or times out on it.",
        "",
        "## Operators",
        "",
        "| Operator | Mutants | Survived |",
        "|---|---|---|",
    ]
    out += [f"| {op} | {n} | {s} |" for op, (n, s) in sorted(counts.items())]
    out += ["", "## Surviving mutants", ""]
    if not survived:
        out.append("None.")
    for k in survived:
        line, label = mutants[k]
        reason = EQUIVALENT.get((lines[line - 1].strip(), label), "not yet reviewed")
        out.append(f"- #{k}, line {line}, {label}: `{lines[line - 1].strip()}` — {reason}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Mutation testing for the repository validator."
    )
    parser.add_argument(
        "--target",
        default=DEFAULT_TARGET,
        help="file to mutate, relative to the repo root",
    )
    parser.add_argument(
        "--tests", nargs="+", default=DEFAULT_TESTS, help="unittest modules to run"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=90.0,
        help="minimum mutation score in percent",
    )
    parser.add_argument(
        "--timeout", type=float, default=120.0, help="seconds per mutant run"
    )
    parser.add_argument(
        "--jobs", type=int, default=min(4, os.cpu_count() or 1), help="parallel workers"
    )
    parser.add_argument(
        "--limit", type=int, default=0, help="only run the first N mutants (sizing)"
    )
    parser.add_argument("--list", action="store_true", help="list mutants and exit")
    parser.add_argument("--only", default="", help="comma-separated mutant numbers to run")
    parser.add_argument("--report", default="", help="write a Markdown report to this path")
    args = parser.parse_args(argv)

    source = (ROOT / args.target).read_text(encoding="utf-8")
    lines = source.splitlines()
    mutants = enumerate_mutants(source)
    if args.list:
        for k, (line, label) in enumerate(mutants):
            print(f"#{k:<4} line {line:<5} {label:<32} {lines[line - 1].strip()}")
        print(f"{len(mutants)} mutants")
        return 0
    selected = list(range(len(mutants)))[: args.limit or None]
    if args.only:
        selected = [int(k) for k in args.only.split(",")]

    with tempfile.TemporaryDirectory() as tmp:
        slots = queue.Queue()
        for j in range(max(1, args.jobs)):
            copy = Path(tmp) / f"repo{j}"
            shutil.copytree(
                ROOT,
                copy,
                ignore=shutil.ignore_patterns(".git", "__pycache__", ".agents"),
            )
            slots.put(copy)

        baseline_repo = slots.get()
        (baseline_repo / args.target).write_text(
            ast.unparse(ast.parse(source)), encoding="utf-8"
        )
        started = time.time()
        if (
            run_suite(baseline_repo, args.tests, args.timeout, failfast=False)
            != "passed"
        ):
            print(
                "Baseline suite fails on the unmutated (round-tripped) target; fix tests first."
            )
            return 2
        baseline = time.time() - started
        slots.put(baseline_repo)
        print(
            f"{len(selected)} of {len(mutants)} mutants, {args.jobs} jobs, baseline suite {baseline:.1f}s"
        )

        def run(k):
            repo = slots.get()
            try:
                (repo / args.target).write_text(
                    build_mutant(source, k), encoding="utf-8"
                )
                return k, run_suite(repo, args.tests, args.timeout, failfast=True)
            finally:
                slots.put(repo)

        results = {}
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
            for done, (k, outcome) in enumerate(pool.map(run, selected), start=1):
                results[k] = outcome
                if done % 25 == 0:
                    print(f"  {done}/{len(selected)} done", flush=True)

    survived = [k for k in selected if results[k] == "passed"]
    killed = len(selected) - len(survived)
    score = 100.0 * killed / len(selected) if selected else 100.0
    print(
        f"killed {killed}, survived {len(survived)}, total {len(selected)}; mutation score {score:.1f}%"
    )
    for k in survived:
        line, label = mutants[k]
        reason = EQUIVALENT.get((lines[line - 1].strip(), label), "")
        print(f"  SURVIVED #{k} line {line}: {label}: {lines[line - 1].strip()}" + (f"  [equivalent: {reason}]" if reason else ""))
    if args.report:
        write_report(ROOT / args.report, args, mutants, selected, survived, lines, score)
    if score < args.threshold:
        print(f"FAIL: score {score:.1f}% is below the threshold {args.threshold:.0f}%")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
