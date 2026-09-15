"""CYK chart membership: fill a recognition chart of a small CNF grammar.

The task generates a small Chomsky-normal-form grammar over a short terminal
string, runs the CYK recognition algorithm, and asks for either the sorted
nonterminals of a queried span cell or the total number of distinct
derivations (parses) of the string.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class CykChartMembershipV3Config(Config):
    num_terminals: int = 2
    num_nonterminals: int = 3
    string_len: int = 4
    max_rules: int = 8

    def apply_difficulty(self, level):
        self.num_nonterminals = 3 + level // 2
        self.string_len = 4 + level
        self.max_rules = 8 + 2 * level


def _make_string_and_grammar(cfg):
    """Build a grammar together with a guaranteed-derivable string.

    Returns (terminals, nonterm, binary_rules, unary_rules, string, ways)."""
    start = "S"
    nonterm = [start]
    while len(nonterm) < cfg.num_nonterminals:
        cand = "N" + str(len(nonterm))
        nonterm.append(cand)

    terminals = ["a", "b", "c", "d"][:cfg.num_terminals]
    n = cfg.string_len

    binary_rules = {}
    unary_rules = {}

    out_chars = [None] * n

    def build(lo, hi, root):
        # Recursively assign productions so span [lo, hi) derives, returning
        # the nonterminal at the root of that span. If hi-lo == 1 pick a
        # terminal character.
        if hi - lo == 1:
            t = random.choice(terminals)
            out_chars[lo] = t
            unary_rules[(root, t)] = True
            return
        mid = random.randint(lo + 1, hi - 1)
        B = random.choice(nonterm)
        C = random.choice(nonterm)
        binary_rules[(root, B, C)] = True
        build(lo, mid, B)
        build(mid, hi, C)

    build(0, n, start)
    string = "".join(out_chars)

    # Extra structural variety: add a handful of random binary and unary rules
    # so the grammar is not fully determined by the constructed tree.
    extra = max(2, cfg.max_rules // 3)
    for _ in range(extra):
        A = random.choice(nonterm)
        B = random.choice(nonterm)
        C = random.choice(nonterm)
        binary_rules[(A, B, C)] = True
        if random.random() < 0.4:
            unary_rules[(A, random.choice(terminals))] = True

    return terminals, nonterm, list(binary_rules.keys()), list(unary_rules), string


def _cyk(terminals, nonterm, binary_rules, unary_rules, string):
    """Return (chart, deriv_count). chart[i][j] is set of nonterms spanning
    string[i:j] (length j-i). deriv_count counts distinct parse trees for the
    whole string using a DP over spans."""
    n = len(string)
    unary = {}
    for (A, t) in unary_rules:
        unary.setdefault(t, set()).add(A)

    bin_by_B = {}
    for (A, B, C) in binary_rules:
        bin_by_B.setdefault(B, []).append((A, C))

    chart = [[set() for _ in range(n + 1)] for _ in range(n)]

    # Derivations DP: ways[i][j] dict nonterminal -> count
    ways = [[{} for _ in range(n + 1)] for _ in range(n)]

    for i in range(n):
        t = string[i]
        for A in unary.get(t, ()):
            chart[i][i + 1].add(A)
            ways[i][i + 1][A] = 1

    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length
            for k in range(i + 1, j):
                for B in chart[i][k]:
                    for (A, C) in bin_by_B.get(B, ()):
                        if C in chart[k][j]:
                            chart[i][j].add(A)
                            nb = ways[i][k].get(B, 0)
                            nc = ways[k][j].get(C, 0)
                            ways[i][j][A] = ways[i][j].get(A, 0) + nb * nc

    return chart, ways


class CykChartMembership(Task):
    summary = ("Fill the CYK recognition chart of a small Chomsky-normal-form "
               "grammar over a short terminal string, returning the sorted "
               "nonterminals of a queried span cell or the total derivation count.")
    config_cls = CykChartMembershipV3Config

    def generate_entry(self):
        terminals, nonterm, binary_rules, unary_rules, string = _make_string_and_grammar(self.config)
        n = self.config.string_len

        chart, ways = _cyk(terminals, nonterm, binary_rules, unary_rules, string)
        # S must derive the whole string by construction.
        assert "S" in chart[0][n] and ways[0][n].get("S", 0) >= 1

        # Choose a balanced query: count the parses, list a content cell, or a
        # confirmed-empty cell.
        query_type = random.choice(
            ["count"] * 2 + ["cell"] + ["empty"])

        if query_type == "cell":
            candidates = []
            for i in range(n):
                for j in range(i + 1, n + 1):
                    if chart[i][j] and not (i == 0 and j == n):
                        candidates.append((i, j))
            if not candidates:
                query_type = "count"
            else:
                i, j = random.choice(candidates)

        if query_type == "empty":
            empties = [(a, b) for a in range(n) for b in range(a + 1, n + 1)
                       if not chart[a][b]]
            if not empties:
                query_type = "count"

        if query_type == "count":
            total = ways[0][n].get("S", 0)
            answer_str = str(total)
            metadata = {
                "terminals": terminals,
                "nonterminals": nonterm,
                "binary_rules": [[A, B, C] for (A, B, C) in binary_rules],
                "unary_rules": [[A, t] for (A, t) in unary_rules],
                "string": string,
                "query_type": "count",
                "deriv_count": total,
            }
        elif query_type == "cell":
            answer = sorted(chart[i][j])
            answer_str = " ".join(answer)
            metadata = {
                "terminals": terminals,
                "nonterminals": nonterm,
                "binary_rules": [[A, B, C] for (A, B, C) in binary_rules],
                "unary_rules": [[A, t] for (A, t) in unary_rules],
                "string": string,
                "query_type": "cell",
                "span": [i, j],
                "cell": sorted(chart[i][j]),
            }
        else:
            i, j = random.choice(empties)
            answer_str = "EMPTY"
            metadata = {
                "terminals": terminals,
                "nonterminals": nonterm,
                "binary_rules": [[A, B, C] for (A, B, C) in binary_rules],
                "unary_rules": [[A, t] for (A, t) in unary_rules],
                "string": string,
                "query_type": "cell",
                "span": [i, j],
                "cell": [],
            }

        return Entry(metadata=metadata, answer=answer_str)

    def render_prompt(self, metadata):
        return "\n".join(_render_prompt_lines(metadata))

    def score_answer(self, answer, entry):
        metadata = entry.metadata
        query_type = metadata["query_type"]
        gold = entry.answer
        if query_type == "cell":
            return 1.0 if answer == gold else 0.0
        # count: accept canonical int spelling, trim whitespace
        return 1.0 if answer.strip() == gold else 0.0


def _render_prompt_lines(metadata):
    m = metadata
    lines = [
        "A small grammar in Chomsky normal form is given:",
    ]
    rules = []
    for A, t in m["unary_rules"]:
        rules.append(f"{A} -> {t}")
    for A, B, C in m["binary_rules"]:
        rules.append(f"{A} -> {B} {C}")
    # sort rules for determinism
    rules.sort()
    lines.extend(rules)
    lines.append("")
    lines.append(f"The input terminal string is: {m['string']}")
    lines.append("")
    if m["query_type"] == "cell":
        i, j = m["span"]
        lines.append(
            f"Run CYK recognition on this string. A chart cell is indexed "
            f"by an interval [a, b) of string positions. Write down the "
            f"nonterminals in the cell for the interval [{i}, {j}); an "
            f"empty cell is recorded as the single word EMPTY. List the "
            f"nonterminals in sorted lexicographic order."
        )
    else:
        lines.append(
            "Run CYK recognition on this string and count the total number "
            "of distinct derivation trees (parses) of the whole string "
            "rooted at the start symbol S. Answer with that count as a "
            "non-negative integer."
        )
    return lines


TASK_META = {'parent_source_id': None,
 'idea': 'cyk_chart_membership (draw 3 of 3, unguided baseline)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_invariants_r1/cyk_chart_membership',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 4238614268,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
