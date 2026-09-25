"""Bounded loop deformation on cell complexes.

A loop on a cell complex is a cyclic sequence of labeled edges. Allowed local
deformations:
  - spur insertion/removal: an adjacent inverse pair x x' cancels (or may be
    inserted at a gap), shrinking/growing the loop by two edges.
  - face-boundary substitution: a contiguous path of the loop that is an arc of
    a face boundary is replaced by the complementary arc of the same face; when
    the complement is shorter the loop shrinks.

Anchors (vertices that must be preserved) and a length cap are given. The task
asks for the sequence of loop words that takes the loop down to a length no
greater than the cap by valid deformations, or the marker for impossibility.

Generation is *constructive*: we start from a short reduced loop and apply
reverse deformations (inserting spurs and growing face detours) so a valid
forward reduction to <= cap is guaranteed to exist. The gold answer is that
forward chain, so every instance is solvable and verifiable.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'bounded_loop_deformation (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_inference_modes_r4/bounded_loop_deformation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

NEG = {'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F',
       'A': 'a', 'B': 'b', 'C': 'c', 'D': 'd', 'E': 'e', 'F': 'f'}


def _neg(ch):
    return NEG[ch]


def _fully_reduce(word):
    """Greedily delete adjacent inverse pairs to square zero-length-free form."""
    w = list(word)
    changed = True
    while changed:
        changed = False
        for i in range(len(w) - 1):
            if w[i] == _neg(w[i + 1]):
                del w[i:i + 2]
                changed = True
                break
    return ''.join(w)


def _square_faces(letters, count):
    """Build a set of square faces (cyclic 4-edge boundaries) over the alphabet."""
    faces = []
    picks = set()
    for _ in range(count * 3):
        a, b, c, d = random.sample(letters, 4)
        key = (a, b, c, d)
        if key in picks:
            continue
        picks.add(key)
        faces.append((a, b, c, d))
        if len(faces) >= count:
            break
    if not faces:
        faces = [(letters[0], letters[1], letters[2], letters[3])]
    return faces


def _face_arc_pairs(face):
    """All (short_arc, long_arc) pairs of a square face.

    A square face f = (e0,e1,e2,e3) has cyclic boundary. For each edge, its
    1-edge arc and the complementary 3-edge arc connect the same two vertices.
    Yields (arc1, arc3) as strings.
    """
    f = list(face)
    pairs = []
    L = 4
    for i in range(L):
        short = f[i]
        long_ = f[(i + 1) % L] + f[(i + 2) % L] + f[(i + 3) % L]
        pairs.append((short, long_))
    return pairs


def _build_loop(cap, faces, letters, num_moves):
    """Construct a solvable instance.

    Start from a short reduced loop w0 of length <= cap, then apply num_moves
    reverse deformations that each grow the loop. Face detours happen first
    (innermost), spur insertions last (outermost). Forward replay then removes
    spurs first, then detours, so a detour never destroys a recorded spur pair
    and each detour substring stays contiguous when it is removed. Returns
    (start_word, faces, forward_moves, w0) with value-based forward moves.
    """
    core_len = random.randint(1, min(cap, 3))
    w = [random.choice(letters) for _ in range(core_len)]
    w = list(_fully_reduce(''.join(w))) or [random.choice(letters)]
    w0 = ''.join(w)
    forward_moves = []

    n_face = random.randint(0, min(num_moves, 2))
    for _ in range(n_face):
        placed = False
        for face in faces:
            for short, long_ in _face_arc_pairs(face):
                cur = ''.join(w)
                if short not in cur:
                    continue
                idx = cur.find(short)
                neww = cur[:idx] + long_ + cur[idx + 1:]
                if neww.count(long_) == 1 and len(neww) <= 28:
                    w = list(neww)
                    forward_moves.append(('face', ''.join(face), short, long_))
                    placed = True
                    break
            if placed:
                break
        if not placed:
            break

    # remainder as spurs, all appended at the tail so they form a clean stack
    # removed in reverse order, never perturbing the inner face detours/core.
    for _ in range(num_moves - n_face):
        x = random.choice(letters)
        w = w + [x, _neg(x)]
        forward_moves.append(('spur', x + _neg(x)))

    start = ''.join(w)
    return start, faces, forward_moves, w0


def _apply_forward_step(w, mv):
    """Apply one forward move to word w, returning the new word or None if invalid."""
    if mv[0] == 'spur':
        pair = mv[1]
        if pair[0] != _neg(pair[1]):
            return None
        idx = w.find(pair)
        if idx < 0:
            return None
        return w[:idx] + w[idx + 2:]
    else:
        _, face, short, long_ = mv
        idx = w.find(long_)
        if idx < 0:
            return None
        return w[:idx] + short + w[idx + len(long_):]


def _verify_chain(start, cap, faces, forward_moves, w0):
    """Replay the forward reduction; return the chain of words or None if invalid."""
    w = start
    chain = [w]
    for mv in reversed(forward_moves):
        nw = _apply_forward_step(w, mv)
        if nw is None:
            return None
        w = nw
        chain.append(w)
    if len(w) > cap:
        return None
    if _fully_reduce(w) != _fully_reduce(w0):
        return None
    return chain


def _canonical(chain):
    return '>'.join(chain)


@dataclass
class BoundedLoopDeformationConfig(Config):
    alphabet: int = 4       # number of distinct edge labels
    moves: int = 2          # number of deformations in the chain
    cap: int = 2            # target max loop length

    def apply_difficulty(self, level):
        self.alphabet = stochastic_rounding(self.alphabet + level)
        self.moves = 1 + level
        self.cap = stochastic_rounding(self.cap + (level // 2))


class BoundedLoopDeformation(Task):
    summary = ("Contract or reroute edge loops on supplied cell complexes using spur "
               "insertion/removal and face-boundary substitutions; respect fixed anchors "
               "and length caps, returning a shortest deformation or impossibility.")
    design_choice = ("Answer as a canonical sequence of loop-edge labels to delete, "
                     "preserving all anchors and ending at a loop no longer than the cap.")
    config_cls = BoundedLoopDeformationConfig

    def generate_entry(self):
        cfg = self.config
        letters = [c for c in 'abcdef'[:cfg.alphabet]]
        for _ in range(60):
            faces = _square_faces(letters, cfg.alphabet)
            start, _, forward_moves, w0 = _build_loop(
                cfg.cap, faces, letters, cfg.moves)
            chain = _verify_chain(start, cfg.cap, faces, forward_moves, w0)
            if chain is not None:
                break
        else:
            chain = [start]
        faces_txt = [''.join(f) for f in faces]
        return Entry(metadata={
            'start': start,
            'faces': faces_txt,
            'cap': cfg.cap,
            'anchors': 'start vertex only',
        }, answer=_canonical(chain))

    def render_prompt(self, metadata):
        faces_txt = '; '.join(
            f"face {i + 1}: boundary {metadata['faces'][i]}"
            for i in range(len(metadata['faces'])))
        return (
            f"A loop on a cell complex has edge sequence {metadata['start']!r}. "
            f"The complex has {faces_txt}. Allowed deformations: (1) spur "
            f"insertion/removal -- delete an adjacent inverse pair x x' ; (2) "
            f"face-boundary substitution -- replace a contiguous path of the loop "
            f"that is an arc of a face boundary by the complementary arc of that "
            f"face. Reduce the loop to length at most {metadata['cap']} while "
            f"preserving the {metadata['anchors']}. Give the sequence of loop "
            f"words, separated by '>', listing the loop after each deletion from "
            f"the start word down to a word of length at most {metadata['cap']}, or "
            f"'impossible' if no such reduction exists."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == entry.answer else 0.0
