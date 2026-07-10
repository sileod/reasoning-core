import random
import typing
from dataclasses import dataclass
from functools import lru_cache

from typing_extensions import Self as _TypingSelf

if not hasattr(typing, "Self"):
    typing.Self = _TypingSelf

from pyggp import game_description_language as gdl
from pyggp.engine_primitives import Turn
from pyggp.interpreters import ClingoInterpreter, Interpreter

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround


@dataclass
class GameBestMoveConfig(Config):
    nodes: int = 7
    max_branch: int = 2
    horizon: int = 3

    def apply_difficulty(self, level):
        self.nodes = sround(self.nodes + level)
        self.max_branch = sround(self.max_branch + 0.25 * level)
        self.horizon = sround(self.horizon + level / 3)


def _name(i):
    return f"n{i}"


def _move_key(move):
    return str(move)


def _move_answer(move):
    text = _move_key(move)
    if text.startswith("move(") and text.endswith(")"):
        return text[5:-1]
    return text


def _edge_lines(edges, style):
    labels = ("left", "right", "up", "down", "take")
    if style == "edge":
        facts = [f"edge({_name(i)},{_name(j)})." for i, outs in edges.items() for j in sorted(outs)]
    else:
        facts = [
        f"arc({_name(i)},{labels[k % len(labels)]},{_name(j)})."
        for i, outs in edges.items()
        for k, j in enumerate(sorted(outs))
        ]
    return [" ".join(facts)]


def _fact_line(facts):
    return " ".join(facts)


