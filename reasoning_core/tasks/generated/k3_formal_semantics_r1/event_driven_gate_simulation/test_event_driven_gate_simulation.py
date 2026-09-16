import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_generates_and_scores():
    from event_driven_gate_simulation import (
        EventDrivenGateSimulation, EventDrivenGateSimulationV2Config,
    )
    random.seed(2302342651)
    cfg = EventDrivenGateSimulationV2Config()
    task = EventDrivenGateSimulation(config=cfg)
    for _ in range(40):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer('', ex) == 0.0
        assert task.score_answer('garbage', ex) == 0.0
        prompt = task.render_prompt(ex.metadata)
        assert 'v@t' in prompt
        assert ';' in ex.answer


def test_difficulty_changes():
    from event_driven_gate_simulation import EventDrivenGateSimulationV2Config
    c0 = EventDrivenGateSimulationV2Config()
    c0.apply_difficulty(0)
    c6 = EventDrivenGateSimulationV2Config()
    c6.apply_difficulty(6)
    assert c6.n_gates > c0.n_gates


def test_levels_generate():
    from event_driven_gate_simulation import EventDrivenGateSimulation
    for lvl in (0, 3, 6):
        task = EventDrivenGateSimulation(_level=lvl)
        task.config.set_level(lvl)
        for _ in range(12):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
