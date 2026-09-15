"""What the backlog owes, derived from the archive, the package and the plans."""
from pathlib import Path

import pytest
import yaml

from reasoning_core.task_search import backlog, cli


def _repo(root, *, tasks=(), plans=(), archives=()):
    """A repository with just the three directories the backlog reads."""
    task_root = root / "reasoning_core" / "tasks" / "generated" / "wave1"
    task_root.mkdir(parents=True)
    for name in tasks:
        (task_root / f"{name}.py").write_text(
            "from reasoning_core.template import Task\n\n\n"
            f"class Whatever(Task):\n    task_name = {name!r}\n"
            '    summary = "does a thing"\n')
    plan_root = root / "reasoning_core" / "task_search" / "plans"
    plan_root.mkdir(parents=True)
    for plan_name, ideas in plans:
        (plan_root / f"{plan_name}.yaml").write_text(yaml.safe_dump(
            {"name": plan_name,
             "trials": [{"id": f"P{index:03d}v1", "idea": idea,
                         "owned_path": f"reasoning_core/tasks/generated/{plan_name}/x"}
                        for index, idea in enumerate(ideas, start=1)]}))
    archive_root = root / "reasoning_core" / "task_search" / "proposals" / "archive"
    archive_root.mkdir(parents=True)
    for wave_name, names in archives:
        (archive_root / f"{wave_name}.yaml").write_text(yaml.safe_dump(
            {"kind": "sft_task_proposals", "name": wave_name,
             "proposals": [{"id": f"P{index:03d}", "name": name,
                            "summary": f"a task about {name}"}
                           for index, name in enumerate(names, start=1)]}))
    return root


@pytest.mark.parametrize("proposed, built", [
    # _snake breaks before every capital, so a proposal written lowercase and the task
    # that implements it disagree about underscores and about nothing else.
    ("BTreePromotedKey", "b_tree_promoted_key"),
    ("MVCCVisibility", "m_v_c_c_visibility"),
    ("LL1PredictiveParsing", "l_l1_predictive_parsing"),
    ("graph_coloring", "graph_coloring"),
])
def test_a_renamed_implementation_still_matches_its_proposal(proposed, built):
    assert backlog.comparison_key(proposed) == backlog.comparison_key(built)


def test_ideas_that_differ_by_more_than_underscores_do_not_match():
    assert (backlog.comparison_key("window_function")
            != backlog.comparison_key("window_function_execution"))


def test_a_proposal_with_a_task_is_not_owed(tmp_path):
    root = _repo(tmp_path, tasks=["b_tree_promoted_key"],
                 archives=[("w", ["BTreePromotedKey", "minimal_unsat_core"])])
    assert [row.name for row in backlog.pending(root)] == ["minimal_unsat_core"]


def test_attempts_are_counted_in_trials_across_every_plan(tmp_path):
    root = _repo(tmp_path, archives=[("w", ["minimal_unsat_core"])], plans=[
        ("wave1", ["minimal_unsat_core_v1 (draw 1 of 2)",
                   "minimal_unsat_core_v2 (draw 2 of 2)"]),
        ("wave2", ["minimal_unsat_core (draw 1 of 1)"])])
    assert backlog.attempted(root)[backlog.comparison_key("minimal_unsat_core")] == 3
    assert [row.attempts for row in backlog.pending(root)] == [3]


def test_an_idea_out_of_attempts_stops_being_offered(tmp_path):
    root = _repo(tmp_path, archives=[("w", ["minimal_unsat_core"])],
                 plans=[("wave1", ["minimal_unsat_core (draw 1 of 1)"])])
    assert len(backlog.pending(root, max_attempts=None)) == 1
    assert len(backlog.pending(root, max_attempts=2)) == 1
    assert backlog.pending(root, max_attempts=1) == []


def test_a_file_that_is_not_a_proposal_wave_is_not_a_backlog(tmp_path):
    root = _repo(tmp_path, archives=[("w", ["minimal_unsat_core"])])
    archive = root / "reasoning_core" / "task_search" / "proposals" / "archive"
    (archive / "notes.yaml").write_text(yaml.safe_dump({"kind": "something_else"}))
    (archive / "broken.yaml").write_text("{[not yaml")
    assert [row.name for row in backlog.pending(root)] == ["minimal_unsat_core"]


def test_plan_skipping_implemented_leaves_the_archive_alone(tmp_path, monkeypatch, capsys):
    root = _repo(tmp_path, tasks=["already_built"],
                 archives=[("w", ["already_built", "still_owed"])])
    archive = (root / "reasoning_core" / "task_search" / "proposals"
               / "archive" / "w.yaml")
    before = archive.read_text()
    built = {}

    monkeypatch.setattr(cli, "_repo_root", lambda *args: root)
    monkeypatch.setattr(cli.subprocess, "check_output", lambda *args, **kwargs: "abc123\n")
    monkeypatch.setattr("reasoning_core.task_search.plan_builder.write_plan",
                        lambda path, plan: built.update(plan))
    cli.main(["plan", str(archive), "--name", "w_r1", "--skip-implemented"])

    assert [trial["idea"] for trial in built["trials"]] == ["still_owed (draw 1 of 1)"]
    assert archive.read_text() == before
    assert "1 of 2 proposals already implemented" in capsys.readouterr().out


