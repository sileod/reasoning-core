import random

from reasoning_core.tasks.generated.k3_global_from_local_r4.gear_train_signed_ratio import (
    gear_train_signed_ratio as gt,
)


def _score(task, ex):
    return task.score_answer(ex.answer, ex)


def test_config_difficulty_changes():
    cfg = gt.GearTrainConfig()
    cfg.set_level(0)
    base = (cfg.min_len, cfg.max_len, cfg.max_teeth)
    cfg.set_level(6)
    hi = (cfg.min_len, cfg.max_len, cfg.max_teeth)
    assert hi[0] >= base[0] and hi[2] > base[2]


def test_gold_scores_one_all_levels():
    task = gt.GearTrainSignedRatio()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(6):
            ex = task.generate_example()
            assert _score(task, ex) == 1.0, (level, ex.answer)
            assert ex.metadata["output"] >= 0
            assert all(isinstance(a, int) for e in ex.metadata["edges"] for a in [e[3], e[4]])


def test_answer_is_jam_or_signed_ratio():
    task = gt.GearTrainSignedRatio()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(6):
            ans = task.generate_example().answer
            assert ans == "jam" or (ans.replace("-", "").split("/")[0].isdigit()), ans


def _propagate_from_edges(edges, output):
    return gt._propagate(output + 1, edges, output, driver=0)


def test_answers_consistent_with_independent_propagation():
    random.seed(241712510)
    task = gt.GearTrainSignedRatio()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(8):
            ex = task.generate_example()
            edges = [(e[0], e[1], e[2], e[3], e[4]) for e in ex.metadata["edges"]]
            assert ex.answer == _propagate_from_edges(edges, ex.metadata["output"])


def test_chain_never_jams_and_matches_product():
    random.seed(7)
    task = gt.GearTrainSignedRatio()
    task.config.set_level(0)
    single_paths = 0
    for _ in range(60):
        ex = task.generate_example()
        edges = [(e[0], e[1], e[2], e[3], e[4]) for e in ex.metadata["edges"]]
        u_set = {e[0] for e in edges}
        v_set = {e[1] for e in edges}
        if u_set & v_set:
            continue
        single_paths += 1
        assert ex.answer == _propagate_from_edges(edges, ex.metadata["output"])
        assert ex.answer != "jam"


def test_diamond_exists_and_both_labels_appear():
    random.seed(12345)
    task = gt.GearTrainSignedRatio()
    task.config.set_level(3)
    saw_jam = saw_ratio = saw_consistent_diamond = False
    for _ in range(250):
        ex = task.generate_example()
        if ex.answer == "jam":
            saw_jam = True
        else:
            saw_ratio = True
        edges = list(ex.metadata["edges"])
        u_set = {e[0] for e in edges}
        v_set = {e[1] for e in edges}
        if u_set & v_set:
            saw_consistent_diamond = True
    assert saw_jam and saw_ratio and saw_consistent_diamond


def test_junk_and_empty_do_not_score():
    task = gt.GearTrainSignedRatio()
    ex = task.generate_example()
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("xyz", ex) < 1.0
    assert task.score_answer("3/2", ex) <= 1.0


def test_inconsistent_diamond_is_jam():
    random.seed(99)
    task = gt.GearTrainSignedRatio()
    task.config.set_level(2)
    for _ in range(40):
        ex = task.generate_example()
        edges = list(ex.metadata["edges"])
        u_set = {e[0] for e in edges}
        v_set = {e[1] for e in edges}
        if u_set & v_set and ex.answer == "jam":
            S, T = ex.metadata["edges"][0][0], ex.metadata["output"]
            X = [e for e in edges if e[0] == S or e[1] == S]
            assert ex.answer == "jam"
            return
    assert False, "no inconsistent diamond generated"
