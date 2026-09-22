"""Solve word equations over concatenation.

A word equation has two sides over a string alphabet plus variables. We search
for a substitution binding each variable to a concrete string (possibly empty)
such that the two sides become equal strings.

Three answer regimes:
  mode = "unique"    -> the unique substitution: variables in sorted (ascending)
                        order joined as `var=string` with commas; empty string
                        written as `var=` (nothing after the equals).
  mode = "solutions" -> the number of distinct substitutions (each a tuple of
                        binding strings) under a length cap C; a non-negative
                        integer.
  mode = "unsat"     -> the literal answer "unsat" when no substitution works.

In the "unique" and "unsat" modes the generator brute-force search verifies the
answer, so it never claims uniqueness or unsatisfiability it did not check.
"""

import random
import itertools
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class WordEquationConfig(Config):
    num_vars: int = 2
    const_alphabet: int = 2
    max_binding: int = 3
    solution_cap: int = 3
    max_len: int = 5

    def apply_difficulty(self, level):
        # keep the exhaustive solver affordable: num_vars, alphabet and binding
        # cap stay small; structural depth comes from longer, more-interleaved
        # equations.
        self.num_vars = 2 + stochastic_rounding(min(level, 2) / 2)
        self.const_alphabet = 2 + stochastic_rounding(min(level, 1) / 1)
        self.max_binding = 2 + stochastic_rounding(min(level, 1) / 1)
        self.solution_cap = self.max_binding
        self.max_len = 4 + level


def _all_words(alphabet, cap):
    yield ""
    for length in range(1, cap + 1):
        for tup in itertools.product(alphabet, repeat=length):
            yield "".join(tup)


def _render_side(w, binding):
    return "".join(binding.get(ch, ch) if ch in binding else ch for ch in w)


def _solves(lhs, rhs, var_syms, binding):
    return _render_side(lhs, binding) == _render_side(rhs, binding)


def _search_unique(lhs, rhs, var_syms, alphabet, cap):
    words = list(_all_words(alphabet, cap))
    found = []
    for combo in itertools.product(words, repeat=len(var_syms)):
        binding = dict(zip(var_syms, combo))
        if _solves(lhs, rhs, var_syms, binding):
            found.append(combo)
    return found


