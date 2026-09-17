import itertools
import random
import re
from dataclasses import dataclass
from fractions import Fraction
from math import prod

import numpy as np

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'factor_graph_marginal (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_novel_composition_r2/factor_graph_marginal',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1336314872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class FactorGraphMarginalV2Config(Config):
    n_vars: int = 4
    max_extra: int = 1
    ternary_domains: int = 0

    def apply_difficulty(self, level):
        self.n_vars = min(8, 4 + int((level + 1) // 2))
        self.max_extra = min(3, 1 + int(level / 2))
        self.ternary_domains = min(2, int(level / 3))


def _eliminate(domains, factors, evidence, query, order):
    remaining = set(domains) - set(evidence) - {query}
    assert len(order) == len(remaining) and set(order) == remaining
    work = []
    for factor in factors:
        scope = factor["vars"]
        array = np.array(factor["table"], dtype=object).reshape(
            tuple(domains[v] for v in scope))
        array = array[tuple(evidence.get(v, slice(None)) for v in scope)]
        work.append(([v for v in scope if v not in evidence], np.asarray(array)))
    for variable in order:
        bucket = [(s, a) for s, a in work if variable in s]
        work = [(s, a) for s, a in work if variable not in s]
        union = sorted({v for scope, _ in bucket for v in scope})
        joint = np.ones(tuple(domains[v] for v in union), dtype=object)
        for scope, array in bucket:
            axes = sorted(range(len(scope)), key=lambda i: union.index(scope[i]))
            shape = tuple(domains[v] if v in scope else 1 for v in union)
            joint *= array.transpose(axes).reshape(shape)
        axis = union.index(variable)
        work.append(([v for v in union if v != variable], joint.sum(axis=axis)))
    weights = np.ones(domains[query], dtype=object)
    for scope, array in work:
        assert scope == [] or scope == [query]
        weights *= array
    return [int(w) for w in weights]


def _enumerate(domains, factors, evidence, query):
    lookups = []
    for factor in factors:
        scope = factor["vars"]
        keys = itertools.product(*(range(domains[v]) for v in scope))
        lookups.append((scope, dict(zip(keys, factor["table"]))))
    names = list(domains)
    choices = [[evidence[v]] if v in evidence else range(domains[v]) for v in names]
    weights = [0] * domains[query]
    for values in itertools.product(*choices):
        assignment = dict(zip(names, values))
        weight = prod(table[tuple(assignment[v] for v in scope)] for scope, table in lookups)
        weights[assignment[query]] += weight
    return weights


def _factor_table(scope, domains):
    shape = tuple(domains[v] for v in scope)
    for _ in range(64):
        table = [random.randint(1, 5) for _ in range(prod(shape))]
        array = np.array(table, dtype=object).reshape(shape)
        if len(scope) == 1:
            return table
        interacting = True
        for axis, size in enumerate(shape):
            matrix = np.moveaxis(array, axis, 0).reshape(size, -1)
            if np.all(matrix * matrix[0, 0] == matrix[:, :1] * matrix[:1, :]):
                interacting = False
                break
        if interacting:
            return table
    raise RuntimeError("failed to draw an interacting factor")


def _connected_count(scopes, evidence, query):
    reached = {query}
    while True:
        before = len(reached)
        for scope in scopes:
            free = set(scope) - set(evidence)
            if free & reached:
                reached.update(free)
        if len(reached) == before:
            return len(reached)


def _parse_table(answer):
    if not isinstance(answer, str) or len(answer) > 2048:
        raise ValueError("invalid table")
    parts = answer.strip().split(",")
    if not all(re.fullmatch(r"[0-9]+(?:/[1-9][0-9]*)?", p.strip()) for p in parts):
        raise ValueError("expected comma-separated nonnegative rational numbers")
    return [Fraction(p.strip()) for p in parts]


class FactorGraphMarginal(Task):
    summary = "Compute exact single-variable marginals in discrete factor graphs by variable elimination with randomized orders, over tree and loopy topologies, unary to ternary factors, binary and ternary domains, and absent or partial evidence; answer with the marginal probability table."
    design_choice = "Vary the variable ordering for elimination per instance, chosen deterministically from a seeded random, to test robustness against suboptimal orderings."
    config_cls = FactorGraphMarginalV2Config
    task_version = 2

    def generate_entry(self):
        for _ in range(64):
            n = random.randint(self.config.n_vars, min(8, self.config.n_vars + 1))
            names = [chr(65 + i) for i in range(n)]
            domains = dict.fromkeys(names, 2)
            for v in random.sample(names, random.randint(0, self.config.ternary_domains)):
                domains[v] = 3
            growth = random.sample(names, n)
            scopes = [[v] for v in names]
            i = 1
            while i < n:
                count = random.randint(1, min(2, n - i))
                scopes.append([random.choice(growth[:i])] + growth[i:i + count])
                i += count
            topology = random.choice(["tree", "loopy"])
            if topology == "loopy":
                for _ in range(random.randint(1, self.config.max_extra)):
                    scopes.append(random.sample(names, random.randint(2, 3)))
            for scope in scopes:
                random.shuffle(scope)
            query = random.choice(names)
            observed = random.sample([v for v in names if v != query], random.randint(0, min(2, n - 3)))
            evidence = {v: random.randrange(domains[v]) for v in sorted(observed)}
            if _connected_count(scopes, evidence, query) < 3:
                continue
            factors = [{"vars": scope, "table": _factor_table(scope, domains)} for scope in scopes]
            order = [v for v in names if v != query and v not in evidence]
            random.shuffle(order)
            weights = _eliminate(domains, factors, evidence, query, order)
            checked = _enumerate(domains, factors, evidence, query)
            assert weights == checked
            total = sum(weights)
            assert total > 0
            marginal = [Fraction(w, total) for w in weights]
            assert sum(marginal) == 1 and all(0 <= p <= 1 for p in marginal)
            assert all(p * total == w for p, w in zip(marginal, checked))
            return Entry(metadata={
                "domains": domains, "factors": factors, "evidence": evidence,
                "query": query, "elimination_order": order, "topology": topology,
                "weights": weights, "normalizer": total,
            }, answer=", ".join(str(p) for p in marginal))
        raise RuntimeError("failed to generate a graph with three interacting unobserved variables")

    def render_prompt(self, metadata):
        domains = metadata["domains"]
        lines = [
            "Infer the distribution of one hidden variable in this discrete factor graph.",
            "Domains: " + "; ".join(f"{v}=0..{d - 1}" for v, d in domains.items()) + ".",
            "Each factor lists nonnegative unnormalized weights in lexicographic order of "
            "its displayed arguments' value tuples (last argument changes fastest). "
            "For binary (A,B), the order is (0,0),(0,1),(1,0),(1,1).",
        ]
        for i, factor in enumerate(metadata["factors"]):
            lines.append(f"f{i}({','.join(factor['vars'])}) = " + ", ".join(map(str, factor["table"])))
        evidence = metadata["evidence"]
        lines.append("Evidence: " + (", ".join(f"{v}={x}" for v, x in evidence.items()) if evidence else "none") + ".")
        lines.extend([
            "An assignment's weight is the product of all listed factors. Condition on "
            "the evidence by discarding inconsistent assignments, then normalize the remaining weights.",
            f"Compute the exact marginal of {metadata['query']}. Use variable elimination: "
            "first substitute evidence, then sum out " + ", ".join(metadata["elimination_order"]) + " in that order; "
            "retain the query variable and normalize.",
            "Return only its probabilities for values 0,1,... in increasing value order, "
            "as reduced fractions (integers when integral) separated by commas. Format example: 1/3, 2/3.",
        ])
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        try:
            return float(_parse_table(answer) == _parse_table(entry.answer))
        except (ValueError, ZeroDivisionError, TypeError, OverflowError):
            return 0.0
