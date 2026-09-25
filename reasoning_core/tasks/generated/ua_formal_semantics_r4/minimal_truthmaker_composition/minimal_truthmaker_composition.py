"""Minimal truthmaker composition: compute minimal supporting situations for
clauses built from positive/negative facts, conjunction, disjunction, and
finite quantification; distinguish support from mere compatibility; return the
unique minimal fact set, or the canonical 'NO' token when none exists.

Semantics (truthmaker support). A *situation* is a set of positive ground facts
(e.g. P(a)) that obtain. A situation S supports a clause as follows:
  - supports the atomic fact P(x)   iff  the fact P(x) is in S;
  - supports not P(x)               iff  P(x) is not in S;
  - supports (A and B)              iff  it supports both A and B;
  - supports (A or B)               iff  it supports at least one of A, B;
  - supports (for every x in D: F)  iff  it supports F(x) for each x in D;
  - supports (for some x in D: F)   iff  it supports F(x) for some x in D.

The minimal supporting situation is the smallest (by inclusion) situation that
supports the clause. We report the *unique* minimal situation; if there are none
or more than one, the answer is 'NO' -- which is what distinguishes support from
mere compatibility (a situation that is merely compatible / non-conflicting is
not automatically a supporter).
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'minimal_truthmaker_composition (variant 2 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_semantics_r4/minimal_truthmaker_composition',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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

_INDIVIDUALS = ['a', 'b', 'c', 'd']
_PREDICATES = ['P', 'Q', 'R']


def _render_fact(f):
    return f"{f[0]}({f[1]})"


def _supports(node, S):
    k = node['k']
    if k == 'pos':
        return node['f'] in S
    if k == 'neg':
        return node['f'] not in S
    if k in ('and', 'all'):
        for c in node['c']:
            if not _supports(c, S):
                return False
        return True
    if k in ('or', 'ex'):
        for c in node['c']:
            if _supports(c, S):
                return True
        return False
    raise ValueError(k)


def _all_positive_facts(node):
    facts = set()
    stack = [node]
    while stack:
        n = stack.pop()
        k = n['k']
        if k == 'pos':
            facts.add(n['f'])
        elif k in ('and', 'or', 'all', 'ex'):
            stack.extend(n['c'])
    return facts


def _minimal_supports(node):
    facts = sorted(_all_positive_facts(node))
    m = len(facts)
    supporting = []
    for mask in range(1 << m):
        S = set(facts[i] for i in range(m) if (mask >> i) & 1)
        if _supports(node, S):
            supporting.append(S)
    mins = []
    for S in supporting:
        if not any(S2 < S for S2 in supporting):
            mins.append(frozenset(S))
    return set(mins)


def _canonical(mins):
    if len(mins) != 1:
        return 'NO'
    facts = sorted(mins.pop(), key=_render_fact)
    if not facts:
        return 'EMPTY'
    return ' '.join(_render_fact(f) for f in facts)


def compute_truthmaker_answer(node):
    mins = _minimal_supports(node)
    n = len(mins)
    # Domain check: a count of minimal situations is a non-negative integer.
    assert isinstance(n, int) and n >= 0
    return _canonical(mins), n


def _formula_text(node):
    k = node['k']
    if k in ('pos', 'neg'):
        if k == 'pos':
            return _render_fact(node['f'])
        return "not " + _render_fact(node['f'])
    if k in ('and', 'or'):
        join = ' and ' if k == 'and' else ' or '
        return "(" + join.join(_formula_text(c) for c in node['c']) + ")"
    if k in ('all', 'ex'):
        quant = 'every x in' if k == 'all' else 'some x in'
        dom = ", ".join(node['dom'])
        pred = node['pred']
        sign = node['sign']
        atom = _render_fact((pred, 'x'))
        if sign == 'neg':
            atom = "not " + atom
        return f"(for {quant} {{{dom}}}: {atom})"
    raise ValueError(k)


def _atom(preds, inds):
    pred = random.choice(preds)
    obj = random.choice(inds)
    kind = random.choice(['pos', 'neg'])
    return {'k': kind, 'f': (pred, obj)}


def _build_formula(preds, inds, atoms):
    def rec(budget, allow_quant):
        if budget <= 1:
            return _atom(preds, inds)
        r = random.random()
        if allow_quant and len(inds) >= 2 and r < 0.28:
            sub = sorted(random.sample(inds, random.randint(2, len(inds))))
            qk = random.choice(['all', 'ex'])
            pred = random.choice(preds)
            sign = random.choice(['pos', 'neg'])
            body = {'k': sign, 'f': (pred, sub[0])}
            children = [{'k': sign, 'f': (pred, i)} for i in sub]
            return {'k': qk, 'dom': sub, 'pred': pred, 'sign': sign, 'c': children}
        op = random.choice(['and', 'or'])
        left = 1 + random.randint(0, budget - 1)
        right = max(1, budget - left)
        return {'k': op, 'c': [rec(left, False), rec(right, False)]}

    return rec(atoms, True)


@dataclass
class MinimalTruthmakerConfig(Config):
    n_inds: int = 2
    n_preds: int = 1
    atoms: int = 2

    def apply_difficulty(self, level):
        self.n_inds = 2 + min(level, 2)
        self.n_preds = 1 + (1 if level >= 0 else 0) + (1 if level >= 4 else 0)
        self.atoms = 3 + level


class MinimalTruthmakerComposition(Task):
    summary = ("Compute minimal supporting situations (sets of positive ground "
               "facts) for clauses over positive/negative atoms, conjunction, "
               "disjunction, and finite universal/existential quantification "
               "over named individuals; return the unique minimal set as a "
               "canonical sorted fact string, or NO when none or several exist.")
    config_cls = MinimalTruthmakerConfig
    design_choice = ("Generate instances from a fixed vocabulary of named individuals "
                     "and predicates, with the answer being the unique minimal set or "
                     "a canonical 'NO' token when none exists.")

    def generate_entry(self):
        cfg = self.config
        inds = _INDIVIDUALS[:cfg.n_inds]
        preds = _PREDICATES[:cfg.n_preds]
        want = 'unique' if random.random() < 0.68 else 'no'
        node = None
        for _ in range(60):
            cand = _build_formula(preds, inds, cfg.atoms)
            mins = _minimal_supports(cand)
            label = 'unique' if len(mins) == 1 else 'no'
            if label == want:
                node = cand
                break
        if node is None:
            node = cand
        answer, n = compute_truthmaker_answer(node)
        formula = _formula_text(node)
        metadata = {
            'formula': formula,
            'individuals': inds,
            'predicates': preds,
            'n_supports': n,
            'answer': answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        indiv = ", ".join(metadata['individuals'])
        return (
            "Truthmaker semantics. The named individuals are {"
            + indiv
            + "}. A fact is an atomic claim like P(a) (positive) or not P(a) "
            "(negative). A situation is a set of facts that obtain. A situation S "
            "supports a clause as follows: S supports P(x) iff the fact P(x) is in "
            "S; S supports not P(x) iff the fact P(x) is not in S; S supports (A "
            "and B) iff it supports both; S supports (A or B) iff it supports at "
            "least one; S supports (for every x in D: F) iff it supports F(x) for "
            "each x in D; S supports (for some x in D: F) iff it supports F(x) for "
            "some x in D.\n\n"
            "Consider the clause: " + metadata['formula'] + "\n\n"
            "Give the unique minimal supporting situation (the smallest set of "
            "facts by inclusion that supports the clause). If none exists or more "
            "than one minimal situation exists, answer exactly NO. Otherwise list "
            "the facts of the unique situation separated by spaces and sorted "
            "lexicographically, e.g. 'P(a) Q(b)', or exactly EMPTY if no facts are "
            "needed."
        )

    def distractor_candidates(self, entry):
        answer = entry['answer']
        yield 'EMPTY'
        yield 'NO'
        yield 'Q(a) P(b)'


def _norm(a):
    return ' '.join((a or '').strip().upper().split())


def score_answer(answer, entry):
    return 1.0 if _norm(answer) == _norm(entry['answer']) else 0.0
