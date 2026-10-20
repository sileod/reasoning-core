"""Independent oracles for the Jev procedural tasks ported from tasksource.jev.procedural.

Each oracle recomputes the gold labels from what a model sees -- the state and the question wording -- with its own
code (replays, brute-force searches, truth tables, exact posteriors, prose parsers), never with the generator's
helpers or hidden data. Moved from tasksource's tests/test_procedural_execution.py, test_record_eligibility.py and
test_procedural_jev.py when the generators moved here.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import product

import pytest

from reasoning_core import get_task
from reasoning_core.decision import jev_request

TASKS = ["claim_support", "entity_belief_tracking", "event_state_reconstruction", "event_triggered_execution",
         "goal_directed_planning", "graph_navigation", "instruction_execution", "multi_view_adjudication",
         "needle_retrieval", "partial_observation_calibration", "policy_applicability", "policy_under_uncertainty",
         "practical_arithmetic", "record_aggregation", "record_eligibility", "state_perturbation", "table_lookup",
         "taxonomy_routing"]


@lru_cache(None)
def _task(name):
    return get_task(name)


@lru_cache(None)
def at_level(name, level, n):
    """n states of one level, each with all its questions."""
    return [jev_request(_task(name), seed, level) for seed in range(n)]


def mixed(name, n):
    """n states cycling through levels 0-4 (seed i at level i % 5)."""
    per = -(-n // 5)
    return [at_level(name, i % 5, per)[i // 5] for i in range(n)]


def labels(request):
    return {qid: q["label"] for qid, q in request["questions"].items()}


def ask(request, qid, pattern):
    """The groups of `pattern` searched in a question's instructions (probes are named there)."""
    match = re.search(pattern, request["questions"][qid]["instructions"])
    assert match, (qid, request["questions"][qid]["instructions"])
    return match.groups() if len(match.groups()) > 1 else match.group(1)


def _scalar(text):
    text = text.strip()
    return {"True": True, "False": False}.get(text, int(text) if re.fullmatch(r"-?\d+", text) else text)


def parse_records(text):
    """Flat records back from any render_records style: JSON, Markdown table, CSV or key=value lines."""
    text = text.strip()
    if text.startswith("["):
        return json.loads(text)
    lines = text.split("\n")
    if re.fullmatch(r"\w+=.*", lines[0]):
        return [{k: _scalar(v) for k, v in (part.split("=", 1) for part in line.split("; "))} for line in lines]
    sep = " | " if len(lines) > 1 and set(lines[1]) <= set("-| ") else ","
    rows = [line.split(sep) for line in lines if not set(line) <= set("-| ")]
    return [dict(zip(rows[0], map(_scalar, row))) for row in rows[1:]]


# --------------------------------------------------------------------------- every task: typing and determinism

@pytest.mark.parametrize("name", TASKS)
def test_answers_are_well_typed(name):
    for level in range(5):
        for request in at_level(name, level, 30):
            json.dumps(request, allow_nan=False)
            assert request["questions"]
            for qid, q in request["questions"].items():
                criteria = q.get("criteria")
                if q["type"] == "noul":
                    assert isinstance(q["label"], bool)
                    if "target" in q:
                        assert 0 <= q["target"]["true"] <= 1
                elif q["type"] == "score":
                    assert len(criteria) <= 10, (name, qid)   # the Jev API limit
                    assert q["label"] in range(len(criteria)), (name, qid)
                else:
                    assert len(set(criteria)) == len(criteria) and q["label"] in criteria, (name, qid)
                if "target" in q and q["type"] != "noul":
                    assert abs(sum(q["target"].values()) - 1) < 1e-6
                    assert q["type"] == "score" or set(q["target"]) <= set(criteria)
        assert jev_request(_task(name), 31, level) == jev_request(_task(name), 31, level)   # deterministic


def test_generation_does_not_depend_on_the_hash_seed():
    script = ("import hashlib, json\nfrom reasoning_core import get_task\nfrom reasoning_core.decision import "
              f"jev_request\nfor name in {TASKS!r}:\n    h = hashlib.sha1()\n    for i in range(10):\n"
              "        h.update(json.dumps(jev_request(get_task(name), i, i % 5), sort_keys=True).encode())\n"
              "    print(name, h.hexdigest())")
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    outputs = [subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True, cwd=root,
                              env={**os.environ, "PYTHONHASHSEED": seed,
                                   "PYTHONPATH": os.pathsep.join([root, os.environ.get("PYTHONPATH", "")])}).stdout
               for seed in ("1", "2")]
    assert outputs[0] and outputs[0] == outputs[1]


# --------------------------------------------------------------------------- instruction_execution

def _instruction_oracle(state):
    from reasoning_core.tasks.jev.instruction_execution import DOMAINS
    noun, prop = state["entity_type"], state["property"]
    positive, negative = next((p, n) for d, _, p, n in DOMAINS if d == noun)
    verb_value = {positive: True, negative: False}
    request = state["request"]
    for pattern, kind in ((r"Are (.+) currently \w+\?", "query"), (r"At 18:30, (\S+) (.+)\.", "schedule"),
                          (r"Whenever a review event occurs, (\S+) (.+)\.", "rule"),
                          (r"First (\S+) (.+), then (\S+) them\.", "ordered"), (r"Please (\S+) (.+)\.", "immediate")):
        match = re.fullmatch(pattern, request)
        if match:
            break
    groups = match.groups()
    selector = groups[0] if kind == "query" else groups[1]
    values = ([verb_value[groups[0]], verb_value[groups[2]]] if kind == "ordered" else
              [] if kind == "query" else [verb_value[groups[0]]])
    entities = state["entities"]
    excluded = None
    if ", except " in selector:
        selector, excluded = selector.split(", except ")
    site = re.fullmatch(rf"all {noun}s at site (\w+)(?: with tier (\w+))?", selector)
    if selector.startswith(f"all {noun}s in "):
        ids = list(state["groups"][selector[len(f"all {noun}s in "):]])
    elif site:
        ids = [e["id"] for e in entities if e["site"] == site[1] and site[2] in (None, e["tier"])]
    else:
        ids = [e["id"] for e in entities if e["name"] == selector]
        if len(ids) != 1:   # an ambiguous or unknown name
            assert kind == "immediate" and excluded is None, request
            kind, ids = "clarify", []
    if excluded:
        (gone,) = [e["id"] for e in entities if e["name"] == excluded]
        ids.remove(gone)

    before = {e["id"]: e for e in entities}
    final = {i: dict(e) for i, e in before.items()}
    unavailable = [i for i in ids if not before[i]["available"]]
    if kind in ("clarify", "query", "schedule", "rule"):
        status = kind
    elif not ids:
        status = "no_change"
    elif unavailable and state["execution_policy"] == "atomic":
        status = "blocked"
    else:
        allowed = [i for i in ids if before[i]["available"]]
        status = "partial" if unavailable and allowed else "execute" if allowed else "blocked"
        for value in values if allowed else []:
            for i in allowed:
                final[i][prop] = value
        if status == "execute" and len(values) == 1 and all(final[i][prop] == before[i][prop] for i in ids):
            status = "no_change"
    changed = sum(e[prop] != final[i][prop] for i, e in before.items())
    return status, ids, final, changed


