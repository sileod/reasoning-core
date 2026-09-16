import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

CLASSES = ["state", "activity", "accomplishment", "achievement"]

CLASS_LABEL = {"state": "S", "activity": "A", "accomplishment": "Acc", "achievement": "Ach"}

IN_OK = {"state": False, "activity": False, "accomplishment": True, "achievement": False}
FOR_OK = {"state": True, "activity": True, "accomplishment": False, "achievement": False}
PROG_OK = {"state": False, "activity": True, "accomplishment": True, "achievement": False}
STOP_END = {"state": False, "activity": True, "accomplishment": False, "achievement": False}

VERDICTS = {"state": (0, 1, 0), "activity": (0, 1, 1), "accomplishment": (1, 0, 0), "achievement": (0, 0, 1)}

PREDICATES = {
    "state": ["know the answer", "belong to the club", "own a car", "resemble his father",
              "understand the problem", "believe the rumour", "love jazz music", "weigh a ton",
              "desire the prize", "prefer tea", "want a break", "suspect the truth",
              "need a rest", "abhor violence", "fear the dark", "contain water"],
    "activity": ["run in the park", "push the cart", "swim laps", "shout for joy",
                 "dance on the stage", "drive the truck", "write letters", "jog downhill",
                 "watch the birds", "talk on the phone", "play the piano", "breathe deeply",
                 "pull the rope", "clap loudly", "march in step", "hum a tune"],
    "accomplishment": ["build a house", "read the novel", "paint the wall", "walk to school",
                       "write a report", "bake a cake", "repair the bridge", "draw a portrait",
                       "fold the laundry", "assemble the shelf", "solve the puzzle", "mow the lawn",
                       "transplant the tree", "translate the text", "bake the bread", "dig a well"],
    "achievement": ["reach the summit", "find the key", "die tragically", "spot the intruder",
                    "win the match", "graduate from college", "arrive at the airport", "lose the wallet",
                    "explode the bomb", "recognize the face", "discover the cure", "cross the line",
                    "notice the typo", "catch the thief", "abandon the plan", "break the vase"],
}

ADVERBIALS = ["in five minutes", "for five minutes", "in ten days", "for ten days"]


@dataclass
class AspectualClassConfig(Config):
    def apply_difficulty(self, level):
        pass


class AspectualClassEntailment(Task):
    summary = ("Classify event predicates as state, activity, accomplishment, or achievement "
               "using in/for-adverbial, progressive-entailment, and stop-test diagnostics, then "
               "verdict the licensed inferences; answers are the class plus those verdicts.")
    design_choice = ("Use single-sentence predicates with explicit adverbial/progressive/stop-test "
                     "probes, answer as class plus three yes/no verdicts in fixed order.")
    config_cls = AspectualClassConfig

    def generate_entry(self):
        cls = random.choice(CLASSES)
        predicate = random.choice(PREDICATES[cls])
        v = VERDICTS[cls]
        verdicts = " ".join("yes" if x else "no" for x in v)
        answer = f"{CLASS_LABEL[cls]} {verdicts}"
        return Entry(
            metadata={"cls": cls, "predicate": predicate, "answer": answer},
            answer=answer,
        )

    def render_prompt(self, metadata):
        cls = metadata["cls"]
        predicate = metadata["predicate"]

        return "\n".join([
            "Vendler's four aspectual classes are state (S), activity (A), accomplishment (Acc), "
            "and achievement (Ach). The diagnostics:",
            "1. an 'in X' adverbial marks a bounded, telic result (natural for accomplishments);",
            "2. a 'for X' adverbial marks an unbounded, durative event (natural for states and activities);",
            "3. the progressive is natural only for eventive, non-state predicates;",
            "4. the 'stop V-ing' test: stopping marks the ongoing activity-session as over for activities, "
            "marks incompletion for accomplishments, and is not naturally licensed by states or achievements.",
            "",
            f"Classify the predicate '{predicate}'. Then give the class label and the three verdicts in "
            "this fixed order:",
            "(1) is an 'in X' adverbial acceptable?  (2) is a 'for X' adverbial acceptable?  "
            "(3) does 'stop V-ing' imply the event/session is over?",
            "Answer format: the class label (S, A, Acc, or Ach) followed by three yes/no words, "
            "e.g. for an activity:  A no yes yes",
        ])

    def score_answer(self, answer, entry):
        gold = entry.answer
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'aspectual_class_entailment (draw 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_synthetic_grammars_r1/aspectual_class_entailment',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
