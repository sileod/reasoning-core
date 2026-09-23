import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'ferrers_diagram_operations (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_state_tracking_r4/ferrers_diagram_operations',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = "Present the partition as a list of row lengths and ask for the conjugate partition as a list, with all answers being valid integer sequences."


def _conjugate(rows):
    if not rows:
        return []
    return [sum(1 for r in rows if r > j) for j in range(rows[0])]


def _hook_length(i, j, rows):
    return (rows[i] - j - 1) + sum(1 for r in rows[i + 1:] if r > j) + 1


def _hook_lengths(rows):
    n = len(rows)
    out = []
    for i in range(n):
        row = []
        for j in range(rows[i]):
            row.append(_hook_length(i, j, rows))
        out.append(row)
    return out


def _count_syt_fact(rows):
    n = sum(rows)
    num = math.factorial(n)
    denom = 1
    for i in range(len(rows)):
        for j in range(rows[i]):
            denom *= _hook_length(i, j, rows)
    return num // denom


@dataclass
class FerrersConfig(Config):
    max_part: int = 5
    num_parts: int = 3

    def apply_difficulty(self, level):
        self.max_part = stochastic_rounding(self.max_part + level * 2)
        self.num_parts = stochastic_rounding(self.num_parts + level)


class FerrersDiagramOperations(Task):
    summary = "Operate on Ferrers diagrams of integer partitions: form the conjugate partition by transposition, compute hook lengths of cells, and count standard Young tableaux via the hook-length formula."
    config_cls = FerrersConfig
    task_version = 2

    def generate_entry(self):
        max_part = max(2, self.config.max_part)
        num_parts = max(1, self.config.num_parts)
        while True:
            rows = sorted(
                [random.randint(1, max_part) for _ in range(num_parts)],
                reverse=True,
            )
            if rows[0] <= 0 or len(rows) == 0:
                continue
            mode = random.choice(["conjugate", "hook", "count"])
            if mode == "conjugate":
                answer = _conjugate(rows)
                if answer == rows:
                    continue
                answer_str = "[" + ", ".join(str(x) for x in answer) + "]"
                break
            elif mode == "hook":
                i = random.randrange(len(rows))
                j = random.randrange(rows[i])
                hl = _hook_length(i, j, rows)
                assert hl >= 1
                answer_str = str(hl)
                break
            else:
                cnt = _count_syt_fact(rows)
                assert cnt >= 1
                assert isinstance(cnt, int)
                answer_str = str(cnt)
                break

        metadata = {"rows": rows, "mode": mode, "cell": (i, j) if mode == "hook" else None}
        return Entry(metadata=metadata, answer=answer_str)

    def render_prompt(self, metadata):
        rows = metadata["rows"]
        mode = metadata["mode"]
        rows_str = ", ".join(str(r) for r in rows)
        if mode == "conjugate":
            return (
                f"A Ferrers diagram of a partition is a left-justified Young diagram whose "
                f"rows contain the parts as row lengths, from top to bottom. The partition "
                f"here has row lengths {rows_str}. The conjugate partition is obtained by "
                f"transposing the diagram: its parts are the column heights, read top to "
                f"bottom. Give the conjugate partition as a list of positive integers in "
                f"decreasing order (the empty list if it has none)."
            )
        elif mode == "hook":
            i, j = metadata["cell"]
            return (
                f"A Ferrers diagram of a partition is a left-justified Young diagram whose "
                f"rows contain the parts as row lengths, from top to bottom. The partition "
                f"here has row lengths {rows_str}. The hook length of a cell is the number "
                f"of cells to its right in its row plus the number of cells below it in its "
                f"column plus one. Give the hook length of the cell in row {i + 1} (1-indexed "
                f"from the top), column {j + 1} (1-indexed from the left). The answer is one "
                f"positive integer."
            )
        else:
            return (
                f"A Ferrers diagram of a partition is a left-justified Young diagram whose "
                f"rows contain the parts as row lengths, from top to bottom. The partition "
                f"here has row lengths {rows_str}. A standard Young tableau (SYT) of shape "
                f"given by this partition fills its cells with the numbers 1 through {sum(rows)} "
                f"exactly once, so that entries increase along each row and each column. "
                f"The hook-length formula counts the number of SYT of a shape as n! / "
                f"product of hook lengths. How many standard Young tableaux of this shape "
                f"are there? The answer is one non-negative integer."
            )


def score_answer(self, answer, entry):
    mode = entry["metadata"]["mode"]
    answer = answer.strip()
    if mode == "conjugate":
        try:
            items = [int(x.strip()) for x in answer.strip("[]").split(",") if x.strip() != ""]
        except Exception:
            return 0.0
        gold = _conjugate(entry["metadata"]["rows"])
        if items == gold:
            return 1.0
        return 0.0
    elif mode == "hook":
        try:
            v = float(answer)
        except Exception:
            return 0.0
        i, j = entry["metadata"]["cell"]
        gold = _hook_length(i, j, entry["metadata"]["rows"])
        return 1.0 if int(v) == gold else 0.0
    else:
        try:
            v = int(answer)
        except Exception:
            return 0.0
        gold = _count_syt_fact(entry["metadata"]["rows"])
        return 1.0 if v == gold else 0.0
