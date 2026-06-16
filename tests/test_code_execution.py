import pytest

from reasoning_core.tasks import code_execution as code_tasks
from reasoning_core.tasks.code_execution import (
    CodeRunnability,
    MesopyCodeCfg,
    RunReport,
    function_triviality,
    sample_problem,
)


def report(value, args):
    return RunReport(ok=True, value=repr(value), args=args, steps=10)


def test_function_triviality():
    assert function_triviality([report(3, [1]), report(3, [2])]) == "constant"
    assert function_triviality([report(1, [1, 4]), report(2, [2, 5])]) == "identity"
    assert function_triviality([report(2, [1]), report(4, [2])]) is None


def test_sample_problem_rejects_trivial_function(monkeypatch):
    cfg = MesopyCodeCfg(
        max_attempts=1,
        min_steps=0,
        trivial_accept_prob=0,
        trivial_probes=2,
    )
    monkeypatch.setattr(code_tasks, "make_code", lambda *_: "def endpoint(x): return 1")
    monkeypatch.setattr(code_tasks, "run_code", lambda *_: report(1, [0]))

    with pytest.raises(RuntimeError):
        sample_problem(cfg, want_error=False, failure_rate=0)


def test_code_runnability_has_ok_answer(monkeypatch):
    run = report(4, [2])
    monkeypatch.setattr(code_tasks, "sample_problem", lambda *args, **kwargs: ("code", run))
    task = CodeRunnability(MesopyCodeCfg(runnable_prob=1))
    problem = task.generate()

    assert problem.answer == "OK"
    assert "The answer is `OK`" in task.prompt(problem.metadata)
    assert task.score_answer("OK", problem) == 1.0
