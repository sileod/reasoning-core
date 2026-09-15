import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


def _label(cluster):
    return min(cluster)


def _canon(a, b):
    la = min(a)
    lb = min(b)
    return (a, b) if la < lb else (b, a)


def _merge_frac(method, key, a, b, c, sa, sb):
    dac = key[_canon(a, c)]
    dbc = key[_canon(b, c)]
    if method == "single":
        return min(dac, dbc)
    if method == "complete":
        return max(dac, dbc)
    if method == "average":
        return Fraction(sa * dac + sb * dbc, sa + sb)
    if method == "wpgma":
        return Fraction(dac + dbc, 2)
    raise ValueError(method)


@dataclass
class AggloConfig(Config):
    level: int = 0
    seed: int = 0
    min_n: int = 3
    max_n: int = 5
    max_d: int = 12
    method: str = "single"

    def apply_difficulty(self, level):
        self.level = level
        self.min_n = 3
        self.max_n = min(6, 3 + level)
        self.method = ["single", "complete", "average", "wpgma"][level % 4]


class AgglomerativeLinkageMerge(Task):
    summary = "Agglomerate a small distance matrix by repeatedly merging the closest pair and recomputing linkage (single/complete/average/WPGMA) exactly; return the merge list with levels or the partition at a cut."
    design_choice = "Answer as a list of merge tuples (i,j,height) with cluster labels assigned by smallest original index, and require fractional heights as reduced fractions."
    config_cls = AggloConfig

    def _run(self, method, n, rows):
        key = {}
        for i in range(n):
            for j in range(i + 1, n):
                key[(frozenset((i,)), frozenset((j,)))] = Fraction(rows[i][j])
        active = {frozenset((i,)) for i in range(n)}
        merges = []
        while len(active) > 1:
            alist = sorted(active, key=lambda s: sorted(s))
            best = None
            bestd = None
            for idx in range(len(alist)):
                for jdx in range(idx + 1, len(alist)):
                    a = alist[idx]
                    b = alist[jdx]
                    d = key[_canon(a, b)]
                    if bestd is None or d < bestd:
                        bestd = d
                        best = (a, b)
            a, b = best
            la = _label(a)
            lb = _label(b)
            lab = la if la < lb else lb
            merges.append((lab, la + lb - lab, str(bestd)))
            merged = a | b
            sm = len(merged)
            sa = len(a)
            sb = len(b)
            newkey = {}
            for c in active:
                if c == a or c == b:
                    continue
                newkey[_canon(merged, c)] = _merge_frac(method, key, a, b, c, sa, sb)
            active.discard(a)
            active.discard(b)
            active.add(merged)
            for (k, v) in newkey.items():
                key[k] = v
        return merges

    def generate_entry(self):
        method = self.config.method
        n = random.randint(self.config.min_n, self.config.max_n)
        rows = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                d = random.randint(1, self.config.max_d)
                rows[i][j] = d
                rows[j][i] = d
        merges = self._run(method, n, rows)
        out = [(a, b, h) for (a, b, h) in merges]
        return Entry(metadata={"method": method, "rows": rows, "n": n}, answer=repr(out))

    def render_prompt(self, metadata):
        lines = []
        n = metadata["n"]
        rows = metadata["rows"]
        for i in range(n):
            lines.append(" ".join(str(rows[i][j]) for j in range(n)))
        linkage_desc = {
            "single": "the minimum of the two distances to that cluster",
            "complete": "the maximum of the two distances to that cluster",
            "average": "the size-weighted mean of the two distances to that cluster (UPGMA)",
            "wpgma": "the plain mean of the two distances to that cluster",
        }
        return (
            f"Using {metadata['method']} linkage agglomerative hierarchical clustering, cluster "
            f"these points by their distance matrix: rows are points 0..{n-1}, entry (i,j) is "
            f"d(i,j), d(i,i)=0.\n"
            + "\n".join(lines)
            + "\n\nRepeatedly merge the two current clusters with the smallest linkage distance; "
              "after merging, replace them by one cluster whose index is the smallest original "
              "index among their members, and recompute its distance to every other cluster as "
              + linkage_desc[metadata["method"]]
              + ". Report every merge as a tuple (i,j,height) in merge order, with i<j the two "
              "cluster indices being merged at that step. Give each height as a fully reduced "
              "fraction (e.g. 3/2); integers as themselves (e.g. 4). Output only the list of "
              "tuples, in order."
        )

    def score_answer(self, answer, entry):
        return float(answer == entry.answer)


TASK_META = {'parent_source_id': None,
 'idea': 'agglomerative_linkage_merge (draw 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_dependence_relevance_r1/agglomerative_linkage_merge',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
