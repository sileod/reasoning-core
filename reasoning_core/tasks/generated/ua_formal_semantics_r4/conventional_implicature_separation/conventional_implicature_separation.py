import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

NAMES = ("Mary", "John", "Suki", "Diego", "Lena", "Omar", "Priya", "Andre", "Tara", "Kofi")
MAIN_PREDS = (
    "should resign",
    "finished the report",
    "won the prize",
    "missed the train",
    "adopted the dog",
    "sold the house",
    "passed the exam",
    "attended the meeting",
    "paid the rent",
    "returned the call",
)
APPOSITIVES = (
    "is a brilliant surgeon",
    "is an only child",
    "speaks four languages",
    "grew up in Lima",
    "has never owned a car",
    "wrote the opening chapter",
)
PARENTHETICALS = (
    "is famously punctual",
    "is quietly generous",
    "has an unusual memory",
    "rarely speaks in meetings",
    "is prone to exaggeration",
    "keeps meticulous notes",
)
ADJECTIVES = ("damn", "wretched", "no-good", "dreadful", "two-faced")
NOUNS = ("scoundrel", "tyrant", "menace", "charlatan", "schemer")
FACTIVE_VERBS = ("know", "realize", "regret")
NONFACTIVE_VERBS = ("believe", "think", "suppose", "expect")
SUPPLEMENT_DEVICES = ("appositive", "expressive", "parenthetical")
CONTEXT_KEYS = ("negation", "conditional", "attitude")


def _make_device(dev, name):
    if dev == "appositive":
        app = random.choice(APPOSITIVES)
        return {"device": "appositive", "content": f"{name} {app}", "frag": f", who {app},"}
    if dev == "parenthetical":
        par = random.choice(PARENTHETICALS)
        return {"device": "parenthetical", "content": f"{name} {par}", "frag": f" \u2014 who {par} \u2014"}
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    return {
        "device": "expressive",
        "content": f"{name} is a {adj} {noun}",
        "frag": f", that {adj} {noun},",
    }


@dataclass
class ConventionalImplicatureSeparationV2Config(Config):
    num_supplements: int = 1

    def apply_difficulty(self, level):
        self.num_supplements = min(3, 1 + level // 2)


TASK_META = {'parent_source_id': None,
 'idea': 'conventional_implicature_separation (variant 2 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_semantics_r4/conventional_implicature_separation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1211525277,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


class ConventionalImplicatureSeparation(Task):
    summary = (
        "Compose asserted and supplementary content for appositives, expressives, "
        "and parentheticals under negation, conditionals, and attitude embedding; "
        "return each content contribution and its attributed source."
    )
    design_choice = (
        "Use a fixed 3x3 grid of answers: for each of negation, conditional, and "
        "attitude, list the content pieces as a semicolon-separated string, each "
        "prefixed by A (asserted) or P (projective)."
    )
    config_cls = ConventionalImplicatureSeparationV2Config
    task_version = 2

    def generate_entry(self):
        name = random.choice(NAMES)
        mainpred = random.choice(MAIN_PREDS)
        main_content = f"{name} {mainpred}"
        k = self.config.num_supplements
        devices = random.sample(SUPPLEMENT_DEVICES, k)

        supplements = []
        for _ in range(200):
            supplements = [_make_device(d, name) for d in devices]
            if len({s["content"] for s in supplements}) == k:
                break
        if len({s["content"] for s in supplements}) != k:
            raise RuntimeError("could not produce distinct supplement contents")

        factive = random.random() < 0.5
        attitude_verb = random.choice(FACTIVE_VERBS) if factive else random.choice(NONFACTIVE_VERBS)

        main_label = {"negation": "A", "conditional": "A", "attitude": "P" if factive else "A"}
        rows = []
        for ctx in CONTEXT_KEYS:
            pieces = [f"{main_label[ctx]}: main: {main_content}"]
            for s in supplements:
                pieces.append(f"P: {s['device']}: {s['content']}")
            rows.append(f"{ctx}: " + "; ".join(pieces))
        answer = "\n".join(rows)

        sentence = name + "".join(s["frag"] for s in supplements) + f" {mainpred}."
        metadata = {
            "name": name,
            "main_pred": mainpred,
            "main_content": main_content,
            "supplements": [{"device": s["device"], "content": s["content"]} for s in supplements],
            "attitude_verb": attitude_verb,
            "factive": factive,
            "sentence": sentence,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return _render(metadata)

    def score_answer(self, answer, entry=None):
        if not isinstance(answer, str):
            return 0.0
        if entry is None:
            return 0.0
        gold = entry["answer"]
        return 1.0 if " ".join(answer.split()) == " ".join(gold.split()) else 0.0


def _render(md):
    sups = md["supplements"]
    pieces = " ".join(
        f"({i + 1}) {s['device']}: {s['content']}"
        for i, s in enumerate(sups)
    )
    verb = md["attitude_verb"]
    factive = md["factive"]
    attitude_note = (
        f"{verb} is factive, so its complement projects"
        if factive
        else f"{verb} is non-factive, so its complement stays asserted"
    )
    return (
        "In projective-content semantics, the main clause is at-issue (its content is "
        "asserted), while content supplied by an appositive, an expressive, or a "
        "parenthetical is a conventional implicature that projects: it survives when "
        "the sentence is negated, put in a conditional, or embedded under an attitude "
        "verb. Belief and desire verbs leave their complement asserted; factive verbs "
        "(know, realize, regret) project their complement.\n"
        f"Sentence: {md['sentence']}\n"
        f"Content contributions with their sources: {pieces}. The main contribution "
        f"is (asserted): {md['main_content']}.\n"
        f"Now embed this sentence under negation, a conditional, and the attitude "
        f"'{md['name']} {verb} that ...' ({attitude_note}).\n"
        "For each of 'negation', 'conditional', and 'attitude', list every content "
        "piece as a semicolon-separated string, each prefixed by A (asserted) or P "
        "(projective), main first. Format each row as "
        "the context, a colon, then 'A: main: <text>; P: <source>: <text>; ...'. "
        "Answer with exactly three lines, one per context, in the order negation, "
        "conditional, attitude."
    )
