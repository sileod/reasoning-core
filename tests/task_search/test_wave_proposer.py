import json
import re
from pathlib import Path

import pytest
import yaml

from reasoning_core.task_search import wave_proposer
from reasoning_core.task_search.wave_proposer import (
    CatalogEntry,
    CRITIC_MAX_BATCH,
    ChatClient,
    RETRY_BACKOFF,
    UpstreamError,
    _critic_votes,
    _extract_json,
    _proposal_entries,
    build_catalog,
    catalog_record,
    check_proposal_file,
    closest_entries,
    proposal_problems,
    propose_wave,
    validate_proposal_wave,
    write_proposal_wave,
)


ROOT = Path(__file__).parents[2]
VARIANT = re.compile(r"_v\d+$")


def proposal(name="fresh_operation"):
    return {
        "name": name,
        "summary": ("Propagate signed relation constraints across cycles and overlapping"
                    " paths, answering the queried pair's parity."),
    }


class FakeClient:
    def __init__(self, generated, reviews):
        self.generated = generated
        self.reviews = reviews
        self.calls = []

    def json(self, purpose, system, user, max_tokens=32768):
        self.calls.append({"purpose": purpose, "request_sha256": "a",
                           "response_sha256": "b", "response_id": purpose})
        return self.generated if purpose.startswith("propose") else self.reviews


def test_catalog_includes_gallery_plans_and_tasks():
    entries = build_catalog(ROOT)
    sources = catalog_record(entries)["sources"]

    assert sources["gallery"] >= 60
    assert sources["plan"] >= 90
    # No floor on proposals, in either direction. The catalog keys by name and prefers the
    # best account of an idea, so a proposal that got built is counted as the task it
    # became: the number falls as the pipeline succeeds -- 80 when most of the catalog was
    # unbuilt, 8 once wave12 landed 27 of them. What has to hold is that no proposed idea
    # drops out of the catalog, which is what the catalog is for: a wave is remembered even
    # when nobody implemented it. That is the next line, and it is the whole claim.
    assert {entry.name for entry in _proposal_entries(ROOT)} <= {entry.name for entry in entries}
    assert any(entry.name == "graph_pathfinding" for entry in entries)


def test_the_catalog_names_each_idea_once():
    """The catalog is a prompt, so a repeat is paid for on every proposal call.

    Each shipped task was also a gallery line, each `external` proposal was also two
    wave8 plan trials, and the trials arrived under names -- `..._v1`, `..._v2` -- that
    no proposal would ever collide with. That was 499 entries for 278 ideas.
    """
    entries = build_catalog(ROOT)
    names = [entry.name for entry in entries]

    assert len(names) == len(set(names))
    assert not [name for name in names if VARIANT.search(name)]
    assert not any(entry.entry_id.startswith("plan:wave8:") for entry in entries), (
        "wave8 fanned the external eighty into drafts; the ideas are already catalogued")


def test_catalog_uses_task_coverage_summaries_for_novelty():
    # By name, not by entry id: a shipped task is also a gallery line, the catalog now
    # keeps one of the two, and the summary is the same either way -- which is the point.
    entries = {entry.name: entry for entry in build_catalog(ROOT)}

    csp = entries["constraint_satisfaction"]
    arithmetic = entries["arithmetics"]
    assert csp.summary == (
        "Solve query-aware assignment, graph, scheduling, grid, set, and numeric CSPs.")
    assert arithmetic.summary == (
        "Compositional arithmetics with float/int/bool, varied operators, number theory.")


def test_closest_entries_uses_signature_not_only_name():
    catalog = (
        CatalogEntry("old:parity", "signed_graph_query",
                     "compose signed constraints and output queried parity", "plan"),
        CatalogEntry("old:sort", "sorting", "sort a list", "task"),
    )

    assert closest_entries(proposal(), catalog, limit=1)[0].entry_id == "old:parity"


def test_a_proposal_is_a_name_and_a_coverage_summary():
    assert proposal_problems(proposal()) == []

    assert proposal_problems({"name": "Bad Name", "summary": proposal()["summary"]}) == [
        "name must be canonical snake_case"]
    assert proposal_problems({"name": "ok_task", "summary": "sorts a list"}) == [
        "summary must be 40-240 characters, got 12"]
    assert proposal_problems({"name": "ok_task", "summary": "x " * 40}) == [
        "summary must be one trimmed line"]


def test_a_proposal_may_not_smuggle_back_the_old_boilerplate():
    """Difficulty ladders are a library-wide choice, not a per-proposal one."""
    noisy = proposal()
    noisy["data"] = {"difficulty": {"level_0": "one path"}}
    noisy["demonstration"] = {"prompt": "...", "answer": "..."}

    assert proposal_problems(noisy) == ["unexpected keys: data, demonstration"]


