import random

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'discrete_tomographic_completion (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_shortcuts_fail_r4/discrete_tomographic_completion',
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

design_choice = ("Vary answer form by instance: forced cell value, feasible interval endpoints, "
                 "or a unique-solution flag, with each level emitting at least two distinct answer types.")


def _enumerate(n, m, rsum, csum, region_targets, regions_of_cell, cap, node_limit=30000):
    """Enumerate binary matrices matching sums, capped at `cap` solutions.

    Returns (solutions, complete, masked_values_seen_endpoints) where masked is cell (n-1, m-1).
    """
    region_tot = [0] * len(region_targets)
    rsum_l = list(rsum)
    csum_l = list(csum)
    res = []
    complete = False
    seen = {0: False, 1: False}
    nodes = 0

    def backtrack(i, j, mat):
        nonlocal complete, nodes
        if len(res) >= cap or nodes >= node_limit:
            return
        if i == n:
            if (all(c == 0 for c in csum_l)
                    and all(t == rt for t, rt in zip(region_tot, region_targets))):
                res.append(tuple(tuple(row) for row in mat))
                seen[mat[n - 1][m - 1]] = True
            return
        ni, nj = (i, j + 1) if j + 1 < m else (i + 1, 0)
        for v in (0, 1):
            if len(res) >= cap or nodes >= node_limit:
                return
            nodes += 1
            if v == 1:
                if rsum_l[i] <= 0 or csum_l[j] <= 0:
                    continue
                rsum_l[i] -= 1
                csum_l[j] -= 1
                ri = regions_of_cell.get((i, j), -1)
                if ri >= 0:
                    if region_tot[ri] >= region_targets[ri]:
                        rsum_l[i] += 1
                        csum_l[j] += 1
                        continue
                    region_tot[ri] += 1
            mat[i][j] = v
            backtrack(ni, nj, mat)
            mat[i][j] = 0
            if v == 1:
                rsum_l[i] += 1
                csum_l[j] += 1
                ri = regions_of_cell.get((i, j), -1)
                if ri >= 0:
                    region_tot[ri] -= 1

    backtrack(0, 0, [[0] * m for _ in range(n)])
    complete = (len(res) < cap) and (nodes < node_limit)
    return res, complete, seen


