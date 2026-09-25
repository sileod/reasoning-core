import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _upper_hull(points):
    """Concave upper hull: vertices of the envelope, slopes strictly decreasing."""
    hull = []
    for (x, y) in sorted(points):
        while len(hull) >= 2:
            x0, y0 = hull[-2]
            x1, y1 = hull[-1]
            s01 = (y1 - y0) / (x1 - x0)
            s12 = (y - y1) / (x - x1)
            if s12 >= s01:
                hull.pop()
            else:
                break
        hull.append((x, y))
    return hull


def _parse_coeff(s):
    s = s.strip()
    if not (s.startswith("[") and s.endswith("]")):
        return None
    inner = s[1:-1].strip()
    if not inner:
        return None
    parts = inner.split(",")
    try:
        vals = [int(p.strip()) for p in parts]
    except ValueError:
        return None
    return vals


def _parse_corner(s):
    s = s.strip()
    if ";" not in s:
        return None
    vert_part, bp_part = s.split(";", 1)
    vertices = []
    for tok in vert_part.split(","):
        tok = tok.strip()
        if ":" not in tok:
            return None
        i_s, c_s = tok.split(":", 1)
        try:
            vertices.append((int(i_s), int(c_s)))
        except ValueError:
            return None
    if "bp:" not in bp_part:
        return None
    bp_s = bp_part.split("bp:", 1)[1]
    bps = []
    for tok in bp_s.split(","):
        tok = tok.strip()
        if not tok:
            return None
        try:
            bps.append(int(tok))
        except ValueError:
            return None
    if len(bps) != len(vertices) - 1:
        return None
    return vertices, bps


def _format_corner(vertices, bps):
    vert = ",".join(f"{i}:{c}" for (i, c) in vertices)
    bp = ",".join(str(b) for b in bps)
    return f"{vert};bp:{bp}"


def _format_coeff(vals):
    return "[" + ",".join(str(v) for v in vals) + "]"


