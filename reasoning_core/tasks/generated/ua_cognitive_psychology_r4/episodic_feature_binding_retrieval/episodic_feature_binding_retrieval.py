import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'episodic_feature_binding_retrieval (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_cognitive_psychology_r4/episodic_feature_binding_retrieval',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

FEATURES = ["color", "shape", "texture", "material", "motion", "sound",
            "temperature", "speed", "weight", "size"]
VALUES = ["red", "blue", "round", "smooth", "loud", "hot", "fast", "heavy",
          "large", "spiky", "cold", "slow", "soft", "shiny"]
RESPONSES = ["Alpha", "Bravo", "Charlie", "Delta", "Echo",
             "Foxtrot", "Golf", "Hotel", "India", "Juliett"]


def latest_response(metadata):
    """Response bound to the queried feature in its most recent episode.

    Scans episodes from latest to earliest and returns the response of the
    first episode containing the queried feature (the recency rule).
    """
    query = metadata["query_feature"]
    for episode in reversed(metadata["episodes"]):
        for feature, _value, response in episode:
            if feature == query:
                return response
    return None


@dataclass
class EpisodicBindingConfig(Config):
    n_episodes: int = 2
    max_per_episode: int = 1
    pool_size: int = 3
    multi_bias: float = 0.7

    def apply_difficulty(self, level):
        self.n_episodes = 2 + int(level)
        self.max_per_episode = 1 + int(level) // 2
        self.pool_size = min(len(FEATURES), 3 + int(level))


class EpisodicFeatureBindingRetrieval(Task):
    summary = "Retrieve feature-response bindings from prior episodes by a stated recency rule; vary partial repetitions, overwritten bindings, and competing episodes; return the response bound to the queried feature in its latest episode."
    design_choice = "Represent episodes as triples of (feature, value, response) and ask for the response bound to a queried feature under a recency rule that selects the latest episode containing that feature, with distractors in older episodes."
    config_cls = EpisodicBindingConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        pool = FEATURES[:cfg.pool_size]
        episodes = []
        for _ in range(cfg.n_episodes):
            k = random.randint(1, cfg.max_per_episode)
            k = min(k, len(pool))
            features = random.sample(pool, k)
            episode = [(f, random.choice(VALUES), random.choice(RESPONSES))
                       for f in features]
            episodes.append(episode)

        occurrences = {}
        for episode in episodes:
            for feature, _v, _r in episode:
                occurrences[feature] = occurrences.get(feature, 0) + 1

        multi = sorted(f for f, c in occurrences.items() if c >= 2)
        if multi and random.random() < cfg.multi_bias:
            query = random.choice(multi)
        else:
            query = random.choice(sorted(occurrences))

        metadata = {"episodes": episodes, "query_feature": query}
        gold = latest_response(metadata)
        assert gold in RESPONSES, "gold must be a valid response token"
        assert gold is not None
        return Entry(metadata=metadata, answer=gold)

    def render_prompt(self, metadata):
        lines = []
        for index, episode in enumerate(metadata["episodes"], 1):
            bindings = "; ".join(
                f"{feature} = {value} (response {response})"
                for feature, value, response in episode
            )
            lines.append(f"Episode {index}: {bindings}")
        query = metadata["query_feature"]
        lines.append(
            f"Using the recency rule that the most recent episode containing a "
            f"feature overrides all earlier bindings of that feature, which "
            f"response is bound to the feature '{query}' in its latest episode? "
            f"Distractors appear in older episodes."
        )
        lines.append("Answer with the single response token only.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        return float(isinstance(answer, str) and answer.strip() == entry.answer)
