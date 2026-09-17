import itertools
import json
import random
import re

import pytest
import z3

from reasoning_core.tasks.generated.k3_controlled_nli_r1.speaker_role_consistency import speaker_role_consistency as mod


def parse_expression(text, facts, roles):
    tokens = re.findall(r"H\([A-Z]\)|F\d+|NOT|AND|OR|XOR|IFF|[()]", text)
    position = 0

    def parse():
        nonlocal position
        token = tokens[position]
        position += 1
        if token == "NOT":
            return z3.Not(parse())
        if token == "(":
            left = parse()
            op = tokens[position]
            position += 1
            right = parse()
            assert tokens[position] == ")"
            position += 1
            return {"AND": z3.And, "OR": z3.Or, "XOR": z3.Xor, "IFF": lambda a, b: a == b}[op](left, right)
        if token.startswith("H("):
            return roles[token[2]]
        return facts[token]

    result = parse()
    assert position == len(tokens)
    return result


def independent_answer(prompt, n):
    roles = {chr(65 + i): z3.Bool(chr(65 + i)) for i in range(n)}
    facts = {}
    solver = z3.Solver()
    constraints = []
    for line in prompt.splitlines():
        fact_match = re.fullmatch(r"(F\d+) = (.*)", line)
        claim_match = re.fullmatch(r"C(\d+)\. ([A-Z]) claims: (.*)", line)
        if fact_match:
            name, expression = fact_match.groups()
            facts[name] = z3.BoolVal(expression == "true") if expression in ("true", "false") else parse_expression(expression, facts, roles)
        if claim_match:
            number, owner, expression = claim_match.groups()
            constraint = roles[owner] == parse_expression(expression, facts, roles)
            constraints.append(constraint)
            solver.add(constraint)
            result = solver.check()
            assert result in (z3.sat, z3.unsat)
            if result == z3.unsat:
                return f"C{number}"
    valid = []
    for bits in itertools.product((True, False), repeat=n):
        substitutions = [(role, z3.BoolVal(value)) for role, value in zip(roles.values(), bits)]
        if all(z3.is_true(z3.simplify(z3.substitute(c, substitutions))) for c in constraints):
            valid.append("".join("H" if bit else "L" for bit in bits))
    assert valid
    return min(valid)


@pytest.mark.parametrize("level", [0, 2, 5, 6])
def test_prompt_independently_determines_gold(level):
    random.seed(200 + level)
    task = mod.SpeakerRoleConsistency()
    task.config.set_level(level)
    modes = set()
    for _ in range(8):
        entry = task.generate_entry()
        prompt = task.render_prompt(entry.metadata)
        assert independent_answer(prompt, entry.metadata["n_speakers"]) == entry.answer
        assert task.score_answer(entry.answer, entry) == 1.0
        assert task.score_answer("garbage", entry) == 0.0
        assert task.score_answer("", entry) == 0.0
        metadata = json.loads(json.dumps(entry.metadata))
        assert task.render_prompt(metadata) == prompt
        modes.add(entry.answer.startswith("C"))
    assert modes == {True, False}


def test_boolean_operators_and_negation():
    for left, right in itertools.product((False, True), repeat=2):
        expected = {"AND": left and right, "OR": left or right, "XOR": left != right, "IFF": left == right}
        for op, value in expected.items():
            assert mod.boolean(op, left, right) == value
        for negated in (False, True):
            claim = ["fact", 0, 1, "AND", 0, negated]
            assert mod.claim_truth(claim, [right, left], [left]) == (left != negated)


def test_prefix_blocking_and_tie_break():
    claim = ["link", 1, 0, "IFF", 0, False]
    solutions, blocking, _ = mod.exhaustive_candidates(2, [True], [claim], [0])
    assert solutions == [(True, True), (False, False)]
    assert blocking is None
    flipped = [*claim[:-1], True]
    solutions, blocking, previous = mod.exhaustive_candidates(2, [True], [claim, flipped], [0, 0])
    assert not solutions and blocking == 1
    assert previous == [(True, True), (False, False)]


def test_scorer_does_not_access_self():
    class NoAccess:
        def __getattribute__(self, name):
            raise AssertionError(name)

    entry = mod.Entry(metadata={}, answer="HLLH")
    score = mod.SpeakerRoleConsistency.score_answer
    assert score(NoAccess(), " HLLH ", entry) == 1.0
    for answer in (None, [], "", "LHHH", "hllh", "H L L H"):
        assert score(NoAccess(), answer, entry) == 0.0


def test_seed_reproducibility_and_fractional_difficulty():
    task = mod.SpeakerRoleConsistency()
    task.config.set_level(2.5)
    random.seed(618)
    first = task.generate_entry()
    random.seed(618)
    second = task.generate_entry()
    assert first.metadata == second.metadata
    assert first.answer == second.answer
