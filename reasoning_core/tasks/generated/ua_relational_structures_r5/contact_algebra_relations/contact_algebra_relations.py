import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'contact_algebra_relations (variant 2 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_relational_structures_r5/contact_algebra_relations',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1211525277,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

LABELS = ["disjoint", "touching", "overlap", "contains", "tangential_contain"]


def _overlap2(a, b):
    ox = min(a[2], b[2]) - max(a[0], b[0])
    oy = min(a[3], b[3]) - max(a[1], b[1])
    return ox, oy


def _positive_overlap(a, b):
    ox, oy = _overlap2(a, b)
    return ox > 0 and oy > 0


def _touch(a, b):
    ox, oy = _overlap2(a, b)
    return (ox >= 0 and oy >= 0) and not (ox > 0 and oy > 0)


def _boundary_share(a, b):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    oy = min(ay1, by1) - max(ay0, by0)
    ox = min(ax1, bx1) - max(ax0, bx0)
    if oy >= 0 and (ax0 == bx0 or ax0 == bx1 or ax1 == bx0 or ax1 == bx1):
        return True
    if ox >= 0 and (ay0 == by0 or ay0 == by1 or ay1 == by0 or ay1 == by1):
        return True
    return False


def _rect_minus(r, s):
    x0, y0, x1, y1 = r
    sx0, sy0, sx1, sy1 = s
    ox0 = max(x0, sx0)
    oy0 = max(y0, sy0)
    ox1 = min(x1, sx1)
    oy1 = min(y1, sy1)
    if ox1 <= ox0 or oy1 <= oy0:
        return [r]
    out = []
    if x0 < ox0:
        out.append((x0, y0, ox0, y1))
    if ox1 < x1:
        out.append((ox1, y0, x1, y1))
    if y0 < oy0:
        out.append((ox0, y0, ox1, oy0))
    if oy1 < y1:
        out.append((ox0, oy1, ox1, y1))
    return [q for q in out if q[0] < q[2] and q[1] < q[3]]


def _rectlist_sub(part, sub):
    out = []
    for r in part:
        stack = [r]
        for s in sub:
            nxt = []
            for rr in stack:
                nxt.extend(_rect_minus(rr, s))
            stack = nxt
        out.extend(stack)
    return out


def _any_positive(A, B):
    for a in A:
        for b in B:
            if _positive_overlap(a, b):
                return True
    return False


def _any_touch(A, B):
    for a in A:
        for b in B:
            if _touch(a, b):
                return True
    return False


def _any_boundary_share(A, B):
    for a in A:
        for b in B:
            if _boundary_share(a, b):
                return True
    return False


def _dedup(rects):
    seen = set()
    out = []
    for r in rects:
        if r[0] < r[2] and r[1] < r[3] and r not in seen:
            seen.add(r)
            out.append(r)
    return out


def classify(A, B):
    A = _dedup(A)
    B = _dedup(B)
    A_mB = _rectlist_sub(A, B)
    B_mA = _rectlist_sub(B, A)
    if not A_mB and not B_mA:
        return "equal"
    if _any_positive(A, B):
        if not B_mA and A_mB:
            return "tangential_contain" if _any_boundary_share(A, B) else "contains"
        if not A_mB and B_mA:
            return "contained_by"
        return "overlap"
    return "touching" if _any_touch(A, B) else "disjoint"


