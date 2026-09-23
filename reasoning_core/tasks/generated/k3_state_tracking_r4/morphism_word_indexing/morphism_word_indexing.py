import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

ALPHABET = "abcdefghijklmnopqrstuvwxyz"


@dataclass
class MorphismWordConfig(Config):
    max_len: int = 64
    max_L: int = 2
    max_alphabet: int = 2
    min_len: int = 4

    def apply_difficulty(self, level):
        self.max_alphabet = min(4, 2 + level // 3)
        self.max_L = 2 if level < 4 else 3
        self.max_len = min(6000, 8 * (3 ** level) + 4)
        self.min_len = max(4, 8 * (3 ** max(0, level - 3)))


def _kth_symbol(letters, morph, seed, n, k):
    """Materialize f^n(seed) and return the symbol at position k.

    The uniform morphism sends every letter to a block of equal length L, so
    f^n(seed) has length L^n for an n-iteration depth and each level of the
    descent reuses the same block boundary arithmetic. We still build the
    whole word so the answer is checked against the actual iterated image.
    """
    word = seed
    for _ in range(n):
        word = "".join(morph[c] for c in word)
    return word[k]


class MorphismWordIndexing(Task):
    summary = "Descend positionally through a uniform morphism's substitution blocks; answer the kth (binary-indexed) symbol of the iterated image."
    design_choice = "Answer format: output the kth symbol as a single lowercase letter from the alphabet, with k given in binary and the morphism specified by a fixed list of substitution rules."
    config_cls = MorphismWordConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        while True:
            a = random.randint(2, cfg.max_alphabet)
            letters = random.sample(ALPHABET, a)
            L = random.randint(2, cfg.max_L)
            if L > cfg.max_L:
                continue
            n = 1
            while L ** n < cfg.min_len and L ** (n + 1) <= cfg.max_len:
                n += 1
            while L ** (n + 1) <= cfg.max_len:
                if random.random() < 0.5:
                    break
                n += 1
            length = L ** n
            if length < cfg.min_len or length > cfg.max_len:
                continue
            morph = {c: "".join(random.choice(letters) for _ in range(L)) for c in letters}
            seed = random.choice(letters)
            word = seed
            for _ in range(n):
                word = "".join(morph[c] for c in word)
            assert len(word) == length, (L, n, length)
            k = random.randrange(length)
            answer = word[k]
            assert _kth_symbol(letters, morph, seed, n, k) == answer
            kbin = bin(k)[2:]
            return Entry(
                metadata={
                    "alphabet": letters,
                    "morphism": morph,
                    "seed": seed,
                    "n": n,
                    "L": L,
                    "length": length,
                    "k_binary": kbin,
                    "answer": answer,
                },
                answer=answer,
            )

    def render_prompt(self, metadata):
        rules = "\n".join(
            f"  {c} -> {metadata['morphism'][c]}" for c in metadata["alphabet"]
        )
        alphabet = ", ".join(metadata["alphabet"])
        return (
            f"A uniform morphism over the alphabet {{{alphabet}}} replaces each letter by a "
            f"fixed string of length {metadata['L']}:\n"
            f"{rules}\n"
            f"Beginning with the single-letter word {metadata['seed']}, applying the morphism "
            f"{metadata['n']} times produces a word of length {metadata['length']}.\n"
            f"What symbol is at position k = {metadata['k_binary']} (binary, 0-indexed) of that word?\n"
            "The answer is the single lowercase letter at that position."
        )

    def score_answer(self, answer, entry):
        prepr = lambda x: str(x).strip()
        answer = prepr(answer)
        reference = prepr(entry["answer"])
        if answer == reference:
            return 1.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'morphism_word_indexing (variant 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_state_tracking_r4/morphism_word_indexing',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3867019559,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
