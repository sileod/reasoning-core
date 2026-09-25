import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


def closure_added_rows(determinants, dependents, background, query=None):
    """Return (added_rows, forced) where forced is True iff query tuple in closure.

    Multivalued dependency X ->> Y over attribute set R means: if two rows
    agree on X, swapping their Y-values gives two rows that must also be in
    the relation. Closure = all tuples reachable by repeated swaps from the
    base table. We iterate swaps to a fixed point, tracking the tuple set.
    """
    attrs = 3
    rows = set(tuple(background))
    changed = True
    while changed:
        changed = False
        for det, dep in zip(determinants, dependents):
            z = [a for a in range(attrs) if a not in det and a not in dep]
            groups = {}
            for row in rows:
                key = tuple(row[i] for i in det)
                groups.setdefault(key, []).append(row)
            for key, group in groups.items():
                if len(group) < 2:
                    continue
                yvals = {tuple(row[i] for i in dep) for row in group}
                zvals = {tuple(row[i] for i in z) for row in group}
                for yv in yvals:
                    for zv in zvals:
                        nr = [None] * attrs
                        for i, v in zip(det, key):
                            nr[i] = v
                        for i, v in zip(dep, yv):
                            nr[i] = v
                        for i, v in zip(z, zv):
                            nr[i] = v
                        nr = tuple(nr)
                        if nr not in rows:
                            rows.add(nr)
                            changed = True
    q = tuple(query)
    forced = q in rows
    added = len(rows) - len(background)
    return added, forced


@dataclass
class MVDClosureConfig(Config):
    nattrs: int = 3
    nbase: int = 3
    nfds: int = 1
    trials: int = 60

    def apply_difficulty(self, level):
        self.nattrs = 3
        self.nbase = stochastic_rounding(2 + level)
        self.nfds = 1 + (level >= 3)
        self.trials = 60 + 40 * level


class MultivaluedDependencyClosure(Task):
    summary = "Close finite relations under multivalued dependencies by swapping attribute blocks between rows agreeing on determinants; handle interacting dependencies and return forced-row membership or added-row count."
    design_choice = "Answer form: single yes/no on whether a queried tuple is forced, versus an integer count of added rows after full closure."
    config_cls = MVDClosureConfig

    def generate_entry(self):
        # attributes R = {0,1,2}
        while True:
            nbase = self.config.nbase
            attrs = [0, 1, 2]
            rows = []
            for _ in range(nbase):
                rows.append(tuple(random.randrange(3) for _ in attrs))
            rows = sorted(set(rows))
            # choose determinants: single or pair among the 3 attrs
            nfds = self.config.nfds
            determinants = []
            if nfds == 1:
                determinants = [random.choice([[0], [1], [2]])]
            else:
                determinants = random.sample([[0], [1], [2], [0, 1], [0, 2], [1, 2]], 2)
            dependents = []
            for det in determinants:
                rest = [a for a in attrs if a not in det]
                dep = random.choice(rest)
                dependents.append([dep])
            background = rows
            # build query
            if random.random() < 0.5:
                q = tuple(random.randrange(3) for _ in attrs)
            else:
                # derive a query from a closure-extended row: pick pair of base rows
                # agreeing on a determinant and construct a swapped row (guaranteed in closure)
                det = determinants[0]
                dep = dependents[0]
                # find two rows agreeing on det (or manufacture one)
                pair = None
                for a in range(len(background)):
                    for b in range(a + 1, len(background)):
                        if all(background[a][i] == background[b][i] for i in det):
                            pair = (background[a], background[b])
                            break
                    if pair:
                        break
                if pair is not None:
                    ra, rb = pair
                    q = list(ra)
                    for i in dep:
                        q[i] = rb[i]
                    q = tuple(q)
                else:
                    q = tuple(random.randrange(3) for _ in attrs)
            added, forced = closure_added_rows(determinants, dependents, background, q)
            if added >= 0:
                break
        # balance label: reuse forced as true-answer, force construction of both
        # We already get both forced True/False across the two branches.
        entry_metadata = {
            "attrs": attrs,
            "rows": [list(r) for r in background],
            "dependencies": [[list(d), list(e)] for d, e in zip(determinants, dependents)],
            "query": list(q),
        }
        return Entry(metadata=entry_metadata, answer="yes" if forced else "no")

    def render_prompt(self, metadata):
        dep_lines = []
        for d, e in metadata["dependencies"]:
            dep_lines.append(f"{d} ->> {e}")
        dep_str = "; ".join(dep_lines)
        return (
            f"Consider a relation over attributes [0, 1, 2] with rows "
            f"{[list(r) for r in metadata['rows']]}. "
            f"The multivalued dependencies are: {dep_str}, "
            f"where X ->> Y means that if two rows agree on all attributes in X, "
            f"then swapping their Y-blocks must also yield rows present in the "
            f"relation, and this property is applied recursively to a fixed point "
            f"to close the relation. "
            f"Is the tuple {metadata['query']} forced to be present in the closed relation? "
            f"Answer exactly 'yes' or 'no'."
        )

    def score_answer(self, answer, entry):
        canon = "yes" if entry.answer == "yes" else "no"
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip().lower()
        if a == canon:
            return 1.0
        if a in ("yes", "no"):
            return 0.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'multivalued_dependency_closure (variant 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_representation_specific_r4/multivalued_dependency_closure',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
