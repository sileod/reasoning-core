import random

import pytest

from reasoning_core.template import Config, Entry
from reasoning_core.tasks.generated.k3_parsing_and_agreement_r4.concat_stack_evaluate.concatenative_stack_evaluation import (
    WORDS,
    ConcatStackConfig,
    ConcatStackEvaluate,
    exec_flat,
    flatten,
    word_min,
)


def _fresh(level=0):
    config = ConcatStackConfig()
    config.set_level(level)
    return ConcatStackEvaluate(config=config)


def test_gold_answers_score_one():
    task = ConcatStackEvaluate()
    task.config.set_level(0)
    for _ in range(60):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_modes_varp():
    task = ConcatStackEvaluate()
    task.config.set_level(0)
    modes = set()
    for _ in range(120):
        ex = task.generate_example()
        modes.add(ex.metadata['mode'])
    assert modes == {1, 2, 3}


def test_mode1_answer_matches_execution():
    task = ConcatStackEvaluate()
    task.config.set_level(2)
    for _ in range(40):
        ex = task.generate_example()
        if ex.metadata['mode'] != 1:
            continue
        st, under = exec_flat(flatten(ex.metadata['program']))
        assert under is None
        assert ' '.join(str(x) for x in reversed(st)) == ex.answer


def test_word_min_positive():
    for w in WORDS:
        assert word_min(w) >= 1


def test_words_do_not_recurse():
    def refs(w):
        return {t for t in WORDS[w] if t in WORDS}

    queue = list(WORDS)
    seen = set()
    while queue:
        w = queue.pop()
        if w in seen:
            continue
        seen.add(w)
        for r in refs(w):
            if r == w:
                assert False, 'self recursion'
            queue.append(r)
    assert seen == set(WORDS) or set(WORDS).issubset(seen)


def test_metadata_json_serializable():
    task = ConcatStackEvaluate()
    task.config.set_level(0)
    import json
    for _ in range(20):
        ex = task.generate_example()
        json.dumps(dict(ex.metadata))


def test_all_levels_generate():
    for level in range(7):
        task = ConcatStackEvaluate()
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_wrong_answers_score_zero():
    task = ConcatStackEvaluate()
    task.config.set_level(0)
    ex = task.generate_example()
    assert task.score_answer('', ex) < 1.0
    assert task.score_answer('zzz 999', ex) < 1.0
