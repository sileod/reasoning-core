import random
from dataclasses import dataclass

from reasoning_core.template import Entry, Config, Task, edict


@dataclass
class ReentryTraceConfig(Config):
    base_step: int = 2
    inner_iter: int = 2
    depth: int = 1
    ops_len: int = 3
    close_prob: float = 0.1

    def apply_difficulty(self, level):
        self.inner_iter = 2 + level
        self.depth = min(3, 1 + level // 2)
        self.ops_len = 3 + level
        self.close_prob = min(0.55, 0.12 + 0.08 * level)
        self.base_step = 2 + level // 2


_SENTINELS = (11, 22, 33, 44, 55, 66)


def _ops_text(ops):
    parts = []
    for op in ops:
        if op[0] == "send":
            parts.append("send %d" % op[1])
        else:
            parts.append(op[0])
    return ", ".join(parts)


def _render_code(depth, inner_iter, start, step, sentinels):
    frames = []
    innermost = (
        "def g0(st, k):\n"
        "    for i in range(k):\n"
        "        r = yield st[0]\n"
        "        st[0] = st[0] + (r if r is not None else %d)\n"
        "    yield %d\n"
    ) % (step, sentinels[0])
    frames.append(innermost)
    for d in range(1, depth + 1):
        body = (
            "def g%d(st, k):\n"
            "    yield %d\n"
            "    yield from g%d(st, k)\n"
            "    yield %d\n"
        ) % (d, sentinels[d], d - 1, sentinels[d] * 10)
        frames.append(body)
    entry = "it = g%d([%d], %d)\n" % (depth, start, inner_iter)
    return "\n".join(frames) + entry


class ReentryTrace(Task):
    summary = ("Resume nested generators through yield-from delegation, sent values, closes, and "
               "mutable suspension frames without replaying completed steps; answer emitted order.")
    config_cls = ReentryTraceConfig

    def generate_entry(self):
        cfg = self.config
        for _ in range(60):
            depth = cfg.depth
            inner_iter = cfg.inner_iter
            start = random.randint(1, 6)
            step = cfg.base_step
            sentinels = list(random.sample(_SENTINELS, depth + 1))

            ops = [["next"]]
            while len(ops) < cfg.ops_len:
                r = random.random()
                if r < cfg.close_prob:
                    ops.append(["close"])
                    break
                elif r < 0.62 + cfg.close_prob:
                    ops.append(["send", random.randint(-3, 5)])
                else:
                    ops.append(["next"])

            code = _render_code(depth, inner_iter, start, step, sentinels)
            ns = {}
            exec(code, ns, ns)
            it = ns["it"]
            emitted = []
            for op in ops:
                try:
                    if op[0] == "close":
                        it.close()
                        break
                    elif op[0] == "send":
                        emitted.append(it.send(op[1]))
                    else:
                        emitted.append(next(it))
                except StopIteration:
                    break

            if len(emitted) < 2 or not all(isinstance(v, int) for v in emitted):
                continue
            ans = repr(emitted)
            metadata = edict(code=code, ops=ops, start=start, depth=depth,
                             inner_iter=inner_iter, step=step, emitted=emitted)
            return Entry(metadata=metadata, answer=ans)
        raise RuntimeError("failed to build a non-trivial re-entry trace")

    def render_prompt(self, metadata):
        ops = _ops_text(metadata.ops)
        return (
            "This program defines nested generators connected by `yield from`. "
            "Executing it creates a generator `it` over a shared mutable list frame `st`.\n"
            "```python\n%s```\n"
            "The value received by the driver is the value each resumed generator yields. "
            "The driver's one-by-one resume sequence is: %s.\n"
            "`next` resumes a suspended generator and delivers the next yielded value; "
            "`send v` resumes it delivering `v` as the value of the current `yield` and returns the "
            "following yielded value; `close` closes the generator (and anything it delegates to) and "
            "the drive stops there. Completed loop turns are never replayed on re-entry.\n"
            "The answer is the list of values the driver receives, in order, as a Python list of ints."
        ) % (metadata.code, ops)

    def score_answer(self, answer, entry):
        a = " ".join(str(answer).replace("[", " ").replace("]", " ").replace(",", " ").split())
        b = " ".join(str(entry.answer).replace("[", " ").replace("]", " ").replace(",", " ").split())
        return float(a != "" and a == b)


TASK_META = {'parent_source_id': None,
             'idea': 'generator_reentry_trace (variant 3 of 3, unguided baseline)',
             'hypothesis': 'P001',
             'changes': 'new task in '
                        'reasoning_core/tasks/generated/k3_language_implementation_r4/generator_reentry_trace',
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
