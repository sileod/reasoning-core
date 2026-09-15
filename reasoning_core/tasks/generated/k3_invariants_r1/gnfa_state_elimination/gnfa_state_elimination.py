import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

EPS = "eps"
NONE = "{}"


def star(r: str) -> str:
    if not r or r == NONE:
        return EPS
    if r == EPS:
        return EPS
    if r == EPS:
        return EPS
    if len(r) == 1:
        return f"{r}*"
    return f"({r})*"


def concat(a: str, b: str) -> str:
    if not a or a == NONE or not b or b == NONE:
        return NONE
    if a == EPS:
        return b
    if b == EPS:
        return a
    return f"{a}{b}"


def union(a: str, b: str) -> str:
    if not a or a == NONE:
        return b
    if not b or b == NONE:
        return a
    if a == b:
        return a
    return f"({a})|({b})"


def render_label(lab: str) -> str:
    if not lab or lab == NONE:
        return NONE
    return lab


@dataclass
class GnfaConfig(Config):
    level: int = 0
    state_count: int = 4
    mode: str = "final"

    def apply_difficulty(self, level):
        self.level = level
        self.state_count = 3 + level
        self.mode = "final"


def _add_transition(trans, a, b, label):
    if label == NONE:
        return
    key = (a, b)
    cur = trans.get(key, NONE)
    trans[key] = union(cur, label)


def _build_gnfa(n, alphabet):
    trans = {}
    for i in range(n):
        for j in range(n):
            r = random.random()
            n_letters = random.choice([0, 1]) if r < 0.35 else random.choice([1, 2])
            labels = set()
            for _ in range(n_letters):
                labels.add(random.choice(alphabet))
            if labels:
                lab = "|".join(sorted(labels))
                _add_transition(trans, i, j, lab)
    return trans


def _eliminate(trans, rip, keep):
    new = {}
    for i in keep:
        for j in keep:
            r4 = trans.get((i, j), NONE)
            r1 = trans.get((i, rip), NONE)
            r2 = trans.get((rip, rip), NONE)
            r3 = trans.get((rip, j), NONE)
            if r1 != NONE and r3 != NONE:
                term = concat(concat(r1, star(r2)), r3)
            else:
                term = NONE
            new[(i, j)] = union(r4, term)
    return new


def _compute(n, trans, order, start, accept, query_edge=None, query_cut=None):
    remaining = set(range(n))
    steps = []
    eliminated = 0
    for rip in order:
        remaining.discard(rip)
        eliminated += 1
        trans = _eliminate(trans, rip, remaining)
        steps.append((rip, dict(trans)))
        if query_cut is not None and eliminated >= query_cut:
            break
    if query_edge is not None:
        return (trans, remaining, steps)
    return (trans, remaining, steps)


