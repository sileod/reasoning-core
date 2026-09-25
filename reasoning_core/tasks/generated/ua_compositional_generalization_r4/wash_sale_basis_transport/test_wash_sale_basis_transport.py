import pytest

from reasoning_core.tasks.generated.ua_compositional_generalization_r4.wash_sale_basis_transport.wash_sale_basis_transport import (
    WashSaleBasisTransport,
)


def test_generate_and_score():
    task = WashSaleBasisTransport()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_score_bad_answers():
    task = WashSaleBasisTransport()
    x = task.generate_example()
    assert task.score_answer("", x) < 1.0
    assert task.score_answer("junk", x) < 1.0


def test_difficulty_changes():
    task = WashSaleBasisTransport()
    c0 = task.config.lots
    task.config.set_level(6)
    assert task.config.lots > c0


def test_metadata_json_serializable():
    import json
    task = WashSaleBasisTransport()
    x = task.generate_example()
    json.dumps(x.metadata)


def test_answer_domain():
    task = WashSaleBasisTransport()
    for _ in range(50):
        x = task.generate_example()
        int(x.answer)
