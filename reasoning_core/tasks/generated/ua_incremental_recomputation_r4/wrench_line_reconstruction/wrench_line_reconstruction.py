"""Wrench line reconstruction: reexpress integer force systems as a resultant
force-moment pair at a chosen reference point, locate the central axis, and
extract its pitch, distinguishing pure couples by a canonical token.
"""

import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


def _gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a or 1


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def _add(a, b):
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]


def _sub(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def _scale(a, s):
    return [a[0] * s, a[1] * s, a[2] * s]


def _vec_eq(a, b):
    return a[0] == b[0] and a[1] == b[1] and a[2] == b[2]


def _reduce_frac(num, den):
    if den < 0:
        num, den = -num, -den
    if num == 0:
        return 0, 1
    g = _gcd(num, den)
    return num // g, den // g


def _frac_str(num, den):
    n, d = _reduce_frac(num, den)
    if d == 1:
        return str(n)
    return "{}/{}".format(n, d)


def _fr(fr):
    n, d = fr
    if d == 1:
        return str(n)
    return "{}/{}".format(n, d)


def _vec3_str(v):
    return "[{}, {}, {}]".format(_fr(v[0]), _fr(v[1]), _fr(v[2]))


def _ivec_str(v):
    return "[{}, {}, {}]".format(v[0], v[1], v[2])


def _axis_repr(d, p0):
    """Central axis through fractional point p0 along integer direction d.
    Return 'piercing point | direction' where the piercing point sets the
    largest-magnitude direction component's coordinate to zero, in reduced
    fraction form, and direction is the canonical reduced integer vector."""
    g = _gcd(_gcd(d[0], d[1]), d[2])
    dr = [d[0] // g, d[1] // g, d[2] // g]
    if dr[0] < 0 or (dr[0] == 0 and dr[1] < 0) or (dr[0] == 0 and dr[1] == 0 and dr[2] < 0):
        dr = [-dr[0], -dr[1], -dr[2]]
    comps = [abs(c) for c in dr]
    coord = comps.index(max(comps))
    # point p0 + t*dr with t chosen so coordinate `coord` becomes 0.
    p0f = [Fraction(a, b) for (a, b) in p0]
    t = -p0f[coord] / dr[coord]
    pt = [p0f[k] + t * dr[k] for k in range(3)]
    # convert to reduced int pairs
    out = []
    for fr in pt:
        out.append((fr.numerator, fr.denominator))
    return "{} along {}".format(_vec3_str(out), _ivec_str(dr))


def _frac(num, den):
    n, d = _reduce_frac(num, den)
    return (n, d)


def _find_axis_point_exact(F, M):
    """Rational point p on the central axis, the unique point closest to the
    origin: p = (F x M) / (F.F). Always valid for F != 0. Built with integer
    arithmetic."""
    FF = _dot(F, F)
    FM = _cross(F, M)
    out = []
    for k in range(3):
        n, d = _reduce_frac(FM[k], FF)
        out.append((n, d))
    return out


def _verify_axis(F, M, pt, MF, FF, pitch_str):
    pitch = Fraction(*_reduce_frac(MF, FF))
    p = [Fraction(*fr) for fr in pt]
    Ff = [Fraction(c) for c in F]
    Mf = [Fraction(c) for c in M]
    pxF = [
        p[1] * Ff[2] - p[2] * Ff[1],
        p[2] * Ff[0] - p[0] * Ff[2],
        p[0] * Ff[1] - p[1] * Ff[0],
    ]
    rhs = [Mf[k] - pitch * Ff[k] for k in range(3)]
    assert pxF == rhs, (F, M, pt, pxF, rhs)
    assert _vec3_str(pt) != ""
    assert pitch_str == _fr((pitch.numerator, pitch.denominator)), (pitch_str, pitch)


@dataclass
class WrenchLineConfig(Config):
    max_coord: int = 8

    def apply_difficulty(self, level):
        self.max_coord = 2 + 3 * level


class WrenchLineReconstruction(Task):
    summary = ("Reexpress integer force systems as resultant force-moment pairs at a "
               "reference point, locate the central axis in reduced-fraction form, "
               "extract its pitch, and signal pure couples with a canonical token; "
               "covers general, concurrent, parallel and pure-couple regimes.")
    design_choice = ("Use integer-valued wrench coordinates and ask for the central axis "
                     "in reduced fraction form, with pure couples signaled by a canonical "
                     "'pure couple' token.")
    config_cls = WrenchLineConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        mc = cfg.max_coord
        variant = random.choice(["general", "concurrent", "parallel", "couple"])

        if variant == "couple":
            cr = [random.randint(1, mc), random.randint(1, mc), random.randint(1, mc)]
            if random.random() < 0.5:
                cr = [-cr[0], -cr[1], -cr[2]]
            g = _gcd(_gcd(cr[0], cr[1]), cr[2])
            crr = [cr[0] // g, cr[1] // g, cr[2] // g]
            if crr[0] < 0 or (crr[0] == 0 and crr[1] < 0) or (crr[0] == 0 and crr[1] == 0 and crr[2] < 0):
                crr = [-crr[0], -crr[1], -crr[2]]
            ref = [random.randint(-mc, mc) for _ in range(3)]
            F = [0, 0, 0]
            M = list(cr)
            axis_answer = "pure couple"
            pitch_answer = "pure couple"
            forces = []
        elif variant == "concurrent":
            intersect = [random.randint(-mc, mc) for _ in range(3)]
            ref = [random.randint(-mc, mc) for _ in range(3)]
            if _vec_eq(ref, intersect):
                ref[0] += 1
            F = [0, 0, 0]
            for _ in range(random.randint(2, 3)):
                f = [random.randint(-mc, mc) for _ in range(3)]
                if f == [0, 0, 0]:
                    f[0] = random.randint(1, mc)
                F = _add(F, f)
            if _vec_eq(F, [0, 0, 0]):
                F = [random.randint(1, mc), random.randint(1, mc), random.randint(1, mc)]
            r = [intersect[k] - ref[k] for k in range(3)]
            M = _cross(r, F)
            p0f = _find_axis_point_exact(F, M)
            axis_answer = _axis_repr(F, p0f)
            pitch_answer = "0"
            FF = _dot(F, F)
            MF = _dot(M, F)
            assert _reduce_frac(MF, FF) == (0, 1)
            forces = [F]
        elif variant == "parallel":
            base = [random.randint(-mc, mc) for _ in range(3)]
            if base == [0, 0, 0]:
                base = [1, 0, 0]
            while base[1] == 0 and base[2] == 0:
                base[1] = random.randint(1, mc)
            F = [0, 0, 0]
            lines = []
            for _ in range(random.randint(2, 3)):
                lam = random.randint(-mc, mc)
                if lam == 0:
                    lam = 1
                Fi = _scale(base, lam)
                pi = [random.randint(-mc, mc) for _ in range(3)]
                lines.append((pi, Fi))
                F = _add(F, Fi)
            if _vec_eq(F, [0, 0, 0]):
                F = _scale(base, 1)
                lines[0] = (lines[0][0], _scale(base, -1))
            ref = [random.randint(-mc, mc) for _ in range(3)]
            M = [0, 0, 0]
            for pi, Fi in lines:
                ri = [pi[k] - ref[k] for k in range(3)]
                M = _add(M, _cross(ri, Fi))
            p0f = _find_axis_point_exact(F, M)
            axis_answer = _axis_repr(F, p0f)
            FF = _dot(F, F)
            MF = _dot(M, F)
            pitch_answer = _frac_str(MF, FF)
            forces = [l[1] for l in lines]
        else:  # general
            ref = [random.randint(-mc, mc) for _ in range(3)]
            F = [0, 0, 0]
            M = [0, 0, 0]
            forces = []
            for _ in range(random.randint(2, 3)):
                f = [random.randint(-mc, mc) for _ in range(3)]
                if f == [0, 0, 0]:
                    f = [1, 1, 1]
                pi = [random.randint(-mc, mc) for _ in range(3)]
                forces.append(f)
                ri = [pi[k] - ref[k] for k in range(3)]
                M = _add(M, _cross(ri, f))
                F = _add(F, f)
            if _vec_eq(F, [0, 0, 0]):
                if _vec_eq(M, [0, 0, 0]):
                    return self.generate_entry()
                g = _gcd(_gcd(M[0], M[1]), M[2])
                crr = [M[k] // g for k in range(3)]
                if crr[0] < 0 or (crr[0] == 0 and crr[1] < 0) or (crr[0] == 0 and crr[1] == 0 and crr[2] < 0):
                    crr = [-crr[0], -crr[1], -crr[2]]
                axis_answer = "pure couple"
                pitch_answer = "pure couple"
                forces = forces
                found = True
            else:
                found = False

            if not found:
                p0f = _find_axis_point_exact(F, M)
                axis_answer = _axis_repr(F, p0f)
                FF = _dot(F, F)
                MF = _dot(M, F)
                pitch_answer = _frac_str(MF, FF)

        ref = list(ref)
        metadata = {
            "reference": ref,
            "resultant_force": list(F),
            "moment": list(M),
            "variant": variant,
            "axis": axis_answer,
            "pitch": pitch_answer,
        }
        answer = "{} | {}".format(axis_answer, pitch_answer)

        # ---- self-verification ----
        if axis_answer != "pure couple":
            FF = _dot(F, F)
            MF = _dot(M, F)
            pn, pd = _reduce_frac(MF, FF)
            assert _frac_str(MF, FF) == pitch_answer, (F, M, pitch_answer)
            p0f = _find_axis_point_exact(F, M)
            _verify_axis(F, M, p0f, MF, FF, pitch_answer)
        return Entry(metadata=metadata, answer=answer)
    def render_prompt(self, metadata):
        ref = _ivec_str(metadata["reference"])
        F = _ivec_str(metadata["resultant_force"])
        M = _ivec_str(metadata["moment"])
        return (
            "A wrench acting on a rigid body is described at the reference point P={} by a "
            "resultant force vector F={} and a moment vector M={} about P (standard right-"
            "handed basis). Reexpress it as its central axis: give a point that lies on the "
            "central axis together with the axis direction, and the screw pitch. "
            "Answer format: '[x, y, z] along [dx, dy, dz] | pitch', where the point "
            "coordinates are reduced fractions, the direction integers are reduced with the "
            "first nonzero component (x then y then z) positive, and the pitch is a reduced "
            "fraction. If F is the "
            "zero vector and M is not, it is a pure couple and you must answer exactly 'pure "
            "couple | pure couple'.".format(ref, F, M)
        )

    def score_answer(self, answer, entry):
        gold = "{} | {}".format(entry.metadata["axis"], entry.metadata["pitch"])
        if isinstance(answer, str):
            return 1.0 if answer.strip() == gold else 0.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'wrench_line_reconstruction (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_incremental_recomputation_r4/wrench_line_reconstruction',
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
