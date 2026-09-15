import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class WindowFunctionConfig(Config):
    nrows: int = 6
    ncols: int = 4
    width: int = 3

    def apply_difficulty(self, level):
        self.nrows = 6 + 2 * level
        self.ncols = 3 + level
        self.width = 2 + level


def _make_table(nrows, ncols):
    headers = []
    seen = set()
    while len(headers) < ncols:
        h = random.choice(
            ["q", "sales", "score", "id", "amount", "val", "cnt", "price", "rank", "n"]
        )
        if h not in seen:
            seen.add(h)
            headers.append(h)
    rows = [
        [int(random.randint(0, 100)) for _ in range(ncols)]
        for _ in range(nrows)
    ]
    return headers, rows


def _parse_target(headers, rows, ops, target_idx):
    ncols = len(headers)
    nrows = len(rows)
    idx_map = {h: i for i, h in enumerate(headers)}
    col_idx = idx_map[ops["col"]]
    width = ops["width"]

    values = [rows[r][col_idx] for r in range(nrows)]

    if ops["fn"] == "running_sum":
        out = []
        s = 0
        for v in values:
            s += v
            out.append(s)
    elif ops["fn"] == "running_avg":
        out = []
        s = 0
        for i, v in enumerate(values):
            s += v
            out.append(s / (i + 1))
    elif ops["fn"] == "rank":
        order = sorted(values)
        out = []
        for v in values:
            out.append(order.index(v) + 1)
    elif ops["fn"] == "lag":
        out = [None] * nrows
        for i in range(1, nrows):
            out[i] = values[i - 1]
    elif ops["fn"] == "lead":
        out = [None] * nrows
        for i in range(nrows - 1):
            out[i] = values[i + 1]
    elif ops["fn"] == "window_sum":
        out = []
        for i in range(nrows):
            lo = max(0, i - width + 1)
            out.append(sum(values[lo : i + 1]))
    elif ops["fn"] == "window_avg":
        out = []
        for i in range(nrows):
            lo = max(0, i - width + 1)
            window = values[lo : i + 1]
            out.append(sum(window) / len(window))
    else:
        raise RuntimeError("unknown fn")

    return out[target_idx]


def _target_for(ops, target_idx, headers, rows):
    val = _parse_target(headers, rows, ops, target_idx)
    if val is None:
        return None
    if isinstance(val, float):
        return round(val, 4)
    return val


def _format_value(v):
    if v is None:
        return "NULL (no prior row)"
    if isinstance(v, float):
        s = f"{v:.4f}".rstrip("0").rstrip(".")
        return s if s else "0"
    return str(v)


def _render_table(headers, rows):
    lines = []
    lines.append("  " + " | ".join(f"{h:>8}" for h in headers))
    for row in rows:
        lines.append("  " + " | ".join(f"{v:>8}" for v in row))
    return "\n".join(lines)


def _describe_fn(fn, width):
    if fn == "running_sum":
        return "running total (ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"
    if fn == "running_avg":
        return "running average over all rows up to and including the current row"
    if fn == "rank":
        return "rank (smallest value ranks 1, ties share the same rank)"
    if fn == "lag":
        return "1-lag value, taken from the immediately preceding row"
    if fn == "lead":
        return "1-lead value, taken from the immediately following row"
    if fn == "window_sum":
        return f"sum over the last {width} rows up to and including the current row"
    if fn == "window_avg":
        return f"average over the last {width} rows up to and including the current row"
    raise RuntimeError("unknown fn")


def compute_answer(metadata):
    ops = metadata["ops"]
    headers = metadata["headers"]
    rows = metadata["rows"]
    return _target_for(ops, metadata["target_idx"], headers, rows)


class WindowFunctionV3(Task):
    task_name = "window_function"
    summary = "Compute partitioned ordered running totals, ranks, lag or lead values, or bounded-window aggregates for a queried table row."
    design_choice = (
        "Present a candidate row and ask whether its computed window value matches a given target, "
        "requiring yes/no answers with balanced distribution."
    )
    config_cls = WindowFunctionConfig
    task_version = 2

    def generate_entry(self):
        nrows = self.config.nrows
        ncols = self.config.ncols
        width = self.config.width if self.config.width < nrows else nrows - 1

        while True:
            headers, rows = _make_table(nrows, ncols)
            fn = random.choice(
                ["running_sum", "running_avg", "rank", "lag", "lead", "window_sum", "window_avg"]
            )
            col = random.choice(headers)
            target_idx = random.randint(0, nrows - 1)
            ops = {
                "fn": fn,
                "col": col,
                "width": width,
            }

            gold = _target_for(ops, target_idx, headers, rows)
            if fn in ("lag", "lead") and target_idx in (0, nrows - 1):
                gold = None

            target = random.uniform(0, 1) < 0.5
            if target:
                shown = gold
                if shown is None:
                    shown = gold
                correct = True
            else:
                wrong = gold
                if wrong is None:
                    wrong = int(random.randint(0, 200))
                else:
                    delta = random.choice([-5, -3, -1, 1, 2, 4, 7])
                    if isinstance(wrong, float):
                        wrong = round(wrong + delta, 4)
                    else:
                        wrong = wrong + delta
                    if wrong is None:
                        wrong = int(random.randint(0, 200))
                correct = (wrong == gold) if gold is not None else False
                shown = wrong

            metadata = {
                "headers": headers,
                "rows": rows,
                "ops": ops,
                "target_idx": target_idx,
                "target_val": shown,
                "answer_is_yes": correct,
            }

            if gold is not None:
                assert isinstance(gold, (int, float, type(None)))
                if isinstance(gold, float):
                    assert -1e9 < gold < 1e9

            return Entry(metadata=metadata, answer="yes" if correct else "no")

    def render_prompt(self, metadata):
        headers = metadata["headers"]
        rows = metadata["rows"]
        ops = metadata["ops"]
        target_idx = metadata["target_idx"]
        fn_desc = _describe_fn(ops["fn"], ops["width"])

        prompt = (
            "A table has one column for each attribute below, ordered top to bottom by row.\n"
            "Columns: " + ", ".join(headers) + "\n"
            + _render_table(headers, rows)
            + "\n\n"
            f"Consider the {fn_desc} computed on the column '{ops['col']}' "
            f"for row {target_idx + 1} (the {_ordinal(target_idx)} row).\n"
            "Answer 'yes' if that computed value equals exactly "
            f"{_format_value(metadata['target_val'])} and 'no' otherwise.\n"
            "Your answer is exactly one word: 'yes' for a match, 'no' for a mismatch."
        )
        return prompt

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip().lower()
        if a not in ("yes", "no"):
            return 0.0
        return 1.0 if a == entry.answer else 0.0


def _ordinal(idx):
    n = idx + 1
    if n % 100 in (11, 12, 13):
        return f"{n}th"
    rem = n % 10
    if rem == 1:
        return f"{n}st"
    if rem == 2:
        return f"{n}nd"
    if rem == 3:
        return f"{n}rd"
    return f"{n}th"


TASK_META = {'parent_source_id': None,
 'idea': 'window_function_execution (draw 3 of 3)',
 'hypothesis': 'manual_high_value_80:window_function_execution',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/window_function_execution',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2342189148,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
