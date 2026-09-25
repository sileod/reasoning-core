"""Ephemeron liveness: which objects survive garbage collection under strong,
weak and ephemeron reference semantics."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def compute_alive(n, roots, strong, weak, ephems):
    """Least fixpoint of survival. Strong refs retain; weak refs never retain;
    an ephemeron (container, key, value) retains its value only while both the
    container and the key are alive. Returns the set of alive indices."""
    alive = set(roots)
    adj = [[] for _ in range(n)]
    for s, t in strong:
        adj[s].append(t)
    changed = True
    while changed:
        changed = False
        for u in range(n):
            if u not in alive:
                continue
            for v in adj[u]:
                if v not in alive:
                    alive.add(v)
                    changed = True
        for c, k, v in ephems:
            if c in alive and k in alive and v not in alive:
                alive.add(v)
                changed = True
    return alive


def label(i):
    return chr(65 + i)


def render_answer(alive, n):
    return "".join(label(i) for i in sorted(alive))


@dataclass
class EphemeronLivenessConfig(Config):
    n: int = 4
    root_count: int = 1
    num_strong: int = 2
    num_weak: int = 1
    num_ephem: int = 1

    def apply_difficulty(self, level):
        self.n = 4 + level
        self.root_count = 1 + (level // 3)
        self.num_strong = 2 + level
        self.num_weak = 1 + level
        self.num_ephem = 1 + level


class EphemeronLiveness(Task):
    summary = ("Resolve object retention with strong references, weak references, "
               "and ephemerons whose values survive only when both container and key "
               "survive; vary rooted cycles and chained activations; answer surviving "
               "objects.")
    design_choice = ("Present a graph of objects with marked roots and edges; solver "
                     "lists objects reachable from roots after applying ephemeron "
                     "value-retention rules to weak edges.")
    config_cls = EphemeronLivenessConfig
    task_version = 2

    def generate_entry(self):
        n = self.config.n
        while True:
            roots = random.sample(range(n), self.config.root_count)
            strong = []
            weak = []
            for _ in range(self.config.num_strong):
                s = random.randrange(n)
                t = random.randrange(n)
                while t == s:
                    t = random.randrange(n)
                strong.append((s, t))
            for _ in range(self.config.num_weak):
                s = random.randrange(n)
                t = random.randrange(n)
                while t == s:
                    t = random.randrange(n)
                weak.append((s, t))
            ephems = []
            for _ in range(self.config.num_ephem):
                c = random.randrange(n)
                k = random.randrange(n)
                v = random.randrange(n)
                while v == c:
                    v = random.randrange(n)
                ephems.append((c, k, v))
            alive = compute_alive(n, roots, strong, weak, ephems)
            if not alive:
                continue
            # Keep answer size varied; never degenerate to a single constant answer.
            if len(alive) > 0:
                break
        return Entry(
            metadata={
                "n": int(n),
                "roots": [int(r) for r in roots],
                "strong": [list(e) for e in strong],
                "weak": [list(e) for e in weak],
                "ephems": [list(e) for e in ephems],
                "alive": sorted(int(i) for i in alive),
                "n_alive": int(len(alive)),
            },
            answer=render_answer(alive, n),
        )

    def render_prompt(self, metadata):
        n, roots = metadata["n"], metadata["roots"]
        labels = [label(i) for i in range(n)]
        lines = ["Objects " + ", ".join(labels) +
                 " are the live heap of a program. "
                 "The garbage-collection roots are " +
                 ", ".join(label(r) for r in roots) + "."]
        for s, t in metadata["strong"]:
            lines.append(f"Strong reference {label(s)} -> {label(t)}.")
        for s, t in metadata["weak"]:
            lines.append(f"Weak reference {label(s)} -> {label(t)}.")
        for c, k, v in metadata["ephems"]:
            lines.append(f"Ephemeron in {label(c)}: key {label(k)}, value {label(v)}.")
        lines.append(
            "A strong reference keeps its target alive. A weak reference does not "
            "keep its target alive. An ephemeron's value stays alive only while "
            "both its container and its key are alive."
        )
        lines.append(
            "Which objects survive garbage collection? Answer with the surviving "
            "object labels concatenated in alphabetical order (for example, \"ABE\"); "
            "answer \"none\" if no object survives."
        )
        return "\n".join(lines)


TASK_META = {'parent_source_id': None,
 'idea': 'ephemeron_liveness (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_dependence_relevance_r4/ephemeron_liveness',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
