import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class SimplicialOperatorNormalizationConfig(Config):
    min_ops: int = 2
    max_ops: int = 3
    max_index: int = 2

    def apply_difficulty(self, level):
        self.min_ops = 2 + level
        self.max_ops = 3 + level * 2
        self.max_index = 2 + level


def _simulate(vertices, word):
    """Apply a word of face/degeneracy maps left-to-right where maps compose
    right-to-left: iterate the word from the end and mutate the list in place."""
    for kind, idx in reversed(word):
        if kind == 'd':
            vertices.pop(idx)
        else:
            vertices.insert(idx + 1, vertices[idx])
    return vertices


def normalize(word):
    """Reduce a word using the simplicial identities to canonical form
    (all degeneracies on the left, all faces on the right)."""
    ops = [list(op) for op in word]
    while True:
        reduced = False
        i = 0
        while i < len(ops) - 1:
            k1, x = ops[i]
            k2, y = ops[i + 1]
            if k1 == 'd' and k2 == 's':
                if x == y or x == y + 1:
                    del ops[i:i + 2]
                elif x < y:
                    ops[i:i + 2] = [['s', y - 1], ['d', x]]
                else:
                    ops[i:i + 2] = [['s', y], ['d', x - 1]]
                reduced = True
                i = 0
                continue
            i += 1
        if not reduced:
            break
    s_block = [op[1] for op in ops if op[0] == 's']
    d_block = [op[1] for op in ops if op[0] == 'd']
    return s_block, d_block


def _render_word(word):
    return " ".join(f"{kind}{idx}" for kind, idx in word)


def _fmt(indices):
    return "[" + ", ".join(str(i) for i in indices) + "]"


def _format_answer(omitted, repeated):
    return f"omitted={_fmt(omitted)}; repeated={_fmt(repeated)}"


def _score_answer(answer, entry):
    ref = entry['answer']
    return 1.0 if str(answer).strip() == str(ref).strip() else 0.0


class SimplicialOperatorNormalization(Task):
    summary = ("Normalize composites of dimension-indexed simplicial face and degeneracy maps "
               "using index-shift and cancellation identities; return the sorted vertex indices "
               "omitted by the face block and repeated by the degeneracy block in canonical form.")
    design_choice = ("Return the list of vertex indices that are omitted (face maps) and repeated "
                     "(degeneracy maps) in the canonical form, as two sorted lists.")
    config_cls = SimplicialOperatorNormalizationConfig
    task_version = 2

    def generate_entry(self):
        for _ in range(500):
            n_ops = random.randint(self.config.min_ops, self.config.max_ops)
            max_index = self.config.max_index
            word = []
            for _ in range(n_ops):
                kind = random.choice(('d', 's'))
                idx = random.randint(0, max_index)
                word.append((kind, idx))
            start = list(range(max_index + 2))
            try:
                res_original = _simulate(list(start), word)
            except IndexError:
                continue
            s_block, d_block = normalize(list(word))
            canon_word = [('s', x) for x in s_block] + [('d', x) for x in d_block]
            res_canon = _simulate(list(start), canon_word)
            if res_canon != res_original:
                continue
            omitted = sorted(d_block)
            repeated = sorted(s_block)
            if not all(isinstance(v, int) and v >= 0 for v in omitted + repeated):
                continue
            answer = _format_answer(omitted, repeated)
            metadata = {
                'word': _render_word(word),
                'omitted': omitted,
                'repeated': repeated,
                'canonical': _render_word(canon_word),
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError(f"{self.task_name}: failed to produce an admissible example")

    def render_prompt(self, metadata):
        return (
            "Simplicial face maps d_i and degeneracy maps s_j satisfy the simplicial "
            "identities. In a word written left to right, an adjacent pair d_i s_j reduces: "
            "d_i s_i and d_i s_{i+1} cancel to the identity; d_i s_j = s_{j-1} d_i when i < j; "
            "and d_i s_j = s_j d_{i-1} when i > j+1. Pushing every degeneracy left of every "
            "face and cancelling identities yields the canonical form, an s-block (repeated "
            "vertices) followed by a d-block (omitted vertices). For example the word "
            "\"d0 s0\" cancels to the identity, giving omitted=[]; repeated=[] and the word "
            "\"d0 d1\" gives omitted=[0, 1]; repeated=[].\n\n"
            f"Normalize this word to canonical form and report the two sorted lists, keeping "
            f"multiplicity of any repeated index. Format exactly: omitted=[...]; repeated=[...].\n\n"
            f"word: {metadata['word']}"
        )

    def score_answer(self, answer, entry):
        return _score_answer(answer, entry)


TASK_META = {'parent_source_id': None,
 'idea': 'simplicial_operator_normalization (variant 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_semantics_preserving_translation_r4/simplicial_operator_normalization',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2302342651,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
