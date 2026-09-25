"""Diffraction motif abduction v2.

A hidden cyclic motif of signed phase weights produces a reflection mask through
the phase-addition (cyclic autocorrelation) rule. Given the observed mask, infer
any motif whose reflections reproduce it.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'diffraction_motif_abduction (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_uncertainty_r4/diffraction_motif_abduction',
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

_SYMBOLS = ('+', '-', '0')


def _weights(motif):
    return [1 if c == '+' else (-1 if c == '-' else 0) for c in motif]


def _autocorr(weights):
    length = len(weights)
    return [
        sum(weights[i] * weights[(i + k) % length] for i in range(length))
        for k in range(length)
    ]


def _full_mask(weights):
    return ['1' if value != 0 else '0' for value in _autocorr(weights)]


def _reproduces(weights, mask):
    """Check the motif reproduces every observed ('1'/'0') mask entry."""
    if len(weights) != len(mask):
        return False
    autocorr = _autocorr(weights)
    for value, entry in zip(autocorr, mask):
        if entry == '?':
            continue
        target = entry == '1'
        if (value != 0) != target:
            return False
    return True


def _parse_motif(answer):
    if not isinstance(answer, str):
        return None
    motif = answer.strip()
    if not motif:
        return None
    if not all(c in _SYMBOLS for c in motif):
        return None
    return motif


def _score_motif(answer, entry):
    motif = _parse_motif(answer)
    if motif is None:
        return 0.0
    period = entry.metadata.get('period')
    if period is None or len(motif) != period:
        return 0.0
    mask = entry.metadata.get('mask')
    if mask is None or len(mask) != period:
        return 0.0
    base = _weights(motif)
    for shift in range(period):
        rotated = base[shift:] + base[:shift]
        if _reproduces(rotated, mask):
            return 1.0
    return 0.0


@dataclass
class DiffractionMotifConfig(Config):
    min_len: int = 4
    max_len: int = 6
    min_unknown: int = 0
    max_unknown: int = 0

    def apply_difficulty(self, level):
        self.min_len = 8 + level
        self.max_len = 10 + level
        self.min_unknown = max(0, level - 1)
        self.max_unknown = level


class DiffractionMotifAbduction(Task):
    summary = ("Infer hidden cyclic signed-weight motifs from allowed/extinguished "
               "reflection masks; vary period, translated copies, signed weights, and "
               "incompletely observed positions; any reproduced motif is accepted.")
    design_choice = ("Encode motifs as cyclic sequences of phase signs; present allowed "
                     "reflections as a binary vector and extinguished ones as zeros; "
                     "require output of any motif string that reproduces the mask under "
                     "the addition rule.")
    task_version = 2
    config_cls = DiffractionMotifConfig

    def generate_entry(self):
        cfg = self.config
        for _ in range(400):
            length = random.randint(cfg.min_len, cfg.max_len)
            motif = ''.join(random.choice(_SYMBOLS) for _ in range(length))
            if all(c == '0' for c in motif):
                continue
            full = _full_mask(_weights(motif))
            if '1' not in full or '0' not in full:
                continue
            n_unknown = random.randint(cfg.min_unknown, min(cfg.max_unknown, length - 1))
            hidden = set(random.sample(range(length), n_unknown)) if n_unknown else set()
            mask = ['?' if i in hidden else full[i] for i in range(length)]
            observed = [x for x in mask if x != '?']
            if not observed or '1' not in observed or '0' not in observed:
                continue
            if not _reproduces(_weights(motif), mask):
                raise RuntimeError('source motif failed its own verifier')
            return Entry(
                metadata={'period': length, 'mask': mask, 'weights': motif},
                answer=motif,
            )
        raise RuntimeError('diffraction_motif_abduction: no admissible example')

    def render_prompt(self, metadata):
        mask = ' '.join(metadata['mask'])
        length = metadata['period']
        return (
            "A repeating motif is a cyclic sequence of P phase signs (weights), each "
            "entry one of +, - or 0. Its diffraction gives a reflection at angular "
            f"shift k of S(k) = sum_{{(i=0)}}^{{P-1}} w[i] * w[(i+k) mod P]. A "
            "reflection is ALLOWED when S(k) is nonzero and EXTINGUISHED when S(k)=0.\n\n"
            f"Observed reflection mask (length P={length}): allowed '1', extinguished "
            f"'0', unobserved '?':\n{mask}\n\n"
            "Name a motif string over {+, -, 0} of exactly this length that is "
            "compatible with every observed reflection, i.e. whose S(k) is nonzero "
            "wherever the mask reads '1' and zero wherever it reads '0'. Any translated "
            "(rotated) copy of a compatible motif is accepted. Print only the motif "
            "string."
        )

    def score_answer(self, answer, entry):
        return _score_motif(answer, entry)
