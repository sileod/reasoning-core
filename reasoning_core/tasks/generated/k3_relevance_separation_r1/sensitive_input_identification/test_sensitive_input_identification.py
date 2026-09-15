import random

from reasoning_core.tasks.generated.k3_relevance_separation_r1.sensitive_input_identification.sensitive_input_identification import (
    SensitiveInputIdentification,
    compute_critical,
    eval_tree,
    format_answer,
    parse_answer,
    render_tree,
)


def test_gold_scores_one():
    random.seed(1)
    task = SensitiveInputIdentification()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_recompute_critical_sets():
    random.seed(42)
    task = SensitiveInputIdentification()
    x = task.generate_example()
    tree, assign, n = x.metadata["tree"], x.metadata["assign"], x.metadata["n"]
    crit, pairs, base = compute_critical(tree, assign, n)
    assert crit == x.metadata["crit_bits"]
    assert pairs == [tuple(p) for p in x.metadata["crit_pairs"]]
    assert base == x.metadata["base"]
    assert eval_tree(tree, assign) == x.metadata["base"]


def test_junk_scores_zero():
    random.seed(7)
    task = SensitiveInputIdentification()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("garbage", x) == 0.0
    assert task.score_answer("[];[]", x) in (0.0, 1.0)


def test_all_levels_valid():
    task = SensitiveInputIdentification()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(5):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0
            assert parse_answer(x.answer) is not None


def test_difficulty_changes():
    task = SensitiveInputIdentification()
    task.config.set_level(0)
    n0 = task.config.n
    task.config.set_level(6)
    n6 = task.config.n
    assert n6 > n0


def test_format_roundtrip():
    bits = [0, 3]
    pairs = [(1, 2), (2, 4)]
    s = format_answer(bits, pairs)
    assert s == "[0,3];[(1 2),(2 4)]"
    assert parse_answer(s) == ((0, 3), ((1, 2), (2, 4)))
    assert parse_answer("[];[]") == ((), ())


def test_distractors_rejected():
    random.seed(99)
    task = SensitiveInputIdentification()
    for _ in range(20):
        x = task.generate_example()
        for d in task.distractor_candidates(x):
            assert d != x.answer
            assert task.score_answer(d, x) == 0.0


def test_read_once_each_variable_once():
    random.seed(123)

    def collect(node):
        if node[0] == "var":
            return [node[1]]
        out = []
        for child in node[1:]:
            out.extend(collect(child))
        return out

    task = SensitiveInputIdentification()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            x = task.generate_example()
            leaves = sorted(collect(x.metadata["tree"]))
            assert leaves == list(range(x.metadata["n"])), (
                "read-once invariant broken: variables are not a permutation"
            )


def test_answer_domain_valid():
    random.seed(5)
    task = SensitiveInputIdentification()
    for level in (0, 3, 6):
        task.config.set_level(level)
        n = task.config.n
        for _ in range(20):
            x = task.generate_example()
            bits, pairs = parse_answer(x.answer)
            assert all(0 <= b < n for b in bits)
            assert all(0 <= a < b < n for a, b in pairs)
            assert sorted(bits) == list(bits)
            assert list(pairs) == sorted(pairs)


def test_both_parts_varied():
    random.seed(2024)
    task = SensitiveInputIdentification()
    saw_bits_empty, saw_bits_nonempty = False, False
    saw_pairs_empty, saw_pairs_nonempty = False, False
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(30):
            x = task.generate_example()
            bits, pairs = parse_answer(x.answer)
            saw_bits_empty |= (len(bits) == 0)
            saw_bits_nonempty |= (len(bits) > 0)
            saw_pairs_empty |= (len(pairs) == 0)
            saw_pairs_nonempty |= (len(pairs) > 0)
    assert saw_bits_empty and saw_bits_nonempty
    assert saw_pairs_empty and saw_pairs_nonempty
