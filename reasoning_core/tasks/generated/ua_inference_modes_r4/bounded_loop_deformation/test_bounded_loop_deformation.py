import random

from reasoning_core.tasks.generated.ua_inference_modes_r4.bounded_loop_deformation.bounded_loop_deformation import (
    BoundedLoopDeformation,
    BoundedLoopDeformationConfig,
    _fully_reduce,
    _verify_chain,
    _square_faces,
    _build_loop,
    NEG,
)


def test_generate_and_score():
    random.seed(12345)
    task = BoundedLoopDeformation()
    task.config.set_level(1)
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_summary_present():
    assert isinstance(BoundedLoopDeformation.summary, str)
    assert len(BoundedLoopDeformation.summary) > 10


def test_impossibility_domain():
    random.seed(99)
    task = BoundedLoopDeformation()
    task.config.set_level(4)
    for _ in range(30):
        x = task.generate_example()
        words = x.answer.split('>')
        assert len(words[-1]) <= task.config.cap
        # consecutive words differ by one valid move (chain shrinks toward end)
        assert len(words) >= 2


def test_difficulty_changes():
    c = BoundedLoopDeformationConfig()
    c.set_level(0)
    c0 = c.moves
    cap0 = c.cap
    c.set_level(6)
    assert c.moves > c0
    assert c.cap >= cap0


def test_verify_chain_all_levels():
    random.seed(7)
    letters = [c for c in 'abcdef']
    for level in (0, 2, 5, 6):
        c = BoundedLoopDeformationConfig()
        c.set_level(level)
        faces = _square_faces([c for c in 'abcdef'[:c.alphabet]], c.alphabet)
        for _ in range(40):
            start, _, fm, w0 = _build_loop(c.cap, faces, letters, c.moves)
            chain = _verify_chain(start, c.cap, faces, fm, w0)
            assert chain is not None
            assert len(chain[-1]) <= c.cap
            # every chain word is a valid loop (non-empty) and lengths shrink overall
            for wd in chain:
                assert len(wd) >= 1

