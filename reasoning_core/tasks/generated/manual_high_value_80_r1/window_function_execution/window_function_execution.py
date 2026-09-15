"""Partitioned ordered window-function execution over a small fact table.

Asks the model to compute a running total, a rank, a lag/lead value or a
bounded-window aggregate (count/sum/avg) for a queried row, partitioned by
one column and ordered by another, with ties resolved by an explicit tiebreak
column plus the item id.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'window_function_execution (draw 1 of 1)',
 'hypothesis': 'HV-033',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/manual_high_value_80_r1/window_function_execution',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1403199800,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class WindowFunctionConfig(Config):
    n_partitions: int = 2
    n_rows: int = 4
    n_values: int = 5
    window_size: int = 2

    def apply_difficulty(self, level):
        self.n_partitions = 1 + level // 2
        self.n_rows = 4 + level
        self.n_values = 5 + level
        self.window_size = 2 + level // 2


def render_step(mode, ws, query, q_sorted):
    prompt = ""
    if mode == "running":
        prompt += (f"Compute the running total of score over items in the partition "
                   f"of the query row, cumulated in the order stated above, up to and "
                   f"including the query row. What is that running total? "
                   f"Answer with an integer.")
    elif mode == "rank":
        prompt += (f"Compute the rank of the query row within its partition, "
                   f"ordered as stated above, using competition ranking (ties share the "
                   f"same rank and the next rank skips). What is the rank? "
                   f"Answer with an integer.")
    elif mode == "lag":
        prompt += (f"Compute the lag by 1 of the query row's score: the score of the "
                   f"immediately preceding item in the partition order, or empty if there "
                   f"is none. Answer with an integer, or write NONE if there is no "
                   f"preceding item.")
    elif mode == "lead":
        prompt += (f"Compute the lead by 1 of the query row's score: the score of the "
                   f"immediately following item in the partition order, or empty if there "
                   f"is none. Answer with an integer, or write NONE if there is no "
                   f"following item.")
    elif mode == "count":
        prompt += (f"Compute a window over the query row's partition consisting of the "
                   f"query row and the {ws - 1} rows immediately preceding it in the "
                   f"partition order (a frame of at most {ws} rows). How many rows are "
                   f"in that window? Answer with a non-negative integer.")
    elif mode == "sum":
        prompt += (f"Compute a window over the query row's partition consisting of the "
                   f"query row and the {ws - 1} rows immediately preceding it in the "
                   f"partition order (a frame of at most {ws} rows). What is the sum of "
                   f"score over that window? Answer with an integer.")
    else:
        prompt += (f"Compute a window over the query row's partition consisting of the "
                   f"query row and the {ws - 1} rows immediately preceding it in the "
                   f"partition order (a frame of at most {ws} rows). What is the average "
                   f"of score over that window? Answer with a decimal number.")
    return prompt


class WindowFunctionExecution(Task):
    summary = ("Compute partitioned ordered running totals, ranks, lag or lead values, "
               "or bounded-window aggregates for a queried table row.")
    config_cls = WindowFunctionConfig

    def generate_entry(self):
        cfg = self.config
        rng = random
        n_part = cfg.n_partitions
        part_names = [f"P{p}" for p in range(n_part)]
        all_rows = []
        for part in part_names:
            count = max(1, rng.randint(cfg.n_rows - 1, cfg.n_rows + 1))
            for i in range(count):
                all_rows.append({
                    "part": part,
                    "score": rng.randint(1, cfg.n_values),
                    "tb": rng.randint(1, cfg.n_values),
                    "id": f"{part}_r{i}",
                })

        query_part = rng.choice(part_names)
        q_rows = [r for r in all_rows if r["part"] == query_part]
        query = max(q_rows, key=lambda r: r["id"])
        q_sorted = sorted(q_rows, key=lambda r: (r["score"], r["tb"], r["id"]))

        mode = rng.choice(["running", "rank", "lag", "lead", "count", "sum", "avg"])
        ws = cfg.window_size
        idx = q_sorted.index(query)

        if mode == "running":
            acc = 0
            for r in q_sorted:
                acc += r["score"]
                if r is query:
                    ans = acc
        elif mode == "rank":
            prev = None
            rank = 0
            ans = 0
            for i, r in enumerate(q_sorted):
                key = (r["score"], r["tb"])
                if prev is None or key != prev:
                    prev = key
                    rank = i + 1
                if r is query:
                    ans = rank
        elif mode == "lag":
            ans = None if idx == 0 else q_sorted[idx - 1]["score"]
        elif mode == "lead":
            ans = None if idx == len(q_sorted) - 1 else q_sorted[idx + 1]["score"]
        elif mode == "count":
            ans = min(idx, ws - 1) + 1
        elif mode == "sum":
            lo = max(0, idx - ws + 1)
            ans = sum(r["score"] for r in q_sorted[lo:idx + 1])
        else:
            lo = max(0, idx - ws + 1)
            win = q_sorted[lo:idx + 1]
            ans = sum(r["score"] for r in win) * 1.0 / len(win)

        if mode == "avg":
            ans_s = f"{ans:.6g}"
        elif ans is None:
            ans_s = "NONE"
        else:
            ans_s = str(ans)

        rows_lines = []
        for part in part_names:
            pr = sorted([r for r in all_rows if r["part"] == part], key=lambda x: x["id"])
            for r in pr:
                rows_lines.append(f"  {r['part']} | score {r['score']} | tb {r['tb']}")

        step = render_step(mode, ws, query, q_sorted)
        prompt = (
            f"Below is a table of items. Each item belongs to a partition (the part "
            f"column), has a numeric score, and a secondary numeric tiebreak value tb.\n"
            f"\nItems:\n" + "\n".join(rows_lines) + "\n\n"
            f"Within each partition, items are ordered by score ascending, then tb "
            f"ascending, then id ascending (ids P<i>_r<j> sort lexicographically). "
            f"The query row is the item {query['part']} with score {query['score']} and "
            f"tb {query['tb']}.\n\n"
            + step
        )

        entry = Entry(
            metadata={
                "mode": mode,
                "rows": all_rows,
                "query": query,
                "query_part": query_part,
                "window_size": ws,
                "answer_raw": ans,
                "prompt": prompt,
            },
            answer=ans_s,
        )
        return entry

    def render_prompt(self, metadata):
        return metadata["prompt"]

    def score_answer(self, answer, entry):
        meta = entry.metadata
        mode = meta["mode"]
        expected = meta["answer_raw"]
        if mode == "avg":
            try:
                return 1.0 if abs(float(answer) - expected) < 1e-4 else 0.0
            except (TypeError, ValueError):
                return 0.0
        if mode in ("lag", "lead") and expected is None:
            return 1.0 if str(answer).strip().upper() == "NONE" else 0.0
        return 1.0 if str(answer).strip() == str(expected) else 0.0
