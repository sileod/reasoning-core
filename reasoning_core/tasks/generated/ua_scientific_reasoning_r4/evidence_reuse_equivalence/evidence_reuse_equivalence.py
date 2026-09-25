"""Evidence reuse equivalence: do two derivations draw on the same set of premises?

Each derivation cites sentence identifiers from a fixed universe. A premise may be
cited more than once, but as an identifier it still names one sentence, so the
support set ignores multiplicity. Two derivations that cite the same identifier a
different number of times, or in a different order, draw on the same support set;
two that differ in which identifiers appear do not. The answer is 'yes' or 'no'.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'evidence_reuse_equivalence (variant 1 of 3)',
 'hypothesis': 'P012',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scientific_reasoning_r4/evidence_reuse_equivalence',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1277236794,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = ("Present pairs of formal proof fragments where the same premise is "
                 "cited twice versus two distinct premises, asking whether the "
                 "support sets are equal as sets of sentence identifiers.")

_IDS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']


def _expand(support, max_mult):
    """Build a shuffled citation list over `support` with multiplicity in 1..max_mult.

    Guarantee at least one duplicated identifier whenever possible, so the
    multiplicity-versus-identity distinction is exercised on most instances.
    """
    out = []
    for i, x in enumerate(sorted(support)):
        m = random.randint(1, max_mult)
        if i == 0 and max_mult >= 2 and random.random() < 0.8:
            m = random.randint(2, max_mult)
        out.extend([x] * m)
    random.shuffle(out)
    return out


def build_prompt(metadata):
    ids = ', '.join(metadata['ids'])
    f1 = ', '.join(metadata['frag1'])
    f2 = ', '.join(metadata['frag2'])
    return (
        f"The fixed universe of sentence identifiers is {{{ids}}}. Two derivations "
        f"each cite sentence premises from this universe. A premise may be cited "
        f"more than once inside a derivation, but as an identifier it still names "
        f"one sentence, so the support set of a derivation ignores how many times "
        f"each identifier is cited and the order of citation. Do the two derivations "
        f"draw on the same support set of sentence identifiers? Answer exactly "
        f"yes or no.\n\n"
        f"Derivation 1 cites: {f1}\n"
        f"Derivation 2 cites: {f2}"
    )


@dataclass
class EvidenceReuseEquivalenceConfig(Config):
    universe: int = 4
    set_size: int = 2
    max_mult: int = 2

    def apply_difficulty(self, level):
        self.universe = stochastic_rounding(self.universe + level)
        self.set_size = stochastic_rounding(self.set_size + level)
        self.max_mult = stochastic_rounding(self.max_mult + level)


class EvidenceReuseEquivalence(Task):
    summary = ("Compare two derivations' premise citations drawn from a fixed "
               "universe of sentence identifiers; repeated use of one source versus "
               "two distinct premises, alternative orderings and different "
               "multiplicities; decide whether the support sets coincide as sets of "
               "identifiers, answering yes or no.")
    config_cls = EvidenceReuseEquivalenceConfig
    task_version = 2
    design_choice = design_choice

    def generate_entry(self):
        cfg = self.config
        universe = min(int(cfg.universe), len(_IDS))
        universe = max(universe, 2)
        size = max(int(cfg.set_size), 1)
        size = min(size, universe)
        max_mult = max(int(cfg.max_mult), 1)
        ids = _IDS[:universe]

        for _attempt in range(400):
            label = random.choice(['yes', 'no'])
            if label == 'yes':
                support = random.sample(ids, size)
                frag1 = _expand(support, max_mult)
                frag2 = _expand(support, max_mult)
                if frag1 == frag2:
                    random.shuffle(frag2)
                if set(frag1) == set(frag2) and set(frag1) == set(support):
                    return Entry(
                        metadata={
                            'ids': list(ids),
                            'frag1': frag1,
                            'frag2': frag2,
                        },
                        answer='yes',
                    )
            else:
                overlap = random.randint(1, min(size, universe - 1))
                base = random.sample(ids, size)
                extra = random.sample([x for x in ids if x not in base],
                                      min(universe - size, size))
                if not extra:
                    continue
                s1 = list(base)
                s2 = base[:overlap] + extra
                frag1 = _expand(s1, max_mult)
                frag2 = _expand(s2, max_mult)
                if set(frag1) != set(frag2):
                    return Entry(
                        metadata={
                            'ids': list(ids),
                            'frag1': frag1,
                            'frag2': frag2,
                        },
                        answer='no',
                    )

        raise RuntimeError('evidence_reuse_equivalence: failed to build instance')

    def render_prompt(self, metadata):
        return build_prompt(metadata)

    def score_answer(self, answer, entry):
        s = str(answer).strip().lower()
        if s not in ('yes', 'no'):
            return 0.0
        return 1.0 if s == entry.answer else 0.0
