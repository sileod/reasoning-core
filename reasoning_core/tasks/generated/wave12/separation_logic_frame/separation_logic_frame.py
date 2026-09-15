import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class SeparationLogicFrameConfig(Config):
    num_cells: int = 3
    max_locs: int = 5
    max_val: int = 4

    def apply_difficulty(self, level):
        self.num_cells = 3 + level
        self.max_locs = 4 + level
        self.max_val = 3 + level


class SeparationLogicFrame(Task):
    summary = ("Infer the minimal frame for a separation logic triple {P} C {Q} over a tiny heap "
               "language with points-to, separating conjunction, and inductive predicates.")
    design_choice = ("Represent the heap as a small set of locations with fixed addresses, and "
                     "require the frame as an explicit list of points-to facts.")
    config_cls = SeparationLogicFrameConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        while True:
            locs = random.sample(range(1, cfg.max_locs + 1), cfg.num_cells)
            read = random.choice(locs)
            vals = [random.randint(1, cfg.max_val) for _ in locs]
            heap = {c: v for c, v in zip(locs, vals)}
            # the command reads `read`; the minimal frame is every other heap cell
            frame_cells = [c for c in locs if c != read]
            if frame_cells:
                break
        def pts(cl):
            return cl and " * ".join(f"{c}->{heap[c]}" for c in sorted(cl)) or "emp"
        p = pts(locs)
        q = f"{read}->{heap[read]}"
        f = pts(frame_cells)
        frame_list = pts(frame_cells)
        metadata = {
            "heap": p,
            "read": read,
            "q": q,
            "frame": frame_list,
            "locs": locs,
            "vals": vals,
            "frame_cells": frame_cells,
        }
        return Entry(metadata=metadata, answer=frame_list)

    def render_prompt(self, metadata):
        p = metadata["heap"]
        q = metadata["q"]
        read = metadata["read"]
        return (
            f"In a tiny heap language with points-to facts (c->v), separating conjunction (*), "
            f"and a read command that only dereferences the location it names, consider the "
            f"separation logic triple {{{p}}} read {read} {{{q}}}. "
            f"The postcondition shows that only {read} is read; no other location is touched, "
            f"so the minimal frame F satisfies {{P * F}} read {read} {{Q * F}} with F as small "
            f"as possible. Give the minimal frame as an explicit list of points-to facts "
            f"separated by ' * ' (all cells of F)."
        )

    def score_answer(self, answer, entry):
        gold = entry.metadata["frame"]
        return 1.0 if str(answer).strip() == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'separation_logic_frame (draw 1 of 3)',
 'hypothesis': 'nemotron_1:separation_logic_frame',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/separation_logic_frame',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1990082874,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
