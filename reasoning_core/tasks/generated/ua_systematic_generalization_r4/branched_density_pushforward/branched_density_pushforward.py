import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


# -------- exact piecewise math with Fraction arithmetic --------


def _seg_value(segs, x):
    """Value of the piecewise-constant source density ``segs`` at point ``x``."""
    for (a, b, v) in segs:
        if a <= x < b:
            return v
    a, b, v = segs[-1]
    if x <= b:
        return v
    raise RuntimeError(f"no segment for x={x}: {segs}")


def _integral_segs(segs):
    total = Fraction(0)
    for (a, b, v) in segs:
        total += v * (b - a)
    return total


def _pushforward(segs, f):
    """Push a piecewise-constant density through a piecewise-affine map.

    ``segs`` is a list of (a, b, value) Fractions partitioning [0, 1].
    ``f`` is a list of (a, b, m, c) Fractions partitioning [0, 1], each an
    affine branch f(x)=m*x+c on [a, b).  Returns (qlist, atoms) where qlist is
    the exact continuous part of the pushforward density [(a, b, value)] and
    atoms is [(y, mass)] for flat branches.
    """
    breakpoints = set()
    for (a, b, m, c) in f:
        if m == 0:
            continue
        breakpoints.add(m * a + c)
        breakpoints.add(m * b + c)
        for (sa, sb, _v) in segs:
            for s in (sa, sb):
                if a < s < b:
                    breakpoints.add(m * s + c)
    bps = sorted(x for x in breakpoints if Fraction(0) <= x <= Fraction(1))

    atoms = []
    for (a, b, m, c) in f:
        if m == 0:
            mass = Fraction(0)
            for (sa, sb, v) in segs:
                lo = max(a, sa)
                hi = min(b, sb)
                if hi > lo:
                    mass += v * (hi - lo)
            if mass > 0:
                atoms.append((Fraction(c), mass))

    qlist = []
    for y0, y1 in zip(bps, bps[1:]):
        if y1 <= y0:
            continue
        ymid = (y0 + y1) / 2
        val = Fraction(0)
        for (a, b, m, c) in f:
            if m == 0:
                continue
            x = (ymid - c) / m
            if a < x < b:
                val += _seg_value(segs, x) / abs(m)
        if val > 0:
            qlist.append((y0, y1, val))
    return qlist, atoms


def _continuous_mass(qlist):
    total = Fraction(0)
    for (a, b, v) in qlist:
        total += v * (b - a)
    return total


def _is_nonmonotone(ys):
    for i in range(1, len(ys) - 1):
        if (ys[i - 1] < ys[i] > ys[i + 1]) or (ys[i - 1] > ys[i] < ys[i + 1]):
            return True
    return False


def _has_plateau(ys):
    return any(ys[i] == ys[i + 1] for i in range(len(ys) - 1))


def _build_map(n, allow_flat):
    """A continuous piecewise-affine map [0,1]->[0,1] that is surjective and
    noninjective (has a fold), optionally with a flat region."""
    if n <= 0:
        raise RuntimeError("map needs at least one piece")
    denom = n * 4
    for _ in range(200):
        xs = [Fraction(i, n) for i in range(n + 1)]
        ys = [Fraction(0)] * (n + 1)
        ys[0] = Fraction(0)
        ys[-1] = Fraction(1)
        for i in range(1, n):
            ys[i] = Fraction(random.randint(1, denom - 1), denom)
        if allow_flat and n >= 2 and random.random() < 0.45:
            i = random.randrange(1, n)
            ys[i + 1] = ys[i]
        if not _is_nonmonotone(ys):
            continue
        if not allow_flat and _has_plateau(ys):
            continue
        branches = []
        for i in range(n):
            a, b = xs[i], xs[i + 1]
            m = (ys[i + 1] - ys[i]) / (b - a)
            c = ys[i] - m * a
            branches.append((a, b, m, c))
        return branches
    raise RuntimeError("could not build a folded map")


def _identity_map():
    return [(Fraction(0), Fraction(1), Fraction(1), Fraction(0))]


def _build_source(n):
    cuts = {Fraction(0), Fraction(1)}
    for _ in range(n - 1):
        cuts.add(Fraction(random.randint(1, 11), 12))
    cuts = sorted(cuts)
    segs = []
    for a, b in zip(cuts, cuts[1:]):
        v = Fraction(random.randint(1, 5), 5)
        segs.append((a, b, v))
    return segs


def _bin_index(x, n):
    i = int(x * n)
    if i >= n:
        i = n - 1
    if i < 0:
        i = 0
    return i


def _fmt(fr):
    fr = Fraction(fr)
    if fr.denominator == 1:
        return str(fr.numerator)
    return f"{fr.numerator}/{fr.denominator}"


def _parse_frac(t):
    t = t.strip()
    if "/" in t:
        a, b = t.split("/")
        return Fraction(int(a), int(b))
    return Fraction(int(t))


def _format_answer(densities, atoms):
    canon = ",".join(_fmt(d) for d in densities)
    if atoms:
        ats = ",".join(
            f"{_fmt(y)}:{_fmt(m)}"
            for (y, m) in sorted(atoms, key=lambda t: (t[0], t[1]))
        )
        canon += "|" + ats
    return canon


