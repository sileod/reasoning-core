"""Verify polynomial sumcheck transcripts across variable orders, field sizes and degree bounds."""

import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'sumcheck_transcript_audit (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_verification_repair_r4/sumcheck_transcript_audit',
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

design_choice = "Hide a missing coefficient in the final round's consistency equation, requiring solvers to derive its unique value from the transcript and field arithmetic constraints."


def _is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def _next_prime(n):
    n = max(n, 3)
    while not _is_prime(n):
        n += 1
    return n


def _eval_poly(coeffs, x, p):
    v = 0
    for c in reversed(coeffs):
        v = (v * x + c) % p
    return v


def _sum_01_deg1_check(rounds, sumval, p):
    """Walk the transcript from sumval and return (consistent_bool, first_bad_round)."""
    cur = sumval
    for rd in rounds:
        fsum = (_eval_poly(rd["coeffs"], 0, p) + _eval_poly(rd["coeffs"], 1, p)) % p
        if fsum != cur:
            return False, rd["round"]
        cur = _eval_poly(rd["coeffs"], rd["challenge"], p) % p
    return True, None


@dataclass
class SumcheckConfig(Config):
    nvars: int = 2
    deg: int = 1
    pbits: int = 5

    def apply_difficulty(self, level):
        self.nvars = 2 + level if level <= 4 else 2 + 4
        self.deg = 1 + min(level, 4)
        self.pbits = 5 + stochastic_rounding(level)

    @property
    def prime(self):
        return _next_prime(2 ** max(3, self.pbits))


