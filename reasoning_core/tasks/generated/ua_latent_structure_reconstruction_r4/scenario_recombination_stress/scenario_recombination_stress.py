import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'scenario_recombination_stress (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_latent_structure_reconstruction_r4/scenario_recombination_stress',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = ("Represent each scenario as a sequence of loads over time steps; the worst cumulative load is "
                 "the maximum prefix sum over any recombined sequence, and the answer is that maximum integer.")


def _max_prefix_sum(seq):
    best = 0
    cur = 0
    for x in seq:
        cur += x
        if cur > best:
            best = cur
    return best


def _min_prefix_sum(seq):
    best = 0
    cur = 0
    for x in seq:
        cur += x
        if cur < best:
            best = cur
    return best


def _subject(p0, p1):
    e1 = _max_prefix_sum(p0)
    e2 = _max_prefix_sum(p0 + p1)
    return max(e1, e2)


def _safe(p0, p1):
    e1 = _min_prefix_sum(p0)
    e2 = _min_prefix_sum(p0 + p1)
    return min(e1, e2)


def _checkpoint_adversary(p0, p1, a, b, history):
    cands = []
    for split in range(1, a):
        for bsplit in range(1, b):
            q0 = p0[:split] + p1[:bsplit]
            q1 = p0[split:] + p1[bsplit:]
            if _subject(q0, q1) > history:
                cands.append((_subject(q0, q1), q0, q1))
    for split in range(1, a):
        for bsplit in range(1, b):
            q0 = p1[:bsplit] + p0[:split]
            q1 = p1[bsplit:] + p0[split:]
            if _subject(q0, q1) > history:
                cands.append((_subject(q0, q1), q0, q1))
    return cands


def _try_switch_whole(p0, p1, history):
    if _subject(p1, p0) > history:
        return (_subject(p1, p0), p1, p0)
    return None


@dataclass
class ScenarioConfig(Config):
    length: int = 4
    n_checks: int = 1
    history: int = 4
    n_steps: int = 3

    def apply_difficulty(self, level):
        self.length = 3 + level
        self.n_checks = 1 + level // 2
        self.history = 3 + level
        self.n_steps = 3 + level


class ScenarioRecombinationStress(Task):
    summary = ("Find the worst cumulative load after uncertainty scenarios are closed under allowed prefix-suffix "
               "recombinations; vary splice checkpoints and history restrictions, and answer the new worst path "
               "or conservatism gap.")
    task_name = "scenario_recombination_stress"

    config_cls = ScenarioConfig
    task_meta = TASK_META
    design_choice = design_choice

    def generate_entry(self):
        cfg = self.config
        L = cfg.length
        while True:
            def rand_seq():
                n = random.randint(max(2, L - 1), L + 1)
                return [random.choice([-2, -1, 1, 2, 3]) for _ in range(n)]
            p0 = rand_seq()
            p1 = rand_seq()
            a, b = len(p0), len(p1)
            if min(a, b) < 2:
                continue
            admissible = set()
            order = ["closed", "switch"]
            random.shuffle(order)
            closed = False
            for op in order:
                if op == "closed":
                    cands = _checkpoint_adversary(p0, p1, a, b, cfg.history)
                    for s, q0, q1 in cands:
                        admissible.add(_subject(q0, q1))
                    if any(_subject(q0, q1) <= cfg.history for q0, q1 in ((p0, p1), (p1, p0))):
                        admissible.add(_subject(p0, p1))
                    closed = True
                else:
                    r = _try_switch_whole(p0, p1, cfg.history)
                    if r is not None:
                        admissible.add(r[0])
            if len(admissible) == 0:
                admissible.add(_subject(p0, p1))
            worst = max(admissible)
            if worst <= _subject(p0, p1):
                worst = _subject(p0, p1)
            assert isinstance(worst, int)
            assert worst >= 0
            metadata = {
                "fwd_seq": p0,
                "bwd_seq": p1,
                "history": cfg.history,
                "closed": closed,
            }
            answer = str(worst)
            return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        p0 = metadata["fwd_seq"]
        p1 = metadata["bwd_seq"]
        h = metadata["history"]
        return (f"Two scenarios have been reconciled into forward and backward load sequences over shared time "
                f"steps: forward {p0} and backward {p1}. The worst cumulative load of a sequence is the maximum "
                f"prefixed sum over its steps (the empty prefix counts 0). You may recombine the two sequences "
                f"by cutting each at exactly one internal splice checkpoint and concatenating a prefix from one "
                f"scenario with the remaining suffix from the other (keeping relative order within each piece); "
                f"the concatenation may be built in either order. A recombined schedule is admissible only when "
                f"its worst cumulative load is at most the history cap of {h}. "
                f"What is the maximum worst cumulative load attainable by any admissible recombined schedule "
                f"(or by the original schedules if no recombination is admissible)? The answer is a single "
                f"non-negative integer.")

    def score_answer(self, answer, entry):
        try:
            return 1.0 if int(str(answer).strip()) == int(entry.answer) else 0.0
        except Exception:
            return 0.0