def test_proposer_rejects_exact_catalog_collision_then_accepts_critic_novelty():
    duplicate = proposal("graph_pathfinding")
    fresh = proposal("signed_constraint_parity")
    client = FakeClient(
        {"proposals": [duplicate, fresh]},
        {"reviews": [{
            "proposal_id": "C001", "verdict": "novel",
            "nearest_neighbors": [
                {"id": "plan:WAVE0:M1", "relationship": "adjacent",
                 "overlap": "both propagate constraints"},
                {"id": "gallery:belief_tracking", "relationship": "different",
                 "overlap": "both update latent relations"},
                {"id": "gallery:constraint_satisfaction", "relationship": "adjacent",
                 "overlap": "both enforce consistency"},
            ],
            "substantive_difference": "tracks parity over redundant signed paths",
            "scores": {"novelty": 5, "sft_value": 5, "feasibility": 4, "clarity": 4},
            "reason": "The cognitive operation is distinct.",
        }]},
    )

    wave = propose_wave(ROOT, name="unit-wave", count=1, rounds=1, client=client)

    assert wave["proposals"][0]["name"] == "signed_constraint_parity"
    assert wave["proposals"][0]["id"] == "P001"
    assert wave["proposals"][0]["novelty"]["verdict"] == "novel"
    assert len(wave["proposals"][0]["novelty"]["nearest_neighbors"]) == 3
    assert wave["rejected"][0]["verdict"] == "duplicate"
    assert validate_proposal_wave(wave) == []


def test_archive_is_durable_and_never_overwritten(tmp_path):
    item = proposal()
    item.update({"id": "P001", "novelty": {
        "verdict": "novel", "substantive_difference": "new operation",
        "scores": {"novelty": 5, "sft_value": 5, "feasibility": 4, "clarity": 4},
        "nearest_neighbors": [
            {"id": f"old:{i}", "relationship": "different", "overlap": "same family"}
            for i in range(3)
        ],
    }})
    wave = {"format_version": 1, "kind": "sft_task_proposals",
            "name": "x", "proposals": [item]}
    path = tmp_path / "archive" / "x.yaml"

    write_proposal_wave(path, wave)

    assert check_proposal_file(path) == []
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        write_proposal_wave(path, wave)


def test_json_extraction_accepts_fenced_reasoning_output():
    assert _extract_json("analysis first\n```json\n{\"proposals\": []}\n```\n") == {
        "proposals": []}


def test_incomplete_wave_is_returned_so_model_calls_are_not_lost():
    client = FakeClient({"proposals": [proposal("graph_pathfinding")]}, {"reviews": []})

    wave = propose_wave(ROOT, name="partial-wave", count=2, rounds=1, client=client)

    assert wave["objective"] == {
        "training_stage": "sft", "requested": 2, "accepted": 0, "complete": False}
    assert wave["rejected"][0]["verdict"] == "duplicate"


def test_neighbor_evidence_overrides_an_inconsistent_novel_verdict():
    client = FakeClient(
        {"proposals": [proposal("signed_constraint_parity")]},
        {"reviews": [{
            "proposal_id": "C001", "verdict": "novel",
            "nearest_neighbors": [
                {"id": "gallery:constraint_satisfaction", "relationship": "variant",
                 "overlap": "same constraint propagation operation"},
                {"id": "gallery:belief_tracking", "relationship": "adjacent",
                 "overlap": "both update latent relations"},
                {"id": "gallery:logic_derivation", "relationship": "different",
                 "overlap": "both compose multiple steps"},
            ],
            "substantive_difference": "only changes relation labels",
            "scores": {"novelty": 5, "sft_value": 5, "feasibility": 5, "clarity": 5},
            "reason": "The proposal is useful.",
        }]},
    )

    wave = propose_wave(ROOT, name="neighbor-gate", count=1, rounds=1, client=client)

    assert wave["proposals"] == []
    assert "contradicted" in wave["rejected"][0]["reason"]


def test_check_proposals_reports_a_missing_archive(tmp_path):
    assert check_proposal_file(tmp_path / "missing.yaml") == [
        f"proposal wave does not exist: {tmp_path / 'missing.yaml'}"]


def test_client_polls_a_pending_asynchronous_request(monkeypatch):
    class Response:
        def __init__(self, status, payload):
            self.status_code = status
            self._payload = payload
            self.content = json.dumps(payload).encode()

        def json(self):
            return self._payload

        def raise_for_status(self):
            if self.status_code >= 400:
                raise RuntimeError(self.status_code)

    posted = Response(202, {"requestId": "abc"})
    finished = Response(200, {"id": "response-1", "choices": [{"message": {
        "content": '{"proposals": []}'}}]})
    observed = {}
    monkeypatch.setattr("requests.post", lambda *args, **kwargs: posted)
    monkeypatch.setattr("time.sleep", lambda _: None)

    def get(url, **kwargs):
        observed["url"] = url
        return finished

    monkeypatch.setattr("requests.get", get)
    client = ChatClient(api_key="secret", timeout=10)

    assert client.json("test", "system", "user") == {"proposals": []}
    assert observed["url"] == "https://integrate.api.nvidia.com/v1/status/abc"
    assert client.calls[0]["response_id"] == "response-1"
    assert "secret" not in json.dumps(client.calls)


