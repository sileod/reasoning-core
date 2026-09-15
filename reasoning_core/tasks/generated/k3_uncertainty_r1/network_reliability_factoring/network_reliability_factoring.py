import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


TASK_META = {'parent_source_id': None,
 'idea': 'network_reliability_factoring (draw 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_uncertainty_r1/network_reliability_factoring',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class NetworkReliabilityConfig(Config):
    n_nodes: int = 4
    n_extra: int = 1
    probes: int = 2

    def apply_difficulty(self, level):
        self.n_nodes = 3 + stochastic_rounding(level * 1.5)
        self.n_extra = 1 + stochastic_rounding(level)


def _connects(edges, src, snk):
    adj = {}
    for a, b in edges:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    seen = {src}
    stack = [src]
    while stack:
        cur = stack.pop()
        for nxt in adj.get(cur, ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return snk in seen


def _bruteforce(edges, p, src, snk):
    names = list(edges.keys())
    n = len(names)
    total = Fraction(0)
    for mask in range(1 << n):
        prob = Fraction(1)
        present = []
        for i, nm in enumerate(names):
            if mask & (1 << i):
                prob *= p[nm]
                present.append(edges[nm])
            else:
                prob *= 1 - p[nm]
        if _connects(present, src, snk):
            total += prob
    return total


def _render_graph(edges, p, src, snk):
    edge_names = sorted(edges.keys())
    header = f"A network connects source node {src} to sink node {snk}. "
    body = " ".join(
        f"edge {name} joins node {edges[name][0]} to node {edges[name][1]} "
        f"and works with probability {p[name]}"
        for name in edge_names
    )
    return header + body + "."


def _series_parallel_reduce(edges, p, src, snk):
    edges = {k: (v[0], v[1]) for k, v in edges.items()}
    p = {k: v for k, v in p.items()}
    while True:
        reduced = False
        for name, (a, b) in list(edges.items()):
            for endpoint, other in ((a, b), (b, a)):
                if endpoint in (src, snk):
                    continue
                deg = sum(1 for (x, y) in edges.values() if x == endpoint or y == endpoint)
                if deg == 1:
                    del edges[name]
                    del p[name]
                    for n2, (x, y) in list(edges.items()):
                        if x == endpoint:
                            edges[n2] = (other, y)
                        elif y == endpoint:
                            edges[n2] = (x, other)
                    reduced = True
                    break
            if reduced:
                break
        if reduced:
            continue
        pairs = {}
        for name, (a, b) in edges.items():
            pairs.setdefault((a, b), []).append(name)
        merged = False
        for key, names in pairs.items():
            if len(names) > 1:
                keep = names[0]
                fail = Fraction(1)
                for nm in names:
                    fail *= 1 - p[nm]
                p[keep] = 1 - fail
                for nm in names[1:]:
                    del edges[nm]
                    del p[nm]
                merged = True
                break
        if merged:
            continue
        series = False
        series_node = None
        for nm, (a, b) in edges.items():
            for node, _other in ((a, b), (b, a)):
                if node in (src, snk):
                    continue
                deg = sum(1 for (x, y) in edges.values() if x == node or y == node)
                if deg == 2:
                    series_node = node
                    break
            if series_node is not None:
                break
        if series_node is not None:
            inc = [nm for nm, (x, y) in edges.items() if x == series_node or y == series_node]
            n1, n2 = inc[0], inc[1]
            e1, e2 = edges[n1], edges[n2]
            o1 = e1[1] if e1[0] == series_node else e1[0]
            o2 = e2[1] if e2[0] == series_node else e2[0]
            p[n1] = p[n1] * p[n2]
            edges[n1] = (o1, o2)
            del edges[n2]
            del p[n2]
            series = True
        if not series:
            break
    return edges, p


def _reliability(edges, p, src, snk):
    edges = {k: (v[0], v[1]) for k, v in edges.items()}
    p = {k: v for k, v in p.items()}
    memo = {}

    def rec(edges, p, src, snk):
        edges = {k: (v[0], v[1]) for k, v in edges.items()}
        p = {k: v for k, v in p.items()}
        edges, p = _series_parallel_reduce(edges, p, src, snk)
        if src == snk:
            return Fraction(1)
        if not edges:
            return Fraction(0)
        incident = [nm for nm, (a, b) in edges.items() if a == src or b == src]
        if not incident:
            return Fraction(0)
        key = (tuple(sorted(edges.items())), tuple(sorted(p.items())), src, snk)
        if key in memo:
            return memo[key]
        keystone = incident[0]
        ka, kb = edges[keystone]
        pe = p[keystone]
        ce = {nm: (a, b) for nm, (a, b) in edges.items() if nm != keystone}
        cp = {nm: v for nm, v in p.items() if nm != keystone}
        for nm, (a, b) in list(ce.items()):
            na = ka if a == kb else a
            nb = ka if b == kb else b
            ce[nm] = (na, nb)
        cedges = {nm: e for nm, e in ce.items() if e[0] != e[1]}
        cp = {nm: v for nm, v in cp.items() if nm in cedges}
        nsrc = ka if src == kb else src
        nsnk = ka if snk == kb else snk
        p_work = rec(cedges, cp, nsrc, nsnk)
        de = {nm: (a, b) for nm, (a, b) in edges.items() if nm != keystone}
        dp = {nm: v for nm, v in p.items() if nm != keystone}
        p_broken = rec(de, dp, src, snk)
        res = pe * p_work + (1 - pe) * p_broken
        memo[key] = res
        return res

    return rec(edges, p, src, snk)


class NetworkReliabilityFactoring(Task):
    summary = ("Compute the exact probability a source reaches its sink when components fail "
               "independently at given rates: collapse series-parallel pairs, factor on a "
               "keystone component, and recurse over both cases to report the network "
               "reliability, exact as a reduced fraction.")
    design_choice = ("Represent each component as an ordered pair (failure probability, success "
                     "probability) and combine series/parallel reductions using exact rational "
                     "arithmetic to avoid floating-point drift.")
    config_cls = NetworkReliabilityConfig

    def generate_entry(self):
        config = self.config
        for _ in range(40):
            result = self._attempt(config)
            if result is not None:
                return result
        raise RuntimeError("could not generate a valid network reliability instance")

    def _attempt(self, config):
        n_nodes = config.n_nodes
        n_edges = n_nodes - 1 + config.n_extra
        nodes = [f"n{i}" for i in range(n_nodes)]
        src, snk = "n0", f"n{n_nodes - 1}"

        edges = {}
        p = {}
        used = set()
        idx = 0
        for i in range(n_nodes - 1):
            name = f"e{idx}"
            idx += 1
            edges[name] = (nodes[i], nodes[i + 1])
            p[name] = Fraction(random.choice([1, 2, 3, 4, 5, 6, 7, 8]), 10)
            used.add((nodes[i], nodes[i + 1]))

        tries = 0
        while len(edges) < n_edges and tries < 200:
            tries += 1
            a = random.choice(nodes)
            b = random.choice(nodes)
            if a == b:
                continue
            if (a, b) in used or (b, a) in used:
                continue
            name = f"e{idx}"
            idx += 1
            edges[name] = (a, b)
            p[name] = Fraction(random.choice([1, 2, 3, 4, 5, 6, 7, 8]), 10)
            used.add((a, b))

        if len(edges) < n_edges:
            return None

        gold = _reliability(edges, p, src, snk)
        if not (Fraction(0) <= gold <= Fraction(1)):
            return None
        if gold == 0 or gold == 1:
            return None

        prompt = _render_graph(edges, p, src, snk)
        prompt += (f" Each edge works or fails independently. Report the exact probability that "
                   f"a working path exists between source node {src} and sink node {snk}, "
                   f"as a reduced fraction p/q.")
        answer = f"{gold.numerator}/{gold.denominator}"
        return Entry(metadata={"edges": {k: list(v) for k, v in edges.items()},
                               "p": {k: f"{p[k]}" for k in p},
                               "src": src, "snk": snk,
                               "gold_num": gold.numerator,
                               "gold_den": gold.denominator},
                     answer=answer)

    def render_prompt(self, metadata):
        edges = {k: tuple(v) for k, v in metadata["edges"].items()}
        p = {k: Fraction(v) for k, v in metadata["p"].items()}
        src, snk = metadata["src"], metadata["snk"]
        prompt = _render_graph(edges, p, src, snk)
        prompt += (f" Each edge works or fails independently. Report the exact probability that "
                   f"a working path exists between source node {src} and sink node {snk}, "
                   f"as a reduced fraction p/q.")
        return prompt

    def score_answer(self, answer, entry):
        import re
        if not isinstance(answer, str):
            return 0.0
        s = answer.strip()
        m = re.fullmatch(r"(\d+)\s*/\s*(\d+)", s)
        if not m:
            return 0.0
        try:
            val = Fraction(int(m.group(1)), int(m.group(2)))
        except ZeroDivisionError:
            return 0.0
        return 1.0 if val == Fraction(entry.metadata['gold_num'], entry.metadata['gold_den']) else 0.0
