"""Metric geometry by chained facts: find an angle, a length, an area or a volume.

planar_geometry_relations asks qualitative questions about coordinates (orientation, incidence,
which point is closer). This task asks for a measured quantity using school facts: angle sums of
triangles and polygons, isosceles and exterior angles, regular polygons, Pythagorean triangles,
perimeters, areas, circles (answers in pi) and volumes. Each fact turns the previous quantity into a
new one, so a chain of k facts is a k-step problem. The asked kind of quantity is drawn first, from
the same distribution at every level; level only adds steps and widens the numbers.
Answers stay short: integers below 1000, halves, or k*pi with such a k -- never decimals.
"""
import random
from dataclasses import dataclass
from fractions import Fraction as F

import sympy as sp

from reasoning_core.template import Config, DevTask, Entry, stochastic_rounding as sround

TRIPLES = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29)]
NAMES = "ABCDEFGHJKLMNPQRSTUVWXYZ"


@dataclass
class GeometryMeasureConfig(Config):
    steps: float = 1
    scale: int = 12

    def apply_difficulty(self, level):
        self.steps += 0.8 * level
        self.scale += 6 * level


def _fmt(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def _angle_list(n, rng, total):
    """n-1 angles of a convex n-gon, leaving a remaining angle strictly between 0 and 180."""
    for _ in range(100):
        angles = [rng.randint(60, 170) for _ in range(n - 1)]
        rest = total - sum(angles)
        if 0 < rest < 180:
            return angles, rest
    return None, None


def _transforms(kind, x, name, rng, scale):
    """Facts that consume a quantity of `kind` and value `x`: (sentence, new name, new kind, new value)."""
    x, out = F(x), []
    if kind == "angle" and x < 180:
        out.append((f"Angle {name} is supplementary to {{prev}}.", f"angle {name}", "angle", 180 - x))
        if x < 90:
            out.append((f"Angle {name} is complementary to {{prev}}.", f"angle {name}", "angle", 90 - x))
        if (180 - x) % 2 == 0:
            out.append((f"Triangle {name} is isosceles and its vertex angle equals {{prev}}.",
                        f"each base angle of triangle {name}", "angle", (180 - x) / 2))
        if x < 90:
            out.append((f"Triangle {name} is isosceles and each of its base angles equals {{prev}}.",
                        f"the vertex angle of triangle {name}", "angle", 180 - 2 * x))
        y = rng.randint(10, 170)
        if x + y < 180:
            out.append((f"Triangle {name} has one angle equal to {{prev}} and another angle of {y} degrees.",
                        f"the third angle of triangle {name}", "angle", 180 - x - y))
            out.append((f"In triangle {name}, the two interior angles not adjacent to vertex {name.lower()} are "
                        f"{{prev}} and {y} degrees.", f"the exterior angle of triangle {name} at vertex {name.lower()}",
                        "angle", x + y))
        if x and 360 % x == 0 and 360 // x >= 3:
            out.append((f"Every exterior angle of the regular polygon {name} equals {{prev}}.",
                        f"the number of sides of polygon {name}", "count", F(360, x)))
    if kind == "count" and x >= 3:
        n = int(x)
        out.append((f"Polygon {name} is convex and has as many sides as {{prev}}.",
                    f"the sum of the interior angles of polygon {name}", "angle", 180 * (n - 2)))
        if 180 * (n - 2) % n == 0:
            out.append((f"Polygon {name} is regular and has as many sides as {{prev}}.",
                        f"each interior angle of polygon {name}", "angle", F(180 * (n - 2), n)))
        angles, rest = _angle_list(n, rng, 180 * (n - 2))
        if angles:
            out.append((f"Polygon {name} is convex, has as many sides as {{prev}}, and all but one of its interior "
                        f"angles measure {', '.join(map(str, angles))} degrees.",
                        f"the remaining interior angle of polygon {name}", "angle", rest))
        side = rng.randint(2, scale)
        out.append((f"Polygon {name} is regular, has as many sides as {{prev}}, and each side is {side} long.",
                    f"the perimeter of polygon {name}", "length", n * side))
    if kind == "length":
        out.append((f"Square {name} has side length equal to {{prev}}.", f"the perimeter of square {name}", "length", 4 * x))
        out.append((f"Square {name} has side length equal to {{prev}}.", f"the area of square {name}", "area", x * x))
        w = rng.randint(2, scale)
        out.append((f"Rectangle {name} has length equal to {{prev}} and width {w}.", f"the area of rectangle {name}", "area", x * w))
        out.append((f"Rectangle {name} has length equal to {{prev}} and width {w}.",
                    f"the perimeter of rectangle {name}", "length", 2 * (x + w)))
        out.append((f"Triangle {name} is equilateral with side length equal to {{prev}}.",
                    f"the perimeter of triangle {name}", "length", 3 * x))
        for a, b, c in TRIPLES:
            for leg, other in ((a, b), (b, a)):
                if x.denominator == 1 and x % leg == 0:
                    k = x / leg
                    out.append((f"Triangle {name} has a right angle; one leg equals {{prev}} and the other leg is "
                                f"{_fmt(other * k)}.", f"the hypotenuse of triangle {name}", "length", c * k))
                if x.denominator == 1 and x % c == 0:
                    k = x / c
                    out.append((f"Triangle {name} has a right angle; its hypotenuse equals {{prev}} and one leg is "
                                f"{_fmt(leg * k)}.", f"the other leg of triangle {name}", "length", other * k))
        out.append((f"Circle {name} has diameter equal to {{prev}}.", f"the circumference of circle {name}", "pi", x))
        out.append((f"Circle {name} has diameter equal to {{prev}}.", f"the area of circle {name}", "pi", x * x / 4))
        out.append((f"Circle {name} has diameter equal to {{prev}}.", f"the radius of circle {name}", "length", x / 2))
        out.append((f"Cube {name} has edge length equal to {{prev}}.", f"the volume of cube {name}", "volume", x ** 3))
        out.append((f"A cylinder {name} has radius equal to {{prev}} and height {w}.",
                    f"the volume of cylinder {name}", "pi", x * x * w))
    if kind == "area":
        r = sp.sqrt(sp.Rational(x.numerator, x.denominator))
        if r.is_rational:
            out.append((f"Square {name} has area equal to {{prev}}.", f"the side length of square {name}", "length",
                        F(int(r.p), int(r.q))))
        w = rng.randint(2, scale)
        if (x / w).denominator == 1:
            out.append((f"Rectangle {name} has area equal to {{prev}} and one side of length {w}.",
                        f"the other side of rectangle {name}", "length", x / w))
            out.append((f"Triangle {name} has area equal to {{prev}} and a base of length {w}.",
                        f"the height of triangle {name} on that base", "length", 2 * x / w))
        out.append((f"Box {name} has a base of area equal to {{prev}} and height {w}.", f"the volume of box {name}", "volume", x * w))
    return out


GOALS = ["angle", "count", "length", "area", "pi", "volume"]


def _short(x):
    """Token-friendly answer: below 1000, and a whole number or a half."""
    return 0 < x < 1000 and x.denominator <= 2


def _start(rng, scale):
    name = rng.choice(NAMES)
    kind = rng.choice(["angle", "angle", "count", "length", "length", "area"])
    if kind == "angle":
        x = F(rng.choice([rng.randint(10, 170), rng.choice([20, 30, 36, 40, 45, 60, 72, 90, 120])]))
        return f"Angle {name} measures {_fmt(x)} degrees.", f"angle {name}", kind, x
    if kind == "length":
        x = F(rng.randint(2, scale) * rng.choice([1, 1, 2, 3, 5]))
        return f"Segment {name} has length {_fmt(x)}.", f"the length of segment {name}", kind, x
    if kind == "area":
        x = F(rng.choice([rng.randint(2, scale) ** 2, rng.randint(2, scale) * rng.randint(2, scale)]))
        return f"Region {name} has area {_fmt(x)}.", f"the area of region {name}", kind, x
    x = F(rng.randint(3, 12))
    return f"Figure {name} has {_fmt(x)} sides.", f"the number of sides of figure {name}", kind, x


def _answer(kind, x):
    return f"{_fmt(x)}*pi" if kind == "pi" else _fmt(x)


def _parse(text):
    t = str(text).strip().lower().replace("π", "*pi").replace("^", "**").replace("°", "")
    t = t.replace("degrees", "").replace("degree", "").strip(" .*")
    t = t.split("=")[-1].strip()
    if len(t) > 60:
        return None
    try:
        return sp.sympify(t.replace("**pi", "*pi").lstrip("*"), locals={"pi": sp.pi})
    except Exception:
        return None


class GeometryMeasure(DevTask):
    summary = "Chain school geometry facts (angle sums, isosceles and exterior angles, regular polygons, Pythagoras, perimeter, area, circles, volume) to an exact measure."
    task_version = 2

    def __init__(self, config=None):
        super().__init__(config=config or GeometryMeasureConfig())

    def generate_entry(self):
        rng, c = random, self.config
        want = max(1, sround(c.steps))
        goal = rng.choice(GOALS)  # drawn before the chain, so level cannot shift what is asked
        for _ in range(5000):
            sentence, prev, kind, x = _start(rng, c.scale)
            lines, used, steps = [sentence], {prev.split()[-1]}, 0
            while steps < want and kind not in ("pi", "volume"):
                name = rng.choice([n for n in NAMES if n not in used])
                options = [o for o in _transforms(kind, x, name, rng, c.scale) if _short(F(o[3]))]
                if steps < want - 1:  # pi and volume answers end a chain: keep them for the last step
                    options = [o for o in options if o[2] not in ("pi", "volume")] or options
                if not options:
                    break
                text, new, kind, x = rng.choice(options)
                x = F(x)
                lines.append(text.format(prev=prev))
                prev, steps = new, steps + 1
                used.add(name)
            if kind == goal and (steps == want or (steps and kind in ("pi", "volume"))):
                return Entry({"facts": lines, "target": prev, "steps": steps, "kind": kind}, _answer(kind, x))
        raise RuntimeError("geometry_measure: no chain")

    def render_prompt(self, m):
        return (" ".join(m["facts"]) + f"\nWhat is {m['target']}?\n"
                "The answer is a whole number, a half such as 7/2, or k*pi when pi appears; no units.")

    def score_answer(self, answer, entry):
        got, gold = _parse(answer), _parse(entry.answer)
        if got is None or gold is None:
            return 0.0
        try:
            return float(bool(sp.simplify(got - gold) == 0))
        except Exception:
            return 0.0