def test_client_reads_a_streamed_reply(monkeypatch):
    """Streaming is the default because a silent request to NIM is killed by the gateway.

    kimi-k3 spends minutes reasoning before its first content token, and wave9 died on a
    504 at batch 12 and again at batch 6 while a 16-token request to the same model
    answered fine. The bytes are what hold the connection open, so the reader has to
    survive keep-alive blanks, reasoning-only deltas and the terminating sentinel.
    """
    chunks = [
        'data: {"id": "stream-1", "choices": [{"delta": {"reasoning_content": "think"}}]}',
        "",
        'data: {"id": "stream-1", "choices": [{"delta": {"content": "{\\"proposals\\":"}}]}',
        ": keep-alive",
        'data: {"id": "stream-1", "choices": [{"delta": {"content": " []}"}}]}',
        "data: [DONE]",
        'data: {"id": "stream-1", "choices": [{"delta": {"content": "ignored"}}]}',
    ]

    class Response:
        status_code = 200
        content = b"consuming this would eat the stream"

        def raise_for_status(self):
            return None

        def iter_lines(self, decode_unicode=False):
            return iter(chunks)

    observed = {}

    def post(url, **kwargs):
        observed.update(stream=kwargs.get("stream"), body=kwargs.get("json"))
        return Response()

    monkeypatch.setattr("requests.post", post)
    client = ChatClient(api_key="secret", timeout=10)

    assert client.json("test", "system", "user") == {"proposals": []}
    # Asking for a stream and then not reading it as one is the failure that hangs.
    assert observed["stream"] is True and observed["body"]["stream"] is True
    assert client.calls[0]["response_id"] == "stream-1"
    assert "secret" not in json.dumps(client.calls)


def test_a_client_can_still_be_asked_for_a_whole_document(monkeypatch):
    """Endpoints that do not stream have to keep working, so the flag stays a choice."""
    class Response:
        status_code = 200
        content = json.dumps({"id": "doc-1", "choices": [
            {"message": {"content": '{"proposals": []}'}}]}).encode()

        def raise_for_status(self):
            return None

        def json(self):
            return json.loads(self.content)

    monkeypatch.setattr("requests.post", lambda *args, **kwargs: Response())
    client = ChatClient(api_key="secret", timeout=10, stream=False)

    assert client.json("test", "system", "user") == {"proposals": []}
    assert client.calls[0]["response_id"] == "doc-1"


def test_the_critic_can_run_on_a_separate_client_from_the_proposer(tmp_path):
    """A round is two calls, and wave9 lost a whole wave to a 429 raised by the second.

    The proposer had already spent the shared quota by the time the critic asked for its
    turn, so the split is what keeps one call from starving the other. The archive has to
    say which model actually issued the novelty verdicts, or a wave's acceptances cannot
    be attributed later.
    """
    class Client:
        def __init__(self, model, reply):
            self.model, self.provider, self.endpoint = model, "fake", "http://fake"
            self.reasoning_effort, self.calls, self.purposes = None, [], []
            self._reply = reply

        def json(self, purpose, system, user):
            self.purposes.append(purpose)
            self.calls.append({"purpose": purpose})
            return self._reply

    proposer = Client("big", {"proposals": [
        {"name": "novel_thing", "summary": 'Given a labelled hypergraph and a rewrite budget, decide which contraction orders reach the target normal form and report the cheapest one.'}]})
    critic = Client("small", {"reviews": [{
        "proposal_id": "C001", "verdict": "novel",
        "nearest_neighbors": [
            {"id": "plan:WAVE0:M1", "relationship": "adjacent",
             "overlap": "both propagate constraints"},
            {"id": "gallery:belief_tracking", "relationship": "different",
             "overlap": "both update latent relations"},
            {"id": "gallery:constraint_satisfaction", "relationship": "adjacent",
             "overlap": "both enforce consistency"},
        ],
        "substantive_difference": "contracts hyperedges under a cost budget",
        "scores": {"novelty": 5, "sft_value": 5, "feasibility": 5, "clarity": 5},
        "reason": "distinct operation"}]})

    wave = propose_wave(ROOT, name="split", count=1, rounds=1,
                        client=proposer, critic_client=critic)

    assert [p["name"] for p in wave["proposals"]] == ["novel_thing"]
    assert all("propose-round" in purpose for purpose in proposer.purposes)
    assert all("critic-round" in purpose for purpose in critic.purposes)
    assert wave["review"]["model"] == "small"
    assert wave["review"]["shared_with_generator"] is False
    assert wave["generation"]["calls"] and wave["review"]["calls"]


def test_one_client_still_does_both_jobs_when_no_critic_is_given(tmp_path):
    """The split is opt-in at the library level, so existing callers keep working."""
    class Client:
        model, provider, endpoint = "solo", "fake", "http://fake"
        reasoning_effort = None

        def __init__(self):
            self.calls, self.purposes = [], []

        def json(self, purpose, system, user):
            self.purposes.append(purpose)
            self.calls.append({"purpose": purpose})
            if purpose.startswith("propose"):
                return {"proposals": [{"name": "solo_thing", "summary": 'Given a labelled hypergraph and a rewrite budget, decide which contraction orders reach the target normal form and report the cheapest one.'}]}
            return {"reviews": [{
                "proposal_id": "C001", "verdict": "novel",
                "substantive_difference": "it is different",
                "scores": {"novelty": 5, "sft_value": 5, "feasibility": 5, "clarity": 5},
                "nearest_neighbors": [], "reason": "distinct operation"}]}

    solo = Client()
    wave = propose_wave(ROOT, name="solo", count=1, rounds=1, client=solo)

    assert wave["review"]["shared_with_generator"] is True
    assert wave["review"]["calls"] == []
    assert len(solo.purposes) == 2


