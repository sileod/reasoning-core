"""Semantic reconstruction sites.

Under the copy theory of movement a displaced phrase leaves copies at the
positions it has moved through, and its semantic interpretation may be
"reconstructed" to (re)-read at any of those copy sites.  Here a structure is
generated as an ordered spine of positions together with several displaced
phrases (fronted, raised, or nested movements); each displaced phrase owns an
interval of spine positions that host its possible copy sites, labelled with a
unique letter.  Scope, binding and idiom conditions constrain how the phrases
may jointly be reconstructed (each phrase reconstructs to exactly one of its
sites, and every condition must hold at once).  A site is a *licensed
interpretation copy* when it participates in at least one jointly admissible
reconstruction.

The gold answer is computed by exhaustive search over every joint assignment of
phrases to their copy positions (bounded: a handful of phrases with short
intervals), so the verdict for every labelled site is mechanically verified, not
hand-analyzed.  The standard algorithm named in the prompt is copy-theory
reconstruction constrained by scope, binding, and idiom reconstruction.
"""

import random
from itertools import product
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'semantic_reconstruction_sites (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_synthetic_grammars_r4/semantic_reconstruction_sites',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1336314872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = ("Answer as a balanced yes/no per candidate copy site, where each site is labeled "
                 "with a letter and the solver outputs the subset of letters that jointly satisfy "
                 "the constraints.")

MOVEMENTS = ["fronting", "raising", "nested movement"]
Q_NAMES = ["every critic", "no teacher", "some lawyer", "few artists", "all students",
           "each senator", "most doctors", "any reviewer"]
B_NAMES = ["Ana", "Ben", "Cora", "Dan", "Eli", "Fay", "Gil", "Hal", "Ira",
           "Jill", "Ken", "Lia", "Max", "Nora", "Owen", "Pia", "Quinn"]
IDIOMS = ["strings", "beans", "tabs", "favors", "corners", "time"]
PREDICATES = ["pulled", "spilled", "kept", "owed", "cut", "bought"]
PRONOUNS = ["her", "him", "them"]


def _check(assign, constraints):
    for c in constraints:
        t = c[0]
        if t == "order":
            _, i, j, rel = c
            vi, vj = assign[i], assign[j]
            if rel == "lt" and not (vi < vj):
                return False
            if rel == "gt" and not (vi > vj):
                return False
        elif t == "idiom":
            _, i, pos = c
            if assign[i] != pos:
                return False
    return True


def _satisfying(intervals, constraints):
    ranges = [range(lo, hi + 1) for (lo, hi) in intervals]
    out = []
    for assign in product(*ranges):
        if _check(assign, constraints):
            out.append(assign)
    return out


