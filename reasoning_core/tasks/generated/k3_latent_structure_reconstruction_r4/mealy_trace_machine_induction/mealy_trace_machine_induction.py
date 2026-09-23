import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

_INPUTS = ("a", "b")
_OUTPUTS = ("0", "1")


@dataclass
class MealyTraceMachineInductionV1Config(Config):
    n_states: int = 2
    seed: int = 0

    def apply_difficulty(self, level):
        self.n_states = stochastic_rounding(2 + 1.2 * level)


def _reachable(states, next_f, init):
    seen = {init}
    stack = [init]
    while stack:
        q = stack.pop()
        for i in _INPUTS:
            nxt = next_f[q][i]
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return sorted(seen)


def _partition_refinement(states, next_f, out_f):
    """Partition refinement minimization of a Mealy machine over `states`."""
    sig = {q: tuple(int(out_f[q][i]) for i in _INPUTS) for q in states}
    classes = {}
    for q in states:
        classes.setdefault(sig[q], []).append(q)
    partition = [frozenset(c) for c in classes.values()]
    while True:
        index = {}
        for ci, c in enumerate(partition):
            for q in c:
                index[q] = ci
        groups = {}
        for c in partition:
            for q in sorted(c):
                key = (sig[q], tuple(index[next_f[q][i]] for i in _INPUTS))
                groups.setdefault(key, []).append(q)
        new_partition = [frozenset(g) for g in groups.values()]
        if len(new_partition) == len(partition):
            return sorted(new_partition, key=min)
        partition = new_partition


def _reach(h, next_f, init):
    q = init
    for c in h:
        q = next_f[q][c]
    return q


def _suffix_output(s, e, next_f, out_f):
    q = s
    out_last = None
    for c in e:
        out_last = out_f[q][c]
        q = next_f[q][c]
    return out_last


def _distinguishing_string(s1, s2, next_f, out_f):
    """Shortest input string (a<b lex) whose last-step output differs at s1/s2."""
    from collections import deque
    seen = {(s1, s2)}
    q = deque([(s1, s2, "")])
    while q:
        a, b, path = q.popleft()
        for i in _INPUTS:
            oa = out_f[a][i]
            ob = out_f[b][i]
            np_ = path + i
            if oa != ob:
                return np_
            na = next_f[a][i]
            nb = next_f[b][i]
            if (na, nb) not in seen:
                seen.add((na, nb))
                q.append((na, nb, np_))
    return None


def _shortest_history_per_state(states, next_f, init):
    """BFS from init; returns dict state -> shortest (by len, then lex) history."""
    hist = {init: ""}
    frontier = [init]
    while frontier:
        nxt_frontier = []
        for q in frontier:
            for i in _INPUTS:
                r = next_f[q][i]
                cand = hist[q] + i
                if r not in hist or (
                    len(cand) == len(hist[r]) and cand < hist[r]
                ):
                    hist[r] = cand
                    if r not in nxt_frontier:
                        nxt_frontier.append(r)
        frontier = nxt_frontier
    return hist