def _neighbors():
    return [
        {"id": "plan:WAVE0:M1", "relationship": "adjacent",
         "overlap": "both propagate constraints"},
        {"id": "gallery:belief_tracking", "relationship": "different",
         "overlap": "both update latent relations"},
        {"id": "gallery:constraint_satisfaction", "relationship": "adjacent",
         "overlap": "both enforce consistency"},
    ]


class VotingCritic:
    """A critic whose verdict per sample is scripted, one entry per call."""

    model, provider, endpoint = "small", "fake", "http://fake"
    reasoning_effort = None

    def __init__(self, verdicts):
        self.verdicts, self.calls, self.purposes = list(verdicts), [], []

    def json(self, purpose, system, user):
        self.purposes.append(purpose)
        self.calls.append({"purpose": purpose})
        verdict = self.verdicts.pop(0)
        if verdict is None:
            return {"reviews": []}
        return {"reviews": [{
            "proposal_id": "C001", "verdict": verdict,
            "nearest_neighbors": _neighbors(),
            "substantive_difference": "contracts hyperedges under a cost budget",
            "scores": {"novelty": 5 if verdict == "novel" else 2, "sft_value": 5,
                       "feasibility": 5, "clarity": 5},
            "reason": f"judged {verdict}"}]}


def _one_proposal_client(*names):
    class Client:
        model, provider, endpoint = "big", "fake", "http://fake"
        reasoning_effort = None

        def __init__(self):
            self.calls = []

        def json(self, purpose, system, user):
            self.calls.append({"purpose": purpose})
            return {"proposals": [proposal(name) for name in names]}

    return Client()


@pytest.mark.parametrize("verdicts, accepted, votes", [
    (["novel", "novel", "duplicate"], True, "2/3"),
    (["novel", "duplicate", "duplicate"], False, "1/3"),
])
def test_the_critic_is_polled_k_times_and_the_majority_decides(verdicts, accepted, votes):
    """One flash opinion is noisy, and its two errors do not cost the same.

    A wrong reject loses one idea; a wrong accept spends an implementation trial and then
    sits in the catalog as the thing every later novelty check measures against.
    """
    critic = VotingCritic(verdicts)
    wave = propose_wave(ROOT, name="voted", count=1, rounds=1,
                        client=_one_proposal_client("signed_constraint_parity"),
                        critic_client=critic, critic_samples=3)

    assert len(critic.purposes) == 3
    if accepted:
        assert wave["proposals"][0]["novelty"]["votes"] == votes
        assert wave["proposals"][0]["novelty"]["dissent"] == ["duplicate"]
        assert validate_proposal_wave(wave) == []
    else:
        assert wave["proposals"] == []
        assert wave["rejected"][0]["votes"] == votes
        assert "1/3 samples judged it novel" in wave["rejected"][0]["reason"]


def test_samples_that_skip_a_candidate_leave_the_decision_to_the_ones_that_did_not():
    """Partial failure is the common case with a small model, not an aborted round."""
    critic = VotingCritic([None, "novel", "novel"])
    wave = propose_wave(ROOT, name="partial", count=1, rounds=1,
                        client=_one_proposal_client("signed_constraint_parity"),
                        critic_client=critic, critic_samples=3)

    assert wave["proposals"][0]["novelty"]["votes"] == "2/2"


def test_each_sample_shuffles_the_candidates_and_verdicts_follow_the_proposal():
    """The shuffle is the reason K samples are worth more than one repeated K times.

    Candidates are presented as an ordered list and judged partly against each other, so
    the same order twice mostly reproduces the same opinion twice. Shuffling also means a
    verdict has to be carried back through that sample's own seating: get the mapping
    wrong and the votes land on the neighbouring proposal, which no threshold would catch.
    """
    liked, disliked = "zzq_liked_operation", "zzq_disliked_operation"
    seatings = []

    class SeatAwareCritic:
        model, provider, endpoint = "small", "fake", "http://fake"
        reasoning_effort = None

        def __init__(self):
            self.calls = []

        def json(self, purpose, system, user):
            self.calls.append({"purpose": purpose})
            seating = sorted((liked, disliked), key=user.index)
            seatings.append(seating)
            return {"reviews": [
                {"proposal_id": f"C{seat:03d}",
                 "verdict": "novel" if name == liked else "duplicate",
                 "nearest_neighbors": _neighbors(),
                 "substantive_difference": "a genuinely different operation",
                 "scores": {"novelty": 5 if name == liked else 1, "sft_value": 5,
                            "feasibility": 5, "clarity": 5},
                 "reason": f"judged on {name}"}
                for seat, name in enumerate(seating, 1)]}

    wave = propose_wave(ROOT, name="shuffled", count=2, rounds=1,
                        client=_one_proposal_client(liked, disliked),
                        critic_client=SeatAwareCritic(), critic_samples=6)

    assert [p["name"] for p in wave["proposals"]] == [liked]
    assert {name for name, _ in [tuple(seat) for seat in seatings]} == {liked, disliked}, \
        "every sample presented the same candidate first, so the order was never shuffled"


