import random
from dataclasses import dataclass
from typing import List, Tuple

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'paragraph_reflow_resynchronization (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_representation_specific_r4/paragraph_reflow_resynchronization',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

SW = True
GLUE = True
NWSP = True


def _py_word_wrap(words, max_width, use_nwsp=True):
    lines = []
    i = 0
    n = len(words)
    while i < n:
        width = 0
        start = i
        while i < n:
            word = words[i]
            wlen = len(word)
            if use_nwsp and wlen > max_width:
                firstpart = word[:max_width]
                if width > 0:
                    lines.append([])
                lines.append([firstpart])
                rest_idx = start
                lines.append([])
                width = 0
                i = i + 1
                word = word[max_width:]
                while word:
                    piece = word[:max_width]
                    lines[-1].append(piece)
                    word = word[max_width:]
                i = i + (len(''.join(lines[-1])) // max_width)
                break
            gap = 1 if (width > 0 or start < i) else 0
            if width + gap + wlen > max_width:
                break
            width += (gap if width > 0 else 0) + wlen
            i += 1
        line = words[start:i]
        lines.append(line)
    return lines


def _split_into_tokens(text):
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == ' ':
            tokens.append(' ')
            i += 1
        elif c == '\n':
            tokens.append('\n')
            i += 1
        else:
            j = i
            while j < n and text[j] not in ' \n':
                j += 1
            tokens.append(text[i:j])
            i = j
    return tokens


def wrap_into_lines(tokens, max_width):
    lines = []
    cur = []
    cur_width = 0
    for tok in tokens:
        if tok == '\n':
            if cur:
                lines.append(cur)
                cur = []
                cur_width = 0
            else:
                lines.append([''])
                cur_width = 0
            continue
        if tok == ' ':
            if cur and cur_width > 0 and cur_width + 1 <= max_width:
                cur.append(tok)
                cur_width += 1
            continue
        wlen = len(tok)
        if cur_width > 0:
            if cur_width + 1 + wlen <= max_width:
                cur.append(' ')
                cur.append(tok)
                cur_width += 1 + wlen
            else:
                lines.append(cur)
                cur = [tok]
                cur_width = wlen
        else:
            if cur_width + wlen <= max_width:
                cur.append(tok)
                cur_width = wlen
            else:
                if len(cur) == 0 and wlen > max_width:
                    lines.append([tok])
                    cur = []
                    cur_width = 0
                else:
                    lines.append(cur)
                    cur = [tok]
                    cur_width = wlen
    if cur:
        lines.append(cur)
    return lines


def reflow(text, max_width, nwsp=True):
    tokens = _split_into_tokens(text)
    return wrap_into_lines(tokens, max_width)


def render_lines(lines):
    return [' '.join(l).strip() if l else '' for l in lines]


def render_with_nwsp(lines):
    out = []
    for l in lines:
        s = ''.join(l).rstrip(' ')
        out.append(s)
    return out


@dataclass
class ParagraphReflowResyncConfig(Config):
    min_words: int = 6
    max_words: int = 12
    max_width: int = 12
    long_words: bool = False
    nwsp: bool = True
    actions: tuple = ('edit', 'remove', 'insert')

    def apply_difficulty(self, level):
        self.min_words = stochastic_rounding(self.min_words + level * 2)
        self.max_words = stochastic_rounding(self.max_words + level * 3)
        self.max_width = stochastic_rounding(max(6, self.max_width - level // 2))
        if level >= 3:
            self.long_words = True
        if level >= 5:
            self.nwsp = False


class ParagraphReflowResync(Task):
    summary = "Repair cached line layouts after token or width edits under wrapping, glue, and discretionary-break rules; track spill and pullback until unchanged suffix alignment, returning changed lines."
    design_choice = "Return only the minimal set of line indices whose text changed, not entire reflowed paragraphs, with answer as a sorted list of integers."
    task_version = 2
    config_cls = ParagraphReflowResyncConfig

    def _generate_paragraph(self):
        c = self.config
        base_words = []
        vocab = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "theta",
                 "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "rho",
                 "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega",
                 "the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog",
                 "lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
                 "adipiscing", "art", "of", "and", "in", "on", "for", "with"]
        n_words = random.randint(c.min_words, c.max_words)
        words = []
        for _ in range(n_words):
            if c.long_words and random.random() < 0.15:
                wl = random.randint(c.max_width + 1, c.max_width + 5)
                words.append(''.join(random.choice('abcdefghij') for _ in range(wl)))
            else:
                words.append(random.choice(vocab))
        return words, n_words

    def _layout(self, words, max_width, nwsp):
        lines = []
        i = 0
        n = len(words)
        if not nwsp:
            while i < n:
                w = words[i]
                if len(w) > max_width:
                    lines.append(w)
                    i += 1
                    continue
                width = len(w)
                start = i
                i += 1
                while i < n and len(words[i]) <= max_width and width + 1 + len(words[i]) <= max_width:
                    width += 1 + len(words[i])
                    i += 1
                lines.append(' '.join(words[start:i]))
        else:
            buf = ''
            cur = ''
            def flush(line):
                nonlocal cur
                s = line.rstrip()
                lines.append(s)
                cur = ''
            i = 0
            while i < n:
                w = words[i]
                if len(w) > max_width:
                    if cur:
                        flush(cur)
                    lines.append(w)
                    i += 1
                    continue
                if not cur:
                    cur = w
                    i += 1
                    continue
                if len(cur) + 1 + len(w) <= max_width:
                    cur = cur + ' ' + w
                    i += 1
                else:
                    flush(cur)
            if cur:
                lines.append(cur)
        return lines

    def generate_entry(self):
        c = self.config
        words, n_words = self._generate_paragraph()
        max_width = c.max_width
        nwsp = c.nwsp

        action = random.choice(c.actions)
        if action == 'edit':
            idx = random.randrange(len(words))
            new_word = random.choice(["alpha", "beta", "gamma", "delta", "eps",
                                      "zeta", "eta", "theta", "iota", "kappa",
                                      "lambda", "mu", "nu", "xi", "omicron",
                                      "rho", "sigma", "tau", "upsilon", "phi",
                                      "chi", "psi", "omega", "the", "a", "at",
                                      "q", "x", "zz", "omega", "ellipsis",
                                      "transcendent", "supercalifragilistic"])
            words[idx] = new_word
        elif action == 'remove':
            if len(words) > 1:
                idx = random.randrange(len(words))
                words.pop(idx)
        else:
            idx = random.randrange(len(words) + 1)
            new_word = random.choice(["alpha", "beta", "zeta", "omega", "and",
                                      "of", "the", "mu", "k", "w", "isis",
                                      "eleemosynary", "antidisestablishmentarianism"])
            words.insert(idx, new_word)

        base_words = words
        base_max = max_width

        lines_before = self._layout(list(words), base_max, nwsp)

        edit2 = random.choice(['width', 'token', None, None])
        width_delta = random.randint(-2, 2)
        new_max = base_max + width_delta
        if new_max < 3:
            new_max = 3

        final_words = list(words)
        t_idx = None
        t_new = None
        if nwsp:
            pass
        if edit2 == 'token':
            t_idx = random.randrange(len(final_words))
            t_new = random.choice(["alpha", "iota", "the", "q", "omega", "mu",
                                   "zz", "and", "a", "super", "iso"])
            final_words[t_idx] = t_new

        lines_after = self._layout(list(final_words), new_max, nwsp)

        changed = []
        m = max(len(lines_before), len(lines_after))
        for i in range(m):
            b = lines_before[i] if i < len(lines_before) else None
            a = lines_after[i] if i < len(lines_after) else None
            if b != a:
                changed.append(i)

        if not changed:
            changed = [len(lines_before)]

        return Entry(metadata={
            "words_before": base_words,
            "width_before": base_max,
            "words_after": final_words,
            "width_after": new_max,
            "nwsp": nwsp,
            "lines_before": lines_before,
            "lines_after": lines_after,
            "changed": sorted(changed),
        }, answer=repr(sorted(changed)))

    def render_prompt(self, metadata):
        before_lines = metadata["lines_before"]
        after_lines = metadata["lines_after"]
        wb = metadata["width_before"]
        wa = metadata["width_after"]
        nwsp = metadata["nwsp"]
        style = "glue+discretionary-break" if nwsp else "glue-only"

        lb = "\n".join(f"{i}: {l}" for i, l in enumerate(before_lines))
        la = "\n".join(f"{i}: {l}" for i, l in enumerate(after_lines))
        return (
            f"A cached paragraph was laid out at width {wb} ({style}), producing these lines "
            f"(0-indexed, each line on its own row):\n{lb}\n"
            f"The paragraph then changed (a word was edited, inserted, or removed, and the width "
            f"became {wa}) and was re-wrapped. The new lines are:\n{la}\n"
            f"Return the sorted list of line indices whose text differs between the old and new "
            f"layouts. The answer is a sorted list of integers, e.g. [1, 3]."
        )

    def score_answer(self, answer, entry):
        expected = sorted(entry.metadata['changed'])
        try:
            parsed = eval(answer)
        except Exception:
            return 0.0
        if not isinstance(parsed, list):
            return 0.0
        parsed = [int(x) for x in parsed]
        parsed = sorted(parsed)
        return 1.0 if parsed == expected else 0.0
