"""Concentrated-liquidity (Uniswap v3 style) swaps with range activations."""

import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


def _round_half_up(fr):
    return (2 * fr.numerator + fr.denominator) // (2 * fr.denominator)


def _active_liquidity(s, positions):
    total = 0
    for p in positions:
        if p["lo"] <= s <= p["hi"]:
            total += p["L"]
    return total


def _swap0(s, a, positions, max_price):
    rem = Fraction(a)
    while rem > 0:
        bps = sorted({p["lo"] for p in positions} | {p["hi"] for p in positions})
        below = [b for b in bps if b < s]
        b_lo = max(below) if below else 1
        if b_lo < 1:
            b_lo = 1
        L = _active_liquidity(s, positions)
        if L <= 0 or b_lo >= s:
            break
        dx = L * (Fraction(1, b_lo) - Fraction(1, s))
        if rem <= dx:
            denom = Fraction(1, s) - rem / L
            if denom <= 0:
                break
            s = 1 / denom
            rem = 0
        else:
            rem -= dx
            s = Fraction(b_lo)
    return s


def _swap1(s, a, positions, max_price):
    rem = Fraction(a)
    while rem > 0:
        bps = sorted({p["lo"] for p in positions} | {p["hi"] for p in positions})
        above = [b for b in bps if b > s]
        b_hi = min(above) if above else max_price
        L = _active_liquidity(s, positions)
        if L <= 0 or b_hi <= s:
            break
        dy = L * (b_hi - s)
        if rem <= dy:
            s = s + rem / L
            rem = 0
        else:
            rem -= dy
            s = Fraction(b_hi)
    return s


def _simulate(positions, ops, s0, max_price):
    s = Fraction(s0)
    for op in ops:
        kind = op["type"]
        if kind == "swap0":
            s = _swap0(s, op["amount"], positions, max_price)
        elif kind == "swap1":
            s = _swap1(s, op["amount"], positions, max_price)
        elif kind == "add":
            positions.append({"L": op["L"], "lo": op["lo"], "hi": op["hi"],
                              "id": op["id"]})
        elif kind == "remove":
            pid = op["pid"]
            for i, p in enumerate(positions):
                if p["id"] == pid:
                    del positions[i]
                    break
    return s


@dataclass
class LiquidityRangeUpdatesConfig(Config):
    min_narrow: int = 1
    max_narrow: int = 2
    min_ops: int = 2
    max_ops: int = 3
    max_price: int = 40
    max_liq: int = 8
    max_amount: int = 12

    def apply_difficulty(self, level):
        self.max_narrow = min(8, 2 + level)
        self.max_ops = min(12, 2 + level)
        self.max_price = 20 * (level + 2)
        self.max_liq = 4 + level
        self.max_amount = 8 + 4 * level


