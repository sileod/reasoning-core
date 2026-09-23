import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


TASK_META = {'parent_source_id': None,
 'idea': 'circular_digest_mapping (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_non_local_structured_r4/circular_digest_mapping',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1336314872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class CircularDigestConfig(Config):
    a: int = 2
    b: int = 2
    length: int = 90

    def apply_difficulty(self, level):
        self.a = stochastic_rounding(2 + 0.7 * level, random.randrange(2 ** 32))
        self.b = stochastic_rounding(2 + 0.7 * level, random.randrange(2 ** 32))
        self.length = stochastic_rounding(90 + 55 * level, random.randrange(2 ** 32))


def _cyclic_gaps(points, L):
    n = len(points)
    out = []
    for i in range(n):
        j = (i + 1) % n
        if j == 0:
            out.append(points[0] + L - points[i])
        else:
            out.append(points[j] - points[i])
    return out


def _candidate_gaps_for(frags, L, a, b, k, m, delta):
    cumA = [0]
    for f in frags["a"][:-1]:
        cumA.append((cumA[-1] + f) % L)
    cumB = [0]
    for f in frags["b"][:-1]:
        cumB.append((cumB[-1] + f) % L)
    arel = cumA
    brel = [(c + delta) % L for c in cumB]
    comb = sorted(arel + brel)
    if len(set(comb)) != a + b:
        return None
    return (_cyclic_gaps(comb, L), (brel[m] - arel[k]) % L)


def _build_and_verify(a, b, L, frags_presented, k, m, gold):
    n = a + b
    found_any = False
    for delta in range(L):
        res = _candidate_gaps_for(frags_presented, L, a, b, k, m, delta)
        if res is None:
            continue
        gaps, gap = res
        if gaps != frags_presented["ab"]:
            continue
        found_any = True
        if gap != gold:
            return False
    return found_any


class CircularDigestMapping(Task):
    summary = (
        "From ordered single- (A/B) and double-digest (A+B) fragment lengths of a "
        "circular molecule, place integer cut sites so every digest is explained in the "
        "fixed clockwise frame anchored at coordinate 0; answers give the clockwise "
        "gap length from a named A-cut site to a named B-cut site."
    )
    design_choice = (
        "Answers give the length of the queried gap between two specified cut sites, "
        "requiring the solver to infer the map first."
    )
    config_cls = CircularDigestConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        for _ in range(600):
            a, b = cfg.a, cfg.b
            L = cfg.length
            n = a + b
            positions = sorted(random.sample(range(L), n))
            a_idx = sorted(random.sample(range(n), a))
            aposes = [positions[i] for i in a_idx]
            bposes = sorted(
                [positions[i] for i in sorted(set(range(n)) - set(a_idx))]
            )
            if len(aposes) != a or len(bposes) != b:
                continue
            shift = aposes[0]
            arel = sorted((p - shift) % L for p in aposes)
            brel = sorted((p - shift) % L for p in bposes)
            ab_pos = sorted(arel + brel)
            a_frags = _cyclic_gaps(arel, L)
            b_frags = _cyclic_gaps(brel, L)
            ab_frags = _cyclic_gaps(ab_pos, L)
            k = random.randrange(a)
            m = random.randrange(b)
            gold = (brel[m] - arel[k]) % L
            frags = {"a": a_frags, "b": b_frags, "ab": ab_frags}
            if _build_and_verify(a, b, L, frags, k, m, gold):
                metadata = {
                    "length": int(L),
                    "a_fragments": [int(x) for x in a_frags],
                    "b_fragments": [int(x) for x in b_frags],
                    "ab_fragments": [int(x) for x in ab_frags],
                    "a_coords": [int(x) for x in arel],
                    "b_coords": [int(x) for x in brel],
                    "a_index": int(k),
                    "b_index": int(m),
                    "a_count": int(a),
                    "b_count": int(b),
                }
                return Entry(metadata=metadata, answer=str(int(gold)))
        raise RuntimeError("could not produce a uniquely resolvable digest map")

    def render_prompt(self, metadata):
        L = metadata["length"]
        a = metadata["a_fragments"]
        b = metadata["b_fragments"]
        ab = metadata["ab_fragments"]
        k = metadata["a_index"]
        m = metadata["b_index"]
        return (
            f"A circular DNA molecule has circumference {L} base pairs, with integer "
            f"coordinates on [0, {L}). Two restriction enzymes cut it at distinct sites.\n"
            f"- Enzyme A cuts at {metadata['a_count']} sites. Going clockwise from the "
            f"A-cut site at coordinate 0, successive A-cut sites are separated by "
            f"fragments: {a} (in clockwise order). A-fragment i runs clockwise from "
            f"A-cut site Ai to A-cut site A(i+1).\n"
            f"- Enzyme B cuts at {metadata['b_count']} sites. Going clockwise from the "
            f"B-cut site B0, successive B-cut sites are separated by fragments: {b} "
            f"(clockwise order; the coordinate of B0 is to be determined). B-fragment i "
            f"runs clockwise from B-cut site Bi to B-cut site B(i+1).\n"
            f"- Cutting with both enzymes, going clockwise from the cut site at "
            f"coordinate 0 (which is an A-cut), the combined fragments are: {ab}.\n"
            f"Infer the map. Give the clockwise distance (an integer number of base "
            f"pairs) from cut site A{k} to cut site B{m}."
        )
