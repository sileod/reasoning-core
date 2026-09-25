import random

from reasoning_core.tasks.generated.ua_planning_backtracking_r4.rigidity_brace_design.rigidity_brace_design import (
    rigidity_brace_design,
)
def test_generate_and_score():
    task = rigidity_brace_design()
    task.config.set_level(3)
    random.seed(42)
    seen = set()
    for _ in range(60):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0
        assert entry.answer in ("impossible", "none") or "-" in entry.answer
        seen.add(entry.answer)
    assert len(seen) > 5


def test_score_rejects_junk():
    task = rigidity_brace_design()
    task.config.set_level(0)
    random.seed(1)
    entry = task.generate_example()
    assert task.score_answer("", entry) < 1.0
    assert task.score_answer("garbage", entry) < 1.0
    assert task.score_answer("0-1" if entry.answer != "0-1" else "1-2", entry) < 1.0


def test_all_levels():
    task = rigidity_brace_design()
    for level in range(7):
        task.config.set_level(level)
        random.seed(level * 7 + 3)
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0
        assert len(task.render_prompt(entry.metadata)) < 1500


def test_gold_is_consistent_with_completion():
    task = rigidity_brace_design()
    task.config.set_level(4)
    random.seed(99)
    counts = {"impossible": 0, "none": 0, "bars": 0}
    for _ in range(40):
        entry = task.generate_example()
        m = entry.metadata
        if entry.answer == "impossible":
            counts["impossible"] += 1
        elif entry.answer == "none":
            counts["none"] += 1
        else:
            counts["bars"] += 1
    assert counts["bars"] > 5
    assert counts["impossible"] > 0
    # 'impossible'/'none' must not dominate the distribution (gameability guard).
    assert counts["impossible"] + counts["none"] <= 60


def test_gold_completes_the_target_subspace():
    task = rigidity_brace_design()
    task.config.set_level(4)
    random.seed(7)
    from reasoning_core.tasks.generated.ua_planning_backtracking_r4.rigidity_brace_design.rigidity_brace_design import (
        _rigidity_matrix,
        _nullspace_basis,
    )
    import numpy as np
    mech = rigid = 0
    for _ in range(60):
        entry = task.generate_example()
        m = entry.metadata
        joint_ids = [int(k) for k in m["joints"]]
        coords = {int(k): tuple(v) for k, v in m["joints"].items()}
        grounded = set(int(g) for g in m["grounded"])
        free = sorted(j for j in joint_ids if j not in grounded)
        if entry.answer == "impossible":
            continue
        added = [(int(x) for x in part.split("-")) for part in entry.answer.split(",")]
        added = [(i, j) for i, j in added]
        final = sorted(set(tuple(b) for b in m["current_bars"]) | set(added))
        null = _nullspace_basis(_rigidity_matrix(final, joint_ids, coords, grounded))
        dim = null.shape[1]
        if m["rigid_target"]:
            rigid += 1
            assert dim == 0, "rigid target must have zero mechanism freedom"
        else:
            mech += 1
            assert dim == 1, "rotation-freedom target must have exactly one degree of freedom"
            # The single freedom must be the pivot rotating about the fixed anchor:
            # velocity at pivot = perpendicular to the pivot-anchor vector, others zero.
            px, py = coords[m["pivot"]]
            ax, ay = coords[m["anchor_a"]]
            vec = np.array([-(py - ay), (px - ax)])
            v = null[:, 0]
            vidx = free.index(m["pivot"]) * 2
            piv_vel = v[vidx:vidx + 2]
            others_zero = all(
                abs(val) < 1e-8 for k, val in enumerate(v)
                if k // 2 != free.index(m["pivot"]))
            assert others_zero, "non-pivot joints must not move"
            # velocity proportional (in sign) to the rotation direction
            assert abs(np.dot(piv_vel, vec)) > 0.9 * np.linalg.norm(vec)
    assert mech >= 5 and rigid >= 2