def test_a_two_hundred_carrying_an_upstream_error_is_retried_not_parsed(monkeypatch):
    """OpenRouter answers 200 and puts the upstream 429 in the body.

    raise_for_status is blind to it, so before this the loop took the failure for an
    answer and the caller died on a KeyError several frames from the cause -- with the
    retries it had earned never spent. Measured against the real gateway, which returned
    `{"error": {"message": "Upstream error from Nvidia: Service temporarily overloaded"}}`
    under an HTTP 200.
    """
    replies = [
        {"error": {"message": "Upstream error from Nvidia: Service temporarily overloaded",
                   "code": 502}},
        {"id": "gen-2", "choices": [{"message": {"content": '{"ok": true}'}}]},
    ]
    posted = []

    class Response:
        status_code = 200

        def __init__(self, payload):
            self._payload = payload
            self.content = json.dumps(payload).encode()

        def json(self):
            return self._payload

        def raise_for_status(self):
            return None

    def post(url, **kwargs):
        posted.append(url)
        return Response(replies[len(posted) - 1])

    monkeypatch.setattr("reasoning_core.task_search.wave_proposer.requests.post", post)
    monkeypatch.setattr("reasoning_core.task_search.wave_proposer.time.sleep", lambda _: None)

    client = ChatClient(model="m", endpoint="http://x", api_key="k", stream=False)
    assert client.json("probe", "s", "u") == {"ok": True}
    assert len(posted) == 2, "the body-level failure did not cost a retry"
    assert client.calls[0]["response_id"] == "gen-2"


def test_an_upstream_error_that_never_clears_is_raised_not_swallowed(monkeypatch):
    class Response:
        status_code = 200
        content = b'{"error": {"message": "still overloaded"}}'

        def json(self):
            return {"error": {"message": "still overloaded"}}

        def raise_for_status(self):
            return None

    monkeypatch.setattr("reasoning_core.task_search.wave_proposer.requests.post",
                        lambda url, **kwargs: Response())
    monkeypatch.setattr("reasoning_core.task_search.wave_proposer.time.sleep", lambda _: None)

    client = ChatClient(model="m", endpoint="http://x", api_key="k", stream=False)
    with pytest.raises(UpstreamError, match="still overloaded"):
        client.json("probe", "s", "u")


def test_a_critic_batch_is_capped_so_a_truncated_reply_cannot_reject_the_tail():
    """Measured: deepseek-v4-flash returned one review for twenty-four candidates.

    Every review it does not return is scored as a rejection, so an over-large batch does
    not fail loudly -- it silently rejects everything after the truncation point. Twelve
    came back complete, so the batch is capped there and the round is split across calls.
    """
    seen = []

    class Critic:
        model, provider, endpoint = "small", "fake", "http://fake"
        reasoning_effort = None

        def __init__(self):
            self.calls = []

        def json(self, purpose, system, user):
            self.calls.append({"purpose": purpose})
            count = user.count('"proposal_id"') - 1  # the response shape carries one
            seen.append(count)
            return {"reviews": []}

    candidates = [proposal(f"candidate_number_{index:02d}") for index in range(30)]
    critic = Critic()
    _critic_votes(critic, candidates, [], max_catalog_chars=1000, samples=1,
                  round_index=1, wave_name="capped")

    assert max(seen) <= CRITIC_MAX_BATCH, f"sent a batch of {max(seen)} candidates"
    assert sum(seen) == 30, "candidates were dropped rather than split across batches"
    assert [c["purpose"] for c in critic.calls] == [
        "critic-round-1-batch-1", "critic-round-1-batch-2", "critic-round-1-batch-3"]


def test_a_rejected_proposal_keeps_its_summary_so_it_can_be_rejudged():
    """wave9's seventy-one rejected ideas are unrecoverable: the archive kept the reason
    and dropped the summary, and the proposer's replies keep only a sha256. Without the
    summary a rejection cannot be audited, re-judged, or reconsidered later."""
    critic = VotingCritic(["duplicate"])
    wave = propose_wave(ROOT, name="keeps", count=1, rounds=1,
                        client=_one_proposal_client("signed_constraint_parity"),
                        critic_client=critic, critic_samples=1)

    assert wave["rejected"][0]["summary"] == proposal()["summary"]


def _catalog_of(*pairs):
    from reasoning_core.task_search.wave_proposer import CatalogEntry

    return tuple(CatalogEntry(f"known:{name}", name, summary, "task")
                 for name, summary in pairs)


def test_semantic_retrieval_finds_the_duplicate_that_shares_no_words(monkeypatch):
    """The duplicate the gate exists to catch is the one worded differently.

    rapidfuzz ranks on spelling, so a proposal that renames a known task and paraphrases
    its summary outranks nothing and the critic has to notice it by reading the catalog.
    Meaning ranks it first.
    """
    from reasoning_core.task_search import embedding, wave_proposer

    catalog = _catalog_of(
        ("bit_string_parity", "Count set bits and report whether the total is even."),
        ("quicksort_trace", "Order a list of integers and report the sorted sequence."),
    )
    proposal = {"name": "evenness_of_ones",
                "summary": "Say if the number of ones in a binary word is even."}
    # One axis per catalog entry: the query leans on the first, and shares no words with it.
    vectors = {
        "bit_string_parity": (1.0, 0.0),
        "quicksort_trace": (0.0, 1.0),
        "evenness_of_ones": (0.96, 0.28),
    }

    def fake_embed(texts):
        return tuple(next(vector for name, vector in vectors.items() if name in text)
                     for text in texts)

    monkeypatch.setattr(embedding, "configured", lambda: True)
    monkeypatch.setattr(embedding, "embed", fake_embed)

    got = wave_proposer.semantic_entries([proposal], catalog, limit=1)
    assert [entry.name for entry in got[0]] == ["bit_string_parity"]

    # Both retrievers reach the critic, deduplicated, meaning first.
    merged = wave_proposer.neighbor_entries([proposal], catalog, limit=2)
    assert [entry.name for entry in merged[0]][0] == "bit_string_parity"
    assert len(merged[0]) == len({entry.entry_id for entry in merged[0]})


