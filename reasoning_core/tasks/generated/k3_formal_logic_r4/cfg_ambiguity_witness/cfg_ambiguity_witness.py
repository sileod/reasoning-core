import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'cfg_ambiguity_witness (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_formal_logic_r4/cfg_ambiguity_witness',
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

_TERMINALS = ["a", "b", "c"]
_NTS = ["A", "B"]


def _apply_rules(sent, rules):
    derivs = set()
    for i, sym in enumerate(sent):
        alts = rules.get(sym)
        if alts:
            for rhs in alts:
                derivs.add(sent[:i] + tuple(rhs) + sent[i + 1:])
    return derivs


def _all_sentential_forms(start, rules, terminals, max_len, budget):
    by_len = {}
    frontier = {(start,)}
    visited = set()
    count = 0
    while frontier:
        nxt = set()
        for s in frontier:
            if s in visited or len(s) > max_len:
                continue
            visited.add(s)
            count += 1
            if count > budget:
                return None
            if all(c in terminals for c in s):
                by_len.setdefault(len(s), set()).add(s)
            else:
                d = set()
                for i, sym in enumerate(s):
                    alts = rules.get(sym)
                    if alts:
                        for rhs in alts:
                            ns = s[:i] + tuple(rhs) + s[i + 1:]
                            if len(ns) <= max_len:
                                d.add(ns)
                nxt |= d
        frontier = nxt
    return by_len


def _num_parse_trees(word, rules, terminals):
    n = len(word)
    if n == 0:
        return 0
    table = [[{} for _ in range(n)] for _ in range(n)]
    for i in range(n):
        c = word[i]
        cnt = {}
        for nt, alts in rules.items():
            for rhs in alts:
                if len(rhs) == 1 and rhs[0] == c:
                    cnt[nt] = cnt.get(nt, 0) + 1
        table[0][i] = cnt
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            cnt = {}
            for k in range(i, i + length - 1):
                left = table[k - i][i]
                right = table[i + length - 1 - k - 1][k + 1]
                for la, lv in left.items():
                    for ra, rv in right.items():
                        for nt, alts in rules.items():
                            for rhs in alts:
                                if len(rhs) == 2 and rhs[0] == la and rhs[1] == ra:
                                    cnt[nt] = cnt.get(nt, 0) + lv * rv
            table[length - 1][i] = cnt
    return sum(table[n - 1][0].values())


def _analyze(rules, terminals, start, max_len, budget):
    by_len = _all_sentential_forms(start, rules, terminals, max_len, budget)
    if by_len is None:
        return None, None
    for l in sorted(by_len):
        for w in sorted(by_len[l]):
            if _num_parse_trees(w, rules, terminals) >= 2:
                return l, w
    return None, None


def _guaranteed_ambiguous(rng):
    chosen = sorted(rng.sample(_TERMINALS, 2))
    p = rng.choice(chosen)
    rules = {
        "S": [("A",)],
        "A": [("X",), ("Y",)],
        "X": [(p,)],
        "Y": [(p,)],
    }
    return chosen, ["S", "A", "X", "Y"], "S", rules


def _random_grammar(rng):
    chosen = [rng.choice(_TERMINALS) for _ in range(rng.randint(2, 3))]
    chosen = sorted(set(chosen))[:2]
    while len(chosen) < 2:
        chosen.append(rng.choice([c for c in _TERMINALS if c not in chosen]))
    chosen = chosen[:2]
    start = "S"
    all_nt = [start] + _NTS
    rules = {}
    for nt in all_nt:
        k = rng.randint(1, 2)
        alts = []
        for _ in range(k):
            ln = rng.randint(1, 2)
            rhs = []
            for _ in range(ln):
                if rng.random() < 0.55:
                    rhs.append(rng.choice(chosen))
                else:
                    rhs.append(rng.choice(all_nt))
            alts.append(tuple(rhs))
        rules[nt] = alts
    return chosen, all_nt, start, rules


@dataclass
class CFGAmbiguityConfig(Config):
    max_len: int = 4
    budget: int = 4000

    def apply_difficulty(self, level):
        self.max_len = 3 + level
        self.budget = 1500 + 800 * level


class CFGAmbiguityWitness(Task):
    summary = ("Search a small context-free grammar's derivations for ambiguity: enumerate sentential forms "
               "by length to find the shortest word with two distinct parse trees, or certify unambiguity up to "
               "the checked bound. Yes/no answers with a witnessed word for ambiguous cases.")
    config_cls = CFGAmbiguityConfig
    task_version = 2

    def generate_entry(self):
        max_len = self.config.max_len
        budget = self.config.budget
        for _ in range(40):
            want_yes = random.random() < 0.5
            if want_yes:
                chosen, all_nt, start, rules = _random_grammar(random)
                l, w = _analyze(rules, set(chosen), start, max_len, budget)
                if w is None:
                    chosen, all_nt, start, rules = _guaranteed_ambiguous(random)
                    l, w = _analyze(rules, set(chosen), start, max_len, budget)
                if w is not None:
                    assert w and all(c in chosen for c in w)
                    return Entry(
                        metadata={
                            "rules": {k: [list(r) for r in v] for k, v in rules.items()},
                            "terminals": sorted(chosen),
                            "start": start,
                            "max_len": max_len,
                            "word": "".join(w),
                            "min_word_len": l,
                            "ambiguous": True,
                        },
                        answer="yes " + "".join(w),
                    )
            else:
                chosen, all_nt, start, rules = _random_grammar(random)
                l, w = _analyze(rules, set(chosen), start, max_len, budget)
                if w is None:
                    return Entry(
                        metadata={
                            "rules": {k: [list(r) for r in v] for k, v in rules.items()},
                            "terminals": sorted(chosen),
                            "start": start,
                            "max_len": max_len,
                            "word": None,
                            "min_word_len": None,
                            "ambiguous": False,
                        },
                        answer="no",
                    )
        raise RuntimeError("cfg ambiguity generation failed")

    def render_prompt(self, metadata):
        def fmt_rules(rules):
            return "\n".join(f"{nt} -> {' | '.join(''.join(x) for x in alts)}"
                             for nt, alts in rules.items())

        block = fmt_rules(metadata["rules"])
        term = "".join(metadata["terminals"])
        return (
            f"Consider the context-free grammar with start symbol {metadata['start']} over the "
            f"terminal alphabet {{{term}}}:\n{block}\n\n"
            f"Search the grammar's derivations for ambiguity. A word is unambiguous if every derivation "
            f"of it gives the same parse tree; the grammar is ambiguous if some word has two distinct parse "
            f"trees. Enumerate sentential forms by length to find the shortest word (of length at most "
            f"{metadata['max_len']}) with two distinct parse trees. If the grammar is ambiguous, answer with "
            f"'yes <word>' giving that shortest word; otherwise answer 'no' (no ambiguous word up to length "
            f"{metadata['max_len']}). Example format: 'yes abab' or 'no'."
        )

    def score_answer(self, answer, entry):
        meta = entry.metadata
        if meta["ambiguous"]:
            ans = answer.strip()
            if not ans.lower().startswith("yes"):
                return 0.0
            rest = ans[3:].strip().lower()
            return 1.0 if rest == meta["word"].lower() else 0.0
        else:
            return 1.0 if answer.strip().lower() == "no" else 0.0
