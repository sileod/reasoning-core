import random

from .filler_gap_licensing import (
    FillerGapLicensingV2Config,
    FillerGapLicensingV2Task,
    ISLAND_LABEL,
)


def test_all_levels_generate_and_score():
    task = FillerGapLicensingV2Task()
    for level in range(7):
        cfg = FillerGapLicensingV2Config()
        cfg.set_level(level)
        task.config = cfg
        for _ in range(40):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            assert task.score_answer("", ex) < 1.0
            assert task.score_answer("garbage here", ex) < 1.0


def test_answer_formats():
    task = FillerGapLicensingV2Task()
    cfg = FillerGapLicensingV2Config()
    cfg.set_level(6)
    task.config = cfg
    seen = set()
    for _ in range(200):
        ex = task.generate_example()
        ans = ex.answer
        seen.add(ans.split(":")[0])
        assert ans in (
            "linked: " + "; ".join(ex.metadata["fillers"]),
            "licensed: " + ex.metadata["fillers"][0],
        ) or ans.startswith("island: ")
    assert "island" in seen


def test_level0_no_multi_or_parasitic():
    task = FillerGapLicensingV2Task()
    cfg = FillerGapLicensingV2Config()
    cfg.set_level(0)
    task.config = cfg
    for _ in range(60):
        ex = task.generate_example()
        assert ex.metadata["case"] not in ("multi", "parasitic")


def test_level0_balanced_clean_and_island():
    task = FillerGapLicensingV2Task()
    cfg = FillerGapLicensingV2Config()
    cfg.set_level(0)
    task.config = cfg
    clean = island = 0
    for _ in range(320):
        ex = task.generate_example()
        if ex.metadata["case"] == "clean":
            clean += 1
        else:
            island += 1
    assert clean >= 40, clean
    assert island >= 40, island


def test_multi_orders_by_superiority():
    task = FillerGapLicensingV2Task()
    cfg = FillerGapLicensingV2Config()
    cfg.set_level(6)
    task.config = cfg
    for _ in range(300):
        ex = task.generate_example()
        if ex.metadata["case"] == "multi":
            assert ex.answer == "linked: " + "; ".join(ex.metadata["fillers"])


def test_parasitic_only_high_level():
    task = FillerGapLicensingV2Task()
    for level in (0, 1, 2, 3):
        cfg = FillerGapLicensingV2Config()
        cfg.set_level(level)
        task.config = cfg
        for _ in range(60):
            assert task.generate_example().metadata["case"] != "parasitic"



def test_reproducible_under_fixed_seed():
    random.seed(123)
    task = FillerGapLicensingV2Task()
    cfg = FillerGapLicensingV2Config()
    cfg.set_level(3)
    task.config = cfg
    a = [task.generate_example().answer for _ in range(30)]
    random.seed(123)
    task = FillerGapLicensingV2Task()
    cfg = FillerGapLicensingV2Config()
    cfg.set_level(3)
    task.config = cfg
    b = [task.generate_example().answer for _ in range(30)]
    assert a == b
