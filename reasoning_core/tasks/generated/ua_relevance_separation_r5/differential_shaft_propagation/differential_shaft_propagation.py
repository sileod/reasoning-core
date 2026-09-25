"""Differential shaft propagation: propagate exact rotations through external and internal gear
meshes, shared shafts and closed loops; answer queried shaft motion or LOCKED on conflict."""

import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'differential_shaft_propagation (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_relevance_separation_r5/differential_shaft_propagation',
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

_EXT_TEETH_A = (20, 24, 30, 36, 40, 48, 60)
_EXT_TEETH_B = (15, 18, 20, 24, 30, 36)
_INT_TEETH_A = (20, 24, 28, 32, 36)
_INT_TEETH_B = (48, 60, 72, 84, 90)


@dataclass
class ShaftPropagationConfig(Config):
    shafts: int = 3
    locked_prob: float = 0.35
    queries: int = 1

    def apply_difficulty(self, level):
        self.shafts = stochastic_rounding(self.shafts + level * 1.2)
        self.locked_prob = 0.14
        self.queries = 1 if level < 3 else 2


def solve(connections, n):
    """Return (locked, values) where values maps shaft idx -> Fraction rotation (relative to 0 at +1).

    connections: list of (a, b, R) with R a signed Fraction: rotation_b = R * rotation_a.
    Uses weighted union-find over ratio constraints; a same-root disagreement means a locked loop.
    """
    parent = list(range(n))
    weight = [Fraction(1)] * n  # value[x] = weight[x] * value[root(x)]

    def find(x):
        if parent[x] == x:
            return x, Fraction(1)
        r, w = find(parent[x])
        weight[x] = weight[x] * w
        parent[x] = r
        return r, weight[x]

    for (a, b, R) in connections:
        ra, wa = find(a)
        rb, wb = find(b)
        if ra == rb:
            # value[b] must equal R*value[a]
            if wb != R * wa:
                return True, None
            continue
        parent[rb] = ra
        # value[rb] = R*wa/wb * value[ra]
        weight[rb] = R * wa / wb

    # pin value[0] = 1
    r0, w0 = find(0)
    root_val = Fraction(1) / w0
    values = {}
    for k in range(n):
        rk, wk = find(k)
        if rk != r0:
            return False, None  # disconnected
        values[k] = wk * root_val
    return False, values


def make_edge(a, b, mode):
    """mode in {'ext','int','shaft'}; returns (a,b,R) and a description.",
    """
    if mode == 'shaft':
        return (a, b, Fraction(1)), ('shaft', None, None)
    if mode == 'ext':
        ta = random.choice(_EXT_TEETH_A)
        tb = random.choice(_EXT_TEETH_B)
        return (a, b, -Fraction(ta, tb)), ('ext', ta, tb)
    ta = random.choice(_INT_TEETH_A)
    tb = random.choice(_INT_TEETH_B)
    return (a, b, Fraction(ta, tb)), ('int', ta, tb)


