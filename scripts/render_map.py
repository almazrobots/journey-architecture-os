#!/usr/bin/env python3
"""Render a Journey Architecture OS journey system as one self-contained HTML map.

Usage:
    python3 scripts/render_map.py <journey-system-dir> -o map.html [--lang en|ru] [--title TEXT]

Input is only the CSV registers defined in
skills/journey-architecture/references/ontology.md. Markdown views are never read.
The experience register is optional; without it, posters show what the other
registers hold and say what is missing.

Output is deterministic: the same registers give the same bytes. The page makes
no network requests: fonts are embedded from scripts/render_assets/fonts/, the
diagrams are inline SVG, the script is inline. Every text value from a register
is HTML-escaped; the JSON data block escapes <, > and & as \\u escapes.

Standard library only; Python 3.9 or newer.
"""

import argparse
import base64
import csv
import html
import json
import re
import sys
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "render_assets"
STATUSES = ("observed", "inferred", "hypothesis", "unknown")
STATE_ORDER = ("current", "transitional", "target")
FILES = {
    "actor": "actor-register.csv",
    "journey": "journey-registry.csv",
    "relation": "relation-register.csv",
    "node": "node-register.csv",
    "evidence": "evidence-register.csv",
    "moment": "moment-register.csv",
    "metric": "metric-register.csv",
    "edge": "metric-edge-register.csv",
    "opportunity": "opportunity-register.csv",
    "initiative": "initiative-register.csv",
    "portfolio": "portfolio-register.csv",
    "governance": "governance-register.csv",
    "change": "change-log.csv",
    "experience": "experience-register.csv",
}
# Poster bands fed by the experience register: (band key, row types shown in it)
EXP_BANDS = (
    ("action", ("action",)),
    ("touch", ("touchpoint", "channel")),
    ("expectation", ("expectation",)),
    ("thought", ("thought",)),
    ("pain", ("pain",)),
    ("workaround", ("workaround",)),
    ("emotion", ("emotion",)),
    ("question", ("question",)),
)

T = {
    "en": {
        "lang": "en",
        "status": {
            "observed": "observed",
            "inferred": "inferred",
            "hypothesis": "hypothesis",
            "unknown": "unknown",
        },
        "status_hint": {
            "observed": "directly supported by a cited source or measurement",
            "inferred": "reasoned from observed evidence",
            "hypothesis": "plausible, not yet validated",
            "unknown": "no adequate evidence: an open question",
        },
        "state": {
            "current": "current",
            "target": "target",
            "transitional": "transitional",
        },
        "band": {
            "action": "Actions",
            "touch": "Touchpoints & channels",
            "expectation": "Expectations",
            "thought": "Thoughts",
            "pain": "Pains",
            "workaround": "Workarounds",
            "emotion": "Emotions",
            "question": "Questions",
            "moment": "Moments that matter",
            "metric": "Metrics",
            "opportunity": "Opportunities",
        },
        "rowtype": {"touchpoint": "touchpoint", "channel": "channel"},
        "decision": {
            "act-now": "act now",
            "investigate": "investigate",
            "sequence": "sequence",
            "monitor": "monitor",
            "deprioritize": "deprioritize",
        },
        "moment_type": {},
        "default_title": "Journey system",
        "overview": "The system",
        "journeys": "Journeys",
        "meter_h": "What the map stands on",
        "meter_ev": "Evidence rows",
        "meter_claims": "Claims in the map",
        "meter_claims_note": "Nodes, relations, moments, metrics, metric edges, opportunities (problem and root cause) and experience rows, each with its own status.",
        "meter_ev_note": "Registered findings and registered gaps. An unknown row is an open question, not a finding.",
        "all": "Whole system",
        "other": "Other levels and journeys",
        "rows": "rows",
        "claims": "claims",
        "stages": "stages",
        "no_stages": "not mapped into stages",
        "poster": "Journey map",
        "trigger": "Trigger",
        "start": "Starts",
        "end": "Ends",
        "outcome": "Desired outcome",
        "baseline": "Changes the current journey",
        "versions": "Target and transitional versions",
        "root": "Root metric",
        "no_root": "No actor-outcome metric attached",
        "stage": "Stage",
        "episode": "Episode",
        "goal": "Actor goal",
        "not_measured": "not measured",
        "no_emotion_rows": "No emotion rows: the curve is not drawn.",
        "curve_note": "Solid line only between two observed points; dashed where either point is inferred or a hypothesis. A gap means the stage was not measured; the line is never carried across it.",
        "none_band": "none registered",
        "missing_exp": "This journey system has no experience-register.csv. Actions, touchpoints, expectations, thoughts, pains, workarounds, emotions and questions are not shown; the emotion row stays empty on purpose.",
        "missing_exp_j": "The experience register has no rows for this journey. Actions, touchpoints, expectations, thoughts, pains, workarounds, emotions and questions are not shown.",
        "journey_wide": "Whole journey",
        "service_h": "Service system",
        "service_note": "One lane per actor. Cards are stages; columns line stages up so that a stage sits at or after what it depends on. Arrow line style follows the relation's status.",
        "lane_empty": "stages not mapped",
        "unknown_h": "What we don't know",
        "unknown_note": "Evidence rows registered as unknown. Each is an open question; the items under it depend on the answer.",
        "no_unknowns": "No evidence row is registered as unknown.",
        "depends_on_answer": "Depends on the answer",
        "legend": "How to read",
        "moment_leg": "Moment that matters",
        "root_leg": "Root metric (actor outcome)",
        "details": "Details",
        "close": "Close",
        "back": "Back",
        "finding": "Finding",
        "source": "Source",
        "sample": "Population or sample",
        "limits": "Limitations",
        "collected": "Collected",
        "definition": "Definition",
        "base": "Baseline",
        "target_v": "Target",
        "owner": "Owner",
        "layer": "Layer",
        "evidence": "Evidence",
        "problem": "Problem",
        "root_cause": "Root cause",
        "decision_l": "Decision",
        "hover_hint": "Enter or click for details",
        "relations": "Relations",
        "rel": {
            "precedes": "precedes",
            "can_follow": "can follow",
            "branches_to": "branches to",
            "depends_on": "depends on",
            "shares_touchpoint_with": "shares a touchpoint with",
            "shares_capability_with": "shares a capability with",
            "enables": "enables",
        },
        "rel_in": {
            "precedes": "preceded by",
            "can_follow": "can come after",
            "branches_to": "branched from",
            "depends_on": "needed by",
            "shares_touchpoint_with": "shares a touchpoint with",
            "shares_capability_with": "shares a capability with",
            "enables": "enabled by",
        },
        "generated": "Rendered from the CSV registers by scripts/render_map.py. Fonts: Onest, Literata, JetBrains Mono (SIL Open Font License 1.1).",
        "skip": "Skip to journeys",
        "actor": "Actor",
        "episodes": "Episodes",
        "ev_n": "evidence",
        "in_view_from": "from",
    },
    "ru": {
        "lang": "ru",
        "status": {
            "observed": "наблюдено",
            "inferred": "выведено",
            "hypothesis": "гипотеза",
            "unknown": "неизвестно",
        },
        "status_hint": {
            "observed": "прямо подтверждено источником или замером",
            "inferred": "выведено из наблюдённых свидетельств",
            "hypothesis": "правдоподобно, ещё не проверено",
            "unknown": "свидетельств нет: открытый вопрос",
        },
        "state": {
            "current": "текущее",
            "target": "целевое",
            "transitional": "переходное",
        },
        "band": {
            "action": "Действия",
            "touch": "Точки контакта и каналы",
            "expectation": "Ожидания",
            "thought": "Мысли",
            "pain": "Боли",
            "workaround": "Обходные пути",
            "emotion": "Эмоции",
            "question": "Вопросы",
            "moment": "Моменты, которые решают",
            "metric": "Метрики",
            "opportunity": "Возможности",
        },
        "rowtype": {"touchpoint": "точка контакта", "channel": "канал"},
        "decision": {
            "act-now": "делать сейчас",
            "investigate": "исследовать",
            "sequence": "в очередь",
            "monitor": "наблюдать",
            "deprioritize": "отложить",
        },
        "moment_type": {
            "decision": "решение",
            "trust": "доверие",
            "transition": "переход",
            "recovery": "восстановление",
            "capability": "способность",
            "relationship": "отношения",
            "high-risk": "высокий риск",
        },
        "default_title": "Система путей",
        "overview": "Система",
        "journeys": "Пути",
        "meter_h": "На чём держится карта",
        "meter_ev": "Строки свидетельств",
        "meter_claims": "Утверждения карты",
        "meter_claims_note": "Узлы, связи, моменты, метрики, связи метрик, возможности (проблема и корневая причина) и строки опыта — у каждого свой статус.",
        "meter_ev_note": "Зарегистрированные находки и пробелы. Строка unknown — открытый вопрос, а не находка.",
        "all": "Вся система",
        "other": "Прочие уровни и пути",
        "rows": "строк",
        "claims": "утв.",
        "stages": "стадий",
        "no_stages": "стадии не смоделированы",
        "poster": "Карта пути",
        "trigger": "Триггер",
        "start": "Начало",
        "end": "Конец",
        "outcome": "Желаемый результат",
        "baseline": "Меняет текущий путь",
        "versions": "Целевые и переходные версии",
        "root": "Корневая метрика",
        "no_root": "Метрики результата актора нет",
        "stage": "Стадия",
        "episode": "Эпизод",
        "goal": "Цель актора",
        "not_measured": "не измерено",
        "no_emotion_rows": "Строк эмоций нет: кривая не строится.",
        "curve_note": "Сплошная линия — только между двумя наблюдёнными точками; пунктир — если хотя бы одна точка выведена или гипотеза. Разрыв — стадия не измерена; линия через него не проводится.",
        "none_band": "не зарегистрировано",
        "missing_exp": "В системе нет experience-register.csv. Действия, точки контакта, ожидания, мысли, боли, обходные пути, эмоции и вопросы не показаны; строка эмоций пуста намеренно.",
        "missing_exp_j": "В реестре опыта нет строк по этому пути. Действия, точки контакта, ожидания, мысли, боли, обходные пути, эмоции и вопросы не показаны.",
        "journey_wide": "Весь путь",
        "service_h": "Сервисная система",
        "service_note": "Одна дорожка на актора. Карточки — стадии; столбцы выстроены так, что стадия стоит не раньше того, от чего зависит. Стиль стрелки повторяет статус связи.",
        "lane_empty": "стадии не смоделированы",
        "unknown_h": "Чего мы не знаем",
        "unknown_note": "Строки свидетельств со статусом unknown. Каждая — открытый вопрос; под ним то, что зависит от ответа.",
        "no_unknowns": "Ни одна строка свидетельств не отмечена как unknown.",
        "depends_on_answer": "От ответа зависят",
        "legend": "Как читать",
        "moment_leg": "Момент, который решает",
        "root_leg": "Корневая метрика (результат актора)",
        "details": "Подробнее",
        "close": "Закрыть",
        "back": "Назад",
        "finding": "Находка",
        "source": "Источник",
        "sample": "Популяция или выборка",
        "limits": "Ограничения",
        "collected": "Собрано",
        "definition": "Определение",
        "base": "База",
        "target_v": "Цель",
        "owner": "Владелец",
        "layer": "Слой",
        "evidence": "Свидетельства",
        "problem": "Проблема",
        "root_cause": "Корневая причина",
        "decision_l": "Решение",
        "hover_hint": "Enter или клик — подробнее",
        "relations": "Связи",
        "rel": {
            "precedes": "идёт перед",
            "can_follow": "может идти после",
            "branches_to": "ветвится в",
            "depends_on": "зависит от",
            "shares_touchpoint_with": "общая точка контакта с",
            "shares_capability_with": "общая способность с",
            "enables": "делает возможным",
        },
        "rel_in": {
            "precedes": "после",
            "can_follow": "может идти перед",
            "branches_to": "ветвь от",
            "depends_on": "нужен для",
            "shares_touchpoint_with": "общая точка контакта с",
            "shares_capability_with": "общая способность с",
            "enables": "возможен благодаря",
        },
        "generated": "Собрано из CSV-реестров скриптом scripts/render_map.py. Шрифты: Onest, Literata, JetBrains Mono (SIL Open Font License 1.1).",
        "skip": "К путям",
        "actor": "Актор",
        "episodes": "Эпизоды",
        "ev_n": "свид.",
        "in_view_from": "из",
    },
}


