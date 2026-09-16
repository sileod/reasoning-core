import copy
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ctl_fixpoint_model_checking import (
    CtlFixpointModelChecking,
    _eval_formula,
)


def _verify_entry(entry):
    n = len(entry.metadata["trans"])
    letter_to_i = {chr(ord('a') + i): i for i in range(n)}
    trans = {letter_to_i[k]: [letter_to_i[t] for t in v]
             for k, v in entry.metadata["trans"].items()}
    labels = [entry.metadata["labels"][chr(ord('a') + i)] for i in range(n)]
    gold = _eval_formula(trans, labels, entry.metadata["formula"])
    expected = ''.join(sorted(chr(ord('a') + i) for i in gold)) or 'emptyset'
    assert entry.answer == expected
    return trans, labels


def test_gold_answer_scores_one():
    task = CtlFixpointModelChecking()
    for _ in range(30):
        task.config.set_level(random.randrange(7))
        entry = task.generate_example()
        _verify_entry(entry)
        assert task.score_answer(entry.answer, entry) == 1.0


def test_empty_set_is_emptyset():
    task = CtlFixpointModelChecking()
    task.config.set_level(0)
    entry = task.generate_example()
    n = len(entry.metadata["trans"])
    trans, labels = _verify_entry(entry)
    result = entry.answer
    assert result == 'emptyset' or all(c in 'abcdefghijklmnopqrstuvwxyz' for c in result)


def test_junk_scores_zero():
    task = CtlFixpointModelChecking()
    for _ in range(20):
        entry = task.generate_example()
        assert task.score_answer('', entry) < 1.0
        assert task.score_answer('zz', entry) < 1.0
        assert task.score_answer(None, entry) < 1.0


def test_difficulty_changes_config():
    task = CtlFixpointModelChecking()
    c0 = copy.deepcopy(task.config)
    task.config.set_level(3)
    assert task.config != c0
    assert task.config.states >= c0.states


def test_different_prompts():
    task = CtlFixpointModelChecking()
    prompts = set()
    for _ in range(30):
        entry = task.generate_example()
        prompts.add(entry.prompt)
    assert len(prompts) >= 5


def test_ef_matches_reachable():
    from ctl_fixpoint_model_checking import _eu
    trans = {0: [1], 1: [2], 2: [2]}
    # states that can reach 2 (which satisfies the target) under EF
    reach = {0, 1, 2}
    assert _eu(trans, set(range(3)), {2}) == reach


def test_au_and_eg_domain():
    from ctl_fixpoint_model_checking import _au, _eg
    trans = {0: [1], 1: [1]}
    # AU p p: all paths stay in p; labels outside not needed, p set is all
    assert _au(trans, set(range(2)), set(range(2))) == set(range(2))
    # EG on self-loop state 1 in p-set {1}
    assert _eg(trans, {1}) == {1}


def test_answer_alphabet():
    task = CtlFixpointModelChecking()
    task.config.set_level(6)
    for _ in range(20):
        entry = task.generate_example()
        n = len(entry.metadata["trans"])
        if entry.answer == 'emptyset':
            continue
        assert len(entry.answer) <= n
        assert all(c in 'abcdefghijklmnopqrstuvwxyz' for c in entry.answer)
