import ast
import random
import string
from dataclasses import dataclass

from reasoning_core.template import Config, Problem, Task, edict


ALPHA = string.ascii_lowercase[:8]
WORDS = "nova river amber delta orbit pixel quiet signal vector winter".split()


@dataclass
class StringTransductionConfig(Config):
    length: int = 8
    n_ops: int = 2
    alphabet_size: int = 5
    edit_ops: int = 3
    edit_rate: float = 0.25

    def update(self, c=1):
        self.length += 2 * c
        self.n_ops += c
        self.alphabet_size = min(8, self.alphabet_size + int(c >= 2))
        self.edit_ops += c


def caesar(s, k):
    return "".join(chr(97 + (ord(c) - 97 + k) % 26) if c.isalpha() else c for c in s)


def rotate(s, k):
    if not s:
        return s
    k %= len(s)
    return s[k:] + s[:k]


def dedupe(s):
    out = []
    for c in s:
        if not out or out[-1] != c:
            out.append(c)
    return "".join(out)


def apply_edits(s, edits):
    xs = list(s)
    for op, i, x in edits:
        i = max(0, min(i, len(xs)))
        if op == "insert":
            xs.insert(i, x)
        elif op == "delete" and i < len(xs):
            del xs[i]
        elif op == "replace" and i < len(xs):
            xs[i] = x
    return "".join(xs)


class StringTransduction(Task):
    def __init__(self, config=StringTransductionConfig()):
        super().__init__(config=config)

    def _program(self, alphabet):
        r, k = random.randint(1, 3), random.randint(1, 5)
        ops = [
            ("reverse", lambda s: s[::-1]),
            ("sort ascending", lambda s: "".join(sorted(s))),
            ("sort descending", lambda s: "".join(sorted(s, reverse=True))),
            ("dedupe adjacent repeats", dedupe),
            (f"rotate left by {r}", lambda s, r=r: rotate(s, r)),
            (f"caesar shift by {k}", lambda s, k=k: caesar(s, k)),
        ]
        a, b = random.sample(alphabet, 2)
        ops += [
            (f"replace {a} with {b}", lambda s, a=a, b=b: s.replace(a, b)),
            (f"keep only {a} and {b}", lambda s, a=a, b=b: "".join(c for c in s if c in {a, b})),
        ]
        return random.sample(ops, max(1, int(self.config.n_ops)))

    def _edits(self, s, alphabet):
        edits, xs = [], list(s)
        for _ in range(max(1, int(self.config.edit_ops))):
            op = random.choice(["insert", "delete", "replace"])
            if not xs:
                op = "insert"
            i = random.randrange(len(xs) + (op == "insert"))
            x = random.choice(alphabet)
            edits.append((op, i, x))
            xs = list(apply_edits("".join(xs), [edits[-1]]))
        return edits

    def generate(self):
        for _ in range(20):
            alphabet = ALPHA[: self.config.alphabet_size]
            mode = "edit" if random.random() < self.config.edit_rate else "program"
            if mode != "edit" and random.random() < 0.25:
                xs = random.sample(WORDS, random.randint(4, min(8, len(WORDS))))
                source = " ".join(xs)
            else:
                source = "".join(random.choice(alphabet) for _ in range(self.config.length))

            if mode == "edit":
                edits = self._edits(source, alphabet)
                target = apply_edits(source, edits)
                meta = edict(mode=mode, source=source, edits=edits)
            else:
                program = self._program(alphabet)
                target = source
                for _, f in program:
                    target = f(target)
                meta = edict(mode=mode, source=source, ops=[name for name, _ in program])
            target = target.strip()  # word-source ops (e.g. sort) push the join spaces to an
            if target:                # end; drop that leading/trailing whitespace (scorer strips too)
                return Problem(meta, target)
        raise RuntimeError("failed to generate nonempty string transduction")

    def prompt(self, m):
        if m.mode == "edit":
            lines = []
            for op, i, x in m.edits:
                lines.append(f"- insert {x} at index {i}" if op == "insert" else f"- delete at index {i}" if op == "delete" else f"- replace index {i} with {x}")
            return f"String: {m.source}\nEdits:\n" + "\n".join(lines) + "\nAnswer with the final string."
        return f"String: {m.source}\nOperations:\n" + "\n".join(f"- {x}" for x in m.ops) + "\nAnswer with the final string."

    def score_answer(self, answer, entry):
        return float(str(answer).strip() == str(entry.answer).strip())
