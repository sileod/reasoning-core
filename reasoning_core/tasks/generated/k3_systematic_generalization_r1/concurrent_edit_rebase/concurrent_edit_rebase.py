"""Rebase one concurrent insert/delete edit onto another over an indexed buffer.

Two edits A (priority, applied first) and B (incoming, to be rebased) are both
expressed against the original 0-indexed buffer.  A single edit is either an
insertion of k items before some index, or a deletion of a contiguous range
[a, b).  We transform B onto A producing Bp, and report the transformed insert
position / delete range, or an explicit no-op when B has no surviving effect
after A.  Every generated answer is verified by simulating both application
orders on the item-identity buffer and asserting the resulting documents match.
"""
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, edict


@dataclass
class ConcurrentEditRebaseConfig(Config):
    n: int = 5
    max_k: int = 1
    max_attempts: int = 200

    def apply_difficulty(self, level):
        self.n = 5 + 2 * level
        self.max_k = 1 + (level + 1) // 2
        self.max_attempts = 200 + 50 * level


def _apply_pos(op, buf):
    """Apply an op by current buffer position. op = ('ins', pos, block) | ('del', a, b)."""
    if op[0] == "ins":
        pos, block = op[1], op[2]
        return buf[:pos] + block + buf[pos:]
    a, b = op[1], op[2]
    return buf[:a] + buf[b:]


def _apply_id_ins(buf, target, block):
    """Insert block immediately before the original item with id ``target`` (append if absent)."""
    idx = None
    for i, e in enumerate(buf):
        if e == target:
            idx = i
            break
    if idx is None:
        idx = len(buf)
    return buf[:idx] + block + buf[idx:]


def _apply_id_del(buf, a, b):
    """Delete every original item whose id lies in [a, b); inserted markers survive."""
    return [e for e in buf if not (isinstance(e, int) and a <= e < b)]


def _rebase(A, B):
    """Rebase edit B onto edit A. Returns ('ins', pos, k), ('del', a, b) or None for no-op.

    A, B are ('ins', pos, k) or ('del', a, b) in original coordinates.
    """
    ta, tb = A[0], B[0]
    if ta == "ins" and tb == "ins":
        pA, kA, pB, kB = A[1], A[2], B[1], B[2]
        return ("ins", pB if pB < pA else pB + kA, kB)
    if ta == "ins" and tb == "del":
        pA, kA, a, b = A[1], A[2], B[1], B[2]
        return ("del", a + (kA if a >= pA else 0), b + (kA if b >= pA else 0))
    if ta == "del" and tb == "ins":
        aA, bA, pB, kB = A[1], A[2], B[1], B[2]
        if pB <= aA:
            return ("ins", pB, kB)
        if pB >= bA:
            return ("ins", pB - (bA - aA), kB)
        return None
    aA, bA, aB, bB = A[1], A[2], B[1], B[2]
    ov = lambda lo, hi: max(0, min(bA, hi) - max(aA, lo))
    s = aB - ov(0, aB)
    e = bB - ov(0, bB)
    if s == e:
        return None
    return ("del", s, e)


def _noop_valid(A, B):
    """True iff B genuinely has no surviving effect after A (so 'no-op' is the answer)."""
    ta, tb = A[0], B[0]
    if ta == "del" and tb == "ins":
        aA, bA, pB = A[1], A[2], B[1]
        return aA < pB < bA
    if ta == "del" and tb == "del":
        aA, bA, aB, bB = A[1], A[2], B[1], B[2]
        return aA <= aB and bB <= bA
    return False


def _gen_op(n, max_k, kind):
    if kind == "ins":
        return ("ins", random.randint(0, n), random.randint(1, max_k))
    a = random.randint(0, n - 1)
    b = random.randint(a + 1, n)
    return ("del", a, b)


def _norm(text):
    return " ".join(str(text or "").strip().split()).lower()


