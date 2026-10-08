"""Judge support, conflict, and decisive provenance from duplicated, invalid, and contradictory evidence.

Levels add evidence and origins (with lexicographic tie-breaks past S9), then retractions (level 2), mirrored
origins that are not independent (level 3), and validity decided by a collection-day cutoff instead of a flag
(level 4). Ported from tasksource.jev.procedural.evidence_sufficiency (renamed: a generated task owns that name);
its level tables stop at 4.
"""
import random
from dataclasses import dataclass

from reasoning_core.decision import Decision
from reasoning_core.template import Config, Entry, Task, stochastic_rounding as sround

N_EVIDENCE = [4, 6, 9, 12, 16]
N_ORIGINS = [3, 4, 5, 7, 11]


@dataclass
class ClaimSupportConfig(Config):
    def apply_difficulty(self, level):
        pass  # the generator reads the level


class ClaimSupport(Task):
    summary = "Judge whether evidence suffices, conflicts, and which origin is decisive, under stated validity rules."
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or ClaimSupportConfig())

    def generate_entry(self, state_seed=None, question=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, level = random.Random(state_seed), min(self.config.level, 4)
        origins = [f"S{i+1}" for i in range(N_ORIGINS[level])]
        evidence = []
        for i in range(max(4, sround(N_EVIDENCE[level] * rng.uniform(0.85, 1.15), seed=rng.random()))):
            evidence.append({
                "id": f"E{i+1}",
                "origin": rng.choice(origins),
                "role": rng.choice(["support", "support", "contradict", "irrelevant"]),
                "valid": rng.random() < 0.8,
                "reliability": rng.choice([1, 2, 3]),
            })
        if rng.random() < 0.85:  # usually guarantee one valid support, without fixing its origin
            evidence[0].update(origin=rng.choice(origins), role="support", valid=True)

        rules = ["Support is sufficient only with at least two independent valid supporting origins and no valid "
                 "contradictory origin. Duplicates from one origin count once."]
        cutoff = None
        if level >= 4:  # validity is derived from the collection day
            cutoff = rng.randint(5, 10)
            for item in evidence:
                item["day"] = rng.randint(cutoff, 15) if item.pop("valid") else rng.randint(1, cutoff - 1)
            rules.append(f"Evidence is valid only if collected on day {cutoff} or later.")
        else:
            rules.append("Evidence with valid=false is invalid.")
        retracted = set()
        if level >= 2:
            targets = rng.sample(evidence, min(len(evidence), rng.randint(1, level)))
            for item in targets:
                retracted.add(item["id"])
                evidence.append({"id": f"E{len(evidence)+1}", "origin": rng.choice(origins), "role": "retraction",
                                 "retracts": item["id"], **({"day": rng.randint(1, 15)} if cutoff else {"valid": True})})
            rules.append("A retraction makes the evidence it names invalid, whatever the retraction's own validity; "
                         "retractions neither support nor contradict.")
        mirrors = {}
        if level >= 3:
            for copy, source in zip(*[iter(rng.sample(origins, 2 * rng.randint(1, 2)))] * 2):
                mirrors[copy] = source
            rules.append("A mirrored origin republishes its source and is not independent of it.")
        rules.append("Break reliability ties by the origin names in lexicographic (string) order.")

        def valid(item):
            ok = item["day"] >= cutoff if cutoff else item["valid"]
            return ok and item["id"] not in retracted

        valid_support, valid_contradict = {}, set()
        for item in evidence:
            if not valid(item):
                continue
            if item["role"] == "support":
                valid_support[item["origin"]] = max(valid_support.get(item["origin"], 0), item["reliability"])
            elif item["role"] == "contradict":
                valid_contradict.add(item["origin"])
        independent = {mirrors.get(origin, origin) for origin in valid_support}
        supported = len(independent) >= 2 and not valid_contradict
        conflict = bool(valid_support and valid_contradict)
        decisive = min(valid_support, key=lambda o: (-valid_support[o], o)) if valid_support else "none"
        state = {
            "claim": "The deployment is sufficiently supported as the cause of the incident.",
            "rules": rules,
            **({"mirrored_origins": [{"origin": c, "mirrors": s} for c, s in mirrors.items()]} if mirrors else {}),
            "evidence": evidence,
        }
        questions = {
            "claim_supported": Decision(supported, type="noul", instructions=
                                        "Following the stated rules, is the claim sufficiently supported?"),
            "has_conflict": Decision(conflict, type="noul", instructions=
                "Is there at least one valid supporting origin and at least one valid contradictory origin?"),
            "strongest_support_origin": Decision(decisive, criteria=dict.fromkeys(origins + ["none"]), instructions=
                "Which origin of valid supporting evidence has the highest reliability? Break ties "
                "lexicographically; choose none if there is no valid support."),
        }
        qid = question or random.choice(sorted(questions))
        return Entry({"payload": state, "state_seed": state_seed, "question_id": qid}, questions[qid])
