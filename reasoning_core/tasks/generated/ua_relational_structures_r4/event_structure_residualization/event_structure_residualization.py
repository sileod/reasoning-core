"""Event structure residualization: which events remain enabled after a configuration.

Represent an event structure as integer event IDs with sets of causal pairs (a -> b,
a must complete before b, hence a < b in id order) and conflict pairs (a # b, the two
cannot both be completed). A configuration is a downward-closed, conflict-free subset
of completed events. After it, an uncompleted event remains enabled iff it conflicts
with no completed event and every event that must complete before it has completed.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'event_structure_residualization (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_relational_structures_r4/event_structure_residualization',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _parse_ids(value):
    """Parse a canonical answer (e.g. '[3, 5]', '[]', or bare '3 5') into sorted ints.

    Whitespace/empty strings parse to None (a non-answer); a literal '[]' parses to an
    empty list (a valid answer). Non-integer garbage parses to None.
    """
    text = str(value).strip()
    if not text:
        return None
    if len(text) >= 2 and text[0] == "[" and text[-1] == "]":
        inner = text[1:-1]
    else:
        inner = text
    if inner.strip() == "":
        return []
    out = []
    for token in inner.replace(",", " ").split():
        try:
            out.append(int(token))
        except ValueError:
            return None
    return sorted(set(out))


def _fmt(ids):
    return "[" + ", ".join(str(i) for i in sorted(ids)) + "]"


def _score(answer, entry):
    gold = _parse_ids(entry.answer)
    got = _parse_ids(answer)
    if gold is None or got is None:
        return 0.0
    return 1.0 if got == gold else 0.0


@dataclass
class EventResidualConfig(Config):
    n_events: int = 4
    max_conflicts: int = 2
    config_seed: int = 2

    def apply_difficulty(self, level):
        self.n_events = 4 + 2 * level
        self.max_conflicts = 2 + level
        self.config_seed = 2 + level


class EventStructureResidualization(Task):
    summary = ("Residualize finite event structures after a configuration: discharge "
               "completed causes, exclude conflicting alternatives, and retain inherited "
               "conflicts; answer which events remain enabled as the sorted list of "
               "enabled event IDs.")
    design_choice = ("Represent each event as a unique integer ID, with the residual "
                     "structure encoded as a set of integer pairs for causal edges and a "
                     "set of integer triples for conflict edges, and the answer as a "
                     "sorted list of enabled event IDs.")
    config_cls = EventResidualConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_events
        ids = list(range(1, n + 1))

        # The most common failure mode of rejection loops is a top level whose search
        # never terminates. We build the whole instance inside a bounded inner loop and
        # prefer a non-empty enabled set so that no single label (especially the empty
        # set) dominates the answer prior; empty is still occasionally produced.
        for _ in range(10):
            causal_pairs = set()
            for e in ids[1:]:
                lower = [i for i in ids if i < e]
                k = 1 if random.random() < 0.45 else 2
                k = min(k, len(lower))
                for c in random.sample(lower, k):
                    causal_pairs.add((c, e))
            causal_edges = sorted(causal_pairs)

            rev = {}
            for a, b in causal_edges:
                rev.setdefault(b, []).append(a)

            # The configuration is the downward closure of a set of seed events: add
            # every transitive cause, so it is downward closed by construction.
            seed_events = random.sample(ids, min(cfg.config_seed, n))
            config_set = set()
            stack = list(seed_events)
            while stack:
                x = stack.pop()
                if x in config_set:
                    continue
                config_set.add(x)
                for parent in rev.get(x, ()):
                    stack.append(parent)

            residual = sorted(set(ids) - config_set)

            # Conflicts must not join two already-completed events (the configuration
            # must stay conflict-free); they may join a completed with an uncompleted
            # event (exclusion) or two uncompleted events (inherited conflict).
            conflict_pairs = set()
            attempts = 0
            while len(conflict_pairs) < cfg.max_conflicts and attempts < 60:
                attempts += 1
                u, v = random.sample(ids, 2)
                if u == v:
                    continue
                if u in config_set and v in config_set:
                    continue
                conflict_pairs.add(tuple(sorted((u, v))))
            conflict_edges = sorted(conflict_pairs)

            # An uncompleted event that conflicts with a completed event is excluded.
            excluded = set()
            for a, b in conflict_edges:
                if a in config_set:
                    excluded.add(b)
                if b in config_set:
                    excluded.add(a)

            # Enabled: uncompleted, not excluded, every cause already completed.
            enabled = []
            for e in residual:
                if e in excluded:
                    continue
                if all(parent in config_set for parent in rev.get(e, ())):
                    enabled.append(e)
            enabled = sorted(enabled)

            if enabled:
                break

        # Defining invariants: the enabled set is a subset of the residual that is free
        # of completed-caused exclusion and whose every cause is completed.
        assert all(e not in config_set and e not in excluded
                   and all(p in config_set for p in rev.get(e, ()))
                   for e in enabled)
        assert all(e in residual for e in enabled)
        for a, b in conflict_edges:
            if a in config_set:
                assert b not in enabled
            if b in config_set:
                assert a not in enabled

        metadata = {
            "ids": ids,
            "causal": [list(p) for p in causal_edges],
            "conflict": [list(p) for p in conflict_edges],
            "config": sorted(config_set),
            "enabled": enabled,
        }
        return Entry(metadata=metadata, answer=_fmt(enabled))

    def render_prompt(self, metadata):
        ids = ", ".join(str(i) for i in metadata["ids"])
        causal = ", ".join(f"{a} -> {b}" for a, b in metadata["causal"]) or "none"
        conflict = ", ".join(f"{a} # {b}" for a, b in metadata["conflict"]) or "none"
        config = ", ".join(str(i) for i in metadata["config"]) or "none"
        return (
            f"An event structure over events {{{ids}}} has causality edges (a -> b "
            f"means event a must complete before event b can) and conflict edges "
            f"(a # b means events a and b cannot both complete).\n"
            f"Causality: {causal}\n"
            f"Conflict: {conflict}\n"
            f"Configuration completed: {{{config}}}\n"
            f"After this configuration, which events remain enabled? An event that has "
            f"not completed remains enabled when it conflicts with no completed event "
            f"and every event that must complete before it has already completed.\n"
            f"Answer with the sorted list of enabled event IDs, e.g. [3, 5]; [] if none."
        )

    def score_answer(self, answer, entry):
        return _score(answer, entry)
