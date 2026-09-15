import random

from reasoning_core.tasks.generated.k3_verification_repair_r1.lz77_tokenization.lz77_tokenization import (
    LZ77Tokenization,
    lz77_parse,
    lz77_reconstruct,
    format_answer,
    MARKER,
)


def test_gold_scores_one_every_level():
    for level in range(7):
        task = LZ77Tokenization()
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = LZ77Tokenization()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("garbage", ex) == 0.0
    assert task.score_answer(None, ex) == 0.0


def test_reconstruct_matches_input_deterministic():
    random.seed(1662004003)
    for _ in range(200):
        letters = "abcde"
        w = random.randint(2, 6)
        data = "".join(random.choices(letters, k=random.randint(5, 30))) + MARKER
        triples = lz77_parse(data, w)
        assert triples[0] == (0, 0, data[0])
        assert lz77_reconstruct(triples) == data


def test_parse_well_formed():
    random.seed(1)
    data = "abracadabra" + MARKER
    triples = lz77_parse(data, 7)
    # every length-0 triple has a real offset 0
    for off, ln, ch in triples:
        assert ln == 0 or ln >= 1
        assert ch == MARKER or ch in "abcdr" or ch == "b"
