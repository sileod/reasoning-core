import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'weakest_precondition_computation (draw 2 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_invariants_r1/weakest_precondition_computation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2701974858,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _ceil_div(a, b):
    return -((-a) // b)


def _floor_div(a, b):
    return a // b


def _subst(entry, coef, const):
    """Backward substitute x := coef*x + const into bound entry (lo, hi).

    lo <= coef*x_old + const <= hi   (coef > 0)
    => ceil((lo-const)/coef) <= x_old <= floor((hi-const)/coef)
    """
    lo, hi = entry
    nlo = _ceil_div(lo - const, coef) if lo is not None else None
    nhi = _floor_div(hi - const, coef) if hi is not None else None
    return (nlo, nhi)


def _render_interval(lo, hi):
    lo_s = "-inf" if lo is None else str(lo)
    hi_s = "+inf" if hi is None else str(hi)
    return "%s <= x <= %s" % (lo_s, hi_s)


def _canon_intervals(intervals):
    """Render a merged list of intervals as a canonical DNF over x.

    Intervals already sorted/merged; join with ' || ' (logical or).
    """
    parts = [_render_interval(lo, hi) for (lo, hi) in intervals]
    return " || ".join(parts)


def _render_prog(prog, indent=0):
    out = []
    pad = "    " * indent
    for stmt in prog:
        if stmt[0] == "assign":
            _, coef, const = stmt
            out.append("%s x := %s*x + %s" % (pad, coef, const))
        elif stmt[0] == "if":
            _, glo, ghi, th, el = stmt
            out.append("%s if %s <= x <= %s then" % (pad, glo, ghi))
            out.extend(_render_prog(th, indent + 1))
            out.append("%s else" % pad)
            out.extend(_render_prog(el, indent + 1))
            out.append("%s end" % pad)
    return out


def _render_post(post):
    parts = [_render_interval(lo, hi) for (lo, hi) in post]
    return " and ".join(parts)


@dataclass
class WPCConfig(Config):
    depth: int = 1
    nassign: int = 2
    bounds: int = 3

    def apply_difficulty(self, level):
        self.depth = 1 + level
        self.nassign = 2 + level


class WeakestPreconditionComputation(Task):
    summary = ("Push a stated postcondition backward through assignments and "
               "guarded branches of small integer programs, simplifying to a "
               "canonical linear predicate over the input variables.")
    design_choice = ("Include guarded conditional branches (if-else) where each branch may assign "
                     "different linear expressions, requiring the weakest precondition to be a "
                     "conjunction of implications or a max/min of linear predicates over the "
                     "input variables.")
    config_cls = WPCConfig
    task_version = 2

    def generate_entry(self):
        for _ in range(120):
            entry = self._try()
            if entry is not None:
                return entry
        raise RuntimeError("failed to generate instance")

    def _try(self):
        B = self.config.bounds
        nass = self.config.nassign

        kind = random.choice(["lower", "upper", "band"])
        if kind == "lower":
            a = random.randint(-B, B)
            post = [(a, None)]
        elif kind == "upper":
            b = random.randint(-B, B)
            post = [(None, b)]
        else:
            a = random.randint(-B, B)
            b = random.randint(-B, B)
            if a > b:
                a, b = b, a
            post = [(a, b)]

        prog = self._build_prog(nass, B)
        wp = self._compute_wp(prog, post)
        if wp is None:
            return None
        canon = _canon_intervals(wp)

        for x in range(-80, 81):
            res = self._run(prog, x)
            pre = self._intervals_hold(wp, x)
            posth = self._bounds_hold_list(post, res)
            if pre != posth:
                return None

        metadata = {"program": prog, "post": post, "wp": canon}
        return Entry(metadata=metadata, answer=canon)

    def _build_prog(self, nass, B):
        def arand():
            return (random.randint(1, 3), random.randint(-B, B))

        prog = []
        nlead = random.randint(0, max(0, nass))
        for _ in range(nlead):
            prog.append(("assign",) + arand())
        # exactly one guarded branch
        prog.append(("if", random.randint(-2, 1), random.randint(0, 2),
                     [("assign",) + arand()], [("assign",) + arand()]))
        ntail = random.randint(0, nass)
        for _ in range(ntail):
            prog.append(("assign",) + arand())
        return prog

    def _compute_wp(self, prog, post):
        alts = [[e for e in post]]
        i = len(prog) - 1
        while i >= 0:
            stmt = prog[i]
            if stmt[0] == "assign":
                _, coef, const = stmt
                alts = [[_subst(e, coef, const) for e in alt] for alt in alts]
            else:
                _, glo, ghi, th, el = stmt
                wp_t = self._wp_block(th, alts)
                wp_e = self._wp_block(el, alts)
                new_alts = []
                for alt in wp_t:
                    new_alts.append([(glo, ghi)] + list(alt))
                for alt in wp_e:
                    new_alts.append([(None, glo - 1)] + list(alt))
                    new_alts.append([(ghi + 1, None)] + list(alt))
                alts = new_alts
            i -= 1
        return self._union_intervals(alts)

    def _wp_block(self, blk, tail_alts):
        alts = [list(a) for a in tail_alts]
        for stmt in reversed(blk):
            _, coef, const = stmt
            alts = [[_subst(e, coef, const) for e in alt] for alt in alts]
        return alts

    def _union_intervals(self, alts):
        intervals = []
        for alt in alts:
            los = [l for (l, h) in alt if l is not None]
            his = [h for (l, h) in alt if h is not None]
            lo = max(los) if los else None
            hi = min(his) if his else None
            if lo is not None and hi is not None and lo > hi:
                continue  # empty alternative contributes nothing
            intervals.append((lo, hi))
        if not intervals:
            return None
        intervals.sort(key=lambda t: ((t[0] if t[0] is not None else -10**9),
                                      (t[1] if t[1] is not None else 10**9)))
        merged = [intervals[0]]
        for (lo, hi) in intervals[1:]:
            mlo, mhi = merged[-1]
            prev_hi = mhi if mhi is not None else 10**9
            cur_lo = lo if lo is not None else -10**9
            if cur_lo <= prev_hi + 1:
                nlo = mlo if mlo is not None else lo
                nhi = hi if hi is not None else mhi
                merged[-1] = (nlo, nhi)
            else:
                merged.append((lo, hi))
        return merged

    def _run(self, prog, x):
        val = x
        for stmt in prog:
            if stmt[0] == "assign":
                _, coef, const = stmt
                val = coef * val + const
            else:
                _, glo, ghi, th, el = stmt
                blk = th if glo <= val <= ghi else el
                for s2 in blk:
                    _, coef, const = s2
                    val = coef * val + const
        return val

    def _intervals_hold(self, intervals, x):
        for (lo, hi) in intervals:
            if (lo is None or x >= lo) and (hi is None or x <= hi):
                return True
        return False

    def _bounds_hold_list(self, bounds, x):
        for (lo, hi) in bounds:
            if lo is not None and x < lo:
                return False
            if hi is not None and x > hi:
                return False
        return True

    def render_prompt(self, metadata):
        return self._make_prompt(metadata["program"], metadata["post"])

    def _make_prompt(self, prog, post):
        lines = []
        lines.append("Consider this small program operating on an integer variable x. Statements "
                     "execute in order. An if statement runs its then-branch when the guard "
                     "holds, otherwise its else-branch.")
        lines.extend(_render_prog(prog))
        lines.append("")
        lines.append("We require the program's final value of x to satisfy the postcondition: "
                     "%s" % _render_post(post))
        lines.append("")
        lines.append("The weakest precondition is the condition on the entry value of x that "
                     "guarantees the postcondition holds. Computed backwards, an if-else turns "
                     "into a disjunction: an input satisfies the precondition iff (the guard "
                     "holds and the then-branch's requirement holds) or (the guard fails and "
                     "the else-branch's requirement holds). Because the program is piecewise "
                     "linear in one variable, this collapses to a union of integer intervals of "
                     "x.")
        lines.append("")
        lines.append("Answer on one line as the union of intervals of integer x, each written "
                     "'lo <= x <= hi' with '-inf'/'+inf' for an unbounded side, adjacent "
                     "intervals merged, intervals joined with ' || ' meaning logical or. A "
                     "single interval needs no ' || '. Example answer format: "
                     "'-inf <= x <= 2 || 5 <= x <= +inf'.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry.answer
        if isinstance(answer, str):
            return 1.0 if answer.strip() == gold.strip() else 0.0
        return 0.0
