import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'multiplicative_interaction_contrast (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_state_tracking_r4/multiplicative_interaction_contrast',
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


_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
           59, 61, 67, 71, 73, 79, 83, 89, 97]


def _primes_up_to(limit):
    return [p for p in _PRIMES if p <= limit]


def _parse_int(answer):
    if answer is None:
        return None
    try:
        s = str(answer).strip()
        iv = int(s)
    except Exception:
        return None
    if iv <= 0:
        return None
    return iv


@dataclass
class MultiplicativeContrastConfig(Config):
    nrows: int = 3
    ncols: int = 3
    max_prime: int = 11
    max_rowval: int = 9
    max_colval: int = 9

    def apply_difficulty(self, level):
        self.nrows = 3 + level
        self.ncols = 3 + level
        self.max_prime = 11 + 5 * level
        self.max_rowval = 5 + 3 * level
        self.max_colval = 5 + 3 * level


def _make_table(nrows, ncols, max_rowval, max_colval):
    rowval = [random.randint(2, max_rowval) for _ in range(nrows)]
    colval = [random.randint(2, max_colval) for _ in range(ncols)]
    table = [[rowval[i] * colval[j] for j in range(ncols)] for i in range(nrows)]
    return rowval, colval, table


class MultiplicativeInteractionContrast(Task):
    summary = ("Positive integer rank-one row by column tables where one entry is multiplied by a "
               "prime; isolate the irreducible 2x2 interaction contrast (cross-ratio), confirm the "
               "multiplied entry breaks it, and recover the restoring prime scalar from the contrast.")
    config_cls = MultiplicativeContrastConfig
    design_choice = ("Answer format: output the minimal positive integer scalar that restores "
                     "invariance, with instances generated so the true scalar is always a prime "
                     "between 2 and 97.")

    def generate_entry(self):
        cfg = self.config
        while True:
            nrows = cfg.nrows
            ncols = cfg.ncols
            prime_pool = _primes_up_to(cfg.max_prime)
            if len(prime_pool) < 2:
                prime_pool = [2, 3]
            r_true = random.choice(prime_pool)
            rowval, colval, base = _make_table(nrows, ncols, cfg.max_rowval, cfg.max_colval)
            ai = random.randrange(nrows)
            aj = random.randrange(ncols)
            ti = random.randrange(nrows)
            tj = random.randrange(ncols)
            if ti == ai and tj == aj:
                continue
            if ti == ai or tj == aj:
                continue
            scaled = [[base[i][j] for j in range(ncols)] for i in range(nrows)]
            scaled[ti][tj] = base[ti][tj] * r_true
            num = scaled[ti][tj] * scaled[ai][aj]
            den = scaled[ti][aj] * scaled[ai][tj]
            if den <= 0 or num % den != 0:
                continue
            contrast = num // den
            if contrast != r_true:
                continue
            ref = scaled[ai][aj]
            break
        return Entry(metadata={
            "shape": [nrows, ncols],
            "table": scaled,
            "anchor": [ai, aj],
            "target": [ti, tj],
            "rescaled_target": int(scaled[ti][tj]),
            "reference": int(ref),
            "true_scalar": int(r_true),
            "contrast": int(contrast),
        }, answer=str(r_true))

    def render_prompt(self, metadata):
        nrows, ncols = metadata["shape"]
        body = "\n".join(" ".join(str(v) for v in row) for row in metadata["table"])
        ai, aj = metadata["anchor"]
        ti, tj = metadata["target"]
        return (
            f"The table below is a multiplicative row-by-column weight table: every entry equals a "
            f"row value times a column value, so the interaction contrast across any 2 rows and 2 "
            f"columns is invariant (equal to 1). One single entry was corrupted: it alone was "
            f"multiplied by an unknown positive integer factor, breaking that invariance, while "
            f"every other entry kept its row-value-times-column-value form. The uncorrupted entry "
            f"at row {ai}, column {aj} still holds its true multiplicative value, and the corrupted "
            f"entry is at row {ti}, column {tj}.\n"
            f"\n"
            f"The interaction contrast of the 2x2 block spanned by the two rows {ai} and {ti} and "
            f"the two columns {aj} and {tj} equals the corrupted entry's multiplier: this is the "
            f"positive integer you are looking for.\n"
            f"\n"
            f"Table (entry value = row value * column value):\n"
            f"{body}\n"
            f"\n"
            f"Compute the 2x2 interaction contrast (the cross-ratio "
            f"({metadata['rescaled_target']} * {metadata['reference']}) / "
            f"({metadata['table'][ti][aj]} * {metadata['table'][ai][tj]})), its value is the "
            f"smallest positive integer (a prime between 2 and 97) that restores the table's "
            f"multiplicative structure. Answer with that prime integer alone."
        )

    def score_answer(self, answer, entry):
        got = _parse_int(answer)
        if got is None:
            return 0.0
        return 1.0 if got == entry.metadata["true_scalar"] else 0.0
