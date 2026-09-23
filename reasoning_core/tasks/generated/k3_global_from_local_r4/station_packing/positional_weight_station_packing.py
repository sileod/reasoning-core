import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround


@dataclass
class StationPackingConfig(Config):
    seed: int = 12345
    n_tasks: int = 6
    max_dur: int = 8
    ct_hi: int = 12
    density: float = 0.3

    def apply_difficulty(self, level):
        self.n_tasks = sround(4 + 1.5 * level)
        self.max_dur = sround(6 + 2 * level)
        self.ct_hi = sround(10 + 4 * level)
        self.density = min(0.85, 0.30 + 0.09 * level)


def _all_successors(pred_of, n):
    succ = {i: [] for i in range(1, n + 1)}
    for u in range(1, n + 1):
        for p in pred_of[u]:
            succ[p].append(u)
    ts = {}
    for i in range(1, n + 1):
        seen = set()
        stack = list(succ[i])
        while stack:
            v = stack.pop()
            if v in seen:
                continue
            seen.add(v)
            stack.extend(succ[v])
        ts[i] = seen
    return ts


def _solve(n, durs, pred_of, ct):
    ts = _all_successors(pred_of, n)
    pw = {}
    for i in range(1, n + 1):
        pw[i] = durs[i - 1] + sum(durs[v - 1] for v in ts[i])
    order = sorted(range(1, n + 1), key=lambda i: (-pw[i], chr(64 + i)))

    stations, used, assigned = [], [], {}
    for i in order:
        placed = None
        for s in range(len(stations)):
            preds_ok = i in assigned or all(p in assigned and assigned[p] <= s for p in pred_of[i])
            if used[s] + durs[i - 1] <= ct and preds_ok:
                placed = s
                break
        if placed is None:
            stations.append([])
            used.append(0)
            placed = len(stations) - 1
        stations[placed].append(i)
        used[placed] += durs[i - 1]
        assigned[i] = placed

    total = sum(durs)
    num_st = len(stations)
    den = num_st * ct
    ball = Fraction(den - total, den) if den > 0 else Fraction(0, 1)
    idles = [ct - used[s] for s in range(num_st)]
    return stations, idles, ball, pw, order


def _format_answer(stations, idles, ball):
    parts = []
    for s in range(len(stations)):
        labels = ",".join(chr(64 + i) for i in sorted(stations[s]))
        parts.append(f"S{s + 1}={labels} idle={idles[s]}")
    parts.append(f"balance_delay={ball.numerator}/{ball.denominator}")
    return " | ".join(parts)


def _prepr(s):
    return " ".join(
        str(s).upper().replace(",", " , ").replace("=", " = ")
        .replace("|", " | ").replace("/", " / ").split()
    )


class StationPacking(Task):
    summary = ("Sum each task's own time plus all successors', sort by positional weight, pack "
               "tasks into stations greedily while precedence and cycle time allow; answers are "
               "station rosters, idle totals, and the resulting balance delay.")
    design_choice = ("Instance parameters: random task counts, precedence densities, and cycle "
                     "times; answer format is a sorted list of station rosters with idle time per "
                     "station and balance delay as a fraction.")
    config_cls = StationPackingConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_tasks
        for _ in range(1000):
            durs = [random.randint(1, cfg.max_dur) for _ in range(n)]
            pred_of = {i: [] for i in range(1, n + 1)}
            for i in range(1, n + 1):
                for j in range(1, i):
                    if random.random() < cfg.density:
                        pred_of[i].append(j)
            ct = random.randint(max(durs), max(durs) + cfg.ct_hi)
            stations, idles, ball, pw, order = _solve(n, durs, pred_of, ct)
            den = len(stations) * ct
            if len(stations) * ct < sum(durs):
                raise RuntimeError("packing exceeded cycle time budget")
            assert 0 <= ball <= 1, "balance delay must be a fraction in [0,1]"
            assert all(idle >= 0 for idle in idles), "idle time must be non-negative"
            break
        else:
            raise RuntimeError("failed to build a feasible station packing after 1000 attempts")

        answer = _format_answer(stations, idles, ball)
        labels = [chr(64 + i) for i in range(1, n + 1)]
        payload = {
            "tasks": " ".join(labels),
            "durations": {l: int(durs[i - 1]) for i, l in enumerate(labels, start=1)},
            "precedence": {
                labels[i - 1]: [labels[p - 1] for p in sorted(pred_of[i])]
                for i in range(1, n + 1)
            },
            "cycle_time": int(ct),
        }
        metadata = edict(
            n=n,
            ct=int(ct),
            durs={chr(64 + i): int(v) for i, v in enumerate(durs, start=1)},
            pred_of={chr(64 + i): [chr(64 + p) for p in sorted(pred_of[i])] for i in range(1, n + 1)},
            pw={chr(64 + i): int(pw[i]) for i in range(1, n + 1)},
            order=[chr(64 + i) for i in order],
            stations=[[chr(64 + i) for i in st] for st in stations],
            idles=[int(x) for x in idles],
            ball=str(ball),
            payload=payload,
        )
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, m):
        prec = "\n".join(
            f"  {a} -> {(' '.join(b) if b else '(none)')}"
            for a, b in m.payload["precedence"].items()
        )
        durs = "  ".join(f"{a}: {d}" for a, d in m.payload["durations"].items())
        return (
            "An assembly line has precedence-constrained tasks, each with a fixed duration, to be "
            "placed into one or more stations of equal cycle time. Ranked positional weight "
            "(RPW) packs tasks greedily: the positional weight of a task is its own duration plus "
            "the durations of all of its (direct and indirect) successors; sort tasks by descending "
            "positional weight (ties by label, alphabetically), then assign each task, in that "
            "order, to the lowest-numbered station whose remaining capacity still fits the task, "
            "all of whose predecessors are already placed (in this or an earlier station). A "
            "station's idle time is cycle time minus the sum of the durations assigned to it, and "
            "the balance delay is (number_of_stations * cycle_time - total_work) / "
            "(number_of_stations * cycle_time), reduced to lowest terms.\n\n"
            f"Tasks: {m.payload['tasks']}\n"
            f"Durations:\n  {durs}\n"
            f"Precedence (a -> b means a must finish before b can begin):\n{prec}\n"
            f"Cycle time: {m.payload['cycle_time']}\n\n"
            "Give the station packing as 'S1=A,B idle=3 | S2=C idle=0 | balance_delay=1/4': one "
            "station roster per station in order (its sorted labels), the station's idle time, "
            "then the balance delay as a reduced fraction."
        )

    def score_answer(self, answer, entry):
        return float(_prepr(answer) == _prepr(entry.answer))


TASK_META = {'parent_source_id': None,
 'idea': 'positional_weight_station_packing (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_global_from_local_r4/positional_weight_station_packing',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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