class ConcurrentEditRebase(Task):
    """Rebase a concurrent insert/delete edit onto a priority base edit."""

    summary = ("Rebase concurrent insert/delete edits over an indexed buffer across priority and "
               "type combinations, returning the transformed position and range or an explicit no-op.")
    config_cls = ConcurrentEditRebaseConfig
    task_version = 2

    def _build(self):
        cfg = self.config
        n = random.randint(4, cfg.n)
        ta = random.choice(("ins", "del"))
        tb = random.choice(("ins", "del"))
        A = _gen_op(n, cfg.max_k, ta)
        B = _gen_op(n, cfg.max_k, tb)
        if ta == "ins" and tb == "del" and B[1] < A[1] < B[2]:
            return None
        Bp = _rebase(A, B)
        if Bp is None:
            if not _noop_valid(A, B):
                return None
            answer = "no-op"
        else:
            S = list(range(n))
            if ta == "ins":
                buf1 = _apply_pos(("ins", A[1], ["A%d" % j for j in range(A[2])]), S)
            else:
                buf1 = _apply_pos(("del", A[1], A[2]), S)
            if Bp[0] == "ins":
                bp = ("ins", Bp[1], ["B%d" % j for j in range(Bp[2])])
            else:
                bp = ("del", Bp[1], Bp[2])
            buf1 = _apply_pos(bp, buf1)
            S2 = list(range(n))
            if tb == "ins":
                buf2 = _apply_pos(("ins", B[1], ["B%d" % j for j in range(B[2])]), S2)
            else:
                buf2 = _apply_pos(("del", B[1], B[2]), S2)
            if ta == "ins":
                buf2 = _apply_id_ins(buf2, A[1], ["A%d" % j for j in range(A[2])])
            else:
                buf2 = _apply_id_del(buf2, A[1], A[2])
            if buf1 != buf2:
                return None
            if Bp[0] == "ins":
                answer = "insert %d" % Bp[1]
            else:
                answer = "delete %d %d" % (Bp[1], Bp[2])
        return (n, A, B, answer)

    def generate_entry(self):
        cfg = self.config
        for _ in range(cfg.max_attempts):
            built = self._build()
            if built is not None:
                n, A, B, answer = built
                meta = edict({
                    "n": n,
                    "A": list(A),
                    "B": list(B),
                    "answer": answer,
                    "payload": {
                        "length": "buffer length N = %d" % n,
                        "base": "base edit A (priority, applied first): " + _describe(A),
                        "incoming": "incoming edit B (to rebase onto A): " + _describe(B),
                    },
                })
                return Entry(metadata=meta, answer=answer)
        raise RuntimeError(
            "Could not build a concurrent edit rebase instance after %d attempts "
            "(n=%d)" % (self.config.max_attempts, self.config.n))

    def render_prompt(self, metadata):
        p = metadata["payload"]
        return (
            "You are rebasing one concurrent edit onto another over an indexed buffer.\n"
            "\n"
            "A buffer has N items with indices 0..N-1. An edit is one of:\n"
            "  - \"insert k before index i\": inserts k new items immediately before the current "
            "item i (i=N appends at the end);\n"
            "  - \"delete [a, b)\": removes the current items a, a+1, ..., b-1.\n"
            "\n"
            "Two edits A and B are each specified against the ORIGINAL buffer, before either is "
            "applied. Edit A has priority and is applied first. Rebase B onto A: produce the "
            "edit Bp against the post-A buffer so that applying A and then Bp yields the same "
            "document as both edits taking effect.\n"
            "\n"
            "Tie-break: when B inserts at the exact same position as A's insert, place Bp's "
            "insertion after A's newly inserted block.\n"
            "\n"
            "Report Bp in exactly one of these forms:\n"
            "  - \"insert P\"       (the new insertion position P)\n"
            "  - \"delete A B\"     (the new range [a, b))\n"
            "  - \"no-op\"          (B has no surviving effect after A)\n"
            "\n"
            "%s\n"
            "%s\n"
            "%s\n"
            "\n"
            "What is the rebased edit Bp?" % (p["length"], p["base"], p["incoming"])
        )

    def score_answer(self, answer, entry):
        ok = _norm(answer) == _norm(entry.answer)
        if not ok:
            return 0.0
        ref = _norm(entry.answer)
        if ref == "no-op":
            return 1.0
        if ref.startswith("insert") or ref.startswith("delete"):
            return 1.0
        return 0.0


def _describe(op):
    if op[0] == "ins":
        return "insert %d before index %d" % (op[2], op[1])
    return "delete [%d, %d)" % (op[1], op[2])


TASK_META = {'parent_source_id': None,
 'idea': 'concurrent_edit_rebase (draw 3 of 3, unguided baseline)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_systematic_generalization_r1/concurrent_edit_rebase',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1618848011,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
