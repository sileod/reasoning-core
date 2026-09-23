import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, edict

TASK_META = {'parent_source_id': None,
 'idea': 'finite_difference_extension (variant 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_state_tracking_r4/finite_difference_extension',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = ("Answer as a single integer for each queried index, with queries listed in a "
                 "fixed increasing order and values separated by spaces.")


def polyval_int(coeffs, x):
    """Horner evaluation of the integer polynomial with the given coefficients.

    coeffs[j] is the coefficient of x**j.
    """
    result = 0
    for c in reversed(coeffs):
        result = result * x + c
    return result


def finite_diff_extend(values, d, target):
    """Extrapolate a degree-d integer sequence with Newton forward differences.

    values[k] is the value at index k (k = 0..len(values)-1). For a polynomial
    of degree d, given at least d+1 consecutive entries the entry at index
    `target` equals sum_{j=0}^{d} binomial(target, j) * Delta^j values[0],
    where Delta^j values[0] is the j-th forward difference at index 0.
    """
    diff = list(values)
    total = diff[0]
    powers = diff[0]
    for j in range(1, d + 1):
        diff = [diff[i + 1] - diff[i] for i in range(len(diff) - 1)]
        total += math.comb(target, j) * diff[0]
    return total


def nth_diff(values, order):
    """Return the forward difference of the given order over consecutive values."""
    diff = list(values)
    for _ in range(order):
        diff = [diff[i + 1] - diff[i] for i in range(len(diff) - 1)]
    return diff


@dataclass
class FiniteDifferenceExtensionConfig(Config):
    degree: int = 3
    given_extra: int = 2
    query_count: int = 2
    query_gap: int = 2
    coeff_magnitude: int = 3

    def apply_difficulty(self, level):
        self.degree = 2 + level
        self.given_extra = 1 + int(level * 0.6)
        self.query_count = 2 + int(level * 0.8)
        self.query_gap = 2 + level
        self.coeff_magnitude = 3 + int(level * 0.6)


class FiniteDifferenceExtension(Task):
    summary = ("Given consecutive integer evaluations of an unknown polynomial of stated "
               "degree, extend its forward-difference table via the vanishing (d+1)-th "
               "difference and report the values at several later queried indices.")
    config_cls = FiniteDifferenceExtensionConfig
    design_choice = design_choice

    def generate_entry(self):
        cfg = self.config
        rng = random
        d = cfg.degree
        given_count = d + 1 + cfg.given_extra
        mag = cfg.coeff_magnitude

        for _ in range(400):
            coeffs = [rng.randint(-mag, mag) for _ in range(d + 1)]
            while coeffs[-1] == 0:
                coeffs[-1] = rng.randint(-mag, mag)

            values = [polyval_int(coeffs, k) for k in range(given_count)]

            dplus = nth_diff(values, d + 1)
            if any(v != 0 for v in dplus):
                continue
            if len(set(values)) < 2:
                continue

            queries = []
            idx = given_count
            for _ in range(cfg.query_count):
                idx += rng.randint(1, cfg.query_gap)
                queries.append(idx)
            queries = sorted(queries)

            answer_ints = [polyval_int(coeffs, n) for n in queries]
            all_ok = True
            extended = values
            for n, av in zip(queries, answer_ints):
                if finite_diff_extend(values, d, n) != av:
                    all_ok = False
                    break
                extended = extended + [av]
                if nth_diff(extended[: d + 2], d + 1)[-1] != 0:
                    all_ok = False
                    break
            if not all_ok:
                continue

            answer = ' '.join(str(x) for x in answer_ints)
            metadata = edict({
                'degree': d,
                'given_indices': list(range(given_count)),
                'given_values': values,
                'query_indices': queries,
                'answer_values': answer_ints,
            })
            metadata.payload = {
                'degree': d,
                'given_indices': list(range(given_count)),
                'given_values': values,
                'query_indices': queries,
            }
            return Entry(metadata=metadata, answer=answer)

        raise RuntimeError('could not produce a valid non-degenerate instance')

    def render_prompt(self, metadata):
        payload = metadata.payload
        given = payload['given_indices']
        vals = payload['given_values']
        queries = payload['query_indices']
        lines = [
            'A polynomial of unknown form is known to have degree exactly '
            '%d.' % payload['degree'],
            'It takes the following integer values at consecutive indices '
            '0 through %d:' % given[-1],
            '',
            'Index : %s' % '  '.join(str(i) for i in given),
            'Value : %s' % '  '.join(str(v) for v in vals),
            '',
            'Because the polynomial has degree %d, its (%d)-th forward '
            'difference is identically zero.' % (payload['degree'], payload['degree'] + 1),
            'Use the forward-difference table to extend the sequence past '
            'index %d and find the value of the polynomial at each queried '
            'index below.' % given[-1],
            'Queried indices, already in increasing order: %s'
            % ', '.join(str(q) for q in queries),
            '',
            'The answer is the polynomial value at each queried index, in the '
            'same increasing order, written as space-separated integers (for '
            'example "7 12" for two queried indices).',
        ]
        return '\n'.join(lines)

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        text = str(answer).strip()
        parts = text.replace(',', ' ').split()
        if not parts or len(parts) != len(entry.metadata.query_indices):
            return 0.0
        try:
            got = [int(p) for p in parts]
        except ValueError:
            return 0.0
        return 1.0 if got == entry.metadata.answer_values else 0.0
