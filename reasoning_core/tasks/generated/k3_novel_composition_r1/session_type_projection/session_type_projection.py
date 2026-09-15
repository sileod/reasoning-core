import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'session_type_projection (draw 3 of 3, unguided baseline)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_novel_composition_r1/session_type_projection',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}

_PARTICIPANTS = ["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7"]
_PAYLOADS = ["m", "d", "k", "a"]


def _is_var(node):
    return isinstance(node, str)


def _render(t):
    if t == "end":
        return "end"
    if isinstance(t, str):
        return t
    if t[0] == "mu":
        return f"mu {t[1]}. {_render(t[2])}"
    if t[0] == "seq":
        return f"{_render(t[1])} . {_render(t[2])}"
    if t[0] == "!":
        return f"{t[1]} ! {t[2]}"
    if t[0] == "?":
        return f"{t[1]} ? {t[2]}"
    raise ValueError(t)


def _collect_ids(t, out):
    """Collect participants appearing in a type node (recursion var allowed)."""
    if t == "end" or isinstance(t, str):
        return
    if t[0] == "mu":
        _collect_ids(t[2], out)
    elif t[0] == "seq":
        _collect_ids(t[1], out)
        _collect_ids(t[2], out)
    elif t[0] == "!" or t[0] == "?":
        out.append(t[1])


def _projects_participant(t, p):
    """True if participant p appears anywhere in the type node (no recursion var descent)."""
    if t == "end" or isinstance(t, str):
        return False
    if t[0] == "mu":
        return _projects_participant(t[2], p)
    if t[0] == "seq":
        return _projects_participant(t[1], p) or _projects_participant(t[2], p)
    if t[0] == "!" or t[0] == "?":
        return t[1] == p
    return False


def _project(t, p):
    """Project global type node t onto participant p -> ('type', local) or ('error',)."""
    if t == "end":
        return ("type", "end")
    if isinstance(t, str):  # recursion variable
        # The participant occurs in the body (checked by caller), so keep the variable
        return ("type", t)
    if t[0] == "mu":
        if not _projects_participant(t[2], p):
            return ("type", "end")
        body = _project(t[2], p)
        if body[0] == "error":
            return body
        if body[1] == "end":
            return ("type", "end")
        return ("type", f"mu {t[1]}. {body[1]}")
    if t[0] == "seq":
        left = _project(t[1], p)
        if left[0] == "error":
            return left
        right = _project(t[2], p)
        if right[0] == "error":
            return right
        if left[1] == "end":
            return right
        if right[1] == "end":
            return left
        return ("type", f"({left[1]}) . ({right[1]})")
    if t[0] == "!" or t[0] == "?":
        if t[1] == p:
            return ("type", _render(t))
        return ("type", "end")
    raise ValueError(t)


def _linear(depth, ids, pay):
    """Build a non-recursive sequence of interaction nodes (no mu)."""
    if depth <= 0:
        return "end"
    n = random.randint(1, 2)
    nodes = []
    for _ in range(n):
        s = random.choice(ids)
        r = random.choice([x for x in ids if x != s])
        if random.random() < 0.5:
            nodes.append(("!", s, random.choice(pay)))
        else:
            nodes.append(("?", r, random.choice(pay)))
    node = nodes[0]
    rest = _linear(depth - 1, ids, pay)
    return ("seq", node, rest)


def _build(depth, ids, pay):
    """Build a well-formed global type tree.

    Recursion is never nested: a single mu binds one fresh variable that
    appears exactly once, at the tail of a non-empty interaction body, so the
    only cycle runs through the bound variable and projection terminates with a
    non-degenerate body. Every mu body contains at least one interaction.
    """
    if depth < 2:
        return _linear(depth, ids, pay)
    if random.random() < 0.35:
        var = f"X{random.randrange(1000)}"
        body = _linear(depth - 1, ids, pay)
        if body == "end":
            body = ("!", random.choice(ids), random.choice(pay))
        return ("mu", var, ("seq", body, var))
    return _linear(depth, ids, pay)


