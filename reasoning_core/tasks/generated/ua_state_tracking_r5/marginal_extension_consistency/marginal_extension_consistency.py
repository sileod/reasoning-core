import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


def _frac(f):
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def _joint_marginals(d, wmax):
    """Build a valid joint over (A,B,C) with integer weights, return marginals (A,B) and (B,C)."""
    while True:
        t = [[[random.randint(1, wmax) for _ in range(d)] for _ in range(d)] for _ in range(d)]
        W = sum(sum(sum(row) for row in plane) for plane in t)
        ab = [[Fraction(sum(t[a][b][c] for c in range(d)), W) for b in range(d)] for a in range(d)]
        bc = [[Fraction(sum(t[a][b][c] for a in range(d)), W) for b in range(d)] for c in range(d)]
        if all(sum(ab[a][b] for a in range(d)) > 0 for b in range(d)):
            return ab, bc


def _b_marginal(ab):
    return [sum(ab[a][b] for a in range(len(ab))) for b in range(len(ab))]


def _is_compatible(ab, bc):
    return _b_marginal(ab) == _b_marginal(bc)


def _range(ab, bc, x, z):
    d = len(ab)
    mb = _b_marginal(ab)
    lo = Fraction(0)
    hi = Fraction(0)
    for b in range(d):
        pb = mb[b]
        pa_x = ab[x][b] / pb
        pc_z = bc[b][z] / pb
        lo += pb * max(Fraction(0), pa_x + pc_z - 1)
        hi += pb * min(pa_x, pc_z)
    return lo, hi


def _parse_pair(s):
    parts = str(s).strip().split()
    if len(parts) != 2:
        return None
    try:
        return Fraction(parts[0]), Fraction(parts[1])
    except (ValueError, ZeroDivisionError):
        return None


@dataclass
class MarginalExtensionCfg(Config):
    states: int = 2
    weight_max: int = 4

    def apply_difficulty(self, level):
        self.states = 2 + level
        self.weight_max = 4 + 2 * level


class MarginalExtensionConsistency(Task):
    summary = ("Combine probability tables on overlapping variable subsets into constraints on "
               "one joint distribution; determine compatibility or the attainable range of an "
               "unreported event probability.")
    config_cls = MarginalExtensionCfg
    task_version = 2

    def generate_entry(self):
        d = self.config.states
        wmax = self.config.weight_max
        if random.random() < 0.5:
            ab, bc = _joint_marginals(d, wmax)
            compatible = random.random() < 0.5
            if not compatible:
                for _ in range(50):
                    wa = [[random.randint(1, wmax) for _ in range(d)] for _ in range(d)]
                    Wa = sum(sum(r) for r in wa)
                    alt_ab = [[Fraction(wa[a][b], Wa) for b in range(d)] for a in range(d)]
                    if not _is_compatible(alt_ab, bc):
                        ab = alt_ab
                        break
                else:
                    compatible = True
            answer = "yes" if compatible else "no"
            return Entry(metadata={
                "mode": "compat", "states": d,
                "ab": [[_frac(v) for v in row] for row in ab],
                "bc": [[_frac(v) for v in row] for row in bc],
                "gold": answer,
            }, answer=answer)
        else:
            ab, bc = _joint_marginals(d, wmax)
            x = random.randrange(d)
            z = random.randrange(d)
            lo, hi = _range(ab, bc, x, z)
            assert 0 <= lo <= hi <= 1
            answer = f"{_frac(lo)} {_frac(hi)}"
            return Entry(metadata={
                "mode": "range", "states": d, "x": x, "z": z,
                "ab": [[_frac(v) for v in row] for row in ab],
                "bc": [[_frac(v) for v in row] for row in bc],
                "lo": _frac(lo), "hi": _frac(hi), "gold": answer,
            }, answer=answer)

    def render_prompt(self, m):
        d = m.states
        val = " ".join(map(str, range(d)))

        def grid(tag, rows, row_name, col_name):
            hdr = f"{tag}: rows are {row_name} values, columns are {col_name} values."
            body = "\n".join(f"{i}: {' '.join(row)}" for i, row in enumerate(rows))
            return hdr + "\n" + body

        tables = (
            f"Three variables A, B and C each take one value from {{{', '.join(map(str, range(d)))}}}.\n\n"
            f"{grid('P(A,B)', m.ab, 'A', 'B')}\n\n"
            f"{grid('P(B,C)', m.bc, 'B', 'C')}\n\n"
        )
        if m.mode == "compat":
            return (
                tables +
                "A pair of tables is compatible when a single joint distribution over (A,B,C) "
                "consistent with both of them exists. Are these two tables compatible? "
                "Answer yes or no. Give your answer."
            )
        return (
            tables +
            f"A joint distribution over (A,B,C) consistent with both tables above is known to exist "
            f"(the tables are compatible). Across every such joint distribution, what range of values "
            f"can the probability P(A={m.x}, C={m.z}) take? State the minimum and the maximum as two "
            f"reduced fractions separated by a space, e.g. '1/4 3/8'. Give your answer."
        )

    def score_answer(self, answer, entry):
        if entry.metadata.get("mode") == "compat":
            a = str(answer).strip().lower()
            if a in ("yes", "no"):
                return 1.0 if a == entry.answer else 0.0
            return 0.0
        pair = _parse_pair(answer)
        if pair is None:
            return 0.0
        lo, hi = pair
        gold_lo = Fraction(entry.metadata["lo"])
        gold_hi = Fraction(entry.metadata["hi"])
        return 1.0 if (lo == gold_lo and hi == gold_hi) else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'marginal_extension_consistency (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_state_tracking_r5/marginal_extension_consistency',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1618848011,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
