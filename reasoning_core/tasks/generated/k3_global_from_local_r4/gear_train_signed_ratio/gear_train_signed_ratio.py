"""Signed gear-train ratio solver: parse meshes, shafts and belts into one train and
report the output's signed rational speed or a jam verdict when parities clash."""

import random
from dataclasses import dataclass

from sympy import Rational

from reasoning_core.template import Config, Entry, Task


@dataclass
class GearTrainConfig(Config):
    min_len: int = 3
    max_len: int = 5
    max_teeth: int = 20
    diamond_p: float = 0.5
    consistent_p: float = 0.7

    def apply_difficulty(self, level):
        self.min_len = 3 + level
        self.max_len = 5 + level
        self.max_teeth = 20 + 8 * level
        self.diamond_p = 0.5
        self.consistent_p = 0.7


def _transmittance(kind, a, b):
    """Return (sign, numerator, denominator) for power a -> b through component `kind`.

    The sign is symmetric (a gear mesh reverses direction whether read up- or downstream),
    the magnitude is asymmetric: reading from x to y the ratio is x_count / y_count.
    """
    if kind == 'shaft':
        return (1, 1, 1)
    if kind == 'mesh':
        return (-1, a, b)
    if kind == 'openbelt':
        return (1, a, b)
    if kind == 'crossbelt':
        return (-1, a, b)
    raise ValueError(kind)


def _seg(config, u, v):
    """Build one oriented connection u -> v along the power-flow direction."""
    if random.random() < 0.15:
        return (u, v, 'shaft', 1, 1)
    kind = random.choice(['mesh', 'openbelt', 'crossbelt'])
    a = random.randint(3, config.max_teeth)
    b = random.randint(3, config.max_teeth)
    return (u, v, kind, a, b)


def _branch_product(edges):
    """Return (parity, Rational magnitude) of the product over oriented edges."""
    parity = 1
    rat = Rational(1)
    for _, _, kind, a, b in edges:
        sign, n, d = _transmittance(kind, a, b)
        parity *= sign
        rat *= Rational(n, d)
    return (parity, rat)


def _propagate(nnodes, edges, target, driver=0):
    """Solve shaft speeds from `driver` (set to +1) by propagation; return canonical
    signed ratio string of `target`, or 'jam' if two paths disagree."""
    omega = [None] * nnodes
    omega[driver] = Rational(1)
    adj = {i: [] for i in range(nnodes)}
    for u, v, kind, a, b in edges:
        sign, n, d = _transmittance(kind, a, b)
        adj[u].append((v, sign, n, d))
        adj[v].append((u, sign, d, n))
    stack = [driver]
    while stack:
        u = stack.pop()
        for v, ssign, snum, sden in adj[u]:
            cand = omega[u] * ssign * Rational(snum, sden)
            if omega[v] is None:
                omega[v] = cand
                stack.append(v)
            elif omega[v] != cand:
                return 'jam'
    if omega[target] is None:
        return 'jam'
    return str(omega[target])


class GearTrainSignedRatio(Task):
    summary = ("Gear meshes, shared shafts, and open or crossed belts forming one train: "
               "multiply pitch ratios and flip signs along each path from driver to output; "
               "answer the output's signed rational speed or a jam verdict when parities clash.")
    design_choice = ("Provide a diagram-like textual listing of meshes, shafts, and belts; "
                     "solver must parse the topology and return a canonical signed ratio "
                     "string like '3/2' or 'jam'.")
    config_cls = GearTrainConfig
    task_version = 2

    def generate_entry(self):
        config = self.config
        steps = random.randint(config.min_len, config.max_len)
        use_diamond = (random.random() < config.diamond_p) and steps >= 2
        consistent = (random.random() < config.consistent_p) if use_diamond else False

        if not use_diamond:
            edges = [_seg(config, k, k + 1) for k in range(steps)]
            output = steps
        else:
            pre = random.randint(0, steps - 1)
            post = steps - 1 - pre
            edges = []
            counter = 0
            prev = 0
            for _ in range(pre):
                nxt = counter + 1
                counter = nxt
                edges.append(_seg(config, prev, nxt))
                prev = nxt
            S = prev
            X = counter + 1
            Y = counter + 2
            T = counter + 3
            counter = T
            e1 = _seg(config, S, X)
            e2 = _seg(config, X, T)
            pX = _branch_product([e1, e2])
            if consistent:
                e3 = (S, Y, e1[2], e1[3], e1[4])
                e4 = (Y, T, e2[2], e2[3], e2[4])
            else:
                e3 = _seg(config, S, Y)
                e4 = _seg(config, Y, T)
                guard = 0
                while _branch_product([e3, e4]) == pX and guard < 25:
                    e3 = _seg(config, S, Y)
                    e4 = _seg(config, Y, T)
                    guard += 1
                if _branch_product([e3, e4]) == pX:
                    e4 = (Y, T, 'mesh' if e4[2] != 'mesh' else 'crossbelt', e4[3], e4[4] + 1)
            edges += [e1, e2, e3, e4]
            cur = T
            for _ in range(post):
                nxt = counter + 1
                counter = nxt
                edges.append(_seg(config, cur, nxt))
                cur = nxt
            output = cur

        answer = _propagate(output + 1, edges, output, driver=0)
        return Entry(
            metadata={
                "edges": [[u, v, k, a, b] for (u, v, k, a, b) in edges],
                "output": int(output),
                "driver": 0,
            },
            answer=str(answer),
        )

    def render_prompt(self, metadata):
        lines = [
            "A gear train drives an output shaft from a driver. The driver, shaft 0, is turned "
            "clockwise at speed 1.",
            "The connections of the train are:",
        ]
        for u, v, kind, a, b in metadata["edges"]:
            if kind == "mesh":
                lines.append(f"- shaft {u} meshes with shaft {v} (teeth {a} : {b})")
            elif kind == "shaft":
                lines.append(f"- shaft {u} and shaft {v} are mounted on one common shaft")
            elif kind == "openbelt":
                lines.append(f"- shaft {u} connects to shaft {v} with an open belt (pulleys {a} : {b})")
            else:
                lines.append(f"- shaft {u} connects to shaft {v} with a crossed belt (pulleys {a} : {b})")
        lines += [
            "Rules: a gear mesh transmits the ratio (teeth on the upstream shaft)/(teeth on the "
            "downstream shaft) and reverses direction; an open belt transmits the upstream/downstream "
            "pulley radii keeping direction; a crossed belt reverses direction; two gears on one common "
            "shaft share the same speed and direction (1:1).",
            f"The output is shaft {metadata['output']}. Give its signed speed as a reduced signed ratio "
            "like '3/2' or '-5/4', counting clockwise as positive. If the topology makes two routes from "
            "the driver to the output give clashing signs or ratios, answer with the single word 'jam'.",
        ]
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        return 1.0 if str(answer).strip() == str(entry.answer).strip() else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'gear_train_signed_ratio (variant 2 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_global_from_local_r4/gear_train_signed_ratio',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 241712510,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
