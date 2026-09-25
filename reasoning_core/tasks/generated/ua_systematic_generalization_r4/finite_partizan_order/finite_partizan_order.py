import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'finite_partizan_order (variant 2 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_systematic_generalization_r4/finite_partizan_order',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2701974858,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class PartizanOrderConfig(Config):
    n_positions: int = 3
    option_prob: float = 0.45

    def apply_difficulty(self, level):
        self.n_positions = max(3, int(3.0 + 0.7 * level))
        self.option_prob = min(0.75, 0.40 + 0.05 * level)


def _left_options(n, sign, lset, rset):
    return ((n, m, sign) for m in (lset if sign > 0 else rset))


def _right_options(n, sign, lset, rset):
    return ((n, m, sign) for m in (rset if sign > 0 else lset))


def outcome_class(left_each, right_first):
    """Map (Left-to-move wins, Right-first Left-second wins) to a comparison."""
    if left_each and right_first:
        return "greater"
    if (not left_each) and (not right_first):
        return "less"
    if (not left_each) and right_first:
        return "equal"
    return "incomparable"


def left_wins(sum_state, player, memo, lsets, rsets):
    """Normal-play: does Left win from this sum under normal-play rules?

    sum_state is a sorted tuple of terms (game_id, pos, sign) where sign +1 means
    the base position, -1 the negated position. lsets/rsets give each position's
    Left/Right option lists for each game id.
    """
    key = (sum_state, player)
    if key in memo:
        return memo[key]
    moves = []
    for i, (g, pos, sign) in enumerate(sum_state):
        lset = lsets[g][pos]
        rset = rsets[g][pos]
        opts = _left_options(pos, sign, lset, rset) if player == "L" else _right_options(pos, sign, lset, rset)
        for (_, m, ns) in opts:
            nxt = list(sum_state)
            nxt[i] = (g, m, ns)
            moves.append(tuple(sorted(nxt)))
    if player == "L":
        if not moves:
            memo[key] = False
            return False
        result = any(left_wins(m, "R", memo, lsets, rsets) for m in moves)
        memo[key] = result
        return result
    else:
        if not moves:
            memo[key] = True
            return True
        result = all(left_wins(m, "L", memo, lsets, rsets) for m in moves)
        memo[key] = result
        return result


def compare_positions(game_a, game_b):
    """Compare game A's root position vs game B's root position.

    Each game is a (l_options, r_options) pair where options are lists of
    position indices (position index -> options list).
    """
    a_l, a_r = game_a
    b_l, b_r = game_b
    lsets = {0: a_l, 1: b_l}
    rsets = {0: a_r, 1: b_r}
    nA = len(a_l)
    nB = len(b_l)
    root_a = nA - 1
    root_b = nB - 1
    memo = {}
    left_each = left_wins(((0, root_a, 1), (1, root_b, -1)), "L", memo, lsets, rsets)
    memo2 = {}
    right_first = left_wins(((0, root_a, 1), (1, root_b, -1)), "R", memo2, lsets, rsets)
    return outcome_class(left_each, right_first)


def build_game(n_positions, option_prob):
    """Random DAG of positions: position i< options over positions 0..i-1; root top."""
    n = n_positions
    lsets = []
    rsets = []
    for i in range(n):
        pool = list(range(i))
        rand = random.random
        l = sorted(x for x in pool if rand() < option_prob)
        r = sorted(x for x in pool if rand() < option_prob)
        lsets.append(l)
        rsets.append(r)
    return (lsets, rsets)


class FinitePartizanOrder(Task):
    summary = ("Compare finite partizan games built from left/right option sets, sums, "
               "and negation by recursive option exclusion; return less, equal, greater, "
               "or incomparable, including nonnumeric games.")
    design_choice = ("Encode each game as a directed acyclic graph of positions with "
                     "left/right edges; output comparison by solving a finite partizan "
                     "game outcome class via recursive dominance.")
    config_cls = PartizanOrderConfig

    def generate_entry(self):
        cfg = self.config
        n = max(2, cfg.n_positions)
        while True:
            game_a = build_game(n, cfg.option_prob)
            game_b = build_game(n, cfg.option_prob)
            result = compare_positions(game_a, game_b)
            if result is None:
                continue
            break
        return Entry(
            metadata={
                "n_positions": n,
                "game_a_l": game_a[0],
                "game_a_r": game_a[1],
                "game_b_l": game_b[0],
                "game_b_r": game_b[1],
            },
            answer=result,
        )

    def render_prompt(self, metadata):
        n = metadata["n_positions"]
        a_l = metadata["game_a_l"]
        a_r = metadata["game_a_r"]
        b_l = metadata["game_b_l"]
        b_r = metadata["game_b_r"]

        def fmt(lset, rset):
            return "[%s]/[%s]" % (
                ", ".join(str(x) for x in lset),
                ", ".join(str(x) for x in rset),
            )

        a_lines = ", ".join("P%d=%s" % (i, fmt(a_l[i], a_r[i])) for i in range(n))
        b_lines = ", ".join("Q%d=%s" % (i, fmt(b_l[i], b_r[i])) for i in range(n))
        return (
            "Two finite partizan combinatorial games A and B are given as directed acyclic "
            "graphs of positions. In each game, position k offers Left the option to move "
            "to any position in the set before the slash and Right the option to move to any "
            "position in the set after the slash; a game is {\"left options\" | \"right options\"}. "
            "An empty set means no move is available there. The game A is its top position "
            "P%d and game B is its top position Q%d. "
            "Under normal play (whoever cannot move loses), compare A with B as shortcuts in "
            "Conway's partial order: A is less than B, equal to B, greater than B, or "
            "incomparable with B (fuzzy). Say compare: Game A: %s. Game B: %s. "
            "Answer exactly one word: less, equal, greater, or incomparable."
            % (n - 1, n - 1, a_lines, b_lines)
        )

    def score_answer(self, answer, entry):
        prepr = lambda x: str(x).strip().lower()
        return 1.0 if prepr(answer) == prepr(entry.answer) else 0.0

    def distractor_candidates(self, entry):
        for w in ("less", "equal", "greater", "incomparable"):
            if w != entry.answer:
                yield w
