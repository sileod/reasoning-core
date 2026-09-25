import random

from reasoning_core.tasks.generated.ua_multi_relation_integration_r4.polyhedral_plane_sections.polyhedral_plane_sections import PolyhedralPlaneSections
from reasoning_core.template import Entry


def test_generate_example_and_score():
    random.seed(7)
    task = PolyhedralPlaneSections()
    x = task.generate_example()
    assert isinstance(x, Entry)
    assert task.score_answer(x.answer, x) == 1.0


def test_answers_are_counts():
    random.seed(3)
    task = PolyhedralPlaneSections()
    seen = set()
    for _ in range(60):
        x = task.generate_example()
        nv = int(x.answer)
        assert nv >= 3
        assert nv == x.metadata["n_vertices"]
        seen.add(nv)
    assert len(seen) >= 2


def test_modes_and_solids_varied():
    random.seed(13)
    task = PolyhedralPlaneSections()
    solids = set()
    modes = set()
    for _ in range(80):
        x = task.generate_example()
        solids.add(x.metadata["solid"])
        modes.add(x.metadata["mode"])
    assert len(solids) >= 2
    assert len(modes) >= 2


def test_prompt_deterministic_answer():
    random.seed(17)
    task = PolyhedralPlaneSections()
    for _ in range(20):
        x = task.generate_example()
        prompt = task.render_prompt(x.metadata)
        assert "vertices" in prompt
        assert "=" in prompt


def test_garbage_scores_zero():
    random.seed(9)
    task = PolyhedralPlaneSections()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("abc", x) == 0.0


def test_metadata_json_serializable():
    import json
    random.seed(11)
    task = PolyhedralPlaneSections()
    x = task.generate_example()
    json.dumps(x.metadata)


def test_all_levels_generate():
    random.seed(5)
    for lvl in (0, 2, 6):
        task = PolyhedralPlaneSections()
        task.config.set_level(lvl)
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0
