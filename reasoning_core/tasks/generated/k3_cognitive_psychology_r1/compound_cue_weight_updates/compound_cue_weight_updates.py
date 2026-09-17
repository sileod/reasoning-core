import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'compound_cue_weight_updates (variant 2 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_cognitive_psychology_r1/compound_cue_weight_updates',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
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


@dataclass
class CompoundCueWeightUpdatesConfig(Config):
    n_phases: int = 5
    max_repeats: int = 2
    n_cues: int = 2
    max_attempts: int = 200

    def apply_difficulty(self, level):
        self.n_phases = 5 + int(2 * level)
        self.max_repeats = 2 + int(level / 2)
        self.n_cues = 2 + min(2, int(level / 2))


def _run_rescorla_wagner(phases, rates):
    weights = {cue: Fraction(0) for cue in rates}
    for cues, outcome, repeats in phases:
        for _ in range(repeats):
            error = outcome - sum(weights[cue] for cue in cues)
            for cue in cues:
                weights[cue] += Fraction(rates[cue], 12) * error
    return weights


def _verify_weights(phases, rates):
    labels = sorted(rates)
    numerators = [0] * len(labels)
    denominator = 1
    for cues, outcome, repeats in phases:
        indices = [labels.index(cue) for cue in cues]
        for _ in range(repeats):
            error_numerator = outcome * denominator - sum(numerators[i] for i in indices)
            numerators = [
                12 * value + (rates[labels[i]] * error_numerator if i in indices else 0)
                for i, value in enumerate(numerators)
            ]
            denominator *= 12
    return {cue: Fraction(value, denominator) for cue, value in zip(labels, numerators)}


def _random_schedule(config):
    labels = "ABCD"[:config.n_cues]
    first, second = random.sample(labels, 2)
    pair = "".join(sorted(first + second))
    mode = random.choice(("acquisition", "blocking", "inhibition", "extinction"))
    motifs = {
        "acquisition": [(first, 1), (pair, 1)],
        "blocking": [(first, 1), (first, 1), (pair, 1)],
        "inhibition": [(first, 1), (pair, 0), (first, 1)],
        "extinction": [(pair, 1), (first, 0)],
    }
    motif = motifs[mode]
    extra = []
    for _ in range(config.n_phases - len(motif)):
        size = random.randint(1, min(3, config.n_cues))
        cues = "".join(sorted(random.sample(labels, size)))
        extra.append((cues, random.randint(0, 1)))
    insertion = random.randrange(len(extra) + 1)
    schedule = extra[:insertion] + motif + extra[insertion:]
    phases = [[cues, outcome, random.randint(1, config.max_repeats)]
              for cues, outcome in schedule]
    return mode, phases


class CompoundCueWeightUpdates(Task):
    summary = "Run trial-wise error-correction learning over single and compound cue schedules spanning acquisition, blocking, inhibition, and extinction, and choose which of two probe cues has the stronger signed response."
    design_choice = "Present a probe trial with two cues and ask which cue (A or B) the model predicts will elicit the stronger response, answer as a single letter."
    task_name = "compound_cue_weight_updates"
    task_version = 2
    config_cls = CompoundCueWeightUpdatesConfig

    def generate_entry(self):
        desired = random.choice("AB")
        for _ in range(self.config.max_attempts):
            mode, phases = _random_schedule(self.config)
            rates = {cue: random.choice((2, 3, 4)) for cue in "ABCD"[:self.config.n_cues]}
            weights = _run_rescorla_wagner(phases, rates)
            if abs(weights["A"] - weights["B"]) < Fraction(1, 1000):
                continue
            winner = "A" if weights["A"] > weights["B"] else "B"
            if winner != desired:
                rename = {"A": "B", "B": "A", "C": "C", "D": "D"}
                phases = [["".join(sorted(rename[c] for c in cues)), outcome, repeats]
                          for cues, outcome, repeats in phases]
                rates = {cue: rates[rename[cue]] for cue in sorted(rates)}
                weights = {cue: weights[rename[cue]] for cue in sorted(weights)}
            verified = _verify_weights(phases, rates)
            assert weights == verified
            other = "B" if desired == "A" else "A"
            assert verified[desired] > verified[other]
            assert all(value.denominator > 0 for value in verified.values())
            return Entry(metadata={
                "mode": mode,
                "phases": phases,
                "rates": rates,
                "weights_final": {cue: str(value) for cue, value in verified.items()},
            }, answer=desired)
        raise RuntimeError("Could not generate a non-tied probe after bounded attempts")

    def render_prompt(self, metadata):
        rates = ", ".join(f"{cue}={Fraction(rate, 12)}" for cue, rate in sorted(metadata["rates"].items()))
        schedule = "; ".join(
            f"{cues}{'+' if outcome else '-'} x{repeats}"
            for cues, outcome, repeats in metadata["phases"]
        )
        return (
            "A conditioning model uses the Rescorla-Wagner error-correction rule. "
            "All cue weights start at 0. On each training trial, prediction is the sum of "
            "the weights of the shown cues. Compute error = outcome - prediction once, "
            "then simultaneously add rate(cue) * error to each shown cue's weight. "
            "Absent cues do not change. Weights remain signed, without clipping or rounding.\n"
            f"Cue learning rates: {rates}.\n"
            "Read the schedule left to right: + means outcome 1, - means outcome 0; "
            "letters together mean simultaneous cues. For example, AB- x2 means two "
            "successive trials with A and B together and outcome 0, recomputing error each time.\n"
            f"Schedule: {schedule}.\n"
            "The next trial is an unreinforced probe showing A and B together, with no other cues. "
            "Before any probe update, which cue predicts the stronger response? Compare their "
            "learned signed weights, not absolute magnitudes: the larger weight wins. "
            "There is no tie. Answer with a single letter, A or B (for example: A)."
        )

    def score_answer(self, answer, entry):
        return float(isinstance(answer, str) and answer.strip() == entry.answer)

    def distractor_candidates(self, entry):
        yield "B" if entry.answer == "A" else "A"
