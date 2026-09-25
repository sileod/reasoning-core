import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Reward, Task


FEATURE_SYMBOLS = ("red", "green", "blue", "black", "white")
FEATURE_DEG = {"red": 0.0, "green": 45.0, "blue": 90.0, "black": 135.0, "white": 180.0}


def _perceived(nbr, wts):
    total = sum(wts)
    num = sum(FEATURE_DEG[f] * w for f, w in zip(nbr, wts))
    mean = num / total
    return min(FEATURE_SYMBOLS, key=lambda s: abs(FEATURE_DEG[s] - mean))


@dataclass
class CrowdingConfig(Config):
    num_items: int = 3
    extra: int = 1

    def apply_difficulty(self, level):
        self.num_items = 3 + level
        self.extra = 1 + level


class VisualCrowdingFeaturePooling(Task):
    summary = ("Recover reported target features under weighted spatial feature pooling; vary "
               "eccentricity-dependent neighborhoods, segmentation barriers, flanker weights, and "
               "successive pooling stages; answer the perceived feature symbol.")
    design_choice = ("Answer as a canonical feature symbol (e.g., 'red' or '45deg') chosen from a "
                     "fixed small set, with the perceived feature derived by weighted averaging of "
                     "target and flanker features within a defined neighborhood.")
    config_cls = CrowdingConfig

    def _level(self):
        return self.config.num_items - 3

    def generate_entry(self):
        level = self._level()
        num = self.config.num_items
        multi_stage = level >= 3
        barrier = (level >= 5) and random.random() < 0.5

        target_idx = random.randint(0, num - 1)
        target = random.choice(FEATURE_SYMBOLS)
        others = [random.choice(FEATURE_SYMBOLS) for _ in range(num - 1)]
        items = others[:]
        items.insert(target_idx, target)

        neighborhood = set(range(num))
        barrier_pos = None
        if barrier:
            barrier_pos = random.randint(1, num - 1)
            group = 0 if target_idx < barrier_pos else 1
            if group == 0:
                neighborhood = set(range(barrier_pos))
            else:
                neighborhood = set(range(barrier_pos, num))

        weights = []
        for i in range(num):
            if i == target_idx:
                weights.append(round(random.uniform(0.5, 2.0), 2))
            elif random.random() < 0.35:
                weights.append(0.0)
            else:
                weights.append(round(random.uniform(0.0, 0.7), 2))
        if barrier:
            for i in range(num):
                if i not in neighborhood:
                    weights[i] = 0.0

        if multi_stage:
            for _ in range(2):
                new = []
                for i in range(num):
                    d = abs(target_idx - i)
                    new.append(round(weights[i] / (1.0 + 0.5 * d), 2))
                weights = new

        nbr = sorted(neighborhood)
        used = [items[i] for i in nbr]
        used_w = [weights[i] for i in nbr]
        perceived = _perceived(used, used_w)
        assert perceived in FEATURE_SYMBOLS
        assert target_idx in neighborhood, "target must be in neighborhood"
        assert sum(weights) > 0.0

        metadata = {
            "num_items": num,
            "target_idx": target_idx,
            "elements": items,
            "neighborhood": nbr,
            "barrier_pos": barrier_pos,
            "weights": [float(w) for w in weights],
            "multi_stage": multi_stage,
        }
        return Entry(metadata=metadata, answer=perceived)

    def render_prompt(self, metadata):
        mapping = ", ".join("{s}={d}".format(s=s, d=int(FEATURE_DEG[s]))
                            for s in FEATURE_SYMBOLS)
        body = []
        for i, f in enumerate(metadata["elements"]):
            body.append("position {i}: feature {f}, pooling weight {w}".format(
                i=i, f=f, w=metadata["weights"][i]))
        barrier = ""
        if metadata["barrier_pos"] is not None:
            barrier = (" A segmentation barrier separates positions 0..{lo} from the rest; only the "
                       "target's partition is pooled, items outside it get weight 0.").format(
                lo=metadata["barrier_pos"] - 1)
        stage = ""
        if metadata["multi_stage"]:
            stage = (" Two successive pooling stages are applied: at each stage every item's weight "
                     "is divided by (1 + half its distance in positions from the target), "
                     "attenuating farther flankers.")
        prompt = (
            "Feature degrees: {mapping}. Features pool as the weighted mean of the degrees of "
            "pooled items, using each item's pooling weight; tie rounds to the lower degree. "
            "Pooled items are those in the target's pooling neighborhood (all items unless a "
            "barrier narrows it).\nItems:\n{body}\nTarget at position {t}.{b}{st} Report the "
            "perceived feature (the nearest symbol to the pooled mean) as one symbol from "
            "{full}."
        ).format(
            mapping=mapping,
            body="\n".join(body),
            t=metadata["target_idx"],
            b=barrier,
            st=stage,
            full=list(FEATURE_SYMBOLS),
        )
        return prompt

    def score_answer(self, answer, entry):
        if answer == entry.answer:
            return 1.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'visual_crowding_feature_pooling (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_cognitive_psychology_r4/visual_crowding_feature_pooling',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
