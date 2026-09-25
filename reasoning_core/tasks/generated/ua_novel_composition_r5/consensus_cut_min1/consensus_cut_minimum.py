import random

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'consensus_cut_minimum (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_novel_composition_r5/consensus_cut_minimum',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

DESIGN_CHOICE = ("Represent each valuation as a sequence of adjacent integer intervals with "
                 "per-interval sign and weight, and compute the minimum number of boundary cuts "
                 "that satisfy all signed sums.")


class ConfigCut(Config):
    n: int = 8
    nval: int = 2

    def apply_difficulty(self, level):
        self.n = stochastic_rounding(min(6 + level * 2, 15))
        self.nval = stochastic_rounding(min(2 + level, 5))


def compute_min_cuts(ncells, segments):
    """Brute-force the minimum number of cuts.

    Cells are unit positions 0..ncells-1 on a line [0, ncells].  The sign
    pattern is piecewise constant: it starts + at position 0 and toggles at
    every cut.  A segment (s,e,w) contributes +w on each of its cells covered
    by a + piece and -w on cells covered by a - piece; its signed total must
    be 0.  Return the minimum number of internal cuts making all signed
    totals zero, or None if impossible.

    Only cuts strictly inside the union of all segments can ever matter: a cut
    outside every segment adds to the count without changing any constraint.
    """
    candidates = sorted({k for (s, e, _w) in segments for k in range(s + 1, e)})
    if not candidates:
        return None

    best = None
    n = len(candidates)
    for mask in range(1 << n):
        cuts = [candidates[i] for i in range(n) if (mask >> i) & 1]
        cnt = len(cuts)
        if best is not None and cnt >= best:
            continue
        boundaries = [0] + cuts + [ncells]
        pieces = [(boundaries[i], boundaries[i + 1]) for i in range(len(boundaries) - 1)]
        sign_of_piece = [1 if i % 2 == 0 else -1 for i in range(len(pieces))]

        def sign_at(cell):
            for i, (a, b) in enumerate(pieces):
                if a <= cell < b:
                    return sign_of_piece[i]
            return None

        good = True
        for (s, e, w) in segments:
            t = 0
            for c in range(s, e):
                sg = sign_at(c)
                if sg is None:
                    good = False
                    break
                t += w * sg
            if not good:
                break
            if t != 0:
                good = False
                break
        if good:
            best = cnt
    return best


class ConsensusCutMin1(Task):
    summary = ("Split a line into alternating signs so each piecewise-constant valuation has its "
               "prescribed signed total; vary overlapping supports, target imbalances, and fixed "
               "endpoint signs; answer the fewest cuts or impossibility.")
    design_choice = DESIGN_CHOICE
    config_cls = ConfigCut

    def generate_entry(self):
        ncell = self.config.n
        nval = self.config.nval
        found = {}
        for _ in range(90):
            segments = []
            for _j in range(nval):
                s = random.randint(0, ncell - 2)
                e = random.randint(s + 1, ncell)
                if (e - s) % 2 == 1:
                    if e - 1 > s:
                        e = e - 1
                if (e - s) == 0:
                    if s > 0:
                        s = s - 1
                        e = e + 1
                if e - s >= 2 and (e - s) % 2 == 0:
                    w = random.randint(1, 4)
                    segments.append((s, e, w))
            if len(segments) < 2:
                continue
            ans = compute_min_cuts(ncell, segments)
            if ans is None or ans < 1:
                continue
            if ans not in found:
                found[ans] = segments
        if not found:
            raise RuntimeError("could not build a satisfiable instance")
        target = random.choice(sorted(found))
        segments = found[target]
        metadata = {
            "n": int(ncell),
            "segments": [(int(s), int(e), int(w)) for (s, e, w) in segments],
        }
        return Entry(metadata=metadata, answer=str(target))

    def render_prompt(self, metadata):
        n = metadata["n"]
        lines = [
            "Along the integer line from position 0 to position {} the valuation sign is ".format(n)
            + "constant between cuts and toggles (+ then - then +, ...) at every cut. "
            + "The sign to the left of position 0 is +.",
            "There are valuations, each an interval [s, e) of adjacent cells with a shared weight w:",
        ]
        for (s, e, w) in metadata["segments"]:
            lines.append("  [%d, %d) weight %d: each of its cells contributes +%d if covered by a 'plus' run and -%d if covered by a 'minus' run." % (s, e, w, w, w))
        lines.append("For every valuation its signed total (sum of +w contributions minus sum of -w contributions) must equal 0.")
        lines.append("Find the minimum number of cuts achieving this. Answer with one integer (the fewest cuts).")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        try:
            a = int(str(answer).strip())
        except Exception:
            return 0.0
        return 1.0 if a == int(entry.answer) else 0.0
