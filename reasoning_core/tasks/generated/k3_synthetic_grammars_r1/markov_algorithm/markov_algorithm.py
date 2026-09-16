import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class MarkovAlgorithmConfig(Config):
    alphabet_size: int = 3
    word_min: int = 6
    word_span: int = 4
    n_rules: int = 4
    max_pat_len: int = 2
    max_del: int = 2
    min_steps: int = 3
    dot_prob: float = 0.2
    step_cap: int = 60
    max_attempts: int = 400

    def apply_difficulty(self, level):
        self.alphabet_size = int(self.alphabet_size + 0.4 * level)
        self.word_min = int(self.word_min + 1.2 * level)
        self.word_span = int(self.word_span + 0.6 * level)
        self.n_rules = int(self.n_rules + 0.8 * level)
        self.max_pat_len = int(self.max_pat_len + 0.5 * level)
        self.max_del = int(self.max_del + 0.4 * level)
        self.min_steps = int(self.min_steps + 0.6 * level)
        self.dot_prob = min(0.45, 0.15 + 0.04 * level)
        self.step_cap = int(self.step_cap + 12 * level)


def _simulate(word, rules, cap):
    """Faithful Markov-algorithm execution.

    Rules are (lhs, rhs, dot) applied in order; at each step the first rule whose
    lhs occurs is taken at its leftmost position, the string is rewritten, and the
    scan restarts from the first rule. A dot rule halts immediately on application;
    the process also halts when no lhs occurs. Returns (steps, fired_indices, halted)
    or None if 'cap' is exceeded (never for the generated length-reducing rules).
    """
    steps = 0
    fired = []
    w = word
    while True:
        matched = False
        for idx, (lhs, rhs, dot) in enumerate(rules):
            pos = w.find(lhs)
            if pos == -1:
                continue
            matched = True
            steps += 1
            if steps > cap:
                return None
            fired.append(idx)
            w = w[:pos] + rhs + w[pos + len(lhs):]
            if dot:
                return steps, fired, True
            break
        if not matched:
            return steps, fired, False


class MarkovAlgorithm(Task):
    summary = ("Execute a Markov algorithm with ordered length-reducing rules and "
               "occasional dot-terminating ones on a word: apply the first matching "
               "rule at the leftmost match, restart from the top, halt on a dot-rule "
               "or no match; answer the total number of rule applications (step count).")
    design_choice = ("Choose output: final word only, step count only, or a canonical "
                     "cycle verdict string like 'CYCLE' when no halt occurs.")
    config_cls = MarkovAlgorithmConfig

    def generate_entry(self):
        cfg = self.config
        alphabet = "abcde"[:cfg.alphabet_size]
        for _ in range(cfg.max_attempts):
            wlen = random.randint(cfg.word_min, cfg.word_min + cfg.word_span)
            word = "".join(random.choice(alphabet) for _ in range(wlen))
            rules = []
            for _ in range(cfg.n_rules):
                plen = random.randint(1, cfg.max_pat_len)
                lhs = "".join(random.choice(alphabet) for _ in range(plen))
                rhs_len = random.randint(0, plen - 1)
                rhs = "".join(random.choice(alphabet) for _ in range(rhs_len))
                dot = random.random() < cfg.dot_prob
                if (lhs, rhs, dot) not in rules:
                    rules.append((lhs, rhs, dot))
            if not rules:
                continue
            out = _simulate(word, rules, cfg.step_cap)
            if out is None:
                continue
            steps, fired, halted = out
            distinct_fired = len(set(fired))
            if steps < cfg.min_steps or distinct_fired < 2:
                continue
            metadata = {
                "alphabet": "".join(sorted(alphabet)),
                "word": word,
                "rules": [[lhs, rhs, dot] for lhs, rhs, dot in rules],
                "steps": steps,
                "halted": halted,
                "fired": fired,
            }
            return Entry(metadata=metadata, answer=str(steps))
        raise RuntimeError("markov_algorithm: failed to generate a non-trivial instance")

    def render_prompt(self, metadata):
        rules_lines = []
        for i, (lhs, rhs, dot) in enumerate(metadata.rules, start=1):
            arrow = "-> ." if dot else "-> "
            rules_lines.append(f"{i}. {lhs} {arrow}{rhs}".rstrip())
        rules_text = "\n".join(rules_lines)
        return (
            f"This is a Markov algorithm over the alphabet {metadata.alphabet}.\n"
            "It rewrites strings. Apply the rules below in order (rule 1 first). "
            "At each step, take the first rule whose left side occurs; replace its "
            "leftmost occurrence with the right side, then restart from rule 1. "
            "A rule written 'lhs -> .rhs' halts the algorithm when it is applied; the "
            "algorithm also halts when no rule's left side occurs.\n"
            "Rules:\n"
            f"{rules_text}\n"
            f"Start word: {metadata.word}\n"
            "How many rule applications happen before the algorithm halts? "
            "Answer with a single integer (the step count)."
        )

    def score_answer(self, answer, entry):
        return 1.0 if str(answer).strip() == str(entry.answer).strip() else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'markov_algorithm_execution (draw 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_synthetic_grammars_r1/markov_algorithm_execution',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
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