def test_instruction_execution_effects():
    for level in range(5):
        for r in at_level("instruction_execution", level, 60):
            state, a = r["state"], labels(r)
            status, ids, final, changed = _instruction_oracle(state)
            probe = ask(r, "probe_selected", r"Is (E\d+) in")
            assert ask(r, "probe_final_state", r"is (E\d+)\.") == probe
            assert a["resolution"] == status
            assert a["target_count"] == min(len(ids), 9)
            assert a["changed_count"] == min(changed, 9)
            assert a["probe_selected"] == (probe in ids)
            assert a["probe_final_state"] == final[probe][state["property"]]
            assert a["deferred_registration"] == {"schedule": "one-time schedule",
                                                  "rule": "recurring rule"}.get(status, "nothing")


# --------------------------------------------------------------------------- goal_directed_planning

def _plan_oracle(state, forbidden=None, starting=None):
    steps = state["steps"]
    initial = frozenset(s["id"] for s in steps if s["completed"]) if starting is None else starting
    goal = set(state["goal"])

    @lru_cache(None)
    def solve(done):
        if goal <= set(done):
            return 0
        choices = []
        for s in steps:
            if s["id"] == forbidden or s["id"] in done or not s["available"]:
                continue
            if set(s["requires_all"]) <= set(done) and (not s["requires_any"] or set(s["requires_any"]) & set(done)):
                answer = solve(frozenset((*done, s["id"])))
                if answer is not None:
                    choices.append(answer + 1)
        return min(choices) if choices else None

    legal = [s["id"] for s in steps if s["id"] not in initial and s["available"]
             and set(s["requires_all"]) <= set(initial)
             and (not s["requires_any"] or set(s["requires_any"]) & set(initial))]
    return solve(initial), legal


def test_goal_directed_planning_optimality():
    for level in range(5):
        for r in at_level("goal_directed_planning", level, 60):
            state, a = r["state"], labels(r)
            name = ask(r, "probe_applicable", r"Can (S\d+) be executed")
            assert ask(r, "probe_optimal_first", r"executing (S\d+) first") == name
            assert ask(r, "probe_required", r"execute (S\d+)\?") == name
            distance, legal = _plan_oracle(state)
            assert a["goal_reachable"] == (distance is not None)
            assert a["minimal_actions"] == (9 if distance is None else min(distance, 8))
            assert a["probe_applicable"] == (name in legal)
            assert a["first_legal_action"] == (min(legal, key=lambda x: int(x[1:])) if legal else "none")
            start = frozenset([name, *[s["id"] for s in state["steps"] if s["completed"]]])
            rest = _plan_oracle(state, starting=start)[0] if name in legal else None
            assert a["probe_optimal_first"] == (distance is not None and name in legal and rest == distance - 1)
            without = _plan_oracle(state, forbidden=name)[0]
            assert a["probe_required"] == (distance is not None and (without is None or without > distance))


# --------------------------------------------------------------------------- event_triggered_execution

def _event_oracle(state):
    values = {o["id"]: o["state"] for o in state["objects"]}
    enabled = {r["id"]: r["enabled"] for r in state["rules"]}
    last, events, targets = {}, {}, []
    for e in sorted(state["events"], key=lambda x: x["ts"]):
        if e["kind"] == "control":
            enabled[e["rule"]] = e["enabled"]
            continue
        chosen = None
        for rule in sorted(state["rules"], key=lambda x: (-x["priority"], int(x["id"][1:]))):
            if not enabled[rule["id"]] or rule["event_type"] != e["kind"]:
                continue
            if rule["target"] not in ("any", e["target"]) or e["value"] < rule["min_value"]:
                continue
            if rule["required_state"] is not None and rule["required_state"] != values[e["target"]]:
                continue
            if rule["id"] in last and e["ts"] - last[rule["id"]] < rule["cooldown"]:
                continue
            chosen = rule
            break
        events[e["ts"]] = chosen["id"] if chosen else "none"
        if chosen:
            values[e["target"]] = chosen["set_state"]
            last[chosen["id"]] = e["ts"]
            targets.append(e["target"])
    return values, enabled, events, targets


def test_event_triggered_execution_replay():
    for level in range(5):
        for r in at_level("event_triggered_execution", level, 60):
            a = labels(r)
            values, enabled, events, targets = _event_oracle(r["state"])
            assert a["rule_on_signal"] == events[int(ask(r, "rule_on_signal", r"timestamp (\d+)"))]
            assert a["object_final_state"] == values[ask(r, "object_final_state", r"is (O\d+)\.state")]
            assert a["rule_enabled_at_end"] == enabled[ask(r, "rule_enabled_at_end", r"Is (R\d+) enabled")]
            assert a["total_firings"] == min(sum(x != "none" for x in events.values()), 9)
            assert a["object_ever_targeted"] == (ask(r, "object_ever_targeted", r"on (O\d+) during") in targets)


# --------------------------------------------------------------------------- graph_navigation