class GnfaStateElimination(Task):
    summary = (
        "Reduce a generalized finite automaton to a regex by eliminating states in a stated order, "
        "composing edge labels with union, concatenation, and star; return the label on a queried "
        "edge mid-process or the final equivalent regex."
    )
    config_cls = GnfaConfig

    def generate_entry(self):
        while True:
            try:
                return self._gen_entry()
            except (ValueError, IndexError, KeyError):
                continue

    def _gen_entry(self):
        n = self.config.state_count
        alphabet = ["a", "b", "c"][: random.randint(2, 3)]
        trans = _build_gnfa(n, alphabet)

        start = 0
        accept = n - 1

        elimination_order = list(range(1, n - 1))
        random.shuffle(elimination_order)
        full_order = [start] + elimination_order + [accept]

        mode = "edge" if random.random() < 0.5 else "final"

        if mode == "final":
            order = [s for s in full_order if s not in (start, accept)]
            trans_final, remaining, _ = _compute(n, dict(trans), order, start, accept)
            ans = trans_final.get((start, accept), NONE)
            answer = render_label(ans)
            rendered_order = " -> ".join(f"q{s}" for s in elimination_order)
            metadata = {
                "n": n,
                "alphabet": alphabet,
                "transitions": {
                    f"q{i}|q{j}": render_label(trans.get((i, j), NONE))
                    for i in range(n)
                    for j in range(n)
                },
                "start": "q0",
                "accept": f"q{n-1}",
                "elimination_order": [f"q{s}" for s in elimination_order],
                "mode": "final",
            }
            prompt = (
                f"Consider a generalized nondeterministic finite automaton over alphabet "
                f"{{{', '.join(alphabet)}}}. Its states are {', '.join(f'q{i}' for i in range(n))}; "
                f"q0 is the start state and q{n-1} is the only accept state. "
                f"The transition label from state A to state B is the regex on the edge A->B; "
                f"'{NONE}' means no such edge, and 'eps' means epsilon. "
                f"The transition labels are:\n"
            )
            for i in range(n):
                for j in range(n):
                    lab = render_label(trans.get((i, j), NONE))
                    prompt += f"  q{i} -> q{j} : {lab}\n"
            prompt += (
                f"Eliminate the states one by one in this order: "
                f"{' -> '.join(f'q{s}' for s in elimination_order)}. "
                f"Each elimination removes a state and rewrites every remaining edge's label as "
                f"R1 R2* R3 | R4 (where R1 is the incoming edge to the removed state, R2 its self-loop, "
                f"R3 the outgoing edge, and R4 the old direct label), dropping any term with no edge. "
                f"After all non-start, non-accept states are eliminated, only q0 and q{n-1} remain. "
                f"Give the regex on the final edge q0 -> q{n-1}. "
                f"Use eps for epsilon and {NONE} if the edge does not exist. Answer with only the regex."
            )
        else:
            mid = random.randint(1, max(1, len(elimination_order)))
            query_order = elimination_order[:mid]
            remaining_states = [s for s in range(n) if s not in query_order]
            trans_mid, remaining, _ = _compute(n, dict(trans), query_order, start, accept)
            q_i = random.choice(remaining_states)
            q_j = random.choice(remaining_states)
            ans = trans_mid.get((q_i, q_j), NONE)
            answer = render_label(ans)
            metadata = {
                "n": n,
                "alphabet": alphabet,
                "transitions": {
                    f"q{i}|q{j}": render_label(trans.get((i, j), NONE))
                    for i in range(n)
                    for j in range(n)
                },
                "elimination_order": [f"q{s}" for s in query_order],
                "query_edge": (f"q{q_i}", f"q{q_j}"),
                "mode": "edge",
            }
            prompt = (
                f"Consider a generalized nondeterministic finite automaton over alphabet "
                f"{{{', '.join(alphabet)}}}. Its states are {', '.join(f'q{i}' for i in range(n))}; "
                f"q0 is the start state and q{n-1} is the only accept state. "
                f"The transition labels are:\n"
            )
            for i in range(n):
                for j in range(n):
                    lab = render_label(trans.get((i, j), NONE))
                    prompt += f"  q{i} -> q{j} : {lab}\n"
            prompt += (
                f"Eliminate the states in this order: "
                f"{' -> '.join(f'q{s}' for s in query_order)}. "
                f"Each elimination rewrites every remaining edge's label as R1 R2* R3 | R4, "
                f"dropping any term with no edge (where R1 is the edge into the removed state, "
                f"R2 its self-loop, R3 the edge out, and R4 the old direct label). "
                f"After eliminating exactly these states, give the label on the single edge "
                f"q{q_i} -> q{q_j}. Use eps for epsilon and {NONE} if that edge does not exist. "
                f"Answer with only the regex."
            )
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        n = metadata["n"]
        alphabet = metadata["alphabet"]
        prompt = (
            f"Consider a generalized nondeterministic finite automaton over alphabet "
            f"{{{', '.join(alphabet)}}}. Its states are {', '.join(f'q{i}' for i in range(n))}; "
            f"q0 is the start state and q{n-1} is the only accept state. "
            f"The transition labels are:\n"
        )
        for i in range(n):
            for j in range(n):
                lab = metadata["transitions"].get(f"q{i}|q{j}", NONE)
                prompt += f"  q{i} -> q{j} : {lab}\n"
        order = metadata["elimination_order"]
        prompt += f"Eliminate the states in this order: {' -> '.join(order)}. "
        if metadata["mode"] == "final":
            prompt += (
                f"Each elimination rewrites every remaining edge's label as R1 R2* R3 | R4, "
                f"dropping any term with no edge. After all non-start non-accept states are "
                f"eliminated, give the regex on the final edge q0 -> q{n-1}. "
                f"Use eps for epsilon and {NONE} if the edge does not exist."
            )
        else:
            qi, qj = metadata["query_edge"]
            prompt += (
                f"Each elimination rewrites every remaining edge's label as R1 R2* R3 | R4, "
                f"dropping any term with no edge. After eliminating exactly these states, give "
                f"the label on the edge {qi} -> {qj}. "
                f"Use eps for epsilon and {NONE} if that edge does not exist."
            )
        prompt += " Answer with only the regex."
        return prompt

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        a = str(answer).strip()
        gold = entry.answer.strip()
        return 1.0 if a == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'gnfa_state_elimination (draw 3 of 3, unguided baseline)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_invariants_r1/gnfa_state_elimination',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3143501959,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
