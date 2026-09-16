import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def _parse_q(sentence):
    low = sentence.lower()
    if "exactly" in low:
        n = int([tok for tok in sentence.split() if tok.isdigit()][0])
        return "exactly_n", n
    if "all but one" in low:
        return "all_but_one", None
    if "more than half" in low:
        return "more_than_half", None
    if "most" in low:
        return "most", None
    if "few" in low:
        return "few", None
    raise ValueError(sentence)


def _evaluate(model, quantifier, n):
    A = set(model["A"])
    B = set(model["B"])
    inter = len(A & B)
    elim = len(A) - inter
    if quantifier == "exactly_n":
        return inter == n
    if quantifier == "all_but_one":
        return elim == 1
    if quantifier == "more_than_half":
        return inter > len(A) / 2
    if quantifier == "most":
        return len(A) >= 2 and inter > len(A) / 2
    if quantifier == "few":
        return inter < len(A) / 3
    raise ValueError(quantifier)


def test_gold_scrutinizer():
    random.seed(1339177894)
    from generalized_quantifier_truth import GeneralizedQuantifierTruth
    task = GeneralizedQuantifierTruth()
    task.config.set_level(3)
    for _ in range(300):
        entry = task.generate_entry()
        q, n = _parse_q(entry.metadata["sentence"])
        assert q == entry.metadata["quantifier"]
        expected = _evaluate(entry.metadata["model"], q, n)
        assert entry.answer == ("True" if expected else "False")


def test_all_levels_generate_and_score():
    random.seed(99)
    from generalized_quantifier_truth import GeneralizedQuantifierTruth
    for level in (0, 1, 3, 6):
        task = GeneralizedQuantifierTruth()
        task.config.set_level(level)
        seen = set()
        for _ in range(30):
            entry = task.generate_entry()
            assert task.score_answer(entry.answer, entry) == 1.0
            assert task.score_answer("", entry) < 1.0
            assert task.score_answer("garbage", entry) < 1.0
            seen.add(entry.answer)
        assert seen == {"True", "False"}


def test_nonempty_and_balanced():
    random.seed(12345)
    from generalized_quantifier_truth import GeneralizedQuantifierTruth
    task = GeneralizedQuantifierTruth()
    task.config.set_level(2)
    counts = {"True": 0, "False": 0}
    for _ in range(500):
        entry = task.generate_entry()
        counts[entry.answer] += 1
    assert counts["True"] > 0 and counts["False"] > 0
