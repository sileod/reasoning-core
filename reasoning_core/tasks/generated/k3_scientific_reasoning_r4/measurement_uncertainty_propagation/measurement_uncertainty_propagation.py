"""Uncertainty propagation through a formula DAG.

Leaves are named inputs with central values and absolute half-widths; internal
nodes are binary arithmetic operators (add / subtract / multiply / divide);
each operator carries a dependency flag meaning its two operands are either
fully dependent (combine by worst-case linear sum) or independent (combine by
root-sum-square). The output is the last node's value and half-width, or the
input whose uncertainty contribution to the output is dominant.
"""

import math
import random
from dataclasses import dataclass, field

from reasoning_core.template import Config, Entry, Task

_OPS = ('+', '-', '*', '/')
_MODES = ('lin', 'rss')


def _fmt(v):
    return f"{v:.3f}"


def _propagate(leaves, nodes):
    """Forward propagation of values and absolute half-widths.

    Returns None when a division step has a zero divisor, so the caller can
    resample that instance rather than raise.
    """
    values = [v for (_n, v, _h) in leaves]
    hwidths = [h for (_n, _v, h) in leaves]
    for (op, ai, bi, mode) in nodes:
        av, bv = values[ai], values[bi]
        ah, bh = hwidths[ai], hwidths[bi]
        if op in ('+', '-'):
            v = av + bv if op == '+' else av - bv
            h = (ah + bh) if mode == 'lin' else math.hypot(ah, bh)
        elif op == '*':
            v = av * bv
            rel_a = ah / av if av else float('inf')
            rel_b = bh / bv if bv else float('inf')
            rel = (rel_a + rel_b) if mode == 'lin' else math.hypot(rel_a, rel_b)
            h = abs(v) * rel
        else:
            if bv == 0:
                return None
            v = av / bv
            rel_a = ah / av if av else float('inf')
            rel_b = bh / bv
            rel = (rel_a + rel_b) if mode == 'lin' else math.hypot(rel_a, rel_b)
            h = abs(v) * rel
        values.append(v)
        hwidths.append(h)
    return values, hwidths


def _gradients(leaves, nodes, values):
    """Reverse-mode gradient of the root value w.r.t. each leaf."""
    nleaf = len(leaves)
    grad = [0.0] * (nleaf + len(nodes))
    grad[-1] = 1.0
    for k in range(len(nodes) - 1, -1, -1):
        op, ai, bi, _mode = nodes[k]
        g = grad[nleaf + k]
        av, bv = values[ai], values[bi]
        if op == '+':
            da, db = g, g
        elif op == '-':
            da, db = g, -g
        elif op == '*':
            da, db = g * bv, g * av
        else:
            da = g / bv
            db = -g * av / (bv * bv)
        grad[ai] += da
        grad[bi] += db
    return grad[:nleaf]


_NAME = "ABCDEFGH"


@dataclass
class UncertaintyPropConfig(Config):
    num_inputs: int = 3
    num_internal: int = 2
    regimes: tuple = ('value', 'hwidth', 'dominant')

    def apply_difficulty(self, level):
        self.num_inputs = min(8, 3 + level)
        self.num_internal = 2 + level


