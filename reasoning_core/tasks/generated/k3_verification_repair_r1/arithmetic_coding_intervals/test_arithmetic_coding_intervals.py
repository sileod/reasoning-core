import importlib.util
from pathlib import Path

_HERE = Path(__file__).parent
_SPEC = importlib.util.spec_from_file_location(
    "arithmetic_coding_intervals", _HERE / "arithmetic_coding_intervals.py")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)
ArithmeticCodingConfig = _MOD.ArithmeticCodingConfig
ArithmeticCodingIntervals = _MOD.ArithmeticCodingIntervals
_encode_intervals = _MOD._encode_intervals
_to_common = _MOD._to_common


def test_summary_and_meta():
    assert 'endpoints' in ArithmeticCodingIntervals.summary
    assert 'invert' in ArithmeticCodingIntervals.summary


def test_generate_scores_gold():
    task = ArithmeticCodingIntervals()
    for lvl in range(7):
        cfg = ArithmeticCodingConfig()
        cfg.set_level(lvl)
        task.config = cfg
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_not_scored():
    task = ArithmeticCodingIntervals()
    cfg = ArithmeticCodingConfig()
    task.config = cfg
    for _ in range(10):
        ex = task.generate_example()
        assert task.score_answer('', ex) == 0.0
        assert task.score_answer('garbage', ex) == 0.0


def test_decode_answer_reproduces_word():
    for _ in range(5):
        cfg = ArithmeticCodingConfig()
        cfg.set_level(5)
        task = ArithmeticCodingIntervals()
        task.config = cfg
        ex = task.generate_example()
        if ex.metadata['mode'] == 'decode':
            num = ex.metadata['target_num']
            den = ex.metadata['target_den']
            value = num / den
            lo, hi = _encode_intervals(ex.metadata['word'])
            assert lo <= value < hi


def test_encode_endpoints_are_consistent():
    for _ in range(5):
        cfg = ArithmeticCodingConfig()
        cfg.set_level(0)
        task = ArithmeticCodingIntervals()
        task.config = cfg
        ex = task.generate_example()
        assert ex.metadata['mode'] == 'endpoints'
        lo, hi = _encode_intervals(ex.metadata['word'])
        lo_num, hi_num, den = _to_common(ex.metadata['word'], lo, hi)
        assert (lo_num, hi_num, den) == (ex.metadata['lo'], ex.metadata['hi'],
                                         ex.metadata['den'])


def test_both_inverse_modes_appear():
    cfg = ArithmeticCodingConfig()
    cfg.set_level(5)
    task = ArithmeticCodingIntervals()
    task.config = cfg
    modes = set()
    for _ in range(200):
        ex = task.generate_example()
        assert ex.metadata['mode'] in ('lo', 'decode')
        modes.add(ex.metadata['mode'])
    assert modes == {'lo', 'decode'}


def test_metadata_json_serializable():
    import json
    cfg = ArithmeticCodingConfig()
    cfg.set_level(5)
    task = ArithmeticCodingIntervals()
    task.config = cfg
    ex = task.generate_example()
    json.dumps(ex.metadata)