class DifferentialShaftPropagation(Task):
    summary = ("Propagate exact rotations through external and internal gear meshes, shared shafts, "
               "closed loops, and identify incompatible imposed rotations; return queried shaft motion "
               "as a reduced fraction or the string LOCKED.")
    design_choice = ("Answer format: return the signed rotation count as a reduced fraction "
                     "for each queried shaft, or the string 'LOCKED' if any loop constraint fails.")
    config_cls = ShaftPropagationConfig

    def generate_entry(self):
        cfg = self.config
        for _ in range(300):
            entry = self._gen(cfg)
            if entry is not None:
                return entry
        raise RuntimeError("could not build a feasible instance")

    def _gen(self, cfg):
        n = int(cfg.shafts)
        if n < 3:
            return None
        nodes = list(range(1, n))
        random.shuffle(nodes)
        assigned = [0]
        connections = []
        descs = []
        # build a spanning tree over all shafts (guarantees connectivity)
        for v in nodes:
            u = random.choice(assigned)
            assigned.append(v)
            mode = random.choice(['ext', 'ext', 'ext', 'int', 'shaft'])
            (a, b, R), desc = make_edge(u, v, mode)
            connections.append((a, b, R))
            descs.append((a, b, desc))
        # decide locked vs solvable
        want_locked = random.random() < cfg.locked_prob
        if want_locked:
            u, v = random.sample(assigned, 2)
            if u == v:
                return None
            mode = random.choice(['ext', 'int'])
            (a, b, R), desc = make_edge(u, v, mode)
            trial = list(connections)
            trial.append((a, b, R))
            locked, _ = solve(trial, n)
            if not locked:
                return None  # the random extra mesh happened to be consistent; resample
            connections = trial
            descs.append((a, b, desc))
        # pick queries
        queries = random.sample(range(1, n), min(cfg.queries, n - 1))
        queries.sort()
        locked, values = solve(connections, n)
        if locked != want_locked:
            return None
        if locked:
            answer = "LOCKED"
            vals = None
        else:
            if values is None:
                return None
            if not all(-1000 < values[q].numerator < 1000 and 0 < values[q].denominator < 1000
                       for q in queries):
                return None
            vals = [(q, values[q].numerator, values[q].denominator) for q in queries]
            answer = ", ".join(_fmt(values[q]) for q in queries)
        conn_meta = []
        for (a, b, (kind, ta, tb)) in descs:
            conn_meta.append({'a': a, 'b': b, 'kind': kind, 'ta': ta, 'tb': tb})
        metadata = {
            "n": n,
            "connections": conn_meta,
            "queries": queries,
            "locked": locked,
            "values": vals,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = []
        for c in metadata['connections']:
            a, b, kind = c['a'], c['b'], c['kind']
            if kind == 'shaft':
                lines.append(f"shaft {b} is rigidly shared with shaft {a} (same rotation)")
            elif kind == 'ext':
                lines.append(f"an external gear mesh (teeth {c['ta']}:{c['tb']}) drives shaft {b} "
                             f"from shaft {a}, reversing direction")
            else:
                lines.append(f"an internal ring mesh (teeth {c['ta']}:{c['tb']}) drives shaft {b} "
                             f"from shaft {a}, same direction")
        conn_text = "\n".join(lines)
        qs = ", ".join(str(q) for q in metadata['queries'])
        return (
            f"A gear train has {metadata['n']} shafts numbered 0..{metadata['n'] - 1}. "
            f"Shaft 0 is driven at exactly one counterclockwise turn. For a mesh that reverses "
            f"direction, rotation_b = -(A/B)*rotation_a; an internal same-direction mesh gives "
            f"rotation_b = +(A/B)*rotation_a; a shared shaft gives equal rotation. Closed loops "
            f"are feasible only if every implied rotation agrees. Connections:\n{conn_text}\n"
            f"Give the signed rotation of shaft {qs}, each as a reduced fraction (a plain integer "
            f"such as 1 or -3 is allowed), or exactly the word LOCKED if no consistent rotation exists."
        )

    def score_answer(self, answer, entry):
        metadata = entry.metadata
        if metadata['locked']:
            return 1.0 if str(answer).strip().upper() == 'LOCKED' else 0.0
        queries = metadata['queries']
        expected = _query_fractions(metadata)
        try:
            got = parse_answer(answer, len(queries))
        except (ValueError, ZeroDivisionError, TypeError):
            return 0.0
        if got is None:
            return 0.0
        if len(got) != len(expected):
            return 0.0
        return 1.0 if all(g == e for (g, e) in zip(got, expected)) else 0.0


def _query_fractions(metadata):
    out = []
    for (q, num, den) in metadata['values']:
        out.append(Fraction(num, den))
    return out


def _fmt(fr):
    if fr.denominator == 1:
        return str(fr.numerator)
    return f"{fr.numerator}/{fr.denominator}"


def parse_answer(text, count):
    text = str(text).strip()
    if text.upper() == 'LOCKED':
        return None
    parts = [p.strip() for p in text.split(',')]
    if len(parts) != count:
        raise ValueError("count mismatch")
    return [to_fraction(p) for p in parts]


def to_fraction(tok):
    tok = tok.strip()
    if '/' in tok:
        num, den = tok.split('/', 1)
        return Fraction(int(num), int(den))
    return Fraction(int(tok))


