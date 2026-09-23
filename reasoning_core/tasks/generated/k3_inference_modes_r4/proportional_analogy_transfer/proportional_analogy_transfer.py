"""Proportional analogy transfer across strings, tuples, and small grids.

For each instance the task draws a domain (string / tuple / grid), a deterministic
operation from that domain's fixed parameterless family, a source A, a seed B = op(A),
and (in term mode) a probe C. The operation is verified to be the UNIQUE family member
mapping A to B, so the analogy is unambiguous. In term mode the model must apply that
operation to C and emit the missing term; in name mode it must name the operation.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

DOMAINS = ("string", "tuple", "grid")

# ---------------------------------------------------------------------------
# Operation families (parameterless, deterministic, uniquely nameable)
# ---------------------------------------------------------------------------


def _string_ops():
    return {
        "reverse": lambda s: s[::-1],
        "swap_ends": lambda s: s[-1] + s[1:-1] + s[0],
        "rotl": lambda s: s[1:] + s[0],
        "rotr": lambda s: s[-1] + s[:-1],
        "double": lambda s: s + s,
        "sort": lambda s: "".join(sorted(s)),
        "upper": lambda s: s.upper(),
        "drop_first": lambda s: s[1:],
    }


def _tuple_ops():
    return {
        "reverse": lambda t: t[::-1],
        "rotl": lambda t: t[1:] + t[:1],
        "rotr": lambda t: t[-1:] + t[:-1],
        "negate": lambda t: tuple(-x for x in t),
        "square": lambda t: tuple(x * x for x in t),
        "absolute": lambda t: tuple(abs(x) for x in t),
        "increment": lambda t: tuple(x + 1 for x in t),
        "decrement": lambda t: tuple(x - 1 for x in t),
    }


def _grid_ops():
    return {
        "hflip": lambda g: [row[::-1] for row in g],
        "vflip": lambda g: g[::-1],
        "transpose": lambda g: [list(col) for col in zip(*g)],
        "rot90": lambda g: [list(col)[::-1] for col in zip(*g)],
        "rot180": lambda g: [row[::-1] for row in g[::-1]],
        "rot270": lambda g: [list(col) for col in zip(*g)][::-1],
    }


def _op_family(domain):
    if domain == "string":
        return _string_ops()
    if domain == "tuple":
        return _tuple_ops()
    return _grid_ops()


# ---------------------------------------------------------------------------
# Rendering helpers (shared between prompt and answer, so they stay consistent)
# ---------------------------------------------------------------------------


def _render_domain_value(domain, value):
    if domain == "string":
        return value
    if domain == "tuple":
        return " ".join(str(x) for x in value)
    return " | ".join(" ".join(str(c) for c in row) for row in value)


def _present(domain, value):
    """How an A/B/C value is shown inline in the prompt text."""
    if domain == "string":
        return repr(value)
    return _render_domain_value(domain, value)


def _family_names(domain):
    return sorted(_op_family(domain).keys())


def _format_desc(domain):
    if domain == "string":
        return "a lowercase or uppercase alphabetic string"
    if domain == "tuple":
        return "a space-separated list of integers"
    return "rows joined by ' | ', cells space-separated"


# ---------------------------------------------------------------------------
# Instance construction
# ---------------------------------------------------------------------------


def _make_source(domain, size, r):
    if domain == "string":
        alphabet = "abcdefghijklm"
        base = "".join(r.choice(alphabet) for _ in range(size))
        return base, base
    if domain == "tuple":
        tup = tuple(r.randint(-2, 2) for _ in range(size))
        return tup, tup
    g = [[r.randint(0, 2) for _ in range(size)] for _ in range(size)]
    return g, g


def _unique_op(domain, op_name, A):
    """Return True if op_name is the unique family member mapping A to op(A)."""
    fam = _op_family(domain)
    wanted = fam[op_name](A)
    for other, fn in fam.items():
        if other != op_name and fn(A) == wanted:
            return False
    return True


# ---------------------------------------------------------------------------
# Scoring (module-level; score_answer must not touch self)
# ---------------------------------------------------------------------------


def _score(answer, entry):
    gold = str(entry.answer)
    return 1 if str(answer).strip() == str(gold).strip() else 0


# ---------------------------------------------------------------------------
# Config and Task
# ---------------------------------------------------------------------------


@dataclass
class AnalogTransferConfig(Config):
    base_size: int = 3

    def apply_difficulty(self, level):
        self.base_size = 3 + level


class ProportionalAnalogyTransfer(Task):
    summary = (
        "Proportional analogies A:B::C:? over strings, tuples, and small grids: "
        "induce a unique deterministic transformation from the A:B pair, apply it to "
        "C, and answer the missing term or that transform's name."
    )
    config_cls = AnalogTransferConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        for _ in range(200):
            domain = random.choice(DOMAINS)
            size = 2 + random.randrange(cfg.base_size, cfg.base_size + 2)
            if domain == "grid":
                size = max(2, min(4, size // 1))

            A, _ = _make_source(domain, size, random)
            fam = _op_family(domain)
            op_name = random.choice(sorted(fam))
            B = fam[op_name](A)

            if not _unique_op(domain, op_name, A):
                continue

            mode = "term" if random.random() < 0.55 else "name"

            if mode == "name":
                entry = Entry(
                    metadata={
                        "domain": domain,
                        "mode": "name",
                        "A": A,
                        "B": B,
                        "op": op_name,
                    },
                    answer=op_name,
                )
            else:
                C, _ = _make_source(domain, size, random)
                gold = fam[op_name](C)
                if gold == C or _render_domain_value(domain, gold) == _render_domain_value(domain, B):
                    continue
                entry = Entry(
                    metadata={
                        "domain": domain,
                        "mode": "term",
                        "A": A,
                        "B": B,
                        "C": C,
                        "op": op_name,
                        "gold": gold,
                    },
                    answer=_render_domain_value(domain, gold),
                )
            return entry
        raise RuntimeError("could not construct an unambiguous analogy")

    def render_prompt(self, metadata):
        domain = metadata.domain
        family = ", ".join(_family_names(domain))
        if metadata.mode == "name":
            return (
                f"My {domain} source A = {_present(domain, metadata.A)} became "
                f"B = {_present(domain, metadata.B)} after applying exactly one of the "
                f"operations [{family}]. Which operation was applied to A to produce B? "
                f"Answer with that operation's name from the list."
            )
        return (
            f"Complete this proportional analogy. The transformation mapping "
            f"A = {_present(domain, metadata.A)} to B = {_present(domain, metadata.B)} "
            f"is exactly one of the operations [{family}]. Apply that same operation to "
            f"C = {_present(domain, metadata.C)}. What is the missing term "
            f"C transformed so that A:B :: C:? ? Give the result as {_format_desc(domain)}."
        )

    def score_answer(self, answer, entry):
        return _score(answer, entry)


TASK_META = {'parent_source_id': None,
 'idea': 'proportional_analogy_transfer (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_inference_modes_r4/proportional_analogy_transfer',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1140349348,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
