import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding as sround

TASK_META = {'parent_source_id': None,
 'idea': 'havel_hakimi_realization (draw 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_invariants_r1/havel_hakimi_realization',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = ("Witness form: for a failing step, return the sorted residual degrees "
                 "plus the index of the vertex that cannot be satisfied, rather than the "
                 "full adjacency list.")


def hh_trace(seq):
    """Full Havel-Hakimi trace.

    Returns (outcome, info, residual_at_start_each_round):
      outcome: 'graphical' or 'fail'
      info:     for graphical -> completion round count; for fail -> the failing round number
      residual_at_start_each_round: non-increasing positive residual at the start of round r
        (residual_at_start_each_round[0] is the full positive sequence).
    """
    active = [d for d in sorted(seq, reverse=True) if d > 0]
    residuals = []
    rounds = 0
    while active:
        residuals.append(list(active))
        m = len(active)
        d = active[0]
        if d > m - 1:
            return "fail", rounds + 1, residuals
        rest = [x - 1 for x in active[1:d + 1]] + active[d + 1:]
        active = [x for x in sorted(rest, reverse=True) if x > 0]
        rounds += 1
    return "graphical", rounds, residuals


def _graph_degrees(n, density):
    deg = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < density:
                deg[i] += 1
                deg[j] += 1
    return sorted(deg, reverse=True)


def _overtop_sequence(n):
    """Guaranteed non-graphical: one vertex needs n neighbors but only n-1 exist."""
    seq = [n] + [random.randint(1, n - 1) for _ in range(n - 1)]
    return sorted(seq, reverse=True)


def _render(residual):
    return ",".join(str(x) for x in residual)


def _join(seq):
    return ", ".join(str(x) for x in seq)


@dataclass
class HavelHakimiConfig(Config):
    n_vertices: int = 7
    density_min: float = 0.42
    density_max: float = 0.8

    def apply_difficulty(self, level):
        self.n_vertices = sround(self.n_vertices + 2 * level)
        self.density_min = min(0.55, 0.42 + 0.02 * level)
        self.density_max = min(0.88, 0.8 + 0.02 * level)


class HavelHakimiRealization(Task):
    summary = ("Run the Havel-Hakimi degree-reduction that repeatedly attaches a "
               "maximum-degree vertex to the highest remaining degrees, returning "
               "whether the sequence is graphical, or the failing step with its "
               "witness (sorted residual degrees plus the index of the unsatisfiable "
               "vertex), or the residual multiset after k rounds.")
    config_cls = HavelHakimiConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        mode = random.choices(
            ("graphical", "not", "residual"),
            weights=(0.26, 0.28, 0.46),
        )[0]
        for _ in range(200):
            n = cfg.n_vertices
            density = random.uniform(cfg.density_min, cfg.density_max)
            if mode == "graphical":
                seq = _graph_degrees(n, density)
                outcome, c, residuals = hh_trace(seq)
                if outcome == "graphical":
                    k = c + random.randint(0, 1)
                    answer = "GRAPHICAL"
                    meta = {"sequence": seq, "k": k, "outcome": "graphical",
                            "completion_rounds": c}
                    return Entry(metadata=meta, answer=answer)
            elif mode == "not":
                seq = _overtop_sequence(n)
                outcome, f, residuals = hh_trace(seq)
                if outcome == "fail":
                    k = f
                    residual = residuals[f - 1]
                    answer = "NOTGRAPHICAL " + _render(residual) + " index 0"
                    meta = {"sequence": seq, "k": k, "outcome": "fail",
                            "failing_round": f, "residual": residual, "index": 0}
                    return Entry(metadata=meta, answer=answer)
            else:
                seq = _graph_degrees(n, density)
                outcome, c, residuals = hh_trace(seq)
                if outcome == "graphical" and c >= 2:
                    k = random.randint(1, min(c - 1, 3))
                    residual = residuals[k]
                    answer = "RESIDUAL " + _render(residual)
                    meta = {"sequence": seq, "k": k, "outcome": "residual",
                            "completion_rounds": c, "residual": residual}
                    return Entry(metadata=meta, answer=answer)
        raise RuntimeError("HavelHakimiRealization failed to generate after 200 attempts")

    def render_prompt(self, metadata):
        seq = "[" + _join(metadata["sequence"]) + "]"
        return (
            f"Apply the Havel-Hakimi reduction to the degree sequence {seq}, listed "
            f"largest to smallest. Each round: take the largest remaining degree d; if d "
            f"is greater than the number of remaining vertices minus one, the sequence is "
            f"not graphical and that round fails; otherwise subtract 1 from the d "
            f"next-largest remaining degrees and re-sort largest to smallest. Run exactly "
            f"k={metadata['k']} rounds, then give the outcome: if every degree reaches "
            f"zero within those k rounds, answer exactly GRAPHICAL; if a round fails "
            f"within those k, answer NOTGRAPHICAL followed by the sorted residual degrees "
            f"at the failing round and the 0-based index of the unsatisfiable "
            f"largest-degree vertex, as NOTGRAPHICAL residual index 0; otherwise answer "
            f"RESIDUAL followed by the sorted residual degrees after the k rounds. "
            f"Example answer formats: GRAPHICAL ; NOTGRAPHICAL 4,3,1 index 0 ; "
            f"RESIDUAL 3,2."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == str(entry.answer).strip() else 0.0
