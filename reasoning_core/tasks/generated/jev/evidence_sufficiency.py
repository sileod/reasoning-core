import json
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround
from reasoning_core.tasks.generated.jev._common import canonical_json, choice_answer, jev_prompt, json_score, noul_answer


@dataclass
class JevEvidenceSufficiencyConfig(Config):
    n_evidence: int = 6
    n_origins: int = 4

    def apply_difficulty(self, level):
        self.n_evidence = sround(self.n_evidence + 1.4 * level)
        self.n_origins = sround(self.n_origins + 0.6 * level)


class JevEvidenceSufficiency(Task):
    summary = "Judge support, conflict, and decisive provenance from duplicated, invalid, contradictory, and irrelevant evidence in a Jev request."
    config_cls = JevEvidenceSufficiencyConfig

    def generate_entry(self):
        n_origins = max(3, self.config.n_origins)
        origins = [f"S{i+1}" for i in range(n_origins)]
        evidence = []
        roles = ["support", "support", "contradict", "irrelevant"]
        for i in range(max(4, self.config.n_evidence)):
            origin = random.choice(origins)
            role = random.choice(roles)
            valid = random.random() < 0.8
            reliability = random.choice([1, 2, 3])
            evidence.append({"id": f"E{i+1}", "origin": origin, "role": role, "valid": valid, "reliability": reliability})
        evidence[0].update(origin=origins[0], role="support", valid=True, reliability=3)
        valid_support = {}
        valid_contradict = set()
        for item in evidence:
            if not item["valid"]:
                continue
            if item["role"] == "support":
                valid_support[item["origin"]] = max(valid_support.get(item["origin"], 0), item["reliability"])
            elif item["role"] == "contradict":
                valid_contradict.add(item["origin"])
        supported = len(valid_support) >= 2 and not valid_contradict
        conflict = bool(valid_support and valid_contradict)
        decisive = "none"
        if valid_support:
            decisive = min(valid_support, key=lambda origin: (-valid_support[origin], origin))
        options = origins + ["none"]
        state = {
            "claim": "The deployment is sufficiently supported as the cause of the incident.",
            "rule": "Support is sufficient only with at least two independent valid supporting origins and no valid contradictory origin. Duplicates from one origin count once.",
            "evidence": evidence,
        }
        questions = {
            "claim_supported": {"type": "noul", "instructions": "Under state.rule, is the claim sufficiently supported?"},
            "has_conflict": {"type": "noul", "instructions": "Is there at least one valid supporting origin and at least one valid contradictory origin?"},
            "strongest_support_origin": {
                "type": "choice",
                "instructions": "Which valid supporting origin has the highest reliability? Break ties lexicographically; choose none if there is no valid support.",
                "criteria": {option: option for option in options},
            },
        }
        answers = {
            "claim_supported": noul_answer(supported),
            "has_conflict": noul_answer(conflict),
            "strongest_support_origin": choice_answer(decisive, options),
        }
        return Entry(metadata=edict(state=state, questions=questions), answer=canonical_json(answers))

    def render_prompt(self, m):
        return jev_prompt(m.state, m.questions)

    def score_answer(self, answer, entry):
        return json_score(answer, entry)

    def balancing_key(self, problem):
        a = json.loads(problem.answer)
        return int(a["claim_supported"]["noul"]), int(a["has_conflict"]["noul"])
