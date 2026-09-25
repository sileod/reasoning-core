import os
import random
import sys

sys.path.insert(0, os.getcwd())

from reasoning_core.tasks.generated.ua_state_tracking_r4.likelihood_sufficient_partition.likelihood_sufficient_partition import (
    LikelihoodSufficientPartition,
    _normalize,
)


def test_generate_and_score():
    random.seed(12345)
    task = LikelihoodSufficientPartition()
    for _ in range(20):
        task.config.set_level(random.randint(0, 6))
        entry = task.generate_example()
        assert entry.answer
        assert task.score_answer(entry.answer, entry) == 1.0


def test_wrong_answer():
    random.seed(999)
    task = LikelihoodSufficientPartition()
    task.config.set_level(1)
    entry = task.generate_example()
    gold = entry.answer
    bad = gold + ",0" if not gold.endswith("0") else gold[:-1] + "9"
    assert task.score_answer(bad, entry) == 0.0
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("junk", entry) == 0.0


def test_gold_is_consistent_with_definition():
    random.seed(4242)
    task = LikelihoodSufficientPartition()
    for _ in range(30):
        task.config.set_level(random.randint(0, 6))
        entry = task.generate_example()
        feats = entry.metadata["features"]
        gold = [int(x) for x in entry.answer.split(",")]
        # proportional vectors must share a class label
        for i in range(len(feats)):
            for j in range(i + 1, len(feats)):
                same_prop = _normalize(list(feats[i])) == _normalize(list(feats[j]))
                assert (gold[i] == gold[j]) == same_prop
