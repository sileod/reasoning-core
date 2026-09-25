from reasoning_core.tasks.generated.ua_scientific_reasoning_r5.path_intervention_world_consistency.path_intervention_world_consistency import (
    PathInterventionWorldConsistency,
    ANS_IDENT,
    ANS_WITNESS,
    has_recanting_witness,
)


def test_generate_render_score_roundtrip():
    task = PathInterventionWorldConsistency()
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0
    assert task.render_prompt(ex.metadata)
    assert ex.answer in (ANS_IDENT, ANS_WITNESS)


def test_junk_scores_zero():
    task = PathInterventionWorldConsistency()
    ex = task.generate_example()
    assert task.score_answer("garbage", ex) == 0.0
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("  ", ex) == 0.0
    assert task.score_answer("identifiable\nrecanting_witness", ex) == 0.0


def test_difficulty_changes_config():
    task = PathInterventionWorldConsistency()
    c0 = task.config.chain_len
    task.config.set_level(6)
    assert task.config.chain_len != c0 or task.config.n_branches != 1
    assert task.config.chain_len >= 1


def test_answer_matches_independent_criterion_all_levels():
    for lvl in (0, 1, 2, 3, 4, 5, 6):
        for _ in range(20):
            task = PathInterventionWorldConsistency()
            task.config.set_level(lvl)
            ex = task.generate_entry()
            nodes = ex.metadata["nodes"]
            edges = [tuple(e) for e in ex.metadata["edges"]]
            wit = has_recanting_witness(nodes, edges, "A", "Y")
            assert wit == ex.metadata["witness"]
            assert (ex.metadata["answer"] == ANS_WITNESS) == wit


def test_labels_roughly_balanced():
    task = PathInterventionWorldConsistency()
    wcount = 0
    total = 40
    for _ in range(total):
        ex = task.generate_entry()
        if ex.answer == ANS_WITNESS:
            wcount += 1
    assert 0.2 <= wcount / total <= 0.8


def test_validate():
    task = PathInterventionWorldConsistency()
    task.validate()


def test_not_task_name():
    assert "Task" not in type(PathInterventionWorldConsistency()).__name__


def test_summary_and_design_choice_literals():
    t = PathInterventionWorldConsistency
    assert isinstance(t.summary, str) and len(t.summary) > 20
    assert "two treatment nodes" in t.design_choice
    assert "shared intermediate" in t.design_choice
