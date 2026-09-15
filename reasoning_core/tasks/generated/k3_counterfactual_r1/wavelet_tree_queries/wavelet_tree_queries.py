"""Rank, select, and range-quantile queries answered by descending a wavelet tree/matrix bit partition."""

import random
from dataclasses import dataclass, field

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'wavelet_tree_queries (draw 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_counterfactual_r1/wavelet_tree_queries',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class WaveletConfig(Config):
    length: int = 16
    alphabet_size: int = 4

    def apply_difficulty(self, level):
        self.length = stochastic_rounding(self.length + 6 * level)
        self.alphabet_size = 2 + level


def _rank(symbols, symbol, lo, hi):
    return sum(1 for s in symbols[lo:hi] if s == symbol)


def _range_quantile(symbols, lo, hi, k):
    return sorted(symbols[lo:hi])[k - 1]


def _select(symbols, symbol, occurrence):
    count = 0
    for i, s in enumerate(symbols):
        if s == symbol:
            count += 1
            if count == occurrence:
                return i
    return -1


class WaveletTreeQueries(Task):
    summary = ("Answer rank, select, and range-quantile queries on a symbol sequence by descending its "
               "wavelet tree/matrix through bit partitions; report the requested count, position, or value.")
    design_choice = ("Generate random sequences over alphabets of varying size, with queries targeting "
                     "worst-case bit-depth paths to stress rank operations.")
    config_cls = WaveletConfig

    def generate_entry(self):
        length = self.config.length
        alphabet_size = self.config.alphabet_size

        while True:
            symbols = [random.randrange(alphabet_size) for _ in range(length)]
            seen = set(symbols)
            if len(seen) >= 2:
                break

        query_type = random.choice(["rank", "select", "quantile"])

        if query_type == "rank":
            symbol = random.choice(sorted(seen))
            lo = random.randrange(0, length)
            hi = random.randrange(lo + 1, length + 1)
            result = _rank(symbols, symbol, lo, hi)
            metadata = {
                "symbols": symbols,
                "query": "rank",
                "symbol": symbol,
                "lo": lo,
                "hi": hi,
                "bit_depth": alphabet_size.bit_length(),
            }
            answer = str(result)
        elif query_type == "select":
            symbol = random.choice(sorted(seen))
            total = _rank(symbols, symbol, 0, length)
            occurrence = random.randrange(1, max(total, 1) + 1)
            position = _select(symbols, symbol, occurrence)
            metadata = {
                "symbols": symbols,
                "query": "select",
                "symbol": symbol,
                "occurrence": occurrence,
            }
            answer = str(position)
        else:
            lo = random.randrange(0, length)
            hi = random.randrange(lo + 1, length + 1)
            span = hi - lo
            k = random.randrange(1, span + 1)
            value = _range_quantile(symbols, lo, hi, k)
            metadata = {
                "symbols": symbols,
                "query": "quantile",
                "lo": lo,
                "hi": hi,
                "k": k,
            }
            answer = str(value)

        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        symbols = metadata["symbols"]
        q = metadata["query"]
        if q == "rank":
            return (
                f"Given the symbol sequence S = {symbols!r}, count how many occurrences of symbol "
                f"{metadata['symbol']} appear in positions lo = {metadata['lo']} to hi = {metadata['hi']} "
                f"(0-indexed, hi exclusive). A wavelet tree descends the bit partition of S answering rank "
                f"queries level by level. Report the count as one integer."
            )
        if q == "select":
            return (
                f"Given the symbol sequence S = {symbols!r}, find the 0-indexed position of the "
                f"{_ordinal(metadata['occurrence'])} occurrence of symbol {metadata['symbol']} in S. "
                f"A wavelet tree answers select queries by descending the bit partition. Report the "
                f"position as one integer."
            )
        return (
            f"Given the symbol sequence S = {symbols!r}, find the k = {metadata['k']}-th smallest value "
            f"(1-indexed) among the elements in positions lo = {metadata['lo']} to hi = {metadata['hi']} "
            f"(0-indexed, hi exclusive). A wavelet tree answers range-quantile queries on the bit "
            f"partition. Report that value as one integer."
        )

    def score_answer(self, answer, entry):
        q = entry.metadata["query"]
        try:
            value = int(answer.strip())
        except (ValueError, AttributeError, TypeError):
            return 0.0
        gold = int(entry.answer)
        return 1.0 if value == gold else 0.0


def _ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"
