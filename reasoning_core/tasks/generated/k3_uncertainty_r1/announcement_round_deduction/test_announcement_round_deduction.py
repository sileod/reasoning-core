import random

from reasoning_core.tasks.generated.k3_uncertainty_r1.announcement_round_deduction.announcement_round_deduction import (
    _simulate,
    AnnouncementRoundDeduction,
)


def _make(level):
    t = AnnouncementRoundDeduction(config=None)
    t.config.set_level(level)
    return t


def test_gold_answer_scores_one():
    random.seed(7)
    for level in (0, 2, 5, 6):
        t = _make(level)
        for _ in range(20):
            ex = t.generate_example()
            assert t.score_answer(ex.answer, ex) == 1.0


def test_wrong_answers_score_zero():
    random.seed(11)
    t = _make(2)
    checked = 0
    for _ in range(40):
        ex = t.generate_example()
        g = ex.metadata["agent"]
        r = ex.metadata["round"]
        assert _parse(ex.answer) == (g, r)
        for cand in ("", "A0", "foo", "A9 on round 3", "A0 on round"):
            assert t.score_answer(cand, ex) == 0.0, (cand, ex.answer)
            checked += 1
        # a round that is definitely wrong
        tall = (r + 1) % (t.config.num_agents + 1) or 1
        assert t.score_answer(f"A{g} on round {tall}", ex) == 0.0 if tall != r else True
    assert checked > 0


def _parse(text):
    import re as _re
    m = _re.fullmatch(r"A(\d+) on round (\d+)", str(text).strip())
    return None if not m else (int(m.group(1)), int(m.group(2)))


def test_simulation_matches_metadata():
    random.seed(3)
    for level in (0, 1, 2, 3, 4, 5, 6):
        t = _make(level)
        for _ in range(50):
            ex = t.generate_example()
            n = ex.metadata["num_agents"]
            world = tuple(ex.metadata["world"])
            assert all(v != 0 for v in world) or any(v for v in world)
            assert any(v == 1 for v in world)
            res = _simulate(n, world, n)
            assert res is not None
            agent, rnd = res
            assert (agent, rnd) == (ex.metadata["agent"], ex.metadata["round"])


def test_difficulty_increases_size():
    sizes = [_make(lv).config.num_agents for lv in range(7)]
    assert sizes[0] < sizes[-1]
    assert all(b >= a for a, b in zip(sizes, sizes[1:]))  # monotonic non-decreasing


def test_rounds_track_number_of_reds():
    # For the "at least one Red" muddy-children public fact, the first deduction round
    # equals the number of Red hats, and the deducing agents are exactly the Red ones.
    random.seed(5)
    t = _make(3)
    for _ in range(60):
        ex = t.generate_example()
        n = ex.metadata["num_agents"]
        world = ex.metadata["world"]
        reds = [i for i, v in enumerate(world) if v == 1]
        assert ex.metadata["round"] == len(reds)
        assert ex.metadata["agent"] == min(reds)