def _build(level):
    for _ in range(400):
        L = 4 + level
        nchain = 3 + (level // 2)
        width = 2 if level >= 3 else 3
        intervals = []
        kinds = []
        for k in range(nchain):
            w = min(width, L)
            w = random.randint(1, w)
            lo = random.randint(0, L - w)
            intervals.append((lo, lo + w - 1))
            kinds.append(random.choice(MOVEMENTS))

        constraints = []
        for _ in range(2 + level):
            i, j = random.sample(range(nchain), 2)
            li, hi = intervals[i]
            lj, hj = intervals[j]
            if max(li, lj) > min(hi, hj):
                continue
            rel = random.choice(["lt", "gt"])
            trial = list(constraints) + [("order", i, j, rel)]
            if not _satisfying(intervals, trial):
                continue
            constraints = trial

        for i, (k, (lo, hi)) in enumerate(zip(kinds, intervals)):
            if k == "nested movement" and constraints:
                continue
            if random.random() < 0.35:
                pos = random.randint(lo, hi)
                constraints.append(("idiom", i, pos))

        if not constraints:
            continue

        satisfiers = _satisfying(intervals, constraints)
        if not satisfiers:
            continue

        sites = []
        letter = 0
        for i, (lo, hi) in enumerate(intervals):
            for p in range(lo, hi + 1):
                sites.append((chr(ord("A") + letter), i, p))
                letter += 1
        if letter > 20:
            continue

        yes = set()
        for assign in satisfiers:
            for _, i, p in sites:
                if assign[i] == p:
                    yes.add((i, p))
        gold = [s[0] for s in sites if (s[1], s[2]) in yes]
        no_count = sum(1 for s in sites if (s[1], s[2]) not in yes)
        if not gold or not no_count:
            continue
        return dict(L=L, intervals=intervals, kinds=kinds,
                    constraints=constraints, sites=sites, gold=gold)
    raise RuntimeError("could not build a reconstruction instance")


class ReconstructionConfig(Config):
    level: int = 0

    def apply_difficulty(self, level):
        self.level = level


class SemanticReconstructionSites(Task):
    summary = ("Locate licensed interpretation copies of displaced phrases under binding, scope, "
               "and idiom constraints; vary fronting, raising, and nested movement, returning all "
               "jointly admissible copy choices.")
    config_cls = ReconstructionConfig

    def generate_entry(self):
        data = _build(self.config.level)
        sites = data["sites"]
        intervals = data["intervals"]
        gold = data["gold"]
        answer = " ".join(gold)

        phrase_names = []
        for idx, k in enumerate(data["kinds"]):
            phrase_names.append(f"{idx + 1}: {_phrase_surface(idx, k)}")

        constraints = _describe_constraints_friendly(data)

        return Entry(
            metadata={
                "spine_length": data["L"],
                "phrase_names": phrase_names,
                "constraints": constraints,
                "sites": [(s[0], s[1] + 1, s[2] + 1) for s in sites],
                "gold": gold,
                "intervals": intervals,
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        spine = " ".join(f"P{i + 1}" for i in range(metadata["spine_length"]))
        lines = [
            "Under the copy theory of movement, each displaced phrase may reconstruct its "
            "semantic interpretation to any of its possible copy sites, but all phases must be "
            "jointly admissible: every phrase reconstructs to exactly one site and every scope, "
            "binding and idiom condition below must hold at the same time. A site is a licensed "
            "interpretation copy when it can belong to some jointly admissible reconstruction.",
            "",
            "Spine of positions (highest to lowest): " + spine,
            "",
            "Displaced phrases:",
        ]
        for name in metadata["phrase_names"]:
            lines.append("  " + name)
        lines += ["", "Conditions:"]
        for c in metadata["constraints"]:
            lines.append("  - " + c)
        lines += ["", "Candidate copy sites (letter: phrase copy at position):"]
        for letter, i, p in metadata["sites"]:
            lines.append(f"  {letter}: copy of phrase {i} at position P{p}")
        lines.append(
            "Report, in increasing alphabetical order and separated by single spaces, every site "
            "letter that is a licensed interpretation copy. Example format: 'B D'."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        gold = set(entry.answer.split())
        parsed = set(ch for ch in answer if "A" <= ch <= "Z")
        return 1.0 if parsed == gold else 0.0


def _phrase_surface(idx, kind):
    if kind == "nested movement":
        return f"{random.choice(B_NAMES)}"
    return f"{random.choice(Q_NAMES)}"


def _describe_constraints_friendly(data):
    parts = []
    for c in data["constraints"]:
        t = c[0]
        if t == "order":
            _, i, j, rel = c
            if rel == "lt":
                parts.append(f"phrase {i + 1} must reconstruct strictly above phrase {j + 1} "
                             f"(scope/binding)")
            else:
                parts.append(f"phrase {j + 1} must reconstruct strictly above phrase {i + 1} "
                             f"(scope/binding)")
        else:
            _, i, pos = c
            parts.append(f"the idiom chunk of phrase {i + 1} must reconstruct to position P{pos + 1}")
    return parts
