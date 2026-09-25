import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class ConservativeMeshConfig(Config):
    n_cells: int = 3
    max_density: int = 9

    def apply_difficulty(self, level):
        self.n_cells = stochastic_rounding(self.n_cells + 2 * level)
        self.max_density = stochastic_rounding(self.max_density + level)


def _overlap(a_start, a_end, b_start, b_end):
    return max(0, min(a_end, b_end) - max(a_start, b_start))


def _integer_boundaries(n, start, end, lo, hi):
    cuts = sorted(random.sample(range(lo, hi), n - 1))
    return [start] + cuts + [end]


class ConservativeMeshRemapping(Task):
    summary = "Transfer piecewise constant material densities through prescribed cell splits, merges and boundary shifts by integrating overlap with the previous mesh; return a queried cell's mass or density."
    config_cls = ConservativeMeshConfig
    task_version = 2

    design_choice = "Queried answer is the mass of a specified cell, requiring multiplication of overlap area by old density, versus density alone."

    def generate_entry(self):
        n = self.config.n_cells
        max_d = self.config.max_density

        while True:
            old_density = [random.randint(1, max_d) for _ in range(n)]
            old_edges = _integer_boundaries(n, 0, 10 * n + 1, 1, 10 * n)
            olen = old_edges[-1]
            m = random.randint(2, n)
            new_edges = _integer_boundaries(m, 0, olen, 1, olen)
            new_cells = list(zip(new_edges[:-1], new_edges[1:]))
            if len(new_cells) >= 1:
                break

        mass = []
        for (ns, ne) in new_cells:
            msum = 0.0
            for i in range(n):
                ov = _overlap(ns, ne, old_edges[i], old_edges[i + 1])
                msum += ov * old_density[i]
            mass.append(msum)

        query = random.randrange(len(new_cells))
        ns, ne = new_cells[query]
        ans = mass[query]

        recalc = 0.0
        for i in range(n):
            recalc += _overlap(ns, ne, old_edges[i], old_edges[i + 1]) * old_density[i]
        assert abs(recalc - ans) < 1e-9
        assert ans >= 0

        metadata = {
            "old_density": old_density,
            "old_edges": old_edges,
            "new_cells": [[s, e] for (s, e) in new_cells],
            "query": query,
        }
        answer = repr(round(ans, 6))
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        old_d = metadata["old_density"]
        old_e = metadata["old_edges"]
        new_c = metadata["new_cells"]
        q = metadata["query"]
        lines = []
        for i in range(len(old_d)):
            lines.append("old cell %d: constant density %d over [%d, %d]" % (i, old_d[i], old_e[i], old_e[i + 1]))
        ncells = ", ".join("[%d, %d]" % (s, e) for (s, e) in new_c)
        prompt = (
            "A 1D material occupies domain [0, %d] and is divided into old cells:\n" % old_e[-1]
            + "\n".join(lines)
            + "\nThe mesh is conservatively remapped (mass must be preserved) onto new cells with intervals "
            + ncells
            + ".\n"
            + "For each new cell the mass is the integral of old density over the overlap with old cells; "
            + "with piecewise constant density that is sum of (overlap width x old density).\n"
            + "What is the mass of the new cell at index %d? Answer only the numeric mass.\n" % q
        )
        return prompt

    def score_answer(self, answer, entry):
        try:
            val = float(str(answer).strip())
        except (TypeError, ValueError):
            return 0.0
        target = float(entry.answer)
        return 1.0 if abs(val - target) < 1e-6 else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'conservative_mesh_remapping (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_semantics_r4/conservative_mesh_remapping',
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
