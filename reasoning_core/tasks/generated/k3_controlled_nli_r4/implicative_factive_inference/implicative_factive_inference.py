import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'implicative_factive_inference (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_controlled_nli_r4/implicative_factive_inference',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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

design_choice = "Answer as a three-way label: ENTAILED, DENIED, or OPEN, for the complement under the matrix verb's polarity and embedding type."

# Verb -> asserted state of the complement under plain positive/negative polarity.
# +1: complement asserted true (ENTAILED). -1: asserted false (DENIED). 0: open.
# pretend under negation asserts nothing about P. All others are classic implicatives.
VERB_STATE = {
    "manage":   {"pos": +1, "neg": -1},
    "fail":     {"pos": -1, "neg": +1},
    "remember": {"pos": +1, "neg": -1},
    "forget":   {"pos": -1, "neg": +1},
    "pretend":  {"pos": -1, "neg": 0},
}

ACTIONS = ["finish the report", "attend the meeting", "lock the door", "pay the bill"]


def _complement_form(action, negated):
    return ("not " + action) if negated else action


def _asserted_state(verb, polarity_negated):
    """State of the complement (as an assertion about it) from matrix verb+polarity.

    Returns +1/-1/0 meaning the matrix sentence asserts the complemented
    proposition is true/false/open respectively.
    """
    return VERB_STATE[verb]["neg" if polarity_negated else "pos"]


def _outcome(state, complement_negated):
    """Final label given how strongly the matrix asserts the complement and
    whether the complement itself is a negated action.

    state in {-1,0,+1}: matrix asserts complement-true/false/open.
    complement_negated: the embedded action is negated, flipping truth.
    """
    if state == 0:
        return "OPEN"
    # state +1 means matrix asserts the (possibly negated) complement proposition
    truth = (state > 0) != complement_negated
    return "ENTAILED" if truth else "DENIED"


@dataclass
class ImplicativeFactiveConfig(Config):
    cond_prob: float = 0.30
    q_prob: float = 0.20
    comp_neg: float = 0.2
    compare_prob: float = 0.4

    def apply_difficulty(self, level):
        self.cond_prob = min(0.3 + 0.15 * level, 0.85)
        self.q_prob = min(0.2 + 0.12 * level, 0.80)
        self.comp_neg = 0.2
        self.compare_prob = 0.4


class ImplicativeFactiveInference(Task):
    summary = ("Implicative and factive verbs (manage, fail, remember, pretend) under "
               "negation and conditional or question embedding; compute whether the "
               "complement is entailed, denied or open; also judge equivalence with "
               "the bare assertion.")
    config_cls = ImplicativeFactiveConfig
    task_version = 2

    def generate_entry(self):
        verb = random.choice(list(VERB_STATE))
        action = random.choice(ACTIONS)
        complement_negated = random.random() < self.config.comp_neg
        comp = _complement_form(action, complement_negated)

        emb = random.random()
        if emb < self.config.cond_prob:
            embedding = "conditional"
        elif emb < self.config.cond_prob + self.config.q_prob:
            embedding = "question"
        else:
            embedding = "plain"

        polarity_negated = random.random() < 0.5
        neg_word = "did not" if polarity_negated else "did"

        if embedding == "plain":
            sentence = f"You {neg_word} {verb} to {comp}."
        elif embedding == "question":
            neg_inner = "not " if polarity_negated else ""
            sentence = f"Did you {neg_inner}{verb} to {comp}?"
        else:
            sentence = f"If you {verb} to {comp}, then you subscribed."

        # Under a plain assertion, the verb's polarity asserts the complement.
        # Under a conditional antecedent or a question there is no matrix
        # assertion of the complement, so it is left open (unless factive).
        if embedding == "plain":
            state = _asserted_state(verb, polarity_negated)
        else:
            # pretend/question-conditional: nothing is asserted about P
            state = 0
        outcome = _outcome(state, complement_negated)

        compare = random.random() < self.config.compare_prob
        if compare:
            bare = f"You {verb} to {comp}."
            gold = {"ENTAILED": "YES", "DENIED": "NO", "OPEN": "MAYBE"}[outcome]
            prompt = (f"For the sentence \"{sentence}\", decide whether it is equivalent "
                      f"to the bare assertion \"{bare}\": reply YES when the assertion "
                      f"necessarily follows, NO when its negation necessarily follows "
                      f"given the sentence, and MAYBE when the sentence leaves it open. "
                      f"Pick one word by the truth you actually derived from the sentence.")
        else:
            prompt = (f"For the sentence \"{sentence}\", give the truth of the complement "
                      f"\"{comp}\" forced by the implicative verb '{verb}', its polarity "
                      f"and how it is embedded: reply ENTAILED, DENIED, or OPEN. Pick the "
                      f"one word that matches the inference you derived.")

        return Entry(
            metadata={
                "verb": verb,
                "polarity_negated": polarity_negated,
                "complement": comp,
                "action": action,
                "complement_negated": complement_negated,
                "embedding": embedding,
                "label": outcome,
                "compare": compare,
                "example": sentence,
            },
            answer=gold if compare else outcome,
        )

    def render_prompt(self, metadata):
        sentence = metadata["example"]
        verb = metadata["verb"]
        comp = metadata["complement"]
        if metadata["compare"]:
            bare = f"You {verb} to {comp}."
            return (f"For the sentence \"{sentence}\", decide whether it is equivalent "
                    f"to the bare assertion \"{bare}\": reply YES when the assertion "
                    f"necessarily follows, NO when its negation necessarily follows "
                    f"given the sentence, and MAYBE when the sentence leaves it open. "
                    f"Pick one word by the truth you actually derived from the sentence.")
        return (f"For the sentence \"{sentence}\", give the truth of the complement "
                f"\"{comp}\" forced by the implicative verb '{verb}', its polarity "
                f"and how it is embedded: reply ENTAILED, DENIED, or OPEN. Pick the "
                f"one word that matches the inference you derived.")

    def distractor_candidates(self, entry):
        for lab in ("ENTAILED", "DENIED", "OPEN", "YES", "NO", "MAYBE"):
            if lab != entry.answer:
                yield lab

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip().upper() == entry.answer else 0.0