def _make_table(mstates_partition, next_f, out_f, init):
    """Build a closed, consistent, distinguishing observation table over the
    minimal reachable machine. Each minimal state (partition class) gets one
    representative history; the suffix set E is grown until every class has a
    distinct row signature."""
    state_index = {}
    for ci, c in enumerate(mstates_partition):
        for q in c:
            state_index[q] = ci
    reachable = [q for c in mstates_partition for q in c]
    hist = _shortest_history_per_state(reachable, next_f, init)

    reps = []
    for c in mstates_partition:
        members = sorted(c)
        best = None
        for member in members:
            h = hist[member]
            if best is None or (len(h), h) < (len(best), best):
                best = h
        reps.append(best)

    E = list(_INPUTS)
    guardian = 0
    while guardian < 500:
        guardian += 1
        sig = {}
        for ci, c in enumerate(mstates_partition):
            s = _reach(reps[ci], next_f, init)
            sig[ci] = tuple(int(_suffix_output(s, e, next_f, out_f)) for e in E)
        groups = {}
        for ci, sval in sig.items():
            groups.setdefault(sval, []).append(ci)
        collision = None
        for sval, cis in groups.items():
            if len(cis) > 1:
                collision = cis
                break
        if collision is None:
            break
        c1, c2 = collision[0], collision[1]
        s1 = _reach(reps[c1], next_f, init)
        s2 = _reach(reps[c2], next_f, init)
        ds = _distinguishing_string(s1, s2, next_f, out_f)
        if ds is not None and ds not in E:
            E.append(ds)

    order = sorted(range(len(reps)), key=lambda ci: (len(reps[ci]), reps[ci]))
    H = [reps[ci] for ci in order]
    T = {}
    for h in H:
        s = _reach(h, next_f, init)
        T[h] = [int(_suffix_output(s, e, next_f, out_f)) for e in E]
    return {"H": H, "E": E, "T": T}


