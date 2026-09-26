import random
from reasoning_core.tasks.generated.wave9.event_queue_simulation.event_queue_simulation import EventQueueSimulation


def _solve(arrivals, n_procs):
    """Tick by tick: a free processor starts the best job that has already arrived."""
    pending = [(pr, t, idx, p, w) for idx, (t, p, w, pr) in enumerate(arrivals)]
    busy_until, finished, clock = [0] * n_procs, [0] * n_procs, 0
    while pending:
        for proc in range(n_procs):
            ready = [job for job in pending if job[3] == proc and job[1] <= clock]
            if busy_until[proc] <= clock and ready:
                job = min(ready)
                pending.remove(job)
                busy_until[proc] = finished[proc] = clock + job[4]
        clock += 1
    return max(finished)


def test_a_processor_does_not_wait_for_a_job_still_to_come():
    # The v1 generator ran jobs in priority order regardless of arrival and answered 33:
    # processor 2 idled until the time-23 job, then ran the one that arrived at time 1.
    arrivals = [[1, 2, 6, 5], [17, 0, 1, 1], [11, 0, 3, 1], [12, 1, 6, 3], [23, 2, 4, 4],
                [29, 0, 1, 4]]
    assert _solve(arrivals, 3) == 30


def test_gold_scores_one():
    random.seed(0)
    task = EventQueueSimulation()
    for _ in range(50):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_answer_matches_independent_solver():
    random.seed(1)
    task = EventQueueSimulation()
    for _ in range(50):
        e = task.generate_example()
        arrivals = e.metadata.arrivals
        expect = _solve(arrivals, e.metadata.n_procs)
        assert int(e.answer) == expect


def test_garbage_rejected():
    random.seed(2)
    task = EventQueueSimulation()
    e = task.generate_example()
    for junk in ["", "abc", "-5", "1.5", "None"]:
        assert task.score_answer(junk, e) < 1.0


def test_domains():
    random.seed(3)
    task = EventQueueSimulation()
    for _ in range(50):
        e = task.generate_example()
        val = int(e.answer)
        assert val >= 0
        for (t, p, w, pr) in e.metadata.arrivals:
            assert 0 <= p < e.metadata.n_procs
            assert w >= 1
            assert pr >= 1
