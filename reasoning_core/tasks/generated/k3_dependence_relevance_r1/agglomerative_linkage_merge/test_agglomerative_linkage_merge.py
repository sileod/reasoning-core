import importlib.util
from fractions import Fraction
from pathlib import Path

_HERE = Path(__file__).parent
_SPEC = importlib.util.spec_from_file_location(
    "agglomerative_linkage_merge",
    _HERE / "agglomerative_linkage_merge.py",
)
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)

AggloConfig = _MOD.AggloConfig
AgglomerativeLinkageMerge = _MOD.AgglomerativeLinkageMerge


def test_summary_and_design():
    t = AgglomerativeLinkageMerge
    assert "merge" in t.summary
    assert t.design_choice.startswith("Answer as a list of merge tuples")


def _gen(lvl):
    t = AgglomerativeLinkageMerge()
    cfg = AggloConfig()
    cfg.set_level(lvl)
    t.config = cfg
    return t.generate_entry()


def test_generate_and_score():
    for lvl in range(7):
        e = _gen(lvl)
        t = AgglomerativeLinkageMerge()
        cfg = AggloConfig()
        cfg.set_level(lvl)
        t.config = cfg
        assert t.score_answer(e.answer, e) == 1.0
        assert t.score_answer("garbage", e) == 0.0
        assert t.score_answer("", e) == 0.0


def test_answer_format():
    e = _gen(1)
    assert e.answer.startswith("[")
    assert e.answer.endswith("]")
    import ast
    parsed = ast.literal_eval(e.answer)
    assert len(parsed) == e.metadata["n"] - 1
    for (i, j, h) in parsed:
        assert i < j
        Fraction(h)


def test_render_smoke():
    e = _gen(0)
    t = AgglomerativeLinkageMerge()
    cfg = AggloConfig()
    cfg.set_level(0)
    t.config = cfg
    prompt = t.render_prompt(e.metadata)
    assert "distance matrix" in prompt