class MeasurementUncertaintyPropagation(Task):
    summary = ("Propagate values with uncertainties through formula DAGs, combining terms by "
               "worst-case linear or root-sum-square rules as dependencies dictate; answer the "
               "resulting value, its half-width, or dominant input.")
    design_choice = ("a DAG whose leaves are named inputs with central values and absolute "
                     "half-widths, internal nodes are arithmetic operators, and edges carry "
                     "dependency flags; solver must compute output value and half-width")
    config_cls = UncertaintyPropConfig

    def render_prompt(self, metadata):
        head = ("A measurement network combines several noisy readouts. Absolute uncertainties "
                "are given as half-widths of the intervals (value ± half-width). Each operator "
                "combines its two operands' uncertainties either by the worst-case linear rule "
                "(half-widths add) or by the root-sum-square rule (add squares, take the square "
                "root), depending on whether the two operands' noises are fully dependent or "
                "independent, as stated per step.\n\n"
                "Inputs:\n" + _render_dag(metadata) + "\n")
        if metadata["regime"] == "value":
            return head + ("What is the value of the final output n%d? Give the number rounded "
                           "to 3 decimal places." % (len(metadata["nodes"]) - 1))
        if metadata["regime"] == "hwidth":
            return head + ("What is the half-width (absolute uncertainty) of the final output "
                           "n%d? Give the number rounded to 3 decimal places."
                           % (len(metadata["nodes"]) - 1))
        return head + ("Which single input contributes the most to the uncertainty of the final "
                       "output n%d? Name it by its single letter."
                       % (len(metadata["nodes"]) - 1))

    def generate_entry(self):
        cfg = self.config
        nleaf = min(cfg.num_inputs, 8)
        names = list(_NAME[:nleaf])
        for _trial in range(200):
            leaves = []
            for k, nm in enumerate(names):
                val = random.randint(2, 9)
                hw = random.randint(1, 3)
                leaves.append((nm, val, hw))
            nodes = []
            for _k in range(cfg.num_internal):
                lo = nleaf + _k
                ai = random.randint(0, lo - 1)
                bi = random.randint(0, lo - 2)
                if bi >= ai:
                    bi += 1
                op = random.choice(_OPS)
                mode = random.choice(_MODES)
                nodes.append((op, ai, bi, mode))
            res = _propagate(leaves, nodes)
            if res is None:
                continue
            values, hwidths = res
            if not all(math.isfinite(v) for v in values):
                continue
            if not all(math.isfinite(h) and h > 0 for h in hwidths):
                continue
            if abs(values[-1]) < 1e-9 or abs(values[-1]) > 1e7:
                continue
            grads = _gradients(leaves, nodes, values)
            contribs = [abs(g) * h for g, (_n, _v, h) in zip(grads, leaves)]
            dom = 0
            for i in range(1, nleaf):
                if contribs[i] > contribs[dom]:
                    dom = i
            root_val = values[-1]
            root_hw = hwidths[-1]
            # Defining-property assertions; reject if they ever fail.
            if contribs[dom] <= 0:
                continue
            if not (root_hw >= 0):
                continue
            entries = {
                "value": (root_val, _fmt(root_val)),
                "hwidth": (root_hw, _fmt(root_hw)),
                "dominant": (names[dom], names[dom]),
            }
            regime = random.choice(list(cfg.regimes))
            raw, ans = entries[regime]
            meta = {
                "leaves": [{"name": n, "value": v, "half_width": hw}
                           for (n, v, hw) in leaves],
                "nodes": [{"op": op, "a": ai, "b": bi, "mode": mode}
                          for (op, ai, bi, mode) in nodes],
                "regime": regime,
                "root_value": values[-1],
                "root_hwidth": hwidths[-1],
                "dominant": names[dom],
                "contribs": [float(c) for c in contribs],
                "leaf_grads": [float(g) for g in grads],
            }
            return Entry(metadata=meta, answer=ans)
        raise RuntimeError("could not generate a valid uncertainty DAG")


def _operand_label(meta, tidx):
    nleaf = len(meta["leaves"])
    if tidx < nleaf:
        return meta["leaves"][tidx]["name"]
    return "n" + str(tidx - nleaf)


def _render_dag(meta):
    lines = []
    for lf in meta["leaves"]:
        lines.append(f"  {lf['name']} = {lf['value']} ± {lf['half_width']}")
    lines.append("")
    opname = {'+': 'add', '-': 'subtract', '*': 'multiply', '/': 'divide'}
    for idx, nd in enumerate(meta["nodes"]):
        if nd['mode'] == 'lin':
            dep = ("these two operands' noises are fully dependent, so combine their "
                   "uncertainties by the worst-case linear rule, i.e. the half-widths add")
        else:
            dep = ("these two operands' noises are independent, so combine their "
                   "uncertainties by the root-sum-square rule, i.e. add the squares of the "
                   "half-widths and take the square root")
        lines.append(
            f"  n{idx} = {opname[nd['op']]} of {_operand_label(meta, nd['a'])} and "
            f"{_operand_label(meta, nd['b'])}; " + dep + "."
        )
    return "\n".join(lines)


def score_answer(answer, entry):
    meta = entry.metadata
    regime = meta["regime"]
    s = str(answer).strip()
    if regime == "dominant":
        return float(s == meta["dominant"])
    ref = float(meta["root_value"] if regime == "value" else meta["root_hwidth"])
    try:
        sub = float(s)
    except (ValueError, TypeError):
        return 0.0
    if not math.isfinite(sub):
        return 0.0
    return float(abs(sub - ref) <= 0.01 + 1e-4 * abs(ref))


TASK_META = {'parent_source_id': None,
 'idea': 'measurement_uncertainty_propagation (variant 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scientific_reasoning_r4/measurement_uncertainty_propagation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3867019559,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