def _canonical(s):
    try:
        s = s.strip()
        if "|" in s:
            dens_s, atom_s = s.split("|", 1)
        else:
            dens_s, atom_s = s, ""
        dens = [_parse_frac(t) for t in dens_s.split(",") if t.strip() != ""]
        atoms = []
        for tok in (t for t in atom_s.split(",") if t.strip() != ""):
            y_s, m_s = tok.split(":", 1)
            atoms.append((_parse_frac(y_s), _parse_frac(m_s)))
        return _format_answer(dens, atoms)
    except Exception:
        return "_invalid_" + str(s)


@dataclass
class DensityPushforwardConfig(Config):
    level: int = 0
    n_source_segments: int = 2
    n_bins: int = 4
    n_pieces: int = 3
    compose: bool = False

    def apply_difficulty(self, level):
        self.n_source_segments = 2 + level
        self.n_bins = 4 + 2 * level
        self.n_pieces = 3 + (1 if level >= 2 else 0)
        self.compose = level >= 3


class BranchedDensityPushforward(Task):
    summary = (
        "Transport piecewise probability densities through noninjective maps by "
        "combining inverse-branch contributions and Jacobian factors; vary folds, "
        "flat regions, and composition, returning a density or atom mass."
    )
    design_choice = (
        "Answer as a canonical piecewise-linear density string over fixed bins, "
        "with each bin's value a rational computed from summed inverse branches."
    )
    config_cls = DensityPushforwardConfig
    task_version = 2

    def generate_entry(self):
        n_bins = self.config.n_bins
        for _ in range(50):
            source = _build_source(self.config.n_source_segments)
            f = _build_map(self.config.n_pieces, allow_flat=False)
            g = _build_map(self.config.n_pieces, allow_flat=True) if self.config.compose \
                else _identity_map()
            total_mass = _integral_segs(source)

            q1, atoms1 = _pushforward(source, f)
            if atoms1:
                continue
            q2, atoms2 = _pushforward(q1, g)

            width = Fraction(1, n_bins)
            bin_mass = [Fraction(0)] * n_bins
            for (a, b, v) in q2:
                for i in range(n_bins):
                    lo = max(a, Fraction(i, n_bins))
                    hi = min(b, Fraction(i + 1, n_bins)) if i < n_bins - 1 else min(b, Fraction(1))
                    if hi > lo:
                        bin_mass[i] += v * (hi - lo)
            densities = [bin_mass[i] / width for i in range(n_bins)]
            atoms = sorted(atoms2, key=lambda t: (t[0], t[1]))

            continuous = sum(bin_mass)
            atom_total = sum(m for (_y, m) in atoms)
            recomputed = continuous + atom_total
            if recomputed != total_mass:
                continue
            if any(d < 0 for d in densities):
                continue
            answer = _format_answer(densities, atoms)
            metadata = {
                "n_bins": n_bins,
                "source": [(str(a), str(b), str(v)) for (a, b, v) in source],
                "f": [(str(a), str(b), str(m), str(c)) for (a, b, m, c) in f],
                "g": [(str(a), str(b), str(m), str(c)) for (a, b, m, c) in g],
                "compose": bool(self.config.compose),
                "total_mass": str(total_mass),
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("failed to generate a valid pushforward example")

    def render_prompt(self, metadata):
        nb = metadata["n_bins"]
        bins = []
        for i in range(nb):
            lo = Fraction(i, nb)
            hi = Fraction(1) if i == nb - 1 else Fraction(i + 1, nb)
            closer = "]" if i == nb - 1 else ")"
            bins.append(f"[{_fmt(lo)},{_fmt(hi)}{closer}")
        bins_s = ", ".join(bins)
        source_s = ", ".join(
            f"p(x) = {v} on [{a},{b})" for (a, b, v) in metadata["source"]
        )
        f_s = ", ".join(
            f"on [{a},{b}): f(x)={m}*x+{c} " for (a, b, m, c) in metadata["f"]
        )
        g_s = ", ".join(
            f"on [{a},{b}): g(x)={m}*x+{c} " for (a, b, m, c) in metadata["g"]
        )
        M = metadata["total_mass"]
        lines = [
            "A piecewise-constant probability density on [0,1] is pushed forward "
            f"through piecewise-affine maps. Its total mass is {M}.",
            "",
            f"Source density p (positive, piecewise-constant, total mass {M}):",
            source_s,
            "",
            "Map f (piecewise affine, surjective onto [0,1], with a fold and no "
            "flat region):",
            f_s,
            "",
            "Map g (piecewise affine, surjective onto [0,1]):",
            g_s,
            "",
            f"Push p forward through f to get an intermediate density, then push "
            f"that density forward through g, obtaining the distribution T on [0,1]. "
            f"Partition [0,1] into the {nb} equal bins {bins_s}.",
            "",
            "For each bin give the average density of the continuous part of T in "
            "the bin: (mass of the continuous part of T lying in the bin)/(bin "
            "width). A flat region of a map gathers the p-mass it receives into an "
            "atom at the flat region's value; list any atoms of T as location:mass.",
            "",
            "Answer as the N bin densities -- a comma-separated list of reduced "
            "fractions -- then, if there are atoms, a vertical bar then the atoms "
            "(comma-separated, each location:mass, sorted by location). Example: "
            '"1/2,0,3/4,1|1/3:2/5".',
        ]
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        return int(_canonical(answer) == _canonical(entry.answer))


TASK_META = {'parent_source_id': None,
 'idea': 'branched_density_pushforward (variant 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_systematic_generalization_r4/branched_density_pushforward',
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
