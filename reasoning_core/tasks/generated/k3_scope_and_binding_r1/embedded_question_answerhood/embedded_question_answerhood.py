"""Verdict-only reading judgments for embedded wh-questions.

For a scenario of one or more sentences, each embedding a wh-question under
``know``, ``tell`` or ``wonder``, the model classifies the reading of each
complement as ``exhaustive``, ``mention-some`` or ``pair-list`` and replies
with the ordered label sequence. The reading follows a fixed, stated
convention: two wh-phrases in the clause give ``pair-list``; a wonder-complement
(or an unmarked know/tell clause) gives ``exhaustive``; a know/tell clause
carrying a possibility marker gives ``mention-some``.
"""

import random

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'embedded_question_answerhood (draw 2 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scope_and_binding_r1/embedded_question_answerhood',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3020341981,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

SUBJECTS = ["Kay", "Ann", "Ben", "Sara", "Tom", "Lia", "Mina", "Omar", "Nora", "Ravi"]
AGENTS = ["Leo", "Ana", "Ivo", "Mia", "Zed", "Pia", "Gus", "Tess"]
RECIPIENTS = ["Lee", "Ada", "Ugo", "Rex", "Ina", "Yara"]

DOUBLE = [
    "{S} knows who called whom.",
    "{S} knows who gave which gift.",
    "{S} knows which student chose which topic.",
    "{S} told {R} who works in which office.",
    "{S} wonders who bought which ticket.",
    "{S} knows who wrote which chapter.",
    "{S} told {R} who brought what.",
    "{S} wonders which guest reserved which room.",
    "{S} knows who fixed which door.",
]

WONDER = [
    "{S} wonders who came to the meeting.",
    "{S} wonders which book {A} chose.",
    "{S} wonders what caused the outage.",
    "{S} wonders who should present first.",
    "{S} wonders which route the bus takes.",
    "{S} wonders who will attend the ceremony.",
    "{S} wonders which code the safe opens with.",
]

EXHAUSTIVE = [
    "{S} knows who came to the meeting.",
    "{S} knows who was hired for the project.",
    "{S} knows which prizes {A} awarded.",
    "{S} knows what was on today's menu.",
    "{S} knows where the keys were left.",
    "{S} told {R} who submitted the proposal.",
    "{S} told {R} which tasks remain unfinished.",
    "{S} knows who won the final match.",
    "{S} knows which route the courier took.",
]

MENTION = [
    "{S} knows where she can buy a newspaper at night.",
    "{S} knows which nearby shop still has the medicine in stock.",
    "{S} knows who can fix the broken tap.",
    "{S} told {R} which restaurant has a free table tonight.",
    "{S} knows where there is an open gas station.",
    "{S} knows which colleague is available to cover the shift.",
    "{S} told {R} who is able to give a ride home.",
    "{S} knows which cafe is still open after nine.",
]

_WH2 = "pair-list"
_WONDER_SINGLE = "exhaustive"
_MS = "mention-some"
_EXH = "exhaustive"

_P_DOUBLE = 1.0 / 3.0
_P_WONDER = 0.30


def _fill(template, subj, agent, recip):
    return template.format(S=subj, A=agent, R=recip)


def _make_ascription():
    if random.random() < _P_DOUBLE:
        subj = random.choice(SUBJECTS)
        agent = random.choice(AGENTS)
        recip = random.choice(RECIPIENTS)
        return _fill(random.choice(DOUBLE), subj, agent, recip), None, _WH2
    subj = random.choice(SUBJECTS)
    agent = random.choice(AGENTS)
    recip = random.choice(RECIPIENTS)
    if random.random() < _P_WONDER:
        return _fill(random.choice(WONDER), subj, agent, recip), "wonder", _WONDER_SINGLE
    if random.random() < (0.5 / (1.0 - _P_WONDER)):
        return _fill(random.choice(MENTION), subj, agent, recip), "known", _MS
    return _fill(random.choice(EXHAUSTIVE), subj, agent, recip), "known", _EXH


class EmbeddedQuestionConfig(Config):
    count: int = 1

    def apply_difficulty(self, level):
        self.count = 1 + max(0, (level + 1) // 2)


class EmbeddedQuestionAnswerhood(Task):
    """Judge exhaustive vs mention-some vs pair-list readings of embedded wh-questions."""

    summary = ("Classify embedded wh-question readings as exhaustive, mention-some, or "
               "pair-list: single-wh know/tell with a possibility marker gives mention-some, "
               "two-wh clauses give pair-list, and wonder or unmarked know/tell gives "
               "exhaustive; answer is the ordered verdict sequence.")
    design_choice = ("Use a verdict-only format: output one of 'exhaustive', "
                     "'mention-some', or 'pair-list' for each given ascription, "
                     "with no explicit answer set.")
    config_cls = EmbeddedQuestionConfig
    task_version = 2

    def generate_entry(self):
        ascriptions = []
        verdicts = []
        for _ in range(self.config.count):
            sentence, verb, verdict = _make_ascription()
            ascriptions.append(sentence)
            verdicts.append(verdict)
        return Entry(
            metadata={
                "ascriptions": ascriptions,
                "verdicts": verdicts,
            },
            answer=" ".join(verdicts),
        )

    def render_prompt(self, metadata):
        lines = []
        for i, sent in enumerate(metadata["ascriptions"], 1):
            lines.append(f"{i}) {sent}")
        numbered = "\n".join(lines)
        return (
            "For each numbered sentence, an embedded wh-question appears under the verbs "
            "know, tell, or wonder. Decide which reading that complement receives and reply "
            "with exactly that many verdict words, one per sentence in the same order, "
            "separated by single spaces.\n\n"
            "Convention: a clause with two wh-phrases is pair-list; a wonder-complement is "
            "exhaustive; a know or tell clause carrying a possibility marker (can, able, "
            "available, in stock, open, free) is mention-some; every other know or tell "
            "clause is exhaustive.\n\n"
            + numbered
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        expected = " ".join(entry["metadata"]["verdicts"])
        if answer.strip() == expected:
            return 1.0
        return 0.0
