"""Qualitative limit: path dependence of multivariable rational functions.

f(x, y) = P(x, y) / Q(x, y). We ask whether f approaches a single value as (x, y) approaches the
origin along all admissible paths, or whether different paths give different limits (DIVERGES).

Design: the denominator's zero set decides it.
  * DIVERGES -- Q's zero set is a line through the approach point, separating the domain: paths on
    different sides reach different finite values (or infinity), so there is no unique limit.
  * CONVERGES -- Q's zero set does not pass through the approach point (Q is continuous and nonzero
    there), so every admissible path reaches the same finite rational limit P(0,0)/Q(0,0).
"""

import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'qualitative_limit_path_dependence (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_counterfactual_r4/qualitative_limit_path_dependence',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _frac(n, d):
    g = math.gcd(abs(n), abs(d))
    n, d = n // g, d // g
    if d < 0:
        n, d = -n, -d
    return n, d


def _parse_ratio(s):
    """Parse a reduced rational 'a' or 'a/b'; returns (num, den) canonical or None."""
    s = s.strip()
    if "/" in s:
        parts = s.split("/")
        if len(parts) != 2:
            return None
        n_str, d_str = parts
    else:
        n_str, d_str = s, "1"
    try:
        n = int(n_str)
        d = int(d_str)
    except ValueError:
        return None
    if d == 0:
        return None
    n, d = _frac(n, d)
    if d < 0:
        d = -d
    return n, d


def _render_lin(a, b, c):
    """Render ax + by + c with minimal notation."""
    parts = []
    if a != 0:
        parts.append(("x" if a == 1 else ("-x" if a == -1 else f"{a}x")))
    if b != 0:
        if not parts:
            parts.append(("y" if b == 1 else ("-y" if b == -1 else f"{b}y")))
        else:
            parts.append(("+ y" if b == 1 else ("- y" if b == -1 else f"+ {b}y" if b > 0 else f"- {-b}y")))
    if c != 0 or not parts:
        if parts:
            parts.append(("+ " + str(c) if c > 0 else "- " + str(-c)))
        else:
            parts.append(str(c))
    return " ".join(parts)


def _render_rat(num_terms, den_terms):
    return f"({_render_lin(*num_terms)}) / ({_render_lin(*den_terms)})"


class LimitConfig(Config):
    level: int = 0
    maxc: int = 2

    def apply_difficulty(self, level):
        self.level = level
        self.maxc = 2 + level


class QualitativeLimitPathDependence(Task):
    """Determine whether multivariable rational functions approach one value across all admissible
    paths; vary rational forms (linear-over-linear ratios), pieces/linear zero sets that may separate
    the domain, and constrained approaches through them; answer the common path limit as a canonical
    rational number or DIVERGES when the denominator's zero set separates the domain into conflicting
    values."""
    summary = ("Determine whether multivariable rational functions approach one value over all "
               "admissible paths; vary linear-over-linear ratios with rational coefficients whose "
               "denominator zero set may or may not pass through the approach point; answer the "
               "common path limit as a canonical rational number when the zero set does not separate "
               "the domain, or DIVERGES when different admissible paths reach different limits.")
    design_choice = ("Answer as a canonical rational number or the string 'DIVERGES', with instances "
                     "built from rational functions whose path dependence is decided by whether the "
                     "denominator's zero set separates the domain.")
    config_cls = LimitConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        mc = cfg.maxc

        # Fixed small set of convergent limits so the outcome distribution is a balanced,
        # small label set: DIVERGES plus a handful of distinct rational values.
        conv_limits = [("1/2", (1, 2)), ("1", (1, 1)), ("2", (2, 1)),
                       ("3", (3, 1)), ("1/3", (1, 3))]

        mode = random.random() < 0.5
        if mode:
            # DIVERGES: f = (y - a x) / (y - b x), a != b. The denominator zero line y = b x
            # passes through the origin and separates the domain, so different admissible paths
            # (y = t x for t != b) give different finite limits -> no unique limit.
            while True:
                a = random.randint(-mc, mc)
                if a == 0:
                    continue
                b = random.randint(-mc, mc)
                if b in (0, a):
                    continue
                break
            if random.random() < 0.5:
                num_terms = (a, -1, 0)   # a x - y
                den_terms = (b, -1, 0)   # b x - y
            else:
                num_terms = (-a, 1, 0)   # -a x + y
                den_terms = (-b, 1, 0)   # -b x + y
            answer = "DIVERGES"
        else:
            # CONVERGES: f = (p x + q y + r) / (s x + t y + u) with u != 0, so the denominator's
            # zero set misses the origin and the function is continuous there; every admissible
            # path reaches r / u. Pick the limit from the small label set.
            label, (n, d) = random.choice(conv_limits)
            p = random.randint(-mc, mc)
            q = random.randint(-mc, mc)
            s = random.randint(-mc, mc)
            t = random.randint(-mc, mc)
            # ensure at least one non-constant numerator term so the instance is not trivial
            if p == 0 and q == 0:
                p = random.randint(1, mc)
            if random.random() < 0.5:
                q = 0
            num_terms = (p, q, n)
            den_terms = (s, t, d)
            answer = "0" if n == 0 else label

        prompt = (
            f"Consider the multivariable rational function\n"
            f"    f(x, y) = {_render_rat(num_terms, den_terms)}\n"
            f"defined wherever its denominator is nonzero. As the point (x,y) approaches the "
            f"origin along all admissible paths, does f(x,y) approach a single value that is "
            f"the same for every admissible path? If yes, give that limit as a reduced rational "
            f"number (use 0 for zero, 1/2-style for fractions). If different admissible paths "
            f"give different limits, write DIVERGES. The answer is one value."
        )

        return Entry(metadata={"num_terms": num_terms, "den_terms": den_terms,
                               "mode": "DIVERGES" if mode else "CONVERGES",
                               "prompt": prompt}, answer=answer)

    def render_prompt(self, metadata):
        return metadata["prompt"]

    def score_answer(self, answer, entry):
        gold = entry.answer
        a = answer.strip()
        if gold == "DIVERGES":
            return 1.0 if a == "DIVERGES" else 0.0
        if a == "DIVERGES":
            return 0.0
        parsed = _parse_ratio(a)
        if parsed is None:
            return 0.0
        gold_parsed = _parse_ratio(gold)
        return 1.0 if parsed == gold_parsed else 0.0