class WordEquationSolving(Task):
    summary = ("Solve word equations over concatenation: align constant-and-variable sides, "
               "propagate end-symbol and length constraints to bind variables; answers are the "
               "unique substitution, all solutions under a length cap, or a contradiction.")
    config_cls = WordEquationConfig

    def _rand_word(self, alphabet):
        n = random.randint(0, self.config.max_len)
        return "".join(random.choice(alphabet) for _ in range(n))

    def _construct_satisfiable(self, alphabet, var_syms):
        # every variable must appear at least once so counts/unicity come from
        # real structure, not from free (unused) variables.
        parts = list(var_syms)
        for _ in range(random.randint(0, max(2, self.config.max_len))):
            if random.random() < 0.55:
                parts.append(random.choice(alphabet))
            else:
                parts.append(random.choice(var_syms))
        random.shuffle(parts)
        lhs = "".join(parts)
        binding = {
            v: "".join(random.choice(alphabet) for _ in range(random.randint(0, self.config.max_binding)))
            for v in var_syms
        }
        rhs = "".join(binding.get(ch, ch) if ch in binding else ch for ch in lhs)
        return lhs, rhs, var_syms, binding

    def _construct_unsat(self, alphabet, var_syms):
        # distinct leading constant on each side forces inequality for every binding:
        #   a T1 = b T2  with a != b
        a = random.choice(alphabet)
        b = random.choice([c for c in alphabet if c != a])
        def fill():
            parts = []
            for _ in range(random.randint(0, max(2, self.config.max_len))):
                if random.random() < 0.5:
                    parts.append(random.choice(alphabet))
                else:
                    parts.append(random.choice(var_syms))
            return "".join(parts)
        lhs = a + fill()
        rhs = b + fill()
        return lhs, rhs, var_syms, {}

    def _construct_split(self, alphabet, var_syms):
        # variables placed adjacently equal a random constant word: counting the
        # bounded compositions of |W| into |vars| parts is a genuine multi-solution
        # reasoning problem and never collapses to one solution.
        wlen = random.randint(1, self.config.max_len)
        W = "".join(random.choice(alphabet) for _ in range(wlen))
        lhs = "".join(var_syms)
        rhs = W
        return lhs, rhs, var_syms, {}

    def _roll_mode(self):
        r = random.random()
        if r < 1 / 3:
            return "unique"
        if r < 2 / 3:
            return "solutions"
        return "unsat"

    def generate_entry(self):
        alphabet = [chr(97 + i) for i in range(self.config.const_alphabet)]
        cap = self.config.max_binding
        var_syms = [chr(122 - i) for i in range(self.config.num_vars)]

        target = self._roll_mode()
        attempts = 0
        while attempts < 40000:
            attempts += 1
            if target == "unsat":
                lhs, rhs, _, _ = self._construct_unsat(alphabet, var_syms)
            elif target == "solutions":
                lhs, rhs, _, _ = self._construct_split(alphabet, var_syms)
            else:
                lhs, rhs, _, _ = self._construct_satisfiable(alphabet, var_syms)
            count = len(_search_unique(lhs, rhs, var_syms, alphabet, cap))
            got = "unsat" if count == 0 else ("unique" if count == 1 else "solutions")
            if got == target:
                if target == "unsat":
                    answer = "unsat"
                elif target == "unique":
                    sols = _search_unique(lhs, rhs, var_syms, alphabet, cap)
                    binding = dict(zip(var_syms, sols[0]))
                    answer = ",".join("%s=%s" % (v, binding[v]) for v in sorted(var_syms))
                    assert _solves(lhs, rhs, var_syms, binding)
                else:
                    answer = str(count)
                    assert count >= 1
                break
        else:
            raise RuntimeError("word_equation: could not realize target mode %s" % target)

        metadata = {
            "lhs": lhs,
            "rhs": rhs,
            "vars": var_syms,
            "alphabet": "".join(alphabet),
            "mode": target,
            "max_binding": cap,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lhs = metadata["lhs"]
        rhs = metadata["rhs"]
        vars_str = ", ".join(metadata["vars"])
        alpha = metadata["alphabet"]
        cap = metadata["max_binding"]
        mode = metadata["mode"]
        if mode == "unique":
            return (
                f"We have a word equation over the alphabet {{{alpha}}}. The variables are "
                f"({vars_str}); each is to be replaced by a string of length at most {cap} "
                f"(possibly empty) over {{{alpha}}}. There is exactly one substitution that makes "
                f"{lhs} = {rhs} hold as concatenated strings. Find it and give each binding as "
                f"var=string in alphabetical order of the variable names, entries separated by "
                f"commas; the empty string is written as var= with nothing after the equals sign. "
                f"Example: a=,b=ba would bind a to the empty string and b to ba."
            )
        if mode == "solutions":
            return (
                f"We have a word equation over the alphabet {{{alpha}}}. The variables are "
                f"({vars_str}); each is to be replaced by a string of length at most {cap} "
                f"(possibly empty) over {{{alpha}}}. How many distinct substitutions make "
                f"{lhs} = {rhs} hold as concatenated strings? Answer with that count, a single "
                f"non-negative integer."
            )
        return (
            f"We have a word equation over the alphabet {{{alpha}}}. The variables are "
            f"({vars_str}); each would be replaced by a string of length at most {cap} "
            f"(possibly empty) over {{{alpha}}}. Determine whether any substitution of the "
            f"variables makes {lhs} = {rhs} hold as concatenated strings. If none works, "
            f"answer unsat; otherwise answer satisfiable."
        )

    def score_answer(self, answer, entry):
        return _score(answer, entry)


def _norm_ws(s):
    return "".join(s.split())


def _score(answer, entry):
    if not isinstance(answer, str):
        return 0.0
    mode = entry.metadata["mode"]
    gold = entry.answer
    if mode == "unsat":
        return 1.0 if _norm_ws(answer).lower() == "unsat" else 0.0
    if mode == "solutions":
        a = _norm_ws(answer)
        return 1.0 if a == gold else 0.0
    # unique: compare canonical substitution strings, case of letters preserved
    resp = _norm_ws(answer)
    # normalize comma separation
    resp = resp.replace(" ", "")
    return 1.0 if resp == gold.replace(" ", "") else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'word_equation_solving (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_synthetic_grammars_r4/word_equation_solving',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1618848011,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
