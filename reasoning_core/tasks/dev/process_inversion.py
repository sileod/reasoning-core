"""Reconstruct an internal state of a counting process from its END state and one hidden quantity.

Reworked from the task_search mutation mutated/wave0/m05 process_state (ext #3 on v8_tiny). That
version stated the start count, so the "inversion" was forward simulation and the final count
was decoration. Here one quantity is hidden -- a jar's start count or the amount of one add,
remove or transfer step -- and the final counts are given, so the queried state needs the forward
pass up to the hidden step and the backward pass from the end after it. Every operation is
affine with a nonzero slope in the hidden quantity, so the answer is unique.
"""
import random
from dataclasses import dataclass

from reasoning_core.template import Config, DevTask, Entry, edict, stochastic_rounding as sround

UNITS = "stamps marbles coins books apples cards tokens beads tiles cookies shells stickers pebbles buttons pencils".split()
MUL = {2: "doubled", 3: "tripled", 4: "quadrupled"}
FRAC = {2: "half", 3: "a third", 4: "a quarter"}


@dataclass
class ProcessInversionConfig(Config):
    n_steps: int = 3
    n_jars: int = 1
    max_k: int = 9

    def apply_difficulty(self, level):
        self.n_steps = sround(self.n_steps + 1.2 * level)
        self.n_jars = min(3, 1 + sround(level / 2.5))
        self.max_k = sround(self.max_k + 3 * level)


def _apply(state, step):
    s = list(state)
    op, j, k, *rest = step
    if op == "add":
        s[j] += k
    elif op == "sub":
        s[j] -= k
    elif op == "mul":
        s[j] *= k
    elif op == "div":
        if s[j] % k:
            return None
        s[j] //= k
    else:
        s[j] -= k
        s[rest[0]] += k
    return s if min(s) >= 0 else None


def _text(step, names, unit, hidden):
    op, j, k, *rest = step
    amount = "some" if hidden else str(k)
    if op == "add":
        return f"{amount} {unit} were added to jar {names[j]}"
    if op == "sub":
        return f"{amount} {unit} were removed from jar {names[j]}"
    if op == "move":
        return f"{amount} {unit} were moved from jar {names[j]} to jar {names[rest[0]]}"
    if op == "mul":
        return f"the count in jar {names[j]} was {MUL[k]}"
    return f"the count in jar {names[j]} was cut to {FRAC[k]}"


def _dependence(steps, nj, kind, hid):
    """dep[i][j]: does jar j's count after step i depend on the hidden quantity?

    Moves carry fixed amounts, so dependence never spreads between jars after the hidden step.
    """
    slope = [int(kind == "start" and j == hid) for j in range(nj)]
    dep = [[bool(x) for x in slope]]
    for i, (op, j, k, *rest) in enumerate(steps):
        if kind == "step" and i == hid:
            slope[j] = 1
            if rest:
                slope[rest[0]] = 1
        dep.append([bool(x) for x in slope])
    return dep


class ProcessInversion(DevTask):
    summary = ("Jars of objects go through add, remove, transfer, multiply and divide steps; one start "
               "count or one step amount is hidden and the final counts are given; report the count in "
               "a named jar right after a named step.")
    config_cls = ProcessInversionConfig
    task_version = 1

    def generate_entry(self):
        cfg = self.config
        nj = cfg.n_jars
        start = [random.randint(2, 9) for _ in range(nj)]
        states, steps = [start], []
        while len(steps) < cfg.n_steps:
            op = random.choice(["add", "sub", "mul", "div"] + ["move"] * (nj > 1) * 2)
            j = random.randrange(nj)
            if op in ("mul", "div"):
                step = (op, j, random.choice([2, 2, 3, 4] if op == "div" else [2, 3, 4]))
            elif op == "move":
                step = (op, j, random.randint(1, cfg.max_k), random.choice([i for i in range(nj) if i != j]))
            else:
                step = (op, j, random.randint(2, cfg.max_k))
            nxt = _apply(states[-1], step)
            if nxt is None or max(nxt) > 400:
                continue
            steps.append(step)
            states.append(nxt)
        additive = [i for i, s in enumerate(steps) if s[0] in ("add", "sub", "move")]
        choices = [("start", j) for j in range(nj)] + [("step", i) for i in additive]
        kind, hid = random.choice(choices)
        # Only states that depend on the hidden quantity are asked: those need it recovered from the
        # final counts first, so a forward read from the stated starts never reaches them.
        dep = _dependence(steps, nj, kind, hid)
        options = [(i, j) for i in range(1, len(steps)) for j in range(nj) if dep[i][j]]
        if not options:
            return None
        q_step, q_jar = random.choice(options)
        answer = states[q_step][q_jar]
        names = "ABC"[:nj]
        unit = random.choice(UNITS)
        meta = edict(unit=unit, names=names, start=start, steps=[list(s) for s in steps], final=states[-1],
                     hidden=[kind, hid], q_step=q_step, q_jar=q_jar)
        numbers = {str(x) for x in start + states[-1]} | {str(s[2]) for s in steps}
        if kind == "start":
            numbers.discard(str(start[hid]))
        else:
            numbers.discard(str(steps[hid][2]))
        if str(answer) in numbers:
            return None
        return Entry(metadata=meta, answer=str(answer))

    def render_prompt(self, m):
        hidden_start = m.hidden[1] if m.hidden[0] == "start" else None
        hidden_step = m.hidden[1] if m.hidden[0] == "step" else None
        starts = ", ".join(f"jar {n} starts with {'an unknown number of' if j == hidden_start else m.start[j]} {m.unit}"
                           for j, n in enumerate(m.names))
        steps = "\n".join(f"Step {i + 1}: {_text(s, m.names, m.unit, i == hidden_step)}."
                          for i, s in enumerate(m.steps))
        final = ", ".join(f"jar {n} holds {m.final[j]}" for j, n in enumerate(m.names))
        return (f"{starts[0].upper()}{starts[1:]}. Then:\n{steps}\n"
                f"At the end, {final}.\n"
                f"How many {m.unit} were in jar {m.names[m.q_jar]} right after step {m.q_step}? "
                f"Answer with a number.")

    def score_answer(self, answer, entry):
        try:
            return float(int(str(answer).strip().rstrip(".")) == int(entry.answer))
        except ValueError:
            return 0.0

    def deduplication_key(self, problem):
        m = problem.metadata
        return str((m.start, m.steps, m.hidden, m.q_step, m.q_jar))
