import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class AliasMutationTrackingV3Config(Config):
    level: int = 0
    n_records: int = 3
    n_ops: int = 2
    n_bindings: int = 2
    value_range: int = 20

    def apply_difficulty(self, level):
        self.level = level
        self.n_records = 2 + level
        self.n_ops = 2 + level * 2
        self.n_bindings = 2 + level
        self.value_range = 20 + level * 5


def build_prompt(record_values, binds, ops, query_name):
    lines = []
    for i, v in enumerate(record_values):
        lines.append(f"record r{i} holds the integer {v}.")
    for nm, slot in binds:
        lines.append(f"name {nm} is an alias referring to record r{slot}.")
    for op in ops:
        lines.append(op)
    body = " ".join(lines)
    return (
        "Several named references alias a collection of records. Each record holds a single "
        "integer value. An operation can create a new alias for a record, rebind an existing "
        "name to a different record, or mutate an integer value of a record through one of its "
        "aliases. Aliases to the same record observe the same current value: mutating through "
        "one alias changes what every alias to that record sees, and rebinding a name detaches "
        "it from the record it used to point at. "
        + body
        + f" After these operations, name {query_name} refers to a record. What is the final "
          "integer value held by that record? Answer in the form get_value(name) => value, "
          "with the value as the integer."
    )


class AliasMutationTracking(Task):
    summary = "Track aliases among mutable lists or records through assignment, mutation, and rebinding, returning a queried final value or reference relation."
    design_choice = "Answer is a constrained call string like 'get_value(name)' returning the final integer value, where the difficulty lies in tracking mutations through aliased references."
    config_cls = AliasMutationTrackingV3Config

    def generate_entry(self):
        cfg = self.config
        n_records = cfg.n_records
        n_ops = cfg.n_ops
        n_bindings = cfg.n_bindings

        record_values = [random.randint(-cfg.value_range, cfg.value_range) for _ in range(n_records)]

        binding_names = [f"x{j}" for j in range(n_bindings)]
        binding_slots = [random.randrange(n_records) for _ in range(n_bindings)]

        initial_binds = list(zip(binding_names, binding_slots))
        binds = list(initial_binds)
        ops = []
        ctr = 0
        for _ in range(n_ops):
            op = random.choice(["assign", "rebind", "mutate"])
            if op == "assign":
                new_name = f"y{ctr}"
                ctr += 1
                target = random.randrange(n_records)
                ops.append(f"create a new name {new_name} as an alias for record r{target}.")
                binds.append((new_name, target))
            elif op == "rebind":
                idx = random.randrange(len(binds))
                name, _ = binds[idx]
                target = random.randrange(n_records)
                ops.append(f"rebind name {name} to alias record r{target}.")
                binds[idx] = (name, target)
            else:
                idx = random.randrange(len(binds))
                name, slot = binds[idx]
                change = random.randint(-cfg.value_range, cfg.value_range)
                record_values[slot] += change
                ops.append(f"via name {name}, mutate record r{slot} by adding {change}.")

        query_idx = random.randrange(len(binds))
        query_name, target_slot = binds[query_idx]
        answer_value = record_values[target_slot]

        prompt = build_prompt(record_values, initial_binds, ops, query_name)
        answer = f"get_value({query_name}) => {answer_value}"

        return Entry(
            metadata={
                "record_values": list(record_values),
                "binds": [[n, s] for n, s in initial_binds],
                "ops": list(ops),
                "query_name": query_name,
                "answer_value": answer_value,
                "prompt": prompt,
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        return metadata["prompt"]


TASK_META = {'parent_source_id': None,
 'idea': 'alias_mutation_tracking (draw 3 of 3)',
 'hypothesis': 'manual_high_value_80:alias_mutation_tracking',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/alias_mutation_tracking',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3725686066,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
