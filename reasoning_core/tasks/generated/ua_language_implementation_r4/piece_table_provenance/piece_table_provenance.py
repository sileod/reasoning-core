"""Track character provenance through a piece-table text buffer."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'piece_table_provenance (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_language_implementation_r4/piece_table_provenance',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _exact_provenance(original, edits):
    """Char-level simulation returning (final_str, prov) faithfully.

    prov[i] = ('O', k) or ('A', k) where k is the index of the character in
    the source buffer. For appended chars, k indexes into the sequence of all
    appended characters in the order they were appended.
    """
    buf = [('O', i) for i in range(len(original))]
    orig = list(original)
    appended = []
    for kind, lo, hi, text in edits:
        if kind == 'insert':
            pos = lo
            chunk = []
            for ch in text:
                aidx = len(appended)
                appended.append(ch)
                chunk.append(('A', aidx))
            buf = buf[:pos] + chunk + buf[pos:]
        elif kind == 'delete':
            buf = buf[:lo] + buf[hi:]
        elif kind == 'replace':
            chunk = []
            for ch in text:
                aidx = len(appended)
                appended.append(ch)
                chunk.append(('A', aidx))
            buf = buf[:lo] + chunk + buf[hi:]
    final_chars = []
    prov = []
    for src, k in buf:
        if src == 'O':
            final_chars.append(orig[k])
            prov.append(('O', k))
        else:
            final_chars.append(appended[k])
            prov.append(('A', k))
    return ''.join(final_chars), prov


@dataclass
class PieceTableProvenanceConfig(Config):
    edits: int = 3
    orig_len: int = 6
    max_insert: int = 3

    def apply_difficulty(self, level):
        self.edits = 2 + level
        self.orig_len = 5 + level
        self.max_insert = 2 + level


class PieceTableProvenance(Task):
    summary = ("Track a character through a piece-table buffer under mixed insert, delete, and "
               "replace edits; report which source buffer (original or added) and offset the final "
               "position points to, using append-only piece descriptors over random alphabet tokens.")
    config_cls = PieceTableProvenanceConfig
    design_choice = ("Instances ask for the source buffer and offset of a single final character "
                     "position after a scripted sequence of edits.")

    def generate_entry(self):
        for _ in range(200):
            n_edits = max(1, self.config.edits)
            orig_len = self.config.orig_len
            original = ''.join(random.choice('abcdefghij') for _ in range(orig_len))
            edits = []
            for _ in range(n_edits):
                kind = random.choice(['insert', 'delete', 'replace'])
                if kind == 'insert':
                    pos = random.randint(0, self.config.orig_len + 5)
                    text = ''.join(random.choice('xyz') for _ in range(random.randint(1, self.config.max_insert)))
                    edits.append(('insert', pos, 0, text))
                elif kind == 'delete':
                    # need a valid current length; use orig_len+ generous upper to keep valid
                    # We'll validate by simulation later; bound high and clamp.
                    lo = random.randint(0, orig_len + 8)
                    ln = random.randint(1, 3)
                    hi = lo + ln
                    edits.append(('delete', lo, hi, ''))
                else:
                    lo = random.randint(0, orig_len + 8)
                    ln = random.randint(1, 3)
                    text = ''.join(random.choice('wv') for _ in range(random.randint(1, self.config.max_insert)))
                    edits.append(('replace', lo, lo + ln, text))
            # sanitize edit bounds against actual buffer so they are always valid
            buf = list(range(orig_len))
            clean = []
            for kind, lo, hi, text in edits:
                if kind == 'insert':
                    pos = min(lo, len(buf))
                    clean.append(('insert', pos, 0, text))
                    # grow buf for next steps length accounting only (chars symbolic)
                    buf = buf[:pos] + ['x'] * len(text) + buf[pos:]
                elif kind == 'delete':
                    lo = min(lo, len(buf))
                    hi = min(hi, len(buf))
                    if lo < hi:
                        clean.append(('delete', lo, hi, ''))
                        buf = buf[:lo] + buf[hi:]
                else:
                    lo = min(lo, len(buf))
                    hi = min(hi, len(buf))
                    buf = buf[:lo] + ['x'] * len(text) + buf[hi:]
                    clean.append(('replace', lo, hi, text))
            if len(clean) == 0:
                continue
            final_str, prov = _exact_provenance(original, clean)
            if len(final_str) == 0:
                continue
            query = random.randint(0, len(final_str) - 1)
            src, k = prov[query]
            buf_name = 'original' if src == 'O' else 'added'
            answer = f"{buf_name}:{k}"
            if src == 'O':
                assert 0 <= k < len(original)
            else:
                assert 0 <= k
            # independent check: reconstruct char
            check_char = original[k] if src == 'O' else _appended_char(original, clean, k)
            assert check_char == final_str[query]
            edits_plain = [list(e) for e in clean]
            return Entry(metadata={
                'original': original,
                'edits': edits_plain,
                'query': query,
                'final_str': final_str,
            }, answer=answer)
        raise RuntimeError("could not generate a valid piece-table instance")

    def render_prompt(self, metadata):
        original = metadata['original']
        edits = [_fmt_edit(e) for e in metadata['edits']]
        query = metadata['query']
        lines = [f"Original buffer: {original}"]
        lines.append("Edits (positions are 0-indexed within the buffer at that step):")
        for i, e in enumerate(edits):
            lines.append(f"  {i+1}. {e}")
        lines.append(
            f"What is the provenance of the character currently at final position {query}? "
            "Give its source buffer ('original' or 'added') and its offset within that buffer "
            "as one line in the form 'original:k' or 'added:k', where k is the 0-indexed "
            "character index inside the original buffer or the k-th appended character.")
        return "\n".join(lines)


def _fmt_edit(e):
    kind, lo, hi, text = e
    if kind == 'insert':
        return f"insert {text!r} at position {lo}"
    if kind == 'delete':
        return f"delete the range [{lo}, {hi})"
    return f"replace the range [{lo}, {hi}) with {text!r}"


def _appended_char(original, edits, k):
    """Return the k-th appended character across the edit script."""
    app = []
    for kind, lo, hi, text in edits:
        if text:
            for ch in text:
                app.append(ch)
    return app[k]


def _parse_answer(answer):
    """Parse 'buf:off' where buf is 'original' or 'added'."""
    s = answer.strip()
    if ':' not in s:
        return None
    buf, _, offs = s.partition(':')
    if buf not in ('original', 'added'):
        return None
    try:
        off = int(offs)
    except ValueError:
        return None
    return (buf, off)


def score_answer(answer, entry):
    """Exact-match scorer for a provenance tuple: 'original:k' or 'added:k'."""
    gold_buf, gold_off = entry.answer.split(':')
    parsed = _parse_answer(answer)
    if parsed is None:
        return 0.0
    buf, off = parsed
    if buf == gold_buf and str(off) == gold_off:
        return 1.0
    return 0.0
