import random

import numpy as np

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'affine_view_aliasing (variant 2 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_logic_r4/affine_view_aliasing',
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

design_choice = "Answer as an integer count of overlapping element positions between two strided views, with disjoint yielding 0"


def product(vals):
    p = 1
    for v in vals:
        p *= v
    return p


def _overlap_count(lengths, st1, st2, start1, start2):
    """Count distinct flat storage addresses present in both strided views.

    For each index tuple, view k maps to flat address start_k + sum_i idx_i*st_k[i].
    Count the number of distinct addresses that appear in both views' element sets.
    """
    set1 = set()
    set2 = set()
    for idx in np.ndindex(*lengths):
        off1 = 0
        off2 = 0
        for i in range(len(lengths)):
            off1 += idx[i] * st1[i]
            off2 += idx[i] * st2[i]
        set1.add(start1 + off1)
        set2.add(start2 + off2)
    return len(set1 & set2)


class AffineViewAliasingConfig(Config):
    len_low: int = 2
    len_high: int = 4
    max_stride: int = 3
    n_levels: int = 1
    delta_scale: int = 4
    max_product: int = 24

    def apply_difficulty(self, level):
        self.len_low = 2
        self.len_high = 4
        self.max_stride = min(3, 2 + level // 2)
        self.n_levels = min(1 + level // 2, 2)
        self.delta_scale = 2 + level
        self.max_product = 24


class AffineViewAliasing(Task):
    summary = ("Compose slicing, transposition, reversal, and broadcasting over strided array "
               "views; determine whether selected views share storage and return a shared "
               "address, overlap count, or disjointness.")
    config_cls = AffineViewAliasingConfig
    task_version = 2

    def generate_entry(self):
        while True:
            n = random.randint(1, self.config.n_levels + 1)
            lengths = [random.randint(self.config.len_low, self.config.len_high) for _ in range(n)]
            if product(lengths) > self.config.max_product:
                continue
            rows = product(lengths)

            mode = random.choice(["slice", "transpose", "reverse", "broadcast", "slice"])

            st1 = [random.randint(1, self.config.max_stride) for _ in range(n)]
            if mode == "transpose":
                perm = list(range(n))
                random.shuffle(perm)
                st2 = [st1[p] for p in perm]
            elif mode == "reverse":
                st2 = [-v for v in st1]
            elif mode == "broadcast":
                d = random.randint(1, n)
                st2 = [0] * d + list(st1[d:])
            else:
                st2 = [random.randint(1, self.config.max_stride) for _ in range(n)]

            start1 = random.randint(0, 8)
            delta = random.randint(-self.config.delta_scale, self.config.delta_scale)
            start2 = start1 + delta

            count = _overlap_count(lengths, st1, st2, start1, start2)
            if not (0 <= count <= rows):
                continue

            metadata = {
                "n": n,
                "lengths": [int(v) for v in lengths],
                "rows": int(rows),
                "mode": mode,
                "start1": int(start1),
                "start2": int(start2),
                "st1": [int(v) for v in st1],
                "st2": [int(v) for v in st2],
                "count": int(count),
            }
            return Entry(metadata=metadata, answer=str(count))

    def render_prompt(self, metadata):
        n = metadata["n"]
        lengths = metadata["lengths"]
        idxs = [f"i{i}" for i in range(n)]

        def formula(start, st):
            terms = []
            for i in range(n):
                if st[i] == 1:
                    terms.append(idxs[i])
                elif st[i] == -1:
                    terms.append(f"-{idxs[i]}")
                else:
                    terms.append(f"{st[i]}*{idxs[i]}")
            body = " + ".join(terms)
            return f"{start} + {body}"

        mode_desc = {
            "slice": f"View2 has an independently chosen stride vector ({', '.join(map(str, metadata['st2']))})",
            "transpose": f"View2 is a transposition of view1, so its stride vector ({', '.join(map(str, metadata['st2']))}) is a permutation of view1's",
            "reverse": f"View2 is view1 reversed along every axis, so its stride vector ({', '.join(map(str, metadata['st2']))}) is the elementwise negation of view1's",
            "broadcast": f"View2 broadcasts its leading axes, so an initial block of its stride vector ({', '.join(map(str, metadata['st2']))}) is 0",
        }

        i_spec = ", ".join(idxs)
        shape_txt = ", ".join(map(str, lengths))
        f1 = formula(metadata["start1"], metadata["st1"])
        f2 = formula(metadata["start2"], metadata["st2"])
        return (
            f"In a numerical library everything is a strided view over a flat buffer. A buffer holds an "
            f"implicitly indexed group of elements; here that group has shape ({shape_txt}), which we write "
            f"with index tuple ({i_spec}). Two views both span this whole shape. View1 is anchored at flat "
            f"address {metadata['start1']} and maps each index tuple to {f1}. {mode_desc[metadata['mode']]}; "
            f"view2 is anchored at flat address {metadata['start2']} and maps each tuple to {f2}. An element "
            f"is said to be aliased when the same flat address can arise from both views. Count the number "
            f"of distinct flat addresses that belong to both view1's and view2's sets of produced addresses. "
            f"Two views that share no flat address produce a count of zero. Give that integer count as the answer."
        )

    def score_answer(self, answer, entry):
        try:
            val = int(str(answer).strip())
        except (ValueError, TypeError):
            return 0.0
        if val < 0:
            return 0.0
        return 1.0 if val == int(entry.metadata["count"]) else 0.0
