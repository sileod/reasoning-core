import random
from dataclasses import dataclass

from reasoning_core.template import Task, Entry, Config, edict

LICENSORS = [
    "negation",
    "only",
    "few",
    "question",
    "conditional",
    "comparative",
    "adversative",
    "unlicensed",
]

VOCAB = "one of: negation, only, few, question, conditional, comparative, adversative, unlicensed"

NAMES = [
    "Mia", "Dan", "the guard", "the clerk", "Sam", "Jo",
    "the analyst", "the reviewer", "Nina", "Omar", "the auditor", "the assistant",
]
NOUN_PL = [
    "reports", "files", "charts", "records", "emails", "drafts",
    "checks", "scans", "logs", "forms",
]
NOUN_SG = [
    "report", "file", "document", "entry", "record", "review",
    "inspection", "ledger",
]
VERBS = ["read", "reviewed", "inspected", "approved", "signed", "examined"]
VERBS_BASE = ["read", "review", "inspect", "approve", "sign", "examine"]
ADJS = ["complex", "difficult", "demanding", "thorough", "careful", "strict"]
REACT = ["denied", "doubted", "regretted"]


def _pi():
    return "any " + random.choice(NOUN_PL)


def _main_clause(lic):
    name = random.choice(NAMES)
    noun_pl = random.choice(NOUN_PL)
    verb = random.choice(VERBS)
    vbase = random.choice(VERBS_BASE)
    if lic == "negation":
        return f"{name} did not {vbase} {_pi()}."
    if lic == "only":
        return f"Only {name} {verb} {_pi()}."
    if lic == "few":
        return f"Few {noun_pl} {verb} {_pi()}."
    if lic == "question":
        vbase = random.choice(VERBS_BASE)
        if random.random() < 0.5:
            return f"Did {name} {vbase} {_pi()}?"
        return f"Why did {name} {vbase} {_pi()}?"
    if lic == "conditional":
        nsing = random.choice(NOUN_SG)
        return f"If {name} {verb} {_pi()}, the {nsing} was accepted."
    if lic == "comparative":
        nsing = random.choice(NOUN_SG)
        adj = random.choice(ADJS)
        return f"The {nsing} was more {adj} than {name} {verb} {_pi()}."
    if lic == "adversative":
        name2 = random.choice(NAMES)
        react = random.choice(REACT)
        return f"{name} {react} that {name2} {verb} {_pi()}."
    return f"{name} {verb} {_pi()}."


def _decoy_clause():
    name = random.choice(NAMES)
    nsing = random.choice(NOUN_SG)
    noun_pl = random.choice(NOUN_PL)
    verb = random.choice(VERBS)
    vbase = random.choice(VERBS_BASE)
    kind = random.choice(["neg", "only", "few", "question"])
    if kind == "neg":
        return f"Nobody {verb} the {nsing}."
    if kind == "only":
        return f"Only {name} {verb} the {nsing}."
    if kind == "few":
        return f"Few {noun_pl} {verb} the {nsing}."
    return f"Did {name} {vbase} the {nsing}?"


@dataclass
class PolarityItemLicensingConfig(Config):
    min_decoy: int = 0
    max_decoy: int = 0

    def apply_difficulty(self, level):
        self.min_decoy = max(0, level - 1)
        self.max_decoy = level


class PolarityItemLicensing(Task):
    summary = ("Judge whether a polarity item is licensed in its environment: clause-mate negation, "
               "only, few, questions, conditionals, comparatives, adversative predicates; name the "
               "licensor or return unlicensed, amid decoy clauses that do not govern the item.")
    design_choice = ("Answer format: a single token from a fixed vocabulary of licensor names (e.g., "
                     "'negation', 'only', 'few', 'question', 'conditional', 'comparative', "
                     "'adversative', 'unlicensed'), with each instance requiring exactly one label.")
    config_cls = PolarityItemLicensingConfig

    def generate_entry(self):
        n_decoy = random.randint(self.config.min_decoy, self.config.max_decoy)
        decoys = [_decoy_clause() for _ in range(n_decoy)]
        lic = random.choice(LICENSORS)
        main = _main_clause(lic)
        metadata = edict({
            "lic": lic,
            "n_decoy": n_decoy,
        })
        metadata.payload = {
            "decoys": decoys,
            "main": main,
        }
        return Entry(metadata=metadata, answer=lic)

    def render_prompt(self, metadata):
        rules = (
            "Licensing rules: a polarity item is licensed by exactly one of these, or unlicensed.\n"
            "- negation: 'not' licenses an item in its own clause.\n"
            "- only: 'Only X' licenses an item later in the same clause.\n"
            "- few: 'Few N' (downward entailing) licenses an item in the same clause.\n"
            "- question: a question licenses an item in its own clause.\n"
            "- conditional: an 'if'-antecedent licenses an item in that antecedent.\n"
            "- comparative: a 'more ... than' construction licenses an item in the than-clause.\n"
            "- adversative: 'denied/doubted/regretted' license an item in their 'that'-complement.\n"
            "A negation, only, few or question outside the item's own clause does not license it.\n"
            "In the text below, the polarity item is 'any' and it appears exactly once.\n\n"
        )
        pieces = metadata.payload["decoys"] + [metadata.payload["main"]]
        body = " ".join(pieces)
        fmt = (
            "\n\nWhich licensor licenses the polarity item 'any' in that sentence, or is it "
            "unlicensed? Other sentences are context only and do not govern the item. Answer "
            f"exactly one token, {VOCAB}. Example answers: negation, few, unlicensed."
        )
        return rules + body + fmt

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip().lower()
        gold = str(entry.answer).strip().lower()
        return 1.0 if a == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'polarity_item_licensing (draw 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_parsing_and_agreement_r1/polarity_item_licensing',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