def _dual(local, target):
    """Return the dual of a rendered local type: swap ! and ? symbols.

    The partner id and payload are unchanged; only the send/receive direction
    flips, which is the standard duality of local session types.
    """
    s = local
    out = []
    i = 0
    while i < len(s):
        if s[i] in "!?":
            out.append("?" if s[i] == "!" else "!")
        else:
            out.append(s[i])
        i += 1
    return "".join(out)


@dataclass
class SessionConfig(Config):
    participants: int = 3
    depth: int = 3

    def apply_difficulty(self, level):
        self.participants = min(8, 3 + level)
        self.depth = 2 + level


class SessionTypeProjection(Task):
    summary = ("Project a global multiparty session type onto one participant endpoint "
               "through send/receive/sequence/mu-recursion, compare the projection with a "
               "given local endpoint under duality, and answer 'equal' or 'not'.")
    config_cls = SessionConfig

    def generate_entry(self):
        npart = self.config.participants
        ids = _PARTICIPANTS[:npart]
        global_type = _build(self.config.depth, ids, _PAYLOADS)
        g_render = _render(global_type)

        # choose a participant that actually occurs in the type
        ids_present = []
        _collect_ids(global_type, ids_present)
        participants = sorted(set(ids_present)) or [random.choice(ids)]
        target = random.choice(participants)

        # compute projection
        proj = _project(global_type, target)
        local = proj[1]
        if random.random() < 0.5:
            given = local
            answer = "equal"
        else:
            # dual is definitely not equal unless local is self-dual (empty/tricky)
            given = _dual(local, target)
            answer = "not"
            if given == local:
                # fall back to a made-up mismatched type
                other_leaf = random.choice([i for i in participants if i != target] or [target])
                given = f"{other_leaf} ! a"
                if given == local:
                    given = "end"
                answer = "not"

        prompt = (
            f"Global multiparty session type over participants {', '.join(sorted(participants))}:\n"
            f"  G = {g_render}\n"
            f"Project G onto the local behaviour of participant {target}. In a global "
            f"type a node 'A ! m' means A sends message m (A projects to a send, others "
            f"skip it); 'B ? m' means B receives message m (B projects to a receive, "
            f"others skip it). Sequence 'T1 . T2' projects to the sequential composition "
            f"of the projections (empty parts dropped). Recursion 'mu X. B' where the "
            f"participant occurs in B projects to 'mu X. Bproj', else it is dropped. "
            f"The claimed local type is:\n"
            f"  L = {given}\n"
            f"Decide whether L is exactly the projection of G onto {target}, as computed "
            f"by these rules. Reply with the single token 'equal' when they coincide and "
            f"the single token 'not' when they differ."
        )

        # verification
        recomputed = _project(global_type, target)[1]
        assert recomputed == local
        if answer == "equal":
            assert given == local
        else:
            assert given != local

        metadata = {
            "participants": list(sorted(participants)),
            "target": target,
            "global": g_render,
            "given_local": given,
            "projection": local,
            "answer": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        participants = metadata["participants"]
        return (
            f"Global multiparty session type over participants {', '.join(sorted(participants))}:\n"
            f"  G = {metadata['global']}\n"
            f"Project G onto the local behaviour of participant {metadata['target']}. In a global "
            f"type a node 'A ! m' means A sends message m (A projects to a send, others "
            f"skip it); 'B ? m' means B receives message m (B projects to a receive, "
            f"others skip it). Sequence 'T1 . T2' projects to the sequential composition "
            f"of the projections (empty parts dropped). Recursion 'mu X. B' where the "
            f"participant occurs in B projects to 'mu X. Bproj', else it is dropped. "
            f"The claimed local type is:\n"
            f"  L = {metadata['given_local']}\n"
            f"Decide whether L is exactly the projection of G onto {metadata['target']}, as computed "
            f"by these rules. Reply with the single token 'equal' when they coincide and "
            f"the single token 'not' when they differ."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip()
        for line in a.splitlines():
            tok = line.strip()
            if tok in ("equal", "not"):
                return 1.0 if tok == entry.metadata["answer"] else 0.0
        return 0.0
