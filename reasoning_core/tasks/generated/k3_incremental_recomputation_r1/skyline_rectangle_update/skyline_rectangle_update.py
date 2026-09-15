import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'skyline_rectangle_update (draw 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_incremental_recomputation_r1/skyline_rectangle_update',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _skyline_rle(rects, width):
    xs = sorted({0, width} | {l for l, r, h in rects} | {r for l, r, h in rects})
    runs = []
    for i in range(len(xs) - 1):
        x1, x2 = xs[i], xs[i + 1]
        if x2 <= x1:
            continue
        h = int(max((h for l, r, h in rects if l <= x1 and x2 <= r), default=0))
        if runs and runs[-1][2] == h:
            runs[-1] = (runs[-1][0], x2, h)
        else:
            runs.append((x1, x2, h))
    return runs


def _total_area(runs):
    return sum(h * (x2 - x1) for x1, x2, h in runs)


def _diff_segments(old_runs, new_runs):
    segs = []
    i = j = 0
    while i < len(old_runs) and j < len(new_runs):
        o, n = old_runs[i], new_runs[j]
        x1 = max(o[0], n[0])
        x2 = min(o[1], n[1])
        if x2 > x1 and o[2] != n[2]:
            segs.append((x1, x2, o[2], n[2]))
        if o[1] < n[1]:
            i += 1
        elif n[1] < o[1]:
            j += 1
        else:
            i += 1
            j += 1
    return segs


def _format_answer(segments, delta):
    seg_part = ", ".join(f"{x1}-{x2} {old}->{new}" for x1, x2, old, new in segments)
    return f"{seg_part} ; {delta}"


def _parse_answer(text):
    if not isinstance(text, str):
        return None
    text = text.strip()
    if " ; " not in text:
        return None
    seg_part, _, delta_part = text.partition(" ; ")
    try:
        delta = int(delta_part.strip())
    except Exception:
        return None
    segs = []
    if seg_part.strip():
        for piece in seg_part.split(","):
            piece = piece.strip()
            arrow = piece.split("->")
            if len(arrow) != 2:
                return None
            try:
                head = arrow[0].split()
                x1s, x2s = head[0].split("-")
                old = int(head[1])
                new = int(arrow[1].strip())
                x1, x2 = int(x1s), int(x2s)
            except Exception:
                return None
            segs.append((x1, x2, old, new))
    return (tuple(segs), delta)


@dataclass
class SkylineConfig(Config):
    width: int = 10
    n_base: int = 3
    max_height: int = 4

    def apply_difficulty(self, level):
        self.width = 10 + level * 7
        self.n_base = 3 + level
        self.max_height = 4 + level


class SkylineRectangleUpdate(Task):
    summary = ("Grounded rectangle unions summarized as run-length skylines with areas; "
               "one rectangle is inserted or removed, altering only the slabs it spans; "
               "answer is the changed skyline segments and the integer area delta.")
    design_choice = ("Represent skyline as per-slab height runs; answer lists changed "
                     "(x-range, old height, new height) plus integer area delta.")
    config_cls = SkylineConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        width = cfg.width
        for _ in range(200):
            op = random.choice(["insert", "remove"])
            base_rects = []
            for _ in range(cfg.n_base):
                l = random.randrange(0, width - 1)
                r = random.randrange(l + 1, width + 1)
                if r <= l:
                    continue
                h = random.randrange(1, cfg.max_height + 1)
                base_rects.append((l, r, h))
            if not base_rects:
                continue

            if op == "remove":
                target = random.choice(base_rects)
                new_rects = [x for x in base_rects if x != target]
            else:
                while True:
                    l = random.randrange(0, width - 1)
                    r = random.randrange(l + 1, width + 1)
                    if r > l:
                        break
                h = random.randrange(1, cfg.max_height + 1)
                target = (l, r, h)
                if target in base_rects:
                    continue
                new_rects = base_rects + [target]

            base_runs = _skyline_rle(base_rects, width)
            new_runs = _skyline_rle(new_rects, width)
            segs = _diff_segments(base_runs, new_runs)
            if not segs:
                continue

            old_area = _total_area(base_runs)
            new_area = _total_area(new_runs)
            delta = int(new_area - old_area)
            if op == "insert":
                if delta <= 0:
                    continue
            else:
                if delta >= 0:
                    continue

            tl, tr, th = target
            for x1, x2, o, n in segs:
                if not (x1 >= tl and x2 <= tr):
                    raise RuntimeError("skyline changed outside the altered rectangle span")

            segs = [(int(a), int(b), int(c), int(d)) for a, b, c, d in segs]
            answer = _format_answer(segs, delta)
            metadata = {
                "width": int(width),
                "base_rects": [[int(a), int(b), int(c)] for a, b, c in base_rects],
                "base_runs": [[int(a), int(b), int(c)] for a, b, c in base_runs],
                "op": op,
                "rect": [int(target[0]), int(target[1]), int(target[2])],
                "segments": [[a, b, c, d] for a, b, c, d in segs],
                "area_delta": delta,
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("skyline_rectangle_update: failed to produce a changing instance")

    def render_prompt(self, metadata):
        runs = ", ".join(f"{a}-{b} {c}" for a, b, c in metadata["base_runs"])
        l, r, h = metadata["rect"]
        verb = "insert" if metadata["op"] == "insert" else "remove"
        return (
            f"We track the height profile of rectangles resting on the ground at y=0 over the "
            f"x-range [0,{metadata['width']}). It is given as runs \"x1-x2 h\", meaning the occupied "
            f"height is h from x1 to x2 (h=0 means empty), covering the whole range:\n"
            f"{runs}\n\n"
            f"We now {verb} the rectangle spanning x in [{l},{r}) with height {h}.\n\n"
            f"List every maximal run in the new profile whose height differs from the base profile "
            f"there, as \"x1-x2 old->new\", separated by commas, in increasing x order. After "
            f"\" ; \" write the signed integer change in total covered area (new total minus old "
            f"total).\n"
            f"Example answer: 2-4 3->1, 6-9 3->0 ; -8"
        )

    def score_answer(self, answer, entry):
        ref = _parse_answer(entry.answer)
        got = _parse_answer(answer)
        if ref is None or got is None:
            return 0.0
        return 1.0 if got == ref else 0.0
