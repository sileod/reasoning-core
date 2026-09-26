import io
import json

import pytest

from reasoning_core.task_search import signals
from reasoning_core.task_search.judge import Question, abstain, answer


def test_a_dimension_reads_its_distribution_as_one_number():
    yes_no = signals.Dimension("d", "q?")
    graded = signals.Dimension("e", "q?", ("easy", "medium", "hard"), (1.0, 0.5, 0.0))
    assert yes_no.value({"yes": 0.8, "no": 0.2}) == pytest.approx(0.8)
    assert graded.value({"easy": 0.2, "medium": 0.4, "hard": 0.4}) == pytest.approx(0.4)
    assert yes_no.value(None) is None


class _Judge:
    def __init__(self, p=None):
        self.p, self.calls = p, 0

    def evaluate(self, state, questions):
        self.calls += 1
        if self.p is None:
            return {q.name: abstain("down") for q in questions}
        return {q.name: answer(value=q.choices[0], probs={q.choices[0]: self.p})
                for q in questions}


def test_collect_resumes_asking_only_what_is_missing(monkeypatch, tmp_path):
    def sample(task_name, level, n, seed):
        if task_name == "broken":
            raise RuntimeError("generator crashed")
        return "h", [{"prompt": f"{task_name} L{level} #{i}", "answer": "1"} for i in range(n)]

    monkeypatch.setattr(signals, "sample", sample)
    dims = (signals.Dimension("d", "q?"), signals.Dimension("w", "q?", ("a", "b", "c")))
    jev, kev = _Judge(0.9), _Judge(None)
    monkeypatch.setattr(signals, "make_judge", {"jev": jev, "kev": kev}.get)
    out = tmp_path / "signals.jsonl"

    rows = signals.collect(["ok", "broken"], out, levels=(0,), n=2, dimensions=dims,
                           judges=("jev", "kev"), log=lambda *_: None)
    assert {row.get("error", "")[:12] for row in rows} == {"", "RuntimeError"}
    assert jev.calls == 2 and kev.calls == 2

    kev.p = 0.3   # Kev is back: only Kev is asked again, and Jev's answers survive
    signals.collect(["ok", "broken"], out, levels=(0,), n=2, dimensions=dims,
                    judges=("jev", "kev"), log=lambda *_: None)
    assert jev.calls == 2 and kev.calls == 4
    stored = [json.loads(line) for line in out.read_text().splitlines() if "prompt" in line]
    assert all(row["signals"] == {"jev": {"d": 0.9, "w": 0.9}, "kev": {"d": 0.3, "w": 0.3}}
               for row in stored)


def test_the_audit_reads_only_each_tasks_least_plausible_answers(monkeypatch, tmp_path):
    from reasoning_core.task_search import answer_audit

    def row(task, index, p):
        return {"task": task, "level": 0, "index": index, "prompt": f"{task}{index}",
                "answer": "1", "signals": {"jev": {"correct": p}}}

    rows = [row("a", 0, 0.9), row("a", 1, 0.05), row("a", 2, 0.3), row("a", 3, 0.2),
            row("b", 0, 0.8)]
    assert [(r["task"], r["index"]) for r in answer_audit.suspects(rows, per_task=2)] == [
        ("a", 1), ("a", 3)]

    class Solver:
        def __init__(self, replies):
            self.replies, self.calls = iter(replies), 0

        def complete(self, system, user, **_):
            self.calls += 1
            return "working...\nFINAL: " + next(self.replies)

    out = tmp_path / "audit.jsonl"
    solver = Solver(["2", "2 ", "1", "3"])   # a agrees twice on 2; b's second solve is 1
    verdicts = answer_audit.audit(rows, out, per_task=2, solver=solver, log=lambda *_: None)
    assert [v["verdict"] for v in verdicts] == ["WRONG", "CORRECT"]
    answer_audit.audit(rows, out, per_task=2, solver=solver, log=lambda *_: None)
    assert solver.calls == 4, "a judged suspect is not solved again"


def test_a_formatting_variant_the_scorer_refuses_is_strict_not_wrong():
    from reasoning_core.task_search import answer_audit

    row = {"task": "t", "level": 0, "index": 0, "prompt": "p", "answer": "8,17"}
    assert answer_audit.decide(row, ["8, 17", "8, 17"]) == "STRICT"
    assert answer_audit.decide(row, ["8, 18", "8, 18"]) == "WRONG"
    assert answer_audit.decide(row, ["8,17", "9"]) == "CORRECT"


def test_disagreeing_solves_accuse_nothing():
    from reasoning_core.task_search import answer_audit

    class Solver:
        replies = iter(["FINAL: 5", "FINAL: 6"])

        def complete(self, system, user, **_):
            return next(self.replies)

    row = {"task": "t", "level": 0, "index": 0, "prompt": "p", "answer": "1",
           "signals": {"jev": {"correct": 0.1}}}
    assert answer_audit.adjudicate(row, Solver())["verdict"] == "UNSURE"


def test_a_ladder_calibrated_on_a_probe_is_judged_on_tasks_it_never_saw():
    from reasoning_core.task_search.signal_report import ladder

    rows, measured = [], {}
    for task in range(12):
        for level in (0, 2, 4, 6):
            ease = 1 - level / 8 - task / 40
            rows.append({"task": f"t{task}", "level": level, "index": 0, "prompt": "p" * 10,
                         "answer": "a", "signals": {"jev": {"glance": ease}}})
            measured[(f"t{task}", level)] = ease
    predicted, stats = ladder(rows, measured, features=["jev:glance"])
    assert len(predicted) == 48 and stats["cells"] == 48
    assert stats["cell_rho"] > 0.99 and stats["within_task_rho"] > 0.99
    assert stats["direction"] == "12/12"


def test_the_choice_screen_asks_jev_to_pick_the_reference_among_scored_wrong_answers(
        monkeypatch, tmp_path):
    import reasoning_core
    from reasoning_core.task_search import answer_audit

    class Task:
        def generate_distractors(self, entry, n, max_candidates):
            return ["7", "8"]

    asked = []

    class Jev:
        def evaluate(self, state, questions):
            asked.append(state)
            labels = questions[0].choices
            reference = next(l for l in labels if f"{l}) 1" in state)
            return {"pick": answer(value=reference, probs={l: 0.6 if l == reference else 0.2
                                                          for l in labels})}

    monkeypatch.setattr(reasoning_core, "get_task", lambda name: Task())
    monkeypatch.setattr(answer_audit, "JevJudge", Jev)
    rows = [{"task": "t", "level": 0, "index": 0, "prompt": "p", "answer": "1",
             "metadata": {"x": 1}, "signals": {"jev": {"correct": 0.5}}}]
    path = tmp_path / "rows.jsonl"
    answer_audit.add_choice(rows, path, log=lambda *_: None)
    assert rows[0]["signals"]["jev"]["choice"] == pytest.approx(0.6)
    assert answer_audit.plausibility(rows[0]) == pytest.approx(0.3)
    assert all(option in asked[0] for option in (") 1", ") 7", ") 8"))
    answer_audit.add_choice(rows, path, log=lambda *_: None)
    assert len(asked) == 1 and json.loads(path.read_text())["signals"]["jev"]["choice"]


def test_tied_ranks_score_nothing_by_row_order():
    from reasoning_core.task_search.signal_report import spearman

    floor = [0.0, 0.0, 0.0, 0.5]   # a ladder that only moves at the top
    assert spearman([1, 2, 3, 4], floor) == pytest.approx(spearman([3, 2, 1, 4], floor))
