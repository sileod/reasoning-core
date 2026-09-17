"""Centering transition tracking: two entities, explicit obliqueness ranking."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

CONTINUE = "continue"
RETAIN = "retain"
SHIFT = "shift"
LABELS = (CONTINUE, RETAIN, SHIFT)

FEMALE = ["Maria", "Elena", "Sofia", "Nadia", "Priya", "Ingrid"]
MALE = ["Tomas", "Victor", "Dmitri", "Rashid", "Kwame", "Ivan"]
PRONOUN = {0: ("she", "her"), 1: ("he", "him")}
TRANSITIVE = ["called", "praised", "visited", "thanked", "phoned",
              "congratulated", "warned", "invited"]
INTRANSITIVE = ["arrived", "left", "smiled", "sighed", "waited", "paused", "waved"]

TASK_META = {'parent_source_id': None,
 'idea': 'centering_transition_tracking (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_controlled_nli_r1/centering_transition_tracking',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
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


@dataclass
class CenteringTransitionTrackingConfig(Config):
    n_utterances: int = 3
    pronoun_prob: float = 0.3

    def apply_difficulty(self, level):
        self.n_utterances = 3 + level
        self.pronoun_prob = min(0.9, 0.3 + 0.1 * level)


def _backward_center(prev_cf, cf):
    """Highest-ranked entity of prev_cf realized in cf, else None."""
    for entity in prev_cf:
        if entity in cf:
            return entity
    return None


def _transitions(cf_lists):
    """Centering transition labels for utterances 2..N from Cf lists."""
    labels = []
    prev_cb = None
    for i in range(1, len(cf_lists)):
        prev_cf, cf = cf_lists[i - 1], cf_lists[i]
        cb = _backward_center(prev_cf, cf)
        if cb is None:
            raise RuntimeError("backward center undefined")
        top = cf[0]
        if cb == top:
            labels.append(CONTINUE if cb == prev_cb else RETAIN)
        else:
            labels.append(SHIFT)
        prev_cb = cb
    return labels


def _render_utterance(u, names):
    subject, obj, verb, subj_pron, obj_pron = u
    who = lambda e, p: PRONOUN[e][0] if p else names[e]
    if obj is None:
        return f"{who(subject, subj_pron)} {verb}."
    whom = PRONOUN[obj][1] if obj_pron else names[obj]
    return f"{who(subject, subj_pron)} {verb} {whom}."


class CenteringTransitionTracking(Task):
    summary = ("Track two-entity discourse centers over a short dialogue: rank "
               "realized mentions by the stated subject-over-object obliqueness "
               "order, take the backward-looking center as the highest-ranked "
               "entity of the previous utterance realized in the current one, "
               "and emit the continue/retain/shift transition sequence.")
    design_choice = ("Use a fixed template with two named entities and explicit "
                     "obliqueness rankings, varying only the pronoun references "
                     "and verb semantics to produce deterministic transition labels.")
    config_cls = CenteringTransitionTrackingConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        female_name = random.choice(FEMALE)
        male_name = random.choice(MALE)
        names = (female_name, male_name)

        utterances = []
        cf_lists = []
        # first utterance mentions both entities so a backward center always exists
        subject = random.randint(0, 1)
        obj = 1 - subject
        utterances.append((subject, obj, random.choice(TRANSITIVE),
                           random.random() < cfg.pronoun_prob,
                           random.random() < cfg.pronoun_prob))
        cf_lists.append([subject, obj])

        for _ in range(cfg.n_utterances - 1):
            for _attempt in range(200):
                subject = random.randint(0, 1)
                if random.random() < 0.7:
                    obj = 1 - subject
                    verb = random.choice(TRANSITIVE)
                else:
                    obj = None
                    verb = random.choice(INTRANSITIVE)
                cf = [subject] if obj is None else [subject, obj]
                if _backward_center(cf_lists[-1], cf) is not None:
                    break
            else:
                raise RuntimeError("could not build an utterance with a backward center")
            utterances.append((subject, obj, verb,
                               random.random() < cfg.pronoun_prob,
                               obj is not None and random.random() < cfg.pronoun_prob))
            cf_lists.append(cf)

        labels = _transitions(cf_lists)
        text = [f"{i + 1}. {_render_utterance(u, names)}"
                for i, u in enumerate(utterances)]
        assert len(labels) == cfg.n_utterances - 1
        assert all(label in LABELS for label in labels)
        assert all(len(cf) in (1, 2) for cf in cf_lists)
        answer = ",".join(labels)
        return Entry(metadata={"names": list(names),
                               "utterances": text,
                               "cf_lists": [list(cf) for cf in cf_lists],
                               "backward_centers":
                                   [_backward_center(cf_lists[i - 1], cf_lists[i])
                                    for i in range(1, len(cf_lists))]},
                     answer=answer)

    def render_prompt(self, metadata):
        return (
            "In a short dialogue each utterance mentions one or both of two people. "
            "Rank the people mentioned in an utterance by obliqueness: the subject "
            "ranks above the direct object (a lone subject is the only mention). "
            "The backward-looking center of an utterance is the highest-ranked person "
            "of the previous utterance that is also mentioned in the current one.\n"
            "For every utterance from the second onward, label its transition:\n"
            "- continue: the backward-looking center is the highest-ranked person of "
            "the current utterance and equals the backward-looking center of the "
            "previous utterance;\n"
            "- retain: it is the highest-ranked person of the current utterance but "
            "differs from the previous backward-looking center (the second utterance, "
            "having no previous center, is labeled retain in this case);\n"
            "- shift otherwise.\n"
            "Pronouns refer to exactly one person and resolve by gender.\n\n"
            "Dialogue:\n" + "\n".join(metadata["utterances"]) +
            "\n\nGive one label per utterance from the second onward, in order, as a "
            "comma-separated sequence. Example format: continue,shift,retain"
        )

    def score_answer(self, answer, entry):
        gold = str(entry.answer).strip().lower().split(",")
        given = str(answer).strip().lower().replace(" ", "").split(",")
        if given != gold or not all(label in LABELS for label in gold):
            return 0.0
        return 1.0
