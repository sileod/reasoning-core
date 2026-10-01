"""Solve a resistor netlist exactly: equivalent resistance, or the current through one resistor.

Reworked from the generated resistor_networks (ext #7, margin #2 on v8_tiny). That version only
built series/parallel trees described in prose, which reduce by two rules applied bottom-up.
Here the circuit is a netlist on a random connected graph: cycles and bridges (a Wheatstone
bridge is the smallest case) do not reduce by series/parallel steps, and dead-end branches carry
no current. The gold answer comes from nodal analysis over Fractions, so it is exact.
"""
import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, DevTask, Entry, edict, stochastic_rounding as sround

OHMS = [1, 2, 3, 4, 5, 6, 8, 10, 12]


@dataclass
class ResistorCircuitsConfig(Config):
    n_nodes: int = 3
    extra_edges: int = 1
    max_denominator: int = 60

    def apply_difficulty(self, level):
        self.n_nodes = 3 + sround(0.8 * level)
        self.extra_edges = 1 + sround(0.8 * level)
        self.max_denominator = 60 + 40 * level


def _potentials(n, edges, s, t):
    """Node potentials with t grounded and 1 A injected at s (so v[s] is the s-t resistance)."""
    idx = [i for i in range(n) if i != t]
    pos = {v: k for k, v in enumerate(idx)}
    m = len(idx)
    a = [[Fraction(0)] * (m + 1) for _ in range(m)]
    for u, v, r in edges:
        g = Fraction(1, r)
        for x, y in ((u, v), (v, u)):
            if x != t:
                a[pos[x]][pos[x]] += g
                if y != t:
                    a[pos[x]][pos[y]] -= g
    a[pos[s]][m] = Fraction(1)
    for c in range(m):
        p = next((r for r in range(c, m) if a[r][c] != 0), None)
        if p is None:
            return None
        a[c], a[p] = a[p], a[c]
        for r in range(m):
            if r != c and a[r][c] != 0:
                f = a[r][c] / a[c][c]
                a[r] = [x - f * y for x, y in zip(a[r], a[c])]
    v = [Fraction(0)] * n
    for i in idx:
        v[i] = a[pos[i]][m] / a[pos[i]][pos[i]]
    return v


def _fmt(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def _is_series_parallel(n, edges, s, t):
    """True if repeated series/parallel merges reduce the circuit to one s-t resistor."""
    es = [(u, v) for u, v, _ in edges]
    changed = True
    while changed:
        changed = False
        seen = {}
        for i, (u, v) in enumerate(es):
            key = (min(u, v), max(u, v))
            if key in seen:
                es.pop(i)
                changed = True
                break
            seen[key] = i
        if changed:
            continue
        deg = {}
        for u, v in es:
            deg[u] = deg.get(u, 0) + 1
            deg[v] = deg.get(v, 0) + 1
        for x, d in deg.items():
            if x in (s, t) or d > 2:
                continue
            ends = [e for e in es if x in e]
            es = [e for e in es if x not in e]
            if d == 2:
                (a, b), (c, d2) = ends
                es.append((a if b == x else b, c if d2 == x else d2))
            changed = True
            break
    return len(es) == 1


class ResistorCircuits(DevTask):
    summary = ("Given a resistor netlist on a connected graph (series, parallel, bridges, dead ends), "
               "report the exact equivalent resistance between two nodes, or the signed current "
               "through one resistor when a voltage is applied, as an integer or reduced fraction.")
    config_cls = ResistorCircuitsConfig
    task_version = 1

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_nodes
        edges = [(i, random.randrange(i), random.choice(OHMS)) for i in range(1, n)]
        for _ in range(cfg.extra_edges):
            u, v = random.sample(range(n), 2)
            edges.append((u, v, random.choice(OHMS)))
        random.shuffle(edges)
        s, t = random.sample(range(n), 2)
        pot = _potentials(n, edges, s, t)
        if pot is None:
            return None
        r_eq = pot[s]
        if random.random() < 0.5:
            mode, answer = "resistance", r_eq
        else:
            volts = random.choice([6, 10, 12, 24])
            # Dead ends carry no current; asking about them would make "0" a free answer.
            live = [k for k, (u, v, _) in enumerate(edges) if pot[u] != pot[v]]
            k = random.choice(live)
            u, v, r = edges[k]
            current = (pot[u] - pot[v]) * volts / r_eq / r
            mode, answer = ("current", k, volts), current
        if answer.denominator > cfg.max_denominator or abs(answer.numerator) > 10 * cfg.max_denominator:
            return None
        names = "ABCDEFGHIJKL"
        netlist = [f"R{i + 1}: {r} ohm between {names[u]} and {names[v]}" for i, (u, v, r) in enumerate(edges)]
        meta = edict(netlist=netlist, s=names[s], t=names[t], mode=mode,
                     series_parallel=_is_series_parallel(n, edges, s, t))
        return Entry(metadata=meta, answer=_fmt(answer))

    def render_prompt(self, m):
        head = "A circuit is made of these resistors (nodes are letters):\n" + "\n".join(m.netlist) + "\n\n"
        if m.mode == "resistance":
            q = f"What is the equivalent resistance, in ohms, between nodes {m.s} and {m.t}?"
        else:
            _, k, volts = m.mode
            name = m.netlist[k].split(":")[0]
            first, second = m.netlist[k].split("between ")[1].split(" and ")
            q = (f"A {volts} V source holds node {m.s} at {volts} V above node {m.t}; nothing else is connected. "
                 f"What is the current, in amperes, through {name} flowing from {first} to {second}? "
                 "It is negative if the current flows the other way.")
        return head + q + " Give an exact integer or a reduced fraction such as 7/3."

    def score_answer(self, answer, entry):
        try:
            return float(Fraction(str(answer).strip().rstrip(".").replace(" ", "")) == Fraction(entry.answer))
        except (ValueError, ZeroDivisionError):
            return 0.0
