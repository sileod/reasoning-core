import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'ellipsis_reconstruction (draw 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_parsing_and_agreement_r1/ellipsis_reconstruction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
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

NAMES = ["John", "Mary", "Bill", "Sue", "Tom", "Alice", "Bob", "Kim"]
OBJECTS = ["the book", "the cake", "the report", "the car", "the letter"]
VERBS = ["likes", "reads", "wrote", "bought", "finished", "eats"]
AUX = ["does", "did", "is", "was", "has", "will"]
INTRANS = ["ran", "slept", "laughed", "left", "smiled"]
THEMES = ["the book", "the cake", "the movie", "the party", "the truth"]
WH = ["who", "what", "where", "why"]


@dataclass
class _Config(Config):
    level: int = 0

    def apply_difficulty(self, level):
        self.level = level


def _two_distinct():
    s1 = random.choice(NAMES)
    s2 = random.choice(NAMES)
    while s2 == s1:
        s2 = random.choice(NAMES)
    return s1, s2


def _build(level):
    s1, s2 = _two_distinct()
    mode = random.choice(["vpe", "gapping", "rnr", "sluicing"])
    if mode == "vpe":
        obj = random.choice(OBJECTS)
        verb = random.choice(VERBS)
        aux = random.choice(AUX)
        strict = random.random() < 0.5
        if strict:
            # Transitive with distinct object to force strict reading
            prompt = f"{s1} {verb} {obj}, and {s2} {aux} too."
            answer = f"{s2} {verb} {obj}"
        else:
            # Intransitive: sloppy = self-directed
            verb_i = random.choice(INTRANS)
            prompt = f"{s1} {verb_i}, and {s2} {aux} too."
            answer = f"{s2} {verb_i}"
            return prompt, answer, "vpe"
        return prompt, answer, "vpe_sloppy" if not strict else "vpe_strict"
    elif mode == "gapping":
        verb = random.choice(VERBS)
        obj = random.choice(OBJECTS)
        obj2 = random.choice(OBJECTS)
        if random.random() < 0.5:
            # verb elided from second conjunct; reconstructed as the antecedent verb
            prompt = f"{s1} {verb} {obj}, and {s2} {obj2}."
            answer = f"{s1} {verb} {obj}, and {s2} {verb} {obj2}"
        else:
            # object elided from second conjunct (subcategorized object gap)
            prompt = f"{s1} {verb} {obj}, and {s2} {verb}."
            answer = f"{s1} {verb} {obj}, and {s2} {verb} {obj}"
        return prompt, answer, "gapping"
    elif mode == "rnr":
        obj = random.choice(OBJECTS)
        v1 = random.choice(VERBS)
        v2 = random.choice(VERBS)
        while v2 == v1:
            v2 = random.choice(VERBS)
        prompt = f"{s1} {v1} and {s2} {v2} {obj}."
        answer = f"{s1} {v1} {obj}, and {s2} {v2} {obj}"
        return prompt, answer, "rnr"
    else:
        theme = random.choice(THEMES)
        verb = random.choice(VERBS)
        wh = random.choice(WH)
        if wh == "who":
            prompt = f"{s1} claims {s2} {verb} {theme}, but {s1} refuses to say who."
            answer = f"{s1} refuses to say who {verb} {theme}"
        elif wh == "what":
            prompt = f"{s1} claims {s2} {verb} something, but {s1} refuses to say what."
            answer = f"{s1} refuses to say what {s2} {verb}"
        elif wh == "where":
            prompt = f"{s1} knows {s2} went somewhere, but {s1} refuses to say where."
            answer = f"{s1} refuses to say where {s2} went"
        else:
            prompt = f"{s1} knows {s2} bought it somewhere, but {s1} refuses to say why."
            answer = f"{s1} refuses to say why {s2} bought it"
        return prompt, answer, "sluicing"


class EllipsisReconstruction(Task):
    summary = ("Expand elided material under a named ellipsis--VP-ellipsis with strict or "
               "sloppy pronoun rebinding, gapping, right-node-raising, sluicing--copying "
               "antecedent structure; answer the reconstructed clause or shared remnant.")
    design_choice = ("Answer is a canonical ellipsis-expanded clause string with pronouns "
                     "resolved to explicit antecedents (e.g., 'John likes Mary; Bill does "
                     "too' -> 'Bill likes Mary').")
    config_cls = _Config

    def generate_entry(self):
        prompt, answer, mode = _build(self.config.level)
        return Entry(metadata={"prompt": prompt, "mode": mode}, answer=answer)

    def render_prompt(self, metadata):
        return (f"Reconstruct the elided (omitted) material in the sentence below by copying "
                f"the antecedent clause and resolving every pronoun to its explicit "
                f"antecedent name. Give only the reconstructed canonical clause -- the "
                f"full sentence with the omitted part filled in and pronouns spelled out as "
                f"names. Do not restate the original; output only the expansion.\n\n"
                f"Sentence: {metadata['prompt']}\n"
                f"Reconstructed clause:")

    def score_answer(self, answer, entry):
        gold = entry.answer
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == gold else 0.0