def _graph_oracle(state, removed=None):
    nodes = state["nodes"]
    inf = float("inf")
    dist = {(a, b): 0 if a == b else inf for a, b in product(nodes, repeat=2)}
    for e in state["edges"]:
        if e["open"] and e["id"] != removed:
            dist[e["from"], e["to"]] = min(dist[e["from"], e["to"]], e["cost"])
    for k in nodes:
        for a in nodes:
            for b in nodes:
                dist[a, b] = min(dist[a, b], dist[a, k] + dist[k, b])
    via, start, end = state["via"], state["start"], state["finish"]
    middle = via or end
    cost = dist[start, middle] + (dist[via, end] if via else 0)
    if cost == inf:
        return None, "none"
    hops = [e["to"] for e in state["edges"] if e["open"] and e["id"] != removed
            and e["from"] == start and e["cost"] + dist[e["to"], middle] == dist[start, middle]]
    return cost, min(hops) if hops else "none"


def test_graph_navigation_shortest_paths():
    for level in range(5):
        for r in at_level("graph_navigation", level, 60):
            a = labels(r)
            cost, hop = _graph_oracle(r["state"])
            budget = int(ask(r, "within_budget", r"at most (\d+)\?"))
            probe = ask(r, "edge_essential", r"edge (E\d+) essential")
            assert a["reachable"] == (cost is not None)
            assert a["shortest_cost"] == ("unreachable" if cost is None else str(cost))
            assert a["first_hop"] == hop
            assert a["within_budget"] == (cost is not None and cost <= budget)
            alternative, _ = _graph_oracle(r["state"], probe)
            assert a["edge_essential"] == (cost is not None and (alternative is None or alternative > cost))


def test_execution_tasks_scale_and_vary():
    for name, key, n in (("instruction_execution", "entities", 60), ("goal_directed_planning", "steps", 60),
                         ("event_triggered_execution", "rules", 60), ("graph_navigation", "nodes", 60)):
        levels = [at_level(name, level, n) for level in range(5)]
        sizes = [sum(len(r["state"][key]) for r in rs) / len(rs) for rs in levels]
        assert sizes == sorted(sizes) and len(set(sizes)) == 5, (name, sizes)
        for rs in levels:
            assert len({json.dumps(r["state"], sort_keys=True) for r in rs}) == len(rs), name
    top = lambda name, n: at_level(name, 4, n)
    assert any(labels(r)["resolution"] in ("schedule", "rule", "clarify") for r in top("instruction_execution", 60))
    assert any(s["requires_any"] for r in top("goal_directed_planning", 60) for s in r["state"]["steps"])
    assert any(e["kind"] == "control" for r in top("event_triggered_execution", 60) for e in r["state"]["events"])
    assert any(r["state"]["via"] for r in top("graph_navigation", 60))


# --------------------------------------------------------------------------- record_eligibility

def _kleene(expr, facts):
    """A second interpreter with independently expressed Kleene logic."""
    op = expr["op"]
    if op == "sum_le":
        operands = [facts.get(f) for f in expr["fields"]]
        return None if any(x is None for x in operands) else sum(operands) <= expr["value"]
    if op in ("eq", "ge", "le", "in"):
        candidate = facts.get(expr["field"])
        if candidate is None:
            return None
        return {"eq": lambda: candidate == expr["value"], "ge": lambda: candidate >= expr["value"],
                "le": lambda: candidate <= expr["value"], "in": lambda: candidate in expr["values"]}[op]()
    if op == "not":
        return {True: False, False: True, None: None}[_kleene(expr["arg"], facts)]
    if op == "implies":
        p, q = (_kleene(expr[k], facts) for k in ("if", "then"))
        return True if p is False or q is True else False if p is True and q is False else None
    values = [_kleene(child, facts) for child in expr["args"]]
    if op == "and":
        return False if any(v is False for v in values) else True if all(v is True for v in values) else None
    return True if any(v is True for v in values) else False if all(v is False for v in values) else None


def _classify(values):
    if any(value is False for value in values):
        return "ineligible"
    return "eligible" if all(value is True for value in values) else "undetermined"


def _atom(op, field, value):
    return {"op": op, "field": field, "value": value}


REQUIREMENTS = [  # (pattern, kind, expression from the matched groups), read off the requirement prose
    (r"The quoted base price must not exceed €(\d+)\.", "fee", lambda b: _atom("le", "fee", int(b))),
    (r"Only base prices of €(\d+) or less are acceptable\.", "fee", lambda b: _atom("le", "fee", int(b))),
    (r"The combined base price and additional charges must be at most €(\d+)\.", "total",
     lambda b: {"op": "sum_le", "fields": ["fee", "extras"], "value": int(b)}),
    (r"Availability must begin within (\d+) days\.", "lead", lambda b: _atom("le", "lead_days", int(b))),
    (r"Capacity must accommodate at least (\d+) people\.", "capacity", lambda b: _atom("ge", "capacity", int(b))),
    (r"The location must be in the (\w+) region(?: or the (\w+) region)?\.", "region",
     lambda *r: {"op": "in", "field": "region", "values": [x for x in r if x]}),
    (r"Exclude offers that require annual membership\.", "membership",
     lambda: {"op": "not", "arg": _atom("eq", "membership", True)}),
    (r"The provider must hold a current certification\.", "certified", lambda: _atom("eq", "certified", True)),
    (r"No mandatory deposit is permitted\.", "deposit", lambda: _atom("eq", "deposit", False)),
    (r"The published rating must be at least (\d+) out of 5\.", "rating", lambda b: _atom("ge", "rating", int(b))),
    (r"The start date must be on or before day (\d+) of the planning period\.", "start",
     lambda b: _atom("le", "start_day", int(b))),
    (r"Either in-person delivery, or remote delivery with onboarding included, is required\.", "mode",
     lambda: {"op": "or", "args": [_atom("eq", "mode", "in person"), {"op": "and", "args": [
         _atom("eq", "mode", "remote"), _atom("eq", "onboarding", True)]}]}),
    (r"If service is expedited, the response time must be no more than (\d+) hours\.", "conditional",
     lambda b: {"op": "implies", "if": _atom("eq", "expedited", True), "then": _atom("le", "response_hours", int(b))}),
    (r"Support must include either a dedicated help desk, or live chat with extended hours\.", "support",
     lambda: {"op": "or", "args": [_atom("eq", "desk_support", True), {"op": "and", "args": [
         _atom("eq", "chat_support", True), _atom("eq", "extended_hours", True)]}]}),
]
FILLER = {"The listing was refreshed after its last review.", "A reference code is available on request.",
          "It was entered into the catalogue this quarter.", "The offer carries an internal tracking number."}


