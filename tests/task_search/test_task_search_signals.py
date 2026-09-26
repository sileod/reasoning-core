import io
import json

import pytest

from reasoning_core.task_search import judge_span, signals
from reasoning_core.task_search.judge import Question, abstain, answer


def test_a_dimension_reads_its_distribution_as_one_number():
    yes_no = signals.Dimension("d", "q?")
    graded = signals.Dimension("e", "q?", ("easy", "medium", "hard"), (1.0, 0.5, 0.0))
    assert yes_no.value({"yes": 0.8, "no": 0.2}) == pytest.approx(0.8)
    assert graded.value({"easy": 0.2, "medium": 0.4, "hard": 0.4}) == pytest.approx(0.4)
    assert yes_no.value(None) is None


def _span_replying(monkeypatch, reply=None, error=None):
    sent = []

    def opener(request, timeout=None):
        sent.append(json.loads(request.data))
        if error:
            raise error
        return io.BytesIO(json.dumps(reply).encode())

    monkeypatch.setattr(judge_span.urllib.request, "urlopen", opener)
    return judge_span.SpanJudge(key="k"), sent


def test_span_renormalises_present_against_absent_and_declines_wider_questions(monkeypatch):
    judge_, sent = _span_replying(monkeypatch, {"results": [
        {"id": "two", "p_present": 0.6, "p_absent": 0.2, "p_not_observable": 0.2}]})
    got = judge_.evaluate("state", [Question("two", "Is it?", ("yes", "no")),
                                    Question("three", "Which?", ("a", "b", "c"))])
    assert got["two"]["probs"] == pytest.approx({"yes": 0.75, "no": 0.25})
    assert got["three"]["value"] is None
    assert [b["id"] for b in sent[0]["behaviors"]] == ["two"]


def test_a_failing_span_stops_asking_instead_of_holding_up_the_run(monkeypatch):
    judge_, sent = _span_replying(monkeypatch, error=OSError("daily cap"))
    question = Question("q", "Is it?", ("yes", "no"))
    assert judge_.evaluate("s", [question])["q"]["value"] is None
    assert judge_.evaluate("s", [question])["q"]["reason"].startswith("span unreachable")
    assert len(sent) == 1


class _Judge:
    def __init__(self, p=None, two_way=False):
        self.p, self.calls, self.two_way = p, 0, two_way

    def answers(self, question):
        return not self.two_way or len(question.choices) == 2

    def evaluate(self, state, questions):
        self.calls += 1
        if self.p is None:
            return {q.name: abstain("down") for q in questions}
        return {q.name: answer(value=q.choices[0], probs={q.choices[0]: self.p})
                if self.answers(q) else abstain("two-way only") for q in questions}


def test_collect_resumes_asking_only_what_is_missing(monkeypatch, tmp_path):
    def sample(task_name, level, n, seed):
        if task_name == "broken":
            raise RuntimeError("generator crashed")
        return "h", [{"prompt": f"{task_name} L{level} #{i}", "answer": "1"} for i in range(n)]

    monkeypatch.setattr(signals, "sample", sample)
    dims = (signals.Dimension("d", "q?"), signals.Dimension("w", "q?", ("a", "b", "c")))
    jev, span = _Judge(0.9), _Judge(None, two_way=True)
    monkeypatch.setattr(signals, "make_judge", {"jev": jev, "span": span}.get)
    out = tmp_path / "signals.jsonl"

    rows = signals.collect(["ok", "broken"], out, levels=(0,), n=2, dimensions=dims,
                           log=lambda *_: None)
    assert {row.get("error", "")[:12] for row in rows} == {"", "RuntimeError"}
    assert jev.calls == 2 and span.calls == 2

    span.p = 0.3   # Span is back: only Span is asked again, and Jev's answers survive
    signals.collect(["ok", "broken"], out, levels=(0,), n=2, dimensions=dims,
                    log=lambda *_: None)
    assert jev.calls == 2 and span.calls == 4
    stored = [json.loads(line) for line in out.read_text().splitlines() if "prompt" in line]
    assert all(row["signals"] == {"jev": {"d": 0.9, "w": 0.9}, "span": {"d": 0.3}}
               for row in stored)
    signals.collect(["ok"], out, levels=(0,), n=2, dimensions=dims, log=lambda *_: None)
    assert jev.calls == 2 and span.calls == 4, "a question Span cannot answer is not re-asked"


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
