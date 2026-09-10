"""The embeddings transport behind the novelty gate's semantic ranking."""
import io
import json

import pytest

from reasoning_core.task_search import embedding


@pytest.fixture
def configured(monkeypatch):
    monkeypatch.setenv("TASK_SEARCH_EMBED_ENDPOINT", "https://example.invalid/v1/embeddings")
    monkeypatch.setenv("TASK_SEARCH_EMBED_KEY_ENV", "FAKE_EMBED_KEY")
    monkeypatch.setenv("FAKE_EMBED_KEY", "x")
    monkeypatch.setattr(embedding.time, "sleep", lambda _seconds: None)


def _answer(monkeypatch, responder):
    seen = []

    def urlopen(request, timeout=None):
        seen.append(json.loads(request.data))
        return io.BytesIO(json.dumps(responder(seen[-1])).encode())

    monkeypatch.setattr(embedding.urllib.request, "urlopen", urlopen)
    return seen


def test_configuration_is_read_from_the_environment(monkeypatch, configured):
    assert embedding.configured()
    assert embedding.model() == "BAAI/bge-m3"
    monkeypatch.delenv("FAKE_EMBED_KEY")
    assert not embedding.configured()


def test_a_long_catalog_is_batched_and_comes_back_in_order(monkeypatch, configured):
    """Vectors are matched to inputs by the index the API reports, not by arrival order."""
    monkeypatch.setattr(embedding, "BATCH", 2)

    def responder(body):
        # Answers shuffled on purpose: only the index says which text a vector belongs to.
        rows = [{"index": position, "embedding": [float(len(text)), 0.0]}
                for position, text in enumerate(body["input"])]
        return {"data": list(reversed(rows))}

    seen = _answer(monkeypatch, responder)
    got = embedding.embed(["a", "bb", "ccc", "dddd", "eeeee"])
    assert [vector[0] for vector in got] == [1.0, 2.0, 3.0, 4.0, 5.0]
    assert [len(call["input"]) for call in seen] == [2, 2, 1]
    assert {call["model"] for call in seen} == {"BAAI/bge-m3"}


def test_a_short_answer_raises_rather_than_mislabelling_vectors(monkeypatch, configured):
    """Silently accepting fewer vectors would compare a proposal to the wrong entry."""
    _answer(monkeypatch, lambda body: {"data": [{"index": 0, "embedding": [1.0]}]})
    with pytest.raises(RuntimeError, match="did not answer every input"):
        embedding.embed(["one", "two"])


def test_a_rate_limit_is_waited_out_and_a_bad_key_is_not(monkeypatch, configured):
    import urllib.error

    calls = []

    def flaky(code, fails):
        def urlopen(request, timeout=None):
            calls.append(code)
            if len(calls) <= fails:
                raise urllib.error.HTTPError("u", code, "busy", {}, None)
            return io.BytesIO(json.dumps(
                {"data": [{"index": 0, "embedding": [1.0, 0.0]}]}).encode())
        monkeypatch.setattr(embedding.urllib.request, "urlopen", urlopen)

    flaky(429, 2)
    assert embedding.embed(["one"])
    assert len(calls) == 3

    calls.clear()
    flaky(401, 1)
    with pytest.raises(RuntimeError, match="embedding request failed"):
        embedding.embed(["one"])
    assert len(calls) == 1


def test_similarity_is_a_dot_product_and_rank_is_stable():
    """bge-m3 returns unit-length vectors, so cosine needs no normalisation."""
    assert embedding.similarity((1.0, 0.0), (1.0, 0.0)) == pytest.approx(1.0)
    assert embedding.similarity((1.0, 0.0), (0.0, 1.0)) == pytest.approx(0.0)
    # Ties break on position, so the same catalog ranks the same way twice.
    vectors = [(1.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    assert embedding.rank((1.0, 0.0), vectors, 2) == (0, 1)