class TomographicConfig(Config):
    rows: int = 3
    cols: int = 3
    region_count: int = 2
    density: float = 0.5

    def apply_difficulty(self, level):
        self.rows = min(3 + (level // 3), 4)
        self.cols = min(3 + (level // 3), 4)
        self.region_count = 2 + (level // 2)
        self.density = random.choice([0.35, 0.5, 0.65])


class DiscreteTomographicCompletion(Task):
    summary = ("Recover bounded binary arrays from overlapping directional sums, masked cells, "
               "and region totals, including ambiguous and inconsistent systems; answer a forced "
               "cell value, its attainable range, or uniqueness.")
    config_cls = TomographicConfig
    design_choice = design_choice

    def generate_entry(self):
        n = self.config.rows
        m = self.config.cols
        rc = self.config.region_count
        for _ in range(400):
            entry = self._try(n, m, rc)
            if entry is not None:
                return entry
        raise RuntimeError("could not generate")

    def _try(self, n, m, rc):
        density = self.config.density
        mat = [[1 if random.random() < density else 0 for _ in range(m)] for _ in range(n)]
        masked = (n - 1, m - 1)
        rm, cm = masked
        rows_sum = [sum(row) - row[cm] for row in mat]
        cols_sum = [sum(mat[i][j] for i in range(n)) - mat[rm][j] for j in range(m)]

        cells = [(i, j) for i in range(n) for j in range(m) if (i, j) != masked]
        random.shuffle(cells)
        parts = cells[: int(len(cells) * 0.7)]
        random.shuffle(parts)
        region_cell_sets = [[] for _ in range(rc)]
        for idx, c in enumerate(parts):
            region_cell_sets[idx % rc].append(c)
        region_targets = [sum(mat[i][j] for (i, j) in cs) for cs in region_cell_sets]

        regions_of_cell = {}
        for ri, cs in enumerate(region_cell_sets):
            for (i, j) in cs:
                regions_of_cell[(i, j)] = ri

        cap = 3
        sols, complete, seen = _enumerate(n, m, rows_sum, cols_sum, region_targets,
                                          regions_of_cell, cap)
        if not sols:
            return None

        if complete:
            total = len(sols)
            rmc = {s[rm][cm] for s in sols}
            kind = random.choice(["forced", "range", "unique"])
            if kind == "range" and len(rmc) != 2:
                return None
            if kind == "forced" and len(rmc) != 1:
                return None
            if kind == "unique" and total != 1:
                ans, qtype = "0", "unique"
                question = ("Is the masked cell value uniquely determined across all valid "
                            "completions? Answer 1 if the value is forced to a single number, "
                            "0 if more than one value is possible.")
            elif kind == "unique":
                ans, qtype = "1", "unique"
                question = ("Is the masked cell value uniquely determined across all valid "
                            "completions? Answer 1 if the value is forced to a single number, "
                            "0 if more than one value is possible.")
            elif kind == "forced":
                ans, qtype = str(list(rmc)[0]), "forced"
                question = ("What value (0 or 1) must the masked cell take in every valid "
                            "completion?")
            else:
                lo, hi = min(rmc), max(rmc)
                ans, qtype = f"{lo} {hi}", "range"
                question = ("What are the minimum and maximum values the masked cell can take "
                            "across all valid completions? Answer as 'min max'.")
        else:
            # many solutions (ambiguous). Only safe claim: both values present.
            if seen[0] and seen[1]:
                ans, qtype = "0 1", "range"
                question = ("What are the minimum and maximum values the masked cell can take "
                            "across all valid completions? Answer as 'min max'.")
            else:
                return None

        metadata = {
            "rows": n, "cols": m, "rows_sum": rows_sum, "cols_sum": cols_sum,
            "regions": [[list(c) for c in cs] for cs in region_cell_sets],
            "region_targets": region_targets, "masked": list(masked),
            "mat": mat, "solutions": len(sols), "answer_type": qtype,
            "question": question,
        }
        return Entry(metadata=metadata, answer=ans)

    def _render_prompt(self, metadata):
        n, m = metadata["rows"], metadata["cols"]
        masked = metadata["masked"]
        qtype = metadata["answer_type"]
        lines = []
        lines.append(
            f"We have a {n}x{m} grid where every cell holds a 0 or a 1. The masked cell at "
            f"row {masked[0]+1}, column {masked[1]+1} is hidden; every other cell is present "
            f"but its value is not stated directly.")
        lines.append("Known sums over the visible cells (each excludes the masked cell's own value):")
        lines.append("row sums (row 1..{}): {}".format(n, " ".join(map(str, metadata["rows_sum"]))))
        lines.append("column sums (col 1..{}): {}".format(m, " ".join(map(str, metadata["cols_sum"]))))
        for k, cs in enumerate(metadata["regions"]):
            cstr = " ".join("{},{}".format(i + 1, j + 1) for (i, j) in [tuple(c) for c in cs])
            lines.append(f"region {k+1} cells [{cstr}] sum to {metadata['region_targets'][k]}")
        lines.append(metadata["question"])
        if qtype == "range":
            lines.append("The answer is two integers separated by a space: 'min max'.")
        else:
            lines.append("The answer is one integer.")
        return "\n".join(lines)

    def render_prompt(self, metadata):
        return self._render_prompt(metadata)


def _score_unique(answer):
    return 1.0 if answer.strip() in ("0", "1") else 0.0


def _score_range(answer):
    parts = answer.split()
    if len(parts) != 2:
        return 0.0
    try:
        lo, hi = int(parts[0]), int(parts[1])
    except ValueError:
        return 0.0
    return 1.0 if lo <= hi and 0 <= lo <= 1 and 0 <= hi <= 1 else 0.0


def score_answer(answer, entry):
    qtype = entry["metadata"]["answer_type"]
    if qtype == "range":
        return _score_range(answer)
    return _score_unique(answer)
