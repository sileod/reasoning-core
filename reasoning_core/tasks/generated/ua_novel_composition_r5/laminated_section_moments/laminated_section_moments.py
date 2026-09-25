import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'laminated_section_moments (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_novel_composition_r5/laminated_section_moments',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1339177894,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _region_moments(r):
    """Stiffness-weighted SE, SMY, SMX over one rectangle.

    r = (cx, cy, hx, hy, theta_rad, E). Local half-extents are hx along the local
    a-axis and hy along the local b-axis. Rotating by theta into the global frame,
    the second moment of area about the global x-axis through the centroid is
    Ixx = (4/3) hx hy^3 cos^2(theta) + (4/3) hy hx^3 sin^2(theta).
    """
    cx, cy, hx, hy, theta, E = r
    area = 4.0 * hx * hy
    c, s = math.cos(theta), math.sin(theta)
    ixx = (4.0 / 3.0) * hx * hy ** 3 * c * c + (4.0 / 3.0) * hy * hx ** 3 * s * s
    se = E * area
    smy = E * area * cy
    smx = E * (ixx + area * cy * cy)
    return se, smy, smx


def _section_quantities(rects):
    se = smy = smx = 0.0
    for r in rects:
        a, b, c = _region_moments(r)
        se += a
        smy += b
        smx += c
    y0 = smy / se
    ei = smx - smy * smy / se
    return y0, ei


def _round_int(x):
    return int(round(x))


@dataclass
class LaminatedSectionConfig(Config):
    level: int = 0
    n_patches: int = 2
    n_holes: int = 0
    n_inserts: int = 0

    def apply_difficulty(self, level):
        self.level = level
        self.n_patches = max(1, 3 - level // 3)
        self.n_holes = level // 3
        self.n_inserts = level // 2


def _make_rect(kind):
    cx = random.randint(-8, 8)
    cy = random.randint(-8, 8)
    hx = random.randint(1, 6)
    hy = random.randint(1, 6)
    if kind == "hole":
        theta = 0.0
        E = random.uniform(0.0, 2.5)
    elif kind == "insert":
        theta = math.radians(random.choice([-60, -45, -30, 30, 45, 60]))
        E = random.uniform(8.0, 16.0)
    else:
        theta = 0.0
        E = random.uniform(4.0, 12.0)
    return (cx, cy, hx, hy, theta, E)


def compute_answer(metadata):
    """Recompute the exact integer answer from stored geometry."""
    rects = [tuple(r) for r in metadata["rects"]]
    steps = metadata["steps"]
    mode = metadata["mode"]
    y0, ei = _section_quantities(rects)
    if mode == "neutral_axis":
        value = y0
    elif mode == "stiffness":
        value = ei
    else:
        iA, iB, yA, yB = steps["query"]
        EA = rects[iA][5]
        EB = rects[iB][5]
        ratio = (EA * (yA - y0)) / (EB * (yB - y0))
        value = ratio
    return _round_int(value)


class LaminatedSectionMoments(Task):
    summary = ("Combine offset material patches, holes, and rotated rectangular "
               "inserts using stiffness-weighted area moments; return the neutral "
               "axis, effective bending stiffness, or stress ratio at queried "
               "locations.")
    config_cls = LaminatedSectionConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        for _ in range(5000):
            kinds = (["patch"] * max(1, cfg.n_patches)
                     + ["hole"] * cfg.n_holes
                     + ["insert"] * cfg.n_inserts)
            random.shuffle(kinds)
            rects = [_make_rect(k) for k in kinds]

            y0, ei = _section_quantities(rects)
            if not (math.isfinite(y0) and math.isfinite(ei)):
                continue

            mode = random.choice(["neutral_axis", "stiffness", "stress_ratio"])
            if mode == "stress_ratio":
                pos = [(i, r) for i, r in enumerate(rects) if r[5] > 0]
                if len(pos) < 2:
                    continue
                (iA, rA), (iB, rB) = random.sample(pos, 2)
                yA = rA[1]
                yB = rB[1]
                if abs(yB - y0) < 1.0 or abs(yA - y0) < 1.0:
                    continue
                ratio = (rA[5] * (yA - y0)) / (rB[5] * (yB - y0))
                if not math.isfinite(ratio) or abs(ratio) > 200.0:
                    continue
                steps = {"query": [iA, iB, yA, yB]}
            else:
                steps = {"query": None}

            if mode == "stress_ratio":
                value = ratio
            elif mode == "neutral_axis":
                value = y0
            else:
                value = ei
            if abs(value) > 1e8:
                continue

            ans = _round_int(value)
            metadata = {
                "mode": mode,
                "rects": [[float(x) for x in r] for r in rects],
                "y0": float(y0),
                "ei": float(ei),
                "steps": steps,
                "answer_int": int(ans),
            }
            return Entry(metadata=metadata, answer=str(ans))

        raise RuntimeError("could not generate a laminated section moment entry")

    def _describe(self, r):
        cx, cy, hx, hy, theta, E = r
        s = (f"a rectangle centred at x={cx}, y={cy} with half-width {hx} and "
             f"half-height {hy}")
        if theta != 0.0:
            deg = int(round(math.degrees(theta)))
            s += f", rotated by {deg} degrees"
        return s

    def _surface_kind(self, r):
        E, theta = r[5], r[4]
        if E < 3.0:
            return "hole"
        if theta != 0.0 and E > 7.5:
            return "rotated stiff insert"
        return "material patch"

    def render_prompt(self, metadata):
        rects = [tuple(r) for r in metadata["rects"]]
        mode = metadata["mode"]
        intros = (
            "A laminated beam cross-section is built from rectangular regions, each "
            "with its own bending stiffness E (units are consistent so only relative "
            "values matter). Bending is about the horizontal x-axis, so within any "
            "region the flexural stress is sigma(y) = E * (y - y0), linear in the "
            "vertical coordinate y, with y0 the neutral axis height where stress is "
            "zero."
        )
        parts = [intros]
        for i, r in enumerate(rects):
            parts.append(f"Region {i}: {self._describe(r)}; it is a "
                         f"{self._surface_kind(r)} with stiffness E = {r[5]:.1f}.")
        if mode == "neutral_axis":
            parts.append("Compute the stiffness-weighted neutral axis location y0 of "
                         "the whole section.")
        elif mode == "stiffness":
            parts.append("Compute the effective bending stiffness "
                         "EI = integral of E (y - y0)^2 dA of the whole section, "
                         "weighted by stiffness.")
        else:
            iA, iB, yA, yB = metadata["steps"]["query"]
            parts.append(f"Compute the ratio of flexural stress at height y={yA} in "
                         f"region {iA} to flexural stress at height y={yB} in region "
                         f"{iB}: sigma(yA) / sigma(yB).")
        parts.append("Give a single integer, rounding any non-integer result to the "
                     "nearest whole number.")
        return " ".join(parts)

    def score_answer(self, answer, entry):
        try:
            val = int(answer.strip())
        except Exception:
            return 0.0
        return 1.0 if val == entry.metadata["answer_int"] else 0.0
