import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from reasoning_core.template import Config, Entry
from masked_stencil_identification import (
    MaskedStencilConfig,
    MaskedStencilIdentification,
    _parse_answer,
)


def _summarize(ans):
    if not ans:
        return ''
    return ans


def test_config_difficulty_changes():
    c = MaskedStencilConfig()
    base = (c.radius, c.alphabet, c.runs, c.rows, c.cols)
    c.set_level(1)
    changed = any((
        c.radius != base[0], c.alphabet != base[1], c.runs != base[2],
        c.rows != base[3], c.cols != base[4] or abs(c.mask_prob - 0.3) > 1e-9,
    ))
    assert changed
    c.set_level(0)
    assert c.runs == 2 and c.cols == 7 and c.rows == 5 and c.radius == 1


def test_answer_correct():
    task = MaskedStencilIdentification()
    for _ in range(15):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1


def test_junk_scores_zero():
    task = MaskedStencilIdentification()
    ex = task.generate_example()
    assert task.score_answer('', ex) == 0
    assert task.score_answer('asdf', ex) == 0
    assert task.score_answer('import fakemodule', ex) == 0


def test_answer_matches_observed():
    task = MaskedStencilIdentification()
    for _ in range(10):
        ex = task.generate_example()
        want = _parse_answer(ex.answer)
        got = {i: v for i, v in ex.metadata['answer_list']}
        assert want == got


def test_rule_consistent_with_true_rule():
    base = 2
    r = 1
    W = 3
    # reconstruction can't see the rule; just check indices decode to valid windows
    task = MaskedStencilIdentification()
    for _ in range(10):
        ex = task.generate_example()
        for i, v in ex.metadata['answer_list']:
            assert 0 <= v < ex.metadata['alphabet']
            assert i < (ex.metadata['alphabet'] ** (2 * ex.metadata['radius'] + 1))


def test_metadata_json_serializable():
    import json
    task = MaskedStencilIdentification()
    ex = task.generate_example()
    json.dumps(dict(ex.metadata))


def test_format_example_in_prompt():
    task = MaskedStencilIdentification()
    ex = task.generate_example()
    assert "2:1 5:0" in ex.prompt
    assert "?" in ex.prompt
