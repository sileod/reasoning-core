import random
import string
from dataclasses import dataclass, field

from reasoning_core.template import Config, Entry, Task

LETTERS = string.ascii_lowercase[:6]


def simulate(word, m, prods, max_steps):
    """Apply Post tag-system productions until the word shrinks below m or max_steps.

    Returns (final_word, applied_steps, halted).
    """
    word = list(word)
    steps = 0
    while len(word) >= m and steps < max_steps:
        head = word[0]
        tail = word[m:]
        tail.extend(prods[head])
        word = tail
        steps += 1
    halted = len(word) < m
    return "".join(word), steps, halted


def _pick_alpha(rng_size):
    return random.sample(LETTERS, rng_size)


def _random_word(alpha, lo, hi):
    n = random.randint(lo, hi)
    return "".join(random.choice(alpha) for _ in range(n))


@dataclass
class PostTagConfig(Config):
    alphabet_size: int = 3
    m: int = 2
    word_len: tuple = field(default_factory=lambda: (3, 6))
    prod_len: tuple = field(default_factory=lambda: (1, 3))
    max_steps: int = 40
    k_lo_hi: tuple = field(default_factory=lambda: (1, 5))

    def apply_difficulty(self, level):
        self.alphabet_size = min(5, 2 + level)
        self.m = random.choice([1, 2, 3])
        self.word_len = (2 + level, 4 + 2 * level)
        self.prod_len = (1, 2 + level // 2)
        self.max_steps = 20 + 8 * level
        self.k_lo_hi = (1, 2 + level)


class PostTagSystemEvolution(Task):
    summary = ("Simulate Post tag systems: delete the first m symbols, append the "
               "production keyed by the consumed head symbol; vary m, alphabet, and "
               "productions; answer the word after k steps, halting outcome, or "
               "steps-to-halt.")
    design_choice = ("ask for the exact word after k steps, the step count until "
                     "halting, or the halting symbol/empty-word outcome, with k "
                     "chosen to avoid triviality.")
    config_cls = PostTagConfig

    def generate_entry(self):
        c = self.config
        alpha = _pick_alpha(c.alphabet_size)
        symbols = sorted(alpha)
        while True:
            prods = {}
            for s in symbols:
                pl = random.randint(*c.prod_len)
                prods[s] = _random_word(alpha, 1, pl) if random.random() < 0.9 else ""
            word0 = _random_word(alpha, *c.word_len)
            max_steps = c.max_steps
            _, steps, halted = simulate(word0, c.m, prods, max_steps)
            if steps >= max_steps and not halted:
                continue
            break

        mode = random.choice(["word_after", "steps_halt", "outcome"])

        if mode == "word_after":
            k = random.randint(*c.k_lo_hi)
            cutoff = min(k, steps)
            wordk, _, hk = simulate(word0, c.m, prods, cutoff)
            assert wordk == simulate(word0, c.m, prods, cutoff)[0]
            if wordk == "":
                answer = "empty"
            else:
                answer = wordk
            prompt_mode = ("what the word is after exactly {k} steps; if the system "
                           "halts earlier the word stays at its halting word").format(k=k)
            meta_mode = "word_after"
            q = {"kind": "word_after", "k": k}
        elif mode == "steps_halt":
            if not halted:
                return self.generate_entry()
            assert steps >= 0
            answer = str(steps)
            prompt_mode = ("how many production steps are applied before the word "
                           "shrinks below {m} symbols and the system halts").format(m=c.m)
            meta_mode = "steps_halt"
            q = {"kind": "steps_halt"}
        else:
            if not halted:
                return self.generate_entry()
            wordf = simulate(word0, c.m, prods, max_steps)[0]
            if wordf == "":
                answer = "empty"
            else:
                answer = wordf
            prompt_mode = "what the final (halting) word is; if it becomes empty answer exactly: empty"
            meta_mode = "outcome"
            q = {"kind": "outcome"}

        prods_str = "; ".join("%s -> %r" % (s, prods[s]) for s in symbols)
        metadata = {
            "m": int(c.m),
            "alphabet": [s for s in symbols],
            "productions": {s: prods[s] for s in symbols},
            "word0": word0,
            "mode": meta_mode,
            "k": int(q.get("k", 0)),
            "steps": int(steps),
            "halted": bool(halted),
            "answer": answer,
            "prods_str": prods_str,
            "prompt_mode": prompt_mode,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return (
            "A Post tag system has a deletion number m={m} and a production for each "
            "alphabet symbol. At every step it reads the first (head) symbol, deletes "
            "the first m symbols, and appends the production of the head symbol. It "
            "halts exactly when the word has fewer than m symbols. Alphabet = "
            "{alpha}, productions: {prods}. Start word: {w}.\n\n"
            "Using the standard simulation of a tag system, answer {mode}.\n"
            "Give only the answer: an exact string of letters (type \"empty\" for the "
            "empty word) when the answer is a word, or the integer step count when "
            "asked for steps."
        ).format(
            m=metadata["m"],
            alpha=metadata["alphabet"],
            prods=metadata["prods_str"],
            w=metadata["word0"],
            mode=metadata["prompt_mode"],
        )

    def score_answer(self, answer, entry):
        meta = entry.metadata
        if meta["mode"] in ("word_after", "outcome"):
            return 1.0 if answer.strip() == meta["answer"] else 0.0
        try:
            return 1.0 if int(str(answer).strip()) == int(meta["answer"]) else 0.0
        except (ValueError, TypeError):
            return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'post_tag_system_evolution (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_synthetic_grammars_r4/post_tag_system_evolution',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
