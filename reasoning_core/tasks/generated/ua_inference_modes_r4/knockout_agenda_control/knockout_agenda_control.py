"""Knockout agenda control: force a designated seed to win a single-elimination bracket.

Given a complete pairwise outcome table over a fixed set of seeds, choose a valid
single-elimination bracket structure so that a designated seed wins, keeping any
protected seed pairs apart until the final round. If no bracket can force the
designated seed, report impossibility.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {
    "parent_source_id": None,
    "idea": "knockout_agenda_control (variant 1 of 3)",
    "hypothesis": "P001",
    "changes": "new task in "
    "reasoning_core/tasks/generated/ua_inference_modes_r4/knockout_agenda_control",
    "generation": {
        "provider_name": "albert",
        "model_name": "deepseek-v4-flash",
        "harness_name": "opencode",
        "harness_version": "1.18.32",
        "agent_name": "task-search-worker",
        "settings": {
            "variant": None,
            "requested_seed": 1662004003,
            "seed_forwarded": True,
            "temperature": None,
            "top_p": None,
            "pure": True,
            "max_steps": 56,
            "timeout_seconds": 1800,
            "sandbox": {"name": "bubblewrap", "version": "bubblewrap 0.8.0"},
        },
    },
}

IMPOSSIBLE = "Impossible"


@dataclass
class KnockoutAgendaConfig(Config):
    n: int = 8
    protected_count: int = 3
    infeasible_prob: float = 0.30

    def apply_difficulty(self, level):
        self.n = 4 if level <= 1 else 8
        cap = 1 if self.n == 4 else 3
        self.protected_count = min(level // 2, cap)
        self.infeasible_prob = 0.30


def _num_rounds(n):
    return n.bit_length() - 1


def _bracket_string(order, win, n):
    cur = list(order)
    rounds = []
    while len(cur) > 1:
        pairs = []
        nxt = []
        for i in range(0, len(cur), 2):
            a, b = cur[i], cur[i + 1]
            lo, hi = (a, b) if a < b else (b, a)
            pairs.append("%dv%d" % (lo, hi))
            nxt.append(win[(lo, hi)])
        rounds.append(pairs)
        cur = nxt
    names = ["R%d" % (i + 1) for i in range(len(rounds) - 1)] + ["F"]
    return ";".join(
        "%s:%s" % (nm, ",".join(ps)) for nm, ps in zip(names, rounds)
    )


def _random_outcome(n, override):
    win = {}
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            key = (i, j)
            if (i, j) in override:
                win[key] = override[(i, j)]
            else:
                win[key] = i if random.random() < 0.5 else j
    return win


def _feasible_outcome(n, order, D):
    pos = order.index(D)
    m = _num_rounds(n)
    opponents = []
    for r in range(m):
        s = 1 << r
        sibling = ((pos // s) * s) ^ s
        opponents.append(order[sibling])
    override = {}
    for r, opp in enumerate(opponents):
        s = 1 << r
        sibling = ((pos // s) * s) ^ s
        for k in range(sibling, sibling + s):
            lo, hi = (opp, order[k]) if opp < order[k] else (order[k], opp)
            override[(lo, hi)] = opp
        lo, hi = (D, opp) if D < opp else (opp, D)
        override[(lo, hi)] = D
    return _random_outcome(n, override)


def _impossible_outcome(n, D):
    override = {}
    for o in range(1, n + 1):
        if o == D:
            continue
        lo, hi = (D, o) if D < o else (o, D)
        override[(lo, hi)] = o
    return _random_outcome(n, override)


def _choose_protected(n, count):
    seeds = list(range(1, n + 1))
    random.shuffle(seeds)
    pairs = []
    for k in range(count):
        a, b = seeds[2 * k], seeds[2 * k + 1]
        pairs.append([a, b])
    return pairs


def _split_order(n, protected):
    left, right = [], []
    used = set()
    for a, b in protected:
        used.add(a)
        used.add(b)
        if random.random() < 0.5:
            left.append(a)
            right.append(b)
        else:
            left.append(b)
            right.append(a)
    rest = [s for s in range(1, n + 1) if s not in used]
    random.shuffle(rest)
    cap = n // 2
    need = cap - len(left)
    for s in rest[:need]:
        left.append(s)
    for s in rest[need:]:
        right.append(s)
    random.shuffle(left)
    random.shuffle(right)
    return left + right


def _outcome_list(win):
    out = []
    for key, w in sorted(win.items()):
        out.append([key[0], key[1], w])
    return out


def _build_win(outcomes):
    return {(a, b): w for (a, b, w) in outcomes}


class KnockoutAgendaControl(Task):
    summary = ("From a complete pairwise outcome table over fixed seeds, build a "
               "single-elimination bracket forcing a designated champion while keeping "
               "protected pairs apart until the final, or report impossibility.")
    config_cls = KnockoutAgendaConfig
    task_version = 2

    def generate_entry(self):
        n = self.config.n
        D = random.randint(1, n)
        protected = _choose_protected(n, self.config.protected_count)

        if random.random() < self.config.infeasible_prob:
            win = _impossible_outcome(n, D)
            feasible = False
            bracket = IMPOSSIBLE
            order = _split_order(n, protected)
        else:
            order = _split_order(n, protected)
            for _ in range(200):
                win = _feasible_outcome(n, order, D)
                if _simulate(order, win, n) == D:
                    break
            else:
                win = _feasible_outcome(n, order, D)
            feasible = True
            bracket = _bracket_string(order, win, n)

        outcomes = _outcome_list(win)
        metadata = {
            "n": n,
            "winner": D,
            "protected": protected,
            "outcomes": outcomes,
            "feasible": feasible,
        }
        if feasible:
            sub = _simulate(order, _build_win(outcomes), n)
            assert sub == D, "gold bracket must force the designated winner"
            assert _valid_bracket(
                bracket, n, _build_win(outcomes), D, protected), "gold bracket must be valid"
        else:
            for o in range(1, n + 1):
                if o == D:
                    continue
                lo, hi = (D, o) if D < o else (o, D)
                assert _build_win(outcomes)[(lo, hi)] != D, "impossible instance must have D lose"
        return Entry(metadata=metadata, answer=bracket)

    def render_prompt(self, metadata):
        n = metadata["n"]
        win = _build_win(metadata["outcomes"])
        lines = []
        for s in range(1, n + 1):
            beaten = [o for o in range(1, n + 1) if o != s and win[(min(s, o), max(s, o))] == s]
            if beaten:
                lines.append("Seed %d beats: %s." % (s, ", ".join(str(b) for b in beaten)))
            else:
                lines.append("Seed %d beats nobody." % s)
        if metadata["protected"]:
            prot = ", ".join(
                "%d & %d" % (min(a, b), max(a, b)) for a, b in metadata["protected"]
            )
            prot_line = ("Protected pairings (must not meet before the final): " + prot + ".")
        else:
            prot_line = "There are no protected pairings."
        return (
            "We run a single-elimination knockout among seeds 1..%d. For every pair, the "
            "listed outcome says which seed wins if they meet.\n\n"
            "%s\n\n"
            "%s\n\n"
            "Seed %d is the designated champion that must be forced to win. Construct a "
            "valid full bracket in which seed %d wins, respecting the protected pairings. "
            "If no bracket can make seed %d win, answer exactly: %s\n\n"
            "Otherwise answer with the bracket as round pairings of actual seeds, e.g. "
            "'R1:1v8,4v5;R2:1v4;F:1v4' (fewest rounds first, final marked F); any valid "
            "bracket that forces seed %d wins is accepted."
        ) % (
            n,
            "\n".join(lines),
            prot_line,
            metadata["winner"],
            metadata["winner"],
            metadata["winner"],
            IMPOSSIBLE,
            metadata["winner"],
        )

    def score_answer(self, answer, entry):
        return _score(answer, entry.metadata)


def _simulate(order, win, n):
    cur = list(order)
    while len(cur) > 1:
        nxt = []
        for i in range(0, len(cur), 2):
            a, b = cur[i], cur[i + 1]
            nxt.append(win[(min(a, b), max(a, b))])
        cur = nxt
    return cur[0]


def _valid_bracket(text, n, win, D, protected):
    prot = set((min(a, b), max(a, b)) for a, b in protected)
    segs = [s.strip() for s in text.split(";") if s.strip()]
    m = _num_rounds(n)
    if len(segs) != m:
        return False
    prevwinners = None
    for r, seg in enumerate(segs):
        if ":" not in seg:
            return False
        name, pairs_txt = seg.split(":", 1)
        exp = "F" if r == m - 1 else "R%d" % (r + 1)
        if name.strip() != exp:
            return False
        pairs = [p.strip() for p in pairs_txt.split(",") if p.strip()]
        if len(pairs) != (n >> (r + 1)):
            return False
        allseeds = []
        winners = []
        for p in pairs:
            if "v" not in p:
                return False
            a, b = p.split("v")
            try:
                a, b = int(a), int(b)
            except ValueError:
                return False
            if not (1 <= a <= n and 1 <= b <= n) or a == b:
                return False
            lo, hi = (a, b) if a < b else (b, a)
            allseeds.append(a)
            allseeds.append(b)
            if (lo, hi) in prot and r < m - 1:
                return False
            winners.append(win[(lo, hi)])
        if r == 0:
            if sorted(allseeds) != list(range(1, n + 1)):
                return False
        else:
            if sorted(allseeds) != sorted(prevwinners):
                return False
        prevwinners = winners
    return bool(prevwinners) and prevwinners[0] == D


def _score(answer, metadata):
    n = metadata["n"]
    D = metadata["winner"]
    win = _build_win(metadata["outcomes"])
    strip = (answer or "").strip()
    if strip == IMPOSSIBLE:
        return 1.0 if not metadata["feasible"] else 0.0
    return 1.0 if _valid_bracket(strip, n, win, D, metadata["protected"]) else 0.0
