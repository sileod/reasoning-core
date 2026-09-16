import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _normalise(value):
    return str(value).strip().lower()


@dataclass
class QuantifierConfig(Config):
    universe_size: int = 5

    def apply_difficulty(self, level):
        self.universe_size = min(12, 4 + level)


class GeneralizedQuantifierTruth(Task):
    summary = "Evaluate sentences whose determiners relate sets (most, more than half, exactly n, all but one, few) against small models, covering stacked, negated, and compared determiners; answers are truth values or which listed sentences hold."
    task_version = 2
    config_cls = QuantifierConfig

    def generate_entry(self):
        universe_size = self.config.universe_size
        universe = list(range(1, universe_size + 1))

        A = set(random.sample(universe, random.randint(1, universe_size)))
        B = set(random.sample(universe, random.randint(1, universe_size)))

        model = {"universe": universe, "A": sorted(A), "B": sorted(B)}

        quantifier = random.choice(
            ["most", "more_than_half", "exactly_n", "all_but_one", "few"]
        )
        n = None

        if quantifier == "exactly_n":
            n = random.randint(0, len(A))
            sentence = f"Exactly {n} elements of A are in B."
            target = (len(A & B) == n)
        elif quantifier == "all_but_one":
            sentence = "All but one element of A is in B."
            target = (len(A - B) == 1)
        elif quantifier == "most":
            sentence = "Most elements of A are in B."
            target = (len(A & B) > len(A) / 2 and len(A) >= 2)
        elif quantifier == "more_than_half":
            sentence = "More than half of the elements of A are in B."
            target = (len(A & B) > len(A) / 2)
        else:
            sentence = "Few elements of A are in B."
            target = (len(A & B) < len(A) / 3)

        answer = "True" if target else "False"

        return Entry(
            metadata={
                "model": model,
                "quantifier": quantifier,
                "sentence": sentence,
                "n": n,
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        model = metadata["model"]
        return (
            f"Indicate whether the statement below is true or false; reply "
            f"with exactly True or False. Consider a model with universe "
            f"U = {model['universe']}, set A = {model['A']}, and set B = "
            f"{model['B']}. Statement: {metadata['sentence']}"
        )

    def score_answer(self, answer, entry):
        return 1.0 if _normalise(answer) == _normalise(entry.answer) else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'generalized_quantifier_truth (draw 3 of 3, unguided baseline)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_formal_semantics_r1/generalized_quantifier_truth',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1339177894,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