class LiquidityRangeUpdates(Task):
    summary = ("Concentrated-liquidity AMM swaps (token0/token1) crossing range "
               "boundaries that activate or deactivate positions, with liquidity "
               "additions and removals, returning the final rounded sqrt price.")
    config_cls = LiquidityRangeUpdatesConfig

    def _make_ops(self, positions, s, s0):
        cfg = self.config
        positions = [dict(p) for p in positions]
        n_ops = random.randint(cfg.min_ops, cfg.max_ops)
        n_struct = random.randint(0, max(0, n_ops - 1))
        n_swap = n_ops - n_struct
        swap_dir = [random.choice(("swap0", "swap1")) for _ in range(n_swap)]
        struct_dir = random.sample(["add", "remove"], k=min(2, n_struct))
        struct_tail = [random.choice(["add", "remove"])
                       for _ in range(n_struct - len(struct_dir))]
        types = swap_dir + struct_dir[: n_struct] + struct_tail
        random.shuffle(types)

        ids = {p["id"] for p in positions}
        next_id = max(ids) + 1 if ids else 0
        cur = s
        lo_floor = max(2, int(cfg.max_price * 0.15))
        hi_ceil = max(lo_floor + 2, int(cfg.max_price * 0.85))
        ops = []
        for t in types:
            if t in ("swap0", "swap1"):
                L = _active_liquidity(cur, positions)
                if L <= 0:
                    L = 1
                if t == "swap0" and cur > lo_floor:
                    cap = int(L * (Fraction(1, lo_floor) - Fraction(1, cur)))
                    cap = max(1, int(cap * 0.8))
                    hi = min(cfg.max_amount, cap)
                elif t == "swap1" and cur < hi_ceil:
                    cap = int(L * (hi_ceil - cur))
                    cap = max(1, int(cap * 0.8))
                    hi = min(cfg.max_amount, cap)
                else:
                    hi = 1
                amount = random.randint(1, max(1, hi))
                ops.append({"type": t, "amount": amount})
                cur = _swap0(cur, amount, positions, cfg.max_price) if t == "swap0" \
                    else _swap1(cur, amount, positions, cfg.max_price)
            elif t == "add":
                lo = random.randint(lo_floor, max(lo_floor, hi_ceil - 4))
                hi = random.randint(lo + 2, cfg.max_price - 1)
                L = random.randint(1, cfg.max_liq)
                positions.append({"id": next_id, "lo": lo, "hi": hi, "L": L})
                ops.append({"type": "add", "lo": lo, "hi": hi, "L": L,
                            "id": next_id})
                next_id += 1
            else:
                removable = [p["id"] for p in positions if p["id"] != 0]
                if removable:
                    pid = random.choice(removable)
                    positions = [p for p in positions if p["id"] != pid]
                    ops.append({"type": "remove", "pid": pid})
                else:
                    lo = random.randint(lo_floor, max(lo_floor, hi_ceil - 4))
                    hi = random.randint(lo + 2, cfg.max_price - 1)
                    L = random.randint(1, cfg.max_liq)
                    positions.append({"id": next_id, "lo": lo, "hi": hi, "L": L})
                    ops.append({"type": "add", "lo": lo, "hi": hi, "L": L,
                                "id": next_id})
                    next_id += 1
        return ops, positions

    def generate_entry(self):
        for _ in range(200):
            cfg = self.config
            s0 = random.randint(int(cfg.max_price * 0.25) + 2,
                                int(cfg.max_price * 0.75) - 2)
            backbone = {"id": 0, "lo": 1, "hi": cfg.max_price,
                        "L": random.randint(1, max(2, cfg.max_liq))}
            n_narrow = random.randint(cfg.min_narrow, cfg.max_narrow)
            next_id = 1
            positions = [backbone]
            for _ in range(n_narrow):
                lo = random.randint(2, max(2, cfg.max_price - 3))
                hi = random.randint(lo + 2, cfg.max_price - 1)
                positions.append({"id": next_id, "lo": lo, "hi": hi,
                                  "L": random.randint(1, cfg.max_liq)})
                next_id += 1
            init = [dict(p) for p in positions]
            ops, positions = self._make_ops(init, s0, s0)
            final = _simulate([dict(p) for p in init], ops, s0, cfg.max_price)
            if not (final > 0):
                continue
            if final < 1 or final > cfg.max_price:
                continue
            ans = _round_half_up(final)
            if ans < 1 or ans > cfg.max_price:
                continue
            clean_ops = []
            for op in ops:
                if op["type"] in ("swap0", "swap1"):
                    clean_ops.append({"type": op["type"], "amount": op["amount"]})
                elif op["type"] == "add":
                    clean_ops.append({"type": "add", "lo": op["lo"],
                                      "hi": op["hi"], "L": op["L"],
                                      "id": op["id"]})
                else:
                    clean_ops.append({"type": "remove", "pid": op["pid"]})
            init_positions = [{"id": p["id"], "lo": p["lo"], "hi": p["hi"],
                               "L": p["L"]} for p in init]
            rem_count = sum(1 for o in ops if o["type"] == "remove")
            metadata = {
                "initial_sqrt": int(s0),
                "max_price": cfg.max_price,
                "positions": init_positions,
                "ops": clean_ops,
                "removed_count": rem_count,
            }
            return Entry(metadata=metadata, answer=str(ans))
        raise RuntimeError("failed to generate an admissible instance")

    def render_prompt(self, metadata):
        lines = [
            "A concentrated-liquidity (Uniswap v3 style) pool holds several positions, "
            "each with a liquidity L active only while the current sqrt price s lies in "
            "its range [lo, hi]. Within each interval between range boundaries the pool "
            "behaves as one constant-product AMM with total liquidity equal to the sum of "
            "the in-range positions. The price only changes through swaps.",
            "",
            "Swap law: swapping a units of token0 in moves s down to the s' satisfying "
            "a = L*(1/s' - 1/s); swapping a units of token1 in moves s up to the s' "
            "satisfying a = L*(s' - s). All intermediate values are exact rationals and a "
            "single trade may cross several range boundaries, re-activating or "
            "de-activating positions at each one. Liquidity additions and removals change "
            "the positions but do not themselves move the price.",
            "",
            "Initial sqrt price s = %d (integer)." % metadata["initial_sqrt"],
            "",
            "Positions:",
        ]
        for p in metadata["positions"]:
            lines.append("  id %d: lo=%d, hi=%d, L=%d" % (p["id"], p["lo"], p["hi"], p["L"]))
        lines.append("")
        lines.append("Operations, in order:")
        for i, op in enumerate(metadata["ops"]):
            if op["type"] == "swap0":
                lines.append("  %d. swap %d units of token0 in (s goes down)"
                             % (i + 1, op["amount"]))
            elif op["type"] == "swap1":
                lines.append("  %d. swap %d units of token1 in (s goes up)"
                             % (i + 1, op["amount"]))
            elif op["type"] == "add":
                lines.append("  %d. add a position lo=%d, hi=%d, L=%d"
                             % (i + 1, op["lo"], op["hi"], op["L"]))
            else:
                lines.append("  %d. remove the position with id %d" % (i + 1, op["pid"]))
        lines.append("")
        lines.append("After all operations, compute the final sqrt price s and report it "
                     "rounded to the nearest integer (a value at the midpoint rounds up). "
                     "The answer is one integer.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        try:
            return 1.0 if int(str(answer).strip()) == int(entry.answer) else 0.0
        except (ValueError, TypeError):
            return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'liquidity_range_updates (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_dynamic_structures_r5/liquidity_range_updates',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1259343118,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
