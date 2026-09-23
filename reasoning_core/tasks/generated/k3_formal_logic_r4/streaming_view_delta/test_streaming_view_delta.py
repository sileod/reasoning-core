import random
from reasoning_core.tasks.generated.k3_formal_logic_r4.streaming_view_delta.streaming_view_delta import StreamingViewDelta


def test_generate_and_score_delta():
    task = StreamingViewDelta()
    hits = 0
    for _ in range(40):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0
        if x.metadata["kind"] == "delta":
            hits += 1
            assert x.answer.strip() != ""
    assert hits > 0


def test_generate_and_score_query():
    task = StreamingViewDelta()
    hits = 0
    for _ in range(40):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0
        if x.metadata["kind"] == "query":
            hits += 1
            val = int(x.answer)
            assert val >= 0
    assert hits > 0


def test_rejects_junk():
    task = StreamingViewDelta()
    got_query = False
    for _ in range(40):
        x = task.generate_example()
        assert task.score_answer("", x) < 1.0
        assert task.score_answer("garbage", x) < 1.0
        assert task.score_answer("zz not a thing", x) < 1.0
    assert True


def test_metadata_json_serializable():
    import json
    task = StreamingViewDelta()
    for _ in range(20):
        x = task.generate_example()
        json.dumps(x.metadata)
        json.dumps(x.answer)


def test_deterministic_under_seed():
    random.seed(1234)
    task = StreamingViewDelta()
    a1 = [task.generate_example().answer for _ in range(20)]
    random.seed(1234)
    task2 = StreamingViewDelta()
    a2 = [task2.generate_example().answer for _ in range(20)]
    assert a1 == a2
