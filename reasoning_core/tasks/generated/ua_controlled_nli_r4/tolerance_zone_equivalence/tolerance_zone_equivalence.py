import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'tolerance_zone_equivalence (variant 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_controlled_nli_r4/tolerance_zone_equivalence',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2302342651,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _point_in_rect(pt, tol):
    x, y = pt
    return tol["xlo"] <= x <= tol["xlo"] + tol["w"] and tol["ylo"] <= y <= tol["ylo"] + tol["h"]


_ALL_POINTS = [
    (0, 0), (1, 0), (0, 1), (1, 1),
    (2, 0), (0, 2), (2, 1), (1, 2), (2, 2),
    (3, 0), (0, 3), (3, 1), (1, 3),
]


@dataclass
class ToleranceZoneConfig(Config):
    n_vertices: int = 1
    n_candidates: int = 3
    grid: int = 4

    def apply_difficulty(self, level):
        self.n_vertices = 1 + stochastic_rounding(level)
        self.n_candidates = 3 + stochastic_rounding(level)
        self.grid = 4 + stochastic_rounding(level)


class ToleranceZoneEquivalence(Task):
    summary = ("Compare sentences specifying datum-relative tolerance zones, movable envelopes and "
               "shared versus separate alignment; decide whether their geometric acceptance "
               "conditions admit exactly the same candidate shapes, encoded as finite sets of "
               "polygonal vertices compared via canonical vertex-membership signatures.")
    design_choice = ("Encode candidate shapes as finite sets of polygonal vertices and test "
                     "equivalence via canonical vertex-membership signatures under shared versus "
                     "separate datum alignment.")
    config_cls = ToleranceZoneConfig

    def generate_entry(self):
        cfg = self.config
        grid = cfg.grid
        n_cand = cfg.n_candidates
        n_vert = cfg.n_vertices

        target_equal = bool(random.randrange(2))

        shared = True
        t1 = None
        t2 = None
        shapes = None
        acc1 = None
        acc2 = None
        for _ in range(400):
            shared = bool(random.randrange(2))

            t1 = {"xlo": random.randrange(-grid, grid + 1),
                  "ylo": random.randrange(-grid, grid + 1),
                  "w": random.randrange(1, grid + 1),
                  "h": random.randrange(1, grid + 1)}

            shapes = []
            for _ in range(n_cand):
                base = random.choice(_ALL_POINTS)
                verts = [base]
                extra = random.sample([p for p in _ALL_POINTS if p != base],
                                      min(n_vert - 1, len(_ALL_POINTS) - 1))
                verts.extend(extra)
                random.shuffle(verts)
                shapes.append(sorted(verts))

            acc1 = [i for i, v in enumerate(shapes) if any(_point_in_rect(p, t1) for p in v)]
            if not acc1:
                continue

            if target_equal:
                chosen = None
                for _ in range(30):
                    cand = {"xlo": random.randrange(-grid, grid + 1),
                            "ylo": random.randrange(-grid, grid + 1),
                            "w": random.randrange(1, grid + 1),
                            "h": random.randrange(1, grid + 1)}
                    if cand == t1:
                        continue
                    acc_c = [i for i, v in enumerate(shapes) if any(_point_in_rect(p, cand) for p in v)]
                    if not acc_c:
                        continue
                    if acc_c == acc1:
                        chosen = cand
                        break
                t2 = chosen if chosen is not None else dict(t1)
            else:
                t2 = {"xlo": random.randrange(-grid, grid + 1),
                      "ylo": random.randrange(-grid, grid + 1),
                      "w": random.randrange(1, grid + 1),
                      "h": random.randrange(1, grid + 1)}

            acc2 = [i for i, v in enumerate(shapes) if any(_point_in_rect(p, t2) for p in v)]
            if not acc2:
                continue

            equal = (acc1 == acc2)
            if equal != target_equal:
                continue

            break
        else:
            raise RuntimeError("could not generate instance with target label")

        instance = {
            "datum_shared": shared,
            "tol1": {k: t1[k] for k in ("xlo", "ylo", "w", "h")},
            "tol2": {k: t2[k] for k in ("xlo", "ylo", "w", "h")},
            "shapes": shapes,
            "equal": equal,
        }
        ans = "equal" if equal else "not_equal"
        instance["answer"] = ans
        return Entry(metadata=instance, answer=ans)

    def render_prompt(self, metadata):
        shapes = metadata["shapes"]
        tol1 = metadata["tol1"]
        tol2 = metadata["tol2"]
        shared = metadata["datum_shared"]

        shape_desc = "".join(
            f"  Shape {i + 1}: vertices at {pts}.\n" for i, pts in enumerate(shapes)
        )
        if shared:
            zone_desc = (
                f"Both sentences align the candidate set to the same datum origin and allow the "
                f"envelope to be translated with the datum. Sentence 1 accepts a shape if at least one "
                f"of its vertices lies in the rectangle "
                f"[{tol1['xlo']},{tol1['xlo'] + tol1['w']}] x [{tol1['ylo']},{tol1['ylo'] + tol1['h']}]. "
                f"Sentence 2 accepts a shape if at least one of its vertices lies in the rectangle "
                f"[{tol2['xlo']},{tol2['xlo'] + tol2['w']}] x [{tol2['ylo']},{tol2['ylo'] + tol2['h']}]."
            )
        else:
            zone_desc = (
                f"The two sentences use separate datum alignments on the same coordinate axes; each "
                f"candidate shape keeps its displayed coordinates under both readings. Sentence 1 "
                f"accepts a shape if at least one of its vertices lies in the rectangle "
                f"[{tol1['xlo']},{tol1['xlo'] + tol1['w']}] x [{tol1['ylo']},{tol1['ylo'] + tol1['h']}]. "
                f"Sentence 2 accepts a shape if at least one of its vertices lies in the rectangle "
                f"[{tol2['xlo']},{tol2['xlo'] + tol2['w']}] x [{tol2['ylo']},{tol2['ylo'] + tol2['h']}]."
            )

        prompt = (
            f"Consider the collection of candidate shapes given in the coordinate plane, each "
            f"described by a finite set of polygonal vertices:\n{shape_desc}"
            f"The two sentences below each define an acceptance condition for whether a candidate "
            f"shape is allowed in a tolerance zone.\n{zone_desc}\n"
            f"Determine whether the two sentences' geometric acceptance conditions admit exactly "
            f"the same candidate shapes from the collection above.\n"
            f"Answer with exactly one of the two tokens: 'equal' (the acceptance conditions admit "
            f"exactly the same candidate shapes) or 'not_equal' (they differ on at least one "
            f"candidate shape)."
        )
        return prompt

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        norm = answer.strip().lower()
        gold = entry.metadata["answer"]
        return 1.0 if norm == gold else 0.0
