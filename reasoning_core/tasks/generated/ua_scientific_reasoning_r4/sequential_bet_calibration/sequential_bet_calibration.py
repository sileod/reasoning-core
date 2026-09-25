import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Task, Entry, Config, edict
from reasoning_core.template import stochastic_rounding as sround


def _parse_answer(text):
    if isinstance(text, (int,)):
        return Fraction(int(text), 1)
    if isinstance(text, float):
        return None
    s = text.strip()
    if not s:
        return None
    if s.startswith('(') and s.endswith(')'):
        s = s[1:-1]
    if '/' in s:
        num, _, den = s.partition('/')
        try:
            return Fraction(int(num), int(den))
        except Exception:
            return None
    try:
        return Fraction(int(s), 1)
    except Exception:
        return None


def _max_safe_stake(horizon, grid, mult, rebate, init):
    """Return the maximal initial stake S such that the expected wealth
    process is non-increasing at every round (a supermartingale under the
    composite null grid), as a positive Fraction, or None if no such positive
    finite stake exists."""
    n = len(grid)  # number of regimes
    init_sum = sum(init)
    pi = [Fraction(c, init_sum) for c in init]  # regime marginal at t=0
    # E_t[i] = s*es[i] + ec[i]
    es = [pi[i] for i in range(n)]
    ec = [Fraction(0) for _ in range(n)]
    S_prev = (Fraction(1), Fraction(0))  # affine (slope, const) sum at t=0: == s

    ubs = []  # positive-slope upper bounds on s
    lbs = []  # negative-slope lower bounds on s

    for _ in range(horizon):
        new_pi = [Fraction(0) for _ in range(n)]
        for j in range(n):
            for i in range(n):
                new_pi[j] += pi[i] * Fraction(grid[i][j], sum(grid[i]))
        nes = [Fraction(0) for _ in range(n)]
        nec = [Fraction(0) for _ in range(n)]
        for j in range(n):
            for i in range(n):
                p = Fraction(grid[i][j], sum(grid[i]))
                nes[j] += es[i] * p * mult[j]
                nec[j] += ec[i] * p * mult[j]
            nec[j] += new_pi[j] * rebate[j]
        S_cur = (sum(nes), sum(nec))
        slope = S_cur[0] - S_prev[0]
        const = S_cur[1] - S_prev[1]
        if slope > 0:
            ubs.append(-const / slope)
        elif slope < 0:
            lbs.append(-const / slope)
        else:
            if const > 0:
                return None  # infeasible regardless of S
        pi, es, ec, S_prev = new_pi, nes, nec, S_cur

    if not ubs:
        return None  # no upper bound -> unbounded stake
    candidate = min(ubs)
    for lb in lbs:
        if candidate < lb:
            return None
    if candidate <= 0:
        return None
    # verify by re-running the recursion at the candidate stake exactly
    _verify(horizon, grid, mult, rebate, init, candidate)
    return candidate


def _verify(horizon, grid, mult, rebate, init, stake):
    n = len(grid)
    init_sum = sum(init)
    pi = [Fraction(c, init_sum) for c in init]  # regime marginal at t=0
    es = [Fraction(c, init_sum) for c in init]  # E_0[i] coefficient of s
    ec = [Fraction(0) for _ in range(n)]
    S_prev = stake
    for _ in range(horizon):
        new_pi = [Fraction(0) for _ in range(n)]
        for j in range(n):
            for i in range(n):
                new_pi[j] += pi[i] * Fraction(grid[i][j], sum(grid[i]))
        nes = [Fraction(0) for _ in range(n)]
        nec = [Fraction(0) for _ in range(n)]
        for j in range(n):
            for i in range(n):
                p = Fraction(grid[i][j], sum(grid[i]))
                nes[j] += es[i] * p * mult[j]
                nec[j] += ec[i] * p * mult[j]
            nec[j] += new_pi[j] * rebate[j]
        S_cur = sum(nes) * stake + sum(nec)
        assert S_cur <= S_prev, (S_cur, S_prev)
        S_prev = S_cur
        es, ec, pi = nes, nec, new_pi
    return True


@dataclass
class SequentialBetCalibrationConfig(Config):
    horizon: int = 2
    mult_hi: int = 3
    reb_hi: int = 4
    count_hi: int = 4

    def apply_difficulty(self, level):
        self.horizon = sround(2 + 2 * level)
        self.mult_hi = 2 + level
        self.reb_hi = 2 + level
        self.count_hi = 3 + level


