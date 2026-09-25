import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class UniformTestDominanceConfig(Config):
    n_alternatives: int = 2
    m_rules: int = 2
    alpha_range: tuple = (0.02, 0.08)
    size_range: tuple = (0.01, 0.20)

    def apply_difficulty(self, level):
        self.n_alternatives = 2 + (level // 2)
        self.m_rules = 3 + (level // 2)
        self.alpha_range = (0.06, 0.12)
        self.size_range = (0.005, 0.15)


def _strict_dominates(pa, pb):
    """True if power vector pa >= pb coordinatewise with at least one strict gain."""
    if not all(a >= b for a, b in zip(pa, pb)):
        return False
    return any(a > b for a, b in zip(pa, pb))


def _non_dominated_ids(valid):
    ids = [r["id"] for r in valid]
    non = []
    for r in valid:
        dominated = False
        for q in valid:
            if q["id"] == r["id"]:
                continue
            if _strict_dominates(q["powers"], r["powers"]):
                dominated = True
                break
        if not dominated:
            non.append(r["id"])
    non.sort()
    return non


def _format_answer(ids):
    return "[" + ", ".join(str(i) for i in ids) + "]"


def _parse_answer(text):
    if text is None:
        return None
    stripped = text.strip()
    if stripped == "":
        return None
    t = stripped.replace("[", "").replace("]", "").strip()
    if not t:
        return []
    try:
        ids = [int(x.strip()) for x in t.split(",") if x.strip()]
    except ValueError:
        return None
    return sorted(ids)


def _score_answer(answer, gold_list):
    cand = _parse_answer(answer)
    if cand is None:
        return 0.0
    if cand == gold_list:
        return 1.0
    return 0.0


class UniformTestDominance(Task):
    summary = "Compare candidate rejection rules across finite null and alternative families, including randomized decisions; filter size-valid rules and return power-dominance relations or a uniformly best rule if one exists."
    design_choice = "return a compact canonical string listing all non-dominated rules as an ordered list of rule IDs, with no dominance relations if none exist."
    config_cls = UniformTestDominanceConfig
    task_version = 2

    def generate_entry(self):
        m = self.config.n_alternatives
        M = self.config.m_rules
        a_lo, a_hi = self.config.alpha_range
        s_lo, s_hi = self.config.size_range
        alpha = random.uniform(a_lo, a_hi)

        rules = []
        for r in range(M):
            size = random.uniform(s_lo, s_hi)
            base = max(size, 0.30)
            powers = sorted(random.uniform(base, 1.0) for _ in range(m))
            powers = [round(p, 3) for p in powers]
            for p in powers:
                assert s_lo - 1e-9 <= p <= 1.0 + 1e-9
                assert p >= size - 1e-9
            rules.append({"id": r, "size": round(size, 3), "powers": powers})

        valid = [r for r in rules if r["size"] <= alpha + 1e-9]
        non = _non_dominated_ids(valid)
        answer = _format_answer(non)

        metadata = {
            "rules": rules,
            "alpha": round(alpha, 3),
            "n_alternatives": m,
            "valid_ids": [r["id"] for r in valid],
            "answer": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = [
            "A hypothesis test of a null against an alternative family of "
            f"{metadata['n_alternatives']} parameter values uses candidate decision "
            "(possibly randomized) rules. Each rule's size is its chance of rejecting "
            "under the null, and its power is its chance of rejecting at each "
            "alternative (alternatives indexed 1..m, non-decreasing). Size-valid means "
            f"size <= alpha = {metadata['alpha']}. Rule A strictly dominates rule B if "
            "every power of A is >= the corresponding power of B and at least one is >. "
            "A size-valid rule is non-dominated if no other size-valid rule strictly "
            "dominates it.",
        ]
        header = "  rule | size | powers"
        lines.append(header)
        for r in metadata["rules"]:
            ps = ", ".join(str(p) for p in r["powers"])
            lines.append(f"    {r['id']}   | {r['size']:>5} | {ps}")
        lines.append(
            "List the IDs of the non-dominated size-valid rules as a sorted bracket "
            "list, e.g. [0, 2]. If every size-valid rule is dominated (no non-dominated "
            "ones exist), answer []. "
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        return _score_answer(answer, _parse_answer(entry.metadata["answer"]))


TASK_META = {'parent_source_id': None,
 'idea': 'uniform_test_dominance (variant 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scientific_reasoning_r4/uniform_test_dominance',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3867019559,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
