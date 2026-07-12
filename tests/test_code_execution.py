import pytest

from reasoning_core.tasks import code_execution as code_tasks
from reasoning_core.tasks.code_execution import (
    CodeRunnability,
    MesopyCodeCfg,
    RunReport,
    endpoint_probes,
    function_triviality,
    organic_mutations,
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


def test_code_runnability_emits_paired_labels(monkeypatch):
    bad = RunReport(error="NameError", args=[0])
    good = report(4, [1])
    monkeypatch.setattr(code_tasks, "runnability_pair", lambda _: ("name", (("code", bad), ("code", good))))
    task = CodeRunnability()
    problems = [task.generate(), task.generate()]

    assert {problem.answer for problem in problems} == {"OK", "NameError"}
    assert problems[0].metadata.code == problems[1].metadata.code
    assert "The answer is `OK`" in task.prompt(problems[0].metadata)
    assert all(task.score_answer(problem.answer, problem) == 1.0 for problem in problems)


def test_endpoint_probes_vary_each_annotated_argument():
    code = "def endpoint(x: int, s: str):\n    return x, s\n"
    probes = endpoint_probes(code, MesopyCodeCfg(), limit=24)

    assert len({x for x, _ in probes}) > 1
    assert len({s for _, s in probes}) > 1


def test_organic_mutations_are_local_edits_of_generated_code():
    code = (
        "def f0(x: int, s: str):\n"
        "    if x > 0:\n"
        "        return x + len(s)\n"
        "    return x\n"
        "def f1(y: int):\n"
        "    return y\n"
        "def endpoint(x: int, s: str):\n"
        "    return f0(x, s)\n"
    )
    mutations = list(organic_mutations(code))

    assert mutations
    assert all(candidate != code for _, candidate in mutations)
    assert all("def f0" in candidate and "def endpoint" in candidate for _, candidate in mutations)
