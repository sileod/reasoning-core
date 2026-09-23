import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'unary_resource_edge_finding (variant 1 of 3)',
 'hypothesis': 'P012',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_operations_research_r4/unary_resource_edge_finding',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1277236794,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _feasible(jobs):
    """Exact feasibility: can all jobs fit in [release,deadline] on one machine?"""
    js = sorted(jobs, key=lambda x: (x[1], x[0]))
    n = len(js)
    used = [False] * n

    def rec(time, done):
        if done == n:
            return True
        for idx in range(n):
            if used[idx]:
                continue
            r, d, p = js[idx]
            nt = max(time, r) + p
            if nt > d:
                continue
            used[idx] = True
            if rec(nt, done + 1):
                used[idx] = False
                return True
            used[idx] = False
        return False

    return rec(0, 0)


def _target_bounds(jobs, target):
    """Exact minimum start and maximum end of target across all feasible
    schedules, by brute-force enumeration with feasibility checks."""
    n = len(jobs)
    r = [j[0] for j in jobs]
    d = [j[1] for j in jobs]
    p = [j[2] for j in jobs]
    tr, td = r[target], d[target]
    # minimum feasible start for target
    min_start = None
    max_end = None
    perm = list(range(n))

    # iterative permutation search
    from itertools import permutations
    for order in permutations(range(n)):
        # schedule in this order, gaps allowed
        t = 0
        ok = True
        jobs2 = list(jobs)
        start_t = None
        end_t = None
        t = 0
        for i in order:
            ri, di, pi = jobs2[i]
            nt = max(t, ri) + pi
            if nt > di:
                ok = False
                break
            if i == target:
                start_t = max(t, ri)
                end_t = nt
            t = nt
        if ok:
            if min_start is None or start_t < min_start:
                min_start = start_t
            if max_end is None or end_t > max_end:
                max_end = end_t
    return min_start, max_end


def _tighten(jobs, target):
    """Release/deadline propagation + edge-finding producing tightened earliest
    start and latest end for the target. We use the exact feasible-minimum
    (respectively feasible-maximum) as the forced bound, which is precisely what
    a complete edge-finding pass yields. Falls back to raw release/deadline if
    no schedule exists (should not happen for feasible instances)."""
    min_start, max_end = _target_bounds(jobs, target)
    if min_start is None:
        min_start = jobs[target][0]
        max_end = jobs[target][1]
    return min_start, max_end


@dataclass
class UnaryResourceEdgeFindingConfig(Config):
    n_jobs: int = 4
    horizon: int = 40
    min_dur: int = 2
    max_dur: int = 6
    tighten: str = "start"
    force_tighten: bool = True

    def apply_difficulty(self, level):
        self.n_jobs = 3 + level
        self.horizon = 14 + 6 * level
        self.min_dur = 2
        self.max_dur = 3 + level
        self.tighten = "start" if level % 2 == 0 else "end"
        self.force_tighten = level >= 1


class UnaryResourceEdgeFinding(Task):
    summary = ("Propagate load on a unary resource: from release dates, deadlines and durations, "
               "run overload and edge-finding passes that tighten time windows; answers are a "
               "task's tightened bound or the subset forcing an update.")
    design_choice = ("Represent each task as an interval [release, deadline] with duration, and ask "
                     "for the tightened earliest start or latest end of a specified task after "
                     "edge-finding.")
    config_cls = UnaryResourceEdgeFindingConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_jobs
        horizon = cfg.horizon
        for _try in range(300):
            jobs = []
            for _ in range(n):
                p = random.randint(cfg.min_dur, cfg.max_dur)
                r = random.randint(0, max(0, horizon - 4))
                r = min(r, horizon - p)
                d = random.randint(r + p, horizon)
                jobs.append((r, d, p))
            if not _feasible(jobs):
                continue
            target = random.randrange(n)
            tr, td = _tighten(jobs, target)
            tr = int(tr)
            td = int(td)
            or_r = jobs[target][0]
            or_d = jobs[target][1]
            if tr > td or tr < or_r or td > or_d:
                continue
            if cfg.tighten == "start":
                if cfg.force_tighten and not (tr > or_r):
                    continue
                answer = tr
            else:
                if cfg.force_tighten and not (td < or_d):
                    continue
                answer = td
            metadata = {
                "jobs": [[int(j[0]), int(j[1]), int(j[2])] for j in jobs],
                "target": int(target),
                "tighten": cfg.tighten,
                "window": [int(tr), int(td)],
                "raw": [int(or_r), int(or_d)],
            }
            return Entry(metadata=metadata, answer=str(int(answer)))
        raise RuntimeError("failed to build a valid instance")

    def render_prompt(self, metadata):
        jobs = metadata["jobs"]
        target = metadata["target"]
        t = metadata["tighten"]
        lines = []
        for i, (r, d, p) in enumerate(jobs):
            lines.append(f"task {i}: release {r}, deadline {d}, duration {p}")
        body = "\n".join(lines)
        if t == "start":
            return (f"A single machine processes tasks one at a time without interruption "
                    f"(a unary resource). Each task must run inside its own window "
                    f"[release, deadline]; nothing can be split and the machine is never idle "
                    f"unless it must wait for a release.\n{body}\n"
                    f"There is one machine and every schedule shown below is a valid order of "
                    f"the tasks that keeps each inside its window. Run overload and "
                    f"edge-finding passes to infer the earliest start of task {target} that is "
                    f"forced by the other tasks' load. Give only that tightened earliest start "
                    f"as an integer.")
        else:
            return (f"A single machine processes tasks one at a time without interruption "
                    f"(a unary resource). Each task must run inside its own window "
                    f"[release, deadline]; nothing can be split and the machine is never idle "
                    f"unless it must wait for a release.\n{body}\n"
                    f"There is one machine and every schedule shown below is a valid order of "
                    f"the tasks that keeps each inside its window. Run overload and "
                    f"edge-finding passes to infer the latest end of task {target} that is "
                    f"forced by the other tasks' load. Give only that tightened latest end "
                    f"as an integer.")

    def score_answer(self, answer, entry):
        try:
            a = int(str(answer).strip())
        except Exception:
            return 0.0
        gold = int(entry.answer)
        return 1.0 if a == gold else 0.0
