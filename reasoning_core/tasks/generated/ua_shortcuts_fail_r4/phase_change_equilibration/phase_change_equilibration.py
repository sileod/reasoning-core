import random
from dataclasses import dataclass
from math import gcd

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'phase_change_equilibration (variant 2 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_shortcuts_fail_r4/phase_change_equilibration',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 382564971,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = ("Have the solver compute the final state by iteratively melting/freezing until the "
                 "enthalpy balance closes, returning temperature as a decimal and phase fraction as a fraction.")

TF = 0.0


def _frac_str(x):
    """Float fraction in [0,1] -> reduced fraction string n/d."""
    numer = round(x * 1000)
    denom = 1000
    g = gcd(numer, denom)
    return f"{numer // g}/{denom // g}"


def _solve(m1, c1, T1, m2, c2liq, c2sol, L2, Tf, T2):
    """Insulated mixing of two materials at constant enthalpy.

    Material 1: mass m1, heat capacity c1, starts solid at T1 < Tf, never
        phase-changes (absorbs sensible heat only).
    Material 2 (the hot, originally-liquid material): mass m2, liquid heat
        capacity c2liq, solid heat capacity c2sol, latent heat of fusion L2,
        freezing point Tf, starts fully liquid at T2 > Tf.

    Returns (T_final, fraction_of_material2_that_freezes).
    Dereases the freeze fraction iteratively by binary search until the
    enthalpy balance closes to within tolerance.
    """
    # Reference: pick the state where both are at Tf (M1 solid at Tf,
    # M2 liquid at Tf). Enthalpies relative to that point.
    # Heat leaving M2 cooling from T2 to Tf (liquid):
    E2_cool = m2 * c2liq * (T2 - Tf)
    # Heat M1 must absorb to reach Tf from T1:
    E1_warm = m1 * c1 * (Tf - T1)

    # If cooling the liquid M2 alone already warms M1 above Tf, no freezing.
    net = E2_cool - E1_warm
    if net >= 0:
        total_cp = m2 * c2liq + m1 * c1
        T = Tf + net / total_cp
        return T, 0.0

    # deficit must be supplied by freezing a fraction f of M2 (which stays at Tf).
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        freeze_heat = mid * m2 * L2
        # balance: heat out of M2 = heat into M1
        lhs = E2_cool + freeze_heat      # released by M2
        rhs = E1_warm                    # absorbed by M1
        if lhs < rhs:
            lo = mid
        else:
            hi = mid
    f = 0.5 * (lo + hi)
    if f < 1.0 - 1e-12:
        return Tf, f

    # freezes everything; whole mixture ends solid at a common T below Tf.
    num = m2 * c2liq * (T2 - Tf) + m2 * L2 + m2 * c2sol * Tf + m1 * c1 * T1
    den = m2 * c2sol + m1 * c1
    return num / den, 1.0


@dataclass
class PhaseConfig(Config):
    mass_range: tuple = (5, 25)
    cp_range: tuple = (1, 5)

    def apply_difficulty(self, level):
        # larger masses == bigger latent interplay, more fractions
        self.mass_range = (self.mass_range[0], self.mass_range[1] + level * 6)
        self.cp_range = (self.cp_range[0], self.cp_range[1] + level)


