import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _name(i, nd):
    return "x%0*d" % (len(str(nd - 1)), i)


@dataclass
class CallByNeedConfig(Config):
    n: int = 4
    p_edge: float = 0.5
    k_roots: int = 1

    def apply_difficulty(self, level):
        self.n = 4 + level * 2
        self.p_edge = min(0.85, 0.35 + level * 0.07)
        self.k_roots = 1 + level // 3


class CallByNeedThunkAccounting(Task):
    summary = (
        "Evaluate nested aliases and function arguments by demand, creating and "
        "memoizing shared thunks so each forced expression runs once; report the "
        "sorted names of never-demanded definitions over varied acyclic dependency "
        "DAGs and demand roots."
    )
    design_choice = (
        "Report only the set of never-demanded definitions as a sorted list of "
        "names, ignoring values and order."
    )
    config_cls = CallByNeedConfig

    def generate_entry(self):
        n = self.config.n
        names = [_name(i, n) for i in range(n)]

        while True:
            deps = {}
            for i in range(n):
                edges = []
                for j in range(i):
                    if random.random() < self.config.p_edge:
                        edges.append(j)
                deps[i] = set(edges)

            k = min(self.config.k_roots, n)
            roots = random.sample(range(n), k)

            demanded = set(roots)
            stack = list(roots)
            while stack:
                cur = stack.pop()
                for j in deps[cur]:
                    if j not in demanded:
                        demanded.add(j)
                        stack.append(j)

            never = [i for i in range(n) if i not in demanded]
            if 0 < len(never) < n:
                break

        gold = sorted(never)
        gold_str = ", ".join(_name(i, n) for i in gold) if gold else "none"

        metadata = {
            "names": names,
            "deps": {_name(i, n): [_name(j, n) for j in sorted(deps[i])] for i in range(n)},
            "roots": [_name(i, n) for i in sorted(roots)],
            "demanded": [_name(i, n) for i in sorted(demanded)],
            "never": [_name(i, n) for i in gold],
        }
        return Entry(metadata=metadata, answer=gold_str)

    def render_prompt(self, metadata):
        def_lines = "\n".join(
            "    %s = %s" % (nm, " + ".join(metadata["deps"][nm]) if metadata["deps"][nm] else "1")
            for nm in metadata["names"]
        )
        roots = ", ".join(metadata["roots"])
        return (
            "Under call-by-need, a definition is evaluated only when its value is "
            "demanded, the first time it is needed; a shared thunk is memoized, so "
            "each expression runs at most once. A program defines these aliases and "
            "expressions:\n\n%s\n\nThe top-level expression whose value must be "
            "produced references (demands) the definitions %s.\n\nForcing that "
            "expression forces exactly those definitions reachable from %s through "
            "the references in their right-hand sides.\n\nList, in ascending "
            "lexicographic order and separated by commas, the names of all "
            "definitions that are NEVER demanded (never evaluated). If none are "
            "never demanded, answer the single word: none\n\nAnswer:"
            % (def_lines, roots, roots)
        )

    def score_answer(self, answer, entry):
        return _score(answer, entry)


def _parse(answer):
    a = (answer or "").strip()
    if not a or a.lower() == "none":
        return frozenset()
    parts = [p.strip() for p in a.split(",") if p.strip()]
    return frozenset(parts)


def _score(answer, entry):
    gold = frozenset(entry.metadata["never"])
    got = _parse(answer)
    return 1.0 if got == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'call_by_need_thunk_accounting (variant 2 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_formal_logic_r4/call_by_need_thunk_accounting',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3577985643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
