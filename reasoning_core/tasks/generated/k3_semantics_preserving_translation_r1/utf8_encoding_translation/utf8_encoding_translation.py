import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'utf8_encoding_translation (draw 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in reasoning_core/tasks/generated/k3_semantics_preserving_translation_r1/utf8_encoding_translation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1336314872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class Utf8EncodingConfig(Config):
    n: int = 1

    def apply_difficulty(self, level):
        self.n = 1 + int(level * 2)


def _to_utf8(cp):
    return list(chr(cp).encode("utf-8"))


def _byte_to_bin(b):
    return format(b, "08b")


def _valid_codepoint(cp):
    return 0 <= cp <= 0x10FFFF and not (0xD800 <= cp <= 0xDFFF)


def _decode_utf8_bytes(bs):
    return ord(bytes(bs).decode("utf-8"))


class Utf8EncodingTranslation(Task):
    summary = "Encode Unicode code points into UTF-8 byte sequences and decode byte sequences back into code points, spanning 1-4 byte ranges, range-boundary values, and hex or binary renderings; answer is the exact byte list or code point list."
    design_choice = "Provide byte sequences in binary (8-bit groups) and ask for code points in decimal, mixing 1-4 byte lengths and boundary values."
    config_cls = Utf8EncodingConfig

    def _pick_bytes(self):
        cp = self._pick_cp()
        return _to_utf8(cp)

    def _pick_cp(self):
        while True:
            bucket = random.randrange(4)
            if bucket == 0:
                cp = random.randrange(0x80)
            elif bucket == 1:
                cp = random.randrange(0x80, 0x800)
            elif bucket == 2:
                cp = random.randrange(0x800, 0xD800)
                if random.random() < 0.5:
                    cp = random.randrange(0xE000, 0x10000)
            else:
                cp = random.randrange(0x10000, 0x110000)
            if _valid_codepoint(cp):
                return cp

    def generate_entry(self):
        n = random.randrange(1, self.config.n + 1)
        segments = []
        answers = []
        for _ in range(n):
            direction = random.choice(["enc", "dec"])
            if direction == "enc":
                cp = self._pick_cp()
                bytes_seq = _to_utf8(cp)
                segments.append({"kind": "enc", "cp": int(cp)})
                answers.append("B:" + " ".join(str(x) for x in bytes_seq))
                data = bytes(bytes_seq)
                assert list(data.decode("utf-8").encode("utf-8")) == bytes_seq
                assert _valid_codepoint(cp)
            else:
                bs = self._pick_bytes()
                cp = _decode_utf8_bytes(bs)
                assert _valid_codepoint(cp), (bs, cp)
                segments.append({"kind": "dec", "binary": [_byte_to_bin(x) for x in bs]})
                answers.append("C:" + str(cp))
        answer = " | ".join(answers)
        metadata = {"segments": segments, "n": n}
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = []
        for i, seg in enumerate(metadata["segments"], start=1):
            if seg["kind"] == "enc":
                lines.append(f"Segment {i}: code point: {seg['cp']}")
            else:
                lines.append(f"Segment {i}: binary byte sequence: {' '.join(seg['binary'])}")
        given = "\n".join(lines)
        return ("Translate each Unicode segment between a code point (an integer) and its UTF-8 "
                "encoding given as a binary byte sequence (8 bits per byte). For a segment given as "
                f"a code point, give its UTF-8 byte sequence as decimal byte values; for a segment "
                f"given as a binary byte sequence, give the decoded code point.\n\n{given}\n\n"
                "Give the results in the same order, joined by ' | '. Use 'B: v1 v2 ...' for a byte "
                "list and 'C: v' for a code point.")

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == entry.answer.strip() else 0.0
