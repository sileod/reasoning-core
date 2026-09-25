import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


def _letters(alpha):
    if alpha <= 2:
        return ["a", "b"][:alpha]
    return ["a", "b", "c"][:alpha]


def _spectral_radius(matrix):
    n = len(matrix)
    if n == 1:
        return float(matrix[0][0])
    if n == 2:
        a, b = matrix[0]
        c, d = matrix[1]
        tr = a + d
        det = a * d - b * c
        disc = tr * tr - 4 * det
        if disc <= 0:
            return (tr + (abs(disc)) ** 0.5) / 2.0
        disc = disc ** 0.5
        return max((tr + disc) / 2.0, (tr - disc) / 2.0)
    import numpy as np

    return float(max(abs(v) for v in np.linalg.eigvals(np.array(matrix, dtype=float))))


def _is_primitive(matrix):
    n = len(matrix)
    acc = [list(row) for row in matrix]
    for _ in range(n + 2):
        positive = all(v > 0 for row in acc for v in row)
        if positive:
            return True
        acc = [
            [sum(acc[i][k] * matrix[k][j] for k in range(n)) for j in range(n)]
            for i in range(n)
        ]
    return False


def _occurring_letters(images, seed):
    reached = {seed}
    changed = True
    while changed:
        changed = False
        for src in list(reached):
            for ch in images[src]:
                if ch not in reached:
                    reached.add(ch)
                    changed = True
    return reached


def _build_instance(config):
    while True:
        alpha = config.alphabet_size
        letters = _letters(alpha)
        images = {}
        for src in letters:
            k = random.randint(2, config.max_image_len)
            images[src] = "".join(random.choice(letters) for _ in range(k))

        seeds = [
            src
            for src in letters
            if images[src][0] == src and len(images[src]) >= 2
        ]
        if not seeds:
            continue
        seed = random.choice(seeds)

        reach = _occurring_letters(images, seed)
        if len(reach) < 2:
            continue
        order = sorted(reach)
        sub = [letters.index(c) for c in order]
        idx = {c: i for i, c in enumerate(order)}
        matrix = [[0] * len(order) for _ in range(len(order))]
        for src in order:
            for ch in images[src]:
                matrix[idx[src]][idx[ch]] += 1
        if _spectral_radius(matrix) <= 1.05:
            continue
        return images, seed, reach, order, matrix


def _build_no_instance(config):
    while True:
        letters = _letters(3)
        seed = "a"
        others = [c for c in letters if c != seed]
        u_len = random.randint(1, config.max_image_len - 1)
        u = "".join(random.choice(others) for _ in range(u_len))
        images = {seed: seed + u}
        for c in others:
            k = random.randint(2, config.max_image_len)
            images[c] = "".join(random.choice(others) for _ in range(k))
        reach = _occurring_letters(images, seed)
        if len(reach) < 2:
            continue
        order = sorted(reach)
        idx = {c: i for i, c in enumerate(order)}
        matrix = [[0] * len(order) for _ in range(len(order))]
        for src in order:
            for ch in images[src]:
                matrix[idx[src]][idx[ch]] += 1
        if _spectral_radius(matrix) <= 1.05:
            continue
        return images, seed, reach, order, matrix


def _generate_prefix(images, seed, window):
    word = images[seed]
    while len(word) < window:
        word = "".join(images[c] for c in word)
    return word[:window]


def _decide(images, seed, reach, order, matrix, window):
    if _is_primitive(matrix):
        return "yes", True

    word = _generate_prefix(images, seed, window)
    half = window // 2
    suffix = set(word[half:])
    for letter in order:
        if letter not in suffix:
            if letter in word[:half]:
                return "no", True
    return None, False


@dataclass
class SubstitutionUniformRecurrenceConfig(Config):
    alphabet_size: int = 3
    max_image_len: int = 3
    window: int = 6000

    def apply_difficulty(self, level):
        self.alphabet_size = 3
        self.max_image_len = 3 + (level // 2)
        self.window = 6000 + level * 1500


class SubstitutionUniformRecurrence(Task):
    summary = "Decide uniform (bounded-gap) recurrence of infinite words from nonerasing Pisot substitutions with prolongable seeds, over primitive and reducible symbol systems, as a balanced yes/no."
    config_cls = SubstitutionUniformRecurrenceConfig

    design_choice = "Answer as a single token 'yes' or 'no' based on whether the recurrence function is bounded for all prefixes, with instances drawn from a fixed family of Pisot substitutions."

    def generate_entry(self):
        target = random.choice(("yes", "no"))
        window = self.config.window
        fallback = None
        for _ in range(80):
            if target == "no":
                images, seed, reach, order, matrix = _build_no_instance(
                    self.config
                )
            else:
                images, seed, reach, order, matrix = _build_instance(
                    self.config
                )
            answer, ok = _decide(images, seed, reach, order, matrix, window)
            if not ok:
                continue
            if fallback is None:
                fallback = (images, seed, reach, answer)
            if answer == target:
                metadata = {
                    "images": images,
                    "seed_letter": seed,
                    "alphabet": list(reach),
                    "window": window,
                    "recurrence": answer,
                }
                return Entry(metadata=metadata, answer=answer)
        if fallback is None:
            raise RuntimeError("could not label instance")
        images, seed, reach, answer = fallback
        metadata = {
            "images": images,
            "seed_letter": seed,
            "alphabet": list(reach),
            "window": window,
            "recurrence": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        imgs = ", ".join(
            f"{k} -> {v}" for k, v in sorted(metadata["images"].items())
        )
        return (
            f"An infinite word is built by repeatedly applying the nonerasing "
            f"Pisot substitution {{{imgs}}} starting from the prolongable seed "
            f"letter '{metadata['seed_letter']}'. A factor recurs with bounded "
            f"gaps if every two consecutive occurrences are separated by at most "
            f"some fixed bound, and the word is uniformly recurrent when every "
            f"finite block that occurs does so with bounded gaps. Is this word "
            f"uniformly recurrent? Answer exactly 'yes' or 'no'."
        )

    def score_answer(self, answer, entry):
        return _score(answer, entry)


def _score(answer, entry):
    if not isinstance(answer, str):
        return 0.0
    a = answer.strip().lower()
    if a not in ("yes", "no"):
        return 0.0
    return 1.0 if a == entry.answer else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'substitution_uniform_recurrence (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_interacting_updates_r5/substitution_uniform_recurrence',
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
