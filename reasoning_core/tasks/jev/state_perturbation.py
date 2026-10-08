"""Compare minimally edited records: semantic change, changed dimension, and risk direction under an additive rule.

Levels add records and simultaneous changes (whose risk effects can offset), amounts near the threshold, and
look-alike fields that change without being material. Ported from tasksource.jev.procedural.state_perturbation;
its level tables stop at 4.
"""
import random
from dataclasses import dataclass

from reasoning_core.decision import Decision
from reasoning_core.template import Config, Entry, Task

DIMENSIONS = ["authorization", "status", "financial", "ownership", "none"]
RISK = ["Lower operational risk than before.", "No material risk change.", "Higher operational risk than before."]
RISK_RULE = {
    "unauthorized_points": 3,
    "blocked_status_points": 2,
    "amount_threshold": 500,
    "amount_threshold_points": 1,
    "unassigned_owner_points": 1,
    "otherwise_points": 0,
    "direction": "Add the applicable points over all records. Compare after with before: lower total means lower "
                 "risk, equal means no material risk change, and higher total means higher risk.",
}
MATERIAL = "Material fields are authorized, status, amount, and owner; every other field is non-material."
STATUSES = ["open", "blocked", "resolved"]
OWNERS = ["alice", "bob", "unassigned"]
NOTES = ["routine", "reviewed", "imported"]
N_RECORDS = [1, 2, 4, 6, 8]
N_CHANGED = [1, 1, 2, 3, 4]


def _risk(record):
    return ((0 if record["authorized"] else RISK_RULE["unauthorized_points"])
            + RISK_RULE["blocked_status_points"] * (record["status"] == "blocked")
            + RISK_RULE["amount_threshold_points"] * (record["amount"] >= RISK_RULE["amount_threshold"])
            + RISK_RULE["unassigned_owner_points"] * (record["owner"] == "unassigned"))


def _amounts(level):
    return [100, 250, 500, 900] if level < 2 else [100, 900, *range(450, 560, 10)]


def _record(rng, level, i):
    record = {"id": f"R{i+1}", "authorized": rng.choice([True, False]), "status": rng.choice(STATUSES),
              "amount": rng.choice(_amounts(level)), "owner": rng.choice(OWNERS), "note": rng.choice(NOTES)}
    if level >= 2:  # look-alike, non-material fields
        record.update(status_note=rng.choice(STATUSES), amount_quoted=rng.choice(_amounts(level)),
                      previous_owner=rng.choice(OWNERS))
    return record


def _change(rng, level, record, dimension):
    other = lambda values, current: rng.choice([x for x in values if x != current])
    after = dict(record)
    if dimension == "authorization":
        after["authorized"] = not record["authorized"]
    elif dimension == "status":
        after["status"] = other(STATUSES, record["status"])
    elif dimension == "financial":
        after["amount"] = other(sorted(set(_amounts(level))), record["amount"])
    elif dimension == "ownership":
        after["owner"] = other(OWNERS, record["owner"])
    pools = {"note": NOTES, "status_note": STATUSES, "amount_quoted": list(range(450, 560, 10)),
             "previous_owner": OWNERS}
    decoys = [f for f in pools if f in record]
    for field in rng.sample(decoys, rng.randint(1 if dimension == "none" else 0, min(len(decoys), level + 1))):
        after[field] = other(pools[field], record[field])
    return after


@dataclass
class StatePerturbationConfig(Config):
    def apply_difficulty(self, level):
        pass  # the generator reads the level


class StatePerturbation(Task):
    summary = "Diff before/after records for material changes and the direction of an additive risk score."
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or StatePerturbationConfig())

    def generate_entry(self, state_seed=None, question=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, level = random.Random(state_seed), min(self.config.level, 4)
        n = N_RECORDS[level]
        before = [_record(rng, level, i) for i in range(n)]
        changed = set(rng.sample(range(n), min(n, N_CHANGED[level])))
        if n == 1 and rng.random() < 0.2:
            changed = set()
        dimensions = [rng.choice(DIMENSIONS[:-1]) if i in changed else "none" for i in range(n)]
        after = [_change(rng, level, record, dimension) for record, dimension in zip(before, dimensions)]
        unchanged = [i for i in range(n) if i not in changed]
        probe = (rng.choice(sorted(changed)) if changed and (not unchanged or rng.random() < 0.5)
                 else rng.choice(unchanged or [0]))
        delta = sum(map(_risk, after)) - sum(map(_risk, before))
        record_id = before[probe]["id"]
        state = {"before": before, "after": after, "materiality": MATERIAL, "risk_rule": RISK_RULE}
        questions = {
            "material_change": Decision(dimensions[probe] != "none", type="noul",
                                        instructions=f"Did any material field of record {record_id} change?"),
            "changed_dimension": Decision(dimensions[probe], criteria=dict.fromkeys(DIMENSIONS), instructions=
                f"Which material dimension of record {record_id} changed? Choose none when only non-material "
                "fields changed."),
            "risk_direction": Decision((delta > 0) - (delta < 0) + 1, type="score", criteria=RISK, instructions=
                "Following the risk rule, how did total operational risk change from before to after?"),
        }
        qid = question or random.choice(sorted(questions))
        return Entry({"payload": state, "state_seed": state_seed, "question_id": qid}, questions[qid])
