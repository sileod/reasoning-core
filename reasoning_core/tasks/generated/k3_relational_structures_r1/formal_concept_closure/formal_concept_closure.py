"""Formal concept closure / maximal rectangles on object-attribute incidence contexts.

Given a random binary incidence context (objects x attributes), one of three modes is
asked:

- closure: the closure of a given attribute set under the FCA closure operator;
- concepts: the full sorted concept list (maximal rectangles as (extent, intent) pairs);
- implication: whether an attribute implication X -> Y holds in the context.

Answers are canonical and compact: a sorted list for closure, a sorted list of sorted
pairs for concepts, or a plain yes/no for implication. Mode is randomized, and context
size scales with difficulty using the assigned small/medium/large regime.

FCA definitions used:
  ext(B) = { o | B subset of obj(o) }
  B"     = { a | forall o in ext(B): a in obj(o) }
A concept is (extent E, intent I) with I = E' and E = I' (a maximal rectangle).
Implication X -> Y holds iff Y subset of X''.
"""

import ast
import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


def obj_attribute(context, o):
    return context[o]


def extent_of_intent(context, intent):
    """All objects that carry every attribute in intent (sorted list)."""
    return sorted(o for o in range(len(context)) if set(intent) <= set(context[o]))


def intent_of_extent(context, extent):
    """Attributes shared by every object in extent (sorted list)."""
    shared = set(context[0]) if extent else set(range(len(context[0])))
    for o in extent:
        shared &= set(context[o])
    return sorted(shared)


def compute_concepts(context):
    """All concepts as sorted list of ((extent tuple), (intent tuple))."""
    nobj = len(context)
    objs = range(nobj)
    concepts = set()
    for r in range(nobj + 1):
        for extent in itertools.combinations(objs, r):
            intent = intent_of_extent(context, extent)
            if extent_of_intent(context, intent) == list(extent):
                concepts.add((tuple(extent), tuple(intent)))
    return sorted(concepts)


def closure(context, attrs):
    return intent_of_extent(context, extent_of_intent(context, attrs))


def implication_holds(context, lhs, rhs):
    return set(rhs) <= set(closure(context, lhs))


def _parse_int_list(answer):
    try:
        got = ast.literal_eval(answer)
    except Exception:
        return None
    if not isinstance(got, list):
        return None
    try:
        return sorted(int(x) for x in got)
    except Exception:
        return None


NEG = float("-inf")


def _parse_concepts(answer):
    try:
        got = ast.literal_eval(answer)
    except Exception:
        return None
    if not isinstance(got, list):
        return None
    out = []
    for p in got:
        if not isinstance(p, (list, tuple)) or len(p) != 2:
            return None
        ext, intn = p
        if not isinstance(ext, list) or not isinstance(intn, list):
            return None
        try:
            out.append((tuple(sorted(int(x) for x in ext)), tuple(sorted(int(x) for x in intn))))
        except Exception:
            return None
    return sorted(out)


@dataclass
class FormalConceptClosureConfig(Config):
    level: int = 0
    mode: str = "closure"
    nobj: int = 4
    nattr: int = 4

    def apply_difficulty(self, level):
        # Assigned regime: small for concepts, medium for closure, large for implication.
        if self.mode == "concepts":
            self.nobj = 2 + min(level, 6)
            self.nattr = 2 + min(level, 6)
        elif self.mode == "closure":
            self.nobj = 3 + level * 3
            self.nattr = 3 + level * 3
        else:  # implication
            self.nobj = 5 + level * 7
            self.nattr = 5 + level * 7