def _fields(expr):
    if "field" in expr:
        return {expr["field"]}
    if "fields" in expr:
        return set(expr["fields"])
    return set().union(*(_fields(e) for e in [expr.get("arg"), expr.get("if"), expr.get("then"),
                                              *expr.get("args", [])] if e))


def _requirements(user_request):
    out = []
    for line in user_request.split("\n")[1:]:
        number, text = re.fullmatch(r"C(\d+)\. (.*)", line).groups()
        assert int(number) == len(out) + 1
        (kind, expr), = [(kind, build(*m.groups())) for pattern, kind, build in REQUIREMENTS
                         for m in [re.fullmatch(pattern, text)] if m]
        out.append({"kind": kind, "expr": expr})
    return out


@lru_cache(None)
def _sentence_parsers():
    """Every record sentence the stated vocabulary allows, as (regex, field, value or None to read {v})."""
    from reasoning_core.tasks.jev.record_eligibility import DESCRIPTIONS, NAMES, NEGATIVE
    parsers = []
    for field, patterns in DESCRIPTIONS.items():
        for pattern in patterns:
            regex = re.escape(pattern).replace(r"\{v\}", "(.+?)").replace(r"\{unit\}", "(?:day|days)")
            parsers.append((regex, field, None if "{v}" in pattern else True))
    parsers += [(re.escape(text), field, False) for field, text in NEGATIVE.items()]
    for field, name in NAMES.items():
        name = re.escape(name)
        parsers += [(rf"The listing does not specify {name}\.", field, "unknown"),
                    (rf"No information about {name} is provided\.", field, "unknown"),
                    (rf"The sources conflict about {name}: one reports .+; another reports .+\.", field, "unknown")]
    return parsers


def _facts(description):
    facts = {}
    for sentence in re.split(r"(?<=\.)\s+", description):
        if sentence in FILLER:
            continue
        hits = [(field, value, m) for regex, field, value in _sentence_parsers()
                for m in [re.fullmatch(regex, sentence)] if m]
        assert len(hits) == 1, (sentence, hits)
        field, value, m = hits[0]
        assert field not in facts, (field, description)
        facts[field] = None if value == "unknown" else _scalar(m.group(1)) if value is None else value
    return facts


def _eligibility(state):
    requirements = _requirements(state["user_request"])
    results = {}
    for record in state["records"]:
        facts = _facts(record["description"])
        for req in requirements:   # the prose states every fact a requirement reads, possibly as unknown
            assert _fields(req["expr"]) <= set(facts), (req, record["description"])
        results[record["id"]] = [_kleene(req["expr"], facts) for req in requirements]
    return requirements, results


def test_record_eligibility_truth_tables_from_prose():
    for level in range(5):
        for r in at_level("record_eligibility", level, 60):
            a = labels(r)
            requirements, results = _eligibility(r["state"])
            status = {rid: _classify(v) for rid, v in results.items()}
            probe, constraint = ask(r, "requirement_status", r"For (R\d+), is (C\d+) met")
            assert ask(r, "probe_eligibility", r"status of (R\d+)\?") == probe
            assert ask(r, "decisive_constraint", r"For (R\d+),") == probe
            assert ask(r, "eligible_if_relaxed", r"requirement (C\d+) is removed, is (R\d+)") == (constraint, probe)
            assert ask(r, "probe_fully_eligible", r"Is (R\d+) definitely") == probe
            values, selected = results[probe], int(constraint[1:]) - 1
            failures = [i for i, x in enumerate(values) if x is False]
            unknowns = [i for i, x in enumerate(values) if x is None]
            displayed = [rec["id"] for rec in r["state"]["records"]]
            assert a["probe_eligibility"] == status[probe]
            assert a["requirement_status"] == {True: "met", False: "violated", None: "unknown"}[values[selected]]
            assert a["eligible_count"] == min(sum(x == "eligible" for x in status.values()), 9)
            assert a["first_eligible"] == next((x for x in displayed if status[x] == "eligible"), "none")
            assert a["decisive_constraint"] == (f"C{(failures or unknowns)[0] + 1}" if failures or unknowns else "none")
            assert a["eligible_if_relaxed"] == (_classify([v for i, v in enumerate(values) if i != selected])
                                                == "eligible")
            assert a["probe_fully_eligible"] == (status[probe] == "eligible")


def test_record_eligibility_progression_and_no_shortcut():
    from reasoning_core.tasks.jev.record_eligibility import N_CONSTRAINTS
    mean_lengths, total_sizes = [], []
    for level in range(5):
        requests = at_level("record_eligibility", level, 60)
        assert len({json.dumps(r["state"], sort_keys=True) for r in requests}) == len(requests)
        assert len(Counter(labels(r)["eligible_count"] for r in requests)) >= 5
        kinds = [[q["kind"] for q in _requirements(r["state"]["user_request"])] for r in requests]
        assert all(len(k) == N_CONSTRAINTS[level] for k in kinds)
        total_sizes.append(sum(len(r["state"]["records"]) for r in requests) / len(requests))
        mean_lengths.append(sum(len(json.dumps(r["state"])) for r in requests) / len(requests))
        if level == 2:
            assert all({"mode", "support", "total"} & set(k) for k in kinds)
        if level >= 3:
            assert all("conditional" in k for k in kinds)
        if level == 4:   # the first requirement alone does not decide eligibility
            simple_first = 0
            for r in requests:
                _, results = _eligibility(r["state"])
                values = results[ask(r, "probe_eligibility", r"status of (R\d+)\?")]
                simple_first += (values[0] is True) == (_classify(values) == "eligible")
            assert simple_first / len(requests) < 0.7
    assert sorted(total_sizes) == total_sizes and sorted(mean_lengths) == mean_lengths


