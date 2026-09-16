import random

from reasoning_core.tasks.generated.k3_formal_semantics_r1.dynamic_discourse_evaluation.dynamic_discourse_evaluation import (
    DynamicDiscourseEvaluation,
    DynamicDiscourseConfig,
    _evaluate,
    parse_answer,
)


def _task():
    return DynamicDiscourseEvaluation()


def _config(level):
    c = DynamicDiscourseEvaluation().config_cls()
    c.set_level(level)
    return c


def test_gold_scores_one():
    random.seed(7)
    task = _task()
    for _ in range(80):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_junk_scores_zero():
    task = _task()
    e = task.generate_example()
    assert task.score_answer("", e) < 1.0
    assert task.score_answer("garbage", e) < 1.0
    assert task.score_answer("1,2,3", e) < 1.0


def test_answer_well_formed():
    random.seed(3)
    task = _task()
    for level in range(7):
        task.config = _config(level)
        for _ in range(60):
            e = task.generate_entry()
            vals = parse_answer(e.answer)
            roster = {int(row[0]): (row[1], row[2]) for row in e.metadata.roster}
            members = sorted(i for i in roster if roster[i][0] == e.metadata.target_kind)
            if e.metadata.accessible:
                assert sorted(vals) == vals
                assert len(vals) >= 2
                assert all(v in members for v in vals)
            else:
                assert e.answer == "none"


def test_blocked_is_never_nonempty():
    random.seed(5)
    task = _task()
    for _ in range(120):
        task.config = _config(random.randint(0, 6))
        e = task.generate_entry()
        if not e.metadata.accessible:
            assert parse_answer(e.answer) == []


def test_accessible_extends_assignment_set():
    # A top-level indefinite binds r0 to every member of its kind.
    roster = {1: ("knight", "bright"), 2: ("knight", "dim"), 3: ("dragon", "bright")}
    out = _evaluate([{}], ("exists", "r0", "knight"), roster)
    assert sorted({a["r0"] for a in out}) == [1, 2]


def test_connectives_block_export():
    roster = {1: ("knight", "bright"), 2: ("knight", "dim"), 3: ("dragon", "bright")}
    for node in (
        ("not", ("exists", "r0", "knight")),
        ("imp", ("exists", "r0", "knight"), ("testtrait", "r0", "bright")),
        ("or", ("exists", "r0", "knight"), ("exists", "r1", "dragon")),
    ):
        out = _evaluate([{}], ("seq", [node]), roster)
        assert not any("r0" in a for a in out)


def test_difficulty_changes():
    base = DynamicDiscourseConfig()
    b = (base.universe, base.stmts)
    hi = DynamicDiscourseConfig()
    hi.apply_difficulty(6)
    assert hi.universe >= b[0] and hi.stmts >= b[1]


def test_not_constant():
    random.seed(11)
    task = _task()
    answers = set()
    for _ in range(150):
        task.config = _config(random.randint(0, 6))
        e = task.generate_entry()
        answers.add(e.answer)
    assert len(answers) >= 3


def test_metadata_json_roundtrip():
    import json
    task = _task()
    e = task.generate_example()
    m = {
        "roster": e.metadata.roster,
        "asts": e.metadata.asts,
        "prose": e.metadata.prose,
        "target_kind": e.metadata.target_kind,
        "answer": e.metadata.answer,
        "accessible": e.metadata.accessible,
    }
    loaded = json.loads(json.dumps(m))
    assert loaded["answer"] == e.answer
    assert all(isinstance(row, list) for row in loaded["roster"])


def test_never_scores_literal_numbers():
    # The prompt surface numbers (first/last/largest) must never win: accessible answers
    # are never singletons, and "none" is not a number.
    random.seed(21)
    task = _task()
    for _ in range(120):
        task.config = _config(random.randint(0, 6))
        e = task.generate_entry()
        if e.metadata.accessible:
            vals = parse_answer(e.answer)
            assert len(vals) >= 2
