import random
from fractions import Fraction

from reasoning_core.tasks.generated.k3_global_from_local_r4.station_packing.positional_weight_station_packing import (
    StationPacking,
    _solve,
)


def test_smoke():
    random.seed(1)
    t = StationPacking()
    x = t.generate_example()
    assert t.score_answer(x.answer, x) == 1.0
    assert t.score_answer("", x) < 1.0
    assert t.score_answer("garbage zz", x) < 1.0
    assert t.score_answer("S1=A,B idle=0 | balance_delay=0/1", x) < 1.0


def test_difficulty_changes():
    t = StationPacking()
    base = t.config.n_tasks
    for level in (2, 5):
        t.config.set_level(level)
        assert t.config.n_tasks > base


def test_all_levels():
    t = StationPacking()
    for level in (0, 1, 2, 3, 4, 5, 6):
        t.config.set_level(level)
        for _ in range(5):
            x = t.generate_example()
            assert t.score_answer(x.answer, x) == 1.0
            ball = Fraction(x.metadata.ball)
            assert 0 <= ball <= 1, x.metadata.ball
            assert all(idle >= 0 for idle in x.metadata.idles)


def test_constructive_consistency():
    random.seed(7)
    t = StationPacking()
    for _ in range(20):
        x = t.generate_example()
        durs = [int(x.metadata.durs[chr(64 + i)]) for i in range(1, x.metadata.n + 1)]
        pred = {
            i: [ord(p) - 64 for p in x.metadata.pred_of[chr(64 + i)]]
            for i in range(1, x.metadata.n + 1)
        }
        ct = int(x.metadata.ct)
        n = int(x.metadata.n)
        stations, idles, ball, pw, order = _solve(n, durs, pred, ct)
        assert [[chr(64 + i) for i in st] for st in stations] == x.metadata.stations
        assert [int(y) for y in idles] == list(x.metadata.idles)
        assert str(ball) == x.metadata.ball
