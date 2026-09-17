import random
from dataclasses import dataclass
from functools import lru_cache
from itertools import product

import numpy as np
import z3

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'temporal_connective_equivalence (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_algorithms_and_data_structures_r1/temporal_connective_equivalence',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 368817805,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

PUNCTUAL = ("the alarm", "the flash", "the bell", "the click", "the signal")
DURATIVE = ("the inspection", "the broadcast", "the rehearsal", "the rainfall", "the repair")
RELATIONS = ("before", "after", "until", "since", "while", "no-sooner")


@dataclass
class TemporalConnectiveEquivalenceV3Config(Config):
    n_events: int = 2
    clauses: int = 1
    negation_probability: float = 0.25

    def apply_difficulty(self, level):
        self.n_events = min(4, 2 + int(level / 3))
        self.clauses = min(5, 1 + int(level / 1.5))
        self.negation_probability = min(0.5, 0.25 + level / 30)


def atom(relation, a, b):
    return ["rel", relation, a, b]


@lru_cache(maxsize=32)
def timelines(aspects):
    size = len(aspects) + aspects.count("durative")
    domains = [
        [(s, e) for s in range(size) for e in range(size) if s < e]
        if aspect == "durative" else [(t, t) for t in range(size)]
        for aspect in aspects
    ]
    result = np.asarray(list(product(*domains)), dtype=np.int16)
    result.setflags(write=False)
    return result


def truth_values(expr, worlds):
    op = expr[0]
    if op == "not":
        return ~truth_values(expr[1], worlds)
    if op in ("and", "or"):
        left, right = truth_values(expr[1], worlds), truth_values(expr[2], worlds)
        return left & right if op == "and" else left | right
    _, relation, a, b = expr
    sa, ea = worlds[:, a, 0], worlds[:, a, 1]
    sb, eb = worlds[:, b, 0], worlds[:, b, 1]
    if relation == "before":
        return ea < sb
    if relation == "after":
        return sa > eb
    if relation in ("until", "no-sooner"):
        return ea == sb
    if relation == "since":
        return sa == eb
    if relation == "while":
        return (sa <= eb) & (sb <= ea)
    raise ValueError(relation)


def symbolic(expr, endpoints):
    op = expr[0]
    if op == "not":
        return z3.Not(symbolic(expr[1], endpoints))
    if op in ("and", "or"):
        combine = z3.And if op == "and" else z3.Or
        return combine(symbolic(expr[1], endpoints), symbolic(expr[2], endpoints))
    _, relation, a, b = expr
    sa, ea = endpoints[a]
    sb, eb = endpoints[b]
    if relation == "before":
        return ea < sb
    if relation == "after":
        return sa > eb
    if relation in ("until", "no-sooner"):
        return ea == sb
    if relation == "since":
        return sa == eb
    if relation == "while":
        return z3.And(sa <= eb, sb <= ea)
    raise ValueError(relation)


def solver_equivalent(source, target, aspects):
    endpoints = [(z3.Real(f"s{i}"), z3.Real(f"e{i}")) for i in range(len(aspects))]
    solver = z3.Solver()
    solver.set(timeout=500)
    for (s, e), aspect in zip(endpoints, aspects):
        solver.add(s < e if aspect == "durative" else s == e)
    solver.add(z3.Xor(symbolic(source, endpoints), symbolic(target, endpoints)))
    result = solver.check()
    if result == z3.unknown:
        raise RuntimeError("Temporal equivalence solver did not finish")
    return result == z3.unsat


def sample_expression(count, aspects, negation_probability):
    if count == 1:
        a, b = random.sample(range(len(aspects)), 2)
        choices = list(RELATIONS)
        if aspects[a] == "punctual":
            choices = [r for r in choices if r not in ("until", "since")]
        result = atom(random.choice(choices), a, b)
    else:
        split = random.randint(1, count - 1)
        result = [random.choice(("and", "or")),
                  sample_expression(split, aspects, negation_probability),
                  sample_expression(count - split, aspects, negation_probability)]
    return ["not", result] if random.random() < negation_probability else result


def restructure(expr):
    op = expr[0]
    if op == "not":
        child = expr[1]
        if child[0] == "not":
            return restructure(child[1])
        if child[0] in ("and", "or") and random.random() < 0.7:
            return ["or" if child[0] == "and" else "and",
                    restructure(["not", child[1]]), restructure(["not", child[2]])]
        return ["not", restructure(child)]
    if op in ("and", "or"):
        children = [restructure(expr[1]), restructure(expr[2])]
        random.shuffle(children)
        if random.random() < 0.35:
            return ["not", ["or" if op == "and" else "and",
                            ["not", children[0]], ["not", children[1]]]]
        return [op, *children]
    _, relation, a, b = expr
    if relation == "before":
        return atom("after", b, a)
    if relation == "after":
        return atom("before", b, a)
    if relation in ("until", "no-sooner"):
        return atom("since", b, a)
    if relation == "since":
        return atom(random.choice(("until", "no-sooner")), b, a)
    if random.random() < 0.5:
        return atom("while", b, a)
    return ["and", ["not", atom("before", a, b)], ["not", atom("after", a, b)]]


