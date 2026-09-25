import collections

import pytest

from reasoning_core.tasks.generated.ua_cognitive_psychology_r4.episodic_feature_binding_retrieval.episodic_feature_binding_retrieval import (
    EpisodicFeatureBindingRetrieval,
    FEATURES,
    RESPONSES,
    latest_response,
)


def _answers(level, n=400):
    task = EpisodicFeatureBindingRetrieval()
    task.config.set_level(level)
    answers = collections.Counter()
    for _ in range(n):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0
        assert latest_response(e.metadata) == e.answer
        answers[e.answer] += 1
    return answers, task


def test_levels_generate_and_score():
    for level in range(7):
        c, _ = _answers(level)
        assert len(c) >= 3, (level, c)


def test_answers_label_balanced():
    c, _ = _answers(3)
    total = float(sum(c.values()))
    assert len(c) >= 6
    for label, n in c.items():
        assert n / total > 0.05, (label, c)


def test_answer_is_distinct_token():
    task = EpisodicFeatureBindingRetrieval()
    task.config.set_level(5)
    for _ in range(100):
        e = task.generate_example()
        assert e.answer in RESPONSES
        assert latest_response(e.metadata) == e.answer


def test_recency_rule_overwrites():
    task = EpisodicFeatureBindingRetrieval()
    task.config.set_level(4)
    recency_used = 0
    for _ in range(200):
        m = task.generate_example().metadata
        query = m["query_feature"]
        last = None
        for episode in reversed(m["episodes"]):
            if any(f == query for f, _v, _r in episode):
                last = episode
                break
        resp = [r for f, _v, r in last if f == query][0]
        assert latest_response(m) == resp
        if sum(1 for ep in m["episodes"] if any(f == query for f, _v, _r in ep)) >= 2:
            recency_used += 1
    assert recency_used > 20


def test_distractors_in_older_episodes():
    task = EpisodicFeatureBindingRetrieval()
    task.config.set_level(6)
    with_competing = 0
    for _ in range(200):
        m = task.generate_example().metadata
        query = m["query_feature"]
        indices = [i for i, ep in enumerate(m["episodes"])
                   if any(f == query for f, _v, _r in ep)]
        if len(indices) >= 2:
            with_competing += 1
            last_index = max(indices)
            last_resp = [r for f, _v, r in m["episodes"][last_index] if f == query][0]
            assert latest_response(m) == last_resp
    assert with_competing > 20


def test_wrong_answer_scores_zero():
    task = EpisodicFeatureBindingRetrieval()
    for _ in range(50):
        e = task.generate_example()
        for wrong in RESPONSES:
            if wrong != e.answer:
                assert task.score_answer(wrong, e) == 0.0
        assert task.score_answer("", e) == 0.0
        assert task.score_answer("banana", e) == 0.0
        assert task.score_answer(None, e) == 0.0


def test_config_difficulty_changes():
    cfg = EpisodicFeatureBindingRetrieval.config_cls()
    base = (cfg.n_episodes, cfg.max_per_episode, cfg.pool_size)
    cfg.set_level(6)
    assert cfg.n_episodes > base[0]
    assert cfg.max_per_episode >= base[1]
    assert cfg.pool_size > base[2]


def test_prompt_is_answerable_and_concise():
    task = EpisodicFeatureBindingRetrieval()
    for level in (0, 6):
        task.config.set_level(level)
        for _ in range(50):
            e = task.generate_example()
            p = task.render_prompt(e.metadata)
            assert "recency rule" in p
            assert e.metadata["query_feature"] in FEATURES
            assert p.count("Episode") == len(e.metadata["episodes"])