class MealyTraceMachineInduction(Task):
    summary = (
        "Infer a hidden Mealy machine from input/output transcripts by merging "
        "histories with agreeing futures and propagating table entries; answer the "
        "minimized machine, the reply to a fresh input, or the earliest "
        "underdetermined step."
    )
    design_choice = (
        "Answer the minimized machine as an explicit transition table with canonical "
        "state names, requiring the solver to output the full mapping for all inputs."
    )
    config_cls = MealyTraceMachineInductionV1Config

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_states
        states = list(range(n))
        next_f = {q: {i: random.randrange(n) for i in _INPUTS} for q in states}
        out_f = {q: {i: random.choice(_OUTPUTS) for i in _INPUTS} for q in states}

        init = 0
        reachable = _reachable(states, next_f, init)
        partition = _partition_refinement(reachable, next_f, out_f)
        table = _make_table(partition, next_f, out_f, init)
        gold = _machine_to_answer(table, next_f, out_f, init)
        _verify(table, gold, next_f, out_f, init, partition)
        metadata = {
            "n_states": n,
            "sigma": list(_INPUTS),
            "outputs": list(_OUTPUTS),
            "m": len(partition),
            "H": table["H"],
            "E": table["E"],
            "T": table["T"],
            "answer_rows": gold["answer_rows"],
        }
        return Entry(metadata=metadata, answer=gold["text"])

    def render_prompt(self, metadata):
        H = metadata["H"]
        E = metadata["E"]
        T = metadata["T"]
        lines = []
        lines.append(
            "A hidden Mealy machine has input alphabet {a, b} and output alphabet "
            "{0, 1}. It starts from its initial state and we record its input/output "
            "behavior in the observation table below. Each row is a history string "
            "(the inputs fed so far from the start); each column is a distinguishing "
            "suffix string; the cell at (history, suffix) is the output bit the "
            "machine emits as its last step when the suffix is fed immediately after "
            "that history."
        )
        lines.append("")
        lines.append("Observation table (rows: histories, columns: suffixes):")
        lines.append("history" + "".join(f"{'  ' + e:>5}" for e in E))
        for h in H:
            row = f"{h or 'eps':<7}"
            for e in E:
                row += f"{T[h][E.index(e)]:>5}"
            lines.append(row)
        lines.append("")
        lines.append(
            "Two histories lead to the same state iff their rows agree in every "
            "column (their futures agree). Merge equal rows: the minimized machine "
            "has one state per equivalence class. For a merged state v with "
            "representative history h, on input x it emits cell T[h][x] and moves to "
            "the state whose class contains the row indexed by h+x (propagate: look "
            "up h+x's row and merge by it too). The table distinguishes every pair "
            "of states and stays closed under appending one input, so this yields a "
            "well-defined minimized machine."
        )
        lines.append("")
        lines.append(
            "Name states canonically: within each equivalence class take the "
            "lexicographically smallest history (shorter strings first, equal-length "
            "strings in a<b order); order the representatives the same way and call "
            "them q0, q1, ... in that order."
        )
        lines.append("")
        lines.append(
            "Give the completed minimized machine as an explicit transition table "
            "covering every state and every input, in the exact format "
            "`q0 --a--> q1/0 ; q0 --b--> q2/1 ; q1 --a--> ...`, states in order q0, "
            "q1, ..., and within each state input a then b; each entry is "
            "`qk --i--> qm/o` with qk the current state, i the input, qm the next "
            "state, o the output bit. Output only the table, nothing else."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = {}
        for r in entry.metadata["answer_rows"]:
            gold[(r[0], r[1])] = (r[2], r[3])
        user = _parse_answer(answer)
        if user is None:
            return 0.0
        if set(user.keys()) != set(gold.keys()):
            return 0.0
        for k, v in gold.items():
            if user.get(k) != v:
                return 0.0
        return 1.0


def _row_sig(h, E, next_f, out_f, init):
    s = _reach(h, next_f, init)
    return tuple(int(_suffix_output(s, e, next_f, out_f)) for e in E)


def _machine_to_answer(table, next_f, out_f, init):
    H = table["H"]
    E = table["E"]
    T = table["T"]
    classes = {}
    for h in H:
        sig = tuple(T[h])
        classes.setdefault(sig, []).append(h)
    reps = {sig: min(hs, key=lambda h: (len(h), h)) for sig, hs in classes.items()}
    order = sorted(reps.values(), key=lambda h: (len(h), h))
    name = {h: f"q{i}" for i, h in enumerate(order)}
    answer_rows = []
    for h in order:
        s = _reach(h, next_f, init)
        for a in _INPUTS:
            o = out_f[s][a]
            sig_hpa = _row_sig(h + a, E, next_f, out_f, init)
            rep_next = reps[sig_hpa]
            answer_rows.append((name[h], a, name[rep_next], o))
    answer_rows.sort(key=lambda r: (int(r[0][1:]), ("a", "b").index(r[1])))
    text = " ; ".join(f"{r[0]} --{r[1]}--> {r[2]}/{r[3]}" for r in answer_rows)
    return {"text": text, "answer_rows": answer_rows}


def _verify(table, gold, next_f, out_f, init, partition):
    H = table["H"]
    E = table["E"]
    T = table["T"]
    index = {}
    for ci, c in enumerate(partition):
        for q in c:
            index[q] = ci
    classes = {}
    for h in H:
        sig = tuple(T[h])
        classes.setdefault(sig, []).append(h)
    reps = {sig: min(hs, key=lambda h: (len(h), h)) for sig, hs in classes.items()}
    order = sorted(reps.values(), key=lambda h: (len(h), h))
    name = {h: f"q{i}" for i, h in enumerate(order)}
    gold_map = {(r[0], r[1]): (r[2], r[3]) for r in gold["answer_rows"]}
    for h in order:
        s = _reach(h, next_f, init)
        for a in _INPUTS:
            o = out_f[s][a]
            sig_hpa = _row_sig(h + a, E, next_f, out_f, init)
            if sig_hpa not in reps:
                raise RuntimeError("table not closed")
            sn_rep = reps[sig_hpa]
            sn = next_f[s][a]
            assert index[_reach(sn_rep, next_f, init)] == index[sn], (
                "transition target class mismatch"
            )
            assert o == gold_map[(name[h], a)][1], "transition output mismatch"


def _parse_answer(answer):
    try:
        if not isinstance(answer, str):
            return None
        pat = re.compile(r"(q\d+)\s*--([ab])\s*-->\s*(q\d+)\s*/\s*([01])")
        out = {}
        for m in pat.finditer(answer):
            qk, i, qm, o = m.group(1), m.group(2), m.group(3), m.group(4)
            out[(qk, i)] = (qm, o)
        return out
    except Exception:
        return None


TASK_META = {'parent_source_id': None,
 'idea': 'mealy_trace_machine_induction (variant 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_latent_structure_reconstruction_r4/mealy_trace_machine_induction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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