# --------------------------------------------------------------------------- multi_view_adjudication

def _intent(state):
    if any(state["billing"].values()):
        return "billing"
    account, telemetry = state["account"], state["telemetry"]
    failures = account["auth_failures"] if "auth_failures" in account else sum(
        e["kind"] == "login" and not e["ok"] for e in state["recent_events"])
    if account["active"] and (failures >= 2 or account["permission_mismatch"]):
        return "access"
    if telemetry["integration_failures"] >= 2 or telemetry["error_rate_percent"] >= 20:
        return "technical"
    return "other"


def _impact(workflow):
    down = {e["feature"] for e in workflow["affected_features"] if e["status"] == "down"}
    slow = {e["feature"] for e in workflow["affected_features"] if e["status"] == "slow"}
    if down & set(workflow["core_features"]) - set(workflow["workarounds"]):
        return 2
    return int(bool(down | slow))


def test_multi_view_gold_follows_stated_rules():
    for r in mixed("multi_view_adjudication", 200):
        state, a = r["state"], labels(r)
        timeline = state["timeline"]
        deadline = timeline["deadline_hours"] if "deadline_hours" in timeline else (
            None if timeline["due_hour"] is None else timeline["due_hour"] - timeline["now_hour"])
        assert a["intent"] == _intent(state)
        assert a["is_urgent"] == (timeline["executive_escalation"] or (deadline is not None and deadline <= 24))
        assert a["workflow_impact"] == _impact(state["workflow"])


# --------------------------------------------------------------------------- state_perturbation

def _risk(record, rule):
    return ((0 if record["authorized"] else rule["unauthorized_points"])
            + (rule["blocked_status_points"] if record["status"] == "blocked" else 0)
            + (rule["amount_threshold_points"] if record["amount"] >= rule["amount_threshold"] else 0)
            + (rule["unassigned_owner_points"] if record["owner"] == "unassigned" else 0))


def test_state_perturbation_gold_follows_risk_rule():
    for r in mixed("state_perturbation", 200):
        state, a = r["state"], labels(r)
        rule = state["risk_rule"]
        delta = sum(_risk(x, rule) for x in state["after"]) - sum(_risk(x, rule) for x in state["before"])
        assert a["risk_direction"] == (0 if delta < 0 else 2 if delta > 0 else 1)
        probe = ask(r, "changed_dimension", r"record (R\d+)")
        assert ask(r, "material_change", r"record (R\d+)") == probe
        before, after = ({x["id"]: x for x in state[k]}[probe] for k in ("before", "after"))
        fields = {"authorized": "authorization", "status": "status", "amount": "financial", "owner": "ownership"}
        changed = [fields[f] for f in fields if before[f] != after[f]] or ["none"]
        assert changed == [a["changed_dimension"]]
        assert a["material_change"] == (changed != ["none"])


# --------------------------------------------------------------------------- claim_support

def test_strongest_support_origin_is_not_constant():
    assert len({labels(r)["strongest_support_origin"] for r in mixed("claim_support", 200)}) > 3


# --------------------------------------------------------------------------- needle_retrieval

def test_needle_retrieval_gold_follows_records():
    for r in mixed("needle_retrieval", 300):
        a = labels(r)
        body, _, moves = r["state"].partition("\n\nReissued ")
        prose = re.findall(r"The \w+ ([A-Z]-\d{4}) has \w+ (\w+)\.", body)
        if prose:
            value = dict(prose)
            assert len(prose) == body.count(". ") + 1
        else:
            records = parse_records(body)
            field = next(k for k in records[0] if k != "id")
            value = {x["id"]: x[field] for x in records}
            assert len(value) == len(records)
        reissued = dict(re.findall(r"^([A-Z]-\d{4}) -> ([A-Z]-\d{4})$", moves, re.M))
        assert len(reissued) == moves.count(" -> ")
        assert not set(reissued) & set(value)   # a reissued id is never listed
        key = ask(r, "value_of_id", r"([A-Z]-\d{4})")
        assert ask(r, "id_has_value", r"([A-Z]-\d{4})") == key
        while key in reissued:
            key = reissued[key]
        assert a["value_of_id"] == value[key]
        assert a["id_has_value"] == (value[key] == ask(r, "id_has_value", r" (\w+)\?$"))
        assert a["id_listed"] == (ask(r, "id_listed", r"([A-Z]-\d{4})") in value)


# --------------------------------------------------------------------------- record_aggregation

def test_record_aggregation_gold_follows_items():
    from reasoning_core.tasks.jev.record_aggregation import CATEGORIES
    category_of = lambda text: [c for c in CATEGORIES if re.search(rf"\b{c}\b", text)]
    for r in mixed("record_aggregation", 300):
        a, items = labels(r), parse_records(r["state"])
        (category,) = category_of(r["questions"]["count_in_category"]["instructions"])
        for qid in ("any_out_of_stock", "total_above", *(["count_filtered"] if "count_filtered" in a else [])):
            assert category_of(r["questions"][qid]["instructions"]) == [category]
        members = [i for i in items if i["category"] == category]
        assert a["count_in_category"] == min(len(members), 9)
        if "count_filtered" in a:
            cut = int(ask(r, "count_filtered", r"(?:at least|is) (\d+)"))
            stock = "in stock" in r["questions"]["count_filtered"]["instructions"]
            hits = [i for i in members if i["quantity"] >= cut and (i["in_stock"] or not stock)]
            assert a["count_filtered"] == min(len(hits), 9)
        assert a["any_out_of_stock"] == any(not i["in_stock"] for i in members)
        threshold = int(ask(r, "total_above", r"than (\d+)"))
        assert a["total_above"] == (sum(i["quantity"] for i in members) > threshold)
        scope = category_of(r["questions"]["largest_quantity"]["instructions"])
        pool = [i for i in items if i["category"] in scope] if scope else items
        top = max(i["quantity"] for i in pool)
        assert [i["item"] for i in pool if i["quantity"] == top] == [a["largest_quantity"]]


