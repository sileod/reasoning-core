"""Endpoint regressions that a default-level generation smoke misses."""
from types import SimpleNamespace

import pytest

from reasoning_core.evaluation.difficulty import check_headroom


class Generator:
    tokenizer = SimpleNamespace(encode=lambda text: text.split())

    def __init__(self, *, pool=100, long_at=None, crash_at=None):
        self.pool, self.long_at, self.crash_at = pool, long_at, crash_at
        self.draw = 0

    def generate_example(self, *, level, max_tokens, timeout):
        assert max_tokens == 0  # Oversized instances must be observed, not filtered out.
        if level == self.crash_at:
            raise TimeoutError("search exhausted")
        self.draw += 1
        prompt = ("large " * 2049 if level == self.long_at
                  else f"instance {self.draw % self.pool}")
        return SimpleNamespace(prompt=prompt, answer="yes", to_dict=lambda: {"prompt": prompt})

    def score_answer(self, answer, entry):
        return 1

    def deduplication_key(self, entry):
        return entry.prompt


def test_varied_binary_answers_are_allowed():
    rows = check_headroom(Generator())
    assert [row["level"] for row in rows] == [0, 6]
    assert all(row["unique_ratio"] == 1 for row in rows)


@pytest.mark.parametrize("kwargs, reason", [
    ({"pool": 3}, "level 0: instance pool"),
    ({"long_at": 6}, "level 6: prompt has"),
    ({"crash_at": 6}, "level 6: search exhausted"),
])
def test_rejects_unusable_endpoints(kwargs, reason):
    with pytest.raises(ValueError, match=reason):
        check_headroom(Generator(**kwargs))


def test_slow_batch_fails_even_when_each_draw_meets_timeout(monkeypatch):
    ticks = iter(x * 0.6 for x in range(100))
    monkeypatch.setattr("reasoning_core.evaluation.difficulty.time.monotonic",
                        lambda: next(ticks))
    with pytest.raises(ValueError, match="generation averages"):
        check_headroom(Generator(), max_mean_seconds=0.5)


def test_fast_batch_does_not_hide_one_slow_draw(monkeypatch):
    ticks = iter([0, 4])
    monkeypatch.setattr("reasoning_core.evaluation.difficulty.time.monotonic",
                        lambda: next(ticks))
    with pytest.raises(ValueError, match="generation took"):
        check_headroom(Generator())


def test_landing_contract_runs_endpoint_gate(monkeypatch):
    import sys
    from reasoning_core.task_search.validation import _CONTRACT_AUDIT

    module = SimpleNamespace(Candidate=lambda: Generator(long_at=6))
    monkeypatch.setitem(sys.modules, "headroom_candidate", module)
    monkeypatch.setattr(sys, "argv", ["audit", '[["headroom_candidate", "Candidate"]]',
                                     "42", "0,1,2,3,4", "64"])
    with pytest.raises(ValueError, match="level 6: prompt has"):
        exec(_CONTRACT_AUDIT, {})

