"""Greedy LZ77 tokenization.

Given an input string (ending in a special end marker '#') and a search-window
size W, greedily parse the string into (offset, length, next-symbol) triples.
At each position, find the longest prefix of the remaining input that matches a
substring starting anywhere in the most recent W characters of the already
encoded text; among equal-length matches prefer the most recent source (smallest
offset). The next symbol is the character immediately after the matched run.
The answer is the full token stream as semicolon-separated offset:length:char
triples.
"""

import random
import string
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'lz77_tokenization (draw 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_verification_repair_r1/lz77_tokenization',
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

design_choice = "Encode answers as semicolon-separated triples with offset:length:char, e.g. '0:0:a;1:2:b;0:0:c'."

MARKER = "#"


def lz77_parse(data, window):
    """Greedy LZ77 parse. window = search buffer size in characters.

    Among equal-length matches, prefers the most recent source (smallest
    offset). Returns a list of (offset, length, next_char) triples.
    """
    out = []
    i = 0
    n = len(data)
    while i < n:
        wstart = max(0, i - window)
        best_len = 0
        best_j = i
        for j in range(wstart, i):
            k = 0
            while i + k < n and data[i + k] == data[j + k]:
                k += 1
            if k >= best_len:
                best_len = k
                best_j = j
        if best_len == 0:
            out.append((0, 0, data[i]))
            i += 1
        else:
            out.append((i - best_j, best_len, data[i + best_len]))
            i += best_len + 1
    return out


def lz77_reconstruct(triples):
    out = []
    for off, ln, ch in triples:
        if ln == 0:
            out.append(ch)
        else:
            for _ in range(ln):
                out.append(out[len(out) - off])
            out.append(ch)
    return "".join(out)


def format_answer(triples):
    return ";".join("%d:%d:%s" % (o, l, c) for o, l, c in triples)


@dataclass
class LZ77TokenizationConfig(Config):
    length: int = 10
    window: int = 3
    alphabet_size: int = 3

    def apply_difficulty(self, level):
        self.length = stochastic_rounding(self.length + 4 * level)
        self.window = stochastic_rounding(self.window + level)
        self.alphabet_size = stochastic_rounding(self.alphabet_size + max(1, level // 2))


class LZ77Tokenization(Task):
    summary = ("Greedily parse a string into (offset, length, next-symbol) LZ77 triples "
               "under a stated search-window size, emitting the full token stream; "
               "alphabet size, window size, and repeat density vary.")
    config_cls = LZ77TokenizationConfig

    def generate_entry(self):
        letters = string.ascii_lowercase[: self.config.alphabet_size]
        weights = [random.uniform(0.3, 1.0) for _ in letters]
        data = "".join(random.choices(letters, weights=weights, k=self.config.length)) + MARKER
        triples = lz77_parse(data, self.config.window)
        assert lz77_reconstruct(triples) == data, "gold parse must reproduce input"
        answer = format_answer(triples)
        return Entry(metadata={
            "data": data,
            "window": self.config.window,
            "alphabet_size": self.config.alphabet_size,
        }, answer=answer)

    def render_prompt(self, metadata):
        data = metadata["data"]
        w = metadata["window"]
        return (
            "Use greedy LZ77 parsing to tokenize the string below into (offset, length, "
            "next-symbol) triples, then list the full token stream.\n"
            "At each step find the longest prefix of the remaining input that matches a "
            "substring starting anywhere in the most recent %d characters of the already "
            "encoded text; if several sources tie for the longest match, use the one "
            "closest to the current position (smallest offset). The next symbol is the "
            "character immediately after the matched run (an unmatched character is "
            "encoded as offset 0, length 0). The string ends with the special symbol "
            "'#' which is not part of the alphabet and is encoded with the rest.\n"
            "\n"
            "String: %s\n"
            "Answer each triple as offset:length:char and join the triples with "
            "semicolons, e.g. '0:0:a;1:2:b;0:0:c'." % (w, data)
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == entry.answer else 0.0
