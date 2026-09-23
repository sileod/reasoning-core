import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from reasoning_core.template import Entry  # noqa: E402

from proportional_analogy_transfer import (  # noqa: E402
    AnalogTransferConfig,
    ProportionalAnalogyTransfer,
    _op_family,
    _unique_op,
    _render_domain_value,
)


@pytest.fixture(scope="module")
def task():
    random.seed(1234)
    return ProportionalAnalogyTransfer()


def test_generate_and_score(task):
    for _ in range(30):
        ex = task.generate_example(level=random.randint(0, 6))
        assert isinstance(ex, Entry)
        assert task.score_answer(ex.answer, ex) == 1


def test_all_domains_and_modes_seen(task):
    domains = set()
    modes = set()
    for _ in range(80):
        ex = task.generate_example()
        domains.add(ex.metadata.domain)
        modes.add(ex.metadata.mode)
    assert domains == {"string", "tuple", "grid"}
    assert modes == {"term", "name"}


def test_analogy_is_internally_consistent():
    # Verify the A:B pair really uses the recorded op, and term answer = op(C).
    t = ProportionalAnalogyTransfer()
    for _ in range(40):
        ex = t.generate_entry()
        d = ex.metadata
        fam = _op_family(d.domain)
        assert fam[d.op](d.A) == d.B
        if d.mode == "term":
            assert _render_domain_value(d.domain, fam[d.op](d.C)) == ex.answer
            assert fam[d.op](d.C) == d.gold


def test_garbage_scores_zero(task):
    ex = task.generate_example()
    for junk in ("", "junk", "!!!", "0"):
        assert task.score_answer(junk, ex) < 1


def test_grid_entries_are_int_2d_and_json_ok(task):
    for _ in range(20):
        for _ in range(10):
            ex = task.generate_entry()
            if ex.metadata.domain == "grid":
                assert isinstance(ex.metadata.A, list)
                assert all(isinstance(x, int) for r in ex.metadata.A for x in r)
        break


def test_config_difficulty_changes():
    c = AnalogTransferConfig(level=0)
    l0 = c.base_size
    c.set_level(6)
    assert c.base_size > l0


def test_term_answer_not_surface(task):
    # op(C) must differ from C so the answer is not readable off the prompt.
    for _ in range(60):
        ex = task.generate_entry()
        if ex.metadata.mode == "term":
            d = ex.metadata
            fam = _op_family(d.domain)
            assert _render_domain_value(d.domain, fam[d.op](d.C)) != _render_domain_value(d.domain, d.C)

def test_uniqueness_verified():
    # The uniqueness guard must never pass an ambiguous A:B pair.
    t = ProportionalAnalogyTransfer()
    for _ in range(60):
        ex = t.generate_entry()
        assert _unique_op(ex.metadata.domain, ex.metadata.op, ex.metadata.A)