@dataclass
class TropicalConfig(Config):
    min_degree: int = 3
    max_degree: int = 5
    min_hull: int = 2
    max_hull: int = 3
    slope_range: int = 3
    base_range: int = 6
    p_strict: float = 0.5
    below_range: int = 2

    def apply_difficulty(self, level):
        self.min_degree = 3 + level
        self.max_degree = 5 + 2 * level
        self.min_hull = 2
        self.max_hull = min(self.max_degree + 1, 2 + level // 2)
        self.slope_range = 3 + level
        self.base_range = 6 + 2 * level
        self.p_strict = 0.5
        self.below_range = 1 + level


class TropicalCornerTransfer(Task):
    summary = ("Translate univariate min-plus polynomials between coefficient lists and "
               "weighted breakpoint descriptions, accounting for inactive terms and affine "
               "offsets; recover a corner, slope or normalized coefficient.")
    design_choice = ("Instances present the polynomial in either coefficient-list or "
                     "breakpoint form, and the solver must output the equivalent representation "
                     "as a canonical string.")
    config_cls = TropicalConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        for _ in range(800):
            n = random.randint(cfg.min_degree, cfg.max_degree)
            target = random.randint(cfg.min_hull, min(cfg.max_hull, n + 1))
            interiors = n - 1
            if target - 2 > interiors:
                continue
            if target - 2 > 0:
                interior = sorted(random.sample(range(1, n), target - 2))
            else:
                interior = []
            active = [0] + interior + [n]
            if len(set(active)) != target or len(active) < 2:
                continue
            ns = target - 1
            slope_lo = -cfg.slope_range
            slope_hi = cfg.slope_range
            if slope_hi - slope_lo + 1 < ns:
                continue
            s = sorted(random.sample(range(slope_lo, slope_hi + 1), ns), reverse=True)
            cbase = random.randint(-cfg.base_range, cfg.base_range)
            c_at = {active[0]: cbase}
            for k in range(ns):
                c_at[active[k + 1]] = c_at[active[k]] + s[k] * (active[k + 1] - active[k])

            on_seg = {}
            for j in range(n + 1):
                if j in c_at:
                    on_seg[j] = c_at[j]
                    continue
                k = 0
                while not (active[k] < j < active[k + 1]):
                    k += 1
                on_seg[j] = c_at[active[k]] + s[k] * (j - active[k])

            coeff = {}
            for j in range(n + 1):
                if j in c_at:
                    coeff[j] = c_at[j]
                elif random.random() < cfg.p_strict:
                    coeff[j] = on_seg[j] - random.randint(0, cfg.below_range)
                else:
                    coeff[j] = on_seg[j]

            verts = _upper_hull([(i, coeff[i]) for i in range(n + 1)])
            got_active = [i for (i, c) in verts]
            if got_active != active:
                continue
            bps = [-s[k] for k in range(ns)]
            if any(bps[k] >= bps[k + 1] for k in range(ns - 1)):
                continue
            if any(active[k + 1] - active[k] <= 0 for k in range(ns)):
                continue

            coeff_list = [coeff[i] for i in range(n + 1)]
            corner = _format_corner(list(zip(active, [c_at[i] for i in active])), bps)

            if random.random() < 0.5:
                direction = 0
                input_form = _format_coeff(coeff_list)
                answer = corner
            else:
                direction = 1
                input_form = corner
                on_list = [on_seg[i] for i in range(n + 1)]
                answer = _format_coeff(on_list)

            to_check = coeff_list if direction == 0 else [on_seg[i] for i in range(n + 1)]
            chull = _upper_hull([(i, to_check[i]) for i in range(n + 1)])
            if [i for (i, c) in chull] != active:
                continue

            metadata = {
                "n": n,
                "direction": direction,
                "input_form": input_form,
                "active": active,
                "coeff_list": coeff_list,
                "onseg_list": [on_seg[i] for i in range(n + 1)],
                "corner": corner,
                "answer": answer,
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("tropical_corner_transfer: failed to generate an admissible example")

    def render_prompt(self, metadata):
        n_form = (
            "f(x)=min over i of (c_i + i*x) for degrees i=0..n"
        )
        if metadata["direction"] == 0:
            given = metadata["input_form"]
            return (
                f"A univariate min-plus (tropical) polynomial is {n_form}. It is given in "
                f"coefficient-list form, listing c_0,c_1,...,c_n in order, some terms possibly "
                f"inactive (never touching the lower envelope): {given}. "
                f"Output its equivalent breakpoint (corner) form as a single canonical string. "
                f"Give the active terms as comma-separated 'degree:coefficient' pairs in order of "
                f"increasing degree, then a semicolon, then 'bp:' followed by the comma-separated "
                f"breakpoints between consecutive active terms, where the breakpoint between "
                f"active degrees a and b of coefficients c_a and c_b is (c_a-c_b)/(b-a). Only "
                f"terms that are true corners (vertices of the concave lower envelope) belong in "
                f"the active list; on-hull and below-hull terms are omitted. Example: the "
                f"coefficient list [0,1,2,1,0] has active terms 0:0,2:2,4:0 with breakpoints "
                f"-1,1, so the answer is 0:0,2:2,4:0;bp:-1,1."
            )
        else:
            given = metadata["input_form"]
            n_d = metadata["n"]
            return (
                f"A univariate min-plus (tropical) polynomial with degrees 0..{n_d} is "
                f"f(x)=min over i of (c_i + i*x). It is given in breakpoint (corner) form as "
                f"comma-separated 'degree:coefficient' active terms followed by ';bp:' and the "
                f"comma-separated breakpoints between consecutive active terms: {given}. The "
                f"coefficient list is concave with these corners; every non-corner degree j has "
                f"coefficient c_j lying on the straight segment between its two neighboring "
                f"corners (equal to c_a + s*(j-a) where the slope between neighboring corners a,b "
                f"is s=(c_b-c_a)/(b-a), equivalently s=-bp). Output the full equivalent "
                f"coefficient list c_0,c_1,...,c_{n_d} as a single canonical string, a "
                f"bracket-enclosed comma-separated list. Example: corners 0:0,2:2,4:0 with "
                f"breakpoints -1,1 for degrees 0..4 give the answer [0,1,2,1,0]."
            )

    def score_answer(self, answer, entry):
        direction = entry.metadata["direction"]
        if direction == 0:
            got = _parse_corner(str(answer))
            if got is None:
                return 0.0
            ref = _parse_corner(entry.metadata["corner"])
            return 1.0 if got == ref else 0.0
        else:
            got = _parse_coeff(str(answer))
            if got is None:
                return 0.0
            ref = entry.metadata["onseg_list"]
            return 1.0 if got == ref else 0.0

    def distractor_candidates(self, entry):
        direction = entry.metadata["direction"]
        cands = set()
        if direction == 0:
            vertices = [tuple(p) for p in _parse_corner(entry.metadata["corner"])[0]]
            bps = list(_parse_corner(entry.metadata["corner"])[1])
            if len(bps) >= 2:
                shifted = bps[:1] + [bps[0]] + bps[2:]
                cands.add(_format_corner(vertices, shifted))
            if len(vertices) >= 2:
                cands.add(_format_corner(vertices[:1] + vertices[1:-1], bps))
            full = _parse_corner(entry.metadata["corner"])[0]
            cands.add(_format_corner(full[1:], bps))
        else:
            onlist = entry.metadata["onseg_list"]
            n = len(onlist) - 1
            bad = list(onlist)
            bad[n] = bad[n] + 1
            cands.add(_format_coeff(bad))
            rev = list(reversed(onlist))
            cands.add(_format_coeff(rev))
        return list(cands)


TASK_META = {'parent_source_id': None,
 'idea': 'tropical_corner_transfer (variant 2 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_representation_specific_r4/tropical_corner_transfer',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1705404348,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