class PhaseChangeEquilibration(Task):
    summary = ("Conserve enthalpy through insulated mixtures of a phase-locked solid and a "
               "freezing liquid with distinct heat capacities and a latent heat; return the "
               "equilibrium temperature as a decimal and the frozen fraction as a fraction for "
               "all-liquid, co-existing and all-solid final regimes.")
    config_cls = PhaseConfig
    design_choice = design_choice

    def generate_entry(self):
        while True:
            m1 = random.randint(*self.config.mass_range)
            m2 = random.randint(*self.config.mass_range)
            c1 = random.randint(*self.config.cp_range)
            c2liq = random.randint(*self.config.cp_range)
            c2sol = random.randint(*self.config.cp_range)
            L2 = random.randint(60, 400)

            # choose the final regime up front so every one appears at every level
            regime = random.choice(("liq", "mix", "sol"))
            # B = heat absorbed warming solid 1 from T1 to Tf; draw a target interval
            B = random.uniform(100, 20000)
            C = m2 * L2  # latent heat to freeze all of the liquid material
            if regime == "liq":
                A = B + random.uniform(1, 3) * C   # plenty of spare heat, no freezing
            elif regime == "mix":
                f_frac = random.uniform(0.05, 0.95)
                A = B - f_frac * C                  # deficit met by partial freezing
            else:
                A = max(0.0, B - C - random.uniform(0.5, 2.0) * C)

            T1 = TF - B / (m1 * c1)
            T2 = TF + A / (m2 * c2liq)
            if not (-90.0 <= T1 <= -1.0) or not (1.0 <= T2 <= 400.0):
                continue
            if c2sol <= 0 or c2liq <= 0 or L2 <= 0:
                continue

            T, f = _solve(m1, c1, T1, m2, c2liq, c2sol, L2, TF, T2)
            if not (-120.0 <= T <= 410.0):
                continue
            # verify the defining energy balance to reject solver mistakes
            if _verify_balance(m1, c1, T1, m2, c2liq, c2sol, L2, TF, T2, T, f):
                break

        assert 0.0 <= f <= 1.0, f
        T = round(T, 4)
        metadata = {
            "solid": {"mass": m1, "cp": c1, "initial": T1},
            "liquid": {"mass": m2, "cp_liq": c2liq, "cp_sol": c2sol, "latent": L2,
                       "freeze": TF, "initial": T2},
            "T": round(T, 4),
            "frac": _frac_str(f),
        }
        answer = f"{T:g} {metadata['frac']}"
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        s = metadata["solid"]
        l = metadata["liquid"]
        return (
            f"An insulated container mixes a solid and a liquid at constant enthalpy. The solid has "
            f"mass {s['mass']} g, heat capacity {s['cp']} J/(g K) and starts at {s['initial']} C, "
            f"staying solid throughout (no phase change). The liquid has mass {l['mass']} g, liquid "
            f"heat capacity {l['cp_liq']} J/(g K), solid heat capacity {l['cp_sol']} J/(g K), a "
            f"latent heat of fusion {l['latent']} J/g, freezes at {l['freeze']} C, and starts fully "
            f"liquid at {l['initial']} C. Give the final equilibrium temperature as a decimal in "
            f"degrees C (e.g. 12.5). On the same line, after a space, give the fraction of the "
            f"originally-liquid material that ends up frozen, as a reduced fraction n/d (write 0/1 "
            f"if none freezes, 1/1 if all freezes). Example format: `12.5 2/3`."
        )

    def score_answer(self, answer, entry):
        return _score(answer, entry.metadata)


def _verify_balance(m1, c1, T1, m2, c2liq, c2sol, L2, Tf, T2, T, f):
    """Check enthalpy released by M2 equals enthalpy absorbed by M1."""
    if f <= 1e-12:
        # all liquid
        rel = abs(m2 * c2liq * (T2 - T) - m1 * c1 * (T - T1))
        return rel < 1e-3
    if f >= 1.0 - 1e-12:
        rel = abs(m2 * c2liq * (T2 - Tf) + m2 * L2 + m2 * c2sol * (Tf - T) - m1 * c1 * (T - T1))
        return rel < 1e-2
    rel = abs(m2 * c2liq * (T2 - Tf) + f * m2 * L2 - m1 * c1 * (Tf - T1))
    return rel < 1e-2


def _parse(answer):
    parts = answer.strip().split()
    if len(parts) != 2:
        return None
    try:
        T = float(parts[0])
    except ValueError:
        return None
    frac = parts[1]
    if "/" in frac:
        a, b = frac.split("/")
        try:
            fa, fb = float(a), float(b)
        except ValueError:
            return None
        if fb == 0:
            return None
        f = fa / fb
    else:
        try:
            f = float(frac)
        except ValueError:
            return None
    return T, f


def _score(answer, metadata):
    parsed = _parse(answer)
    if parsed is None:
        return 0.0
    T, f = parsed
    gold_T = metadata["T"]
    if abs(T - gold_T) > 0.01:
        return 0.0
    gnum, gden = metadata["frac"].split("/")
    gf = float(gnum) / float(gden)
    if abs(f - gf) > 0.01:
        return 0.0
    return 1.0
