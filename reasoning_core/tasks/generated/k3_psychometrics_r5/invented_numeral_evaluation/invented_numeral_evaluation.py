import collections
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class InventedNumeralConfig(Config):
    base_morphemes: int = 3
    max_string_len: int = 3
    bound: int = 1000

    def apply_difficulty(self, level):
        self.base_morphemes = min(stochastic_rounding(3 + level), 5)
        self.max_string_len = stochastic_rounding(2 + level // 2)
        self.bound = stochastic_rounding(500 + level * 500)


def _parse(s, morph_map):
    if not s:
        return 0
    val_list = [morph_map[ch] for ch in s]
    total = 0
    i = 0
    while i < len(val_list):
        if i + 1 < len(val_list) and val_list[i] < val_list[i + 1]:
            total += val_list[i + 1] - val_list[i]
            i += 2
        else:
            total += val_list[i]
            i += 1
    return total


def _all_valid_strings(morphemes, max_len):
    syms = sorted(set(sym for sym, _ in morphemes))
    morph_map = {sym: val for sym, val in morphemes}
    valid = {}

    def gen(prefix, vals):
        if prefix:
            if len(prefix) <= max_len:
                valid[prefix] = _parse(prefix, morph_map)
        if len(prefix) >= max_len:
            return
        for s in syms:
            gen(prefix + s, vals + [morph_map[s]])

    gen("", [])
    return valid


def _canonical(value, morphemes):
    syms_by_val = sorted(morphemes, key=lambda r: -r[1])
    if value == 0:
        return ""
    for sym, val in syms_by_val:
        if value == val:
            return sym
    return None


def _all_shortest(value, valid):
    best = None
    for k, v in valid.items():
        if v == value and k:
            if best is None or len(k) < len(best) or (len(k) == len(best) and k < best):
                best = k
    return best


def _describe(morphemes):
    return ", ".join(f"{sym}={val}" for sym, val in morphemes)


class InventedNumeralEvaluation(Task):
    summary = "Evaluate and generate invented numeral systems built from stipulated additive and subtractive morpheme rules; answers give a string's value, the canonical string for a value, or a well-formedness verdict."
    config_cls = InventedNumeralConfig
    design_choice = "Generate instances by fixing a random base set of 3-5 numeral morphemes with arbitrary numeric values, then derive all valid strings up to a bound; questions ask value, canonical form, or validity."
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        mode = random.choice(["value", "canonical", "valid"])
        while True:
            n = cfg.base_morphemes
            big = random.randint(50, 500)
            smalls = sorted(random.sample(range(2, 50), n - 1), reverse=True)
            values = [big] + smalls
            random.shuffle(values)
            morphemes = [(chr(ord('A') + i), values[i]) for i in range(n)]
            valid = _all_valid_strings(morphemes, cfg.max_string_len)
            if len(valid) >= 6:
                break
            if n > cfg.base_morphemes * 2:
                raise RuntimeError("could not build numeral system")

        valid_nonempty = [k for k in valid if k]
        if not valid_nonempty:
            valid_nonempty = [sym for sym, _ in morphemes]

        if mode == "value":
            s = random.choice(valid_nonempty)
            expected = valid[s]
            return Entry(
                metadata={"mode": mode, "morphemes": morphemes, "s": s},
                answer=str(expected),
            )

        if mode == "canonical":
            value = random.choice([v for v in set(valid.values()) if v > 0])
            canon = _all_shortest(value, valid)
            if canon is None:
                canon = _canonical(value, morphemes)
            if canon is None:
                canon = "".join(sym for sym, _ in sorted(morphemes, key=lambda r: r[1]))[:2]
            return Entry(
                metadata={"mode": mode, "morphemes": morphemes, "value": value},
                answer=canon,
            )

        big_sym = max(morphemes, key=lambda r: r[1])[0]
        alphabet = [sym for sym, _ in morphemes]
        nonbig = [a for a in alphabet if a != big_sym]
        if random.random() < 0.5:
            filler = [random.choice(nonbig) for _ in range(random.randint(0, max(cfg.max_string_len - 2, 0)))]
            s = big_sym + "".join(filler) + big_sym
            truth = False
        else:
            rest = [random.choice(nonbig) for _ in range(random.randint(0, cfg.max_string_len - 1))]
            s = big_sym + "".join(rest)
            truth = True
        return Entry(
            metadata={"mode": mode, "morphemes": morphemes, "s": s, "big_sym": big_sym},
            answer="yes" if truth else "no",
        )

    def render_prompt(self, metadata):
        morphemes = metadata["morphemes"]
        described = ", ".join(f"{sym}={val}" for sym, val in morphemes)
        intro = (
            f"Numeral system: each symbol has the value: {described}. Reading left to right, "
            f"if a symbol's value is smaller than the following symbol's value, subtract it from "
            f"the next symbol; otherwise add it."
        )
        mode = metadata["mode"]
        if mode == "value":
            return (
                f"{intro} What integer does the string '{metadata['s']}' equal? "
                f"Answer one integer."
            )
        if mode == "canonical":
            return (
                f"{intro} The value {metadata['value']} has a canonical shortest string "
                f"(fewest symbols, and among ties the one first in alphabet order). "
                f"What is it? Answer the string."
            )
        big_sym = metadata.get("big_sym")
        big_rule = (
            f" The symbol '{big_sym}' is a landmark that may appear at most once in any "
            f"well-formed string."
            if big_sym
            else ""
        )
        return (
            f"{intro}{big_rule} Is '{metadata['s']}' a well-formed string of this system? "
            f"Answer yes or no."
        )

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        mode = entry.metadata["mode"]
        ans = answer.strip()
        if mode == "valid":
            return 1.0 if ans == entry.answer else 0.0
        if mode == "value":
            try:
                return 1.0 if int(ans) == int(entry.answer) else 0.0
            except ValueError:
                return 0.0
        return 1.0 if ans == entry.answer else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'invented_numeral_evaluation (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_psychometrics_r5/invented_numeral_evaluation',
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
