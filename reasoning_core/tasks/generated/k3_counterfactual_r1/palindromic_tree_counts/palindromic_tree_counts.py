import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


def _count_occurrences(text, sub):
    count = 0
    start = 0
    while True:
        idx = text.find(sub, start)
        if idx == -1:
            break
        count += 1
        start = idx + 1
    return count


@dataclass
class PalindromicTreeCountsV2Config(Config):
    alphabet: int = 2
    min_len: int = 8
    max_len: int = 12

    def apply_difficulty(self, level):
        self.alphabet = 2 + (level >= 3) + (level >= 5)
        self.min_len = stochastic_rounding(self.min_len + level * 2)
        self.max_len = stochastic_rounding(self.max_len + level * 2)


class PalindromicTreeCounts(Task):
    summary = "Grow a string's palindromic tree symbol by symbol via longest-suffix links, returning the occurrence count of a queried palindrome among all distinct palindromic substrings."
    design_choice = "Return the occurrence count of a specific queried palindrome (given as a string) after full construction, using exact-match lookup."
    config_cls = PalindromicTreeCountsV2Config

    def generate_entry(self):
        alphabet = self.config.alphabet
        letters = "abcde"[:alphabet]
        while True:
            length = random.randint(self.config.min_len, self.config.max_len)
            text = "".join(random.choice(letters) for _ in range(length))
            distinct = {
                text[i:j]
                for i in range(len(text))
                for j in range(i + 1, len(text) + 1)
                if text[i:j] == text[i:j][::-1]
            }
            if len(distinct) < 2:
                continue
            cands = sorted(distinct, key=lambda p: (_count_occurrences(text, p), p))
            counts = [_count_occurrences(text, p) for p in cands]
            if len(set(counts)) < 2:
                continue
            total = sum(counts)
            r = random.uniform(0, total)
            acc = 0
            pal = cands[0]
            for p, c in zip(cands, counts):
                acc += c
                if r < acc:
                    pal = p
                    break
            count = _count_occurrences(text, pal)
            if count >= 1:
                break
        return Entry(
            metadata={
                "text": text,
                "query": pal,
                "count": count,
            },
            answer=str(count),
        )

    def render_prompt(self, metadata):
        return (
            f"Build the palindromic tree of the string '{metadata['text']}' symbol by symbol "
            f"using longest-suffix links. How many times does the palindrome "
            f"'{metadata['query']}' occur as a substring of '{metadata['text']}'? "
            f"Answer with a single non-negative integer."
        )

    def score_answer(self, answer, entry):
        try:
            return 1.0 if int(answer) == int(entry.answer) else 0.0
        except (TypeError, ValueError):
            return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'palindromic_tree_counts (draw 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_counterfactual_r1/palindromic_tree_counts',
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
