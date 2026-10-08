"""Exact posterior probability of a hidden binary state from independent noisy sensors.

The decision is whether the incident is real; `soft` is the exact posterior, the calibration target. Posteriors
within 0.1 of 1/2 are redrawn, so the plain answer (the more probable side) is well defined, and the side is drawn
first, so a constant answer scores one half. Ported from
tasksource.jev.procedural.partial_observation_calibration; its level tables stop at 4.
"""
import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.decision import Decision
from reasoning_core.template import Config, Entry, Task

RATES = [
    (Fraction(4, 5), Fraction(1, 5)),
    (Fraction(3, 4), Fraction(1, 4)),
    (Fraction(2, 3), Fraction(1, 3)),
    (Fraction(9, 10), Fraction(2, 5)),
]
N_SENSORS = [1, 2, 3, 4, 6]
PRIORS = [Fraction(1, 5), Fraction(1, 3), Fraction(1, 2), Fraction(2, 3), Fraction(4, 5)]


def _text(x):
    return f"{x.numerator}/{x.denominator}"


@dataclass
class PartialObservationCalibrationConfig(Config):
    def apply_difficulty(self, level):
        pass  # the generator reads the level


class PartialObservationCalibration(Task):
    summary = "Decide whether a hidden incident is real from noisy sensors; the decision carries the exact posterior."
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or PartialObservationCalibrationConfig())

    def generate_entry(self, state_seed=None, question=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, level = random.Random(state_seed), min(self.config.level, 4)
        real = rng.random() < 0.5
        while True:
            prior = rng.choice(PRIORS)
            yes, no = prior, 1 - prior
            sensors = []
            for i in range(N_SENSORS[level]):
                tpr, fpr = rng.choice(RATES)
                positive = rng.choice([True, False])
                sensors.append({
                    "id": f"S{i+1}",
                    "observed": "positive" if positive else "negative",
                    "p_positive_given_incident": _text(tpr),
                    "p_positive_given_no_incident": _text(fpr),
                })
                yes *= tpr if positive else 1 - tpr
                no *= fpr if positive else 1 - fpr
            posterior = yes / (yes + no)
            if abs(posterior - Fraction(1, 2)) >= Fraction(1, 10) and (posterior > Fraction(1, 2)) == real:
                break
        state = {
            "prior_probability_incident": _text(prior),
            "assumption": "Sensor observations are conditionally independent given whether the incident is real.",
            "sensors": sensors,
        }
        questions = {"incident_real": Decision(
            posterior > Fraction(1, 2), type="noul", soft=round(float(posterior), 6),
            instructions="After conditioning on every sensor observation, is the incident more likely real than not?")}
        qid = question or random.choice(sorted(questions))
        return Entry({"payload": state, "state_seed": state_seed, "question_id": qid}, questions[qid])