def test_an_unavailable_embedder_costs_the_ranking_and_not_the_wave(monkeypatch):
    """Every way of not getting vectors has to land on the string ranking, not an error."""
    from reasoning_core.task_search import embedding, wave_proposer

    catalog = _catalog_of(("bit_string_parity", "Count set bits and report the parity."))
    proposal = {"name": "bit_string_parity", "summary": "Count set bits, report parity."}

    monkeypatch.setattr(embedding, "configured", lambda: False)
    assert wave_proposer.semantic_entries([proposal], catalog) is None

    def refuse(_texts):
        raise RuntimeError("embedding request failed: HTTP Error 429: Too Many Requests")

    monkeypatch.setattr(embedding, "configured", lambda: True)
    monkeypatch.setattr(embedding, "embed", refuse)
    assert wave_proposer.semantic_entries([proposal], catalog) is None

    # ... and the critic still gets neighbours, from rapidfuzz alone.
    merged = wave_proposer.neighbor_entries([proposal], catalog)
    assert [entry.name for entry in merged[0]] == ["bit_string_parity"]


def test_a_brief_steers_the_prompt_and_an_unsteered_wave_is_byte_identical():
    """Steering must be opt-in at the byte level, or it breaks comparison with old waves.

    Every archived wave was proposed against the unsteered prompt. If adding the feature
    moved a single character of it, a wave proposed before and one proposed after would
    stop being the same experiment.
    """
    from reasoning_core.task_search.wave_proposer import _proposer_prompt

    plain = _proposer_prompt(3, "known:x | x | does x", ("y: rejected",))
    steered = _proposer_prompt(3, "known:x | x | does x", ("y: rejected",),
                               "Graph algorithms whose answer is a permutation.")

    assert "What this wave is for" not in plain
    assert "Graph algorithms whose answer is a permutation." in steered
    # The steer is additive: removing its block leaves the prompt that has always been sent.
    without = steered.replace(
        steered[steered.index("\nWhat this wave is for"):steered.index("\nRules:")], "")
    assert without == plain
    # And it says the brief is not a licence to repeat a known task.
    assert "relaxes nothing" in steered


def test_a_brief_is_normalised_and_bounded():
    from reasoning_core.task_search import wave_proposer

    assert wave_proposer.clean_brief("  graph   algorithms\n only ") == "graph algorithms only"
    assert wave_proposer.clean_brief(None) == ""
    with pytest.raises(ValueError, match="over the 2000 character limit".replace(
            " character limit", " limit")):
        wave_proposer.clean_brief("x" * (wave_proposer.BRIEF_MAX_CHARS + 1))


def test_a_generated_wave_records_where_it_came_from_and_what_it_was_asked_for():
    """`proposer` was a provenance kind nothing ever wrote: generated waves had no origin."""
    from reasoning_core.task_search import wave_proposer

    class Client:
        provider, model, calls = "testing", "test-model", ()

        def json(self, purpose, _system, _user):
            if purpose.startswith("propose"):
                return {"proposals": [{
                    "name": "permutation_composition",
                    "summary": ("Compose a sequence of permutations given in cycle notation "
                                "and report the resulting one-line permutation."),
                }]}
            return {"reviews": [{
                "proposal_id": "C001", "verdict": "novel",
                "nearest_neighbors": [
                    {"id": "known:a", "relationship": "different", "overlap": "none"},
                    {"id": "known:b", "relationship": "adjacent", "overlap": "graphs"},
                    {"id": "known:c", "relationship": "different", "overlap": "none"},
                ],
                "substantive_difference": "composes permutations rather than sorting them",
                "scores": {"novelty": 5, "sft_value": 5, "feasibility": 5, "clarity": 5},
                "reason": "distinct operation",
            }]}

    client = Client()
    wave = wave_proposer.propose_wave(
        ".", name="steered_probe", count=1, rounds=1, client=client, critic_client=client,
        brief="  Permutation   algebra.  ")
    where = wave["provenance"]
    assert where["kind"] == "proposer"
    assert where["name"] == "steered_probe"
    assert where["brief"] == "Permutation algebra."
    assert "test-model" in where["source"]

    # An unsteered wave still records provenance, with an empty brief rather than no key:
    # absent means the wave predates steering, empty means nobody steered it.
    open_wave = wave_proposer.propose_wave(
        ".", name="open_probe", count=1, rounds=1, client=client, critic_client=client)
    assert open_wave["provenance"]["brief"] == ""


def test_extract_json_survives_a_raw_newline_inside_a_string():
    """A model that breaks a line inside a field must not cost the wave its whole round."""
    got = _extract_json('{"why": "first\nsecond"}')
    assert got == {"why": "first\nsecond"}


def test_extract_json_accepts_a_trailing_comma():
    """Every human reader accepts it; json.loads does not, and a wave died on that."""
    assert _extract_json('{"a": [1, 2,], "b": 3,}') == {"a": [1, 2], "b": 3}


