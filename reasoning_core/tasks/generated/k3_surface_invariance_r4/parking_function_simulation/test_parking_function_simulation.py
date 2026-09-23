import random

from reasoning_core.tasks.generated.k3_surface_invariance_r4.parking_function_simulation.parking_function_simulation import (
    ParkingFunctionSimulation,
)


def test_simulation_v1_answer_roundtrip():
    random.seed(42)
    task = ParkingFunctionSimulation()
    for _ in range(50):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer("", ex) < 1.0
        assert task.score_answer("junk", ex) < 1.0


def test_simulation_v1_varied_labels():
    random.seed(7)
    task = ParkingFunctionSimulation()
    parkable = nonparkable = 0
    for _ in range(60):
        ex = task.generate_example()
        if ex.metadata["requested"] == "parkable":
            if ex.answer == "yes":
                parkable += 1
            else:
                nonparkable += 1
    assert parkable > 0 and nonparkable > 0
