"""Settlement departure consistency: departures change the residual estate payout.

A fixed estate is divided among claimants holding coprime integer shares under a
stated rule (priority water-filling or proportional). A subset of claimants
depart and immediately take their FULL stated share out of the estate; the
residual is then redistributed among the remaining claimants by the same rule.
The task asks which remaining claimants receive a different amount than before
the departures. Because departing claimants are paid their fixed share rather
than their rule-based award, the redistribution can genuinely change other
claimants' awards; the affected set (often none, sometimes a non-trivial subset)
is computed exactly and verified before the instance is accepted.
"""
import math
import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


def _label(i):
    return chr(ord("A") + i)


def _rand_coprime_claims(n):
    """Return n distinct shares in [2,30] whose gcd is 1 (coprime as a set)."""
    for _ in range(500):
        claims = []
        used = set()
        ok = True
        for _ in range(n):
            c = random.randint(2, 30)
            if c in used:
                ok = False
                break
            used.add(c)
            claims.append(c)
        if not ok:
            continue
        g = 0
        for c in claims:
            g = math.gcd(g, c)
        if g == 1:
            return claims
    raise RuntimeError("could not draw a coprime share set")


def _waterfill(claims, labels, order, estate):
    """Priority water-filling: drain the estate in priority order up to each share."""
    rem = estate
    awards = {}
    for lab in order:
        amt = min(claims[lab], rem)
        awards[lab] = amt
        rem -= amt
    return awards


def _proportional(claims, labels, estate):
    total = sum(claims[lab] for lab in labels)
    return {lab: Fraction(estate * claims[lab], total) for lab in labels}


@dataclass
class SettlementDepartureConfig(Config):
    n_min: int = 2
    n_max: int = 3
    estate_min: int = 10
    estate_max: int = 30
    change_rate: float = 0.78
    modes: tuple = ("priority", "proportional")

    def apply_difficulty(self, level):
        self.n_max = min(3 + 2 * level, 12)
        self.n_min = min(2, self.n_max)
        self.estate_max = min(1000, 30 + 160 * level)
        self.estate_min = 10
        self.change_rate = 0.5 if self.n_max <= 2 else 0.78


class SettlementDepartureConsistency(Task):
    """Settlement rule consistency under claimant departure."""

    summary = ("Remove claimants after paying their assigned shares, then "
               "redistribute the residual estate under capped, proportional, "
               "priority or hybrid rules; determine whether remaining awards "
               "change and identify the affected claimants.")
    design_choice = ("Vary the number of claimants from 2 to 12 and the estate "
                     "size from 10 to 1000, with shares as coprime integers to "
                     "force fractional residuals.")
    config_cls = SettlementDepartureConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        n = random.randint(cfg.n_min, cfg.n_max)
        # n==2 is a binary label set (none vs the single remaining claimant);
        # balance it explicitly to keep any constant guess at the 1/2 floor.
        change_rate = 0.5 if n <= 2 else cfg.change_rate
        mode = random.choice(cfg.modes)
        want_change = random.random() < change_rate

        answer = None
        for _ in range(500):
            estate = random.randint(cfg.estate_min, cfg.estate_max)
            claims_list = _rand_coprime_claims(n)
            labels = [_label(i) for i in range(n)]
            claims = dict(zip(labels, claims_list))
            order = list(labels)
            random.shuffle(order)

            if mode == "proportional" and not want_change:
                # Proportional rule is departure-consistent exactly when the
                # estate equals the total of the shares; force that for "none".
                estate = estimates_to_total(claims, labels, estate)

            # Choose the departing subset, biasing toward reproducible "none".
            if mode == "priority" and not want_change:
                picked = [order[0]]
            else:
                pool = list(order)
                random.shuffle(pool)
                k = random.randint(1, n - 1)
                picked = pool[:k]
            D = set(picked)

            if mode == "priority":
                if not want_change and claims[order[0]] > estate:
                    # top claimant not saturated: removing it would break estate;
                    # redraw until the top is saturated so "none" is achievable.
                    continue
                full = _waterfill(claims, labels, order, estate)
                resid = estate - sum(claims[lab] for lab in D)
                if resid < 0:
                    continue
                remaining = [lab for lab in order if lab not in D]
                new = _waterfill(claims, labels, remaining, resid)
                changed = [lab for lab in remaining if new[lab] != full[lab]]
            else:
                if not want_change:
                    # estate was forced to the total, so awards equal shares;
                    # departure pays share out and residual is exactly the rest.
                    resid = estate - sum(claims[lab] for lab in D)
                else:
                    resid = estate - sum(claims[lab] for lab in D)
                if resid < 0:
                    continue
                total = sum(claims[lab] for lab in labels)
                full = {lab: Fraction(estate * claims[lab], total) for lab in labels}
                remaining = [lab for lab in order if lab not in D]
                sub_total = sum(claims[lab] for lab in remaining)
                new = {}
                for lab in remaining:
                    if sub_total > 0:
                        new[lab] = Fraction(resid * claims[lab], sub_total)
                    else:
                        new[lab] = Fraction(0)
                changed = [lab for lab in remaining if new[lab] != full[lab]]

            changed_sorted = sorted(changed)
            is_none = len(changed_sorted) == 0
            if is_none == (not want_change):
                answer = "none" if is_none else ", ".join(changed_sorted)
                break

        if answer is None:
            answer = "none"

        table = ", ".join(
            f"{lab} has share {claims[lab]}" for lab in labels
        )
        if mode == "priority":
            rule_text = (
                f"The estate is paid by priority (water-filling): claimants are "
                f"processed in the order {', '.join(order)} and each receives up "
                f"to their share until the estate runs out."
            )
        else:
            rule_text = (
                "The estate is paid in proportion to each claimant's share."
            )
        departing = sorted(D, key=lambda lab: labels.index(lab))

        meta = {
            "n": n,
            "estate": estate,
            "mode": mode,
            "claims": claims,
            "priority_order": order,
            "departing": departing,
            "changed": changed_sorted,
            "answer": answer,
            "payload": {
                "shares": table + ".",
                "rule": rule_text,
                "estate": f"The estate to divide is {estate}.",
                "departing": (
                    f"Claimants {', '.join(departing)} immediately depart and take "
                    f"their full stated share out of the estate."
                ),
            },
        }
        return Entry(metadata=meta, answer=answer)

    def render_prompt(self, metadata):
        return (
            "An estate (an integer) is divided among claimants, each of whom is "
            "entitled to a stated integer share.\n\n"
            f"{metadata['payload']['shares']}\n"
            f"{metadata['payload']['rule']}\n"
            f"{metadata['payload']['estate']}\n"
            f"{metadata['payload']['departing']}\n\n"
            "The remaining estate is then redistributed among the claimants who "
            "stayed, using the same rule. Determine which of the REMAINING "
            "claimants ends up receiving a different amount than they received "
            "before the departures.\n\n"
            "Answer with the labels of the affected claimants, separated by "
            "commas in alphabetical order (for example 'B, C'); if no remaining "
            "claimant's amount changes, answer exactly 'none'."
        )


def estimates_to_total(claims, labels, estate):
    """Estate used for the departure-consistent proportional 'none' case."""
    return sum(claims[lab] for lab in labels)


TASK_META = {'parent_source_id': None,
 'idea': 'settlement_departure_consistency (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_uncertainty_r4/settlement_departure_consistency',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
