import random

from reasoning_core.tasks.generated.ua_language_implementation_r4.piece_table_provenance.piece_table_provenance import (
    _exact_provenance,
    _parse_answer,
    PieceTableProvenance,
    score_answer,
)


def test_roundtrip_scores_one():
    task = PieceTableProvenance()
    for _ in range(50):
        ex = task.generate_example()
        assert score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = PieceTableProvenance()
    for _ in range(20):
        ex = task.generate_example()
        assert score_answer("", ex) < 1.0
        assert score_answer("garbage", ex) < 1.0
        assert score_answer("original", ex) < 1.0


def test_answer_reconstructs_character():
    task = PieceTableProvenance()
    for _ in range(30):
        ex = task.generate_example()
        m = ex.metadata
        buf, off = ex.answer.split(':')
        off = int(off)
        final, prov = _exact_provenance(m['original'], [tuple(e) for e in m['edits']])
        if buf == 'original':
            ch = m['original'][off]
        else:
            app = []
            for e in m['edits']:
                if e[3]:
                    app.extend(e[3])
            ch = app[off]
        assert ch == final[m['query']]


def test_answer_balance():
    task = PieceTableProvenance()
    counts = {'original': 0, 'added': 0}
    for _ in range(200):
        ex = task.generate_example()
        buf, _ = ex.answer.split(':')
        counts[buf] += 1
    frac = counts['original'] / (counts['original'] + counts['added'])
    assert 0.25 < frac < 0.75


def test_parse_answer():
    assert _parse_answer("original:3") == ("original", 3)
    assert _parse_answer("added:0") == ("added", 0)
    assert _parse_answer("nope:1") is None
    assert _parse_answer("original:x") is None
    assert _parse_answer("original") is None


def test_difficulty_changes_config():
    task = PieceTableProvenance()
    task.config.set_level(0)
    l0 = task.config.edits
    task.config.set_level(6)
    l6 = task.config.edits
    assert l6 > l0
