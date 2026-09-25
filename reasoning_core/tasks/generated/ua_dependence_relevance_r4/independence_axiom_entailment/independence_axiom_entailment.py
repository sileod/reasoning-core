import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'independence_axiom_entailment (variant 1 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_dependence_relevance_r4/independence_axiom_entailment',
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


def _subsets(nonempty_nonfull):
    """Yield all nonempty proper subsets of a sorted tuple as frozensets."""
    t = tuple(sorted(nonempty_nonfull))
    out = []
    m = len(t)
    for mask in range(1, (1 << m) - 1):
        out.append(frozenset(t[i] for i in range(m) if (mask >> i) & 1))
    return out


def _canon(a, b, c):
    return (frozenset(a), frozenset(b), frozenset(c))


def _axiom_closure(premises, universe, positive):
    """Semi-graphoid closure of CI statements over universe (a set-like frozenset)."""
    closed = set()
    for a, b, c in premises:
        closed.add(_canon(a, b, c))

    changed = True
    while changed:
        changed = False
        items = list(closed)

        for fa, fb, fc in items:
            # symmetry
            nc = _canon(fb, fa, fc)
            if nc not in closed:
                closed.add(nc)
                changed = True

            # decomposition: (A; B1 | C) for nonempty B1 subset of B
            for b1 in _subsets(fb):
                nc = _canon(fa, b1, fc)
                if nc not in closed:
                    closed.add(nc)
                    changed = True

            # weak union: (A; B\B1 | C U B1), nonempty B1 proper subset of B
            for b1 in _subsets(fb):
                b2 = fb - b1
                if b2:
                    nc = _canon(fa, b2, fc | b1)
                    if nc not in closed:
                        closed.add(nc)
                        changed = True

        if positive:
            items = list(closed)
            for fa, fb, fc in items:
                rem = frozenset(universe) - (fa | fb | fc)
                for d in rem:
                    # intersection: (A,B|CUD) & (A,D|CUB) -> (A,BUD|C)
                    k1 = _canon(fa, fb, fc | {d})
                    k2 = _canon(fa, {d}, fc | fb)
                    if k1 in closed and k2 in closed:
                        nc = _canon(fa, fb | {d}, fc)
                        if nc not in closed:
                            closed.add(nc)
                            changed = True
    return closed


def _entails(premises, query, universe, positive):
    closed = _axiom_closure(premises, universe, positive)
    return _canon(query[0], query[1], query[2]) in closed


@dataclass
class IndependenceConfig(Config):
    n_vars: int = 4
    n_premises: int = 3

    def apply_difficulty(self, level):
        self.n_vars = 4 + (level // 2)
        self.n_premises = 3 + (level // 2)


class IndependenceAxiomEntailment(Task):
    summary = ("Derive conditional independence claims from supplied premises using "
               "symmetry, decomposition, weak union, and contraction, with intersection "
               "enabled only under positivity; answer which queries follow.")
    design_choice = ("Queries are yes/no on whether each conditional independence statement "
                     "follows; premises are fixed-size lists of triples over a small variable set.")
    config_cls = IndependenceConfig

    def generate_entry(self):
        n = self.config.n_vars
        varset = list(range(1, n + 1))
        universe = frozenset(varset)

        for _ in range(300):
            premises = []
            for _prem in range(self.config.n_premises):
                perm = random.sample(varset, len(varset))
                s1 = random.randint(1, len(perm) - 2)
                s2 = random.randint(s1 + 1, len(perm) - 1)
                premises.append((frozenset(perm[:s1]),
                                 frozenset(perm[s1:s2]),
                                 frozenset(perm[s2:])))

            positive = random.random() < 0.5
            target = random.random() < 0.5
            clos = _axiom_closure(premises, universe, positive)

            follow = target
            if follow:
                # pick a genuinely derived statement to make it a positive instance
                derived = list(clos)
                if not derived:
                    continue
                fa, fb, fc = random.choice(derived)
            else:
                # pick a statement provably not entailed
                found = False
                for _r in range(50):
                    perm = random.sample(varset, len(varset))
                    s1 = random.randint(1, len(perm) - 2)
                    s2 = random.randint(s1 + 1, len(perm) - 1)
                    cand = (frozenset(perm[:s1]), frozenset(perm[s1:s2]), frozenset(perm[s2:]))
                    if _canon(*cand) not in clos:
                        fa, fb, fc = cand
                        found = True
                        break
                if not found:
                    continue

            answer = "yes" if follow else "no"
            metadata = {
                "premises": [[sorted(a), sorted(b), sorted(c)] for a, b, c in premises],
                "query": [sorted(fa), sorted(fb), sorted(fc)],
                "positive": positive,
            }
            return Entry(metadata=metadata, answer=answer)

        raise RuntimeError("Could not generate an independence entailment instance")

    def render_prompt(self, metadata):
        lines = ["Given the following conditional independence statements over a set of "
                 "variables U, where (A ; B | C) means A is conditionally independent of "
                 "B given C, and the three sets in each statement are pairwise disjoint and "
                 "nonempty, together, they cover nothing in particular:"]
        for a, b, c in metadata["premises"]:
            lines.append(f"  {_fmt(a)} ; {_fmt(b)} | {_fmt(c)}")
        if metadata["positive"]:
            lines.append("Assume the underlying distribution is strictly positive "
                         "(so the intersection axiom applies).")
        qa, qb, qc = metadata["query"]
        lines.append("")
        lines.append("Using the graphoid axioms (symmetry, decomposition, weak union, "
                     "contraction, and intersection only when positivity holds), decide "
                     "whether each statement below follows from the premises.")
        lines.append(f"Statement: {_fmt(qa)} ; {_fmt(qb)} | {_fmt(qc)}")
        lines.append("Respond with the word yes when it follows and the word no when it "
                     "does not follow.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        norm = answer.strip().lower()
        if norm in ("yes", "true"):
            norm = "yes"
        elif norm in ("no", "false"):
            norm = "no"
        else:
            return 0.0
        return 1.0 if norm == entry.answer else 0.0


def _fmt(s):
    if not s:
        return "{}"
    return "{" + ",".join(sorted(str(x) for x in s)) + "}"