# --------------------------------------------------------------------------- policy_under_uncertainty

SENSITIVITY = ["public", "internal", "restricted"]


def _uncertain_policy_answers(state):
    """Brute force from the rendered state: every (role, report outcomes) world, weighted and conditioned."""
    history = {plural[:-1]: int(n) for n, plural in re.findall(r"(\d+) by (\w+)", state["role_evidence"]["history"])}
    reports = [(r["says"], Fraction(*map(int, re.findall(r"\d+", r["reliability"]))))
               for r in state["role_evidence"]["reports"]]
    roles = list(history)
    joint = {}
    for role in roles:
        for outcomes in product(roles, repeat=len(reports)):
            weight = Fraction(history[role], sum(history.values()))
            for said, (_, reliability) in zip(outcomes, reports):
                weight *= reliability if said == role else (1 - reliability) / (len(roles) - 1)
            if list(outcomes) == [said for said, _ in reports]:
                joint[role] = joint.get(role, 0) + weight
    total = sum(joint.values())
    allowed, governing = Fraction(0), {}
    for role, weight in joint.items():
        request = state["request"]
        subject = {**request["subject"], "role": role}
        matching = [p for p in state["policies"] if role in p["roles"] and subject["team"] in p["teams"]
                    and subject["clearance"] >= p["min_clearance"] and request["action"] in p["actions"]
                    and SENSITIVITY.index(request["resource"]["sensitivity"]) <= SENSITIVITY.index(p["max_sensitivity"])]
        top = max(matching, key=lambda p: p["priority"]) if matching else None
        key = top["id"] if top else "none (default deny)"
        governing[key] = governing.get(key, 0) + weight / total
        allowed += weight / total if top and top["effect"] == "allow" else 0
    return {role: weight / total for role, weight in joint.items()}, governing, allowed


def test_uncertain_policy_gold_is_the_exact_posterior():
    errors, sharp = {"prior": [], "report": []}, 0
    requests = mixed("policy_under_uncertainty", 300)
    for r in requests:
        roles, governing, allowed = _uncertain_policy_answers(r["state"])
        q = r["questions"]
        assert q["access_allowed"]["label"] == (allowed > Fraction(1, 2))
        assert q["access_allowed"]["target"]["true"] == pytest.approx(float(allowed), abs=1e-5)
        sharp += allowed in (0, 1)
        for qid, exact in (("requester_role", roles), ("governing_policy", governing)):
            assert q[qid]["label"] == max(exact, key=exact.get)
            for option, p in q[qid]["target"].items():
                assert p == pytest.approx(float(exact.get(option, 0)), abs=1e-5)
        # plugging a single role in, the most common one or the first report's, is clearly worse
        history = {plural[:-1]: int(n) for n, plural in
                   re.findall(r"(\d+) by (\w+)", r["state"]["role_evidence"]["history"])}
        for name, role in (("prior", max(history, key=history.get)),
                           ("report", r["state"]["role_evidence"]["reports"][0]["says"])):
            plugged = _uncertain_policy_answers({**r["state"], "role_evidence": {
                "history": f"1 by {role}s", "reports": []}})[2]
            errors[name].append(abs(float(plugged) - float(allowed)))
    assert sum(errors["prior"]) / len(requests) > 0.1
    assert sum(errors["report"]) / len(requests) > 0.05
    assert 40 < sharp < 150   # the role is irrelevant in some problems, not most


# --------------------------------------------------------------------------- table_lookup

def test_table_lookup_gold_follows_tables():
    for r in mixed("table_lookup", 300):
        a, state = labels(r), r["state"]
        if state.startswith("{"):
            tables = json.loads(state)
        else:
            people, teams = re.fullmatch(r"people:\n(.*)\n\nteams:\n(.*)", state, re.S).groups()
            tables = {"people": parse_records(people), "teams": parse_records(teams)}
        people = {p["name"]: p for p in tables["people"]}
        managers = {t["team"]: t["manager"] for t in tables["teams"]}
        text = r["questions"]["find_person"]["instructions"]
        m = (re.fullmatch(r"Who is on (?P<team>.+) and based in (?P<city>\w+)(?: and started before (?P<cut>\d+))?\?", text)
             or re.fullmatch(r"Which person works in (?P<city>\w+) on (?P<team>.+?)(?: and started before (?P<cut>\d+))?\?",
                             text))
        by_manager = re.fullmatch(r"the team managed by (\w+)", m["team"])
        team = {v: k for k, v in managers.items()}[by_manager[1]] if by_manager else \
            re.fullmatch(r"the (\w+) team", m["team"])[1]
        matching = [p["name"] for p in people.values() if (p["team"], p["city"]) == (team, m["city"])
                    and (m["cut"] is None or p["start_year"] < int(m["cut"]))]
        assert matching == [a["find_person"]]
        subject = ask(r, "manager_of", r"(?:team that|manager of) (\w+)")
        assert a["manager_of"] == managers[people[subject]["team"]]
        name, year = ask(r, "started_before", r"(?:Did|Is) (\w+?)(?:'s start year earlier than| start before) (\d+)")
        assert a["started_before"] == (people[name]["start_year"] < int(year))
        city, since = ask(r, "count_matching", r"in (\w+) (?:started in|whose start year is) (\d+)")
        assert a["count_matching"] == sum(p["city"] == city and p["start_year"] >= int(since) for p in people.values())


# --------------------------------------------------------------------------- entity_belief_tracking

