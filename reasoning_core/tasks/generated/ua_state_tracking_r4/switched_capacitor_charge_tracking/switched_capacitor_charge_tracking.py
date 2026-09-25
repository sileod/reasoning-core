"""Track ideal capacitors through plate reconnections, isolation, grounding, and voltage clamping.

A set of {\"unit\"} conducting nodes (plates) are connected by ideal capacitors with integer
capacitances. Node ``G`` is always grounded (zero voltage). The remaining nodes are floating
conductors that conserve their total integer charge in elementary-charge units. A sequence of
operations rewires the network: reconnecting two conductors merges them (charges add and their
capacitances combine), grounding a conductor attaches it to ``G``, and clamp sets a conductor to
a fixed integer voltage. After the operations the capacitive linear system is solved exactly; the
task asks for one queried plate's final charge as an integer number of elementary charges.
"""

import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Reward, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'switched_capacitor_charge_tracking (variant 1 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_state_tracking_r4/switched_capacitor_charge_tracking',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2409743872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

_NODE_NAMES = ["P", "Q", "R", "S", "T", "U", "V", "W"]


def _ek(a, b):
    return (a, b) if a < b else (b, a)


@dataclass
class SwitchedCapacitorConfig(Config):
    n_nodes: int = 2
    n_ops: int = 1
    cap_max: int = 2
    charge_range: int = 3
    clamp_range: int = 3
    n_edges_factor: int = 1

    def apply_difficulty(self, level: int):
        self.n_nodes = stochastic_rounding(self.n_nodes + level)
        self.n_ops = stochastic_rounding(self.n_ops + level)
        self.cap_max = stochastic_rounding(self.cap_max + level // 2)
        self.charge_range = stochastic_rounding(self.charge_range + level)
        self.clamp_range = stochastic_rounding(self.clamp_range + level // 2)


def _gauss(free_names, cons, clamp_v, cap_to, ground_v=0):
    """Solve for voltages of free nodes.

    free_names: ordered list of free node labels to solve for.
    cons: dict node -> conserved total charge Q (integer).
    clamp_v: dict node->fixed voltage (int) for clamped nodes.
    cap_to: dict (a, b) -> capacitance (int) between two nodes (may include 'G').
    Returns dict node -> Fraction voltage for free nodes.
    Equation for free node i: sum_j C_ij (V_i - V_j) = Q_i.
    """
    n = len(free_names)
    idx = {name: i for i, name in enumerate(free_names)}
    mat = [[Fraction(0)] * (n + 1) for _ in range(n)]
    for name in free_names:
        i = idx[name]
        total_cap = Fraction(0)
        for (a, b), c in cap_to.items():
            if a == name or b == name:
                total_cap += Fraction(c)
                other = b if a == name else a
                if other in idx and other != name:
                    mat[i][idx[other]] -= Fraction(c)
                elif other == "G":
                    mat[i][n] += Fraction(c) * Fraction(ground_v)
                elif other in clamp_v:
                    mat[i][n] += Fraction(c) * Fraction(clamp_v[other])
        mat[i][i] = total_cap
        mat[i][n] -= Fraction(cons[name])
    return _solve_frac(mat, free_names)


def _solve_frac(mat, names):
    """mat: augmented n x (n+1) Fraction matrix. Returns dict name->Fraction."""
    n = len(names)
    m = [row[:] for row in mat]
    for col in range(n):
        pivot = None
        for r in range(col, n):
            if m[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            for name in names:
                return None
        m[col], m[pivot] = m[pivot], m[col]
        piv = m[col][col]
        for cc in range(col, n + 1):
            m[col][cc] = m[col][cc] / piv
        for r in range(n):
            if r != col and m[r][col] != 0:
                factor = m[r][col]
                for cc in range(col, n + 1):
                    m[r][cc] = m[r][cc] - factor * m[col][cc]
    return {names[i]: m[i][n] for i in range(n)}


def _transport(nodes, cap_to, ops, clamped):
    """Apply ops to node charges, returning updated (nodes, cap_to, clamped).

    nodes: dict label -> state dict. keys 'G'(ground), free nodes {'kind':'free','q':int},
        ground {'kind':'ground'}, clamp {'kind':'clamp'}.
    cap_to: dict canonical edge (via _ek) -> int capacitance.
    ops: list of ('reconnect', a, b) | ('ground', a) | ('clamp', a, v).
    """
    for op in ops:
        kind = op[0]
        if kind == "reconnect":
            _, a, b = op
            nodes[b]["q"] += nodes[a]["q"]
            del nodes[a]
            to_merge = {e: c for e, c in cap_to.items() if a in e}
            for e, c in to_merge.items():
                other = e[0] if e[1] == a else e[1]
                del cap_to[e]
                if other == b:
                    continue
                key = _ek(b, other)
                cap_to[key] = cap_to.get(key, 0) + c
        elif kind == "ground":
            _, a = op
            nodes[a] = {"kind": "ground"}
        elif kind == "clamp":
            _, a, v = op
            nodes[a] = {"kind": "clamp"}
            clamped[a] = v
    return nodes, cap_to, clamped


def _build_instance(config):
    node_count = max(2, config.n_nodes)
    n_edges = max(1, node_count * config.n_edges_factor // 2 + 1)
    for _attempt in range(200):
        names = _NODE_NAMES[:node_count]
        nodes = {"G": {"kind": "ground"}}
        for nm in names:
            nodes[nm] = {"kind": "free", "q": random.randint(-config.charge_range,
                                                            config.charge_range)}
        cap_to = {}
        candidates = [_ek(a, b) for a in names + ["G"] for b in names if a != b]
        candidates = list(dict.fromkeys(candidates))
        random.shuffle(candidates)
        for e in candidates[:n_edges]:
            cap_to[e] = random.randint(1, config.cap_max)
        if not cap_to:
            continue
        ops = []
        free = list(names)
        for _ in range(config.n_ops):
            if free:
                action = random.choice(["reconnect", "ground", "clamp"])
                if action == "reconnect" and len(free) >= 2:
                    a = random.choice(free)
                    b = random.choice([x for x in free if x != a])
                    ops.append(("reconnect", a, b))
                    free.remove(a)
                elif action == "ground":
                    a = random.choice(free)
                    ops.append(("ground", a))
                    free.remove(a)
                else:
                    a = random.choice(free)
                    v = random.choice([x for x in range(-config.clamp_range,
                                                       config.clamp_range + 1) if x != 0])
                    ops.append(("clamp", a, v))
                    free.remove(a)
        clamped = {}
        cur_nodes = dict(nodes)
        cur_caps = dict(cap_to)
        _transport(cur_nodes, cur_caps, ops, clamped)
        # choose a query capacitor edge present in the final network
        if not cur_caps:
            continue
        (qa, qb) = random.choice(list(cur_caps.keys()))
        side = random.choice([qa, qb])
        q_c = cur_caps[(qa, qb)]
        # solve
        free_final = [nm for nm, info in cur_nodes.items()
                      if info["kind"] == "free"
                      and any(a == nm or b == nm for (a, b) in cur_caps)]
        cons = {nm: cur_nodes[nm]["q"] for nm in free_final}
        volt = _gauss(free_final, cons, clamped, cur_caps)
        if volt is None:
            continue
        clamp_v_all = dict(clamped)
        v_map = dict(volt)
        for nm, info in cur_nodes.items():
            if info["kind"] == "clamp":
                v_map[nm] = Fraction(clamp_v_all[nm])
            elif info["kind"] == "ground":
                v_map[nm] = Fraction(0)
        if side not in v_map or qa not in v_map or qb not in v_map:
            continue
        other = qb if side == qa else qa
        plate = q_c * (v_map[side] - v_map[other])
        if plate.denominator != 1:
            continue
        ans = int(plate)
        if ans == 0:
            continue
        return nodes, cap_to, ops, clamped, (qa, qb), side, q_c, ans
    raise RuntimeError("could not build a valid instance")


class SwitchedCapacitorChargeTracking(Task):
    summary = ("Track ideal capacitors through plate reconnections, isolation, grounding, and "
               "voltage clamping; conserve charge on floating conductors and return queried "
               "plate charges or capacitor voltages.")
    design_choice = ("Answer format: return the queried plate charge as an integer number of "
                     "elementary charges (e.g., '3'), with no units or sign conventions left "
                     "ambiguous.")
    config_cls = SwitchedCapacitorConfig

    def generate_entry(self):
        cfg = self.config
        nodes, cap_to, ops, clamped, (qa, qb), side, q_c, ans = _build_instance(cfg)
        payload = {
            "nodes": {nm: info["kind"] for nm, info in nodes.items()},
            "charges": {nm: info.get("q") for nm, info in nodes.items()},
            "caps": {f"{a}-{b}": c for (a, b), c in sorted(cap_to.items())},
            "ops": [list(o) for o in ops],
            "clamped": dict(clamped),
            "query_edge": f"{qa}-{qb}",
            "query_side": side,
        }
        return Entry(metadata=payload, answer=str(ans))

    def render_prompt(self, metadata):
        p = metadata
        caps_lines = []
        for key, c in sorted(p["caps"].items()):
            caps_lines.append(f"capacitor {key} has capacitance {c}")
        op_lines = []
        for o in p["ops"]:
            if o[0] == "reconnect":
                op_lines.append(f"reconnect conductors {o[1]} and {o[2]}")
            elif o[0] == "ground":
                op_lines.append(f"ground conductor {o[1]}")
            else:
                op_lines.append(f"clamp conductor {o[1]} to voltage {o[2]}")
        charge_parts = []
        for nm, q in sorted(p["charges"].items()):
            if q is not None:
                charge_parts.append(f"{nm} carries charge {q}")
        parts = [
            "Electric state tracking problem. A capacitor's plates hold equal and opposite "
            "charge; each conductor (a set of plates wired together) stays at a single voltage "
            "and conserves its total charge when it is a floating conductor.",
            "Conductors present at the start: " + ", ".join(
                f"{nm}" for nm in sorted(p["nodes"]) if nm != "G") + f". Ground conductor G is "
            "always at voltage 0 and can supply or absorb any charge.",
            "Capacitances:",
        ]
        parts.append(caps_lines and ("; ".join(caps_lines) + ".") or "none.")
        if charge_parts:
            parts.append("Initial floated charges: " + "; ".join(charge_parts) + ".")
        if op_lines:
            parts.append("Then, in order: " + "; ".join(op_lines) + ".")
        parts.append(
            f"You are asked for the charge on the {p['query_side']} plate of capacitor "
            f"{p['query_edge']} after all operations resolve.")
        parts.append("Charge is conserved and the network reaches electrostatic equilibrium. "
                     "Report that plate's charge as an integer number of elementary charges.")
        return "\n".join(parts)

    def score_answer(self, answer, entry):
        gold = int(entry.answer)
        text = str(answer).strip()
        try:
            val = int(text)
        except Exception:
            return Reward(0.0, reason="not-an-integer")
        return Reward(1.0 if val == gold else 0.0, reason="charge")
