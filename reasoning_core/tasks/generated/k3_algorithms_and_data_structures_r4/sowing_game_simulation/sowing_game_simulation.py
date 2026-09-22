import random
from dataclasses import dataclass

from reasoning_core.template import Entry, Config, Task, edict


@dataclass
class SowingConfig(Config):
    n_pits: int = 5
    max_seed: int = 6
    n_starts: int = 3

    def apply_difficulty(self, level):
        self.n_pits = int(4 + 0.5 * level)
        self.max_seed = int(5 + 0.6 * level)
        self.n_starts = int(2 + 0.5 * level)


def _sow_turn(board, start, direction, max_steps=500):
    n = len(board)
    b = list(board)
    if b[start] == 0:
        return None
    captured = 0
    cur = start
    steps = 0
    while True:
        steps += 1
        if steps > max_steps:
            return None
        s = b[cur]
        b[cur] = 0
        pos = cur
        for _ in range(s):
            pos = (pos + direction) % n
            b[pos] += 1
        L = pos
        if b[L] == 1:
            mirror = n - 1 - L
            captured += b[mirror] + 1
            b[mirror] = 0
            b[L] = 0
            return (b, captured)
        if L != start and b[L] > 0:
            cur = L
            continue
        return (b, captured)


def _play(seeds, starts, direction):
    b = list(seeds)
    captured = 0
    illegal = None
    for p in starts:
        if b[p] == 0:
            illegal = p
            break
        res = _sow_turn(b, p, direction)
        if res is None:
            return None
        b, c = res
        captured += c
    return {"board": b, "captured": captured, "illegal": illegal}


def _norm(text):
    return "".join(str(text).replace(",", " ").split())


class SowingGameSimulation(Task):
    summary = ("Simulate stipulated mancala-style sowing games with clockwise or "
               "counter-clockwise sow direction, mirror capture on an empty final "
               "landing pit, and relay chaining on non-empty landings; answers give "
               "the final pit layout, the captured seed total, or the first illegal "
               "empty-pit move.")
    config_cls = SowingConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_pits
        max_seed = cfg.max_seed
        n_starts = max(2, cfg.n_starts)
        mode = random.choice(("layout", "captured", "illegal"))
        for _ in range(500):
            direction = random.choice((1, -1))
            if mode == "illegal":
                board = [random.randint(0, max_seed) for _ in range(n)]
                empty = [i for i, v in enumerate(board) if v == 0]
                if not empty:
                    continue
                e = random.choice(empty)
                others = [i for i in range(n) if i != e]
                random.shuffle(others)
                starts = [e] + others[: n_starts - 1]
                play = _play(board, starts, direction)
                if play is None or play["illegal"] is None:
                    continue
                metadata = dict(board=board, starts=starts, direction=direction,
                                mode="illegal", n_pits=n, illegal=e)
                return Entry(metadata=edict(metadata), answer=str(e))
            board = [random.randint(1, max_seed) for _ in range(n)]
            candidates = list(range(n))
            random.shuffle(candidates)
            starts = candidates[:n_starts]
            play = _play(board, starts, direction)
            if play is None or play["illegal"] is not None:
                continue
            if mode == "captured":
                if play["captured"] < 1:
                    continue
                metadata = dict(board=board, starts=starts, direction=direction,
                                mode="captured", captured=play["captured"], n_pits=n)
                return Entry(metadata=edict(metadata), answer=str(play["captured"]))
            final = play["board"]
            metadata = dict(board=board, starts=starts, direction=direction,
                            mode="layout", final=final, n_pits=n)
            answer = ",".join(str(x) for x in final)
            return Entry(metadata=edict(metadata), answer=answer)
        raise RuntimeError("failed to generate a valid sowing instance")

    def render_prompt(self, metadata):
        m = metadata
        board_str = ", ".join(f"{i}:{v}" for i, v in enumerate(m["board"]))
        dir_word = "clockwise (right)" if m["direction"] == 1 else "counter-clockwise (left)"
        starts = ", ".join(str(x) for x in m["starts"])
        rules = (
            "There is a circular board of %d pits numbered 0..%d. Initial seeds per pit "
            "(index:count): %s. Sowing moves %s. On each turn: pick up all seeds from the "
            "start pit; if that pit has 0 seeds the move is illegal. Distribute them one "
            "seed per pit moving that direction, wrapping at the end. If the last seed "
            "lands in a pit that was empty before its drop, capture: remove the single "
            "landing seed plus all seeds in the mirror pit (index n-1-L), add them to a "
            "running captured total, and end the turn. Otherwise, if the landing pit is "
            "now non-empty and is not the turn's start pit, relay: continue sowing from "
            "it. Play turns in order starting from pits: %s. "
        ) % (m["n_pits"], m["n_pits"] - 1, board_str, dir_word, starts)
        if m["mode"] == "illegal":
            q = ("Give the pit index of the first illegal move (the first attempted turn "
                 "whose start pit is empty). The answer is one integer.")
        elif m["mode"] == "captured":
            q = ("Give the total number of seeds captured across the whole play. "
                 "The answer is one integer.")
        else:
            q = ("Give the final pit layout after the entire play, as pit counts in pit "
                 "order 0..n-1, comma-separated (e.g. 3,0,5,2).")
        return rules + q

    def score_answer(self, answer, entry):
        return float(_norm(answer) == _norm(entry.answer))


TASK_META = {'parent_source_id': None,
 'idea': 'sowing_game_simulation (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_algorithms_and_data_structures_r4/sowing_game_simulation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 4238614268,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
