import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class PermPatternConfig(Config):
    pattern_half_min: int = 3
    pattern_half_max: int = 4

    def apply_difficulty(self, level):
        self.pattern_half_min = 3 + level
        self.pattern_half_max = 4 + level


def contains_with_witness(text, pattern):
    n = len(text)
    k = len(pattern)
    idx = []
    ti = 0
    for pi in range(k):
        while ti < n and text[ti] != pattern[pi]:
            ti += 1
        if ti >= n:
            return None
        idx.append(ti)
        ti += 1
    return idx


class PermutationPatternWitness(Task):
    summary = "Given two permutations, decide whether the first contains the second as a pattern and return the lexicographically smallest set of indices realizing it, or NONE."
    design_choice = "Generate instances where the pattern length is exactly half the text length, forcing a search over many candidate windows."
    config_cls = PermPatternConfig
    task_version = 2

    def generate_entry(self):
        while True:
            half = random.randint(self.config.pattern_half_min, self.config.pattern_half_max)
            n = 2 * half
            values = list(range(1, n + 1))
            random.shuffle(values)
            text = values
            label = random.random() < 0.75
            if label:
                chosen = sorted(random.sample(range(n), half))
                pattern = [text[c] for c in chosen]
            else:
                while True:
                    entries = values[:]
                    random.shuffle(entries)
                    pattern = entries[:half]
                    if contains_with_witness(text, pattern) is None:
                        break

            witness = contains_with_witness(text, pattern)
            if label:
                assert witness is not None
            else:
                assert witness is None

            ans = "NONE" if witness is None else " ".join(str(x + 1) for x in witness)
            return Entry(metadata={
                "text": text,
                "pattern": pattern,
                "contains": label,
                "witness_0index": witness,
            }, answer=ans)

    def render_prompt(self, metadata):
        text = " ".join(str(x) for x in metadata["text"])
        pattern = " ".join(str(x) for x in metadata["pattern"])
        return (
            f"Given a text permutation T and a pattern permutation P, T contains P if there is "
            f"a strictly increasing sequence of indices i1<i2<...<ik with "
            f"T[i1],T[i2],...,T[ik] = P as a sequence of values. "
            f"Decide whether T contains P, where T = [{text}] and P = [{pattern}]. "
            f"Report the lexicographically smallest 1-based index tuple that realizes it, "
            f"or the single word NONE when no such indices exist"
        )

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        answer = answer.strip()
        if entry.metadata["contains"]:
            text = entry.metadata["text"]
            pattern = entry.metadata["pattern"]
            expected = " ".join(str(x + 1) for x in contains_with_witness(text, pattern))
            return 1.0 if answer == expected else 0.0
        return 1.0 if answer == "NONE" else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'permutation_pattern_witness (draw 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_systematic_generalization_r1/permutation_pattern_witness',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1336314872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
