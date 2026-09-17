import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'speaker_role_consistency (variant 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_controlled_nli_r1/speaker_role_consistency',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3867019559,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

OPERATORS = ("AND", "OR", "XOR", "IFF")


def boolean(op, left, right):
    if op == "AND":
        return left and right
    if op == "OR":
        return left or right
    if op == "XOR":
        return left != right
    if op == "IFF":
        return left == right
    raise ValueError(op)


def evaluate_facts(roots, graph):
    values = list(roots)
    for op, left, right in graph:
        values.append(boolean(op, values[left], values[right]))
    return values


def claim_truth(claim, roles, facts):
    kind, left, right, op, fact, negated = claim
    if kind == "fact":
        value = facts[fact]
    elif kind == "link":
        value = boolean(op, roles[left], facts[fact])
    else:
        value = boolean("XOR", boolean(op, roles[left], roles[right]), facts[fact])
    return value != negated


def exhaustive_candidates(n_speakers, facts, claims, owners):
    survivors = list(itertools.product((True, False), repeat=n_speakers))
    for index, (claim, owner) in enumerate(zip(claims, owners)):
        previous = survivors
        survivors = [roles for roles in previous if claim_truth(claim, roles, facts) == roles[owner]]
        if not survivors:
            return [], index, previous
    return survivors, None, []


@dataclass
class SpeakerRoleConsistencyConfig(Config):
    n_speakers: int = 4
    n_derived: int = 3

    def apply_difficulty(self, level):
        self.n_speakers = min(9, int(4 + 0.8 * level))
        self.n_derived = min(10, int(3 + level))


class SpeakerRoleConsistency(Task):
    summary = "Speakers make claims about a random Boolean fact graph and each other's honest/liar roles: return the lexicographically first full consistent role assignment or the first blocking claim."
    design_choice = "Role roster is fixed per instance but claims are generated from a random graph of facts, so solvers must deduce roles via boolean constraint propagation rather than pattern matching."
    config_cls = SpeakerRoleConsistencyConfig
    task_version = 3

    def generate_entry(self):
        n = self.config.n_speakers
        inconsistent = random.choice((False, True))
        for _ in range(80):
            roots = [random.choice((True, False)) for _ in range(3)]
            graph = []
            for index in range(3, 3 + self.config.n_derived):
                left = index - 1
                right = random.randrange(index - 1)
                if random.choice((False, True)):
                    left, right = right, left
                graph.append([random.choice(OPERATORS), left, right])
            facts = evaluate_facts(roots, graph)
            planted = [random.choice((True, False)) for _ in range(n)]
            cycle = random.sample(range(n), n)
            claims, owners = [], []
            for position, owner in enumerate(cycle):
                for repeat in range(2):
                    left = cycle[(position + 1) % n] if repeat == 0 else random.randrange(n)
                    right = random.choice([i for i in range(n) if i != left])
                    kind = random.choices(("fact", "link", "pair"), (1, 4, 5))[0]
                    claim = [kind, left, right, random.choice(OPERATORS), random.randrange(3, len(facts)), False]
                    claim[-1] = claim_truth(claim, planted, facts) != planted[owner]
                    claims.append(claim)
                    owners.append(owner)
            order = random.sample(range(len(claims)), len(claims))
            claims = [claims[i] for i in order]
            owners = [owners[i] for i in order]
            if inconsistent:
                changed = random.randrange(len(claims))
                claims[changed][-1] = not claims[changed][-1]
            solutions, blocking, previous = exhaustive_candidates(n, facts, claims, owners)
            if bool(solutions) == inconsistent:
                continue
            if solutions:
                answer = "".join("H" if role else "L" for role in solutions[0])
                decoded = tuple(letter == "H" for letter in answer)
                assert all(claim_truth(c, decoded, facts) == decoded[o] for c, o in zip(claims, owners))
                assert answer == min("".join("H" if r else "L" for r in roles) for roles in solutions)
            else:
                assert blocking is not None and previous
                witness = previous[0]
                assert all(claim_truth(c, witness, facts) == witness[o] for c, o in zip(claims[:blocking], owners[:blocking]))
                assert all(claim_truth(claims[blocking], r, facts) != r[owners[blocking]] for r in previous)
                answer = f"C{blocking + 1}"
            return Entry(metadata={"n_speakers": n, "roots": roots, "graph": graph,
                                   "claims": claims, "owners": owners}, answer=answer)
        raise RuntimeError("No instance of the requested consistency mode in 80 attempts")

    def render_prompt(self, metadata):
        n = metadata["n_speakers"]
        names = [chr(65 + i) for i in range(n)]
        lines = [
            f"At a hearing, speakers {', '.join(names)} each have one fixed role from the roster H (honest) or L (liar).",
            "Roles may repeat; no counts are imposed. Every claim by H must be true and every claim by L must be false.",
            "The following fact definitions are given as true rules, not speaker claims. Each F is Boolean. AND requires both operands, OR is inclusive, XOR means exactly one, IFF means equal truth values, and NOT reverses truth.",
        ]
        for index, value in enumerate(metadata["roots"]):
            lines.append(f"F{index + 1} = {'true' if value else 'false'}")
        for index, (op, left, right) in enumerate(metadata["graph"], 4):
            lines.append(f"F{index} = (F{left + 1} {op} F{right + 1})")
        lines.append("In claims, H(A) means 'A has role H' (similarly for other names). Claims are numbered in the order to process:")
        for index, (claim, owner) in enumerate(zip(metadata["claims"], metadata["owners"]), 1):
            kind, left, right, op, fact, negated = claim
            if kind == "fact":
                text = f"F{fact + 1}"
            elif kind == "link":
                text = f"(H({names[left]}) {op} F{fact + 1})"
            else:
                text = f"((H({names[left]}) {op} H({names[right]})) XOR F{fact + 1})"
            if negated:
                text = f"NOT {text}"
            lines.append(f"C{index}. {names[owner]} claims: {text}")
        lines.append(
            "Use Boolean constraint propagation or exhaustive role assignment search. If all claims can hold under the role rules, return the lexicographically smallest role string in speaker order above, with H before L; for example HLLH for four speakers. Otherwise return the first blocking claim Ck: the smallest k such that no assignment satisfies claims C1 through Ck (ignore later claims). Example format: C7. Output only the role string or claim label."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        return float(isinstance(answer, str) and answer.strip() == entry.answer)