def test_a_truncated_stream_frame_is_retried_rather_than_ending_the_wave(monkeypatch):
    """A half-written SSE chunk is transport failing, which is what retries are for.

    It used to escape the loop as a bare JSONDecodeError: wave 3 of the brief job died on
    `Unterminated string starting at: line 1 column 125` seventeen minutes in.
    """
    client = ChatClient(model="m", endpoint="https://example.invalid/v1/chat/completions",
                        api_key="k", stream=True)
    bodies = iter([
        ['data: {"choices": [{"delta": {"content": "half a fra'],
        ['data: {"choices": [{"delta": {"content": "{\\"accepted\\": []}"}}]}',
         "data: [DONE]"],
    ])

    class Response:
        status_code = 200

        def __init__(self):
            self.lines = next(bodies)

        def raise_for_status(self):
            return None

        def iter_lines(self, decode_unicode=False):
            return iter(self.lines)

    monkeypatch.setattr(wave_proposer.requests, "post", lambda *a, **k: Response())
    slept = []
    monkeypatch.setattr(wave_proposer.time, "sleep", slept.append)

    assert client.json("propose", "system", "user") == {"accepted": []}
    assert slept == [wave_proposer.RETRY_BACKOFF[0]]


def test_a_connection_dropped_mid_stream_is_retried(monkeypatch):
    client = ChatClient(model="m", endpoint="https://example.invalid/v1/chat/completions",
                        api_key="k", stream=False)
    outcomes = iter([wave_proposer.requests.ConnectionError("reset by peer"),
                     ('{"accepted": []}', b"", "id-1")])

    class Response:
        status_code = 200

        def raise_for_status(self):
            return None

    def read(self, response, headers):
        outcome = next(outcomes)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(wave_proposer.requests, "post", lambda *a, **k: Response())
    monkeypatch.setattr(ChatClient, "_read_reply", read)
    monkeypatch.setattr(wave_proposer.time, "sleep", lambda seconds: None)

    assert client.json("review", "system", "user") == {"accepted": []}


def test_a_malformed_reply_is_retried_rather_than_ending_the_wave(monkeypatch):
    """The parse used to sit outside the retry loop, so one bad sample cost the wave.

    Drives the real ChatClient.json: only the transport and the backoff are replaced, so
    the retry being exercised is the one that runs in production.
    """
    client = ChatClient(model="m", endpoint="https://example.invalid/v1/chat/completions",
                        api_key="k", stream=False)
    replies = iter(["sorry, I cannot do that", '{"accepted": []}'])

    class Response:
        status_code = 200

        def raise_for_status(self):
            return None

    monkeypatch.setattr(wave_proposer.requests, "post", lambda *a, **k: Response())
    monkeypatch.setattr(
        ChatClient, "_read_reply",
        lambda self, response, headers: (next(replies), b"", "id-1"))
    slept = []
    monkeypatch.setattr(wave_proposer.time, "sleep", slept.append)

    assert client.json("review", "system", "user") == {"accepted": []}
    assert slept == [wave_proposer.RETRY_BACKOFF[0]]


class _Route:
    """A client that answers, or refuses with a 429, on a script."""

    def __init__(self, model, key, script):
        self.model, self.api_key, self.calls = model, key, []
        self._script = iter(script)
        self.provider = "test"

    def json(self, purpose, system, user, **kwargs):
        outcome = next(self._script)
        self.calls.append({"purpose": purpose})
        if outcome == 429:
            response = wave_proposer.requests.Response()
            response.status_code = 429
            raise wave_proposer.requests.HTTPError(response=response)
        return outcome


def test_a_pool_steps_sideways_to_another_key_before_another_model():
    """NVIDIA's quota is per account and per model: one key refused kimi-k3 while serving
    deepseek, and a second key served both. A second key on the model you asked for beats
    the first key on a model you did not."""
    wanted, fallback = {"proposals": ["from k3"]}, {"proposals": ["from the fallback"]}
    pool = wave_proposer.ClientPool([
        _Route("k3", "key1", [429]),
        _Route("k3", "key2", [wanted]),
        _Route("pro", "key1", [fallback]),
        _Route("pro", "key2", [fallback]),
    ])
    assert pool.json("propose", "s", "u") == wanted
    assert pool.model == "k3"


def test_a_pool_falls_back_to_the_next_model_once_every_key_refuses():
    fallback = {"proposals": ["from the fallback"]}
    pool = wave_proposer.ClientPool([
        _Route("k3", "key1", [429]),
        _Route("k3", "key2", [429]),
        _Route("pro", "key1", [fallback]),
    ])
    assert pool.json("propose", "s", "u") == fallback
    assert pool.model == "pro"


def test_a_refusing_route_is_not_asked_again_until_its_cooldown_expires():
    """A cycle with no memory hands work back to an exhausted key every other call."""
    answer = {"proposals": []}
    dead = _Route("k3", "key1", [429])           # scripted once: a second ask would raise
    live = _Route("k3", "key2", [answer, answer])
    pool = wave_proposer.ClientPool([dead, live], cooldown=3600)
    assert pool.json("propose", "s", "u") == answer
    assert pool.json("propose", "s", "u") == answer
    assert len(dead.calls) == 1


