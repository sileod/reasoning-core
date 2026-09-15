import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'cellular_automaton_step (draw 2 of 3)',
 'hypothesis': 'P011',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_verification_repair_r1/cellular_automaton_step',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 525660630,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _rule_lookup(rule, a, b, c):
    index = (a << 2) | (b << 1) | c
    return (rule >> index) & 1


def _step(row, rule):
    n = len(row)
    out = []
    for i in range(n):
        left = row[(i - 1) % n]
        center = row[i]
        right = row[(i + 1) % n]
        out.append(_rule_lookup(rule, left, center, right))
    return out


@dataclass
class CellularAutomatonStepConfig(Config):
    length: int = 8
    min_steps: int = 1
    max_steps: int = 2

    def apply_difficulty(self, level):
        self.length = 6 + 2 * level
        self.min_steps = 1 + level
        self.max_steps = 2 + level


class CellularAutomatonStep(Task):
    summary = ("Advance a one-dimensional elementary cellular automaton under a stated rule "
               "number and boundary convention for several synchronous steps, returning a "
               "queried row string, cell state, or live-cell count.")
    design_choice = ("Use random initial rows with a fixed length, but derive the rule number "
                     "from a hash of the initial row so each instance has a unique rule and "
                     "boundary condition.")
    config_cls = CellularAutomatonStepConfig
    task_version = 2

    def _derive_rule(self, length, steps):
        base = f"{length}:{steps}"
        rule = random.randrange(2 ** 8)
        mix = 0
        for ch in base + str(rule):
            mix = (mix * 31 + ord(ch)) & 0xFFFFFFFFFFFFFFFF
        mix = ((mix ^ (rule * 2654435761)) & 0xFFFFFFFFFFFFFFFF) % 256
        return round(mix)

    def generate_entry(self):
        length = self.config.length
        steps = random.randint(self.config.min_steps, self.config.max_steps)
        while True:
            rule = self._derive_rule(length, steps)
            boundary = random.choice(["periodic", "zero"])
            row = [random.randint(0, 1) for _ in range(length)]
            if sum(row) == 0 or sum(row) == length:
                continue
            if rule in (0, 255):
                continue
            break

        config = {"rule": rule, "boundary": boundary, "row": "".join(map(str, row)),
                  "steps": steps}

        cur = list(row)
        n = len(cur)
        if boundary == "zero":
            for _ in range(steps):
                nxt = []
                for i in range(n):
                    left = cur[i - 1] if i - 1 >= 0 else 0
                    center = cur[i]
                    right = cur[i + 1] if i + 1 < n else 0
                    nxt.append(_rule_lookup(rule, left, center, right))
                cur = nxt
        else:
            for _ in range(steps):
                nxt = []
                for i in range(n):
                    left = cur[(i - 1) % n]
                    center = cur[i]
                    right = cur[(i + 1) % n]
                    nxt.append(_rule_lookup(rule, left, center, right))
                cur = nxt

        final = cur
        mode = random.choice(["row", "cell", "count"])

        final_str = "".join(map(str, final))

        if mode == "row":
            answer = final_str
        elif mode == "cell":
            idx = random.randint(0, length - 1)
            answer = str(final[idx])
            config["query"] = idx
        else:
            answer = str(sum(final))
            config["query"] = "count"

        config["mode"] = mode

        entry = Entry(metadata=config, answer=answer)
        return entry

    def render_prompt(self, metadata):
        cfg = metadata
        row = cfg["row"]
        rule = cfg["rule"]
        boundary = cfg["boundary"]
        steps = cfg["steps"]
        length = len(row)
        if boundary == "periodic":
            bdesc = "cells beyond the ends wrap around to the opposite end (periodic boundary)"
        else:
            bdesc = "cells beyond the ends are treated as 0 (zero boundary)"
        rule_desc = ", ".join(
            f"{a}{b}{c} -> {_rule_lookup(rule, a, b, c)}"
            for a in range(2) for b in range(2) for c in range(2)
        )
        intro = (
            f"An elementary cellular automaton (ECA) of length {length} is updated synchronously. "
            f"The new value of each cell depends on itself, its left neighbor, and its right "
            f"neighbor according to the local rule. Here the transitions are: {rule_desc}. "
            f"Here {bdesc}. "
        )
        if cfg["mode"] == "row":
            question = (f"The initial row is {row}. Apply the rule for {steps} step(s). "
                        f"What is the full row after {steps} step(s)? Answer as a string of 0s "
                        f"and 1s of length {length}.")
        elif cfg["mode"] == "cell":
            idx = cfg["query"]
            question = (f"The initial row is {row}. Apply the rule for {steps} step(s). "
                        f"What is the state (0 or 1) of the cell at position {idx} "
                        f"(0-indexed from the left) after {steps} step(s)? Answer 0 or 1.")
        else:
            question = (f"The initial row is {row}. Apply the rule for {steps} step(s). "
                        f"How many live cells (1s) are in the row after {steps} step(s)? "
                        f"Answer a non-negative integer.")
        return intro + question


def score_answer_cellular_automaton(answer, entry):
    return 1.0 if answer.strip() == entry.answer else 0.0