def test_entity_beliefs_replay_events():
    nested_differs = 0
    for r in mixed("entity_belief_tracking", 300):
        a, state = labels(r), r["state"]
        obj = ask(r, "world_location", r"Where is (item_\d+)")
        agent, believed_obj = ask(r, "agent_belief_location", r"Where does (\w+) believe (item_\d+)")
        assert believed_obj == obj
        other = None
        if "nested_belief_location" in a:
            first, other, nested_obj = ask(r, "nested_belief_location", r"where does (\w+) think (\w+) believes (item_\d+)")
            assert (first, nested_obj) == (agent, obj)
        world = believed = thinks = state["initial_locations"][obj]
        for event in sorted((e for e in state["events"] if e["object"] == obj), key=lambda e: e["step"]):
            world = event["destination"]
            if agent in event["witnesses"]:
                believed = world
                if other in event["witnesses"]:
                    thinks = world
        assert a["world_location"] == world
        assert a["agent_belief_location"] == believed
        assert a["belief_matches_world"] == (world == believed)
        if other:
            assert a["nested_belief_location"] == thinks
            nested_differs += thinks != believed
    assert nested_differs > 20   # the second-order question is not the first-order one


# --------------------------------------------------------------------------- event_state_reconstruction

def test_event_log_replay():
    voids, names = 0, ["routine", "degraded", "critical"]
    for r in mixed("event_state_reconstruction", 300):
        state, a = r["state"], labels(r)
        voided = {e["voids_ts"] for e in state["events"] if e["kind"] == "void"}
        voids += bool(voided)
        current = dict(state["initial_state"])
        for event in sorted(state["events"], key=lambda e: e["ts"]):
            if event["ts"] in voided:
                continue
            current.update({"assign": {"owner": event.get("owner")}, "severity": {"severity": event.get("severity")},
                            "resolve": {"open": False}, "reopen": {"open": True}}.get(event["kind"], {}))
        assert a["current_owner"] == current["owner"]
        assert a["is_open"] == current["open"]
        assert a["current_severity"] == names.index(current["severity"])
        assert r["questions"]["current_severity"]["criteria"][a["current_severity"]].startswith(current["severity"])
    assert voids > 20


# --------------------------------------------------------------------------- taxonomy_routing

def _condition(text):
    m = re.fullmatch(r"(amount|age days) (above|at most) (\d+)", text)
    if m:
        return m[1].replace(" ", "_"), {"above": "gt", "at most": "le"}[m[2]], int(m[3])
    field, value = re.fullmatch(r"(\w+) is (\S+)", text).groups()
    return field, "eq", value


def _holds(condition, ticket):
    field, op, value = condition
    return ticket[field] == value if op == "eq" else ticket[field] > value if op == "gt" else ticket[field] <= value


def test_taxonomy_routing_gold_follows_rules():
    first_hit = []
    requests = mixed("taxonomy_routing", 300)
    for r in requests:
        a = labels(r)
        guide, ticket_text = re.fullmatch(r"Routing guide[^\n]*\n(.*)\n\nTicket: (.*)", r["state"], re.S).groups()
        ticket = {k.replace(" ", "_"): _scalar(v) for k, v in (part.split(": ") for part in ticket_text.split("; "))}
        rules = {row["category"]: [_condition(c) for c in row["rule"].split(" and ")] for row in parse_records(guide)}
        meets = [name for name, rule in rules.items() if all(_holds(c, ticket) for c in rule)]
        assert meets == [a["route"]]
        probe = ask(r, "belongs_to", r"([a-z]+/[a-z-]+)\?")
        assert ask(r, "conditions_met", r"([a-z]+/[a-z-]+)") == probe
        assert a["belongs_to"] == (probe == meets[0])
        assert a["conditions_met"] == sum(_holds(c, ticket) for c in rules[probe])
        assert all(len(rule) < len(r["questions"]["conditions_met"]["criteria"]) for rule in rules.values())
        # routing on a rule's first condition alone is a shortcut that must not work
        first_hit.append(next(n for n, rule in rules.items() if _holds(rule[0], ticket)) == meets[0])
    assert sum(first_hit) / len(requests) < 0.5


# --------------------------------------------------------------------------- practical_arithmetic

def _money(text):
    return int(re.fullmatch(r"[$€£](-?\d+)", text)[1])


def _minutes(text):
    h, m = map(int, text.split(":"))
    return 60 * h + m


def _duration(text):
    m = re.fullmatch(r"(?:(\d+) h)? ?(?:(\d+) min)?", text)
    return 60 * int(m[1] or 0) + int(m[2] or 0)


def _order(state):
    if state.startswith("{"):
        data = json.loads(state)
        lines, rule = data["lines"], data["rule"]
    elif state.startswith("Order: "):
        body, rule = re.fullmatch(r"Order: (.*)\nRule: (.*)", state).groups()
        lines = [{"item": i, "quantity": int(q), "unit_price": _money(p)}
                 for q, i, p in re.findall(r"(\d+) x (\w+) at (\S+) each\.", body)]
        lines += [{"item": i, "quantity": int(q), "unit_price": _money(p)}
                  for i, q, p in re.findall(r"(\w+): (\d+) units at (\S+) per unit\.", body)]
        order = re.findall(r"(\w+)(?: at |: \d+ units)", body)   # restore the listed order of the lines
        lines.sort(key=lambda l: order.index(l["item"]))
    else:
        table, rule = re.fullmatch(r"Order lines \(prices in .\):\n(.*)\n\nRule: (.*)", state, re.S).groups()
        lines = parse_records(table)
    threshold, discount, shipping = map(_money, re.fullmatch(
        r"Orders of (\S+) or more get (\S+) off; smaller orders pay (\S+) shipping\.", rule).groups())
    cost = [l["unit_price"] * l["quantity"] for l in lines]
    total = sum(cost)
    due = total - discount if total >= threshold else total + shipping
    assert cost.count(max(cost)) == 1
    expected = {"amount_due": due, "largest_line": lines[cost.index(max(cost))]["item"]}
    return expected, cost, lines, due


def _ledger(state):
    if state.startswith("{"):
        data = json.loads(state)
        start, transactions = data["opening_balance"], data["transactions"]
    elif state.startswith("The account"):
        start = _money(re.match(r"The account opens the month at (\S+)\.", state)[1])
        transactions = [{"day": int(d), "type": t, "amount": _money(x)} for d, t, x in
                        re.findall(r"[Dd]ay (\d+)(?:,|:) a? ?(deposit|withdrawal) of (\S+?)\.(?: |$)", state)]
    else:
        opening, table = re.fullmatch(r"Opening balance: (\S+)\n(.*)", state, re.S).groups()
        start, transactions = _money(opening), parse_records(table)
    balance, balances = start, []
    for t in transactions:
        balance += t["amount"] if t["type"] == "deposit" else -t["amount"]
        balances.append(balance)
    return start, transactions, balances


