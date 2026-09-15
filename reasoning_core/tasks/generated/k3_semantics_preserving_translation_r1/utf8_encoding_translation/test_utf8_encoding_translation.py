from reasoning_core.tasks.generated.k3_semantics_preserving_translation_r1.utf8_encoding_translation.utf8_encoding_translation import (
    Utf8EncodingTranslation,
)


def _score_true(x):
    return Utf8EncodingTranslation().score_answer(x.answer, x) == 1.0


def test_gold_roundtrip_all_levels():
    task = Utf8EncodingTranslation()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            x = task.generate_example()
            assert _score_true(x)


def test_dec_reconstructs_codepoint():
    task = Utf8EncodingTranslation()
    task.config.set_level(5)
    for _ in range(50):
        x = task.generate_example()
        for seg, part in zip(x.metadata["segments"], x.answer.split(" | ")):
            if seg["kind"] == "dec":
                values = [int(g, 2) for g in seg["binary"]]
                cp = ord(bytes(values).decode("utf-8"))
                assert part == "C:" + str(cp), (seg, part)


def test_enc_reconstructs_bytes():
    task = Utf8EncodingTranslation()
    task.config.set_level(5)
    for _ in range(50):
        x = task.generate_example()
        for seg, part in zip(x.metadata["segments"], x.answer.split(" | ")):
            if seg["kind"] == "enc":
                bs = list(chr(seg["cp"]).encode("utf-8"))
                assert part == "B:" + " ".join(str(b) for b in bs), (seg, part)


def test_garbage_not_scored():
    task = Utf8EncodingTranslation()
    x = task.generate_example()
    assert task.score_answer("", x) < 1.0
    assert task.score_answer("junk", x) < 1.0
    assert task.score_answer("C:999 | B:1 2", x) < 1.0
