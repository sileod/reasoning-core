import heapq
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class CanonicalHuffmanConfig(Config):
    n_symbols: int = 6
    max_weight: int = 20

    def apply_difficulty(self, level):
        self.n_symbols = stochastic_rounding(self.n_symbols + 2 * level)
        self.max_weight = stochastic_rounding(self.max_weight + 5 * level)


def _tree_to_lengths(freq):
    n = len(freq)
    heap = [(f, i, [i]) for i, f in enumerate(freq)]
    heapq.heapify(heap)
    depth = [0] * n
    while len(heap) > 1:
        w1, m1, leaves1 = heapq.heappop(heap)
        w2, m2, leaves2 = heapq.heappop(heap)
        for l in leaves1 + leaves2:
            depth[l] += 1
        merged = leaves1 + leaves2
        min_leaf = min(merged)
        heap.append((w1 + w2, min_leaf, merged))
        heapq.heapify(heap)
    return depth


def _canonical_code(freq, idx):
    lengths = _tree_to_lengths(freq)
    n = len(freq)
    if lengths[idx] == 0:
        return "0"
    order = sorted(range(n), key=lambda i: (lengths[i], i))
    codes = {}
    code = 0
    prev_len = 0
    for i in order:
        l = lengths[i]
        if l == 0:
            continue
        code <<= (l - prev_len)
        codes[i] = format(code, "0{}b".format(l))
        code += 1
        prev_len = l
    return codes[idx]


class CanonicalHuffmanCode(Task):
    summary = (
        "Given positive integer symbol frequencies, build a tie-broken Huffman tree "
        "and output one randomly-chosen symbol's canonical codeword."
    )
    design_choice = (
        "Choose the queried symbol at random from the frequency table, ensuring "
        "all symbols are queried across instances."
    )
    config_cls = CanonicalHuffmanConfig
    task_version = 2

    def generate_entry(self):
        n = self.config.n_symbols
        freq = [random.randint(1, self.config.max_weight) for _ in range(n)]
        idx = random.randrange(n)
        code = _canonical_code(freq, idx)
        symbol = chr(ord("A") + idx)
        metadata = {
            "frequencies": freq,
            "symbols": [chr(ord("A") + i) for i in range(n)],
            "query": symbol,
        }
        return Entry(metadata=metadata, answer=code)

    def render_prompt(self, metadata):
        table = ", ".join(
            f"{s}:{f}" for s, f in zip(metadata["symbols"], metadata["frequencies"])
        )
        return (
            f"Consider the following symbol frequencies: {table}. "
            f"Build the Huffman coding tree using these frequencies, breaking ties "
            f"by merging the two subtrees with the smallest total weight first, and "
            f"when two candidate subtrees have equal weight, prefer the one whose "
            f"root symbol is alphabetically first. Then assign canonical Huffman "
            f"codewords (the standard canonical Huffman algorithm using the depths "
            f"from this tree). What is the canonical codeword for symbol "
            f"{metadata['query']}? Answer with only the binary codeword."
        )

    def score_answer(self, answer, entry):
        return 1.0 if answer.strip() == canonical_for(entry) else 0.0


def canonical_for(entry):
    freq = list(entry.metadata["frequencies"])
    symbols = entry.metadata["symbols"]
    query = entry.metadata["query"]
    idx = symbols.index(query)
    return _canonical_code(freq, idx)


TASK_META = {'parent_source_id': None,
 'idea': 'canonical_huffman_code (draw 1 of 3)',
 'hypothesis': 'external:canonical_huffman_code',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/canonical_huffman_code',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2881578109,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