def _schedule(state):
    m = re.fullmatch(r"Starting at (\d\d:\d\d): (.*)\. (Tasks run .*)", state, re.S)
    if m:
        start, body, rule = m.groups()
        tasks = [(t, _duration(d)) for t, d in re.findall(r"([\w ]+?) \(([^)]+)\)(?:, then |$)", body)]
    else:
        start, table, rule = re.fullmatch(r"Start: (\d\d:\d\d)\n(.*)\n\n(Tasks run .*)", state, re.S).groups()
        tasks = [(row["task"], _duration(str(row["duration"]))) for row in parse_records(table)]
    gap = re.search(r"with a (\d+)-minute break", rule)
    return _minutes(start), tasks, int(gap[1]) if gap else 0


def test_practical_arithmetic_gold_follows_state():
    sizes, ranks = Counter(), Counter()
    for r in mixed("practical_arithmetic", 450):
        a, q, state = labels(r), r["questions"], r["state"]
        sizes[len(a)] += 1
        probabilities = {}
        if "amount_due" in a:
            expected, cost, lines, due = _order(state)
            expected["lines_above"] = sum(c > _money(ask(r, "lines_above", r"(?:than|exceeds) (\S+?)(?: in total)?[?.]$"))
                                          for c in cost)
            units = int(ask(r, "random_line_bulk", r"(?:at least|order) (\d+)")) if "random_line_bulk" in a else 0
            probabilities["random_line_bulk"] = sum(l["quantity"] >= units for l in lines) / len(lines)
            if "within_budget" in a:
                expected["within_budget"] = due <= _money(ask(r, "within_budget", r"(?:at most|budget of) (\S+?)\?"))
            else:
                budget = _money(ask(r, "budget_use", r"(?:budget of|Against a) (\S+?)(?:\?| budget)"))
                expected["budget_use"] = 2 if due > budget else 0 if 2 * due <= budget else 1
            numeric, fmt = "amount_due", lambda v: re.sub(r"\d+", str(v), q["amount_due"]["label"])
        elif "went_negative" in a:
            start, transactions, balances = _ledger(state)
            final, n = balances[-1], len(transactions)
            deposits, change = sum(t["type"] == "deposit" for t in transactions), balances[-1] - start
            expected = {"went_negative": min(balances) < 0, "withdrawal_count": n - deposits,
                        "net_change": 0 if change < -50 else 2 if change > 50 else 1}
            probabilities["random_is_deposit"] = deposits / n
            lows = [f"day {t['day']}" for t, b in zip(transactions, balances) if b == min(balances)]
            assert ("lowest_day" in a) == (len(lows) == 1)   # asked only when the minimum is unique
            assert ("final_balance" in a) == (final >= 0)
            if len(lows) == 1:
                expected["lowest_day"] = lows[0]
            expected["final_balance"] = final
            sym = state[state.index("$") if "$" in state else state.index("€") if "€" in state else state.index("£")]
            numeric, fmt = "final_balance", lambda v: f"{sym}{v}"
        else:
            start, tasks, gap = _schedule(state)
            starts, clock = [], start
            for _, minutes in tasks:
                starts.append(clock)
                clock += minutes + gap
            finish, durations = clock - gap, [m for _, m in tasks]
            assert durations.count(max(durations)) == 1
            long = int(ask(r, "random_is_long", r"(?:more|longer) than (\d+) minutes")) if "random_is_long" in a else 0
            probabilities["random_is_long"] = sum(m > long for m in durations) / len(durations)
            expected = {"done_by_deadline": finish <= _minutes(ask(r, "done_by_deadline", r"(\d\d:\d\d)\?")),
                        "longest_task": tasks[durations.index(max(durations))][0],
                        "starts_before_noon": sum(s < 720 for s in starts), "finish_time": finish}
            numeric, fmt = "finish_time", lambda v: f"{v // 60 % 24:02d}:{v % 60:02d}"
        for qid, p in probabilities.items():   # k-out-of-n events, asked only when not too close to call
            if qid in a:
                assert abs(p - 0.5) >= 0.1 and a[qid] == (p > 0.5), (qid, p)
                assert q[qid]["target"]["true"] == pytest.approx(p, abs=1e-6)
        for qid, label in a.items():
            if qid in probabilities:
                continue
            assert label == (fmt(expected[qid]) if qid == numeric else expected[qid]), (qid, state)
            if qid == numeric:
                assert len(q[qid]["criteria"]) == 5
                ranks[sorted(q[qid]["criteria"], key=lambda o: (len(o), o)).index(label)] += 1
    assert len(sizes) >= 3   # partial question sets: some questions are asked only when well defined
    assert len(ranks) == 5 and min(ranks.values()) > max(ranks.values()) / 2   # gold rank is not a tell


# --------------------------------------------------------------------------- option counts and wording

@pytest.mark.parametrize("name, qid, low, high", [("needle_retrieval", "value_of_id", 6, 20),
                                                  ("table_lookup", "find_person", 5, 30),
                                                  ("entity_belief_tracking", "world_location", 4, 16),
                                                  ("taxonomy_routing", "route", 4, 50)])
def test_option_counts_vary(name, qid, low, high):
    sizes = Counter(len(r["questions"][qid]["criteria"]) for r in mixed(name, 300))
    assert min(sizes) <= low and max(sizes) >= high
    assert max(sizes.values()) / 300 < 0.35, sizes   # no single count dominates


@pytest.mark.parametrize("name", ["needle_retrieval", "record_aggregation", "table_lookup"])
def test_rendered_tasks_vary_wording(name):
    requests = mixed(name, 100)
    for qid in {qid for r in requests for qid in r["questions"]}:   # some questions are asked from a level on
        wordings = {tuple(r["questions"][qid]["instructions"].split()[:2]) for r in requests if qid in r["questions"]}
        assert len(wordings) > 1, qid
