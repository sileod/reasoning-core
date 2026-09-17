"""Trick-taking adjudication under stipulated per-suit rank orders."""
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

PLAYERS = ["North", "East", "South", "West"]
SUITS = "CDHS"
RANKS = "AKQJT9876"

TASK_META = {'parent_source_id': None,
 'idea': 'trick_taking_adjudication (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_cognitive_psychology_r1/trick_taking_adjudication',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
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
class AdjudicationConfig(Config):
    tricks_played: int = 2
    n_ranks: int = 6

    def apply_difficulty(self, level):
        self.tricks_played = 2 + int(level) // 2
        self.n_ranks = min(9, 6 + int(level) // 3)


def legal_plays(hand, led):
    following = [c for c in hand if c[0] == led]
    return following or list(hand)


def strength(card, led, trump, order):
    return (2 if card[0] == trump else 1 if card[0] == led else 0,
            -order[card[0]].index(card[1]))


def winner_of(plays, revoked, trump, order):
    led = plays[0][1][0]
    eligible = [(p, c) for p, c in plays if p not in revoked]
    return max(eligible, key=lambda pc: strength(pc[1], led, trump, order))[0]


def card_value(card, order):
    return len(order[card[0]]) - order[card[0]].index(card[1])


def ordered_cards(cards, order):
    return sorted(cards, key=lambda c: (SUITS.index(c[0]), order[c[0]].index(c[1])))


def format_list(items):
    return "[" + ", ".join(str(x) for x in items) + "]"


def verify_round(metadata):
    hands = {p: list(metadata["initial"][p]) for p in PLAYERS}
    flat = [c for hand in hands.values() for c in hand]
    assert len(flat) == len(set(flat))
    winners, scores, revokes = [], dict.fromkeys(PLAYERS, 0), []
    previous = None
    for tr in metadata["tricks"]:
        plays, order, trump = tr["plays"], tr["order"], tr["trump"]
        for s in SUITS:
            assert sorted(order[s]) == sorted(metadata["ranks"])
        assert len(set(order.values())) == 4
        if previous is not None:
            assert all(previous[s] != order[s] for s in SUITS)
        previous = order
        start = PLAYERS.index(plays[0][0])
        led = plays[0][1][0]
        eligible, revoked = [], []
        for i, (p, c) in enumerate(plays):
            assert p == PLAYERS[(start + i) % 4]
            assert c in hands[p]
            violation = c[0] != led and any(h[0] == led for h in hands[p])
            if violation:
                revoked.append(p)
                scores[p] -= metadata["penalty"]
            else:
                eligible.append((p, c))
            hands[p].remove(c)
        revokes.append(revoked)
        if len(plays) < 4:
            assert tr is metadata["tricks"][-1]
            continue
        suit = trump if any(c[0] == trump for _, c in eligible) else led
        candidates = [(p, c) for p, c in eligible if c[0] == suit]
        best = []
        for p, c in candidates:
            if all(order[suit].index(c[1]) <= order[suit].index(other[1])
                   for _, other in candidates):
                best.append(p)
        assert len(best) == 1
        winners.append(best[0])
        value = sum(list(reversed(order[c[0]])).index(c[1]) + 1 for _, c in plays)
        assert value >= 4
        scores[best[0]] += value
    if metadata["mode"] == "legal":
        tr = metadata["tricks"][-1]
        p = PLAYERS[(PLAYERS.index(tr["plays"][0][0]) + len(tr["plays"])) % 4]
        assert p == metadata["next_player"]
        led = tr["plays"][0][1][0]
        must_follow = any(c[0] == led for c in hands[p])
        allowed = [c for s in SUITS for r in tr["order"][s]
                   for c in [s + r] if c in hands[p] and (not must_follow or s == led)]
        assert allowed
        answer = format_list(allowed)
    elif metadata["mode"] == "winner":
        answer = format_list(winners)
    else:
        assert sum(scores.values()) == sum(
            sum(len(tr["order"][c[0]]) - tr["order"][c[0]].index(c[1])
                for _, c in tr["plays"]) for tr in metadata["tricks"]
        ) - metadata["penalty"] * sum(map(len, revokes))
        answer = format_list([scores[p] for p in PLAYERS])
    return answer, winners, scores, revokes


class TrickTakingAdjudication(Task):
    summary = "Adjudicate trick-taking card play under conflicting per-suit rank orders recomputed each trick, trump and lead-suit rules, follow-suit duties, and revoke penalties; answers list a hand's legal plays, name each trick's winner, or total each player's round points."
    design_choice = "Difficulty arises from conflicting suit orderings per trick, requiring recomputation of rank hierarchy for each adjudication rather than a fixed deck."
    config_cls = AdjudicationConfig
    task_version = 3

    def generate_entry(self):
        mode = random.choice(["legal", "winner", "points"])
        for _ in range(200):
            metadata, answer = self._draw(mode)
            if metadata is None:
                continue
            checked, winners, scores, revokes = verify_round(metadata)
            assert answer == checked
            metadata["winners"] = winners
            metadata["scores"] = scores
            metadata["revokes"] = revokes
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("Could not generate a contested round in 200 attempts")

    def _draw(self, mode):
        count = self.config.tricks_played
        ranks = RANKS[:self.config.n_ranks]
        size = count + 2
        if 4 * size > 4 * len(ranks):
            raise RuntimeError("Too many tricks for the stipulated deck")
        deck = random.sample([s + r for s in SUITS for r in ranks], 4 * size)
        initial = {p: sorted(deck[i * size:(i + 1) * size]) for i, p in enumerate(PLAYERS)}
        hands = {p: list(h) for p, h in initial.items()}
        metadata = {"mode": mode, "initial": initial, "ranks": ranks,
                    "penalty": random.randint(3, 12), "tricks": []}
        scores, winners = dict.fromkeys(PLAYERS, 0), []
        contested = changed_winner = False
        previous = None
        for i in range(count):
            order = {}
            for s in SUITS:
                for _ in range(100):
                    permutation = "".join(random.sample(ranks, len(ranks)))
                    if permutation not in order.values() and (previous is None or permutation != previous[s]):
                        order[s] = permutation
                        break
                else:
                    raise RuntimeError("Could not draw conflicting suit orders")
            trump = random.choice([None, *SUITS])
            leader = random.randrange(4)
            nplays = random.randint(1, 3) if mode == "legal" and i == count - 1 else 4
            plays, revoked = [], []
            for j in range(nplays):
                p = PLAYERS[(leader + j) % 4]
                led = plays[0][1][0] if plays else None
                legal = legal_plays(hands[p], led)
                illegal = [c for c in hands[p] if c not in legal]
                pool = illegal if illegal and random.random() < 0.3 else legal
                card = random.choice(pool)
                if card not in legal:
                    revoked.append(p)
                    scores[p] -= metadata["penalty"]
                plays.append([p, card])
                hands[p].remove(card)
            tr = {"order": order, "trump": trump, "plays": plays}
            metadata["tricks"].append(tr)
            if nplays == 4:
                winner = winner_of(plays, revoked, trump, order)
                winners.append(winner)
                scores[winner] += sum(card_value(c, order) for _, c in plays)
                winning_card = next(c for p, c in plays if p == winner)
                contested |= sum(c[0] == winning_card[0] and p not in revoked for p, c in plays) > 1
                if previous is not None:
                    changed_winner |= winner_of(plays, revoked, trump, previous) != winner
            else:
                p = PLAYERS[(leader + nplays) % 4]
                metadata["next_player"] = p
                cards = ordered_cards(legal_plays(hands[p], plays[0][1][0]), order)
                answer = format_list(cards)
            previous = order
        if not contested or (mode != "legal" and not changed_winner):
            return None, None
        if mode == "winner":
            answer = format_list(winners)
        elif mode == "points":
            answer = format_list([scores[p] for p in PLAYERS])
        return metadata, answer

    def render_prompt(self, metadata):
        m = metadata
        lines = [
            "Adjudicate this club's trick-taking round. Cards use suit C=clubs, D=diamonds, "
            "H=hearts, S=spades followed by rank (T means ten). Every card is unique; "
            "only the dealt cards are in play. No cards are drawn or returned.",
            "The announced leader of each trick is chosen independently, NOT by the previous winner. "
            "Play proceeds North, East, South, West cyclically from that leader. "
            "The first card sets the lead suit. Follow that suit if held immediately before playing; "
            "otherwise any card is legal. The leader may play any held card.",
            f"Playing off-suit while able to follow is a revoke: subtract {m['penalty']} points from "
            "that player, and their card cannot win this trick. It is still removed from their hand "
            "and captured by the winner. Other cards remain eligible. No other penalty applies.",
            "Use the standard maximum-card scan: among eligible cards, any trump beats any non-trump; "
            "if none is trump, only the lead suit can win. The strongest card in that suit wins. "
            "Each trick gives NEW, independent strongest-to-weakest rank strings for each suit; "
            "ordinary card ranks do not apply. Trump=none means no trump.",
        ]
        if m["mode"] == "points":
            lines.append("All players start at zero. The winner captures all four cards. Each card "
                         "is worth its position counted from weakest in its OWN suit's order FOR THAT "
                         "TRICK: weakest=1, next=2, etc. Add captured values and subtract that player's "
                         "revoke penalties. Negative totals are allowed. Unplayed cards score nothing.")
        for p in PLAYERS:
            lines.append(f"Initially {p} holds {', '.join(m['initial'][p])}.")
        for i, tr in enumerate(m["tricks"], 1):
            orders = "; ".join(f"{s}:{tr['order'][s]}" for s in SUITS)
            plays = ", ".join(f"{p}={c}" for p, c in tr["plays"])
            lines.append(f"Trick {i}: trump={tr['trump'] or 'none'}; {orders}. "
                         f"Plays in order: {plays}.")
        if m["mode"] == "legal":
            lines.append(f"The last trick is unfinished. List all legal plays for {m['next_player']} "
                         "now, suits in C,D,H,S order and ranks strongest first under this trick's "
                         "own suit orders. Answer as a bracketed list, for example [CQ, C9, HA].")
        elif m["mode"] == "winner":
            lines.append("List every trick's winner in chronological order. Answer as a bracketed "
                         "list of names, for example [East, South].")
        else:
            lines.append("Total each player's points for the shown round. Answer as a bracketed "
                         "list of integers in North, East, South, West order, for example [12, -3, 8, 0].")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str) or not answer.strip().startswith("[") or not answer.strip().endswith("]"):
            return 0.0
        parts = [p.strip() for p in answer.strip()[1:-1].split(",")]
        gold = [p.strip() for p in entry.answer[1:-1].split(",")]
        return float(parts == gold)
