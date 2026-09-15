import random
import itertools
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


def _find_ranking(coeffs):
    """Find positive integer coefficients c (each in [1,5]) with

    sum_j c[j]*coeffs[i][j] <= -1   for every row i.

    Returns (list_of_coeffs, subset_used) or (None, None). Positive coefficients
    are searched first because with a -1 on the diagonal they already drive
    decrease; larger subsets and larger values are only tried when needed.
    """
    n = len(coeffs)
    for subset_size in range(1, n + 1):
        for comb in itertools.combinations(range(n), subset_size):
            for tup in itertools.product(range(1, 6), repeat=subset_size):
                row = [0.0] * n
                for idx, m in zip(comb, tup):
                    row[idx] = float(m)
                ok = True
                for i in range(n):
                    s = 0.0
                    for j in range(n):
                        s += row[j] * coeffs[i][j]
                    if s >= -1e-9:
                        ok = False
                        break
                if ok:
                    return row, comb
    return None, None


def _signed(m):
    return f"+{m}" if m >= 0 else f"-{abs(m)}"


def _fmt_linear(vec, var_names):
    terms = []
    for i, c in enumerate(vec):
        c = int(round(c))
        if c == 0:
            continue
        if c < 0:
            terms.append(f"- {abs(c)}{var_names[i]}")
        else:
            terms.append(f"+ {c}{var_names[i]}")
    body = " ".join(terms).strip()
    if body.startswith("- "):
        return "-" + body[1:]
    if body.startswith("+ "):
        return body[2:]
    return body if body else "0"


@dataclass
class TerminationRankingConfig(Config):
    nvars: int = 2
    coeff_range: int = 5

    def apply_difficulty(self, level):
        self.nvars = max(1, min(5, stochastic_rounding(self.nvars + level // 2)))
        self.coeff_range = 5


class TerminationRankingFunction(Task):
    summary = "Given a single-loop program with linear integer arithmetic updates and a loop guard, synthesize a linear ranking function proving termination and output its coefficients in canonical form."
    design_choice = "Vary the number of loop variables from 1 to 5, with coefficients restricted to small integers in [-5,5] to keep canonical output simple."
    config_cls = TerminationRankingConfig

    def generate_entry(self):
        n = self.config.nvars
        var_names = [f"x{i+1}" for i in range(n)]
        for _ in range(4000):
            coeffs = []
            for _ in range(n):
                row = [random.randint(-4, 4) for _ in range(n)]
                coeffs.append(row)
            for _ in range(max(1, n // 2)):
                i = random.randrange(n)
                coeffs[i][i] = -1
            row, comb = _find_ranking(coeffs)
            if row is None:
                continue
            guard = [random.randint(-8, 8) for _ in range(n)]
            if all(g >= 0 for g in guard):
                continue

            guard_terms = [f"{_signed(g)} {var_names[i]}" for i, g in enumerate(guard)]
            guard_expr = " ".join(guard_terms).strip()

            update_lines = []
            for i in range(n):
                update_lines.append(f"    {var_names[i]} := {_fmt_linear(coeffs[i], var_names)};")
            updates = "\n".join(update_lines)

            rank_terms = " + ".join(f"a{i+1}*{var_names[i]}" for i in range(n))

            ans = ",".join(str(int(round(v))) for v in row)

            return Entry(
                metadata={
                    "coeffs": coeffs,
                    "guard": guard,
                    "var_names": var_names,
                    "ranking": [int(round(v)) for v in row],
                    "comb": list(comb),
                },
                answer=ans,
            )
        raise RuntimeError("failed to generate termination ranking instance")

    def render_prompt(self, metadata):
        var_names = metadata["var_names"]
        n = len(var_names)
        coeffs = metadata["coeffs"]
        guard = metadata["guard"]
        guard_terms = [f"{_signed(g)} {var_names[i]}" for i, g in enumerate(guard)]
        guard_expr = " ".join(guard_terms).strip()
        update_lines = []
        for i in range(n):
            update_lines.append(f"    {var_names[i]} := {_fmt_linear(coeffs[i], var_names)};")
        updates = "\n".join(update_lines)
        rank_terms = " + ".join(f"a{i+1}*{var_names[i]}" for i in range(n))
        return (
            f"A program computes the following single loop over integer variables "
            f"{', '.join(var_names)}:\n\n"
            f"while ( {guard_expr} >= 0 ) {{\n"
            f"{updates}\n"
            f"}}\n\n"
            f"Each update uses linear integer arithmetic on the current values. "
            f"The loop always terminates if there exists a linear ranking function "
            f"r = {rank_terms}, with integer coefficients a1..a{str(n)}, such that "
            f"whenever the guard holds, r strictly decreases by at least 1 on every "
            f"iteration.\n"
            f"Find such a ranking function and report its coefficient list "
            f"[a1, a2, ..., a{str(n)}] as a comma-separated sequence of integers in "
            f"the order of {', '.join(var_names)}, choosing coefficients with "
            f"absolute value at most 5. "
            f"Give only the coefficient list, nothing else."
        )


TASK_META = {'parent_source_id': None,
 'idea': 'termination_ranking_function (draw 1 of 3)',
 'hypothesis': 'nemotron_2:termination_ranking_function',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/termination_ranking_function',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 313472375,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