class SequentialBetCalibration(Task):
    summary = (
        "Given a composite null transition grid over regimes and history-dependent "
        "betting payoffs (per-regime multipliers and fixed rebates), find the maximal "
        "rational initial stake under which the expected accumulated-wealth process "
        "is a supermartingale (non-increasing at every round)."
    )
    design_choice = (
        "Encode the problem as a grid of transition probabilities and payoff "
        "multipliers, and ask for the maximal initial stake that keeps the expected "
        "wealth process non-increasing at every step; the answer is a rational number."
    )
    config_cls = SequentialBetCalibrationConfig

    def generate_entry(self):
        horizon = self.config.horizon
        for _ in range(400):
            grid = [
                [random.randint(1, self.config.count_hi),
                 random.randint(1, self.config.count_hi)],
                [random.randint(1, self.config.count_hi),
                 random.randint(1, self.config.count_hi)],
            ]
            m0 = random.randint(1, self.config.mult_hi)
            m1 = random.randint(2, self.config.mult_hi + 1)
            r0 = random.randint(-self.config.reb_hi, -1)
            r1 = random.randint(-self.config.reb_hi, -1)
            c0 = random.randint(1, self.config.count_hi)
            c1 = random.randint(1, self.config.count_hi)
            stake = _max_safe_stake(horizon, grid, [m0, m1], [r0, r1], [c0, c1])
            if stake is not None:
                num, den = stake.numerator, stake.denominator
                answer = str(num) if den == 1 else f"{num}/{den}"
                metadata = edict({
                    "horizon": int(horizon),
                    "grid": [[int(v) for v in row] for row in grid],
                    "mult": [int(m0), int(m1)],
                    "rebate": [int(r0), int(r1)],
                    "init": [int(c0), int(c1)],
                    "stake_num": int(num),
                    "stake_den": int(den),
                    "stake": [int(num), int(den)],
                })
                metadata.payload = {
                    "horizon": metadata.horizon,
                    "grid": metadata.grid,
                    "mult": metadata.mult,
                    "rebate": metadata.rebate,
                    "init": metadata.init,
                }
                return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("sequential_bet_calibration: no valid instance after bounded attempts")

    def render_prompt(self, metadata):
        g = metadata.grid
        p00 = _fmt(g[0][0], sum(g[0]))
        p01 = _fmt(g[0][1], sum(g[0]))
        p10 = _fmt(g[1][0], sum(g[1]))
        p11 = _fmt(g[1][1], sum(g[1]))
        m0, m1 = metadata.mult
        r0, r1 = metadata.rebate
        i0, i1 = metadata.init
        return (
            f"A gambler runs a sequential hypothesis test over {metadata.horizon} days. "
            f"Each day the world sits in one of two regimes, A or B, following a null "
            f"transition grid (from the day's regime to the next): A->A = {p00}, A->B = {p01}, "
            f"B->A = {p10}, B->B = {p11}. The bettor's wealth is updated at the end of each day "
            f"depending on that day's ending regime: in regime A wealth is multiplied by {m0} then "
            f"a fixed rebate of {r0} is added; in regime B wealth is multiplied by {m1} then a fixed "
            f"rebate of {r1} is added. The starting regime is A with probability {i0}/{i0 + i1} and "
            f"B with probability {i1}/{i0 + i1}. The bettor stakes an amount S up front, so wealth "
            f"starts at S. The strategy is a valid test only if, under the null law, expected wealth "
            f"never increases from one day to the next (the wealth process is a supermartingale): "
            f"E[W_t] <= E[W_{{t-1}}] at every day t = 1..{metadata.horizon}, where the expectation "
            f"marginalizes over all regime paths. Find the maximal initial stake S for which the "
            f"strategy is valid. Give S as a reduced fraction a/b, or as a whole integer if the "
            f"denominator is 1 (for example, an answer could look like 7/4 or 3)."
        )

    def score_answer(self, answer, entry):
        gold = Fraction(entry.metadata.stake_num, entry.metadata.stake_den)
        got = _parse_answer(answer)
        if got is None:
            return 0.0
        return 1.0 if got == gold else 0.0


def _fmt(num, den):
    f = Fraction(num, den)
    return str(f) if f.denominator != 1 else f"{f.numerator}/1"


TASK_META = {'parent_source_id': None,
 'idea': 'sequential_bet_calibration (variant 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scientific_reasoning_r4/sequential_bet_calibration',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2302342651,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
