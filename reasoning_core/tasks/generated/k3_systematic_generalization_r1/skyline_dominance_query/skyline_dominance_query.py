import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class SkylineDomConfig(Config):
    count_range: tuple = (4, 12)

    def apply_difficulty(self, level):
        self.count_range = (4 + level, 12 + level)


class SkylineDominanceQuery(Task):
    summary = "Given records with 2 numeric attributes and maximize preferences on both, return sorted labels of records not dominated by any other (strict Pareto skyline), over correlated and anticorrelated distributions."
    design_choice = "Use exactly 2 attributes per record, with preferences set to maximize both, so dominance is strict Pareto; answer is the sorted labels of the nondominated frontier."
    config_cls = SkylineDomConfig

    def generate_entry(self):
        lo, hi = self.config.count_range
        count = random.randint(lo, hi)
        distribute = random.choice(["correlated", "anticorrelated"])
        points = []
        for _ in range(count):
            x = random.uniform(0.0, 100.0)
            if distribute == "correlated":
                y = x + random.uniform(-20.0, 20.0)
            else:
                y = 100.0 - x + random.uniform(-20.0, 20.0)
            points.append((float(x), float(y)))
        frontier = []
        for i in range(count):
            dominated = False
            xi, yi = points[i]
            for j in range(count):
                if i == j:
                    continue
                xj, yj = points[j]
                if xj > xi and yj > yi:
                    dominated = True
                    break
                if xj >= xi and yj > yi:
                    dominated = True
                    break
                if xj > xi and yj >= yi:
                    dominated = True
                    break
            if not dominated:
                frontier.append(i)
        frontier.sort()
        answer = ",".join(str(i) for i in frontier)
        return Entry(metadata={"count": count, "distribute": distribute, "points": points}, answer=answer)

    def render_prompt(self, metadata):
        labels = "\n".join(f"  {i}: ({p[0]:.3f}, {p[1]:.3f})" for i, p in enumerate(metadata["points"]))
        return (
            "Records each have 2 numeric attributes. For every attribute, higher is better. "
            "A record is dominated if some other record is at least as good in every attribute and "
            "strictly better in at least one. The Pareto frontier (skyline) is the set of records "
            "that are not dominated by any other. Return the labels of the frontier records, sorted "
            "ascending and comma-separated (e.g. 0,3).\n"
            f"Records:\n{labels}\n"
            "Answer: the sorted labels of the nondominated frontier."
        )

    def score_answer(self, answer, entry):
        try:
            got = sorted(int(x) for x in answer.split(",") if x.strip() != "")
        except Exception:
            return 0.0
        points = entry["metadata"]["points"] if isinstance(entry, dict) else entry.metadata["points"]
        n = len(points)
        frontier = set()
        for i in range(n):
            dominated = False
            xi, yi = points[i]
            for j in range(n):
                if i == j:
                    continue
                xj, yj = points[j]
                if xj >= xi and yj >= yi and (xj > xi or yj > yi):
                    dominated = True
                    break
            if not dominated:
                frontier.add(i)
        want = sorted(frontier)
        if got != want:
            return 0.0
        return 1.0


TASK_META = {'parent_source_id': None,
 'idea': 'skyline_dominance_query (draw 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_systematic_generalization_r1/skyline_dominance_query',
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
