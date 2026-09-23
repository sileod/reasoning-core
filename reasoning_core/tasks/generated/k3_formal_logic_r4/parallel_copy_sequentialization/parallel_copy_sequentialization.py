"""Sequentialize simultaneous parallel copy transfers on registers.

Given a set of simultaneous parallel move (dst := src) transfers -- the kind SSA
destruction emits to put each value where it belongs -- produce a canonical,
call-by-call sequentialization: chains are copied from the far end of the value
flow, two-cycles become swaps, and permutation cycles longer than two rotate
through a single scratch register `t`.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'parallel_copy_sequentialization (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_formal_logic_r4/parallel_copy_sequentialization',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class ParallelCopySequentializationConfig(Config):
    n_regs: int = 5
    max_chain: int = 2
    max_cycle: int = 3

    def apply_difficulty(self, level):
        self.n_regs = int(5 + level)
        self.max_chain = int(2 + level)
        self.max_cycle = int(2 + (level >= 2))


def _r(i):
    return "r%d" % i


def _construct_transfers(n_regs, max_chain, max_cycle, rng):
    """Return an injective partial permutation dst->src (+ a flag scratch_used)
    built from a random mix of component types: value chains, two-cycles and
    longer permutation cycles. Returns (transfers, scratch_used)."""
    for _ in range(600):
        regs = list(range(n_regs))
        rng.shuffle(regs)
        tr = {}
        idx = 0
        n_chain = rng.randrange(0, min(3, max_chain) + 1)
        n_2cyc = rng.randrange(0, 3)
        n_long = rng.randrange(0, 3)
        if n_long and max_cycle < 3:
            n_long = 0
        if n_chain + n_2cyc + n_long == 0:
            n_2cyc = 1
        parts = ["chain"] * n_chain + ["cyc2"] * n_2cyc + ["cycL"] * n_long
        rng.shuffle(parts)
        scratch_used = False
        for p in parts:
            if idx >= n_regs - 1:
                break
            if p == "chain":
                if idx + 2 > n_regs:
                    return tr, scratch_used
                d, s = regs[idx], regs[idx + 1]
                idx += 2
                tr[d] = s
            elif p == "cyc2":
                if idx + 2 > n_regs:
                    return tr, scratch_used
                a, b = regs[idx], regs[idx + 1]
                idx += 2
                tr[a] = b
                tr[b] = a
            else:
                k = rng.choice([3, 4])
                if max_cycle < 3:
                    k = 3
                if idx + k > n_regs:
                    k = n_regs - idx
                if k < 3:
                    return tr, scratch_used
                comp = regs[idx:idx + k]
                idx += k
                for i in range(k):
                    tr[comp[i]] = comp[(i - 1) % k]
                scratch_used = True
        if tr:
            return tr, scratch_used
    raise RuntimeError("could not construct a transfer structure")


def _emit_moves(transfers, n_regs, scratch_used):
    """Emit the canonical ordered move list for an injective partial permutation.

    - Long (>=3) permutation cycles rotate through scratch register t.
    - Two-cycles become swaps (r[a]=r[b]; r[b]=r[a];).
    - Value chains are copied from the far end of the flow so each source stays
      intact until consumed.
    Returns the list of moves (each already ends with ';').
    """
    involved = set(transfers) | set(transfers.values())
    f = {r: transfers.get(r, r) for r in involved}

    seen = set()
    cycles = []
    for start in sorted(involved):
        if start in seen:
            continue
        path = []
        local = set()
        cur = start
        while cur in involved and cur not in local:
            if cur in seen:
                break
            path.append(cur)
            local.add(cur)
            cur = f[cur]
        if cur in local:
            cyc = path[path.index(cur):]
            if len(cyc) >= 2:
                cycles.append(cyc)
            seen.update(path)
        else:
            seen.update(path)

    cycle_regs = set(c for cyc in cycles for c in cyc)
    moves = []
    for cyc in cycles:
        cyc = list(cyc)
        si = cyc.index(min(cyc))
        cyc = cyc[si:] + cyc[:si]
        if len(cyc) == 2:
            a, b = cyc
            moves.append("%s=%s;" % (_r(a), _r(b)))
            moves.append("%s=%s;" % (_r(b), _r(a)))
        else:
            moves.append("t=%s;" % _r(cyc[0]))
            for i in range(len(cyc) - 1):
                moves.append("%s=%s;" % (_r(cyc[i]), _r(cyc[i + 1])))
            moves.append("%s=t;" % _r(cyc[-1]))
            scratch_used = True

    def depth(r):
        d = 0
        walked = set()
        while f[r] != r and r not in walked:
            walked.add(r)
            r = f[r]
            d += 1
        return d

    chain_dsts = [d for d in transfers if d not in cycle_regs]
    for d in sorted(chain_dsts, key=lambda x: -depth(x)):
        moves.append("%s=%s;" % (_r(d), _r(transfers[d])))
    return moves, scratch_used


def _verify(transfers, moves, n_regs):
    val = {i: i for i in range(n_regs)}
    val[n_regs] = -1
    for m in moves:
        if isinstance(m, tuple):
            a, b = m
        else:
            m = m.rstrip(";")
            a, b = m.split("=")
        da = n_regs if a == "t" else int(a[1:])
        sb = n_regs if b == "t" else int(b[1:])
        val[da] = val[sb]
    for d, s in transfers.items():
        if val[d] != s:
            return False
    return True


class ParallelCopySequentialization(Task):
    summary = (
        "Sequentialize simultaneous dst:=src transfers on SSA-destruction edges: "
        "emit ordered moves, swaps for two-cycles, one scratch register for longer "
        "permutation cycles; answers are the emitted move list or a temp's contents."
    )
    design_choice = (
        "Answer format: emit the full ordered move list as a canonical string like "
        "'r1=r2; r3=r1;' with registers numbered from the input graph, or answer "
        "only the final contents of a designated scratch register as an integer."
    )
    config_cls = ParallelCopySequentializationConfig
    task_version = 2

    def generate_entry(self):
        n_regs = self.config.n_regs
        for _ in range(200):
            transfers, scratch_used = _construct_transfers(
                n_regs, self.config.max_chain, self.config.max_cycle, random
            )
            moves, scratch_used = _emit_moves(transfers, n_regs, scratch_used)
            if _verify(transfers, moves, n_regs):
                edges = sorted(
                    "%s:=%s" % (_r(d), _r(s)) for d, s in transfers.items()
                )
                answer = "".join(moves).rstrip(";")
                metadata = {
                    "n_regs": n_regs,
                    "transfers": edges,
                    "scratch_used": bool(scratch_used),
                }
                return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("could not build a verified instance")

    def render_prompt(self, metadata):
        n_regs = metadata["n_regs"]
        lines = [
            "Parallel copy problem. Registers are numbered "
            "r0 through r%d (exactly %d registers)." % (n_regs - 1, n_regs),
            "Simultaneously, as one parallel step, the following transfers must "
            "happen; each 'dst:=src' means the value currently in src is to end up "
            "in dst:",
        ]
        for e in metadata["transfers"]:
            lines.append(e)
        lines.append(
            "Sequentialize these into ordinary single-register move instructions "
            "(each move writes exactly one register, 'a=b' copies b's current value "
            "into a). You may use one scratch register t, initially holding garbage; "
            "a value is only safe to overwrite once every copy that still needs it "
            "has read it. Use a swap for any two-cycle and t for any longer "
            "permutation cycle."
        )
        lines.append(
            "Answer with ONLY the ordered move list as one canonical string, "
            "register numbers as in the input, scratch written as 't', each move "
            "semicolon-terminated with no spaces, e.g. 'r1=r2;r3=r1;'. No prose."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip().replace(" ", "")
        gold = entry.answer
        if a == gold:
            return 1.0
        moves = _parse_moves(a)
        if not moves:
            return 0.0
        n_regs = entry.metadata["n_regs"]
        transfers = {}
        for e in entry.metadata["transfers"]:
            d, s = e.split(":=")
            transfers[int(d[1:])] = int(s[1:])
        return 1.0 if _verify(transfers, moves, n_regs) else 0.0


def _parse_moves(s):
    if not s:
        return None
    parts = s.split(";")
    moves = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if "=" not in p:
            return None
        a, b = p.split("=")
        a = a.strip()
        b = b.strip()
        for var in (a, b):
            if var == "t":
                continue
            if var.startswith("r") and var[1:].isdigit():
                continue
            return None
        moves.append((a, b))
    return moves
