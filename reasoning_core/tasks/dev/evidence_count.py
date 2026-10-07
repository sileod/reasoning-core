"""Numeric mutation of most_probable_evidence: the same independent factors with prior probabilities and the
same observation formula, but asked for a number. Either count the complete true/false assignments of the
factors under which the observation holds (an integer), or give the probability that the observation holds as
a reduced fraction, the latter only when its denominator stays small (no long decimals).
"""
import random
import re
from fractions import Fraction
from itertools import product

from reasoning_core.template import DevTask, Entry
from reasoning_core.tasks.probabilistic_reasoning import (
    MostProbableEvidenceConfig, boolean_value, draw_evidence, evidence_formula, evidence_grammar, generate,
    hidden_atoms)


def _worlds(src):
    probs = {a: Fraction(p) for p, a in re.findall(r"(?m)^\s*([0-9.]+)::\s*([a-z][a-z0-9_]*)\s*\.", src)}
    formula = re.search(r"(?m)^observed :- (.+)\.$", src).group(1)
    atoms = hidden_atoms(src)
    count, prob = 0, Fraction(0)
    for bits in product([False, True], repeat=len(atoms)):
        world = dict(zip(atoms, bits))
        if boolean_value(formula, world):
            count += 1
            w = Fraction(1)
            for a, b in world.items():
                w *= probs[a] if b else 1 - probs[a]
            prob += w
    return len(atoms), count, prob


class EvidenceCount(DevTask):
    summary = ("Given independent factors with prior probabilities and a Boolean observation over them, count the "
               "complete assignments under which the observation holds (integer), or give its exact probability as "
               "a reduced fraction with a small denominator; the numeric twin of most_probable_evidence.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or MostProbableEvidenceConfig())

    def generate_entry(self):
        for _ in range(self.config.max_attempts):
            checked = evidence_formula(generate(evidence_grammar(), depth=self.config.depth, min_depth=4),
                                       self.config)
            if checked is None:
                continue
            src, english, _ = draw_evidence(*checked, self.config)
            n, count, prob = _worlds(src)
            if not 0 < count < 2 ** n:
                continue
            head = english.split("\nWe observe it.")[0]
            if random.random() < 0.5 and prob.denominator <= 1000:
                return Entry({"context": head, "ask": "probability", "n_atoms": n}, f"{prob.numerator}/{prob.denominator}")
            return Entry({"context": head, "ask": "count", "n_atoms": n}, str(count))
        raise RuntimeError("evidence_count: no observation")

    def render_prompt(self, m):
        if m["ask"] == "count":
            return (f"{m['context']}\nOf the {2 ** m['n_atoms']} complete true/false assignments of the factors, "
                    "how many make the observation hold? Answer with an integer.")
        return (f"{m['context']}\nWhat is the probability that the observation holds? "
                "Answer with a reduced fraction such as 3/8.")

    def score_answer(self, answer, entry):
        try:
            return float(Fraction(str(answer).strip().rstrip(".")) == Fraction(entry.answer))
        except (ValueError, ZeroDivisionError):
            return 0.0
