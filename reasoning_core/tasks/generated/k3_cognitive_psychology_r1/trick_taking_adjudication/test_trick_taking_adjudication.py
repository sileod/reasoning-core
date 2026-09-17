import json
import random
from itertools import permutations

import pytest

from reasoning_core.tasks.generated.k3_cognitive_psychology_r1.trick_taking_adjudication.trick_taking_adjudication import (
    PLAYERS,
    SUITS,
    TrickTakingAdjudication,
    card_value,
    legal_plays,
    ordered_cards,
    verify_round,
    winner_of,
)


@pytest.fixture(autouse=True)
def preserve_rng():
    state = random.getstate()
    yield
    random.setstate(state)


def test_follow_suit_and_void():
    hand = ["CA", "CQ", "HK", "SQ"]
    assert legal_plays(hand, "C") == ["CA", "CQ"]
    assert legal_plays(hand, "D") == hand
    assert legal_plays(hand, None) == hand


@pytest.mark.parametrize("trump,revoked,expected", [
    (None, [], "East"),
    ("H", [], "South"),
    ("H", ["South"], "East"),
    (None, ["East"], "North"),
])
def test_winner_lead_trump_and_revoke(trump, revoked, expected):
    order = {s: "QAK" for s in SUITS}
    plays = [["North", "CA"], ["East", "CQ"], ["South", "HK"], ["West", "SQ"]]
    assert winner_of(plays, revoked, trump, order) == expected


def test_each_trick_recomputes_rank_hierarchy():
    plays = [["North", "CA"], ["East", "CQ"], ["South", "HK"], ["West", "SQ"]]
    first = {s: "AQK" for s in SUITS}
    second = {s: "QAK" for s in SUITS}
    assert winner_of(plays, [], None, first) == "North"
    assert winner_of(plays, [], None, second) == "East"
    assert ordered_cards(["CA", "CQ", "HK"], second) == ["CQ", "CA", "HK"]
    assert card_value("CQ", second) == 3
    assert card_value("HK", second) == 1


def test_exhaustive_small_trick_winners():
    plays = [["North", "CA"], ["East", "CQ"], ["South", "HA"], ["West", "HK"]]
    for cranks in permutations("AKQ"):
        for hranks in permutations("AKQ"):
            order = {"C": "".join(cranks), "D": "AKQ", "H": "".join(hranks), "S": "AKQ"}
            for trump in [None, *SUITS]:
                for mask in range(8):
                    revoked = [PLAYERS[i + 1] for i in range(3) if mask & (1 << i)]
                    eligible = [(p, c) for p, c in plays if p not in revoked]
                    suit = trump if any(c[0] == trump for _, c in eligible) else "C"
                    expected = next(p for r in order[suit] for p, c in eligible if c == suit + r)
                    assert winner_of(plays, revoked, trump, order) == expected


def test_independent_capture_and_penalty_example():
    m = {
        "mode": "points", "ranks": "AKQ", "penalty": 5,
        "initial": {"North": ["CA", "DA"], "East": ["CQ", "HA"],
                    "South": ["HK", "DQ"], "West": ["SQ", "DK"]},
        "tricks": [{"order": {"C": "QAK", "D": "AKQ", "H": "KQA", "S": "KAQ"},
                    "trump": "H", "plays": [["North", "CA"], ["East", "HA"],
                                               ["South", "HK"], ["West", "SQ"]]}],
    }
    answer, winners, scores, revokes = verify_round(m)
    assert answer == "[0, -5, 7, 0]"
    assert winners == ["South"]
    assert scores["South"] == 2 + 1 + 3 + 1
    assert revokes == [["East"]]


