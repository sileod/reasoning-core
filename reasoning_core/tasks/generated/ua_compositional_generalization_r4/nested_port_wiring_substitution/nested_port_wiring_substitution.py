"""Nested port-wiring substitution: match a terminal to its mate through a wiring template."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class NestedPortWiringSubstitutionV1Config(Config):
    count: int = 4
    reversed: bool = False

    def apply_difficulty(self, level):
        self.count = 6 + 2 * level
        self.reversed = level >= 2


def _traverse(perm, start, reversed_mode):
    """Follow the permutation from start until returning to start (feedback).
    Returns the mate-path: list of terminal labels, with 'R' inserted after a label
    whenever the next hop goes to a smaller index."""
    path = []
    cur = start
    while True:
        path.append(cur)
        nxt = perm[cur]
        if reversed_mode and nxt < cur:
            path.append("R")
        if nxt == start:
            break
        cur = nxt
    return path


def _make_perm(n, seed):
    rng = random.Random(seed)
    while True:
        perm = list(range(n))
        rng.shuffle(perm)
        fixed = sum(1 for i in range(n) if perm[i] == i)
        if fixed == 0:
            return perm


class NestedPortWiringSubstitution(Task):
    summary = "Expand nested wiring templates by grafting instances into ordered port boundaries, including reversed ports, repeated instances, and feedback; return a terminal's mate-path string or closed-wire count."
    design_choice = "Answer as a canonical mate-path string: list port labels in traversal order from a given terminal to its mate, with 'R' marking reversed port crossings."
    config_cls = NestedPortWiringSubstitutionV1Config

    def generate_entry(self):
        n = self.config.count
        perm = _make_perm(n, random.randrange(2 ** 31))
        start = random.randrange(n)
        path = _traverse(perm, start, self.config.reversed)
        answer = ",".join(str(x) for x in path)
        port_list = sorted((int(i), int(perm[i])) for i in range(n))
        return Entry(metadata={
            "n": n,
            "perm": port_list,
            "start": int(start),
            "reversed": self.config.reversed,
            "path": [int(x) if x != "R" else "R" for x in path],
        }, answer=answer)

    def render_prompt(self, metadata):
        n = metadata["n"]
        perm = metadata["perm"]
        conns = []
        for a, b in perm:
            conns.append(f"terminal {a} feeds terminal {b}")
        lines = [
            f"A nested wiring template has {n} terminals indexed 0..{n-1}, arranged in ordered port boundaries; each terminal feeds exactly one other terminal, so following wires travels through repeated grafted instances.",
            ". ".join(conns) + ".",
        ]
        if metadata["reversed"]:
            lines.append("Where a hop goes leftward to a smaller index, it crosses a reversed port and is marked R.")
        lines.append(f"Starting at terminal {metadata['start']}, follow the feed chain hop by hop until it returns to the start (feedback).")
        lines.append("Give the mate-path: the comma-separated terminal indices visited before closing the loop, with R inserted right after a label whose next hop goes to a smaller index.")
        return " ".join(lines)

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        gold = entry.answer
        return 1.0 if "".join(str(answer).split()) == "".join(str(gold).split()) else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'nested_port_wiring_substitution (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_compositional_generalization_r4/nested_port_wiring_substitution',
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
