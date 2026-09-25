import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'antichain_progress_completion (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_language_implementation_r4/antichain_progress_completion',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _antichain_incomparable(a, b):
    ge = all(x >= y for x, y in zip(a, b))
    le = all(x <= y for x, y in zip(a, b))
    return not ge and not le


def _precedes(f, t):
    if f == t:
        return False
    return all(x <= y for x, y in zip(f, t))


def _parse_tuples(answer, k):
    ans = str(answer).strip()
    if not ans or ans.lower() == "none":
        return set()
    out = set()
    for group in re.findall(r"\(([^()]*)\)", ans):
        parts = [x for x in re.split(r"[\s,]+", group) if x != ""]
        if len(parts) == k:
            try:
                out.add(tuple(int(x) for x in parts))
            except ValueError:
                pass
    return out


@dataclass
class AntichainProgressConfig(Config):
    dims: int = 2
    frontier_size: int = 2
    n_queries: int = 3
    span: int = 2

    def apply_difficulty(self, level):
        self.dims = 2 + (1 if level >= 3 else 0)
        self.frontier_size = 2 + level
        self.n_queries = 3 + level
        self.span = 2 + level


class AntichainProgressCompletion(Task):
    summary = ("Track progress frontiers in partially ordered timestamp spaces through advances, "
               "forks, and joins; determine which queried times are complete because no frontier "
               "element can still precede them.")
    config_cls = AntichainProgressConfig
    design_choice = ("Instances are generated from a fixed set of timestamp coordinates with "
                     "precedence edges; solvers must return a canonical list of complete queried "
                     "times in sorted order.")

    def generate_entry(self):
        k = self.config.dims
        span = self.config.span

        total = span + self.config.frontier_size
        boundary_max = total + k - 1
        frontier = []
        seen = set()
        for _ in range(self.config.frontier_size):
            for _try in range(1000):
                divs = sorted(random.sample(range(1, boundary_max), k - 1)) if k > 1 else []
                bounds = [0] + divs + [boundary_max]
                parts = [bounds[i + 1] - bounds[i] - 1 for i in range(k)]
                p = tuple(parts)
                if p not in seen:
                    seen.add(p)
                    frontier.append(p)
                    break
        assert len(frontier) == self.config.frontier_size, "could not build frontier antichain"
        assert len(set(frontier)) == self.config.frontier_size

        base = random.choice(frontier)
        up_lane = random.randrange(k)
        incomplete = list(base)
        incomplete[up_lane] += 1 + random.randint(0, span)
        incomplete = tuple(incomplete)

        origin = (0,) * k
        queries = {origin, incomplete}
        for _ in range(self.config.n_queries):
            attempts = 0
            q = tuple(random.randint(0, span + 1) for _ in range(k))
            while q in queries and attempts < 60:
                q = tuple(random.randint(0, span + 1) for _ in range(k))
                attempts += 1
            queries.add(q)
        queries = sorted(queries)

        complete = sorted(
            q for q in queries if not any(_precedes(f, q) for f in frontier)
        )
        assert origin in complete, "origin must always be complete"
        assert incomplete not in complete, "pushed query must be incomplete"
        assert 0 < len(complete) < len(queries), "need both a complete and an incomplete query"

        answer = "none" if not complete else ", ".join(str(t) for t in complete)
        metadata = {
            "dims": k,
            "frontier": sorted(frontier),
            "queries": queries,
            "complete": complete,
            "target": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        k = metadata["dims"]
        frontier_lines = ", ".join(str(t) for t in metadata["frontier"])
        query_lines = ", ".join(str(t) for t in metadata["queries"])
        return (
            f"Progress across a system is tracked over {k} independent lanes, and a time is a "
            f"{k}-tuple of non-negative integers, one coordinate per lane. A new time can follow "
            f"an earlier one only when it is at least as large in every lane, so later work makes "
            f"progress by advancing individual lanes (forks and joins of parallel work). "
            f"The current frontier is the set of furthest-progress times observed: "
            f"{frontier_lines}. A frontier element f still precedes a time T when f[i] <= T[i] "
            f"for every lane i and f is not equal to T; such an f means work has not yet finished "
            f"passing T. A queried time T is therefore COMPLETE exactly when no frontier element "
            f"still precedes it.\n"
            f"The queried times are: {query_lines}.\n"
            f"List the queried times that are COMPLETE, in lexicographic order (compare lane by "
            f"lane, first lane smallest first), as tuples separated by comma-space, for example "
            f"'{(0, 1)}, {(2, 0)}'. If no queried time is complete, write the single word 'none'."
        )

    def score_answer(self, answer, entry):
        gold = {tuple(x) for x in entry.metadata["complete"]}
        parsed = _parse_tuples(answer, entry.metadata["dims"])
        if not gold:
            return 1.0 if not parsed else 0.0
        return 1.0 if parsed == gold else 0.0
