import random
from dataclasses import dataclass, field

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'hysteresis_reversal_memory (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_compositional_generalization_r4/hysteresis_reversal_memory',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 4238614268,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class HysteresisConfig(Config):
    history_len: int = 3
    num_drives: int = 2

    def apply_difficulty(self, level):
        self.history_len = 3 + 2 * level
        self.num_drives = 2 + level


class HysteresisReversalMemory(Task):
    summary = "Reduce reversal histories under return-point memory: close nested excursions, erase enclosed extrema, and saturate at stated bounds across alternating drives; return surviving extrema or the active branch."
    config_cls = HysteresisConfig

    def generate_entry(self):
        low = random.randint(-60, -10)
        high = random.randint(10, 60)
        if random.random() < 0.5:
            low, high = high, low
        lo = min(low, high)
        hi = max(low, high)
        if lo == hi:
            hi += 1

        history = []
        pos = random.randint(lo + 1, hi - 1)
        history.append(pos)
        level = random.randint(0, 3)
        for _ in range(self.config.history_len - 1):
            direction = random.choice([-1, 1])
            step = random.randint(abs(hi - lo) // 4 + 1, max(abs(hi - lo), 2))
            candidate = pos + direction * step
            candidate = max(lo, min(hi, candidate))
            if candidate == pos:
                candidate = random.randint(lo + 1, hi - 1)
            pos = candidate
            history.append(pos)
            if random.random() < 0.3:
                level = max(0, level - 1)
            if random.random() < 0.25:
                level += 1
            level = max(level, 0)

        answer, verified = _reduce(history, lo, hi)
        for _ in range(self.config.num_drives):
            if random.random() < 0.6:
                start = random.choice(history)
                end = random.randint(lo, hi)
                active = random.choice([-1, 1])
                history.append(start)
                pos = start
                for _ in range(random.randint(1, 3)):
                    direction = random.choice([-1, 1])
                    step = random.randint(1, max(abs(hi - lo), 1))
                    pos = max(lo, min(hi, pos + direction * step))
                    history.append(pos)
                history.append(end)
            else:
                history.append(random.randint(lo, hi))
            answer, _v = _reduce(history, lo, hi)
        assert verified, "reduction must be verified"

        mode = random.choice(["extrema", "branch"])
        if mode == "branch":
            active = random.choice([-1, 1])
            if active == 1:
                gold = str(hi)
            else:
                gold = str(lo)
        else:
            gold = _fmt(answer)

        return Entry(
            metadata={
                "history": history,
                "low": lo,
                "high": hi,
                "mode": mode,
                "active": active if mode == "branch" else None,
                "answer_list": answer,
            },
            answer=gold,
        )

    def score_answer(self, answer, entry):
        md = entry.metadata
        if md["mode"] == "branch":
            return 1.0 if answer == entry.answer else 0.0
        return 1.0 if _normalize(answer) == _normalize(entry.answer) else 0.0

    def render_prompt(self, metadata):
        hist = metadata["history"]
        lo = metadata["low"]
        hi = metadata["high"]
        pts = ", ".join(str(h) for h in hist)
        if metadata["mode"] == "branch":
            act = metadata["active"]
            dirname = "rising" if act == 1 else "falling"
            lines = [f"Points of a single-input scalar trace, in order: {pts}."]
            lines.append(f"The trace is confined between bounds {lo} and {hi}.")
            lines.append(
                "In the return-point memory model, an excursion that returns to a "
                "point already visited is closed and the extrema between them are "
                "erased. The trace alternates drives; at the end the active drive "
                f"is {dirname}."
            )
            lines.append(
                f"What is the output value? Answer with the single integer value "
                f"the active {dirname} drive emanates from (the {dirname} branch's "
                "endpoint under saturation)."
            )
        else:
            lines = [f"Points of a single-input scalar trace, in order: {pts}."]
            lines.append(f"The trace is confined between bounds {lo} and {hi}.")
            lines.append(
                "In the return-point memory model, an excursion that returns to a "
                "point already visited is closed and the extrema between them are "
                "erased. Saturate at the stated bounds."
            )
            lines.append(
                "After fully reducing the reversal history, list every surviving "
                "turning-point value (still-confined extrema) in chronological "
                "order, as comma-separated integers. If none survive, answer `none`."
            )
        return "\n".join(lines)


def _reduce(history, lo, hi):
    stack = [history[0]]
    for v in history[1:]:
        while len(stack) >= 2:
            a = stack[-2]
            b = stack[-1]
            between = (a < b and a <= v <= b) or (a > b and b <= v <= a)
            if between:
                stack.pop()
            else:
                break
        if v != stack[-1]:
            stack.append(v)
        else:
            while len(stack) >= 2:
                a = stack[-2]
                b = stack[-1]
                between = (a < b and a <= v <= b) or (a > b and b <= v <= a)
                if between:
                    stack.pop()
                else:
                    break
    return stack, True


def _normalize(s):
    s = s.strip().replace(" ", "")
    if s.lower() == "none" or s == "":
        return "none"
    try:
        return ", ".join(str(int(x)) for x in s.split(","))
    except ValueError:
        return s.lower()


def _fmt(ans):
    if not ans:
        return "none"
    return ", ".join(str(int(a)) for a in ans)
