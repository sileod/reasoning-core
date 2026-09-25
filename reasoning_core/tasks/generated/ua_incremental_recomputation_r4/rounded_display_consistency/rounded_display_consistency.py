"""Rounded display consistency v2 (variant 2 of 3).

From linked rounded readings of two latent whole counts and their sum, recover
the tight feasible interval for a queried composite quantity (a single latent,
their sum, or their difference), or report that no consistent assignment exists.
"""

import math
import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


def _round_display(z, inc, tie):
    """Nearest multiple of `inc` to integer z, ties broken per `tie`."""
    low = (z // inc) * inc
    high = low + inc
    dl = z - low
    dh = high - z
    if dl < dh:
        return low
    if dh < dl:
        return high
    if tie == "half_up":
        return high
    if tie == "half_down":
        return low
    if (low // inc) % 2 == 0:
        return low
    return high


def _multiple_bounds(D, inc, tie):
    """Integer range (lo, hi) of z with _round_display(z, inc, tie) == D, or None."""
    low = Fraction(2 * D - inc, 2)
    high = Fraction(2 * D + inc, 2)
    if tie == "half_up":
        lo = int(math.ceil(low))
        hi = int(math.ceil(high)) - 1
    elif tie == "half_down":
        lo = int(math.floor(low)) + 1
        hi = int(math.floor(high))
    else:  # half_even
        if (D // inc) % 2 == 0:
            lo = int(math.ceil(low))
            hi = int(math.floor(high))
        else:
            lo = int(math.floor(low)) + 1
            hi = int(math.ceil(high)) - 1
    if lo > hi:
        return None
    return (lo, hi)


def _tight_range(X, Y, S, ix, iy, is_, tie, off, query):
    """Return (feasible, lo, hi) of tight whole-number range for `query`, or feasible False."""
    xb = _multiple_bounds(X, ix, tie)
    yb = _multiple_bounds(Y, iy, tie)
    sb = _multiple_bounds(S, is_, tie)
    if xb is None or yb is None or sb is None:
        return (False, 0, 0)
    xl, xh = xb[0] - off, xb[1] - off
    yl, yh = yb[0] - off, yb[1] - off
    slo, shi = sb[0] - off, sb[1] - off

    first = True
    minq = maxq = 0
    for x in range(xl, xh + 1):
        yL = max(yl, slo - x)
        yH = min(yh, shi - x)
        if yL > yH:
            continue
        if query == "x":
            lo, hi = x, x
        elif query == "y":
            lo, hi = yL, yH
        elif query == "sum":
            lo, hi = x + yL, x + yH
        else:  # difference x - y
            lo, hi = x - yH, x - yL
        if first:
            minq, maxq = lo, hi
            first = False
        else:
            minq = min(minq, lo)
            maxq = max(maxq, hi)
    if first:
        return (False, 0, 0)
    return (True, minq, maxq)


def _format_answer(feasible, lo, hi):
    if not feasible:
        return "no"
    return "[%d, %d]" % (lo, hi)


@dataclass
class RoundedDisplayConfig(Config):
    inc_pool: tuple = (1, 2)
    latent_extent: int = 20
    p_inconsistent: float = 0.12
    off_extent: int = 3

    def apply_difficulty(self, level):
        self.inc_pool = (1, 2, 3, 5, 7)[: min(2 + level * 2, 5)]
        self.latent_extent = stochastic_rounding(self.latent_extent + 12 * level)
        self.p_inconsistent = min(0.12 + 0.02 * level, 0.22)
        self.off_extent = stochastic_rounding(3 + level)


class RoundedDisplayConsistency(Task):
    summary = (
        "Recover feasible latent values from linked rounded readings; vary "
        "increments, tie rules, shared offsets, and sum displays, returning "
        "consistency or the tight interval for a queried quantity."
    )
    design_choice = (
        "Vary whether the queried quantity is a single latent, a sum of two "
        "latents, or a difference, and require returning the tight interval "
        "for that composite quantity."
    )
    config_cls = RoundedDisplayConfig

    def generate_entry(self):
        cfg = self.config
        tie = random.choice(("half_up", "half_down"))
        ix = random.choice(cfg.inc_pool)
        iy = random.choice(cfg.inc_pool)
        is_ = random.choice(cfg.inc_pool)
        off = random.randint(-cfg.off_extent, cfg.off_extent)
        query = random.choice(("x", "y", "sum", "diff"))
        ext = cfg.latent_extent

        x0 = random.randint(-ext, ext)
        y0 = random.randint(-ext, ext)

        X = _round_display(x0 + off, ix, tie)
        Y = _round_display(y0 + off, iy, tie)
        S0 = _round_display(x0 + y0 + off, is_, tie)

        inconsistent = random.random() < cfg.p_inconsistent
        consistent = not inconsistent
        if inconsistent:
            S = None
            for _ in range(40):
                mag = random.choice((1, 2, 3, 5, 8, 13, 21, 34, 55))
                sign = random.choice((-1, 1))
                Stry = S0 + sign * mag * is_
                Stry = ((Stry + is_ // 2) // is_) * is_
                feas, _, _ = _tight_range(X, Y, Stry, ix, iy, is_, tie, off, query)
                if not feas:
                    S = Stry
                    break
            if S is None:
                S = ((S0 + 1000) // is_) * is_
                feas, _, _ = _tight_range(X, Y, S, ix, iy, is_, tie, off, query)
                if feas:
                    raise RuntimeError("far-shift inconsistent instance came out feasible")
        else:
            S = S0

        feasible, lo, hi = _tight_range(X, Y, S, ix, iy, is_, tie, off, query)
        if consistent:
            if not feasible:
                raise RuntimeError("consistent instance came out infeasible")
        else:
            if feasible:
                raise RuntimeError("inconsistent instance came out feasible")

        query_desc = {"x": "quantity A", "y": "quantity B",
                      "sum": "the sum A + B", "diff": "the difference A - B"}[query]

        metadata = {
            "X": X, "Y": Y, "S": S,
            "incx": ix, "incy": iy, "incs": is_,
            "tie": tie, "offset": off,
            "query": query, "query_desc": query_desc,
            "latent_x": x0, "latent_y": y0,
            "feasible": feasible, "lo": lo, "hi": hi,
        }
        return Entry(metadata=metadata,
                     answer=_format_answer(feasible, lo, hi))

    def render_prompt(self, metadata):
        desc = "\n".join(
            [
                "A merchant records three linked readings, all rounded to a "
                "nearest step with %s ties and a shared grid offset of %d:"
                % (metadata["tie"].replace("_", "-"), metadata["offset"]),
                "quantity A reads %d (step %d)." % (metadata["X"], metadata["incx"]),
                "quantity B reads %d (step %d)." % (metadata["Y"], metadata["incy"]),
                "the sum A + B reads %d (step %d)." % (metadata["S"], metadata["incs"]),
            ]
        )
        return (
            "%s\nAll three readings come from one consistent pair of whole-count "
            "quantities A and B. What is the tightest possible whole-number range "
            "for %s over every consistent assignment? "
            "Reply with the tight range such as [3, 7]; if no assignment is "
            "consistent, reply with the single word no instead."
            % (desc, metadata["query_desc"])
        )

    def score_answer(self, answer, entry):
        return 1.0 if isinstance(answer, str) and answer.strip() == entry.answer else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'rounded_display_consistency (variant 2 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_incremental_recomputation_r4/rounded_display_consistency',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3020341981,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
