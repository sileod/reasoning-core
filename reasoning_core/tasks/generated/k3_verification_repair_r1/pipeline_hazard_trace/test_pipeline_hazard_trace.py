import importlib

from reasoning_core.template import Entry

mod = importlib.import_module(
    "reasoning_core.tasks.generated.k3_verification_repair_r1"
    ".pipeline_hazard_trace.pipeline_hazard_trace"
)


def _make(level=0, count=None):
    cfg = mod.PipelineHazardConfig()
    cfg.set_level(level)
    if count is not None:
        cfg.count = count
    return mod.PipelineHazardTraceTask(config=cfg)


def test_summary_one_line():
    s = mod.PipelineHazardTraceTask.summary
    assert isinstance(s, str) and s.strip() == s and "\n" not in s


def test_answer_is_nonneg_int():
    task = _make(count=5)
    ex = task.generate_example()
    assert int(ex.answer) >= 0


def test_formula_matches_cyclewise():
    import random as _r
    _r.seed(1)
    for _ in range(200):
        instrs = []
        for _ in range(8):
            cls = _r.choice(["alu", "alu", "ld", "slow"])
            if cls == "ld":
                instrs.append(("ld", _r.randrange(4), [_r.randrange(4)], cls))
            else:
                instrs.append((cls, _r.randrange(4),
                               [_r.randrange(4), _r.randrange(4)], cls))
        pairs = [(d, s, c) for (op, d, s, c) in instrs]
        c1, t1 = mod._schedule_formula(pairs)
        c2, t2 = mod._schedule_cyclewise(pairs)
        assert c1 == c2 and t1 == t2
        assert all(b >= a for a, b in zip(c1, c1[1:])) or len(c1) == 1


def test_gold_scores_one():
    task = _make(level=3)
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = _make(level=1)
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("abc", ex) == 0.0
    assert task.score_answer("import x", ex) == 0.0


def test_metadata_json_serializable():
    import json
    task = _make(level=2)
    ex = task.generate_example()
    json.dumps(dict(ex.metadata))
    assert isinstance(ex, Entry)


def test_difficulty_changes_config():
    cfg = mod.PipelineHazardConfig()
    c0 = cfg.count
    cfg.set_level(5)
    assert cfg.count > c0
