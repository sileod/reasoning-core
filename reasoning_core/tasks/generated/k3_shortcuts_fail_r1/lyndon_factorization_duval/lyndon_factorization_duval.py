import random
from dataclasses import dataclass

from reasoning_core.template import Task, Entry, Config, edict, stochastic_rounding as sround

design_choice = "Answer as a canonical string of factors separated by a single space, with each factor quoted if it contains spaces."

TASK_META = {'parent_source_id': None,
 'idea': 'lyndon_factorization_duval (draw 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_shortcuts_fail_r1/lyndon_factorization_duval',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}


@dataclass
class LyndonFactorizationConfig(Config):
    min_len: int = 6
    max_len: int = 12
    alphabet_size: int = 3

    def apply_difficulty(self, level):
        self.min_len = 6 + 3 * level
        self.max_len = 12 + 6 * level
        self.alphabet_size = 3 + level // 3


def _is_lyndon(word):
    m = len(word)
    if m < 1:
        return False
    for r in range(1, m):
        if not word < word[r:] + word[:r]:
            return False
    return True


def _duval(word):
    factors = []
    n = len(word)
    i = 0
    while i < n:
        j = i + 1
        k = i
        while j < n and word[k] <= word[j]:
            if word[k] < word[j]:
                k = i
            else:
                k += 1
            j += 1
        length = j - k
        while i <= k:
            factors.append(word[i:i + length])
            i += length
    return factors


def _verify_factors(word, factors):
    if "".join(factors) != word:
        return False
    if not all(_is_lyndon(f) for f in factors):
        return False
    return all(factors[i] >= factors[i + 1] for i in range(len(factors) - 1))


def _render_factor(f):
    return '"' + f + '"' if " " in f else f


def _factor_answer(factors):
    return " ".join(_render_factor(f) for f in factors)


def _parse_answer(answer):
    tokens = []
    for tok in answer.split(" "):
        tk = tok.strip()
        if len(tk) >= 2 and tk[0] == '"' and tk[-1] == '"':
            tk = tk[1:-1]
        tokens.append(tk)
    return tokens


class LyndonFactorizationDuval(Task):
    config_cls = LyndonFactorizationConfig
    summary = ("Factor a word into its unique non-increasing Lyndon-word sequence by "
               "Duval's three-way scan; inputs vary alphabet, long runs, and "
               "near-periodic structure; answer the ordered factor list.")

    def generate_entry(self):
        cfg = self.config
        alphabet = "".join(chr(ord("a") + i) for i in range(cfg.alphabet_size))
        while True:
            style = random.random()
            if style < 0.15:
                base = random.choice(alphabet)
                word = base * random.randint(cfg.min_len, cfg.max_len)
            elif style < 0.55:
                n = random.randint(cfg.min_len, cfg.max_len)
                run = chr(ord("a") + random.randrange(cfg.alphabet_size))
                if cfg.alphabet_size >= 2:
                    other = chr(ord("a") + random.randrange(cfg.alphabet_size))
                else:
                    other = run
                k = random.randint(0, n)
                word = run * k + other * (n - k)
            else:
                n = random.randint(cfg.min_len, cfg.max_len)
                if cfg.alphabet_size >= 2:
                    period = "".join(
                        random.choice(alphabet) for _ in range(random.randint(1, 3))
                    )
                else:
                    period = alphabet
                reps = max(2, n // max(1, len(period)))
                word = (period * reps)[:n]
                if len(word) < cfg.min_len:
                    word = word + random.choice(alphabet) * (cfg.min_len - len(word))
            factors = _duval(word)
            if factors and _verify_factors(word, factors):
                answer = _factor_answer(factors)
                metadata = edict({
                    "word": word,
                    "alphabet": alphabet,
                    "factors": factors,
                })
                metadata.payload = {
                    "word": word,
                    "alphabet": alphabet,
                }
                metadata["_answer"] = answer
                return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        word = metadata.word
        return (
            f"A Lyndon word is a word that is strictly smaller (in lexicographic order, "
            f"where 'a'<'b'<... ) than every non-trivial rotation of itself. Every word "
            f"has a unique factorization into a sequence of Lyndon words that is "
            f"non-increasing (factor i >= factor i+1 lexicographically); this is called "
            f"the Chen-Fox-Lyndon factorization and Duval's three-way scan computes it "
            f"in linear time. Given the word '{word}', give this factorization as the "
            f"list of its factors in order, separated by single spaces.\n"
            f"The answer is a sequence of words separated by spaces (a factor that "
            f"contains a space appears in double quotes)."
        )

    def score_answer(self, answer, entry):
        expected = _parse_answer(entry.answer)
        got = _parse_answer(answer)
        if got == expected:
            return 1.0
        return 0.0