class InputError(Exception):
    pass


# ---------------------------------------------------------------- helpers
def esc(s):
    return html.escape(s or "", quote=True)


def ids(s):
    return [x.strip() for x in (s or "").split(";") if x.strip()]


def anchor(prefix, x):
    return prefix + "-" + re.sub(r"[^A-Za-z0-9_-]", "_", x or "")


def load(root, key):
    path = root / FILES[key]
    if not path.exists():
        return None
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return [
            {k: (v or "") for k, v in row.items() if k is not None}
            for row in csv.DictReader(fh)
        ]


def seq_key(n):
    try:
        return (int(n.get("sequence") or 0), n["node_id"])
    except ValueError:
        return (0, n["node_id"])


class System:
    def __init__(self, root, lang):
        self.root = root
        self.t = T[lang]
        data = {k: load(root, k) for k in FILES}
        if data["journey"] is None:
            raise InputError("%s: journey-registry.csv not found" % root)
        self.has_experience = data["experience"] is not None
        for k in data:
            data[k] = data[k] or []
        self.d = data
        self.actors = OrderedDict((r["actor_id"], r) for r in data["actor"])
        self.journeys = OrderedDict((r["journey_id"], r) for r in data["journey"])
        self.nodes = OrderedDict((r["node_id"], r) for r in data["node"])
        self.evidence = OrderedDict((r["evidence_id"], r) for r in data["evidence"])
        self.metrics = OrderedDict((r["metric_id"], r) for r in data["metric"])
        self.check()
        self.children = defaultdict(list)
        for n in self.nodes.values():
            if n["parent_node_id"]:
                self.children[n["parent_node_id"]].append(n)
        for k in self.children:
            self.children[k].sort(key=seq_key)
        self.moments_by_node = defaultdict(list)
        for m in data["moment"]:
            self.moments_by_node[m["node_id"]].append(m)
        self.metrics_by_owner = defaultdict(list)
        for m in self.metrics.values():
            self.metrics_by_owner[m["journey_or_node_id"]].append(m)
        self.exp_by_node = defaultdict(list)
        for x in data["experience"]:
            self.exp_by_node[x["node_id"]].append(x)
        self.opps_by_journey = defaultdict(list)
        for o in data["opportunity"]:
            self.opps_by_journey[o["journey_id"]].append(o)

    def check(self):
        bad = []
        cols = {
            "relation": ("evidence_status",),
            "node": ("evidence_status",),
            "evidence": ("evidence_status",),
            "moment": ("evidence_status",),
            "metric": ("evidence_status",),
            "edge": ("evidence_status",),
            "opportunity": ("evidence_status", "root_cause_status"),
            "experience": ("evidence_status",),
        }
        for key, cs in cols.items():
            for i, r in enumerate(self.d[key], start=2):
                for c in cs:
                    if r.get(c, "") not in STATUSES:
                        bad.append(
                            "%s line %d: %s=%r" % (FILES[key], i, c, r.get(c, ""))
                        )
        for i, r in enumerate(self.d["experience"], start=2):
            v = r.get("valence", "")
            if r.get("row_type") == "emotion":
                if not re.fullmatch(r"-?[0-2]", v or ""):
                    bad.append(
                        "%s line %d: emotion row needs valence -2..2, got %r"
                        % (FILES["experience"], i, v)
                    )
        if bad:
            raise InputError("invalid values:\n  " + "\n  ".join(bad))

    # --- structure
    def stage_of(self, nid):
        n = self.nodes.get(nid)
        seen = 0
        while (
            n
            and n["parent_node_id"]
            and n["parent_node_id"] in self.nodes
            and seen < 20
        ):
            n = self.nodes[n["parent_node_id"]]
            seen += 1
        return n["node_id"] if n else None

    def stages(self, jid):
        return sorted(
            (
                n
                for n in self.nodes.values()
                if n["journey_id"] == jid and not n["parent_node_id"]
            ),
            key=seq_key,
        )

    def subtree(self, nid):
        out = [nid]
        for c in self.children.get(nid, []):
            out.extend(self.subtree(c["node_id"]))
        return out

    def journey_of(self, x):
        if x in self.nodes:
            return self.nodes[x]["journey_id"]
        if x in self.journeys:
            return x
        if x in self.metrics:
            return self.journey_of(self.metrics[x]["journey_or_node_id"])
        return ""

    def l2(self):
        return [j for j in self.journeys.values() if j["level"] == "L2"]

    def root_metric(self, jid):
        for m in self.metrics_by_owner.get(jid, []):
            if m["layer"] == "actor-outcome":
                return m
        return None