@pytest.mark.parametrize("level", [0, 0.5, 2, 3, 5, 6])
def test_generation_contract_and_replay(level):
    random.seed(900 + int(level * 10))
    task = TrickTakingAdjudication()
    task.config.set_level(level)
    modes, revoke_seen, trump_seen = set(), False, set()
    for _ in range(45):
        ex = task.generate_example()
        m = json.loads(json.dumps(ex.metadata))
        assert verify_round(m)[0] == ex.answer
        assert task.render_prompt(m) == ex.prompt
        assert task.score_answer(ex.answer, ex) == 1.0
        for wrong in ["", "garbage", "[]", ex.answer + "x", ex.answer[1:-1], None]:
            assert task.score_answer(wrong, ex) == 0.0
        modes.add(m["mode"])
        revoke_seen |= any(m["revokes"])
        for tr in m["tricks"]:
            trump_seen.add(tr["trump"])
        if m["mode"] == "legal":
            cards = ex.answer[1:-1].split(", ")
            assert len(cards) == len(set(cards))
        else:
            assert len(m["winners"]) == task.config.tricks_played
            assert any(
                winner_of(tr["plays"], m["revokes"][i], tr["trump"], m["tricks"][i - 1]["order"])
                != m["winners"][i]
                for i, tr in enumerate(m["tricks"]) if i > 0
            )
    assert modes == {"legal", "winner", "points"}
    assert revoke_seen
    assert None in trump_seen and len(trump_seen) == 5


def test_stateless_scorer_enforces_order():
    class NoAttributes:
        def __getattribute__(self, name):
            raise AssertionError(name)

    random.seed(12)
    task = TrickTakingAdjudication()
    for _ in range(20):
        ex = task.generate_example()
        assert TrickTakingAdjudication.score_answer(NoAttributes(), ex.answer, ex) == 1.0
        parts = ex.answer[1:-1].split(", ")
        shuffled = "[" + ", ".join(reversed(parts)) + "]"
        if shuffled != ex.answer:
            assert task.score_answer(shuffled, ex) == 0.0


def test_verifier_rejects_impossible_logs():
    random.seed(52)
    task = TrickTakingAdjudication()
    ex = task.generate_entry()
    metadata = json.loads(json.dumps(ex.metadata))
    p, card = metadata["tricks"][0]["plays"][0]
    metadata["initial"][p].remove(card)
    with pytest.raises(AssertionError):
        verify_round(metadata)
    metadata = json.loads(json.dumps(ex.metadata))
    metadata["tricks"][0]["plays"][1][0] = p
    with pytest.raises(AssertionError):
        verify_round(metadata)
    metadata = json.loads(json.dumps(ex.metadata))
    metadata["tricks"][1]["order"] = metadata["tricks"][0]["order"].copy()
    with pytest.raises(AssertionError):
        verify_round(metadata)


def test_partial_trick_replays_removed_revoke_card():
    m = {
        "mode": "legal", "ranks": "AKQ", "penalty": 5, "next_player": "East",
        "initial": {"North": ["CA", "DA"], "East": ["CQ", "HA"],
                    "South": ["HK", "DQ"], "West": ["SQ", "DK"]},
        "tricks": [
            {"order": {"C": "QAK", "D": "AKQ", "H": "KQA", "S": "KAQ"},
             "trump": "H", "plays": [["North", "CA"], ["East", "HA"],
                                        ["South", "HK"], ["West", "SQ"]]},
            {"order": {"C": "AKQ", "D": "QKA", "H": "QAK", "S": "KQA"},
             "trump": None, "plays": [["North", "DA"]]},
        ],
    }
    answer, winners, _, revokes = verify_round(m)
    assert answer == "[CQ]"
    assert winners == ["South"]
    assert revokes == [["East"], []]


def test_rng_reproducible_and_difficulty_resets():
    task = TrickTakingAdjudication()
    task.config.set_level(6)
    high = (task.config.tricks_played, task.config.n_ranks)
    task.config.set_level(0)
    assert high > (task.config.tricks_played, task.config.n_ranks)
    random.seed(782)
    first = task.generate_entry()
    random.seed(782)
    second = task.generate_entry()
    assert first.metadata == second.metadata
    assert first.answer == second.answer