def test_keys_are_shared_round_robin_so_one_quota_does_not_cap_the_wave():
    answer = {"proposals": []}
    first = _Route("k3", "key1", [answer, answer])
    second = _Route("k3", "key2", [answer, answer])
    pool = wave_proposer.ClientPool([first, second])
    for _ in range(4):
        pool.json("propose", "s", "u")
    assert len(first.calls) == 2 and len(second.calls) == 2


def test_a_failure_that_is_not_a_rate_limit_is_not_routed_around():
    """A pool is for quotas. Hiding a 500 behind a fallback hides a broken endpoint."""
    response = wave_proposer.requests.Response()
    response.status_code = 500

    class Broken(_Route):
        def json(self, *args, **kwargs):
            raise wave_proposer.requests.HTTPError(response=response)

    pool = wave_proposer.ClientPool([Broken("k3", "key1", []),
                                     _Route("k3", "key2", [{"proposals": []}])])
    with pytest.raises(wave_proposer.requests.HTTPError):
        pool.json("propose", "s", "u")


def test_the_pool_reports_the_model_that_actually_answered():
    pool = wave_proposer.ClientPool([_Route("k3", "key1", [429]),
                                     _Route("pro", "key1", [{"proposals": []}])])
    pool.json("propose", "s", "u")
    assert pool.model == "pro" and len(pool.calls) == 2


class BallotCritic:
    """A critic whose verdict *and* ballot validity are scripted per sample.

    "malformed" is a sample that judged the candidate novel but failed to name three real
    neighbours -- the shape that was costing novelty-5 proposals.
    """

    model, provider, endpoint = "small", "fake", "http://fake"
    reasoning_effort = None

    def __init__(self, script):
        self.script, self.calls, self.purposes = list(script), [], []

    def json(self, purpose, system, user):
        self.purposes.append(purpose)
        self.calls.append({"purpose": purpose})
        entry = self.script.pop(0)
        neighbors = [] if entry == "malformed" else _neighbors()
        return {"reviews": [{
            "proposal_id": "C001", "verdict": "novel",
            "nearest_neighbors": neighbors,
            "substantive_difference": "contracts hyperedges under a cost budget",
            "scores": {"novelty": 5, "sft_value": 5, "feasibility": 5, "clarity": 5},
            "reason": "judged novel"}]}


def test_a_malformed_ballot_abstains_instead_of_voting_against():
    """It cost sandpile_stabilization and rotation_map_faces, both scored novelty 5.

    A critic that cannot name three overlapping neighbours has not found a duplicate; the
    candidate hardest to place is the one with no close neighbours, so counting it against
    was biased against exactly the proposals the wave exists to find.
    """
    critic = BallotCritic(["malformed", "malformed", "novel"])
    wave = propose_wave(ROOT, name="abstain", count=1, rounds=1,
                        client=_one_proposal_client("signed_constraint_parity"),
                        critic_client=critic, critic_samples=3)

    assert [p["name"] for p in wave["proposals"]] == ["signed_constraint_parity"]
    assert wave["proposals"][0]["novelty"]["votes"] == "1/1"


def test_a_candidate_no_sample_could_judge_is_reported_as_unusable_not_as_a_duplicate():
    critic = BallotCritic(["malformed", "malformed", "malformed"])
    wave = propose_wave(ROOT, name="unusable", count=1, rounds=1,
                        client=_one_proposal_client("signed_constraint_parity"),
                        critic_client=critic, critic_samples=3)

    assert wave["proposals"] == []
    assert wave["rejected"][0]["reason"] == "no critic sample returned a usable ballot"


def test_a_rejection_names_the_catalog_entries_it_collided_with():
    """The prose already said something overlapped; it never said what with."""
    ballot = {"neighbors": [
        {"id": "gallery:belief_tracking", "relationship": "same_operation",
         "overlap": "same update"},
        {"id": "gallery:constraint_satisfaction", "relationship": "adjacent",
         "overlap": "both enforce consistency"},
    ]}
    catalog = [wave_proposer.CatalogEntry("gallery:belief_tracking", "belief_tracking",
                                          "tracks beliefs", "gallery"),
               wave_proposer.CatalogEntry("gallery:constraint_satisfaction",
                                          "constraint_satisfaction", "solves", "gallery")]
    said = wave_proposer._collisions(ballot, catalog)
    # The fatal relationship is named; `adjacent` is what a good proposal looks like.
    assert said == " [overlaps belief_tracking (same_operation)]"
    assert "constraint_satisfaction" not in said


def test_a_rejection_with_no_fatal_overlap_adds_nothing():
    ballot = {"neighbors": [{"id": "gallery:x", "relationship": "adjacent",
                             "overlap": "some"}]}
    assert wave_proposer._collisions(ballot, []) == ""


def test_a_pool_does_not_climb_the_retry_ladder_before_trying_another_key(monkeypatch):
    """Sixteen minutes of backoff to learn a key is exhausted is sixteen minutes the
    other key could have been answering."""
    seen = []

    class Recording(_Route):
        def json(self, purpose, system, user, wait_out_rate_limits=True, **kwargs):
            seen.append((self.api_key, wait_out_rate_limits))
            return super().json(purpose, system, user, **kwargs)

    pool = wave_proposer.ClientPool([Recording("k3", "key1", [429]),
                                     Recording("k3", "key2", [{"proposals": []}])])
    pool.json("propose", "s", "u")
    # The first route fails fast; only the last one, with nothing left to route to, waits.
    assert seen == [("key1", False), ("key2", True)]