class SumcheckTranscriptAudit(Task):
    summary = "Verify polynomial sumcheck transcripts across variable orders, field sizes and degree bounds; locate the first inconsistent round or recover a missing coefficient from its consistency equation."
    config_cls = SumcheckConfig

    def generate_entry(self):
        config = self.config
        p = config.prime
        num_vars = config.nvars
        deg = config.deg

        # Build an honest multivariate polynomial g of total degree <= deg and run an
        # honest sumcheck: S = sum over {0,1}^n g, and each round polynomial f_i equals
        # the value summed over remaining coordinates (so the sumcheck is consistent).
        monomials = []
        for exps in itertools.product(range(deg + 1), repeat=num_vars):
            if sum(exps) <= deg and sum(exps) > 0:
                monomials.append(exps)
        if not monomials:
            monomials = [(1,) + (0,) * (num_vars - 1)] if num_vars >= 1 else []
        coeffs_g = {}
        for m in monomials:
            coeffs_g[m] = random.randrange(1, p)

        def g_eval(assign):
            v = 0
            for m, c in coeffs_g.items():
                prod = 1
                for i in range(num_vars):
                    prod = prod * (assign[i] ** m[i]) % p
                v = (v + c * prod) % p
            return v

        def g_partial(prefix, t, i):
            total = 0
            for rest in itertools.product([0, 1], repeat=num_vars - i - 1):
                assign = list(prefix) + [t] + list(rest)
                total = (total + g_eval(assign)) % p
            return total

        S = sum(g_eval(list(a)) for a in itertools.product([0, 1], repeat=num_vars)) % p

        # Honest rounds.
        rounds = []
        claim = S
        prefix = []
        for i in range(num_vars):
            xs = random.sample(range(p), deg + 1)
            ys = [g_partial(prefix, x, i) % p for x in xs]
            poly = _interp(list(zip(xs, ys)), p)
            r_i = random.randrange(p)
            claim = _eval_poly(poly, r_i, p) % p
            rounds.append({"round": i + 1, "coeffs": list(poly), "challenge": r_i})
            prefix.append(r_i)

        # Decide scenario (mode): 0 consistent, 1 first-inconsistent round, 2 missing coeff.
        # Weight consistent rarer so the constant-guess audit stays far below its ceiling.
        mode = random.choice([0, 1, 1, 2, 2, 2])
        num_rounds = len(rounds)

        if mode == 2:
            # Redact one coefficient of the final round; solver recovers it.
            err_i = num_rounds - 1
            poly = list(rounds[err_i]["coeffs"])
            pos = random.randrange(len(poly))
            hidden_val = poly[pos] % p
            rounds[err_i]["missing_idx"] = pos
            rounds[err_i]["hidden_val"] = hidden_val
            ans = str(hidden_val)
        elif mode == 1:
            # Always corrupt exactly one round to create a unique first-inconsistent round.
            err_i = random.randrange(num_rounds)
            poly = list(rounds[err_i]["coeffs"])
            pos = random.randrange(len(poly))
            poly[pos] = (poly[pos] + random.randrange(1, p)) % p
            rounds[err_i]["coeffs"] = poly
            ans = str(err_i + 1)
        else:
            # consistent transcript
            ans = "consistent"

        # Recompute claims forward from S using the (possibly corrupted) coeffs so the
        # printed claim chain is exactly what the auditor derives.
        claim = S
        for rd in rounds:
            rd["claim"] = claim
            claim = _eval_poly(rd["coeffs"], rd["challenge"], p) % p
        final_value = claim

        # Sanity: mode 1 must actually be inconsistent at ans.
        consistent, first_bad = _sum_01_deg1_check(rounds, S, p)
        if mode == 1 and consistent:
            raise RuntimeError("expected inconsistent transcript but it is consistent")
        if mode == 1 and first_bad != err_i + 1:
            raise RuntimeError("first-bad mismatch")
        if mode == 0 and not consistent:
            raise RuntimeError("expected consistent transcript but it is not")

        metadata = {
            "p": p,
            "nvars": num_vars,
            "deg": deg,
            "sum": S,
            "rounds": rounds,
            "final_value": final_value,
            "mode": mode,
        }
        return Entry(metadata=metadata, answer=ans)

    def render_prompt(self, metadata):
        p = metadata["p"]
        rounds = metadata["rounds"]
        lines = [
            f"A verifier checks a polynomial sumcheck transcript over the boolean "
            f"hypercube in the prime field F_{p}. There are {metadata['nvars']} variables "
            f"and {len(rounds)} rounds. The claimed "
            f"total is {metadata['sum']}. For each round, the polynomial f(t) must satisfy "
            f"f(0)+f(1) == the claim entering that round, reduced mod {p}; the next claim "
            f"is f(r), also mod {p}, where r is that round's challenge. Round 1 enters "
            f"with claim = {metadata['sum']}."
        ]
        for rd in rounds:
            poly_str = _poly_str(rd["coeffs"], rd.get("missing_idx"))
            lines.append(
                f"Round {rd['round']}: claim entering = {rd['claim'] % p}, "
                f"f(t) = {poly_str}, challenge r = {rd['challenge']}."
            )
        lines.append("State the audit result exactly:")
        lines.append('- "consistent" if every round satisfies f(0)+f(1) == claim (mod p);')
        lines.append("- the 1-based round number of the first round that violates "
                     "f(0)+f(1) == claim (mod p), if the transcription hides no '?'; or")
        lines.append("- the single integer value of the hidden coefficient '?' that makes "
                     "that round's consistency equation hold, if a '?' appears.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        meta = entry.metadata
        p = meta["p"]
        rounds = meta["rounds"]
        mode = meta["mode"]
        s = str(answer).strip()

        if mode == 2:
            last = rounds[-1]
            target = last.get("hidden_val")
            if target is None:
                return 0.0
            try:
                return 1.0 if int(s) % p == target % p else 0.0
            except ValueError:
                return 0.0

        consistent, first_bad = _sum_01_deg1_check(rounds, meta["sum"], p)
        if mode == 0:
            return 1.0 if s.lower() == "consistent" else 0.0
        # mode 1
        try:
            val = int(s)
        except ValueError:
            # accepting either "consistent" (wrong) or index
            return 0.0
        return 1.0 if val == first_bad else 0.0


def _poly_str(coeffs, missing_idx=None):
    parts = []
    for i, c in enumerate(coeffs):
        if missing_idx == i:
            if i == 0:
                parts.append("?")
            elif i == 1:
                parts.append("?*t")
            else:
                parts.append(f"?*t^{i}")
        elif i == 0:
            parts.append(str(c))
        elif i == 1:
            parts.append(f"{c}*t")
        else:
            parts.append(f"{c}*t^{i}")
    return " + ".join(parts) if parts else "0"


def _interp(points, p):
    """Interpolate univariate polynomial (deg < len(points)) over F_p."""
    coeffs = [0]
    for (xj, yj) in points:
        poly = [1]
        denom = 1
        for (xk, _yk) in points:
            if xk == xj:
                continue
            denom = denom * (xj - xk) % p
            newc = [0] * (len(poly) + 1)
            for i, c in enumerate(poly):
                newc[i] = (newc[i] - c * xk) % p
                newc[i + 1] = (newc[i + 1] + c) % p
            poly = newc
        factor = yj * pow(denom, p - 2, p) % p
        for i, c in enumerate(poly):
            if i >= len(coeffs):
                coeffs.append(0)
            coeffs[i] = (coeffs[i] + c * factor) % p
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs.pop()
    return coeffs
