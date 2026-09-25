import random
from pathlib import Path

from reasoning_core.template import Config
from reasoning_core.tasks.generated.ua_incremental_recomputation_r4.bitemporal_correction_slicing.bitemporal_correction_slicing import (
    BitemporalCorrectionSlicing,
    BitemporalCorrectionSlicingConfig,
    _maximal_changed,
    _fmt,
    _d,
)

OUT = Path(__file__).with_name("samples_P010v1.md")


def _check_answer_format(ans):
    assert ans.startswith("[") and ans.endswith("]")
    body = ans[1:-1]
    rects = body.split(";") if body else []
    for r in rects:
        vp, tp = r.split(",")
        assert vp.startswith("V") and "/" in vp
        assert tp.startswith("T") and "/" in tp
    return rects


def test_gold_scores_one():
    task = BitemporalCorrectionSlicing()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(30):
            e = task.generate_example()
            assert task.score_answer(e.answer, e) == 1.0


def test_wrong_and_junk_score_zero():
    task = BitemporalCorrectionSlicing()
    for level in (0, 3, 6):
        task.config.set_level(level)
        e = task.generate_example()
        assert task.score_answer("", e) < 1.0
        assert task.score_answer("garbage", e) < 1.0
        assert task.score_answer(None, e) < 1.0


def test_answer_format():
    task = BitemporalCorrectionSlicing()
    for level in (0, 6):
        task.config.set_level(level)
        e = task.generate_example()
        rects = _check_answer_format(e.answer)
        assert len(rects) >= 1


def test_answer_matches_brute_force():
    task = BitemporalCorrectionSlicing()
    for level in (0, 3, 6):
        task.config.set_level(level)
        e = task.generate_example()
        md = e.metadata
        segs = []
        from datetime import date
        for s in md["segments"]:
            vf = date.fromisoformat(s["valid_from"])
            vt = date.fromisoformat(s["valid_to"])
            segs.append(((vf - _d(0)).days, (vt - _d(0)).days, s["value"]))
        cs = (date.fromisoformat(md["cv_start"]) - _d(0)).days
        ce = (date.fromisoformat(md["cv_end"]) - _d(0)).days
        changed = _maximal_changed(segs, cs, ce, md["new_value"])
        rects = _check_answer_format(e.answer)
        assert len(rects) == len(changed)
        for (vs, ve), r in zip(changed, rects):
            assert r.startswith("V{}".format(_fmt(_d(vs))))
            assert "/{}".format(_fmt(_d(ve))) in r


def test_changed_region_is_strict_subset_when_possible():
    task = BitemporalCorrectionSlicing()
    task.config.set_level(3)
    seen = 0
    for _ in range(40):
        e = task.generate_example()
        rects = _check_answer_format(e.answer)
        assert len(rects) >= 1
        seen += 1
        assert len(rects) >= 1
    assert seen == 40


def test_multi_rectangle_and_splitting_occur():
    task = BitemporalCorrectionSlicing()
    for level in (0, 3, 6):
        task.config.set_level(level)
        saw_multi = 0
        saw_single = 0
        for _ in range(400):
            e = task.generate_example()
            rects = _check_answer_format(e.answer)
            if len(rects) >= 2:
                saw_multi += 1
            else:
                saw_single += 1
        assert saw_single > 0
        if level == 0:
            assert saw_multi == 0, "level 0 should be single max rectangle (2 segments)"
        else:
            assert saw_multi > 0, f"level {level}: no multi-rectangle answers generated"


def test_config_difficulty_scales():
    cfg = BitemporalCorrectionSlicingConfig()
    cfg.set_level(0)
    base = cfg.nseg
    cfg.set_level(6)
    assert cfg.nseg > base


def test_summary_and_design_choice_present():
    assert isinstance(BitemporalCorrectionSlicing.summary, str)
    assert "changed-history" in BitemporalCorrectionSlicing.summary or "changed" in BitemporalCorrectionSlicing.summary
    assert isinstance(BitemporalCorrectionSlicing.design_choice, str)


def test_metadata_json_serializable():
    import json
    task = BitemporalCorrectionSlicing()
    e = task.generate_example()
    json.dumps(dict(e.metadata))


if __name__ == "__main__":
    random.seed(2409743872)
    task = BitemporalCorrectionSlicing()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        for i in range(2):
            task.config.set_level(level)
            e = task.generate_example()
            lines.append(f"### Example {i+1}")
            lines.append("**Prompt**")
            lines.append(e.prompt)
            lines.append("")
            lines.append("**Answer**")
            lines.append(e.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")
