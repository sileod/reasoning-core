import random
from dataclasses import dataclass

from sympy import Rational

from reasoning_core.template import Config, Entry, Task


def _rng_frac():
    while True:
        v = random.randrange(1, 10)
        if v < 9:
            return Rational(v, 10)


def _product(states):
    result = [()]
    for s in states:
        result = [r + (x,) for r in result for x in s]
    return result


@dataclass
class BayesianNetworkTableConversionConfig(Config):
    n_nodes: int = 3
    max_parents: int = 2
    num_states: int = 2
    query_vars_low: int = 1
    query_vars_high: int = 1

    def apply_difficulty(self, level):
        self.n_nodes = 2 + min(level, 3)
        self.max_parents = 1 + (level // 3)
        self.num_states = 2 + (1 if level >= 6 else 0)
        self.query_vars_low = 1
        self.query_vars_high = min(self.n_nodes - 1, 1 + (level // 2))


TASK_META = {'parent_source_id': None,
 'idea': 'bayesian_network_table_conversion (draw 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_semantics_preserving_translation_r1/bayesian_network_table_conversion',
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


class BayesianNetworkTableConversion(Task):
    summary = "Convert a small Bayesian network's conditional probability tables to its full joint table and back over a fixed variable order, with exact rational entries; answer a marginal probability over a queried partial assignment."
    design_choice = "Answers are a single rational probability per queried joint row, with the query specifying a partial assignment and the solver marginalizing over unlisted variables."
    config_cls = BayesianNetworkTableConversionConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_nodes
        ns = cfg.num_states
        order = list(range(n))

        parents = {}
        for v in range(n):
            possible = list(range(v))
            cnt = random.randint(0, min(len(possible), cfg.max_parents))
            parents[v] = sorted(random.sample(possible, k=cnt))

        cpts = {}
        for v in range(n):
            ps = parents[v]
            npa = ns ** len(ps) if ps else 1
            table = {}
            for pa_idx in range(npa):
                table[pa_idx] = _rng_frac()
            cpts[v] = table

        joint_entries = {}
        states = [list(range(ns)) for _ in range(n)]
        for assignment in _product(states):
            p = Rational(1)
            for v in range(n):
                ps = parents[v]
                base = 0
                if ps:
                    for e, pa in enumerate(ps):
                        base += assignment[pa] * (ns ** e)
                p0 = cpts[v][base]
                p *= (p0 if assignment[v] == 0 else (1 - p0))
            joint_entries[tuple(assignment)] = p

        total = sum(joint_entries.values())
        if total <= 0:
            raise RuntimeError("degenerate joint")

        q = random.randint(cfg.query_vars_low, cfg.query_vars_high)
        q_vars = sorted(random.sample(order, k=q))
        q_vals = tuple(random.randint(0, ns - 1) for _ in q_vars)
        q_assignment = dict(zip(q_vars, q_vals))

        numer = Rational(0)
        for assignment, p in joint_entries.items():
            if all(assignment[v] == q_assignment[v] for v in q_vars):
                numer += p

        marg = numer / total
        if not (0 <= marg <= 1):
            raise RuntimeError("invalid probability")

        metadata = {
            "n_nodes": n,
            "order": order,
            "num_states": ns,
            "parents": {str(v): ps for v, ps in parents.items()},
            "cpts": {str(v): {str(k): str(val) for k, val in table.items()} for v, table in cpts.items()},
            "query_vars": q_vars,
            "query_vals": q_vals,
            "answer": str(marg),
        }
        return Entry(metadata=metadata, answer=str(marg))

    def render_prompt(self, metadata):
        order = metadata["order"]
        ns = metadata["num_states"]
        lines = []
        lines.append(
            f"A Bayesian network has variables {order} over states 0..{ns - 1} in that fixed order. "
            "Each node's table gives P(node state = 0 | parent states); the complementary mass is on state 1.")
        for v in order:
            ps = metadata["parents"][str(v)]
            table = metadata["cpts"][str(v)]
            if not ps:
                lines.append(f"P({v}=0) = {table['0']}.")
            else:
                desc = []
                npa = ns ** len(ps)
                for pa_idx in range(npa):
                    rem = pa_idx
                    pa_vals = []
                    for _ in range(len(ps)):
                        pa_vals.append(rem % ns)
                        rem //= ns
                    pa_vals = tuple(pa_vals)
                    desc.append(f"{table[str(pa_idx)]} when parents {tuple(ps)} = {pa_vals}")
                lines.append(f"P({v}=0 | parents) = " + "; ".join(desc) + ".")
        qv = metadata["query_vars"]
        qval = metadata["query_vals"]
        assignment = ", ".join(f"{v}={val}" for v, val in zip(qv, qval))
        lines.append(f"Marginalize over all unlisted variables. What is P({assignment})?")
        lines.append("Answer as an exact rational a/b.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        try:
            expected = Rational(entry.metadata["answer"])
        except Exception:
            return 0.0
        try:
            got = Rational(str(answer).strip())
        except Exception:
            return 0.0
        return 1.0 if got == expected else 0.0

    def distractor_candidates(self, entry):
        yield "0"
        yield "1"
        yield "1/2"
