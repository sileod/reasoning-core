import json
import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround
from reasoning_core.tasks.generated.jev._common import canonical_json, jev_prompt, json_score


RATES = [
    (Fraction(4, 5), Fraction(1, 5)),
    (Fraction(3, 4), Fraction(1, 4)),
    (Fraction(2, 3), Fraction(1, 3)),
    (Fraction(9, 10), Fraction(2, 5)),
]
PRIORS = [Fraction(1, 5), Fraction(1, 3), Fraction(1, 2), Fraction(2, 3), Fraction(4, 5)]


def _fraction_text(x):
    return f"{x.numerator}/{x.denominator}"


@dataclass
class JevPartialObservationCalibrationConfig(Config):
    n_sensors: int = 2

    def apply_difficulty(self, level):
        self.n_sensors = sround(self.n_sensors + 0.55 * level)


class JevPartialObservationCalibration(Task):
    summary = "Return an exactly computed Jev noul probability for a hidden binary state from independent noisy observations with stated priors and sensor likelihoods."
    config_cls = JevPartialObservationCalibrationConfig

    def generate_entry(self):
        prior = random.choice(PRIORS)
        yes = prior
        no = 1 - prior
        sensors = []
        for i in range(max(1, self.config.n_sensors)):
            tpr, fpr = random.choice(RATES)
            positive = random.choice([True, False])
            sensors.append({
                "id": f"S{i+1}",
                "observed": "positive" if positive else "negative",
                "p_positive_given_incident": _fraction_text(tpr),
                "p_positive_given_no_incident": _fraction_text(fpr),
            })
            yes *= tpr if positive else 1 - tpr
            no *= fpr if positive else 1 - fpr
        posterior = yes / (yes + no)
        state = {
            "prior_probability_incident": _fraction_text(prior),
            "assumption": "Sensor observations are conditionally independent given whether the incident is real.",
            "sensors": sensors,
        }
        questions = {
            "incident_real": {
                "type": "noul",
                "instructions": "What is the posterior probability that the incident is real after conditioning on every sensor observation?",
            }
        }
        answers = {"incident_real": {"type": "noul", "noul": round(float(posterior), 6)}}
        return Entry(metadata=edict(state=state, questions=questions, posterior=_fraction_text(posterior)), answer=canonical_json(answers))

    def render_prompt(self, m):
        return jev_prompt(m.state, m.questions)

    def score_answer(self, answer, entry):
        return json_score(answer, entry)

    def balancing_key(self, problem):
        p = float(json.loads(problem.answer)["incident_real"]["noul"])
        return int(p * 4)
