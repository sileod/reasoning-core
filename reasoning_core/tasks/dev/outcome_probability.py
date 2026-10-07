"""Numeric mutation of most_probable_outcome: the same urn draws (with or without replacement) and the
same pair of statements, but instead of naming the likelier statement, give the exact probability of
one of them as a reduced fraction. Answers stay short and exact (no long decimals).
"""
import random
import re
from fractions import Fraction

from reasoning_core.template import DevTask, Entry
from reasoning_core.tasks.probabilistic_reasoning import (
    MostProbableOutcomeConfig, generate, outcome_grammar, problog, eng, qprobs)


class OutcomeProbability(DevTask):
    summary = ("Give the exact probability, as a reduced fraction, of a statement about two draws from an urn "
               "of two colours with or without replacement (both one colour, at least one, same or different "
               "colours, first draw), the numeric twin of most_probable_outcome.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or MostProbableOutcomeConfig())

    def generate_entry(self):
        while True:
            node = generate(outcome_grammar(self.config.max_count, target=random.choice(["A", "B", "equal"])),
                            depth=self.config.depth)
            src, english = node @ problog, node @ eng
            pick = random.choice("ab")
            p = qprobs(src)[pick]
            q = Fraction(p).limit_denominator(10 ** 5)
            if abs(float(q) - p) < 1e-12 and 0 < q < 1:
                return Entry({"english": english, "statement": pick.upper()}, f"{q.numerator}/{q.denominator}")

    def render_prompt(self, m):
        head = m["english"].split("Which statement is more likely?")[0].rstrip()
        stmt = re.search(rf"^{m['statement']}: (.*?)\.?$", m["english"], re.M).group(1)
        return f"{head}\nWhat is the probability that {stmt}? Answer with a reduced fraction such as 3/8."

    def score_answer(self, answer, entry):
        try:
            got = Fraction(str(answer).strip().rstrip("."))
        except (ValueError, ZeroDivisionError):
            return 0.0
        return float(got == Fraction(entry.answer))