def _holes_in(main, n_holes, S):
    mx0, my0, mx1, my1 = main
    holes = []
    attempts = 0
    while len(holes) < n_holes and attempts < 300:
        attempts += 1
        w = random.randint(max(1, S // 6), max(1, S // 3))
        h = random.randint(max(1, S // 6), max(1, S // 3))
        x = random.randint(mx0 + 1, max(mx0 + 1, mx1 - w - 1))
        y = random.randint(my0 + 1, max(my0 + 1, my1 - h - 1))
        r = (x, y, x + w, y + h)
        if r[2] >= mx1 or r[3] >= my1:
            continue
        if any(_positive_overlap(r, q) for q in holes):
            continue
        holes.append(r)
    return holes


def _block_r(main, S, margin):
    mx0, my0, mx1, my1 = main
    w = random.randint(max(1, S // 4), max(1, S // 2))
    h = random.randint(max(1, S // 4), max(1, S // 2))
    x = random.randint(mx0, max(mx0, mx1 - w))
    y = random.randint(my0, max(my0, my1 - h))
    return (x, y, x + w, y + h)


def _build(cfg, label):
    S = cfg.spread
    mid = S // 2
    n_a = cfg.n_a
    n_b = cfg.n_b
    n_h = cfg.n_holes

    if label in ("contains", "tangential_contain"):
        main = (0, 0, S, S)
        holes = _holes_in(main, min(n_h, 3), S)
        A = _rectlist_sub([main], holes)
        B = _sample_b_inside(S, holes, touch_left=(label == "tangential_contain"))
        return _dedup(A), _dedup(B)
    else:
        A = _build_left(n_a, n_h, S, mid)
        if label == "disjoint":
            g = max(2, S // 6)
            B = _sample_band(mid + g, S, S, n_b)
        elif label == "touching":
            B = _sample_band_touch(mid, S, n_b)
        else:  # overlap
            inset = max(2, mid // 3)
            B = _sample_band(mid - inset, S, S, n_b)
        return _dedup(A), _dedup(B)


def _build_left(n_a, n_h, S, mid):
    blocks = []
    attempts = 0
    while len(blocks) < n_a and attempts < 300:
        attempts += 1
        b = _block_r((0, 0, mid, S), S, 0)
        if any(_positive_overlap(b, q) for q in blocks):
            continue
        blocks.append(b)
    out = []
    for b in blocks:
        holes = _holes_in(b, min(n_h, 3), S)
        out.extend(_rectlist_sub([b], holes))
    return out


def _sample_band(x0, x1, S, n):
    out = []
    attempts = 0
    while len(out) < n and attempts < 400:
        attempts += 1
        w = random.randint(max(1, S // 8), max(1, S // 3))
        h = random.randint(max(1, S // 8), max(1, S // 3))
        x = random.randint(x0, max(x0, x1 - w))
        y = random.randint(0, max(0, S - h))
        if x + w > x1:
            continue
        r = (x, y, x + w, y + h)
        if any(_positive_overlap(r, q) for q in out):
            continue
        out.append(r)
    return out


def _sample_band_touch(mid, S, n):
    out = []
    attempts = 0
    while len(out) < n and attempts < 400:
        attempts += 1
        w = random.randint(max(1, S // 8), max(1, S // 3))
        h = random.randint(max(1, S // 8), max(1, S // 3))
        y = random.randint(0, max(0, S - h))
        r = (mid, y, mid + w, y + h)
        if any(_positive_overlap(r, q) for q in out):
            continue
        out.append(r)
    return out


def _sample_b_inside(S, holes, touch_left):
    margin = max(1, S // 10)
    w = random.randint(margin, max(margin, S // 2))
    h = random.randint(margin, max(margin, S // 2))
    x0 = 0 if touch_left else random.randint(1, max(1, S - w - 1))
    if touch_left:
        x0 = 0
    else:
        x0 = random.randint(1, max(1, S - w - 1))
    y0 = random.randint(1, max(1, S - h - 1))
    r = (x0, y0, min(S, x0 + w), y0 + h)
    return [r]


@dataclass
class ContactAlgebraConfig(Config):
    n_a: int = 1
    n_b: int = 1
    n_holes: int = 0
    spread: int = 8

    def apply_difficulty(self, level):
        self.n_a = max(1, 1 + level)
        self.n_b = max(1, 1 + level)
        self.n_holes = max(0, level - 1)
        self.spread = 8 + 4 * level


class ContactAlgebraRelations(Task):
    summary = ("Evaluate contact, overlap, inclusion, and tangential containment between "
               "regions built by regularized Boolean operations on finite cell complexes of "
               "axis-aligned rectangles; return the queried qualitative relation from a fixed "
               "five-label set.")
    design_choice = ("Build instances from parametric shapes (e.g., polygons, ellipses, or spline "
                     "patches) and ask for the relation using a fixed label set, ensuring spatial "
                     "configurations vary across difficulty levels")
    config_cls = ContactAlgebraConfig

    def generate_entry(self):
        for _ in range(120):
            label = random.choice(LABELS)
            A, B = _build(self.config, label)
            rel = classify(A, B)
            if rel == label:
                metadata = {
                    "region_A": A,
                    "region_B": B,
                    "labels": LABELS,
                    "relation": label,
                }
                return Entry(metadata=metadata, answer=label)
        raise RuntimeError("contact_algebra_relations: could not realize label")

    def render_prompt(self, metadata):
        labels = ", ".join(metadata["labels"])
        prompt = (
            "Region A is the union of the closed axis-aligned rectangles "
            + _render_rects(metadata["region_A"])
            + ". Region B is the union of the closed axis-aligned rectangles "
            + _render_rects(metadata["region_B"])
            + '. A "region" is its entire closed point set, boundaries included. '
            + "Determine the qualitative relation between region A and region B. "
            + 'Choose exactly one of: ' + labels + '. '
            + "Here 'contains' means region A entirely contains region B (B's interior is inside "
            + "A and the two boundaries do not meet); 'tangential_contain' means region A "
            + "contains region B and their boundaries touch; 'touching' means their interiors are "
            + "disjoint but the regions make contact along a shared boundary; 'overlap' means the "
            + "regions share positive area yet neither contains the other. "
            + "The answer is a single word from that list."
        )
        return prompt

    def score_answer(self, answer, entry):
        return 1.0 if str(answer).strip() == str(entry["answer"]).strip() else 0.0


def _render_rects(rects):
    parts = []
    for (x0, y0, x1, y1) in rects:
        parts.append(f"({x0},{y0})-({x1},{y1})")
    return "[" + ", ".join(parts) + "]"
