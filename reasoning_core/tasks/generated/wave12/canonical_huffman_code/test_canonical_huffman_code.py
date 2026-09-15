import random

from reasoning_core.tasks.generated.wave12.canonical_huffman_code.canonical_huffman_code import (
    CanonicalHuffmanCode,
    CanonicalHuffmanConfig,
    _canonical_code,
    _tree_to_lengths,
    canonical_for,
)


def test_gold_answer_scores_one():
    task = CanonicalHuffmanCode()
    for _ in range(30):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_code_is_prefix_free_across_symbols():
    random.seed(2881578109)
    freq = [4, 6, 8, 3, 12, 15]
    codes = [_canonical_code(freq, i) for i in range(len(freq))]
    for a in codes:
        for b in codes:
            if a != b:
                assert not (a.startswith(b) or b.startswith(a))


def test_canonical_format_matches_depth():
    freq = [4, 6, 8, 3, 12, 2]
    n = len(freq)
    code_lengths = [len(_canonical_code(freq, i)) for i in range(n)]
    tree_lengths = _tree_to_lengths(freq)
    assert code_lengths == tree_lengths
    kraft = sum((0.5 ** l) for l in tree_lengths)
    assert abs(kraft - 1.0) < 1e-9


def test_difficulty_changes_config():
    cfg = CanonicalHuffmanConfig()
    base = cfg.n_symbols
    cfg.apply_difficulty(3)
    assert cfg.n_symbols > base


def test_scores_reject_empty_and_junk():
    task = CanonicalHuffmanCode()
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("not a code", entry) == 0.0


def test_canonical_for_matches_answer():
    task = CanonicalHuffmanCode()
    for _ in range(20):
        entry = task.generate_example()
        assert canonical_for(entry) == entry.answer
