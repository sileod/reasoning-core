import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


TASK_META = {
    'parent_source_id': None,
    'idea': 'redundant_signal_race_bounds (variant 1 of 3)',
    'hypothesis': 'P003',
    'changes': 'new task in '
               'reasoning_core/tasks/generated/ua_cognitive_psychology_r4/redundant_signal_race_bounds',
    'generation': {'provider_name': 'albert',
                   'model_name': 'deepseek-v4-flash',
                   'harness_name': 'opencode',
                   'harness_version': '1.18.32',
                   'agent_name': 'task-search-worker',
                   'settings': {'variant': None,
                                'requested_seed': 2267388306,
                                'seed_forwarded': True,
                                'temperature': None,
                                'top_p': None,
                                'pure': True,
                                'max_steps': 56,
                                'timeout_seconds': 1800,
                                'sandbox': {'name': 'bubblewrap',
                                            'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class RedundantSignalRaceBoundsV1Config(Config):
    n_channels: int = 3

    def apply_difficulty(self, level):
        self.n_channels = stochastic_rounding(2 + level)


def _survival(miss, span, time):
    if time < 1:
        return 1.0
    if time >= 1 + span:
        return miss
    unfinished = (1 + span - time) / span
    return miss + (1.0 - miss) * unfinished


def feasible_interval(channels):
    n = len(channels)
    surv = [_survival(m, span, t) for (m, span, t) in channels]
    lo = max(0.0, sum(surv) - (n - 1))
    hi = min(surv)
    return lo, hi


def _frac(x):
    s = f"{round(x, 4):.4f}".rstrip("0").rstrip(".")
    return s or "0"


class RedundantSignalRaceBounds(Task):
    summary = ("Bound redundant-target response distributions under separate-channel racing "
               "without assuming independence; vary channel counts, time points, and missing "
               "probabilities; answer feasible intervals or violated bounds.")
    design_choice = ("Generate bounds as closed-form intervals from per-channel survival "
                     "functions sampled at discrete time points, with missing channels treated "
                     "as never finishing, and ask for min/max feasible probability values.")
    config_cls = RedundantSignalRaceBoundsV1Config
    task_version = 2

    def generate_entry(self):
        while True:
            n = self.config.n_channels
            channels = []
            for _ in range(n):
                miss = random.randint(0, 30) / 100.0
                span = random.randint(2, 6)
                t = random.randint(1, 8)
                channels.append((miss, span, t))
            lo, hi = feasible_interval(channels)
            if 0.0 <= lo <= hi <= 1.0 and hi - lo > 1e-9:
                break
        answer = f"[{_frac(lo)}, {_frac(hi)}]"
        return Entry(
            metadata={
                "channels": [(m, sp, t) for (m, sp, t) in channels],
                "lo": float(lo),
                "hi": float(hi),
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        lines = []
        for i, (m, span, t) in enumerate(metadata["channels"]):
            lines.append(
                f"channel {i+1}: if not missing, its completion time is uniform on 1 to "
                f"{1+span} seconds; it is missing with probability {_frac(m)}"
            )
        chans = "; ".join(lines)
        ts = ", ".join(str(t) for (_, _, t) in metadata["channels"])
        return (
            f"Redundant-target racing: k separate channels race to signal an onset, observed "
            f"independently at fixed time points. Each channel either never finishes (is "
            f"missing) or completes after a stated continuous delay. The channels are NOT "
            f"assumed independent of one another. Listed per channel: {chans}. Every channel "
            f"is observed at the time points {ts} respectively, where the time point indexes "
            f"seconds after onset."
            f" Let p be the probability that ALL channels remain unfinished at their listed "
            f"time. Compute the feasible interval [lower, upper] for p consistent with the "
            f"per-channel survival probabilities, without assuming channel independence or "
            f"any particular positive correlation between them. "
            f"Use the worst-case min and max consistent with only these marginals (Fr\u00e9chet "
            f"bounds). Answer as [lower, upper] with values as decimals, e.g. [0.12, 0.85]."
        )

    def score_answer(self, answer, entry):
        parsed = _parse_interval(answer)
        if parsed is None:
            return 0.0
        lo, hi = parsed
        md = entry["metadata"]
        return 1.0 if abs(lo - float(md["lo"])) < 1e-3 and abs(hi - float(md["hi"])) < 1e-3 else 0.0


def _parse_interval(text):
    text = text.strip()
    if not (text.startswith("[") and text.endswith("]")):
        return None
    parts = text[1:-1].split(",")
    if len(parts) != 2:
        return None
    try:
        return float(parts[0]), float(parts[1])
    except ValueError:
        return None
