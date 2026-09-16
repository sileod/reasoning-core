"""Antecedent binding legality.

Generate a phrase-structure tree containing one target expression -- a
reflexive, a reciprocal, a pronoun, or a name (R-expression) -- together with a
fixed list of candidate antecedent DPs. Using the classic binding conditions,
decide for each candidate whether coindexing it with the target yields a
grammatical (licensed) or ungrammatical (blocked) reading.

The verifier computes c-command directly on the generated tree and determines
the governing category (nearest dominating clause) mechanically, so correctness
comes from the computation, not from hand analysis. Principle A (anaphor must be
bound within its local clause), Principle B (pronoun must be free within its
local clause) and Principle C (an R-expression must be free everywhere) are the
standard algorithm named in the prompt.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'antecedent_binding_legality (draw 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scope_and_binding_r1/antecedent_binding_legality',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = "Per-pair binary verdicts (licensed/blocked) for a fixed list of candidate antecedents, with balanced answer distribution enforced across trials."

NAMES = ["Ana", "Ben", "Cora", "Dan", "Eli", "Fay", "Gil", "Hal", "Ira",
         "Jill", "Ken", "Lia", "Max", "Nora", "Owen", "Pia", "Quinn", "Rosa",
         "Sam", "Tess"]
TRANS1 = ["praised", "called", "saw", "scolded", "admired", "ignored",
          "greeted", "recognized", "invited", "thanked"]
TRANS2 = ["thinks", "believes", "expects", "suspects", "concluded",
          "imagined", "claimed", "supposed"]
PREPS = ["with", "about", "from", "to", "for", "near"]
PRONOUNS = ["him", "her"]
REFLEXIVES = ["himself", "herself"]
RECIPROCAL = "each other"


class _N:
    __slots__ = ("label", "children", "parent")

    def __init__(self, label, children=None):
        self.label = label
        self.children = children if children is not None else []
        self.parent = None
        for c in self.children:
            c.parent = self

    def __repr__(self):
        if not self.children:
            return self.label
        return "[" + self.label + " " + " ".join(repr(c) for c in self.children) + "]"


def _subtree(n):
    yield n
    for c in n.children:
        yield from _subtree(c)


def _cc(a, b):
    pa = a.parent
    if pa is None or b is a:
        return False
    def in_sub(root, node):
        return any(x is node for x in _subtree(root))
    return in_sub(pa, b) and not in_sub(a, b)


def _nearest_s(n):
    cur = n.parent
    while cur is not None:
        if cur.label == "S":
            return cur
        cur = cur.parent
    return None


def _verdict(ttype, cand, tgt):
    cc = _cc(cand, tgt)
    same_gc = _nearest_s(cand) is _nearest_s(tgt)
    if ttype in ("anaphor_sg", "anaphor_pl"):
        return "licensed" if (cc and same_gc) else "blocked"
    if ttype == "pronoun":
        return "blocked" if (cc and same_gc) else "licensed"
    return "blocked" if cc else "licensed"


def _sentence(n):
    if not n.children:
        return n.label
    if n.label == "PP":
        return _sentence(n.children[0]) + " " + _sentence(n.children[1])
    return " ".join(_sentence(c) for c in n.children)


def _build(cfg):
    types = cfg.types
    num_outer = cfg.num_outer
    n_side = cfg.n_side
    ttype = random.choice(types)

    pool = list(NAMES)
    random.shuffle(pool)
    names = iter(pool)

    if ttype == "name":
        tgt_surface = next(names)
    elif ttype == "anaphor_sg":
        tgt_surface = random.choice(REFLEXIVES)
    elif ttype == "anaphor_pl":
        tgt_surface = RECIPROCAL
    else:
        tgt_surface = random.choice(PRONOUNS)

    tgt = _N(tgt_surface)

    inn_subj = _N(next(names))
    vp_children = []
    for _ in range(n_side):
        side = _N("PP", [_N(random.choice(PREPS)), _N(next(names))])
        vp_children.append(side)
    vp_children.append(tgt)
    vp = _N("VP", [_N(random.choice(TRANS1))] + vp_children)
    root = _N("S", [inn_subj, vp])

    for _ in range(num_outer):
        osubj = _N(next(names))
        root = _N("S", [osubj, _N("VP", [_N(random.choice(TRANS2)), root])])

    candidates = [n for n in _subtree(root) if n is not tgt and n.label in NAMES]
    return root, ttype, candidates, tgt


@dataclass
class AntecedentConfig(Config):
    types: tuple = ("anaphor_sg", "anaphor_pl", "pronoun", "name")
    num_outer: int = 0
    n_side: int = 1

    def apply_difficulty(self, level):
        self.num_outer = (level + 1) // 2
        self.n_side = 1 + (1 if level >= 3 else 0)


class AntecedentBindingLegality(Task):
    summary = "Judge coindexed reflexive, reciprocal, pronoun, and R-expression pairs on a generated phrase-structure tree for the binding conditions: c-command, within- or cross-clause locality (governing category), and free-everywhere; answer licensed-or-blocked per candidate, both verdicts present and balanced across trials."
    config_cls = AntecedentConfig

    def generate_entry(self):
        for _ in range(200):
            root, ttype, candidates, tgt = _build(self.config)
            verdicts = [_verdict(ttype, c, tgt) for c in candidates]
            if len(set(verdicts)) >= 2:
                break
        else:
            raise RuntimeError("could not build a binding-mixed instance")
        cand_list = [(i + 1, c.label) for i, c in enumerate(candidates)]
        answer = ", ".join(verdicts)
        return Entry(
            metadata={
                "target_type": ttype,
                "target": tgt.label,
                "tree": repr(root),
                "sentence": _sentence(root),
                "candidates": cand_list,
                "verdicts": verdicts,
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        lines = [
            "Using the classic binding conditions (Principle A for anaphors, Principle B for pronouns, Principle C for names), decide whether coindexing the target expression with each candidate antecedent gives a grammatical (licensed) or ungrammatical (blocked) reading.",
            "",
            "Sentence: " + metadata["sentence"],
            "Tree: " + metadata["tree"],
            "",
            "Target expression (T): " + metadata["target"],
            "Candidate antecedents:",
        ]
        for i, name in metadata["candidates"]:
            lines.append(f"  ({i}) {name}")
        lines.append(
            "Answer with one word per candidate 'licensed' or 'blocked' in the order listed above, separated by commas and nothing else, for example: 'licensed, blocked'."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        norm = " ".join(answer.split())
        norm = norm.replace(" ; ", ", ").replace(" licensed ", " licensed,")
        norm = norm.replace(" blocked ", " blocked,")
        norm = norm.rstrip(",").strip()
        if norm == entry.answer:
            return 1.0
        return 0.0
