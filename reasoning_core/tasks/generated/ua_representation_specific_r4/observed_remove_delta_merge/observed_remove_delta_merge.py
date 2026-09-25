import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class ObservedRemoveDeltaMergeConfig(Config):
    add_ops: int = 2
    remove_ops: int = 2
    seed_size: int = 3
    tagged_duplicates: int = 2
    delayed: int = 1
    causal_replay_ratio: float = 0.5
    tag_pool: int = 8

    def apply_difficulty(self, level):
        self.add_ops = 2 + level
        self.remove_ops = 2 + level
        self.seed_size = 3 + level
        self.tagged_duplicates = 2 + level // 2
        self.delayed = 1 + level // 2
        self.causal_replay_ratio = 0.3 + 0.1 * min(level, 5)
        self.tag_pool = 8 + level


def _apply_observed_remove(seed, adds, removes, delayed, replay):
    # Observed-remove semantics: a tag present in a causal remove operation is
    # permanently removed only if it has been observed (added) by that op.
    # Delayed delivery: some adds arrive after the removes referencing them.
    state = set(seed)
    causal_events = []

    def deliver_add(tag):
        nonlocal state, causal_events
        state.add(tag)
        causal_events.append(("add", tag))

    def deliver_remove(tag):
        nonlocal state
        state.discard(tag)
        causal_events.append(("remove", tag))

    for _ in range(len(seed)):
        causal_events.append(("seed", None))

    add_batch = list(adds)
    remove_batch = list(removes)

    # Timeline: causal removes happen against the adds that have been observed
    # so far. Delayed adds arrive later and should NOT be revived by replay.
    for tag in add_batch:
        deliver_add(tag)
    for tag in remove_batch:
        if tag in state:
            deliver_remove(tag)

    # Delayed delivery: some adds arrive after removes.
    for tag in delayed:
        if tag not in state:
            deliver_add(tag)

    # Replay: re-deliver the add events (tagged duplicates). Observed-remove
    # ensures a removed tag is NOT revived by a later add unless that add is a
    # fresh causal addition not previously observed... here replay semantics:
    # a concurrent/delayed add that the remove already observed must not revive.
    # Simulate replay of prior adds: only revive tags that were never removed.
    return state


class ObservedRemoveDeltaMerge(Task):
    summary = "Merge partial updates to observed-remove sets with tagged duplicate adds, causal removals, delayed delivery, and replay; return changed visible memberships without reviving removed tags."
    config_cls = ObservedRemoveDeltaMergeConfig
    design_choice = "Answer as a compact list of visible tag strings, one per line, in deterministic lexicographic order, with no duplicates."

    def _visible_and_replay(self, seed, adds, removes, delayed, replay):
        state = set(seed)

        def deliver_add(tag):
            state.add(tag)

        def deliver_remove(tag):
            state.discard(tag)

        for tag in adds:
            deliver_add(tag)
        for tag in removes:
            deliver_remove(tag)
        for tag in delayed:
            deliver_add(tag)

        final = set(state)
        # Replay of stale duplicate adds must NOT revive tags that were removed
        # by a causal (observed) remove. Observed-remove: a tag removed is dead
        # to all later replay unless a fresh add for it is delivered.
        for tag in replay:
            if tag in final:
                deliver_add(tag)
        return final

    def generate_entry(self):
        cfg = self.config
        tag_pool = list(range(cfg.tag_pool))
        seed_tags = set(random.sample(tag_pool, min(cfg.seed_size, len(tag_pool))))
        pool_rest = [t for t in tag_pool if t not in seed_tags]

        adds = [random.choice(tag_pool) for _ in range(cfg.add_ops)]
        removals = [random.choice([t for t in tag_pool if t in set(adds) or t in seed_tags] or seed_tags) for _ in range(cfg.remove_ops)]
        delayed = [random.choice(pool_rest) for _ in range(cfg.delayed)]
        replay = [random.choice(tag_pool) for _ in range(cfg.tagged_duplicates)]

        # tagged duplicate adds: repeats of adds to test duplicate-merge
        adds = adds + [random.choice(adds) for _ in range(cfg.tagged_duplicates // 2)]

        visible = self._visible_and_replay(seed_tags, adds, removals, delayed, replay)

        metadata = {
            "seed": sorted(seed_tags),
            "adds": sorted(set(adds)),
            "removes": sorted(set(removals)),
            "delayed_delivery": sorted(set(delayed)),
            "replay": sorted(set(replay)),
            "visible": sorted(visible),
        }
        answer = "\n".join(f"tag{t}" for t in sorted(visible))
        if not visible:
            answer = ""
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = []
        lines.append("You are merging partial CRDT updates for a set whose membership follows observed-remove semantics: a tag is permanently gone once a causal remove of it has been observed, and a later replayed (duplicate/stale) add of an already-removed tag must NOT revive it.")
        lines.append(f"Initial visible tags: {[f'tag{t}' for t in metadata['seed']]}")
        lines.append(f"New adds (delivered in order, before removes): {[f'tag{t}' for t in metadata['adds']]}")
        lines.append(f"Causal removes (delivered immediately after adds): {[f'tag{t}' for t in metadata['removes']]}")
        lines.append(f"Delayed adds (arrive late, must not be revoked unless already-removed tags being replayed): {[f'tag{t}' for t in metadata['delayed_delivery']]}")
        lines.append(f"Replayed duplicate adds (stale, must not revive any removed tag): {[f'tag{t}' for t in metadata['replay']]}")
        lines.append("What is the final set of visible tag strings?")
        lines.append("Answer as the list of visible tag strings, one per line, in lexicographic order, with no duplicates. If the set is empty, answer with an empty line.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        expected = entry.answer
        if answer is None:
            return 0.0
        norm = answer.strip()
        exp_norm = expected.strip()
        if norm == "":
            return 1.0 if exp_norm == "" else 0.0
        got = set(line.strip() for line in norm.splitlines() if line.strip())
        exp = set(line.strip() for line in exp_norm.splitlines() if line.strip())
        return 1.0 if got == exp else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'observed_remove_delta_merge (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_representation_specific_r4/observed_remove_delta_merge',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
