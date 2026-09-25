from reasoning_core.tasks.generated.ua_dynamic_structures_r4.epistemic_event_product_update.epistemic_event_product_update import (
    EpistemicEventProductUpdate,
)


def test_summary_and_design():
    t = EpistemicEventProductUpdate()
    assert isinstance(t.summary, str) and t.summary.strip()
    assert "agent" in t.design_choice


def test_generate_and_score_all_levels():
    for level in (0, 2, 5, 6):
        t = EpistemicEventProductUpdate()
        t.config.set_level(level)
        for _ in range(5):
            ex = t.generate_example()
            assert t.score_answer(ex.answer, ex) == 1.0
            assert ex.prompt
            for junk in ("", "reajrjrje9595!", "import fakemodule"):
                assert t.score_answer(junk, ex) == 0.0


def test_answer_domain():
    t = EpistemicEventProductUpdate()
    t.config.set_level(3)
    ex = t.generate_example()
    agents = set(ex.metadata["agents"])
    for seg in ex.answer.split("|"):
        seg = seg.strip()
        if seg == "-":
            continue
        for name in seg.split(","):
            assert name in agents
