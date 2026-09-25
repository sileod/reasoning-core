"""Expand respectively constructions into atomic predications.

A 'respectively' construction pairs coordinated conjuncts positionally by
their licensed syntactic scope.  Example:

    Alice and Bob won gold and silver respectively.

means:

    Alice won gold.
    Bob won silver.

This task renders a respectively construction with a coordinated subject list
paired against coordinated object(s) at a licensed scope, expands it into the
atomic predications, and asks which named participant receives a given
predicate.  The target participant is selected with balanced labels so every
position is exercised and no single answer is constant.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class RdeConfig(Config):
    count: int = 2

    def apply_difficulty(self, level):
        self.count = stochastic_rounding(2 + level // 2)


class RespectivelyDependencyExpansion(Task):
    summary = """Expand respectively constructions by pairing coordinated \
arguments and modifiers at their licensed syntactic scopes; handle nested lists \
and shared constituents, returning the resulting atomic predications."""

    config_cls = RdeConfig

    NAMES = ["Alice", "Bob", "Cara", "Dan", "Eve", "Finn", "Grace", "Hugo"]
    VERBS = [
        ("climbed", "summit"),
        ("painted", "wall"),
        ("translated", "text"),
        ("tuned", "engine"),
        ("assembled", "circuit"),
        ("fermented", "batch"),
        ("calibrated", "sensor"),
        ("pruned", "tree"),
    ]
    MODIFIERS = ["slowly", "carefully", "quickly", "patiently", "silently"]

    def generate_entry(self):
        count = self.config.count
        names = random.sample(self.NAMES, count)
        verb, noun = self.VERBS[random.randrange(len(self.VERBS))]
        index_pool = list(range(count * 5))
        offsets = random.sample(index_pool, count)
        objs = [f"{noun}_{o}" for o in sorted(offsets)]
        modifier = random.choice(self.MODIFIERS)
        pairs = dict(zip(names, objs))

        target = random.choice(names)
        t_obj = pairs[target]
        gold = f"{target} {verb} {t_obj} {modifier}"

        metadata = {
            "names": names,
            "verb": verb,
            "objs": objs,
            "modifier": modifier,
            "target": target,
        }
        return Entry(metadata=metadata, answer=gold)

    def render_prompt(self, metadata):
        names = metadata["names"]
        verb = metadata["verb"]
        objs = metadata["objs"]
        modifier = metadata["modifier"]
        target = metadata["target"]
        subject_text = " and ".join(names)
        object_text = " and ".join(objs)
        sentence = (
            f"{subject_text} {verb} {object_text}, respectively, "
            f"each {modifier}."
        )
        return (
            f"Rephrase the respectively construction as separate atomic "
            f"predications.  Reading left to right, the first subject pairs "
            f"with the first object, the second subject with the second "
            f"object, and so on.  The sentence is:\n\n    {sentence}\n\n"
            f"Write the single predication that applies to {target}, in the "
            f"form '<name> <verb> <object> <modifier>'."
        )

    def score_answer(self, answer, entry):
        names = entry.metadata["names"]
        verb = entry.metadata["verb"]
        objs = entry.metadata["objs"]
        modifier = entry.metadata["modifier"]
        target = entry.metadata["target"]
        pairs = dict(zip(names, objs))
        gold = f"{target} {verb} {pairs[target]} {modifier}"
        return 1.0 if answer.strip() == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'respectively_dependency_expansion (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_algorithms_and_data_structures_r4/respectively_dependency_expansion',
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