# ---------------------------------------------------------------- page pieces
class Renderer:
    def __init__(self, sysm, title):
        self.s = sysm
        self.t = sysm.t
        self.title = title
        self.details = OrderedDict()

    # --- atoms
    def sw(self, st):
        return '<i class="sw sw-%s" aria-hidden="true"></i>' % st

    def badge(self, st, small=False):
        return '<span class="st st-%s%s" title="%s">%s%s</span>' % (
            st,
            " sm" if small else "",
            esc(self.t["status_hint"][st]),
            self.sw(st),
            esc(self.t["status"][st]),
        )

    def ev_chip(self, eid):
        e = self.s.evidence.get(eid)
        if not e:
            return '<code class="id">%s</code>' % esc(eid)
        st = e["evidence_status"]
        short = eid.split("-", 1)[1] if "-" in eid else eid
        return (
            '<button type="button" class="chip ev" data-ev="%s" aria-haspopup="dialog">%s%s'
            '<span class="vh"> %s, %s</span></button>'
            % (esc(eid), self.sw(st), esc(short), esc(eid), esc(self.t["status"][st]))
        )

    def ev_chips(self, s):
        lst = ids(s)
        if not lst:
            return ""
        return '<span class="chips">%s</span>' % "".join(self.ev_chip(e) for e in lst)

    def met_chip(self, mid, named=False):
        m = self.s.metrics.get(mid)
        if not m:
            return '<code class="id">%s</code>' % esc(mid)
        root = m["layer"] == "actor-outcome"
        return (
            '<button type="button" class="chip met%s" data-met="%s" aria-haspopup="dialog">%s%s</button>'
            % (
                " root" if root else "",
                esc(mid),
                esc(mid),
                (" · " + esc(m["name"])) if named else "",
            )
        )

    def node_link(self, nid, text=None):
        n = self.s.nodes.get(nid)
        label = text or (n["name"] if n else nid)
        return '<a href="#%s">%s</a>' % (anchor("p", nid), esc(label))

    def detail(self, key, body):
        self.details[key] = body
        return key

    def jname(self, jid):
        j = self.s.journeys.get(jid)
        return j["name"] if j else jid

    def state_label(self, st):
        return self.t["state"].get(st, st)

    # --- meters
    def counts(self):
        s = self.s
        ev = defaultdict(Counter)
        cl = defaultdict(Counter)
        for e in s.evidence.values():
            ev[
                e["journey_id"]
                if e["journey_id"] in s.journeys
                and s.journeys[e["journey_id"]]["level"] == "L2"
                else "_other"
            ][e["evidence_status"]] += 1

        def add(j, st):
            key = j if j in s.journeys and s.journeys[j]["level"] == "L2" else "_other"
            cl[key][st] += 1

        for n in s.nodes.values():
            add(n["journey_id"], n["evidence_status"])
        for r in s.d["relation"]:
            add(s.journey_of(r["from_id"]), r["evidence_status"])
        for m in s.d["moment"]:
            add(s.journey_of(m["node_id"]), m["evidence_status"])
        for m in s.metrics.values():
            add(s.journey_of(m["journey_or_node_id"]), m["evidence_status"])
        for e in s.d["edge"]:
            add(s.journey_of(e["from_metric_id"]), e["evidence_status"])
        for o in s.d["opportunity"]:
            add(o["journey_id"], o["evidence_status"])
            add(o["journey_id"], o["root_cause_status"])
        for x in s.d["experience"]:
            add(s.journey_of(x["node_id"]), x["evidence_status"])
        return ev, cl

    def bar(self, label, sub, counter, unit):
        total = sum(counter.values())
        segs = "".join(
            '<span class="seg sw-%s" style="flex-grow:%d"></span>' % (st, counter[st])
            for st in STATUSES
            if counter[st]
        )
        nums = " · ".join(
            "%s %d" % (self.t["status"][st], counter[st]) for st in STATUSES
        )
        return (
            '<div class="mrow"><div class="mlab">%s<span>%s%d %s</span></div>'
            '<div class="bar" role="img" aria-label="%s">%s</div><div class="mnum">%s</div></div>'
            % (
                esc(label),
                (esc(sub) + " · ") if sub else "",
                total,
                esc(unit),
                esc(label + ": " + nums),
                segs or '<span class="seg empty"></span>',
                esc(nums),
            )
        )

    def meter(self):
        ev, cl = self.counts()
        keys = [
            j["journey_id"]
            for j in self.s.l2()
            if ev.get(j["journey_id"]) or cl.get(j["journey_id"])
        ]
        if ev.get("_other") or cl.get("_other"):
            keys.append("_other")
        tot_e, tot_c = Counter(), Counter()
        for c in ev.values():
            tot_e.update(c)
        for c in cl.values():
            tot_c.update(c)

        def label(k):
            if k == "_other":
                return self.t["other"], ""
            return self.jname(k), self.state_label(self.s.journeys[k]["state"])

        cols = []
        for title, note, data, tot, unit in (
            (self.t["meter_ev"], self.t["meter_ev_note"], ev, tot_e, self.t["rows"]),
            (
                self.t["meter_claims"],
                self.t["meter_claims_note"],
                cl,
                tot_c,
                self.t["claims"],
            ),
        ):
            rows = [self.bar(self.t["all"], "", tot, unit)]
            rows += [
                self.bar(*label(k), counter=data.get(k, Counter()), unit=unit)
                for k in keys
            ]
            cols.append(
                '<div class="mcol"><h3>%s</h3><p class="note">%s</p>%s</div>'
                % (esc(title), esc(note), "".join(rows))
            )
        return '<div class="meter">%s</div>' % "".join(cols)

    def legend(self):
        items = "".join(
            "<li>%s<span>%s</span></li>"
            % (self.badge(st), esc(self.t["status_hint"][st]))
            for st in STATUSES
        )
        items += (
            '<li><span class="dia" aria-hidden="true"></span><span>%s</span></li>'
            % esc(self.t["moment_leg"])
        )
        items += '<li><span class="chip met root">MET</span><span>%s</span></li>' % esc(
            self.t["root_leg"]
        )
        return '<div class="legend"><h3>%s</h3><ul>%s</ul></div>' % (
            esc(self.t["legend"]),
            items,
        )

    # --- overview
    def overview(self):
        s = self.s
        doms = [j for j in s.journeys.values() if j["level"] == "L0"]
        lede = doms[0]["desired_outcome"] if len(doms) == 1 else ""
        n_st = sum(1 for n in s.nodes.values() if not n["parent_node_id"])
        facts = [
            "%d %s" % (len(s.l2()), self.t["journeys"].lower()),
            "%d %s" % (n_st, self.t["stages"]),
            "%d %s" % (len(s.evidence), self.t["ev_n"]),
        ]
        out = ['<header class="hero" id="top">']
        out.append('<p class="kicker">Journey Architecture OS</p>')
        out.append("<h1>%s</h1>" % esc(self.title))
        if lede:
            out.append('<p class="lede">%s</p>' % esc(lede))
        out.append('<p class="facts">%s</p>' % " · ".join(esc(f) for f in facts))
        out.append("</header>")
        # journey index as hierarchy
        out.append(
            '<section class="block" aria-labelledby="h-idx"><h2 id="h-idx">%s</h2><ol class="tree">%s</ol></section>'
            % (esc(self.t["journeys"]), self.tree())
        )
        out.append(
            '<section class="block" aria-labelledby="h-meter"><h2 id="h-meter">%s</h2>%s%s</section>'
            % (esc(self.t["meter_h"]), self.meter(), self.legend())
        )
        return "".join(out)

    def tree(self):
        s = self.s
        kids = defaultdict(list)
        roots = []
        for j in s.journeys.values():
            p = j["parent_id"]
            if p and p in s.journeys:
                kids[p].append(j)
            else:
                roots.append(j)

        def item(j, depth):
            jid = j["journey_id"]
            n = len(s.stages(jid))
            meta = [j["level"], self.state_label(j["state"]), j["status"]]
            a = s.actors.get(j["actor_id"])
            if a:
                meta.append(a["name"])
            if j["level"] == "L2":
                meta.append(
                    ("%d %s" % (n, self.t["stages"])) if n else self.t["no_stages"]
                )
            name = esc(j["name"])
            if j["level"] == "L2" and n:
                name = '<a href="#%s">%s</a>' % (anchor("j", jid), name)
            sub = "".join(item(k, depth + 1) for k in kids.get(jid, []))
            return (
                '<li class="lv-%s"><span class="tn">%s</span><span class="tm"><code class="id">%s</code> %s</span>%s</li>'
                % (
                    esc(j["level"]),
                    name,
                    esc(jid),
                    esc(" · ".join(meta)),
                    ("<ol>%s</ol>" % sub) if sub else "",
                )
            )

        return "".join(item(j, 0) for j in roots)

    # --- poster
    def poster(self, j):
        s, t = self.s, self.t
        jid = j["journey_id"]
        stages = s.stages(jid)
        ncol = len(stages)
        actor = s.actors.get(j["actor_id"], {})
        out = [
            '<section class="poster" id="%s" aria-labelledby="%s">'
            % (anchor("j", jid), anchor("jt", jid))
        ]
        # header
        out.append('<div class="ph">')
        out.append(self.actor_card(actor))
        out.append('<div class="pj">')
        kick = [t["poster"], j["level"], self.state_label(j["state"]), j["status"]]
        if j.get("version"):
            kick.append("v" + j["version"])
        out.append(
            '<p class="kicker"><code class="id">%s</code> · %s</p>'
            % (esc(jid), esc(" · ".join(kick)))
        )
        out.append('<h2 id="%s">%s</h2>' % (anchor("jt", jid), esc(j["name"])))
        facts = []
        for lab, key in (
            (t["trigger"], "trigger"),
            (t["start"], "start_boundary"),
            (t["end"], "end_boundary"),
            (t["outcome"], "desired_outcome"),
        ):
            if j.get(key):
                facts.append(
                    "<div><dt>%s</dt><dd>%s</dd></div>" % (esc(lab), esc(j[key]))
                )
        out.append('<dl class="pfacts">%s</dl>' % "".join(facts))
        links = []
        if j.get("baseline_journey_id"):
            b = j["baseline_journey_id"]
            target = (
                ('<a href="#%s">%s</a>' % (anchor("j", b), esc(self.jname(b))))
                if s.stages(b)
                else esc(self.jname(b))
            )
            links.append('<p class="plink">%s: %s</p>' % (esc(t["baseline"]), target))
        vers = [v for v in s.l2() if v["baseline_journey_id"] == jid]
        if vers:
            links.append(
                '<p class="plink">%s: %s</p>'
                % (
                    esc(t["versions"]),
                    ", ".join(
                        (
                            '<a href="#%s">%s</a>'
                            % (anchor("j", v["journey_id"]), esc(v["name"]))
                        )
                        if s.stages(v["journey_id"])
                        else esc(v["name"])
                        for v in vers
                    ),
                )
            )
        root = s.root_metric(jid)
        if root:
            links.append(
                '<p class="plink">%s: %s %s</p>'
                % (esc(t["root"]), self.met_chip(root["metric_id"]), esc(root["name"]))
            )
        else:
            links.append('<p class="plink muted">%s</p>' % esc(t["no_root"]))
        out.append("".join(links))
        out.append("</div>")
        out.append(self.poster_meter(jid))
        out.append("</div>")
        # grid
        out.append(
            '<div class="pscroll" tabindex="0" role="region" aria-label="%s">'
            % esc(j["name"])
        )
        out.append('<div class="pgrid" style="--n:%d">' % ncol)
        out.append('<div class="rl rl-head"><span>%s</span></div>' % esc(t["stage"]))
        for st in stages:
            out.append(self.stage_head(st))
        exp_rows = [
            x
            for st in stages
            for nid in s.subtree(st["node_id"])
            for x in s.exp_by_node.get(nid, [])
        ]
        if not s.has_experience:
            out.append(
                '<div class="missing" style="grid-column:1/-1">%s</div>'
                % esc(t["missing_exp"])
            )
        elif not exp_rows:
            out.append(
                '<div class="missing" style="grid-column:1/-1">%s</div>'
                % esc(t["missing_exp_j"])
            )
        for band, types in EXP_BANDS:
            if band == "emotion":
                out.append(self.emotion_band(stages))
                continue
            if not exp_rows:
                continue
            out.append(self.exp_band(band, types, stages))
        out.append(self.moment_band(stages))
        out.append(self.metric_band(jid, stages))
        out.append(self.opp_band(jid, stages))
        out.append("</div></div></section>")
        return "".join(out)

    def actor_card(self, a):
        name = a.get("name") or "—"
        words = [w for w in re.split(r"[\s/:,()«»\"-]+", name) if w]
        mono = "".join(w[0] for w in words[:2]).upper() or "?"
        return (
            '<aside class="actor" aria-label="%s"><div class="mono" aria-hidden="true">%s</div>'
            '<div><p class="kicker">%s · %s</p><h3>%s</h3><p>%s</p><p class="muted">%s</p></div></aside>'
            % (
                esc(self.t["actor"]),
                esc(mono),
                esc(self.t["actor"]),
                esc(a.get("actor_type", "")),
                esc(name),
                esc(a.get("segment", "")),
                esc(a.get("context", "")),
            )
        )

    def poster_meter(self, jid):
        c = Counter()
        s = self.s
        for n in s.nodes.values():
            if n["journey_id"] == jid:
                c[n["evidence_status"]] += 1
        for nid in [n["node_id"] for n in s.nodes.values() if n["journey_id"] == jid]:
            for x in s.exp_by_node.get(nid, []):
                c[x["evidence_status"]] += 1
            for m in s.moments_by_node.get(nid, []):
                c[m["evidence_status"]] += 1
        segs = "".join(
            '<span class="seg sw-%s" style="flex-grow:%d"></span>' % (st, c[st])
            for st in STATUSES
            if c[st]
        )
        nums = "".join(
            "<li>%s<b>%d</b></li>" % (self.badge(st, True), c[st]) for st in STATUSES
        )
        return (
            '<div class="pmeter"><div class="bar tall" role="img" aria-label="%s">%s</div><ul>%s</ul></div>'
            % (
                esc(
                    " · ".join(
                        "%s %d" % (self.t["status"][st], c[st]) for st in STATUSES
                    )
                ),
                segs or '<span class="seg empty"></span>',
                nums,
            )
        )

    def stage_head(self, st):
        s, t = self.s, self.t
        nid = st["node_id"]
        out = [
            '<div class="sh b-%s" id="%s">' % (st["evidence_status"], anchor("p", nid))
        ]
        out.append(
            '<div class="sh-top"><span class="num">%s</span>%s</div>'
            % (esc(st["sequence"]), self.badge(st["evidence_status"]))
        )
        out.append("<h3>%s</h3>" % esc(st["name"]))
        if st["actor_goal"]:
            out.append(
                '<p class="goal"><span class="lbl">%s</span>%s</p>'
                % (esc(t["goal"]), esc(st["actor_goal"]))
            )
        out.append(self.ev_chips(st["evidence_ids"]))
        eps = s.children.get(nid, [])
        if eps:
            out.append('<ol class="eps" aria-label="%s">' % esc(t["episodes"]))
            for e in eps:
                out.append(
                    '<li id="%s" class="b-%s"><span class="en">%s.%s</span><div><b>%s</b>%s%s</div></li>'
                    % (
                        anchor("p", e["node_id"]),
                        e["evidence_status"],
                        esc(st["sequence"]),
                        esc(e["sequence"]),
                        esc(e["name"]),
                        self.badge(e["evidence_status"], True),
                        self.ev_chips(e["evidence_ids"]),
                    )
                )
            out.append("</ol>")
        out.append("</div>")
        return "".join(out)

    def band_label(self, band, extra=""):
        return '<div class="rl"><span>%s</span>%s</div>' % (
            esc(self.t["band"][band]),
            extra,
        )

    def where(self, st, nid):
        if nid == st["node_id"]:
            return ""
        n = self.s.nodes.get(nid)
        return '<span class="ep">↳ %s</span>' % esc(n["name"]) if n else ""

    def exp_band(self, band, types, stages):
        s = self.s
        out = [self.band_label(band)]
        any_row = False
        cells = []
        for st in stages:
            items = []
            for nid in s.subtree(st["node_id"]):
                for x in s.exp_by_node.get(nid, []):
                    if x["row_type"] in types:
                        items.append((nid, x))
            any_row = any_row or bool(items)
            h = ['<div class="cell">']
            for nid, x in items:
                kind = ""
                if band == "touch":
                    kind = '<span class="kind">%s</span>' % esc(
                        self.t["rowtype"].get(x["row_type"], x["row_type"])
                    )
                h.append(
                    '<div class="xi b-%s xi-%s">%s%s<p>%s</p><div class="xf">%s%s</div></div>'
                    % (
                        x["evidence_status"],
                        esc(band),
                        self.where(st, nid),
                        kind,
                        esc(x["text"]),
                        self.badge(x["evidence_status"], True),
                        self.ev_chips(x["evidence_ids"]),
                    )
                )
            h.append("</div>")
            cells.append("".join(h))
        if not any_row:
            return self.band_label(
                band
            ) + '<div class="cell none" style="grid-column:2/-1">%s</div>' % esc(
                self.t["none_band"]
            )
        return "".join(out + cells)

    def emotion_band(self, stages):
        s, t = self.s, self.t
        col, height, top, bot = 248, 170, 22, 22
        n = len(stages)
        width = col * n

        def y(v):
            return top + (2 - v) * (height - top - bot) / 4.0

        per_stage = []
        for st in stages:
            pts, notes = [], []
            for nid in s.subtree(st["node_id"]):
                for x in s.exp_by_node.get(nid, []):
                    if x["row_type"] != "emotion":
                        continue
                    notes.append((nid, x))
                    if x["evidence_status"] != "unknown":
                        pts.append((nid, x))
            per_stage.append((st, pts, notes))
        svg = [
            '<svg class="curve" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="%s">'
            % (width, height, width, height, esc(t["band"]["emotion"]))
        ]
        svg.append(
            '<defs><pattern id="hatch" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            '<rect width="4" height="4" class="c-bg"/><line x1="0" y1="0" x2="0" y2="4" class="c-inf-line"/></pattern></defs>'
        )
        for v in (2, 1, 0, -1, -2):
            svg.append(
                '<line x1="0" x2="%d" y1="%.1f" y2="%.1f" class="%s"/>'
                % (width, y(v), y(v), "c-zero" if v == 0 else "c-grid")
            )
            svg.append(
                '<text x="6" y="%.1f" class="c-ax">%s</text>'
                % (y(v) - 3, ("+%d" % v) if v > 0 else ("−%d" % -v if v < 0 else "0"))
            )
        coords = []  # per stage list of (x, y, status, text)
        for i, (st, pts, notes) in enumerate(per_stage):
            x0 = i * col
            if i:
                svg.append(
                    '<line x1="%d" x2="%d" y1="0" y2="%d" class="c-col"/>'
                    % (x0, x0, height)
                )
            cs = []
            for k, (nid, x) in enumerate(pts):
                cx = x0 + col * (k + 1) / (len(pts) + 1.0)
                cs.append((cx, y(int(x["valence"])), x["evidence_status"], x["text"]))
            coords.append(cs)
            if not cs:
                svg.append(
                    '<rect x="%d" y="%d" width="%d" height="%d" class="c-gap"/>'
                    % (x0 + 10, top, col - 20, height - top - bot)
                )
                svg.append(
                    '<text x="%d" y="%.1f" text-anchor="middle" class="c-gaptext">%s</text>'
                    % (x0 + col // 2, y(0) + 4, esc(t["not_measured"]))
                )
        segs = []
        for i, cs in enumerate(coords):
            chain = list(cs)
            if i + 1 < len(coords) and coords[i + 1] and cs:
                chain = chain + [coords[i + 1][0]]
            for a, b in zip(chain, chain[1:]):
                solid = a[2] == "observed" and b[2] == "observed"
                segs.append(
                    '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="%s"/>'
                    % (a[0], a[1], b[0], b[1], "c-solid" if solid else "c-dash")
                )
        svg.extend(segs)
        for cs in coords:
            for cx, cy, stt, txt in cs:
                svg.append(
                    '<circle cx="%.1f" cy="%.1f" r="7" class="c-pt c-%s"><title>%s</title></circle>'
                    % (cx, cy, stt, esc("%s · %s" % (t["status"][stt], txt)))
                )
        svg.append("</svg>")
        has_any = any(notes for _, _, notes in per_stage)
        lab = self.band_label(
            "emotion",
            '<p class="rl-note">%s</p>'
            % esc(t["curve_note"] if has_any else t["no_emotion_rows"]),
        )
        out = [
            lab,
            '<div class="cell curve-cell" style="grid-column:2/-1">%s</div>'
            % "".join(svg),
        ]
        out.append('<div class="rl rl-sub" aria-hidden="true"></div>')
        for st, pts, notes in per_stage:
            h = ['<div class="cell">']
            for nid, x in notes:
                val = x["valence"]
                h.append(
                    '<div class="xi b-%s xi-emotion">%s<p><b class="val">%s</b> %s</p><div class="xf">%s%s</div></div>'
                    % (
                        x["evidence_status"],
                        self.where(st, nid),
                        esc(
                            ("+" + val)
                            if val and not val.startswith("-") and val != "0"
                            else val.replace("-", "−")
                        ),
                        esc(x["text"]),
                        self.badge(x["evidence_status"], True),
                        self.ev_chips(x["evidence_ids"]),
                    )
                )
            if not notes:
                h.append('<p class="gapnote">%s</p>' % esc(t["not_measured"]))
            h.append("</div>")
            out.append("".join(h))
        return "".join(out)

    def moment_band(self, stages):
        s = self.s
        cells, anyrow = [], False
        for st in stages:
            h = ['<div class="cell">']
            for nid in s.subtree(st["node_id"]):
                for m in s.moments_by_node.get(nid, []):
                    anyrow = True
                    h.append(
                        '<div class="mt b-%s" id="%s"><span class="dia" aria-hidden="true"></span><div>%s'
                        '<p class="mt-h"><code class="id">%s</code> · %s</p><p>%s</p><div class="xf">%s%s%s</div></div></div>'
                        % (
                            m["evidence_status"],
                            anchor("m", m["moment_id"]),
                            self.where(st, nid),
                            esc(m["moment_id"]),
                            esc(
                                self.t["moment_type"].get(
                                    m["moment_type"], m["moment_type"]
                                )
                            ),
                            esc(m["outcome_at_stake"]),
                            self.badge(m["evidence_status"], True),
                            "".join(self.met_chip(x) for x in ids(m["metric_ids"])),
                            self.ev_chips(m["evidence_ids"]),
                        )
                    )
            h.append("</div>")
            cells.append("".join(h))
        if not anyrow:
            return self.band_label(
                "moment"
            ) + '<div class="cell none" style="grid-column:2/-1">%s</div>' % esc(
                self.t["none_band"]
            )
        return self.band_label("moment") + "".join(cells)

    def metric_band(self, jid, stages):
        s = self.s
        jw = [m for m in s.metrics_by_owner.get(jid, [])]
        extra = ""
        if jw:
            extra = '<div class="rl-chips">%s</div>' % "".join(
                self.met_chip(m["metric_id"]) for m in jw
            )
        cells, anyrow = [], bool(jw)
        for st in stages:
            h = ['<div class="cell">']
            for nid in s.subtree(st["node_id"]):
                for m in s.metrics_by_owner.get(nid, []):
                    anyrow = True
                    h.append(
                        '<div class="mi b-%s">%s%s<p>%s <span class="muted">· %s</span></p></div>'
                        % (
                            m["evidence_status"],
                            self.where(st, nid),
                            self.met_chip(m["metric_id"]),
                            esc(m["name"]),
                            esc(m["layer"]),
                        )
                    )
            h.append("</div>")
            cells.append("".join(h))
        if not anyrow:
            return self.band_label(
                "metric"
            ) + '<div class="cell none" style="grid-column:2/-1">%s</div>' % esc(
                self.t["none_band"]
            )
        return self.band_label("metric", extra) + "".join(cells)

    def opp_card(self, o, st=None):
        t = self.t
        where = self.where(st, o["node_id"]) if st and o["node_id"] else ""
        return (
            '<div class="op b-%s" id="%s">%s<div class="op-top"><code class="id">%s</code><span class="dec dec-%s">%s</span></div>'
            '<p class="op-o">%s</p><p><span class="lbl">%s</span>%s</p><p><span class="lbl">%s %s</span>%s</p>'
            '<div class="xf">%s%s</div></div>'
            % (
                o["evidence_status"],
                anchor("o", o["opportunity_id"]),
                where,
                esc(o["opportunity_id"]),
                esc(o["decision"]),
                esc(
                    t["decision"].get(o["decision"], o["decision"])
                    + (" · " + o["status"] if o.get("status") else "")
                ),
                esc(o["actor_outcome"]),
                esc(t["problem"]),
                esc(o["problem"]),
                esc(t["root_cause"]),
                self.badge(o["root_cause_status"], True),
                esc(o["root_cause"]),
                self.badge(o["evidence_status"], True),
                self.ev_chips(o["evidence_ids"]),
            )
        )

    def opp_band(self, jid, stages):
        s = self.s
        opps = s.opps_by_journey.get(jid, [])
        stage_ids = {st["node_id"] for st in stages}
        by_stage = defaultdict(list)
        wide = []
        for o in opps:
            stg = s.stage_of(o["node_id"]) if o["node_id"] else None
            (by_stage[stg].append(o) if stg in stage_ids else wide.append(o))
        if not opps:
            return self.band_label(
                "opportunity"
            ) + '<div class="cell none" style="grid-column:2/-1">%s</div>' % esc(
                self.t["none_band"]
            )
        out = [self.band_label("opportunity")]
        for st in stages:
            out.append(
                '<div class="cell">%s</div>'
                % "".join(self.opp_card(o, st) for o in by_stage.get(st["node_id"], []))
            )
        if wide:
            out.append(
                '<div class="rl rl-sub"><span>%s</span></div><div class="cell wide" style="grid-column:2/-1">%s</div>'
                % (esc(self.t["journey_wide"]), "".join(self.opp_card(o) for o in wide))
            )
        return "".join(out)

    # --- service view
    def service(self):
        s, t = self.s, self.t
        states = [st for st in STATE_ORDER if any(j["state"] == st for j in s.l2())]
        if not states:
            return ""
        views = []
        for st in states:
            views.append((st, self.service_state(st)))
        tabs = "".join(
            '<button type="button" role="tab" id="%s" aria-controls="%s" aria-selected="%s"%s>%s</button>'
            % (
                anchor("tab", st),
                anchor("sv", st),
                "true" if i == 0 else "false",
                "" if i == 0 else ' tabindex="-1"',
                esc(self.state_label(st)),
            )
            for i, (st, _) in enumerate(views)
        )
        panels = "".join(
            '<div class="sview%s" id="%s" role="tabpanel" aria-labelledby="%s">%s</div>'
            % (" on" if i == 0 else "", anchor("sv", st), anchor("tab", st), body)
            for i, (st, body) in enumerate(views)
        )
        return (
            '<section class="block" aria-labelledby="h-svc"><h2 id="h-svc">%s</h2><p class="note">%s</p>'
            '<div class="tabs" role="tablist" aria-label="%s">%s</div>%s</section>'
            % (
                esc(t["service_h"]),
                esc(t["service_note"]),
                esc(t["service_h"]),
                tabs,
                panels,
            )
        )

    def service_state(self, state):
        s, t = self.s, self.t
        base = [j["journey_id"] for j in s.l2() if j["state"] == state]
        inview = list(base)
        for r in s.d["relation"]:
            a, b = s.journey_of(r["from_id"]), s.journey_of(r["to_id"])
            for x, y in ((a, b), (b, a)):
                if (
                    x in base
                    and y
                    and y not in inview
                    and y in s.journeys
                    and s.journeys[y]["level"] == "L2"
                ):
                    inview.append(y)
        order = {jid: i for i, jid in enumerate(s.journeys)}
        inview.sort(key=lambda x: order.get(x, 0))
        # lanes by actor
        lanes = OrderedDict()
        actor_order = {a: i for i, a in enumerate(s.actors)}
        for jid in sorted(
            inview,
            key=lambda x: (
                actor_order.get(s.journeys[x]["actor_id"], 999),
                order.get(x, 0),
            ),
        ):
            lanes.setdefault(s.journeys[jid]["actor_id"], []).append(jid)
        # order journeys within a lane by precedes / can_follow
        for aid, js in lanes.items():
            before = defaultdict(set)
            for r in s.d["relation"]:
                a, b = r["from_id"], r["to_id"]
                if a in js and b in js:
                    if r["relation"] in ("precedes", "branches_to"):
                        before[b].add(a)
                    elif r["relation"] == "can_follow":
                        before[a].add(b)
            ordered, left = [], list(js)
            while left:
                pick = next(
                    (x for x in left if not (before[x] - set(ordered))), left[0]
                )
                ordered.append(pick)
                left.remove(pick)
            lanes[aid] = ordered
        # items and constraints
        items, lane_of, item_of_node = [], {}, {}
        for li, (aid, js) in enumerate(lanes.items()):
            for jid in js:
                sts = s.stages(jid)
                if sts:
                    for stn in sts:
                        key = stn["node_id"]
                        items.append(key)
                        lane_of[key] = li
                        for nid in s.subtree(key):
                            item_of_node[nid] = key
                else:
                    key = "J:" + jid
                    items.append(key)
                    lane_of[key] = li
        cons = []
        prev_by_lane = {}
        for it in items:
            li = lane_of[it]
            if li in prev_by_lane:
                cons.append((prev_by_lane[li], it, 1))
            prev_by_lane[li] = it
        wires = []
        for r in s.d["relation"]:
            a, b = item_of_node.get(r["from_id"]), item_of_node.get(r["to_id"])
            if not a or not b or a == b:
                continue
            same = lane_of[a] == lane_of[b]
            rel = r["relation"]
            if rel == "depends_on":
                cons.append((b, a, 0))
                wires.append({"a": b, "b": a, "s": r["evidence_status"], "r": rel})
            elif rel in ("precedes", "branches_to", "enables"):
                cons.append((a, b, 1 if same and rel != "enables" else 0))
                wires.append({"a": a, "b": b, "s": r["evidence_status"], "r": rel})
            elif rel == "can_follow":
                cons.append((b, a, 1 if same else 0))
                wires.append({"a": b, "b": a, "s": r["evidence_status"], "r": rel})
            else:
                if not same:
                    cons.append((a, b, 0))
                    cons.append((b, a, 0))
                wires.append(
                    {"a": a, "b": b, "s": r["evidence_status"], "r": rel, "u": 1}
                )
        col = {it: 0 for it in items}
        limit = len(items) + 1
        stable = False
        for _ in range(4 * len(items) + 4):
            changed = False
            for a, b, dlt in cons:
                if col[b] < col[a] + dlt and col[a] + dlt <= limit:
                    col[b] = col[a] + dlt
                    changed = True
            if not changed:
                stable = True
                break
        if not stable:  # cyclic constraints: fall back to lane order only
            col = {it: 0 for it in items}
            for _ in range(len(items) + 1):
                for a, b, dlt in cons:
                    if dlt and lane_of[a] == lane_of[b] and col[b] < col[a] + dlt:
                        col[b] = col[a] + dlt
        ncol = (max(col.values()) + 1) if col else 1
        out = [
            '<div class="sscroll" tabindex="0" role="region" aria-label="%s: %s">'
            % (esc(t["service_h"]), esc(self.state_label(state)))
        ]
        out.append(
            '<div class="sgrid" style="--n:%d" data-wires="%s">'
            % (ncol, esc(json.dumps(wires, sort_keys=True, ensure_ascii=True)))
        )
        out.append('<svg class="wires" aria-hidden="true"></svg>')
        for li, (aid, js) in enumerate(lanes.items()):
            a = s.actors.get(aid, {})
            jrel = []
            for r in s.d["relation"]:
                if (
                    r["from_id"] in js
                    and r["to_id"] in s.journeys
                    and r["to_id"] not in js
                ):
                    jrel.append(
                        "%s → %s"
                        % (
                            t["rel"].get(r["relation"], r["relation"]),
                            self.jname(r["to_id"]),
                        )
                    )
                elif (
                    r["to_id"] in js
                    and r["from_id"] in s.journeys
                    and r["from_id"] not in js
                ):
                    jrel.append(
                        "%s ← %s"
                        % (
                            t["rel_in"].get(r["relation"], r["relation"]),
                            self.jname(r["from_id"]),
                        )
                    )
            out.append(
                '<div class="lane-h" style="grid-row:%d"><p class="kicker">%s</p><h3>%s</h3>%s</div>'
                % (
                    li + 1,
                    esc(a.get("actor_type", "")),
                    esc(a.get("name", aid)),
                    "".join(
                        '<p class="lrel">%s</p>' % esc(x) for x in sorted(set(jrel))
                    ),
                )
            )
            cells = defaultdict(list)
            for it in items:
                if lane_of[it] == li:
                    cells[col[it]].append(it)
            for c in range(ncol):
                inner = "".join(self.service_card(it, state) for it in cells.get(c, []))
                out.append(
                    '<div class="scell" style="grid-row:%d;grid-column:%d">%s</div>'
                    % (li + 1, c + 2, inner)
                )
        out.append("</div></div>")
        return "".join(out)

    def service_card(self, it, state):
        s, t = self.s, self.t
        if it.startswith("J:"):
            jid = it[2:]
            j = s.journeys[jid]
            tag = "" if j["state"] == state else " · %s" % self.state_label(j["state"])
            return (
                '<div class="sc ghost" id="%s"><p class="kicker">%s%s</p><h4>%s</h4><p class="muted">%s</p></div>'
                % (
                    anchor("s-" + state, it),
                    esc(jid),
                    esc(tag),
                    esc(j["name"]),
                    esc(t["lane_empty"]),
                )
            )
        n = s.nodes[it]
        j = s.journeys.get(n["journey_id"], {})
        tag = (
            ""
            if j.get("state") == state
            else " · %s" % self.state_label(j.get("state", ""))
        )
        key = "sc-%s-%s" % (state, it)
        body = ['<p class="kicker"><code class="id">%s</code></p>' % esc(it)]
        body.append(
            '<h3 class="dt">%s</h3>%s'
            % (esc(n["name"]), self.badge(n["evidence_status"]))
        )
        if n["actor_goal"]:
            body.append(
                '<p><span class="lbl">%s</span>%s</p>'
                % (esc(t["goal"]), esc(n["actor_goal"]))
            )
        body.append(
            '<p><span class="lbl">%s</span></p>%s'
            % (esc(t["evidence"]), self.ev_chips(n["evidence_ids"]))
        )
        rels = []
        for r in s.d["relation"]:
            if r["from_id"] in s.subtree(it):
                rels.append(
                    "<li>%s %s → %s</li>"
                    % (
                        self.badge(r["evidence_status"], True),
                        esc(t["rel"].get(r["relation"], r["relation"])),
                        self.node_link(r["to_id"])
                        if r["to_id"] in s.nodes
                        else esc(self.jname(r["to_id"])),
                    )
                )
            elif r["to_id"] in s.subtree(it):
                rels.append(
                    "<li>%s %s ← %s</li>"
                    % (
                        self.badge(r["evidence_status"], True),
                        esc(t["rel_in"].get(r["relation"], r["relation"])),
                        self.node_link(r["from_id"])
                        if r["from_id"] in s.nodes
                        else esc(self.jname(r["from_id"])),
                    )
                )
            if r.get("note") and (
                r["from_id"] in s.subtree(it) or r["to_id"] in s.subtree(it)
            ):
                rels.append('<li class="muted">%s</li>' % esc(r["note"]))
        if rels:
            body.append(
                '<p><span class="lbl">%s</span></p><ul class="rels">%s</ul>'
                % (esc(t["relations"]), "".join(rels))
            )
        if s.stages(n["journey_id"]):
            body.append(
                '<p><a href="#%s">%s →</a></p>' % (anchor("p", it), esc(t["poster"]))
            )
        self.detail(key, "".join(body))
        eps = s.children.get(it, [])
        epl = (
            (
                '<ul class="seps">%s</ul>'
                % "".join(
                    '<li class="b-%s">%s</li>' % (e["evidence_status"], esc(e["name"]))
                    for e in eps
                )
            )
            if eps
            else ""
        )
        mts = sum(len(s.moments_by_node.get(x, [])) for x in s.subtree(it))
        sts = s.stages(n["journey_id"])
        jlabel = (" · " + self.jname(n["journey_id"])) if sts and sts[0]["node_id"] == it else ""
        return (
            '<div class="sc b-%s" id="%s"><button type="button" class="open" data-open="%s" aria-haspopup="dialog">'
            '<span class="kicker">%s %s%s%s</span><span class="nm">%s</span></button>%s'
            '<div class="xf">%s%s<span class="cnt">%d %s</span></div></div>'
            % (
                n["evidence_status"],
                anchor("s-" + state, it),
                esc(key),
                esc(t["stage"]),
                esc(n["sequence"]),
                esc(jlabel),
                esc(tag),
                esc(n["name"]),
                epl,
                self.badge(n["evidence_status"], True),
                '<span class="dia sm" title="%s"></span>' % esc(t["moment_leg"])
                if mts
                else "",
                len(ids(n["evidence_ids"])),
                esc(t["ev_n"]),
            )
        )

    # --- unknowns
    def unknowns(self):
        s, t = self.s, self.t
        unk = [e for e in s.evidence.values() if e["evidence_status"] == "unknown"]
        if not unk:
            return (
                '<section class="block" aria-labelledby="h-unk"><h2 id="h-unk">%s</h2><p class="note">%s</p></section>'
                % (esc(t["unknown_h"]), esc(t["no_unknowns"]))
            )
        cites = defaultdict(list)
        for n in s.nodes.values():
            for e in ids(n["evidence_ids"]):
                cites[e].append(
                    (
                        '<a href="#%s">%s</a>'
                        % (anchor("p", n["node_id"]), esc(n["name"]))
                    )
                )
        for m in s.d["moment"]:
            for e in ids(m["evidence_ids"]):
                cites[e].append(
                    '<a href="#%s">%s</a>'
                    % (anchor("m", m["moment_id"]), esc(m["moment_id"]))
                )
        for o in s.d["opportunity"]:
            for e in ids(o["evidence_ids"]):
                cites[e].append(
                    '<a href="#%s">%s</a>'
                    % (anchor("o", o["opportunity_id"]), esc(o["opportunity_id"]))
                )
        for m in s.metrics.values():
            for e in ids(m["evidence_ids"]):
                cites[e].append(self.met_chip(m["metric_id"]))
        groups = OrderedDict()
        order = {jid: i for i, jid in enumerate(s.journeys)}
        for e in sorted(
            unk,
            key=lambda e: (
                order.get(e["journey_id"], 10**6),
                e["node_id"],
                e["evidence_id"],
            ),
        ):
            groups.setdefault(e["journey_id"], OrderedDict()).setdefault(
                e["node_id"], []
            ).append(e)
        out = [
            '<section class="block" aria-labelledby="h-unk"><h2 id="h-unk">%s</h2><p class="note">%s</p><div class="unk">'
            % (esc(t["unknown_h"]), esc(t["unknown_note"]))
        ]
        for jid, by_node in groups.items():
            out.append(
                '<div class="ug"><h3>%s</h3>'
                % esc(self.jname(jid) if jid else t["other"])
            )
            for nid, rows in by_node.items():
                out.append(
                    '<p class="un">%s</p>'
                    % (self.node_link(nid) if nid else esc(t["journey_wide"]))
                )
                out.append("<ul>")
                for e in rows:
                    c = cites.get(e["evidence_id"], [])
                    out.append(
                        '<li class="uq">%s<p class="q">%s</p>%s%s</li>'
                        % (
                            self.ev_chip(e["evidence_id"]),
                            esc(e["finding"]),
                            ('<p class="muted">%s</p>' % esc(e["limitations"]))
                            if e["limitations"]
                            else "",
                            (
                                '<p class="dep"><span class="lbl">%s</span>%s</p>'
                                % (esc(t["depends_on_answer"]), ", ".join(c))
                            )
                            if c
                            else "",
                        )
                    )
                out.append("</ul>")
            out.append("</div>")
        out.append("</div></section>")
        return "".join(out)

    # --- page
    def data_json(self):
        s = self.s
        ev = {
            k: {
                "s": v["evidence_status"],
                "t": v["source_type"],
                "r": v["source_reference"],
                "c": v["collected_at"],
                "p": v["population_or_sample"],
                "f": v["finding"],
                "l": v["limitations"],
                "j": v["journey_id"],
                "n": v["node_id"],
            }
            for k, v in s.evidence.items()
        }
        mt = {
            k: {
                "n": v["name"],
                "d": v["definition"],
                "l": v["layer"],
                "u": v["unit"],
                "b": v["baseline"],
                "g": v["target"],
                "s": v["evidence_status"],
                "o": v["owner"],
                "e": v["evidence_ids"],
                "a": v["journey_or_node_id"],
            }
            for k, v in s.metrics.items()
        }
        t = self.t
        ui = {
            k: t[k]
            for k in (
                "finding",
                "source",
                "sample",
                "limits",
                "collected",
                "definition",
                "base",
                "target_v",
                "owner",
                "layer",
                "evidence",
                "hover_hint",
                "back",
            )
        }
        data = {"ev": ev, "met": mt, "st": t["status"], "ui": ui}
        raw = json.dumps(
            data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return (
            raw.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
        )

    def fonts(self):
        out = []
        for fam, file, weight, style in (
            ("JA Display", "display.woff2", "400 800", "normal"),
            ("JA Text", "text.woff2", "400 600", "normal"),
            ("JA Text", "text-italic.woff2", "400", "italic"),
            ("JA Mono", "mono.woff2", "500", "normal"),
        ):
            p = ASSETS / "fonts" / file
            if p.exists():
                b = base64.b64encode(p.read_bytes()).decode("ascii")
                out.append(
                    "@font-face{font-family:'%s';src:url(data:font/woff2;base64,%s) format('woff2');"
                    "font-weight:%s;font-style:%s;font-display:swap}"
                    % (fam, b, weight, style)
                )
        return "".join(out)

    def page(self):
        s, t = self.s, self.t
        posters = [self.poster(j) for j in s.l2() if s.stages(j["journey_id"])]
        body = [
            '<a class="skip" href="#h-idx">%s</a>' % esc(t["skip"]),
            '<main class="wrap">',
            self.overview(),
            "".join(posters),
            self.service(),
            self.unknowns(),
            '<footer class="foot"><p>%s</p></footer>' % esc(t["generated"]),
            "</main>",
            '<aside id="drawer" role="dialog" aria-modal="false" aria-labelledby="drawer-title" hidden>'
            '<button type="button" class="x" aria-label="%s">Esc ✕</button><div id="drawer-body"></div></aside>'
            % esc(t["close"]),
            '<div id="tip" role="tooltip" hidden></div>',
            "".join(
                '<template id="%s">%s</template>' % (anchor("d", k), v)
                for k, v in self.details.items()
            ),
        ]
        return (
            '<!doctype html>\n<html lang="%s">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            "<title>%s</title>\n<style>%s%s</style>\n</head>\n<body>\n%s\n"
            '<script type="application/json" id="jaos-data">%s</script>\n<script>%s</script>\n</body>\n</html>\n'
            % (
                t["lang"],
                esc(self.title),
                self.fonts(),
                CSS,
                "".join(body),
                self.data_json(),
                JS,
            )
        )


CSS = r"""
:root{
  --ground:#A9B4AE;--ground-2:#9DA9A3;--card:#F4F6F2;--card-2:#E6EBE6;--ink:#101815;--ink-2:#44524C;--rule:#7C8A84;
  --obs:#1B4B8A;--inf:#3C89C0;--hyp:#B36F08;--unk:#646E77;--mtm:#B0306A;--accent:#101815;--focus:#B0306A;
  --f-d:'JA Display','Onest',system-ui,sans-serif;--f-t:'JA Text','Literata',Georgia,serif;--f-m:'JA Mono','JetBrains Mono',ui-monospace,monospace;
  --col:248px;--lab:176px;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ground:#17201C;--ground-2:#1C2622;--card:#232E29;--card-2:#2C3833;--ink:#E8EEEA;--ink-2:#A7B5AE;--rule:#56645E;
  --obs:#8EBBF4;--inf:#5A9ECF;--hyp:#EFB04A;--unk:#9AA4AD;--mtm:#EC7EB3;--accent:#E8EEEA;--focus:#EC7EB3;color-scheme:dark}}
:root[data-theme="dark"]{
  --ground:#17201C;--ground-2:#1C2622;--card:#232E29;--card-2:#2C3833;--ink:#E8EEEA;--ink-2:#A7B5AE;--rule:#56645E;
  --obs:#8EBBF4;--inf:#5A9ECF;--hyp:#EFB04A;--unk:#9AA4AD;--mtm:#EC7EB3;--accent:#E8EEEA;--focus:#EC7EB3;color-scheme:dark}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--ground);color:var(--ink);font:15px/1.5 var(--f-t);padding-inline:16px;padding-block:28px 72px}
.wrap{max-width:1440px;margin:0 auto;display:flex;flex-direction:column;gap:56px}
h1,h2,h3,h4{font-family:var(--f-d);margin:0;text-wrap:balance;letter-spacing:-.01em}
h1{font-size:clamp(40px,7.5vw,96px);line-height:.92;font-weight:800;letter-spacing:-.035em;max-width:16ch}
h2{font-size:clamp(28px,4.2vw,52px);line-height:.98;font-weight:800;letter-spacing:-.03em}
h3{font-size:17px;line-height:1.2;font-weight:700}
h4{font-size:15px;font-weight:700}
p{margin:0}
a{color:inherit;text-underline-offset:2px;text-decoration-thickness:1px}
code,.id{font-family:var(--f-m);font-size:.82em;letter-spacing:0}
.kicker{font:600 11px/1.3 var(--f-d);letter-spacing:.12em;text-transform:uppercase;color:var(--ink-2)}
.kicker .id{letter-spacing:0;text-transform:none;font-size:11px}
.lbl{display:block;font:600 10.5px var(--f-d);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-2);margin-bottom:1px}
.muted{color:var(--ink-2)}
.note{font-size:14px;color:var(--ink-2);max-width:78ch}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.chip,.pscroll,.sscroll{position:relative}
:focus-visible{outline:3px solid var(--focus);outline-offset:2px}
.skip{position:absolute;left:-999px}.skip:focus{left:16px;top:8px;background:var(--card);padding:6px 10px;z-index:50}
.block{display:flex;flex-direction:column;gap:18px}

.hero{display:flex;flex-direction:column;gap:14px;padding-block:12px 4px}
.lede{font-size:clamp(18px,2vw,23px);line-height:1.4;max-width:46ch}
.facts{font:600 14px var(--f-d);letter-spacing:.02em}

/* status encoding: colour + pattern + label */
.sw{display:inline-block;width:11px;height:11px;flex:none;border-radius:2px;vertical-align:-1px}
.sw-observed{background:var(--obs);border:1.5px solid var(--obs)}
.sw-inferred{background:repeating-linear-gradient(135deg,var(--inf) 0 2px,transparent 2px 4px);border:1.5px solid var(--inf)}
.sw-hypothesis{background:radial-gradient(circle,var(--hyp) 1.1px,transparent 1.5px) 0 0/4px 4px;border:1.5px dashed var(--hyp)}
.sw-unknown{background:transparent;border:1.5px dotted var(--unk)}
.st{display:inline-flex;align-items:center;gap:5px;font:600 11.5px var(--f-d);padding:2px 8px 2px 6px;border-radius:99px;background:var(--card-2);white-space:nowrap}
.st.sm{font-size:10.5px;padding:1px 6px 1px 4px}
.st-observed{color:var(--obs)}.st-inferred{color:var(--inf)}.st-hypothesis{color:var(--hyp)}.st-unknown{color:var(--unk)}
.b-observed{border:2px solid var(--obs)!important}
.b-inferred{border:1.5px solid var(--inf)!important}
.b-hypothesis{border:1.5px dashed var(--hyp)!important}
.b-unknown{border:1.5px dotted var(--unk)!important}
.chips{display:inline-flex;flex-wrap:wrap;gap:4px}
.chip{font:500 11px/1.5 var(--f-m);display:inline-flex;align-items:center;gap:4px;padding:1px 6px;border-radius:4px;border:1px solid var(--rule);background:transparent;color:var(--ink);cursor:pointer}
.chip:hover{background:var(--card-2)}
.chip.met.root{background:var(--ink);color:var(--card);border-color:var(--ink);font-weight:700}
.dia{display:inline-block;width:13px;height:13px;background:var(--mtm);transform:rotate(45deg);flex:none}
.dia.sm{width:9px;height:9px}

/* index + meters */
.tree,.tree ol{list-style:none;margin:0;padding:0}
.tree ol{padding-left:22px;border-left:2px solid var(--rule);margin-left:6px}
.tree li{padding:6px 0 6px 10px}
.tree .tn{display:block;font:700 17px/1.25 var(--f-d)}
.tree .lv-L0>.tn{font-size:22px}
.tree .tm{display:block;font-size:13px;color:var(--ink-2)}
.meter{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.mcol{background:var(--card);border-radius:14px;padding:18px;display:flex;flex-direction:column;gap:12px}
.mrow{display:grid;grid-template-columns:minmax(0,15em) minmax(0,1fr);gap:2px 14px;align-items:center}
.mlab{font:600 13.5px/1.25 var(--f-d)}.mlab span{display:block;font:400 12px var(--f-t);color:var(--ink-2)}
.bar{display:flex;height:16px;gap:2px}.bar.tall{height:22px}
.seg{display:block;min-width:4px;height:100%;border-radius:3px}
.seg.sw-inferred{background:repeating-linear-gradient(135deg,var(--inf) 0 3px,transparent 3px 6px)}
.seg.sw-hypothesis{background:radial-gradient(circle,var(--hyp) 1.6px,transparent 2px) 0 0/6px 6px}
.seg.empty{flex:1;border:1.5px dashed var(--rule)}
.mnum{grid-column:2;font-size:11.5px;color:var(--ink-2);font-variant-numeric:tabular-nums}
.legend{background:var(--card-2);border-radius:14px;padding:14px 18px}
.legend ul{list-style:none;margin:8px 0 0;padding:0;display:flex;flex-wrap:wrap;gap:8px 22px;font-size:13px}
.legend li{display:flex;align-items:center;gap:8px}

/* poster */
.poster{background:var(--card);border-radius:22px;overflow:hidden;box-shadow:0 1px 0 rgba(0,0,0,.06),0 18px 50px rgba(10,20,15,.14)}
.ph{display:grid;grid-template-columns:minmax(0,300px) minmax(0,1fr) minmax(0,230px);gap:28px;padding:28px;background:var(--ink);color:var(--card)}
.ph .kicker,.ph .muted,.ph .lbl{color:color-mix(in srgb,var(--card) 72%,transparent)}
.ph h2{font-size:clamp(30px,4.4vw,58px);max-width:20ch}
.actor{display:flex;gap:14px;align-items:flex-start}
.actor .mono{flex:none;width:64px;height:64px;border-radius:50%;background:var(--card);color:var(--ink);display:grid;place-items:center;font:800 24px var(--f-d);letter-spacing:-.02em}
.actor h3{font-size:19px;margin:2px 0 6px}
.actor p{font-size:13px}
.pj{display:flex;flex-direction:column;gap:12px;min-width:0}
.pfacts{margin:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px 22px}
.pfacts dt{font:600 10.5px var(--f-d);letter-spacing:.1em;text-transform:uppercase;color:color-mix(in srgb,var(--card) 70%,transparent)}
.pfacts dd{margin:0;font-size:14px}
.plink{font-size:13.5px}
.plink .chip{color:var(--card);border-color:color-mix(in srgb,var(--card) 50%,transparent)}
.plink .chip.root{background:var(--card);color:var(--ink)}
.pmeter{display:flex;flex-direction:column;gap:10px}
.pmeter ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr auto;gap:4px 10px;font-size:13px}
.pmeter li{display:contents}.pmeter b{font:700 14px var(--f-d);text-align:right;font-variant-numeric:tabular-nums}
.pscroll{overflow-x:auto;overscroll-behavior-x:contain}
.pgrid{display:grid;grid-template-columns:var(--lab) repeat(var(--n),var(--col));width:max-content;min-width:100%}
.rl{position:sticky;left:0;z-index:3;background:var(--card-2);padding:14px 14px;border-top:1px solid color-mix(in srgb,var(--rule) 40%,transparent);display:flex;flex-direction:column;gap:6px}
.rl span{font:700 12.5px/1.2 var(--f-d);letter-spacing:.06em;text-transform:uppercase}
.rl-head{background:var(--card)}
.rl-note{font-size:11.5px;color:var(--ink-2);line-height:1.35}
.rl-sub{border-top:0}
.rl-chips{display:flex;flex-wrap:wrap;gap:4px}
.cell{padding:10px 8px;display:flex;flex-direction:column;gap:8px;min-width:0;border-top:1px solid color-mix(in srgb,var(--rule) 40%,transparent);border-left:1px dashed color-mix(in srgb,var(--rule) 45%,transparent)}
.cell.none{font-size:13px;color:var(--ink-2);font-style:italic}
.cell.wide{flex-direction:row;flex-wrap:wrap}.cell.wide>*{width:calc(var(--col) - 16px)}
.missing{padding:14px 18px;background:repeating-linear-gradient(135deg,transparent 0 8px,color-mix(in srgb,var(--unk) 12%,transparent) 8px 16px);font-size:14px;border-top:1px solid var(--rule)}
.sh{margin:10px 6px;padding:14px;border-radius:14px;background:var(--card);display:flex;flex-direction:column;gap:8px;min-width:0}
.sh-top{display:flex;justify-content:space-between;align-items:center;gap:8px}
.num{font:800 44px/0.85 var(--f-d);letter-spacing:-.04em}
.sh h3{font-size:19px;line-height:1.15;letter-spacing:-.015em}
.goal{font-size:13.5px}
.eps{list-style:none;margin:4px 0 0;padding:0;display:flex;flex-direction:column;gap:6px}
.eps li{display:flex;gap:8px;padding:7px 8px;border-radius:9px;background:var(--card-2);font-size:13px}
.eps li b{font-weight:600;display:block;margin-bottom:3px}
.en{font:700 12px var(--f-d);color:var(--ink-2);padding-top:1px}
.xi,.mt,.op,.mi{background:var(--card);border-radius:10px;padding:9px 10px;display:flex;flex-direction:column;gap:6px;font-size:13.5px;line-height:1.4}
.xi-thought p{font-style:italic}
.xi-pain{background:color-mix(in srgb,var(--mtm) 7%,var(--card))}
.xi .kind,.ep{font:600 10.5px var(--f-d);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2)}
.ep{letter-spacing:.02em;text-transform:none;font-size:11.5px}
.xf{display:flex;flex-wrap:wrap;gap:4px 6px;align-items:center}
.val{font:800 14px var(--f-d)}
.gapnote{font:600 12px var(--f-d);color:var(--ink-2);letter-spacing:.04em;text-transform:uppercase}
.curve-cell{padding:0;border-left:0}
.curve{display:block}
.curve .c-grid{stroke:var(--rule);stroke-opacity:.35;stroke-width:1}
.curve .c-zero{stroke:var(--ink-2);stroke-width:1.2}
.curve .c-col{stroke:var(--rule);stroke-opacity:.45;stroke-dasharray:3 4}
.curve .c-ax{fill:var(--ink-2);font:600 10px var(--f-d)}
.curve .c-gap{fill:none;stroke:var(--unk);stroke-width:1.5;stroke-dasharray:2 5;rx:10}
.curve .c-gaptext{fill:var(--unk);font:700 11px var(--f-d);letter-spacing:.08em;text-transform:uppercase}
.curve .c-solid{stroke:var(--ink);stroke-width:3;stroke-linecap:round}
.curve .c-dash{stroke:var(--ink);stroke-width:2.2;stroke-dasharray:7 6;stroke-linecap:round}
.curve .c-pt{stroke-width:2.5}
.curve .c-observed{fill:var(--obs);stroke:var(--obs)}
.curve .c-inferred{fill:url(#hatch);stroke:var(--inf)}
.curve .c-hypothesis{fill:var(--card);stroke:var(--hyp);stroke-dasharray:3 2.5}
.curve .c-bg{fill:var(--card)}.curve .c-inf-line{stroke:var(--inf);stroke-width:2}
.mt{flex-direction:row;gap:10px;background:color-mix(in srgb,var(--mtm) 9%,var(--card))}
.mt .dia{margin-top:5px}
.mt>div{display:flex;flex-direction:column;gap:4px;min-width:0}
.mt-h{font:700 12.5px var(--f-d);color:var(--mtm)}
.op-top{display:flex;justify-content:space-between;gap:8px;align-items:center}
.op-o{font:700 14.5px/1.3 var(--f-d)}
.dec{font:700 11px var(--f-d);padding:2px 9px;border-radius:99px;background:var(--ink);color:var(--card);letter-spacing:.02em}
.dec-investigate,.dec-monitor{background:transparent;color:var(--ink);border:1.5px solid var(--ink)}
.dec-sequence{background:transparent;color:var(--ink);border:1.5px dashed var(--ink)}
.dec-deprioritize{background:var(--card-2);color:var(--ink-2)}

/* service view */
.tabs{display:inline-flex;flex-wrap:wrap;gap:4px;background:var(--card-2);padding:4px;border-radius:99px;align-self:flex-start}
.tabs button{font:700 14px var(--f-d);color:var(--ink);background:transparent;border:0;padding:8px 18px;border-radius:99px;cursor:pointer}
.tabs button[aria-selected="true"]{background:var(--ink);color:var(--card)}
.sview:not(.on){display:none}
.sscroll{overflow-x:auto;background:var(--card-2);border-radius:18px;overscroll-behavior-x:contain}
.sgrid{position:relative;display:grid;grid-template-columns:var(--lab) repeat(var(--n),minmax(220px,236px));width:max-content;min-width:100%}
.wires{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:0;overflow:visible}
.lane-h{position:sticky;left:0;z-index:3;grid-column:1;background:var(--ink);color:var(--card);padding:16px 14px;display:flex;flex-direction:column;gap:6px;border-bottom:1px solid var(--ground-2)}
.lane-h .kicker{color:color-mix(in srgb,var(--card) 70%,transparent)}
.lrel{font-size:12px;color:color-mix(in srgb,var(--card) 80%,transparent)}
.scell{padding:14px 10px;display:flex;flex-direction:column;gap:10px;border-bottom:1px dashed color-mix(in srgb,var(--rule) 60%,transparent);position:relative;z-index:1}
.sc{background:var(--card);border-radius:12px;padding:11px 12px;display:flex;flex-direction:column;gap:7px}
.sc.ghost{background:transparent;border:1.5px dashed var(--rule)}
.open{all:unset;box-sizing:border-box;display:flex;flex-direction:column;gap:3px;cursor:pointer;border-radius:4px}
.open:focus-visible{outline:3px solid var(--focus);outline-offset:3px}
.open:hover .nm{text-decoration:underline;text-underline-offset:3px}
.nm{font:700 15px/1.25 var(--f-d);letter-spacing:-.01em}
.seps{margin:0;padding-left:16px;font-size:12.5px;color:var(--ink-2)}
.seps li{border:0!important}
.cnt{font:500 11px var(--f-m);color:var(--ink-2)}
.rels{margin:0;padding-left:18px;font-size:13px;display:flex;flex-direction:column;gap:4px}

/* unknowns */
.unk{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,420px),1fr));gap:16px}
.ug{background:var(--card);border-radius:16px;padding:18px;display:flex;flex-direction:column;gap:8px;border:1.5px dotted var(--unk)}
.ug ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:12px}
.un{font:700 13px var(--f-d);color:var(--ink-2)}
.uq{display:flex;flex-direction:column;gap:5px;align-items:flex-start}
.q{font-size:15.5px;line-height:1.4}
.dep{font-size:13px}
.foot{font-size:12.5px;color:var(--ink-2)}

/* drawer + tip */
#drawer{position:fixed;top:0;right:0;bottom:0;width:min(460px,100vw);overflow:auto;background:var(--card);color:var(--ink);border-left:2px solid var(--ink);padding:calc(18px + env(safe-area-inset-top,0px)) 22px calc(28px + env(safe-area-inset-bottom,0px));z-index:40;box-shadow:-18px 0 50px rgba(0,0,0,.25)}
#drawer[hidden],#tip[hidden]{display:none}
#drawer .x{position:absolute;top:12px;right:12px;font:700 13px var(--f-d);background:var(--card-2);color:var(--ink);border:0;border-radius:99px;padding:6px 12px;cursor:pointer}
#drawer-body{display:flex;flex-direction:column;gap:12px;font-size:14px}
#drawer .dt{font-size:24px;padding-right:70px}
#drawer .back{align-self:flex-start;font:700 13px var(--f-d);background:transparent;color:var(--ink);border:1.5px solid var(--ink);border-radius:99px;padding:4px 12px;cursor:pointer}
#tip{position:fixed;z-index:45;max-width:min(380px,calc(100vw - 16px));background:var(--ink);color:var(--card);padding:10px 12px;border-radius:10px;font-size:13px;line-height:1.4;pointer-events:none;box-shadow:0 10px 28px rgba(0,0,0,.28)}
#tip .st{background:var(--card);margin-bottom:5px}
#tip .k{display:block;margin-top:6px;font-size:11px;opacity:.7}

@media (max-width:980px){.ph{grid-template-columns:minmax(0,1fr)}.meter{grid-template-columns:minmax(0,1fr)}}
@media (max-width:560px){:root{--col:224px;--lab:112px}.mrow{grid-template-columns:minmax(0,1fr)}.mnum{grid-column:1}
  .pfacts{grid-template-columns:minmax(0,1fr)}.ph{padding:20px}.rl{padding:10px 8px}.rl span{font-size:11px}
  .sgrid{grid-template-columns:var(--lab) repeat(var(--n),minmax(200px,212px))}}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
@page{size:A4 landscape;margin:9mm}
@media print{
  :root{--ground:#fff;--col:1fr}
  body{padding:0;font-size:10px}
  .tabs,#drawer,#tip,.skip{display:none!important}
  .sview{display:block!important;break-inside:avoid;margin-bottom:12px}
  .poster{break-before:page;box-shadow:none;border:1px solid #999;border-radius:0}
  .pscroll,.sscroll{overflow:visible}
  .pgrid{width:100%;grid-template-columns:90px repeat(var(--n),minmax(0,1fr))}
  .sgrid{width:100%;grid-template-columns:90px repeat(var(--n),minmax(0,1fr))}
  .curve{width:100%;height:auto}
  .rl,.lane-h{position:static}
  .xi,.mt,.op,.mi,.sh,.sc,.ug{break-inside:avoid}
  .block{break-before:page}
}
"""

JS = r"""
(function(){
var D=JSON.parse(document.getElementById('jaos-data').textContent),U=D.ui;
var drawer=document.getElementById('drawer'),body=document.getElementById('drawer-body'),tip=document.getElementById('tip');
var stack=[],lastFocus=null;
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function badge(s){return '<span class="st st-'+esc(s)+'"><i class="sw sw-'+esc(s)+'" aria-hidden="true"></i>'+esc(D.st[s]||s)+'</span>'}
function field(l,v){return v?'<p><span class="lbl">'+esc(l)+'</span>'+esc(v)+'</p>':''}
function render(){body.innerHTML=(stack.length>1?'<button type="button" class="back">← '+esc(U.back)+'</button>':'')+stack[stack.length-1];body.scrollTop=0}
function open(h){hideTip();if(drawer.hidden){lastFocus=document.activeElement;stack=[]}stack.push(h);render();drawer.hidden=false;(body.querySelector('.back')||drawer.querySelector('.x')).focus()}
function close(){drawer.hidden=true;stack=[];if(lastFocus&&lastFocus.focus)lastFocus.focus()}
function evHtml(k){var v=D.ev[k];if(!v)return '';return '<p class="kicker">'+esc(v.t)+'</p><h3 id="drawer-title" class="dt">'+esc(k)+'</h3><div>'+badge(v.s)+'</div>'+
  field(U.finding,v.f)+field(U.source,v.r)+field(U.sample,v.p)+field(U.collected,v.c)+field(U.limits,v.l)+'<p class="muted">'+esc(v.j)+(v.n?' · '+esc(v.n):'')+'</p>'}
function metHtml(k){var w=D.met[k];if(!w)return '';return '<p class="kicker">'+esc(w.l)+' · '+esc(w.a)+'</p><h3 id="drawer-title" class="dt">'+esc(k)+' · '+esc(w.n)+'</h3><div>'+badge(w.s)+'</div>'+
  field(U.definition,w.d)+field(U.base,w.b)+field(U.target_v,w.g)+field(U.owner,w.o)+field(U.evidence,w.e)}
function tipHtml(el){var k=el.getAttribute('data-ev');if(k&&D.ev[k]){var v=D.ev[k];return badge(v.s)+' <b>'+esc(k)+'</b><br>'+esc(v.f)}
  k=el.getAttribute('data-met');if(k&&D.met[k]){var w=D.met[k];return badge(w.s)+' <b>'+esc(k)+'</b> · '+esc(w.l)+'<br>'+esc(w.n)}return ''}
function showTip(el){var h=tipHtml(el);if(!h)return;tip.innerHTML=h+'<span class="k">'+esc(U.hover_hint)+'</span>';tip.hidden=false;el.setAttribute('aria-describedby','tip');
  var r=el.getBoundingClientRect(),w=tip.offsetWidth,hh=tip.offsetHeight,x=Math.max(8,Math.min(r.left,innerWidth-w-8)),y=r.bottom+8;
  if(y+hh>innerHeight-8)y=Math.max(8,r.top-hh-8);tip.style.left=x+'px';tip.style.top=y+'px'}
function hideTip(el){tip.hidden=true;if(el&&el.removeAttribute)el.removeAttribute('aria-describedby')}
function chipOf(e){return e.target.closest&&e.target.closest('[data-ev],[data-met]')}
['mouseover','focusin'].forEach(function(t){document.addEventListener(t,function(e){var c=chipOf(e);if(c)showTip(c)})});
['mouseout','focusout'].forEach(function(t){document.addEventListener(t,function(e){var c=chipOf(e);if(c)hideTip(c)})});
window.addEventListener('scroll',function(){hideTip()},true);
document.addEventListener('keydown',function(e){if(e.key==='Escape'){if(!tip.hidden){hideTip();return}if(!drawer.hidden)close()}});
drawer.querySelector('.x').addEventListener('click',close);
document.addEventListener('click',function(e){
  if(e.target.closest('#drawer .back')){stack.pop();render();(body.querySelector('.back')||drawer.querySelector('.x')).focus();return}
  var o=e.target.closest('[data-open]');if(o){var tp=document.getElementById('d-'+o.getAttribute('data-open').replace(/[^A-Za-z0-9_-]/g,'_'));if(tp)open(tp.innerHTML);return}
  var c=e.target.closest('[data-ev]');if(c){var h=evHtml(c.getAttribute('data-ev'));if(h)open(h);return}
  c=e.target.closest('[data-met]');if(c){var h2=metHtml(c.getAttribute('data-met'));if(h2)open(h2);return}
  var a=e.target.closest('#drawer a[href^="#"]');if(a){drawer.hidden=true;stack=[]}
});
var tabs=[].slice.call(document.querySelectorAll('.tabs [role=tab]'));
function show(id){tabs.forEach(function(t){var on=t.getAttribute('aria-controls')===id;t.setAttribute('aria-selected',on?'true':'false');t.tabIndex=on?0:-1;
  document.getElementById(t.getAttribute('aria-controls')).classList.toggle('on',on)});requestAnimationFrame(drawAll)}
tabs.forEach(function(t,i){t.addEventListener('click',function(){show(t.getAttribute('aria-controls'))});
  t.addEventListener('keydown',function(e){var d=e.key==='ArrowRight'?1:e.key==='ArrowLeft'?-1:0;if(!d)return;var n=tabs[(i+d+tabs.length)%tabs.length];n.focus();show(n.getAttribute('aria-controls'))})});
var NS='http://www.w3.org/2000/svg';
function draw(g){var svg=g.querySelector('.wires');if(!svg||!g.offsetParent)return;while(svg.firstChild)svg.removeChild(svg.firstChild);
  var W=[];try{W=JSON.parse(g.getAttribute('data-wires')||'[]')}catch(e){}
  var R=g.getBoundingClientRect(),view=g.closest('.sview'),vid=view?view.id:'x',ink=getComputedStyle(document.documentElement).getPropertyValue('--ink');
  svg.setAttribute('viewBox','0 0 '+R.width+' '+R.height);
  var defs=document.createElementNS(NS,'defs'),m=document.createElementNS(NS,'marker');m.setAttribute('id','ah-'+vid);m.setAttribute('viewBox','0 0 10 10');
  m.setAttribute('refX','9');m.setAttribute('refY','5');m.setAttribute('markerWidth','7');m.setAttribute('markerHeight','7');m.setAttribute('orient','auto-start-reverse');
  var p0=document.createElementNS(NS,'path');p0.setAttribute('d','M0,0L10,5L0,10z');p0.setAttribute('fill',ink);m.appendChild(p0);defs.appendChild(m);svg.appendChild(defs);
  W.forEach(function(w){var a=document.getElementById(vid.replace(/^sv-/,'s-')+'-'+w.a.replace(/[^A-Za-z0-9_-]/g,'_')),b=document.getElementById(vid.replace(/^sv-/,'s-')+'-'+w.b.replace(/[^A-Za-z0-9_-]/g,'_'));
    if(!a||!b)return;var A=a.getBoundingClientRect(),B=b.getBoundingClientRect(),d,x1,y1,x2,y2;
    if(Math.abs(A.left-B.left)<20){x1=A.left+A.width*.8-R.left;x2=B.left+B.width*.8-R.left;
      if(A.bottom<B.top){y1=A.bottom-R.top;y2=B.top-R.top}else{y1=A.top-R.top;y2=B.bottom-R.top}
      d='M'+x1+','+y1+' C'+x1+','+((y1+y2)/2)+' '+x2+','+((y1+y2)/2)+' '+x2+','+y2}
    else{var fw=A.left<B.left;x1=(fw?A.right:A.left)-R.left;x2=(fw?B.left:B.right)-R.left;y1=A.top+Math.min(28,A.height/2)-R.top;y2=B.top+Math.min(28,B.height/2)-R.top;
      var mx=(x1+x2)/2;d='M'+x1+','+y1+' C'+mx+','+y1+' '+mx+','+y2+' '+x2+','+y2}
    var p=document.createElementNS(NS,'path');p.setAttribute('d',d);p.setAttribute('fill','none');p.setAttribute('stroke',ink);
    p.setAttribute('stroke-width',w.s==='observed'?'2.6':'1.8');
    if(w.s==='hypothesis')p.setAttribute('stroke-dasharray','7 5');if(w.s==='unknown')p.setAttribute('stroke-dasharray','1.5 5');
    if(!w.u)p.setAttribute('marker-end','url(#ah-'+vid+')');p.setAttribute('opacity','.8');svg.appendChild(p)})}
function drawAll(){[].forEach.call(document.querySelectorAll('.sgrid'),draw)}
if(window.ResizeObserver){var ro=new ResizeObserver(drawAll);[].forEach.call(document.querySelectorAll('.sgrid'),function(g){ro.observe(g)})}
window.addEventListener('load',drawAll);if(document.fonts&&document.fonts.ready)document.fonts.ready.then(drawAll);
window.addEventListener('beforeprint',function(){[].forEach.call(document.querySelectorAll('.sview'),function(v){v.classList.add('on')});drawAll()});
drawAll();
})();
"""


def render(root, lang="en", title=None):
    sysm = System(Path(root), lang)
    if not title:
        doms = [j for j in sysm.journeys.values() if j["level"] == "L0"]
        title = doms[0]["name"] if len(doms) == 1 else T[lang]["default_title"]
    return Renderer(sysm, title).page()


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Render a journey system (CSV registers) as one self-contained HTML map."
    )
    ap.add_argument("system", help="directory holding the CSV registers")
    ap.add_argument("-o", "--output", required=True, help="HTML file to write")
    ap.add_argument(
        "--lang",
        choices=sorted(T),
        default="en",
        help="interface language (register text is shown as is)",
    )
    ap.add_argument(
        "--title",
        help="page title (default: the L0 domain name, if there is exactly one)",
    )
    args = ap.parse_args(argv)
    try:
        page = render(args.system, args.lang, args.title)
    except InputError as exc:
        print("render_map: %s" % exc, file=sys.stderr)
        return 2
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print("%s: %d bytes" % (out, len(page.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
