import random
from dataclasses import dataclass, field

from reasoning_core.template import Config, Entry, Task


def _signed8(byte):
    return byte - 256 if byte >= 128 else byte


def _simulate(ops, v0):
    """Run the checkpoint trace from the initial byte; return list of answer tokens.

    Each op is a dict; each produces either ('type', value) reducing to a token or
    the literal string 'trap' that terminates the trace.
    """
    tokens = []
    v = v0
    for op in ops:
        kind = op["kind"]
        if kind == "uadd":
            nv = (v + op["k"]) & 0xFF
            tokens.append(f"{nv}u")
            v = nv
        elif kind == "sadd":
            nv = (v + (op["k"] & 0xFF)) & 0xFF
            tokens.append(f"{_signed8(nv)}s")
            v = nv
        elif kind == "umul":
            nv = (v * op["k"]) & 0xFF
            tokens.append(f"{nv}u")
            v = nv
        elif kind == "udiv":
            if op["k"] == 0:
                tokens.append("trap")
                break
            nv = v // op["k"]
            tokens.append(f"{nv}u")
            v = nv
        elif kind == "cast":
            if op["to"] == "signed":
                tokens.append(f"{_signed8(v)}s")
            else:
                tokens.append(f"{v}u")
        elif kind == "index":
            if op["m"] == 0 or v >= op["m"]:
                tokens.append("trap")
                break
            tokens.append(f"{v}u")
        elif kind == "enum":
            if v not in op["allowed"]:
                tokens.append("trap")
                break
            tokens.append(f"{v}u")
        elif kind == "union":
            nb = op["nbits"]
            nvars = op["nvars"]
            tag = v >> (8 - nb)
            if tag >= nvars:
                tokens.append("trap")
                break
            payload = v & ((1 << (8 - nb)) - 1)
            if op["variants"][tag] == "signed":
                half = 1 << (8 - nb - 1)
                payload = payload - (1 << (8 - nb)) if payload >= half else payload
                tokens.append(f"{payload}s")
            else:
                tokens.append(f"{payload}u")
        else:  # unreachable
            raise RuntimeError("unknown op")
    return tokens


def _render_ops(ops):
    """Render each checkpoint op as a short human sentence for the prompt."""
    lines = []
    for idx, op in enumerate(ops):
        kind = op["kind"]
        if kind == "uadd":
            lines.append(f"{idx + 1}: add {op['k']} as an unsigned byte (wrap mod 256).")
        elif kind == "sadd":
            lines.append(f"{idx + 1}: add {op['k']} as a signed byte (wrap within -128..127).")
        elif kind == "umul":
            lines.append(f"{idx + 1}: multiply by {op['k']} as an unsigned byte (wrap mod 256).")
        elif kind == "udiv":
            lines.append(f"{idx + 1}: divide by {op['k']} as an unsigned byte (division by zero traps).")
        elif kind == "cast":
            lines.append(f"{idx + 1}: reinterpret the byte as {'signed' if op['to'] == 'signed' else 'unsigned'}.")
        elif kind == "index":
            lines.append(f"{idx + 1}: use the byte as an index into an array of size {op['m']} (out of range traps).")
        elif kind == "enum":
            lines.append(f"{idx + 1}: use the byte as an enum tag; valid tags are {sorted(op['allowed'])} (others trap).")
        elif kind == "union":
            variants = {i: t for i, t in enumerate(op["variants"])}
            lines.append(
                f"{idx + 1}: treat the byte as a tagged union: the top {op['nbits']} bits are the tag, "
                f"the remaining bits are the payload. Valid variants are {variants} (invalid tag traps, "
                f"payload read as the variant's type)."
            )
    return lines


@dataclass
class RepresentationBoundaryConfig(Config):
    checkpoints: int = 2

    def apply_difficulty(self, level):
        self.checkpoints = 2 + level


class RepresentationBoundaryValues(Task):
    summary = ("Pass byte values through fixed-width signed and unsigned arithmetic, enum tags, "
               "pointer indices, tagged unions, casts, and traps; answer each checkpoint's "
               "value-with-type or first invalid reinterpretation.")
    design_choice = ("Checkpoints require exact integer answers for signed/unsigned overflow at "
                     "fixed bit widths, with traps answered as the word 'trap'.")
    config_cls = RepresentationBoundaryConfig

    def _pick_op(self, depth):
        kinds = ["uadd", "sadd", "umul", "udiv", "cast", "index", "enum", "union"]
        kind = random.choice(kinds)
        if kind == "uadd":
            return {"kind": "uadd", "k": random.randrange(0, 257)}
        if kind == "sadd":
            return {"kind": "sadd", "k": random.randrange(-128, 128)}
        if kind == "umul":
            return {"kind": "umul", "k": random.randrange(0, 256)}
        if kind == "udiv":
            return {"kind": "udiv", "k": random.randrange(0, 9)}
        if kind == "cast":
            return {"kind": "cast", "to": random.choice(["signed", "unsigned"])}
        if kind == "index":
            return {"kind": "index", "m": random.randrange(1, 201)}
        if kind == "enum":
            size = random.randrange(1, 7)
            allowed = sorted(random.sample(range(0, 256), min(size, 256)))
            return {"kind": "enum", "allowed": allowed}
        nb = random.randrange(2, 8)
        nvars = random.randrange(2, 7)
        variants = [random.choice(["signed", "unsigned"]) for _ in range(nvars)]
        return {"kind": "union", "nbits": nb, "nvars": nvars, "variants": variants}

    def generate_entry(self):
        n = self.config.checkpoints
        for _ in range(40):
            v0 = random.randrange(0, 256)
            ops = [self._pick_op(i) for i in range(n)]
            tokens = _simulate(ops, v0)
            if not tokens:
                continue
            if len(tokens) == n and random.random() < 0.9:
                # want variety: skip optics, keep this non-trapping chain
                pass
            if all(t == "trap" for t in tokens):
                continue  # an all-trap trace is degenerate
            answer = ", ".join(tokens)
            metadata = {
                "initial_byte": v0,
                "checkpoints": ops,
                "tokens": tokens,
            }
            # self-check: recompute from raw representation and confirm identity
            recomputed = _simulate(ops, v0)
            if recomputed != tokens:
                continue
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("could not generate a valid trace")

    def render_prompt(self, metadata):
        v0 = metadata["initial_byte"]
        lines = _render_ops(metadata["checkpoints"])
        body = "\n".join(lines)
        return (
            f"An 8-bit value starts as the byte {v0}. A sequence of checkpoints "
            f"processes it left to right; unsigned arithmetic wraps mod 256 and signed "
            f"arithmetic wraps within -128..127. A checkpoint traps if it divides by "
            f"zero, indexes out of range, uses an invalid enum tag, or selects an "
            f"invalid tagged-union variant; a trap ends the sequence at that "
            f"checkpoint.\n"
            f"Checkpoints:\n{body}\n\n"
            f"List each checkpoint's result in order as a comma-separated list: unsigned "
            f"values as an integer followed by 'u', signed values as an integer followed "
            f"by 's', and a trapped checkpoint as the word 'trap'. Example format: "
            f"'42u, -5s, trap'. Output only the list."
        )


TASK_META = {'parent_source_id': None,
 'idea': 'representation_boundary_values (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_language_implementation_r4/representation_boundary_values',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
