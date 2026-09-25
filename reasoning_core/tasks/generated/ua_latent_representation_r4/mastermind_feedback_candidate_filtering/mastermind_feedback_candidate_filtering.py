import random
import string
from dataclasses import dataclass
from itertools import product

from reasoning_core.template import Config, Entry, Task


@dataclass
class MastermindFilterConfig(Config):
    length: int = 3
    colors: int = 4
    base_guesses: int = 2
    max_candidates: int = 12
    max_additional: int = 6

    def apply_difficulty(self, level):
        self.length = 3 + level // 2
        self.colors = min(12, 4 + level // 2)
        self.base_guesses = 2 + level // 2
        self.max_candidates = 12 + level
        self.max_additional = 4 + level


def _alphabet(k):
    return string.ascii_uppercase[:k]


def _all_codes(length, colors):
    alpha = _alphabet(colors)
    return ["".join(p) for p in product(alpha, repeat=length)]


def _feedback(secret, guess):
    n = len(secret)
    exact = sum(1 for i in range(n) if guess[i] == secret[i])
    counts = {}
    for ch in secret:
        counts[ch] = counts.get(ch, 0) + 1
    gc = {}
    for ch in guess:
        gc[ch] = gc.get(ch, 0) + 1
    total = 0
    for ch, c in counts.items():
        total += min(c, gc.get(ch, 0))
    wrong = total - exact
    return (exact, wrong)


def _candidates(codes, feedbacks):
    return [c for c in codes if all(_feedback(c, g) == (e, w) for (g, (e, w)) in feedbacks)]


def _join(codes):
    return ",".join(codes)


class MastermindFeedbackCandidateFiltering(Task):
    summary = ("Filter secret codes under Mastermind feedback: given guesses with exact-position "
               "and wrong-position counts, keep the candidate set consistent with every clue and "
               "list all remaining codes in alphabetical order.")
    config_cls = MastermindFilterConfig
    design_choice = ("Present feedback as exact counts (e.g., '2 correct position, 1 wrong "
                     "position') and require listing all remaining codes in canonical order.")

    def generate_entry(self):
        config = self.config
        length = config.length
        colors = config.colors
        alpha = _alphabet(colors)
        all_codes = _all_codes(length, colors)

        secret = "".join(random.choice(alpha) for _ in range(length))

        guess_count = config.base_guesses
        guesses = []
        attempts = 0
        seen = set()
        while len(guesses) < guess_count and attempts < guess_count + config.max_additional + 8:
            cand = "".join(random.choice(alpha) for _ in range(length))
            if cand in seen:
                attempts += 1
                continue
            seen.add(cand)
            guesses.append(cand)
            attempts += 1

        feedbacks = [(g, _feedback(secret, g)) for g in guesses]

        remaining = _candidates(all_codes, feedbacks)
        assert len(remaining) >= 1, "secret not in candidate set"

        extra = 0
        while len(remaining) > config.max_candidates and extra < config.max_additional and len(all_codes) > 1:
            g = "".join(random.choice(alpha) for _ in range(length))
            if g in seen:
                extra += 1
                continue
            seen.add(g)
            guesses.append(g)
            feedbacks.append((g, _feedback(secret, g)))
            remaining = _candidates(all_codes, feedbacks)
            extra += 1

        assert len(remaining) >= 1
        remaining = sorted(remaining)
        assert remaining[0] in all_codes and all(c in all_codes for c in remaining)
        assert all(_feedback(c, g) == (e, w) for (g, (e, w)) in feedbacks for c in remaining)

        answer = _join(remaining)

        metadata = {
            "length": length,
            "colors": colors,
            "alphabet": alpha,
            "guesses": list(guesses),
            "feedback_counts": [[int(e), int(w)] for (_, (e, w)) in feedbacks],
            "candidate_count": int(len(remaining)),
            "answers": list(remaining),
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        n = metadata["length"]
        alpha = metadata["alphabet"]
        lines = []
        lines.append(
            "A secret code is a sequence of %d pegs, each peg one color from {%s}. "
            "Colors may repeat. You are shown several guesses against the secret code; "
            "after each guess you are told exactly how many pegs are the right color in the "
            "right position ('correct position') and how many are the right color but in the "
            "wrong position ('wrong position')." % (n, alpha)
        )
        for i, g in enumerate(metadata["guesses"]):
            e, w = metadata["feedback_counts"][i]
            lines.append(
                "Guess %s: %d correct position, %d wrong position." % (g, e, w)
            )
        lines.append(
            "List every code consistent with ALL of the feedback above, i.e. the candidate set "
            "of secrets that each guess would score exactly as reported. "
            "Answer as the codes separated by commas, in alphabetical order, with no spaces. "
            "For example, if the candidates were AAB, ABA and BAA the answer would be: AAB,ABA,BAA"
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        norm = answer.strip().replace(" ", "")
        if norm == entry.answer:
            return 1.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'mastermind_feedback_candidate_filtering (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_latent_representation_r4/mastermind_feedback_candidate_filtering',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
