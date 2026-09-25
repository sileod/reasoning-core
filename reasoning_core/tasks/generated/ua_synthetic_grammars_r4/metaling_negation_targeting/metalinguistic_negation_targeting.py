import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'metalinguistic_negation_targeting (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_synthetic_grammars_r4/metalinguistic_negation_targeting',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1259343118,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

LAYERS = ["truth", "presupposition", "wording", "register"]

TRUTH_CLAUSES = [
    "the sky is blue", "the cat is on the mat", "two plus two is four",
    "water boils at one hundred degrees", "the earth orbits the sun",
    "the sun sets in the west", "iguanas lay eggs", "mercury is a metal",
    "bats are mammals", "the amazon is a river", "honey never spoils",
    "octopuses have three hearts", "the pyramids are in egypt",
    "gold conducts electricity", "zebras have stripes", "fire needs oxygen",
]

SUBJ = ["Alex", "Maria", "Jon", "Sam", "Priya", "Noor", "Ivan", "Lena", "Omar", "Sara"]
VERB_ING = ["smoking", "running", "attending", "drinking", "singing", "cooking",
            "drawing", "skipping", "gardening", "cycling", "hiking", "boxing"]
VERBS = {"smoking": "smoke", "running": "run", "attending": "attend",
         "drinking": "drink", "singing": "sing", "cooking": "cook",
         "drawing": "draw", "skipping": "skip", "gardening": "garden",
         "cycling": "cycle", "hiking": "hike", "boxing": "box"}
THAT_CLAUSES = ["it was raining", "the meeting was on Tuesday", "the store is closed",
                "the baby was asleep", "the test was easy", "the flight was delayed",
                "the market crashed", "the cake had no sugar", "the door was locked",
                "the film had a sequel", "the train left at noon", "the repair was cheap"]

WORDINGS = ["wealthy", "tiny", "quickly", "exhausted", "intelligent", "sturdy",
            "adorable", "vast", "candid", "brisk", "fragile", "punctual"]
REGISTERS = ["yell", "shout", "demand", "grumble", "snap", "blurt", "hiss", "mumble"]


def _build_clause():
    """Return (kind, clause) where kind is one of the four semantic layers."""
    kind = random.choice(LAYERS)
    if kind == "truth":
        return kind, random.choice(TRUTH_CLAUSES)
    if kind == "presupposition":
        subj = random.choice(SUBJ)
        vi = random.choice(VERB_ING)
        tc = random.choice(THAT_CLAUSES)
        return kind, "{} stopped {} after noting that {}".format(subj, vi, tc)
    if kind == "wording":
        return kind, "the dress is " + random.choice(WORDINGS)
    return kind, "he " + random.choice(REGISTERS) + " his answer"


@dataclass
class MNCConfig(Config):
    """Metalinguistic Negation Config."""
    depth: int = 1

    def apply_difficulty(self, level):
        self.depth = 1 + level


class MetalingNegationTargetingV3(Task):
    task_name = "metaling_negation_targeting"
    summary = ("Locate what a negation rejects using explicit contrasts over truth, "
               "presupposition, wording, and register; compose quotation and nested "
               "denials, returning the semantic layer targeted by each denial.")
    config_cls = MNCConfig

    def generate_entry(self):
        kind, clause = _build_clause()
        depth = self.config.depth
        if depth == 1:
            text = "I did not say {}.".format(clause)
        else:
            inner = clause
            for _ in range(depth):
                inner = "he did not say \"{}\"".format(inner)
            text = "Frank said: {}.".format(inner)
        answer = kind
        return Entry(metadata={"kind": kind, "clause": clause, "depth": depth,
                               "text": text, "answer": answer},
                     answer=answer)

    def render_prompt(self, metadata):
        return (metadata["text"] + " What semantic layer does the denial target -- "
                "truth, presupposition, wording, or register?")

    def score_answer(self, answer, entry):
        return 1.0 if str(answer).strip().lower() == str(entry.metadata["answer"]).strip().lower() else 0.0
