import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class MenuAttentionConfig(Config):
    level: int = 0
    max_items: int = 4

    def apply_difficulty(self, level):
        self.level = level
        self.max_items = 3 + level


_LETTERS = "ABCDEFGHIJ"


def _select(first, second, attention, rank):
    """Highest-preferred considered item, or the first-listed item (default) if none considered."""
    considered = [it for it in (first, second) if it in attention]
    if considered:
        return min(considered, key=lambda it: rank[it])
    return first


def _setup_text(m):
    return (
        "A customer may select among the items "
        f"{', '.join(m['candidates'])}. "
        "Its stated preferences, most preferred first, are: "
        f"{', '.join(m['pref'])}. "
        "The customer attends to (considers) exactly the items in its attention set "
        f"{{ {', '.join(m['attention'])} }}; an item outside this set is not considered "
        "and can never be selected. When choosing from a two-item menu the customer scans "
        "both offered items, considers those lying in its attention set, and selects the one "
        "it ranks highest; if it considers neither offered item, it selects the first-listed "
        "item of the menu (the default)."
    )


class MenuAttentionAbduction(Task):
    summary = ("Separate stated preference from limited consideration using forced two-item menu "
               "choices under stated attention and default axioms; vary preference order, attention "
               "set, defaults, and distractors as the item pool expands; return balanced binary "
               "preference-selection or attention-membership relations.")
    config_cls = MenuAttentionConfig
    task_version = 2

    design_choice = ("Answer format: binary forced-choice between two candidate relations "
                     "(e.g., 'prefers X' vs 'prefers Y') for each query, with balanced labels.")

    def _base_scene(self):
        cfg = self.config
        count = random.randint(3, cfg.max_items)
        items = list(_LETTERS[:count])
        pref = random.sample(items, len(items))
        rank = {it: i for i, it in enumerate(pref)}
        attn_size = random.randint(1, len(items))
        attention = random.sample(items, attn_size)
        return items, pref, rank, attention

    def generate_entry(self):
        kind = random.choice(["preference", "attention"])
        if kind == "preference":
            items, pref, rank, attention = self._base_scene()
            x, y = random.sample(items, 2)
            target = random.choice([x, y])
            other = y if target == x else x
            template = random.choice(["both", "limited", "default"])
            if template == "both":
                if rank[other] < rank[target]:
                    pref = [it for it in pref if it not in (target, other)]
                    pref = [target, other] + pref
                    rank = {it: i for i, it in enumerate(pref)}
                attention = sorted([target, other])
                first, second = random.sample([x, y], 2)
            elif template == "limited":
                attention = [target]
                first, second = random.sample([x, y], 2)
            else:
                attention = sorted(z for z in items if z not in (target, other))
                first, second = target, other
            gold = _select(first, second, attention, rank)
            assert gold == target, (pref, attention, rank, first, second, gold, target)
            metadata = {
                "kind": "preference",
                "candidates": items,
                "pref": pref,
                "attention": attention,
                "menu": [first, second],
                "answer": gold,
            }
        else:
            items, pref, rank, attention = self._base_scene()
            q = random.choice(items)
            target = random.choice(["yes", "no"])
            if target == "yes":
                attention = sorted(set(attention) | {q})
            else:
                attention = sorted(z for z in attention if z != q)
            gold = "yes" if q in attention else "no"
            assert gold == target, (q, attention, gold, target)
            metadata = {
                "kind": "attention",
                "candidates": items,
                "pref": pref,
                "attention": attention,
                "query": q,
                "answer": gold,
            }

        return Entry(metadata=metadata, answer=gold)

    def render_prompt(self, metadata):
        m = metadata
        body = _setup_text(m)
        if m["kind"] == "preference":
            return (
                body
                + f"\n\nGiven a menu that offers exactly {m['menu'][0]} and {m['menu'][1]}, "
                f"which of these two items does the customer select? "
                f"Name that single item label."
            )
        return (
            body
            + f"\n\nFocus on the item {m['query']}. "
            f"Is it part of the customer's attention set right now? "
            f"Answer with a single word."
        )

    def score_answer(self, answer, entry):
        gold = entry["answer"]
        if isinstance(answer, str):
            return 1.0 if answer.strip().lower() == str(gold).strip().lower() else 0.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'menu_attention_abduction (variant 2 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_inference_modes_r4/menu_attention_abduction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1211525277,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
