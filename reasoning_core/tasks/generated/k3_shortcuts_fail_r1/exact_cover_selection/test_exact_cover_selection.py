from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.exact_cover_selection.exact_cover_selection import (
    ExactCoverSelection,
    ExactCoverSelectionV1Config,
    TASK_META,
    _all_covers,
)


def _entry(task, level=None):
    if level is not None:
        task.config.set_level(level)
    return task.generate_example()


def test_summary_and_design_choice():
    assert "NONE" in ExactCoverSelection.summary
    assert "sorted chosen labels" in ExactCoverSelection.summary
    assert "0-1 matrix" in ExactCoverSelection.design_choice


def test_task_meta_present():
    assert TASK_META["hypothesis"] == "P002"
    assert TASK_META["idea"].startswith("exact_cover_selection")


def test_difficulty_changes_config():
    task = ExactCoverSelection()
    base_u = task.config.universe_size
    base_n = task.config.n_subsets
    task.config.set_level(3)
    assert task.config.universe_size > base_u or task.config.n_subsets > base_n
    task.config.set_level(0)
    assert task.config.universe_size == ExactCoverSelectionV1Config.universe_size


def test_gold_scores_1_all_levels():
    task = ExactCoverSelection()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(5):
            e = task.generate_example()
            assert task.score_answer(e.answer, e) == 1.0


def test_both_labels_appear():
    task = ExactCoverSelection()
    labels = set()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(30):
            e = task.generate_example()
            labels.add(e.answer)
    assert "NONE" in labels
    assert any(a != "NONE" for a in labels)


def test_balance_not_constant():
    task = ExactCoverSelection()
    task.config.set_level(0)
    solvable = 0
    total = 0
    for _ in range(300):
        e = task.generate_example()
        total += 1
        if e.answer != "NONE":
            solvable += 1
    frac = solvable / total
    assert 0.25 < frac < 0.75, frac


def test_junk_scores_0():
    task = ExactCoverSelection()
    for level in [0, 3, 6]:
        task.config.set_level(level)
        e = task.generate_example()
        assert task.score_answer("", e) == 0.0
        assert task.score_answer("garbage", e) < 1.0


def test_gold_accuracy_with_external_check():
    """Recompute the cover with an independent verifier matching metadata."""
    task = ExactCoverSelection()
    for level in [0, 3, 6]:
        task.config.set_level(level)
        e = task.generate_example()
        subsets = e.metadata["subsets"]
        u = e.metadata["universe_size"]
        covers = _all_covers(subsets, u)
        if e.answer == "NONE":
            assert not covers
        else:
            chosen = [int(x) for x in e.answer.split(",")]
            assert sorted(chosen) == sorted(min(covers, key=tuple))
            covered = set()
            for i in chosen:
                assert covered.isdisjoint(subsets[i])
                covered |= set(subsets[i])
            assert covered == set(range(u))


def test_metadata_json_serializable():
    import json
    task = ExactCoverSelection()
    for level in [0, 6]:
        task.config.set_level(level)
        e = task.generate_example()
        json.dumps(e.metadata)
        json.dumps(e.answer)


def test_nonminimal_cover_scores_0():
    """An exact cover that is not lexicographically smallest must score 0."""
    task = ExactCoverSelection()
    task.config.set_level(0)
    e = task.generate_example()
    subsets = e.metadata["subsets"]
    u = e.metadata["universe_size"]
    covers = _all_covers(subsets, u)
    if len(covers) < 2:
        return
    best = min(covers, key=tuple)
    other = next(c for c in covers if c != best)
    ans = ",".join(str(i) for i in sorted(other))
    assert task.score_answer(ans, e) == 0.0


def test_out_of_range_and_duplicate_scores_0():
    task = ExactCoverSelection()
    task.config.set_level(0)
    e = task.generate_example()
    assert task.score_answer("-1,0", e) == 0.0
    assert task.score_answer("0,0", e) == 0.0
    assert task.score_answer("999", e) == 0.0


def test_prompt_mentions_lexmin_and_none():
    task = ExactCoverSelection()
    task.config.set_level(0)
    e = task.generate_example()
    p = task.render_prompt(e.metadata)
    assert "lexicographically" in p
    assert "NONE" in p
    for i, s in enumerate(e.metadata["subsets"]):
        assert f"row {i}: {s}" in p

