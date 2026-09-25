import random
from collections import defaultdict, deque
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

LETTERS = "abcdefgh"


def _comp(arr, x, y):
    return "%s(%s,%s)" % (arr, x, y)


def _deduce(relations, start, end):
    """Exact parity BFS: the set of signs (as reachable parities) linking
    `start` to `end` through the given signed equalities.

    A relation (src, dst, sign) states src == sign*dst.  Moving across it
    multiplies the accumulated sign by `sign`.  If both +1 and -1 reach the
    target endpoint, the entries are forced to zero.  This enumerates every
    path implicitly (state = (component, parity)), so it can never under- or
    over-approximate the reachable sign set.
    """
    adj = defaultdict(list)
    for src, dst, sign in relations:
        w = 0 if sign == 1 else 1
        adj[src].append((dst, w))
        adj[dst].append((src, w))
    seen = {(start, 0)}
    dq = deque([(start, 0)])
    while dq:
        node, parity = dq.popleft()
        for nxt, weight in adj.get(node, []):
            np = parity ^ weight
            if (nxt, np) not in seen:
                seen.add((nxt, np))
                dq.append((nxt, np))
    parities = {p for (node, p) in seen if node == end}
    if parities == {0}:
        return "+1"
    if parities == {1}:
        return "-1"
    if parities == {0, 1}:
        return "0"
    raise RuntimeError("target endpoint not reachable")


def _fresh(used, pool, arrays):
    while True:
        arr = random.choice(arrays)
        x = random.choice(pool)
        y = random.choice(pool)
        comp = _comp(arr, x, y)
        if comp not in used:
            used.add(comp)
            return comp


def _grab(used_ordered):
    return random.choice(used_ordered)


def _make_leg(start, end, leg_len, target_product, used, pool, arrays):
    """A chain of `leg_len` fresh intermediates with total signed product
    `target_product` from start to end, rendered as signed equalities."""
    nodes = [start]
    for _ in range(leg_len):
        nodes.append(_fresh(used, pool, arrays))
    nodes.append(end)
    signs = [random.choice((1, -1)) for _ in range(leg_len)]
    prod = 1
    for s in signs:
        prod *= s
    signs.append(target_product * prod)
    edges = []
    for a, b, s in zip(nodes, nodes[1:], signs):
        edges.append((a, b, s))
    return edges


@dataclass
class SignedSymmetryForcingConfig(Config):
    nletters: int = 3
    leg_len: int = 2
    noise_comp: int = 1
    noise_rel: int = 1

    def apply_difficulty(self, level):
        self.nletters = min(8, 3 + level)
        self.leg_len = 2 + min(level, 4)
        self.noise_comp = 1 + level // 2
        self.noise_rel = 1 + level // 2


class SignedSymmetryForcing(Task):
    summary = ("Deduce component relations from signed index symmetries across arrays and "
               "polynomial coefficients; combine swaps, cycles, and repeated indices; answer "
               "forced zero, relative sign, or independence.")
    design_choice = ("Instances present two arrays A[i,j] and B[j,i] with an explicit symmetry "
                     "rule A[i,j]=s*B[j,i] for s in {+1,-1}; solver must output forced zero if "
                     "repeated indices force both signs, else the relative sign between "
                     "symmetric components.")
    config_cls = SignedSymmetryForcingConfig
    task_version = 2

    def generate_entry(self):
        pool = list(LETTERS[: self.config.nletters])
        arrays = ("A", "B")
        a, b = pool[0], pool[1]
        start = _comp("A", a, b)
        end = _comp("A", b, a)
        arrays = ("A", "B")
        used = {start, end}
        used_ordered = [start, end]
        cls = random.choice(("+1", "-1", "0"))
        for _ in range(80):
            relations = []
            if cls in ("+1", "-1"):
                target = 1 if cls == "+1" else -1
                relations.extend(
                    _make_leg(start, end, self.config.leg_len, target, used, pool, arrays)
                )
                used_ordered.extend([c for (a_, b_, s_) in relations for c in (a_, b_)])
            else:
                relations.extend(
                    _make_leg(start, end, self.config.leg_len, 1, used, pool, arrays)
                )
                used_ordered.extend([c for (a_, b_, s_) in relations for c in (a_, b_)])
                where = len(relations)
                relations.extend(
                    _make_leg(start, end, self.config.leg_len, -1, used, pool, arrays)
                )
                used_ordered.extend([c for (a_, b_, s_) in relations[where:] for c in (a_, b_)])
            for _ in range(self.config.noise_rel):
                src = _grab(used_ordered)
                dst = _fresh(used, pool, arrays)
                used_ordered.append(dst)
                relations.append((src, dst, random.choice((1, -1))))
            answer = _deduce(relations, start, end)
            if answer == cls:
                break
        else:
            raise RuntimeError("could not build a signed symmetry instance for class %r" % cls)
        metadata = {
            "relations": relations,
            "target_start": start,
            "target_end": end,
            "nletters": self.config.nletters,
            "leg_len": self.config.leg_len,
        }
        return Entry(metadata=metadata, answer=str(answer))

    def render_prompt(self, metadata):
        lines = []
        for idx, (src, dst, sign) in enumerate(metadata["relations"], 1):
            lines.append("%d. %s = %s\u00b7%s" % (idx, src, sign, dst))
        body = "\n".join(lines)
        s = metadata["target_start"]
        e = metadata["target_end"]
        return (
            "Two arrays A and B are indexed by pairs of letters. The entries obey these signed "
            "index-symmetry relations (each \"X = s\\u00b7Y\" means the entry X equals s times "
            "the entry Y, so a step with s=-1 flips the sign):\n\n"
            + body
            + "\n\nDetermine the relation between the symmetric components "
            + s
            + " and "
            + e
            + ". Combine the relations until "
            + s
            + " is expressed in terms of "
            + e
            + ": if the composition forces "
            + s
            + " to equal both "
            + e
            + " and its negation, then both entries must vanish. Reply with one token only: "
            "a plus sign, a minus sign, or the word zero, corresponding respectively to a "
            "relative factor equal to positive one, negative one, or a forced-vanishing pair "
            "of entries."
        )

    def score_answer(self, answer, entry):
        ref = entry.answer
        candidate = str(answer).strip()
        if candidate == "+1" or candidate == "-1" or candidate == "0":
            return 1.0 if str(ref).strip() == candidate else 0.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'signed_symmetry_forcing (variant 1 of 3)',
 'hypothesis': 'P012',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_inference_modes_r4/signed_symmetry_forcing',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1277236794,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
