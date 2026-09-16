import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

FACTIVE_V = ["know", "realize", "regret", "notice", "be aware"]
DEFINITE_N = ["king", "student", "author", "owner", "manager", "editor"]
PEOPLE = ["Alice", "Bob", "the manager", "the professor", "the senator",
          "the director", "the intern", "the clerk"]
MODALS = ["must", "might", "may", "should", "could"]
ATTITUDES = ["believe", "think", "say", "claim", "suspect"]
CONJ = ["and", "but", "while", "or"]
OBJECTS = ["the report", "the key", "the contract", "the decision", "the plan",
           "the memo", "the budget", "the proposal"]


def _factive_phrase(verb, subj, obj):
    return f"{subj} {verb} that {obj} was approved"


def _definite_phrase(noun, subj):
    return f"the {noun} of {subj}"


def _make_trigger():
    if random.random() < 0.5:
        return ("factive", _factive_phrase(random.choice(FACTIVE_V),
                                           random.choice(PEOPLE),
                                           random.choice(OBJECTS)))
    return ("definite", _definite_phrase(random.choice(DEFINITE_N),
                                         random.choice(PEOPLE)))


def _generate(level):
    """Return (sentence, per-trigger projection verdicts).

    Projection model (classic, positional):
      - A lone trigger, or a coordination under negation / a modal / an attitude
        verb, has all presuppositions project (Y...Y).
      - A bare coordination C1 C2 ... Cn: the first clause's presupposition
        projects, every later clause's is filtered by the earlier assertions and
        does not project (Y N...N).
    """
    n = 2 if level == 0 else (3 if level <= 4 else 4)
    triggers = [_make_trigger() for _ in range(n)]
    phrases = [t[1] for t in triggers]

    if random.random() < 0.5:
        # scope operator over the whole coordination -> everything projects
        con = " and ".join(phrases)
        r = random.random()
        if r < 0.34:
            sentence = f"It is not the case that {con}"
        elif r < 0.67:
            sentence = f"It {random.choice(MODALS)} be that {con}"
        else:
            holder = random.choice(PEOPLE)
            sentence = f"{holder} {random.choice(ATTITUDES)} that {con}"
        verdict = [True] * n
    else:
        con = f" {random.choice(CONJ)} ".join(phrases)
        sentence = con
        verdict = [i == 0 for i in range(n)]

    ans = "".join("Y" if v else "N" for v in verdict)
    return sentence, triggers, ans


@dataclass
class PresupConfig(Config):
    level: int = 0

    def apply_difficulty(self, level):
        self.level = level


class PresuppositionProjection(Task):
    summary = ("Project presuppositions from factive and definite triggers through "
               "embeddings (negation, conditionals, modals, disjunction, attitudes) "
               "via filtering and local satisfaction; answers are the surviving set "
               "or a verdict on one trigger, emitted as a single Y/N string per "
               "trigger in order.")
    design_choice = ("Answer format: a single verdict string per trigger in order, e.g., "
                     "'YNY', where Y=projects, N=does not.")
    config_cls = PresupConfig

    def generate_entry(self):
        sentence, triggers, ans = _generate(self.config.level)
        metadata = {
            "sentence": sentence,
            "triggers": [{"phrase": t[1], "type": t[0]} for t in triggers],
            "answer": ans,
        }
        return Entry(metadata=metadata, answer=ans)

    def render_prompt(self, metadata):
        labels = "; ".join(
            f"{i+1}: \"{t['phrase']}\"" for i, t in enumerate(metadata["triggers"])
        )
        return (
            f"Decide which presuppositions survive (project) from the sentence below. "
            f"For each trigger, write Y if its presupposition projects, N if it does not. "
            f"Answer as a single string of Y/N in trigger order.\n\n"
            f"Sentence: {metadata['sentence']}\n"
            f"Triggers: {labels}\n"
            f"Answer (one Y/N per trigger):"
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == entry.answer else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'presupposition_projection (draw 2 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_formal_semantics_r1/presupposition_projection',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2072234021,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