def mutate(expr):
    op = expr[0]
    if op == "rel":
        _, relation, a, b = expr
        if random.random() < 0.3:
            return ["not", expr]
        return atom(random.choice([r for r in RELATIONS if r != relation]), a, b)
    if op == "not":
        return expr[1] if random.random() < 0.35 else ["not", mutate(expr[1])]
    if random.random() < 0.35:
        return ["or" if op == "and" else "and", expr[1], expr[2]]
    side = random.choice((1, 2))
    return [op, mutate(expr[1]) if side == 1 else expr[1],
            mutate(expr[2]) if side == 2 else expr[2]]


def render_expression(expr, names, variant):
    op = expr[0]
    if op == "not":
        return f"it is not true that ({render_expression(expr[1], names, variant)})"
    if op in ("and", "or"):
        left = render_expression(expr[1], names, variant)
        right = render_expression(expr[2], names, variant)
        return f"both ({left}) and ({right})" if op == "and" else f"at least one holds: ({left}) or ({right})"
    _, relation, i, j = expr
    a, b = names[i], names[j]
    if a in PUNCTUAL and relation in ("until", "since"):
        return (f"{a} ended just as {b} began" if relation == "until"
                else f"{a} began just as {b} ended")
    forms = {
        "before": (f"{a} was before {b}", f"before {b}, {a} had finished"),
        "after": (f"{a} was after {b}", f"after {b}, {a} began"),
        "until": (f"{a} continued until {b} began", f"{a} ended just as {b} began"),
        "since": (f"{a} ran since {b} ended", f"{a} began just as {b} ended"),
        "while": (f"{a} occurred while {b} occurred", f"{a} overlapped {b}"),
        "no-sooner": (f"no sooner had {a} ended than {b} began", f"{b} began the instant {a} ended"),
    }
    return forms[relation][variant]


class TemporalConnectiveEquivalence(Task):
    summary = "Clauses linked by until, since, while, before/after and no-sooner under scoped negation, conjunction or disjunction and durative or punctual aspect are coerced to event orderings and intervals to judge with yes/no whether restructured paraphrases preserve the temporal claim."
    config_cls = TemporalConnectiveEquivalenceV3Config
    task_version = 3

    def generate_entry(self):
        desired = random.choice((True, False))
        n = self.config.n_events
        d = random.randint(1, min(2, n - 1))
        aspects = ["durative"] * d + ["punctual"] * (n - d)
        random.shuffle(aspects)
        durations = iter(random.sample(DURATIVE, d))
        points = iter(random.sample(PUNCTUAL, n - d))
        names = [next(durations) if a == "durative" else next(points) for a in aspects]
        worlds = timelines(tuple(aspects))
        for _ in range(150):
            source = sample_expression(self.config.clauses, aspects, self.config.negation_probability)
            target = restructure(source)
            if not desired:
                target = mutate(target)
            source_truth = truth_values(source, worlds)
            target_truth = truth_values(target, worlds)
            if not source_truth.any() or source_truth.all() or not target_truth.any() or target_truth.all():
                continue
            equivalent = bool(np.array_equal(source_truth, target_truth))
            if equivalent != desired:
                continue
            assert solver_equivalent(source, target, aspects) == equivalent
            variant = random.randrange(2)
            source_text = render_expression(source, names, variant)
            target_text = render_expression(target, names, 1 - variant)
            if source_text == target_text:
                continue
            return Entry(metadata={"names": names, "aspects": aspects,
                                   "source": source, "target": target,
                                   "source_text": source_text, "target_text": target_text},
                         answer="yes" if equivalent else "no")
        raise RuntimeError("Could not sample a nontrivial temporal equivalence pair")

    def render_prompt(self, metadata):
        aspects = "; ".join(f"{name}: {aspect}" for name, aspect in zip(metadata["names"], metadata["aspects"]))
        return (
            "An editor is restructuring a timing report. Do the original and rewrite permit exactly the same timelines?\n"
            "Each named event occurs once on a real-valued timeline. A punctual event has start=end; "
            "a durative event has start<end and occupies its entire closed interval. "
            f"Events: {aspects}.\n"
            "Use these precise editorial conventions (also for punctual events): before means end(A)<start(B); "
            "after reverses before. Until means end(A)=start(B); since means start(A)=end(B), "
            "with no requirement about the present. No sooner A than B means end(A)=start(B), "
            "not a positive delay. While/overlap means the closed intervals intersect, even at one endpoint. "
            "The phrases 'just as' and 'the instant' mean equality. Negation denies only its parenthesized "
            "claim, never event existence. 'Both' is conjunction; 'at least one' is inclusive disjunction. "
            "No other temporal facts or implications from narrative order are assumed. "
            "Compare all endpoint orderings, allowing ties, rather than just one plausible timeline.\n"
            f"Original: {metadata['source_text']}.\n"
            f"Rewrite: {metadata['target_text']}.\n"
            "Reply yes if equivalent and no otherwise. Format example: yes. Give only the label."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return float(answer.strip().lower() == entry.answer)
