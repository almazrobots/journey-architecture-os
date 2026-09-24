#!/usr/bin/env python3
"""Deterministic stand-in for a model command, used by tests/test_evals.py.

Reads a prompt on stdin and prints a canned answer chosen from the prompt content:

* routing prompt (contains <available_skills>): answers {"skill": X} where X comes from an
  ``[[answer:X]]`` marker in the request, else "none". A request containing
  ``[[malformed-first]]`` gets a non-JSON answer on the first call (state kept in
  $FAKE_AGENT_STATE) to exercise retries.
* judge prompt (contains "impartial evaluator"): fails if the graded response still contains a raw
  ontology ID (method judges must see normalized text), else passes when it contains the token
  EVIDENCE-DISCIPLINE.
* generation prompt: a skill-loaded prompt (contains <skill name=) gets a response that
  follows the conventions; the baseline prompt gets one that does not, except that input
  containing ``[[flaky-baseline]]`` alternates between passing and failing the judge.
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

prompt = sys.stdin.read()

if "<available_skills>" in prompt:
    request = re.search(r"<request>\n(.*?)\n</request>", prompt, re.S).group(1)
    if "[[malformed-first]]" in request:
        state = Path(os.environ["FAKE_AGENT_STATE"]) / hashlib.sha1(request.encode()).hexdigest()
        if not state.exists():
            state.write_text("seen")
            print("Sure! I think the best skill is probably the mapping one.")
            sys.exit(0)
    m = re.search(r"\[\[answer:([a-z-]+)\]\]", request)
    print("```json\n" + json.dumps({"skill": m.group(1) if m else "none"}) + "\n```")
elif "impartial evaluator" in prompt:
    response = re.search(r"<response>\n(.*?)\n</response>", prompt, re.S).group(1)
    if re.search(r"\b(?:EVD|MTM|MET|OPP|NOD|JRN)-[0-9A-Z]", response) and "[[convention-judge]]" not in prompt:
        # a method judge must never see raw ontology IDs (they reveal the condition)
        print(json.dumps({"pass": False, "reason": "saw a raw ontology ID"}))
    else:
        passed = "EVIDENCE-DISCIPLINE" in response
        print(json.dumps({"pass": passed, "reason": "token present" if passed else "token absent"}))
elif "<skill name=" in prompt:
    print("| id | status |\n|---|---|\n| EVD-2026-0001 | observed |\n| EVD-2026-0002 | inferred |\n"
          "The VP claim is a hypothesis; refund timing is unknown. EVIDENCE-DISCIPLINE")
elif "[[flaky-baseline]]" in prompt:
    # passes the judge on the 1st, 3rd, ... call for the same prompt
    state = Path(os.environ["FAKE_AGENT_STATE"]) / ("flaky-" + hashlib.sha1(prompt.encode()).hexdigest())
    count = int(state.read_text()) + 1 if state.exists() else 1
    state.write_text(str(count))
    print("Plain answer." + (" EVIDENCE-DISCIPLINE" if count % 2 else ""))
else:
    print("Customers love it. See EVD-26-1.")
