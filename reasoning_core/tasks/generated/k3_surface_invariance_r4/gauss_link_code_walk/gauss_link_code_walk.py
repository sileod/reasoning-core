import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class GaussLinkConfig(Config):
    n_cross_low: int = 3
    n_cross_high: int = 5

    def apply_difficulty(self, level):
        self.n_cross_low = max(2, 2 + level)
        self.n_cross_high = min(12, 5 + 2 * level)


def _decompose(code):
    """Trace a signed Gauss code into components in order of first appearance.

    code: list of (crossing_id, sign) with each crossing_id appearing exactly
    twice. Returns the per-component writhe list (writhe of a component is the
    sum of signs of crossings whose two occurrences both lie on that component),
    ordered by the first code position each component occupies.
    """
    n = len(code)
    occ = {}
    for i, (cid, _sgn) in enumerate(code):
        occ.setdefault(cid, []).append(i)
    other = [None] * n
    for cid, idxs in occ.items():
        other[idxs[0]] = idxs[1]
        other[idxs[1]] = idxs[0]

    visited = [False] * n
    writhes = []
    for start in range(n):
        if visited[start]:
            continue
        comp = set()
        cur = start
        while not visited[cur]:
            visited[cur] = True
            comp.add(cur)
            swapped = other[cur]
            if not visited[swapped]:
                visited[swapped] = True
                comp.add(swapped)
            cur = (swapped + 1) % n
        w = 0
        for cid, idxs in occ.items():
            if idxs[0] in comp and idxs[1] in comp:
                w += code[idxs[0]][1]
        writhes.append(w)
    return writhes


def _build_code(n_cross):
    """Build a valid signed Gauss code on crossings 0..n_cross-1.

    Returns (code, writhes, ids_ordered) or None if construction fails.
    Each crossing_id appears exactly twice; a sign (+1/-1) is attached to each.
    Crossings are relabeled along participant order for a compact prompt.
    """
    for _attempt in range(200):
        crossings = [cid for cid in range(n_cross)]
        random.shuffle(crossings)
        code_labels = crossings + crossings
        random.shuffle(code_labels)
        if any(code_labels[i] == code_labels[(i + 1) % (2 * n_cross)]
               for i in range(2 * n_cross)):
            continue
        signs = {}
        for cid in range(n_cross):
            signs[cid] = 1 if random.random() < 0.5 else -1
        code = [(cid, signs[cid]) for cid in code_labels]

        writhes = _decompose(code)
        if len(writhes) < 1:
            continue
        if all(w == 0 for w in writhes):
            continue
        if len(writhes) == 1 and n_cross < 5 and len(set(signs.values())) < 2:
            continue
        first_pos = {}
        seen = set()
        for i, (cid, _s) in enumerate(code):
            if cid in seen:
                first_pos[cid] = i
            else:
                seen.add(cid)
        ids_ordered = []
        seen2 = set()
        for cid, _s in code:
            if cid not in seen2:
                seen2.add(cid)
                ids_ordered.append(cid)
        return code, writhes, ids_ordered
    return None


def _format_gauss(code, ids_ordered):
    """Render the signed Gauss code with compact crossing labels in occurrence order."""
    rank = {cid: i for i, cid in enumerate(ids_ordered)}
    tokens = []
    for cid, sgn in code:
        label = chr(ord('A') + rank[cid])
        tokens.append(("+" if sgn > 0 else "-") + label)
    return " ".join(tokens)


TASK_META = {'parent_source_id': None,
 'idea': 'gauss_link_code_walk (variant 2 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_surface_invariance_r4/gauss_link_code_walk',
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


class GaussLinkCodeWalk(Task):
    summary = "Trace signed Gauss/DT codes of knot and link diagrams: follow the strand order to recover components, fix crossing signs, and compute per-component writhe as a comma-separated list of signed integers ordered by first appearance, across single- and multi-component diagrams with mixed over/under crossings."
    design_choice = "Generate diagrams with mixed over/under crossings and require answers as a single comma-separated list of writhe per component, ordered by first appearance."
    config_cls = GaussLinkConfig
    task_version = 2

    def generate_entry(self):
        low = max(2, self.config.n_cross_low)
        high = max(low, self.config.n_cross_high)
        n_cross = random.randint(low, high)
        built = _build_code(n_cross)
        for _ in range(20):
            if built is not None:
                break
            n_cross = random.randint(low, high)
            built = _build_code(n_cross)
        if built is None:
            raise RuntimeError("could not build a valid signed Gauss code")
        code, writhes, ids_ordered = built

        verify = _decompose(code)
        if verify != writhes:
            built = _build_code(n_cross)
            if built is None:
                raise RuntimeError("invalid signed Gauss code")
            code, writhes, ids_ordered = built
            verify = _decompose(code)
            if verify != writhes:
                raise RuntimeError("invalid signed Gauss code after retry")

        gauss = _format_gauss(code, ids_ordered)
        answer = ",".join(str(w) for w in writhes)
        metadata = {
            "gauss": gauss,
            "crossings": [[cid, sgn] for cid, sgn in code],
            "component_writhes": list(writhes),
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        gauss = metadata["gauss"]
        return (
            "Here is the signed Gauss code of an oriented link diagram: "
            f"{gauss}. "
            "In it each letter names a crossing and appears exactly twice; the sign "
            "attached to a letter is that crossing's sign. Trace the code, splitting "
            "it into its components in order of first appearance along the sequence "
            "(the component containing the first symbol comes first). For each "
            "component its writhe is the sum of the signs of crossings whose two "
            "occurrences both lie on that component (crossings shared between two "
            "components do not count toward either). Give the writhe of each "
            "component as a comma-separated list of signed integers, in "
            "first-appearance order. Example format: 2,-1,0."
        )

    def score_answer(self, answer, entry):
        return _score_answer(answer, entry)


def _parse_writhes(text):
    text = (text or "").strip()
    if not text:
        return None
    try:
        parts = [p.strip() for p in text.split(",")]
        vals = [int(p) for p in parts if p != ""]
    except Exception:
        return None
    if not vals or len(vals) != len(parts):
        return None
    return vals


def _score_answer(answer, entry):
    gold = _parse_writhes(entry["answer"])
    ans = _parse_writhes(answer) if isinstance(answer, str) else None
    if ans is None or gold is None:
        return 0.0
    return 1.0 if ans == gold else 0.0
