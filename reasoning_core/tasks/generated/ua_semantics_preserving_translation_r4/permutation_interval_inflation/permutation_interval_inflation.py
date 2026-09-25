"""Permutation interval inflation: expand nested permutation blocks left-to-right."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'permutation_interval_inflation (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_semantics_preserving_translation_r4/permutation_interval_inflation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _stochastic_parts(n, m):
    """Partition n into m positive integers summing to n, uniformly at random."""
    n -= m
    cuts = sorted(random.sample(range(n + m - 1), m - 1)) if m > 1 else []
    parts = []
    prev = -1
    for c in cuts + [n + m - 1]:
        parts.append(c - prev)
        prev = c
    return parts


class _Node:
    __slots__ = ("lo", "hi", "children")

    def __init__(self, lo, hi, children):
        self.lo = lo
        self.hi = hi
        self.children = children

    def expand(self):
        out = []
        for c in self.children:
            if isinstance(c, _Node):
                out.extend(c.expand())
            else:
                out.append(c)
        return out

    def render(self):
        inner = ",".join(c.render() if isinstance(c, _Node) else str(c) for c in self.children)
        return f"({self.lo}..{self.hi}):[{inner}]"


def _leaf(value):
    return value


def _build(lo, hi, depth):
    """Build a nested block over [lo, hi] that expands to a permutation of it."""
    n = hi - lo + 1
    if n == 1:
        return _leaf(lo)
    if depth <= 0:
        vals = list(range(lo, hi + 1))
        random.shuffle(vals)
        return _Node(lo, hi, vals)
    m = random.randint(2, min(3, n))
    sizes = _stochastic_parts(n, m)
    children = []
    cursor = lo
    for s in sizes:
        if s == 1:
            children.append(_leaf(cursor))
            cursor += 1
        else:
            children.append(_build(cursor, cursor + s - 1, depth - 1))
            cursor += s
    return _Node(lo, hi, children)


def _generate(total, depth):
    root = _build(1, total, depth)
    expanded = root.expand()
    assert sorted(expanded) == list(range(1, total + 1))
    return root


def _flatten_expr(expr_str):
    """Independent parser: rebuild the tree from a rendered expression string."""

    def parse(expr):
        expr = expr.strip()
        if expr.isdigit():
            return _leaf(int(expr))
        assert expr.startswith("("), expr
        depth = 0
        i = 0
        while True:
            ch = expr[i]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        hi_idx = i
        assert expr[hi_idx + 1] == ":"
        lo, hi = (int(x) for x in expr[1:hi_idx].split(".."))
        inner = expr[hi_idx + 3:-1]
        children = []
        if inner:
            d = 0
            cur = ""
            for ch in inner:
                if ch == "(" or ch == "[":
                    d += 1
                elif ch == ")" or ch == "]":
                    d -= 1
                if ch == "," and d == 0:
                    children.append(cur)
                    cur = ""
                else:
                    cur += ch
            children.append(cur)
        return _Node(lo, hi, [parse(c) for c in children])

    return parse(expr_str)


@dataclass
class IntervalInflationConfig(Config):
    total: int = 6
    depth: int = 2

    def apply_difficulty(self, level):
        self.total = max(3, stochastic_rounding(6 + level * 4))
        self.depth = 1 + level // 2


class PermutationIntervalInflation(Task):
    summary = ("Expand nested permutation blocks whose parent ranks determine block value "
               "ranges and whose children determine internal order; vary block sizes and "
               "nesting, returning the expanded permutation or a queried image.")
    design_choice = ("Answer format: return the full expanded permutation as a comma-separated "
                     "list of integers, with nested blocks flattened left-to-right.")
    config_cls = IntervalInflationConfig

    def generate_entry(self):
        total = self.config.total
        depth = self.config.depth
        root = _generate(total, depth)
        return Entry(metadata={"expr": root.render(), "total": total},
                     answer=",".join(str(v) for v in root.expand()))

    def render_prompt(self, metadata):
        return (
            "A nested permutation block (lo..hi):[c1,c2,...] expands into a permutation of the "
            "integers {lo,...,hi}. The block's parent ranks determine its value range (its lo..hi), "
            "and the children's order determines the internal order. A bare integer is a singleton "
            "leaf that expands to itself. Flatten the whole expression left-to-right into one "
            "permutation of 1..N.\n\n"
            f"Expand this block:\n{metadata['expr']}\n\n"
            "Answer with the expanded permutation as a comma-separated list of integers, e.g. "
            "for (1..3):[2,1,3] the answer is 2,1,3.")

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        try:
            got = [int(x) for x in answer.split(",") if x.strip() != ""]
        except ValueError:
            return 0.0
        gold = [int(x) for x in entry["answer"].split(",") if x.strip() != ""]
        return 1.0 if got == gold else 0.0