def test_planning_a_wave_that_owes_nothing_is_refused(tmp_path, monkeypatch):
    root = _repo(tmp_path, tasks=["already_built"], archives=[("w", ["already_built"])])
    archive = (root / "reasoning_core" / "task_search" / "proposals"
               / "archive" / "w.yaml")
    monkeypatch.setattr(cli, "_repo_root", lambda *args: root)
    with pytest.raises(SystemExit) as error:
        cli.main(["plan", str(archive), "--name", "w_r1", "--skip-implemented"])
    assert "nothing to plan" in str(error.value)


@pytest.mark.parametrize("wave, expected", [
    ("k3_reusable-operations", "k3_reusable_operations_r1"),
    ("UNBUILT", "unbuilt_r1"),
    ("manual_high_value_80", "manual_high_value_80_r1"),
])
def test_a_plan_name_is_an_importable_identifier(wave, expected):
    name = backlog.plan_name(wave, 1)
    assert name == expected and name.isidentifier()


def test_rounds_skip_the_plans_a_wave_already_has(tmp_path):
    root = _repo(tmp_path, plans=[("w_r1", ["a"]), ("w_r2", ["b"])])
    assert backlog.next_round(root, "w") == 3
    assert backlog.next_round(root, "other") == 1


def test_a_landed_task_covers_its_proposal_under_whatever_name_it_chose(tmp_path):
    """A landed task is named by the module the implementor wrote, not by the proposal
    that asked for it: regular_expression_derivative shipped as reg_exp_derivative. Matched
    on names alone the proposal stayed owed, so the pipeline would rebuild it every night
    against a task that already exists."""
    module = (tmp_path / "reasoning_core" / "tasks" / "generated"
              / "k3_systematic_generalization_r1" / "reg_exp_derivative")
    module.mkdir(parents=True)
    (module / "reg_exp_derivative.py").write_text(
        "TASK_META = {'hypothesis': 'P001', 'idea': 'regular_expression_derivative'}\n"
        "class RegExpDerivative(Task):\n    pass\n")
    wave = {"name": "k3_systematic-generalization",
            "proposals": [{"id": "P001", "name": "regular_expression_derivative",
                           "summary": "s"},
                          {"id": "P002", "name": "something_else", "summary": "s"}]}

    owed = [name for _, name, _ in backlog.unimplemented(wave, tmp_path)]

    assert owed == ["something_else"], "a renamed landed task left its proposal owed"


def test_a_plan_whose_trials_never_ran_does_not_spend_the_idea_s_budget(tmp_path):
    """The failure this cost six days to find. A wave is planned, the service is killed
    before the run -- restart, quota wall, interrupt -- and the plan stays on disk claiming
    three trials that never launched. Counted as attempts they retire the idea, and with
    every idea retired the service reports `0 proposals owed` four times an hour while the
    archive is full. Nothing is broken loudly enough to look at."""
    _repo(tmp_path, plans=[("brief_r1", ["owed_idea", "owed_idea", "owed_idea"])],
          archives=[("brief", ["owed_idea"])])
    backlog.record_outcomes(tmp_path, "brief_r1", {"P001v1": "harness_failed"})

    counts = backlog.attempted(tmp_path)

    assert counts[backlog.comparison_key("owed_idea")] == 1, (
        "only the trial that produced an outcome was actually spent")
    assert [row.name for row in backlog.pending(tmp_path, max_attempts=3)] == ["owed_idea"]


def test_a_plan_from_before_outcomes_were_recorded_still_counts_every_trial(tmp_path):
    """Plans predating the record have no record, and an empty one would mean the opposite
    of a missing one. Reading a missing record as `nothing ran` would reopen every idea the
    pipeline has ever tried and failed, which is a worse failure than the one being fixed.
    """
    _repo(tmp_path, plans=[("brief_r1", ["tired_idea", "tired_idea", "tired_idea"])],
          archives=[("brief", ["tired_idea"])])

    assert backlog.attempted(tmp_path)[backlog.comparison_key("tired_idea")] == 3
    assert backlog.pending(tmp_path, max_attempts=3) == []


def test_outcomes_merge_across_runs_rather_than_replacing(tmp_path):
    """A plan can be run more than once and in pieces -- a retry queue, a resumed wave --
    and what a later run does not cover was still spent by an earlier one."""
    (tmp_path / "reasoning_core" / "task_search" / "plans").mkdir(parents=True)

    backlog.record_outcomes(tmp_path, "brief_r1", {"P001v1": "success"})
    merged = backlog.record_outcomes(tmp_path, "brief_r1", {"P002v1": "validation_failed"})

    assert merged == {"P001v1": "success", "P002v1": "validation_failed"}
    assert backlog.outcomes(tmp_path, "brief_r1") == {"P001v1", "P002v1"}


def test_the_outcomes_record_is_not_mistaken_for_a_plan(tmp_path):
    """`attempted` globs `*.yaml` in the plans directory and `next_round` globs
    `<wave>_r*.yaml` there. A sibling `brief_r1.outcomes.yaml` would be read as a plan and
    would take round 1's number with it, so the record lives in its own directory."""
    _repo(tmp_path, plans=[("brief_r1", ["an_idea"])], archives=[("brief", ["an_idea"])])
    backlog.record_outcomes(tmp_path, "brief_r1", {"P001v1": "success"})

    plans = sorted(path.name for path in
                   (tmp_path / "reasoning_core" / "task_search" / "plans").glob("*.yaml"))

    assert plans == ["brief_r1.yaml"], f"the record was left where plans are read: {plans}"
    assert backlog.next_round(tmp_path, "brief") == 2
