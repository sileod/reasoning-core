"""Direct-inverse inflection synthesizer.

Transitive verb inflection in a synthetic direct-inverse alignment system.
The solver must (1) place two arguments on a person-animacy hierarchy,
(2) decide direct vs inverse voice, (3) produce the voice-altered stem plus
agent and patient agreement affixes.

The assigned design choice makes the verb stem itself vary with voice, so the
answer cannot be produced by affix swapping alone: the solver must also apply
the stem-ablaut rule.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'direct_inverse_inflection (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_paraphrase_equivalence_r1/direct_inverse_inflection',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

PERSON_LABELS = {
    "1s": "1st person singular",
    "1p": "1st person plural",
    "2s": "2nd person singular",
    "2p": "2nd person plural",
    "3": "3rd person",
}

# Hierarchy rank: higher number = more prominent (outranks).
HIERARCHY = {
    "1s": 6, "1p": 5, "2s": 4, "2p": 3,
    "3-prox": 2, "3-obv": 1,
}

# Voice marker in the stem: direct uses '-an' final, inverse uses '-in' final
# and additionally lengthens a short root vowel (a->aa, i->ii, e->ee, o->oo).
# Roots never contain more than one simple vowel we choose to subject to ablaut.
ROOTS = ["kak", "pok", "mik", "wes", "top", "nak", "pil", "wot",
         "bal", "sim", "sen", "tom", "kap", "gim", "del", "nop"]

AGENT_AFFIX = {"1s": "-in", "1p": "-enan", "2s": "-at", "2p": "-eyek", "3": "-ah"}
PATIENT_AFFIX = {"1s": "-in", "1p": "-enan", "2s": "-at", "2p": "-eyek", "3": "-ah"}


def _role_key(role):
    if role["person"] in ("1s", "1p", "2s", "2p"):
        return role["person"]
    # third person: person stays "3", animacy distinguishes prox/obv
    if role["animacy"] == "proximate":
        return "3-prox"
    return "3-obv"


def _affix_key(role):
    if role["person"] in ("1s", "1p", "2s", "2p"):
        return role["person"]
    return "3"


def _rank(role):
    return HIERARCHY[_role_key(role)]


def _ablaut(root, inverse):
    """Apply the stem rule. Inverse lengthens the vowel and final becomes '-in'."""
    if inverse:
        # lengthen the only vowel
        out = []
        for ch in root:
            if ch == "a":
                out.append("aa")
            elif ch == "i":
                out.append("ii")
            elif ch == "e":
                out.append("ee")
            elif ch == "o":
                out.append("oo")
            else:
                out.append(ch)
        return "".join(out) + "in"
    return root + "an"


def _voice(agent, patient):
    """Return ('direct'|'inverse', boolean inverse)."""
    ar = _rank(agent)
    pr = _rank(patient)
    if ar > pr:
        return "direct", False
    return "inverse", True


def _role_for_person(person, animacy="proximate"):
    return {"person": person, "animacy": animacy}


def _make_args(third_prob):
    """Produce an (agent, patient) pair with a decided voice.

    With probability `third_prob` the instance is a third-vs-third pair where
    proximate/obviative status decides the voice; otherwise it is a
    non-third-vs-third pair where the fixed hierarchy decides the voice. Both
    voices are represented in each family, so the label stays balanced while the
    structural depth (prox/obv reasoning vs trivial hierarchy reading) scales
    with the difficulty level.
    """
    if random.random() < third_prob:
        # third-vs-third: whichever is proximate outranks the obviative one.
        if random.random() < 0.5:
            agent = _role_for_person("3", "proximate")
            patient = _role_for_person("3", "obviative")
        else:
            agent = _role_for_person("3", "obviative")
            patient = _role_for_person("3", "proximate")
        return agent, patient
    # non-third-vs-third: voice follows the fixed hierarchy 1st/2nd > 3rd.
    if random.random() < 0.5:
        agent = _role_for_person(random.choice(["1s", "1p", "2s", "2p"]))
        patient = _role_for_person("3",
                                   random.choice(["proximate", "proximate", "obviative"]))
    else:
        agent = _role_for_person("3", random.choice(["proximate", "obviative"]))
        patient = _role_for_person(random.choice(["1s", "1p", "2s", "2p"]))
    return agent, patient


@dataclass
class DirectInverseConfig(Config):
    third_prob: float = 0.4

    def apply_difficulty(self, level):
        # As level rises, a larger share of instances are third-vs-third, forcing
        # the proximate/obviative status assignment and the voice decision off the
        # hierarchy, rather than the trivial non-third-vs-third case. Capped so
        # the instance pool keeps structural variety even at high levels.
        self.third_prob = min(0.35 + 0.055 * level, 0.68)


class DirectInverseInflection(Task):
    summary = ("Inflect transitive verbs in a synthetic direct-inverse system: compare arguments "
               "on a person-animacy hierarchy, assign proximate/obviative status among third "
               "persons, choose direct or inverse voice; answer the fully inflected forms.")
    design_choice = ("Generate verbs whose stem shape changes predictably under direct vs inverse "
                     "voice, so the solver must produce the altered stem plus agreement affixes, "
                     "not just affix swapping.")
    config_cls = DirectInverseConfig

    def generate_entry(self):
        agent, patient = _make_args(self.config.third_prob)
        inverse = _voice(agent, patient)[1]
        root = random.choice(ROOTS)

        stem = _ablaut(root, inverse)
        agent_affix = AGENT_AFFIX[_affix_key(agent)]
        patient_affix = PATIENT_AFFIX[_affix_key(patient)]
        full_form = stem + agent_affix + patient_affix

        # assert the domain: answer is a non-empty string of letters/dashes
        assert full_form, "answer must be non-empty"
        # reinject a self-consistency check: recompute and compare
        assert full_form == _inflect(agent, patient, root), "self-check mismatch"

        metadata = {
            "agent": agent,
            "patient": patient,
            "root": root,
            "voice": "direct" if not inverse else "inverse",
            "stem": stem,
            "agent_affix": agent_affix,
            "patient_affix": patient_affix,
            "full_form": full_form,
        }
        return Entry(metadata=metadata, answer=full_form)

    def score_answer(self, answer, entry):
        return 1.0 if answer == _gold_string(entry) else 0.0

    def render_prompt(self, metadata):
        a = metadata["agent"]
        p = metadata["patient"]
        a_desc = _describe_role(a)
        p_desc = _describe_role(p)
        return (
            "A language uses a direct~inverse verb alignment over a person-animacy "
            "hierarchy: 1st > 1st-plural > 2nd > 2nd-plural > proximate-3rd > obviative-3rd. "
            "The agent is the more prominent participant. If the agent outranks the patient the "
            "clause is DIRECT; if the patient outranks the agent it is INVERSE.\n"
            f"The agent is {a_desc} and the patient is {p_desc}.\n"
            f"The transitive verb root is '{metadata['root']}'. The verb stem is the root plus a "
            "voice marker: in the DIRECT voice the stem is root + '-'an'; in the INVERSE voice the "
            "stem is root with its vowel lengthened (a, i, e, o become aa, ii, ee, oo) plus '-'in'.\n"
            "Agreement is shown by two suffixes after the stem: first the agent agreement suffix, "
            "then the patient agreement suffix. The suffixes are: 1st singular '-in', 1st plural "
            "'-enan', 2nd singular '-at', 2nd plural '-eyek', and 3rd '-ah'.\n"
            "Give the complete inflected verb: stem + agent suffix + patient suffix. "
            "Answer with just that one inflected form."
        )


def _inflect(agent, patient, root):
    inverse = _voice(agent, patient)[1]
    stem = _ablaut(root, inverse)
    return stem + AGENT_AFFIX[_affix_key(agent)] + PATIENT_AFFIX[_affix_key(patient)]


def _describe_role(role):
    if role["person"] in ("1s", "1p", "2s", "2p"):
        return PERSON_LABELS[role["person"]]
    return f"{role['animacy']} third person"


def _gold_string(entry):
    return (_ablaut(entry.metadata["root"],
                    _voice(entry.metadata["agent"], entry.metadata["patient"])[1])
            + AGENT_AFFIX[_affix_key(entry.metadata["agent"])]
            + PATIENT_AFFIX[_affix_key(entry.metadata["patient"])])
