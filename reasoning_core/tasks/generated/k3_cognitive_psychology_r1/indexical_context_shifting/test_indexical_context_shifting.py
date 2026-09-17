import json
import random
from collections import Counter

import pytest

from reasoning_core.tasks.generated.k3_cognitive_psychology_r1.indexical_context_shifting.indexical_context_shifting import (
    CONTEXTS,
    REFERENTS,
    IndexicalConfig,
    IndexicalContextShifting,
    shift,
    verify,
)


@pytest.fixture(autouse=True)
def preserve_random_state():
    state = random.getstate()
    random.seed(729651269)
    yield
    random.setstate(state)


def test_every_primitive_and_context():
    operators = [[kind, sign, offset] for kind in ("day", "city")
                 for sign in (-1, 0, 1) for offset in range(4)] + [["swap", 0, 0]]
    for op in operators:
        results = []
        for start in CONTEXTS:
            final = shift(start, op)
            results.append(final)
            verify(start, [op], final, REFERENTS[final[0]][final[1]])
        assert sorted(results) == list(CONTEXTS)


def test_nested_order_and_current_coordinates():
    start = (1, 2)
    operators = [["day", 1, 1], ["city", -1, 2], ["swap", 0, 0]]
    current = start
    for op in operators:
        current = shift(current, op)
    assert current == (0, 0)
    verify(start, operators, current, "Mira")
    reverse = start
    for op in reversed(operators):
        reverse = shift(reverse, op)
    assert reverse != current


def test_negative_wrap_and_simultaneous_swap():
    assert shift((0, 3), ["day", -1, 0]) == (1, 3)
    assert shift((3, 0), ["city", -1, 0]) == (3, 1)
    assert shift((3, 1), ["swap", 0, 0]) == (1, 3)


def test_verifier_rejects_false_gold_and_unknown_operations():
    with pytest.raises(AssertionError):
        verify((0, 0), [["day", 0, 1]], (0, 0), "Mira")
    with pytest.raises(AssertionError):
        verify((0, 0), [], (0, 0), "Tomas")
    with pytest.raises(ValueError):
        verify((0, 0), [["invalid", 0, 0]], (0, 0), "Mira")
    with pytest.raises(ValueError):
        shift((0, 0), ["invalid", 0, 0])


@pytest.mark.parametrize("level", range(7))
def test_generated_distribution_and_roundtrip(level):
    task = IndexicalContextShifting()
    task.config.set_level(level)
    counts = Counter()
    for _ in range(160):
        entry = task.generate_entry()
        data = json.loads(json.dumps(entry.metadata))
        prompt = task.render_prompt(data)
        assert prompt == task.render_prompt(entry.metadata)
        assert "outermost bracket inward" in prompt
        assert "count of shifts" not in prompt
        verify(data["start"], data["operators"], data["trace"][-1], entry.answer)
        assert task.score_answer(entry.answer, entry) == 1
        assert task.score_answer("", entry) == 0
        assert task.score_answer("junk", entry) == 0
        counts[entry.answer] += 1
    assert set(counts) == {name for row in REFERENTS for name in row}
    assert max(counts.values()) < 35


def test_scorer_is_stateless_and_exact():
    class Forbidden:
        def __getattribute__(self, name):
            raise AssertionError(name)

    task = IndexicalContextShifting()
    entry = task.generate_entry()
    score = IndexicalContextShifting.score_answer
    assert score(Forbidden(), entry.answer, entry) == 1
    assert score(Forbidden(), "  " + entry.answer + "\n", entry) == 1
    for value in (None, [], {}, 2, entry.answer.lower(), entry.answer + "."):
        assert score(Forbidden(), value, entry) == 0


def test_seed_reproducibility_and_difficulty_reset():
    def draw():
        random.seed(729651269)
        task = IndexicalContextShifting()
        task.config.set_level(6)
        return [(entry.metadata, entry.answer) for entry in
                (task.generate_entry() for _ in range(20))]

    assert draw() == draw()
    config = IndexicalConfig()
    depths = []
    for level in range(7):
        config.set_level(level)
        depths.append(config.depth)
    assert depths == sorted(set(depths))
    config.set_level(0)
    assert config.depth == 2
