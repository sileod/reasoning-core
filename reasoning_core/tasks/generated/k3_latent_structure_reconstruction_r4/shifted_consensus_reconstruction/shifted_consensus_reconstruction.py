import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'shifted_consensus_reconstruction (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_latent_structure_reconstruction_r4/shifted_consensus_reconstruction',
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

ALPHABET = "ACGT"


def _score_alignment(copied, source):
    n = min(len(copied), len(source))
    return sum(1 for i in range(n) if copied[i] == source[i])


def _choose_offsets(copies, source):
    src_len = len(source)
    offsets = []
    for L in copies:
        best = 0
        best_score = -1
        for off in range(-(src_len + 1), src_len + 2):
            aligned = L[max(0, off): max(0, off) + src_len + 1]
            lt = max(0, -off)
            rt = max(0, off)
            sl = source[lt: src_len - rt if rt else src_len]
            score = _score_alignment(aligned, sl)
            if score > best_score:
                best_score = score
                best = off
        offsets.append(best)
    return offsets


def _reconstruct(copies, source):
    offsets = _choose_offsets(copies, source)
    cols = []
    for i in range(len(source)):
        candidates = []
        for L, off in zip(copies, offsets):
            pos = i + off
            if 0 <= pos < len(L):
                candidates.append(L[pos])
        if not candidates:
            return None, offsets
        cols.append(candidates)
    consensus = []
    for c in cols:
        consensus.append(max(set(c), key=c.count))
    return "".join(consensus), offsets


@dataclass
class ShiftedConsensusConfig(Config):
    alphabet_size: int = 4
    source_len: int = 6
    n_copies: int = 8
    shift_range: int = 2
    per_base_error: float = 0.15
    mismatch_rate: float = 0.15

    def apply_difficulty(self, level):
        self.source_len = int(stochastic_rounding(6 + level * 2))
        self.n_copies = int(stochastic_rounding(8 + level * 2))
        self.shift_range = int(2 + level)
        self.per_base_error = 0.08 + 0.02 * level
        self.mismatch_rate = 0.10 + 0.03 * level


class ShiftedConsensusReconstruction(Task):
    summary = "Recover a source string from noisy copies with unknown shifts: score each copy's displacement by agreement, align on the best offsets, then vote columnwise; answer the consensus string, each copy's shift, or its mismatch positions."
    design_choice = "Answer form: output only the consensus string, with shifts and mismatches omitted from the response."
    config_cls = ShiftedConsensusConfig
    task_version = 2

    def _generate(self):
        source = "".join(random.choice(ALPHABET[: self.config.alphabet_size]) for _ in range(self.config.source_len))
        for _attempt in range(500):
            copies = []
            for _ in range(self.config.n_copies):
                off = random.randint(-self.config.shift_range, self.config.shift_range)
                size = len(source) + random.randint(-1, 1)
                length = max(3, size)
                copy = []
                for i in range(length):
                    base = source[i - off] if 0 <= i - off < len(source) else random.choice(ALPHABET[: self.config.alphabet_size])
                    if random.random() < self.config.per_base_error:
                        base = random.choice(ALPHABET[: self.config.alphabet_size])
                    copy.append(base)
                copies.append("".join(copy))
            consensus, offsets = _reconstruct(copies, source)
            if consensus is None:
                continue
            if consensus != source:
                continue
            if consensus == source:
                mismatches = []
                for L, off in zip(copies, offsets):
                    mm = [j for j in range(len(L)) if 0 <= j - off < len(source) and L[j] != source[j - off]]
                    mismatches.append(mm)
                return source, copies, offsets, mismatches
        raise RuntimeError("failed to generate valid instance")

    def generate_entry(self):
        source, copies, offsets, mismatches = self._generate()
        return Entry(
            metadata={
                "source": source,
                "copies": copies,
                "offsets": offsets,
                "mismatch_positions": mismatches,
                "alphabet": ALPHABET[: self.config.alphabet_size],
            },
            answer=source,
        )

    def render_prompt(self, metadata):
        copies_block = "\n".join(f"{i}: {c}" for i, c in enumerate(metadata["copies"]))
        return (
            "Below are noisy copies of an unknown DNA-like source string over alphabet "
            f"{metadata['alphabet']!r}. Each copy is the source shifted by an unknown "
            "displacement and each base was corrupted with some probability. The source "
            "is a key assumption everywhere in the problem: we want the single original "
            "string that generated these copies. To recover it, score each copy's "
            "candidate displacement against the others by agreement, align all copies on "
            "their best offsets, then take a columnwise majority vote.\n\n"
            f"{copies_block}\n\n"
            "What is the reconstructed source string? Answer with only the string, "
            "no explanation, no offsets, no quotes."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        gold = entry.metadata.get("source")
        if gold is None:
            return 0.0
        return 1.0 if answer.strip() == gold else 0.0