class _SmallGraphGame:
    def _sample_dag(self):
        n = self.config.nodes
        leaf_count = random.randint(2, min(3, n - 2))
        first_leaf = n - leaf_count
        edges = {i: set() for i in range(n)}
        for i in range(first_leaf):
            candidates = list(range(i + 1, n))
            width = random.randint(1, min(self.config.max_branch, len(candidates)))
            edges[i].update(random.sample(candidates, width))
        return edges

    def _reachable_leaves(self, edges, start):
        seen, stack, leaves = set(), [start], set()
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            if not edges[node]:
                leaves.add(node)
            stack.extend(edges[node])
        return leaves

    def _rules(self, edges, start, payoffs, spec):
        leaves = [i for i, outs in edges.items() if not outs]
        horizon = self.config.horizon
        val, opp_val = spec["value"]
        terminal_fact = spec["terminal_fact"]
        lines = [
            "role(player).",
            "role(opponent).",
            f"init(at({_name(start)})).",
            "init(step(t0)).",
            "init(control(player)).",
        ]
        lines.append(_fact_line(f"succ(t{i},t{i + 1})." for i in range(horizon)))
        lines += _edge_lines(edges, spec["move"])
        lines.append(_fact_line(f"{terminal_fact}({_name(i)})." for i in leaves))
        lines.append(_fact_line(f"{val}({_name(i)},{v})." for i, v in sorted(payoffs.items())))
        lines.append(_fact_line(f"{opp_val}({_name(i)},{100 - v})." for i, v in sorted(payoffs.items())))
        if spec["control"] == "owner":
            lines.append(_fact_line(f"owner({_name(i)},{random.choice(('player', 'opponent'))})." for i in edges))

        if spec["move"] == "edge":
            lines += [
                "legal(R, move(Y)) :- true(control(R)), true(at(X)), edge(X,Y).",
                "next(at(Y)) :- does(R, move(Y)), true(control(R)), true(at(X)), edge(X,Y).",
            ]
            owner_next = "next(control(R2)) :- does(R, move(Y)), owner(Y,R2)."
        else:
            lines += [
                "legal(R, go(A,Y)) :- true(control(R)), true(at(X)), arc(X,A,Y).",
                "next(at(Y)) :- does(R, go(A,Y)), true(control(R)), true(at(X)), arc(X,A,Y).",
            ]
            owner_next = "next(control(R2)) :- does(R, go(A,Y)), owner(Y,R2)."

        lines.append("next(step(T2)) :- true(step(T)), succ(T,T2), does(R,M).")
        if spec["control"] == "owner":
            lines.append(owner_next)
        else:
            lines += [
                "next(control(opponent)) :- true(control(player)), does(player,M).",
                "next(control(player)) :- true(control(opponent)), does(opponent,M).",
            ]
        lines += [
            f"terminal :- true(at(X)), {terminal_fact}(X).",
            f"terminal :- true(step(t{horizon})).",
            f"goal(player,V) :- true(at(X)), {val}(X,V).",
            f"goal(opponent,V) :- true(at(X)), {opp_val}(X,V).",
        ]
        return "\n".join(lines)

    def _spec(self):
        return {
            "move": "edge",
            "control": "alternate",
            "terminal_fact": "leaf",
            "value": ("value", "opp_value"),
        }

    def _plain_description(self, edges, start, payoffs):
        edge_parts = []
        for i, outs in sorted(edges.items()):
            if outs:
                edge_parts.append(f"{_name(i)}->{','.join(_name(j) for j in sorted(outs))}")
        payoff_parts = [f"{_name(i)}:{payoffs[i]}" for i in sorted(edges)]
        return (
            f"Start: {_name(start)}. Turns alternate player, opponent. "
            f"Move along one edge per turn, for at most {self.config.horizon} moves. "
            "Play ends upon reaching a leaf or the move horizon; in either case, "
            "player's score is the current node's payoff. "
            f"Node payoffs: {'; '.join(payoff_parts)}. "
            f"Edges: {'; '.join(edge_parts)}."
        )

    def _solve(self, interpreter, role, state):
        @lru_cache(maxsize=None)
        def value(state):
            if interpreter.is_terminal(state):
                return interpreter.get_goal_by_role(state, role)
            maximizing = Interpreter.get_roles_in_control(state) == frozenset({role})
            child_values = [value(next_state) for _, next_state in interpreter.get_all_next_states(state)]
            return (max if maximizing else min)(child_values)

        options = []
        for move in interpreter.get_legal_moves_by_role(state, role):
            next_state = interpreter.get_next_state(state, Turn(((role, move),)))
            options.append((value(next_state), _move_key(move)))
        best_score = max(score for score, _ in options)
        return min(move for score, move in options if score == best_score), best_score, {move: score for score, move in options}

    def _sample_position(self, attempts=80):
        for _ in range(attempts):
            edges = self._sample_dag()
            leaves = [i for i, outs in edges.items() if not outs]
            if not leaves:
                continue
            payoffs = {i: random.randrange(0, 101, 10) for i in edges}
            start = random.randrange(max(1, self.config.nodes // 2))
            if len(self._reachable_leaves(edges, start)) < 2:
                continue
            spec = self._spec()
            rules = self._rules(edges, start, payoffs, spec)
            try:
                interpreter = ClingoInterpreter.from_ruleset(gdl.parse(rules))
                state = interpreter.get_init_state()
                role = next(r for r in interpreter.get_roles() if str(r) == "player")
                moves = interpreter.get_legal_moves_by_role(state, role)
                if len(moves) < 2 or interpreter.is_terminal(state):
                    continue
                answer, score, root_values = self._solve(interpreter, role, state)
            except Exception:
                continue
            move_scores = {_move_answer(move): value for move, value in root_values.items()}
            yield edict(
                start=start,
                spec=spec,
                rules=rules,
                state=state,
                role=role,
                moves=moves,
                answer=_move_answer(answer),
                score=score,
                root_values=root_values,
                move_scores=move_scores,
                description=self._plain_description(edges, start, payoffs),
            )

    def _metadata(self, position):
        return edict(
            rules=position.rules,
            description=position.description,
            state=", ".join(sorted(map(str, position.state))),
            role=str(position.role),
            backed_up_score=position.score,
            root_values=position.root_values,
            move_scores=position.move_scores,
            legal_moves=sorted(position.move_scores),
            game_config=position.spec,
        )


class GameBestMove(_SmallGraphGame, Task):
    summary = "Determine the minimax-optimal move for a player in a finite graph-based game."
    def __init__(self, config=GameBestMoveConfig()):
        super().__init__(config=config)

    def generate_entry(self):
        for position in self._sample_position():
            if len(set(position.move_scores.values())) < 2:
                continue
            if list(position.move_scores.values()).count(position.score) > 1:
                continue
            return Entry(metadata=self._metadata(position), answer=position.answer)
        raise RuntimeError("Could not sample a non-degenerate game position")

    def render_prompt(self, metadata):
        return (
            "In this graph game, choose player's best move. "
            "Player chooses on player turns; opponent chooses on opponent turns. "
            "Opponent minimizes player score.\n\n"
            f"{metadata.description}\n"
            f"Legal player moves now: {', '.join(metadata.legal_moves)}.\n"
            "The answer is the destination node of the best move."
        )

    def score_answer(self, answer, entry):
        return float(str(answer).strip() == entry.answer)


class GameForcedWin(_SmallGraphGame, Task):
    summary = "Decide if a player can force a win from a given state in a graph-based game."
    def __init__(self, config=GameBestMoveConfig()):
        super().__init__(config=config)

    def generate_entry(self):
        desired = random.choice((True, False))
        fallback = None
        for position in self._sample_position():
            if position.score == 50 or len(set(position.move_scores.values())) < 2:
                continue
            answer = "yes" if position.score > 50 else "no"
            if (answer == "yes") == desired:
                return Entry(metadata=self._metadata(position), answer=answer)
            if fallback is None:
                fallback = (position, answer)
        if fallback is not None:
            position, answer = fallback
            return Entry(metadata=self._metadata(position), answer=answer)
        raise RuntimeError("Could not sample a non-degenerate forced-win position")

    def render_prompt(self, metadata):
        return (
            "In this graph game, decide whether player can force a win. "
            "Player chooses on player turns; opponent chooses on opponent turns. "
            "Opponent minimizes player score. A win means final player score is greater than 50.\n\n"
            f"{metadata.description}\n"
            "The answer is yes or no."
        )

    def score_answer(self, answer, entry):
        return float(str(answer).strip().lower() == entry.answer)
