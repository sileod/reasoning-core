import random

from reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.counter_machine_trace.counter_machine_trace import (
    CounterMachineConfig,
    CounterMachineTrace,
)


def _task(level):
    cfg = CounterMachineConfig()
    cfg.set_level(level)
    t = CounterMachineTrace()
    t.config = cfg
    return t


def test_generate_levels():
    for level in range(7):
        t = _task(level)
        x = t.generate_example()
        assert x.answer


def test_gold_scores_one():
    for level in (0, 3, 6):
        t = _task(level)
        for _ in range(20):
            x = t.generate_example()
            assert t.score_answer(x.answer, x) == 1.0


def test_wrong_answer_scores_zero():
    t = _task(2)
    x = t.generate_example()
    assert t.score_answer('', x) == 0.0
    assert t.score_answer('bogus', x) == 0.0
    assert t.score_answer('9999999', x) == 0.0


def test_difficulty_changes_config():
    c0 = CounterMachineConfig()
    c0.set_level(0)
    c6 = CounterMachineConfig()
    c6.set_level(6)
    assert c6.segments >= c0.segments
    assert c6.max_init >= c0.max_init
    assert c6.num_regs >= c0.num_regs


def test_modes_all_appear():
    t = _task(4)
    seen = set()
    for _ in range(120):
        x = t.generate_example()
        seen.add(x.metadata.mode)
    assert seen == {'value', 'steps', 'trace'}


def test_deterministic_seed():
    t = _task(3)
    random.seed(12345)
    a = [t.generate_example().answer for _ in range(10)]
    random.seed(12345)
    b = [t.generate_example().answer for _ in range(10)]
    assert a == b


def test_steps_and_trace_domain():
    t = _task(5)
    for _ in range(40):
        x = t.generate_example()
        assert x.metadata['_steps'] >= 1
        if x.metadata.mode == 'steps':
            assert int(x.answer) == x.metadata['_steps']
        if x.metadata.mode == 'trace':
            vals = [int(v) for v in x.answer.split(',')]
            assert len(vals) == x.metadata['_steps']