class FormalConceptClosure(Task):
    summary = "Compute closures and maximal-rectangle concepts for object-attribute incidence contexts; modes ask one set's closure, the full sorted concept list, or whether an attribute implication holds."
    config_cls = FormalConceptClosureConfig
    design_choice = "Choose context size: small (≤8 objects/attributes) for exhaustive list mode, medium (≤20) for closure mode, large (≤50) for implication checks."

    def _generate_context(self):
        density = 0.35 + random.random() * 0.3
        return [[a for a in range(self.config.nattr) if random.random() < density]
                for _ in range(self.config.nobj)]

    def generate_entry(self):
        mode = self.config.mode
        nattr = self.config.nattr
        while True:
            context = self._generate_context()
            if mode == "closure":
                seed = sorted(random.sample(range(nattr), random.randint(0, nattr)))
                clos = closure(context, seed)
                if len(clos) >= 1 and len(seed) <= nattr:
                    meta = {"context": context, "mode": mode, "seed": seed, "closure": clos}
                    return Entry(metadata=meta, answer=self._fmt_list(clos))
            elif mode == "concepts":
                concepts = compute_concepts(context)
                if not concepts:
                    continue
                meta = {"context": context, "mode": mode, "answer_concepts": concepts}
                return Entry(metadata=meta, answer=self._fmt_concepts(concepts))
            else:
                lhs = sorted(random.sample(range(nattr), random.randint(1, nattr)))
                rhs = sorted(random.sample(range(nattr), random.randint(1, nattr)))
                holds = implication_holds(context, lhs, rhs)
                meta = {"context": context, "mode": mode, "lhs": lhs, "rhs": rhs, "holds": holds}
                return Entry(metadata=meta, answer="yes" if holds else "no")

    def _fmt_list(self, lst):
        return "[" + ", ".join(str(x) for x in lst) + "]"

    def _fmt_concepts(self, concepts):
        parts = ", ".join("(" + self._fmt_list(list(e)) + ", " + self._fmt_list(list(i)) + ")" for e, i in concepts)
        return "[" + parts + "]"

    def _render_context(self, context):
        return "\n".join("object %d has attributes %s" % (oi, self._fmt_list(attrs))
                         for oi, attrs in enumerate(context))

    def render_prompt(self, metadata):
        ctx = self._render_context(metadata["context"])
        mode = metadata["mode"]
        if mode == "closure":
            seed = self._fmt_list(metadata["seed"])
            return (
                f"Objects and attributes form an incidence context:\n{ctx}\n"
                f"For an attribute set X, its closure X'' is the set of attributes that every object "
                f"carrying all of X also carries. Compute the closure of {seed}. "
                f"Answer with one sorted list of attribute ids, e.g. [0, 2]."
            )
        if mode == "concepts":
            return (
                f"Objects and attributes form an incidence context:\n{ctx}\n"
                f"A concept (maximal rectangle) is a pair (E, I) where E is a maximal set of objects, "
                f"I is the attribute set they all share, and E = {{o: I ⊆ obj(o)}} with I closed. "
                f"List ALL concepts as [([objs], [attrs]), ...]: each extent and intent sorted ascending, "
                f"the list sorted lexicographically by then by extent then intent."
            )
        lhs = self._fmt_list(metadata["lhs"])
        rhs = self._fmt_list(metadata["rhs"])
        return (
            f"Objects and attributes form an incidence context:\n{ctx}\n"
            f"An implication X -> Y holds iff every object carrying all of X also carries all of Y. "
            f"Does {lhs} -> {rhs} hold here? Answer exactly 'yes' or 'no'."
        )

    def score_answer(self, answer, entry):
        mode = entry.metadata["mode"]
        if mode == "closure":
            got = _parse_int_list(answer)
            return 1.0 if got is not None and got == entry.metadata["closure"] else 0.0
        if mode == "concepts":
            got = _parse_concepts(answer)
            gold = sorted(tuple(tuple(x) for x in pair) for pair in entry.metadata["answer_concepts"])
            return 1.0 if got is not None and got == gold else 0.0
        if mode == "implication":
            return 1.0 if str(answer).strip().lower() == entry.answer else 0.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'formal_concept_closure (draw 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_relational_structures_r1/formal_concept_closure',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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
