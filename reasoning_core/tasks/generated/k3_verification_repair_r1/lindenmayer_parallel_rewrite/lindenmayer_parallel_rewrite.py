import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class LindenmayerConfig(Config):
    steps: int = 2

    def apply_difficulty(self, level):
        self.steps = 2 + level


SYMBOLS = "ABC"


def _expected_count(initial, productions, terminal_symbol, steps):
    trans = {a: {} for a in SYMBOLS}
    for a in SYMBOLS:
        chosen, probs = productions[a]
        for b, p in zip(chosen, probs):
            trans[a][b] = trans[a].get(b, 0.0) + p
    cur = {s: float(initial[s]) for s in SYMBOLS}
    for _ in range(steps):
        nxt = {s: 0.0 for s in SYMBOLS}
        for a in SYMBOLS:
            for b, w in trans[a].items():
                nxt[b] += cur[a] * w
        cur = nxt
    return cur[terminal_symbol]


TASK_META = {'parent_source_id': None,
 'idea': 'lindenmayer_parallel_rewrite (draw 2 of 3)',
 'hypothesis': 'P012',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_verification_repair_r1/lindenmayer_parallel_rewrite',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 214538085,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


class LindenmayerParallelRewrite(Task):
    summary = "Expand an L-system by replacing every symbol simultaneously for a stated number of steps over mixed constant/rewriting productions, returning the count of a queried symbol in the final string."
    design_choice = "Use probabilistic productions with weighted alternatives, and ask for the count of a queried symbol in the final string."
    config_cls = LindenmayerConfig

    def generate_entry(self):
        steps = self.config.steps
        alphabet = list(SYMBOLS)
        # Pick a queried symbol.
        terminal_symbol = random.choice(alphabet)
        # initial string: each symbol count 0..2, at least one symbol
        initial = {}
        while not any(initial.values()):
            initial = {a: random.randint(0, 2) for a in alphabet}
        initial = {a: c for a, c in initial.items()}

        def sample_productions():
            prods = {}
            for a in alphabet:
                variants = random.choice([2, 3])
                chosen = random.sample(alphabet, variants)
                weights = [random.randint(1, 5) for _ in range(variants)]
                total = float(sum(weights))
                probs = [w / total for w in weights]
                prods[a] = (chosen, probs)
            return prods

        productions = sample_productions()
        # Rejection-sample until expectation is clean, non-negative and discrete.
        for _ in range(2000):
            expect = _expected_count(initial, productions, terminal_symbol, steps)
            ans = int(round(expect))
            if abs(expect - ans) < 0.15 and expect >= 0:
                break
            productions = sample_productions()

        productions_meta = {}
        for a in alphabet:
            chosen, probs = productions[a]
            productions_meta[a] = [f"{s}:{p}" for s, p in zip(chosen, probs)]
        metadata = {
            "alphabet": alphabet,
            "initial": initial,
            "productions": productions_meta,
            "terminal_symbol": terminal_symbol,
            "steps": steps,
            "expected": float(expect),
        }
        answer = str(ans)
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        initial = "".join(s * metadata["initial"][s] for s in SYMBOLS if metadata["initial"][s])
        lines = []
        for a in SYMBOLS:
            opts = []
            for item in metadata["productions"][a]:
                sym, p = item.split(":")
                opts.append(f"{sym} with probability {p}")
            lines.append(f"{a} -> " + ", ".join(opts))
        prod_text = "\n".join(lines)
        terminal = metadata["terminal_symbol"]
        steps = metadata["steps"]
        return (
            f"In an L-system, in a single step every symbol is replaced simultaneously "
            f"according to independent probabilistic productions:\n{prod_text}\n"
            f"Start with the string \"{initial}\". After exactly {steps} step(s), what is the "
            f"expected number of occurrences of the symbol {terminal} in the string? "
            f"Give the expected count as a non-negative integer (round to the nearest integer)."
        )

    def score_answer(self, answer, entry):
        try:
            val = int(str(answer).strip())
        except (ValueError, TypeError):
            return 0.0
        return 1.0 if val == int(entry.answer) else 0.0
