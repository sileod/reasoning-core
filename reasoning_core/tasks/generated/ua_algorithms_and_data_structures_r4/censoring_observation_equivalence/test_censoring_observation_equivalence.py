import json
import random

from reasoning_core.template import Entry

from reasoning_core.tasks.generated import ua_algorithms_and_data_structures_r4  # noqa
from reasoning_core.tasks.generated.ua_algorithms_and_data_structures_r4 import \
    censoring_observation_equivalence  # noqa
from reasoning_core.tasks.generated.ua_algorithms_and_data_structures_r4.censoring_observation_equivalence.censoring_observation_equivalence import \
    CensoringObservationEquivalence


def _task(level=0):
    cfg = CensoringObservationEquivalence.config_cls()
    cfg.set_level(level)
    return CensoringObservationEquivalence(config=cfg)


def test_summary_present():
    s = CensoringObservationEquivalence.summary
    assert isinstance(s, str) and s.strip()
    assert "\n" not in s


def test_generate_and_score():
    t = _task()
    x = t.generate_example()
    assert isinstance(x, Entry)
    assert x.answer in ("YES", "NO")
    assert t.score_answer(x.answer, x) == 1
    assert t.score_answer("", x) == 0
    assert t.score_answer("maybe", x) == 0


def test_metadata_json():
    t = _task()
    x = t.generate_example()
    json.dumps(dict(x.metadata))


def test_label_balance():
    t = _task()
    counts = {"YES": 0, "NO": 0}
    for _ in range(60):
        x = t.generate_example()
        counts[x.answer] += 1
    assert counts["YES"] >= 15 and counts["NO"] >= 15


def test_evidence_consistency_all_levels():
    for level in range(0, 7):
        t = _task(level)
        for _ in range(10):
            x = t.generate_example()
            assert x.answer in ("YES", "NO")
            assert t.score_answer(x.answer, x) == 1
            md = json.loads(json.dumps(dict(x.metadata)))
            assert md["n"] == t.config.length
            assert md["maxval"] == t.config.maxval


def test_deterministic_under_seed():
    random.seed(123)
    t1 = _task()
    a = [t1.generate_example().answer for _ in range(20)]
    random.seed(123)
    t2 = _task()
    b = [t2.generate_example().answer for _ in range(20)]
    assert a == b
