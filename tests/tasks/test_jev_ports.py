import json

import pytest

from reasoning_core import get_task
from reasoning_core.decision import Decision, jev_request

TASKS = ["event_triggered_execution", "goal_directed_planning", "graph_navigation", "instruction_execution",
         "record_eligibility"]


@pytest.mark.parametrize("name", TASKS)
def test_validates(name):
    get_task(name).validate()


@pytest.mark.parametrize("name", TASKS)
def test_state_seed_reproduces_every_question(name):
    task = get_task(name)
    for level in range(5):
        for seed in range(8):
            request = jev_request(task, seed, level)
            assert request == jev_request(task, seed, level)
            json.dumps(request)
            for qid, q in request["questions"].items():
                x = task.generate_example(level=level, state_seed=seed, question=qid)
                assert isinstance(x.answer, Decision) and x.answer.label == q["label"]
                assert x.answer.question["instructions"] == q["instructions"]
                assert x.metadata.payload == request["state"]
