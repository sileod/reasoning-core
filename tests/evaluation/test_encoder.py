import pytest

from reasoning_core.evaluation.distractors import POLICIES, char, is_wrong, negatives
from reasoning_core.evaluation.metrics import EvalExample, score_mcq
from reasoning_core.utils.hf_sample import sample_rows


def test_negatives_are_distinct_and_never_the_gold():
    row = {"prompt": "E1 is newer than E2. E4 is the oldest.", "answer": "E3", "task": "t"}
    pool = ["E1", "E2", "E3", "E5", "bin", "7"]
    for policy in POLICIES:
        got = negatives(row, pool, k=3, policy=policy, seed=1, verify=False)
        assert len(got) == 3 and len(set(got)) == 3 and "E3" not in got


def test_char_similarity_ranks_near_misses_first():
    assert char("[3, 5, 7]", ["cabinet", "[3, 5, 8]", "No"])[0] == "[3, 5, 8]"


def test_the_verifier_rejects_only_wrong_answers():
    import reasoning_core as rc
    T = rc.get_task("arithmetics")
    row = (T() if isinstance(T, type) else T).generate_example().to_dict()
    assert not is_wrong(row["answer"], row)
    assert is_wrong("definitely not the answer", row)


def test_score_mcq_takes_any_cost_lower_is_better():
    examples = [EvalExample("q", "x", ("x", "y"), 0), EvalExample("q", "y", ("x", "y"), 1)]
    result = score_mcq(examples, lambda ex: [0.0, 1.0])      # always picks choice 0
    assert result["accuracy"] == 0.5 and result["margin"] == 0.0


def test_sample_rows_needs_a_pinned_revision():
    with pytest.raises(ValueError):
        sample_rows("tasksource/tasksource_dpo_pairs", "main", n=10)
