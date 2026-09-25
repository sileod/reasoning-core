import random
from dataclasses import dataclass, field

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'conditional_model_pasting (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_dependence_relevance_r4/conditional_model_pasting',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = "Represent each model as a full probability table over a fixed finite grid and answer whether a queried table is in the closure after iterative pasting."


@dataclass
class ConditionalModelPastingConfig(Config):
    r_state: int = 2
    n_models: int = 3
    denominator: int = 8
    inner_cells: int = 2
    new_query_prob: float = 0.5

    def apply_difficulty(self, level):
        self.r_state = 2 + (1 if level >= 4 else 0)
        self.inner_cells = 2
        self.n_models = min(3 + (level + 1) // 2, 5)
        self.denominator = 8 + 4 * (level >= 3)


def _cell_mass(base, c1, R):
    return sum(base[c1 * R:(c1 + 1) * R])


def _paste(base, donor, inner_cells, R):
    K = inner_cells * R
    out = [0] * K
    for c1 in range(inner_cells):
        bm = _cell_mass(donor, c1, R)
        if bm == 0:
            continue
        am = _cell_mass(base, c1, R)
        for r in range(R):
            num = am * donor[c1 * R + r]
            if num % bm != 0:
                return None
            out[c1 * R + r] = num // bm
    return tuple(out)


def _closure(models, inner_cells, R, cap=100000):
    current = list(models)
    seen = set(current)
    frontier = list(current)
    steps = 0
    while frontier:
        steps += 1
        if steps > cap:
            return None, seen
        base = frontier.pop()
        for donor in current:
            p = _paste(base, donor, inner_cells, R)
            if p is None:
                continue
            if p not in seen:
                seen.add(p)
                current.append(p)
                frontier.append(p)
    return current, seen


def _random_table(inner_cells, R, D):
    K = inner_cells * R
    cuts = sorted(random.sample(range(1, D + K - 1), K - 1))
    prev = 0
    counts = []
    for c in cuts:
        counts.append(c - prev)
        prev = c
    counts.append(D + K - 1 - prev)
    counts = [c - 1 for c in counts]
    return tuple(counts)


@dataclass
class _M:
    pass


class ConditionalModelPasting(Task):
    summary = ("Close finite sets of probability models under recombining one model's "
               "partition masses with other models' within-cell conditionals; vary zero-mass "
               "cells and permitted donors; answer membership or newly admitted models.")
    config_cls = ConditionalModelPastingConfig

    def generate_entry(self):
        c = self.config
        inner = c.inner_cells
        R = c.r_state
        D = c.denominator
        K = inner * R

        while True:
            models = [_random_table(inner, R, D) for _ in range(c.n_models)]
            if len(set(models)) < 2:
                continue
            rects = [m for m in models if 0 in m]
            notrect = [m for m in models if 0 not in m]
            if not notrect:
                continue
            closure, seen = _closure(models, inner, R)
            if closure is None or len(closure) < 2:
                continue
            newly = len(closure) - len(set(models))
            if newly < len(set(models)):
                continue

            if random.random() < c.new_query_prob:
                pool = closure[len(set(models)):]
                winner = random.choice(pool) if pool else closure[0]
                query = winner
                answer = "yes"
            else:
                while True:
                    q = _random_table(inner, R, D)
                    if q not in seen:
                        query = q
                        answer = "no"
                        break

            metadata = {
                "r_state": R,
                "inner_cells": inner,
                "denominator": D,
                "models": models,
                "query": query,
                "closure_size": len(closure),
            }
            return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        m = metadata
        R = m["r_state"]
        inner = m["inner_cells"]

        def fmt(t):
            parts = []
            for c1 in range(inner):
                row = ", ".join(str(v) for v in t[c1 * R:(c1 + 1) * R])
                parts.append("[" + row + "]")
            return "(" + "; ".join(parts) + ")"

        lines = [f"A probability model over {inner} cells, each with {R} states, is a table of "
                 f"integer masses summing to {m['denominator']}. The masses of the {inner} cells "
                 f"(sums within each top-level {fmt(tuple(0 for _ in range(inner * R)))} bracket) "
                 f"are its cell partition, and within a top-level bracket the states are its "
                 f"within-cell conditionals."]
        lines.append("A pasted model is formed from a base model and a donor model: its cell "
                     "partition masses come from the base, while inside each top-level bracket "
                     "the base's states are rescaled to match the donor's within-cell conditional "
                     "for that bracket.")
        lines.append("Starting from the given models, repeatedly form every possible pasted "
                     "model (with any pair of base and donor among all models obtained so far) "
                     "until no new model appears. The resulting set is the model closure.")
        lines.append("Models:")
        for i, t in enumerate(m["models"]):
            lines.append(f"  model {i}: {fmt(t)}")
        lines.append(f"Question: is the following table in the closure? {fmt(m['query'])}")
        lines.append("Answer exactly the single word 'yes' if it is in the closure, or 'no' if "
                     "it is not.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        ans = entry.answer
        if isinstance(answer, str):
            answer = answer.strip().lower()
        return 1.0 if answer == ans else 0.0
