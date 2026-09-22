import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'centering_transition_walk (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_controlled_nli_r4/centering_transition_walk',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

A_NPS = ["the doctor", "the lawyer", "the teacher", "the nurse", "the coach", "the guard"]
B_NPS = ["the patient", "the client", "the student", "the guest", "the officer", "the buyer"]

TVERBS = ["saw", "met", "greeted", "found", "noticed", "called", "watched", "joined"]
REFL = ["examined", "studied", "praised", "admired"]
INTRANS = ["paused", "sighed", "waited", "nodded", "left"]

SHAPES = [
    ("full", "full"),
    ("full", "pron"),
    ("pron", "full"),
    ("pron", "pron"),
    ("full", "absent"),
    ("pron", "absent"),
    ("full", "pron"),
]


def _np(ent, a_np, b_np):
    return a_np if ent == "A" else b_np


def _psubj(ent):
    return "She" if ent == "A" else "He"


def _pobj(ent):
    return "her" if ent == "A" else "him"


def _prefl(ent):
    return "herself" if ent == "A" else "himself"


def build_utterance():
    a_np = random.choice(A_NPS)
    b_np = random.choice(B_NPS)
    sub_entity = random.choice(["A", "B"])
    shape = random.choice(SHAPES)
    sub_form, obj_form = shape
    if obj_form == "pron" and sub_form == "full" and sub_entity == "A":
        obj_entity = sub_entity if random.random() < 0.35 else "B"
    elif sub_form == "pron" and obj_form == "full":
        obj_entity = sub_entity if random.random() < 0.35 else ("B" if sub_entity == "A" else "A")
    elif sub_form == "pron" and obj_form == "pron":
        obj_entity = sub_entity if random.random() < 0.25 else ("B" if sub_entity == "A" else "A")
    else:
        obj_entity = "B" if sub_entity == "A" else "A"
    return {
        "a_np": a_np,
        "b_np": b_np,
        "sub_entity": sub_entity,
        "sub_form": sub_form,
        "obj_entity": obj_entity,
        "obj_form": obj_form,
    }


def render_utterance(spec):
    sub_entity = spec["sub_entity"]
    obj_entity = spec["obj_entity"]
    sub_form = spec["sub_form"]
    obj_form = spec["obj_form"]
    if sub_form == "full" and obj_form == "full":
        s = f"{_np(sub_entity, spec['a_np'], spec['b_np'])} {random.choice(TVERBS)} {_np(obj_entity, spec['a_np'], spec['b_np'])}."
    elif sub_form == "full" and obj_form == "pron":
        if sub_entity == obj_entity:
            s = f"{_np(sub_entity, spec['a_np'], spec['b_np'])} {random.choice(REFL)} {_prefl(obj_entity)}."
        else:
            s = f"{_np(sub_entity, spec['a_np'], spec['b_np'])} {random.choice(TVERBS)} {_pobj(obj_entity)}."
    elif sub_form == "pron" and obj_form == "full":
        s = f"{_psubj(sub_entity)} {random.choice(TVERBS)} {_np(obj_entity, spec['a_np'], spec['b_np'])}."
    elif sub_form == "pron" and obj_form == "pron":
        if sub_entity == obj_entity:
            s = f"{_psubj(sub_entity)} {random.choice(REFL)} {_prefl(obj_entity)}."
        else:
            s = f"{_psubj(sub_entity)} {random.choice(TVERBS)} {_pobj(obj_entity)}."
    elif sub_form == "full" and obj_form == "absent":
        s = f"{_np(sub_entity, spec['a_np'], spec['b_np'])} {random.choice(INTRANS)}."
    elif sub_form == "pron" and obj_form == "absent":
        s = f"{_psubj(sub_entity)} {random.choice(INTRANS)}."
    else:
        raise RuntimeError("bad form")
    return s[:1].upper() + s[1:]


def utterance_state(spec):
    cf = []
    for role in ("sub", "obj"):
        if spec[role + "_form"] == "full":
            cf.append(spec[role + "_entity"])
    cp = cf[0] if cf else None
    cb = None
    for role in ("sub", "obj"):
        if spec[role + "_form"] == "pron":
            cb = spec[role + "_entity"]
            break
    return {"Cf": cf, "Cp": cp, "Cb": cb}


def transition_label(prev, cur):
    p_cb, p_cp, p_cf = prev["Cb"], prev["Cp"], prev["Cf"]
    c_cb = cur["Cb"]
    if c_cb is None:
        return "establish"
    if p_cb is None:
        return "smooth-shift" if c_cb in p_cf else "rough-shift"
    if c_cb == p_cb:
        return "continue" if p_cb == p_cp else "retain"
    return "smooth-shift" if c_cb in p_cf else "rough-shift"


@dataclass
class CenteringConfig(Config):
    pairs: int = 3

    def apply_difficulty(self, level):
        self.pairs = 3 + level


class CenteringTransitionWalk(Task):
    summary = ("Execute a stated centering algorithm over multi-sentence passages: rank "
               "forward-looking centers by the given role order, resolve each pronoun to the "
               "top accessible candidate, and report the transition label at every step.")
    design_choice = ("Use sentence pairs from a fixed corpus and ask for the transition label "
                     "between each adjacent pair, with the role order always subject > object "
                     "> other.")
    config_cls = CenteringConfig
    task_version = 2

    def generate_entry(self):
        n_pairs = int(self.config.pairs)
        specs = [build_utterance() for _ in range(n_pairs + 1)]
        text = " ".join(render_utterance(s) for s in specs)
        states = [utterance_state(s) for s in specs]
        labels = [transition_label(states[i], states[i + 1]) for i in range(n_pairs)]
        answer = " ".join(labels)
        states2 = [utterance_state(s) for s in specs]
        labels2 = [transition_label(states2[i], states2[i + 1]) for i in range(n_pairs)]
        if labels2 != labels:
            raise RuntimeError("centering label verification failed")
        metadata = {
            "passage_text": text,
            "pairs": n_pairs,
            "specs": specs,
            "states": [[{"Cf": list(st["Cf"]), "Cp": st["Cp"], "Cb": st["Cb"]} for st in states]],
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        pas = metadata["passage_text"]
        n = metadata["pairs"]
        return (
            "Centering transition walk. Every sentence has a subject role and an object role. "
            "Forward-looking centers Cf of a sentence are its entities realized by a full noun "
            "phrase, ranked by role order subject > object > other, so the preferred center Cp "
            "is the highest-ranked full-NP entity. The backward-looking center Cb is the "
            "subject-role pronoun if one exists, else the object-role pronoun if one exists, "
            "else none. Between each adjacent sentence pair, the transition label is: "
            "establish if the current Cb is none; continue if current Cb equals previous Cb and "
            "previous Cb equals previous Cp; retain if current Cb equals previous Cb but "
            "previous Cb differs from previous Cp; smooth-shift if current Cb differs from "
            "previous Cb and current Cb is in the previous Cf; rough-shift if current Cb "
            "differs from previous Cb and current Cb is not in the previous Cf.\n\n"
            f"Passage ({n} adjacent pairs):\n{pas}\n\n"
            f"Report the {n} transition labels in order, separated by single spaces, using "
            "exactly the tokens establish, continue, retain, smooth-shift, rough-shift."
        )

    def score_answer(self, answer, entry):
        return 1.0 if isinstance(answer, str) and answer.split() == entry.answer.split() else 0.0
