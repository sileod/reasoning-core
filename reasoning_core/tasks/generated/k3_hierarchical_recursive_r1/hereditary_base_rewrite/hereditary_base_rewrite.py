import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class HereditaryBaseRewriteConfig(Config):
    base: int = 2
    max_start: int = 8

    def apply_difficulty(self, level):
        self.base = 2 + level // 2
        self.max_start = 4 + level * 2


def _hereditary_repr(n, base):
    if n == 0:
        return "0"
    parts = []
    e = 0
    while n > 0:
        n, d = divmod(n, base)
        if d:
            if e == 0:
                parts.append(str(d))
            elif e == 1:
                parts.append(f"{d}*{base}" if d > 1 else str(base))
            else:
                exp = _hereditary_repr(e, base)
                term = f"{base}^({exp})"
                if d > 1:
                    term = f"{d}*{term}"
                parts.append(term)
        e += 1
    return "+".join(reversed(parts))


def _strip_parens(s):
    s = s.strip()
    if s.startswith("(") and s.endswith(")"):
        depth = 0
        for i, ch in enumerate(s):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    if i == len(s) - 1:
                        return s[1:-1]
                    break
    return s


def _split_top(s, sep):
    depth = 0
    parts = []
    cur = []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == sep and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return parts


def _parse_term(t, base):
    stars = _split_top(t, "*")
    if len(stars) == 1:
        c = 1
        rest = t
    else:
        c = int(stars[0])
        rest = "*".join(stars[1:])
    rest = _strip_parens(rest)
    if "^" in rest:
        bstr, estr = _split_top(rest, "^")
        b = int(bstr)
        return c * (b ** _parse_hereditary(_strip_parens(estr), base))
    if rest.isdigit():
        return c * int(rest)
    return c * _parse_hereditary(rest, base)


def _parse_hereditary(s, base):
    s = s.strip().replace(" ", "")
    if not s or s == "0":
        return 0
    total = 0
    for t in _split_top(s, "+"):
        if t:
            total += _parse_term(t, base)
    return total


def _term_bump(t, base, nb):
    stars = _split_top(t, "*")
    if len(stars) == 1:
        c = 1
        rest = t
    else:
        c = int(stars[0])
        rest = "*".join(stars[1:])
    rest = _strip_parens(rest)
    if "^" in rest:
        bstr, estr = _split_top(rest, "^")
        return c * (nb ** _eval_bump(_strip_parens(estr), base, nb))
    if rest == str(base):
        return c * nb
    return c * int(rest)


def _eval_bump(s, base, nb):
    s = s.strip().replace(" ", "")
    if not s or s == "0":
        return 0
    total = 0
    for t in _split_top(s, "+"):
        if t:
            total += _term_bump(t, base, nb)
    return total


class HereditaryBaseRewrite(Task):
    summary = "Hereditary base-b numerals with recursively expanded exponents: given an integer's hereditary base-b form, apply one Goodstein step (replace the base by b+1 throughout the expression, evaluate, then subtract one) and return the result as a rewritten hereditary base-(b+1) expression."
    design_choice = "Answer as a canonical string expression using digits, parentheses, and caret symbols, with exponents recursively expanded in hereditary form."
    config_cls = HereditaryBaseRewriteConfig

    def generate_entry(self):
        base = self.config.base
        max_start = self.config.max_start
        while True:
            n = random.randint(1, max_start * 40)
            hereditary = _hereditary_repr(n, base)
            new_base = base + 1
            target_val = _eval_bump(hereditary, base, new_base) - 1
            if target_val >= 0:
                break
        ans = _hereditary_repr(target_val, new_base)
        parsed = _parse_hereditary(ans, new_base)
        assert parsed == target_val, (parsed, target_val, ans)
        return Entry(
            metadata={
                "base": base,
                "new_base": new_base,
                "n": n,
                "hereditary": hereditary,
                "target_value": target_val,
                "answer": ans,
            },
            answer=ans,
        )

    def render_prompt(self, metadata):
        return (
            "The hereditary base-"
            + str(metadata["base"])
            + " form of "
            + str(metadata["n"])
            + " is "
            + metadata["hereditary"]
            + ". Apply one Goodstein step: replace every occurrence of "
            + str(metadata["base"])
            + " (including inside exponents) by "
            + str(metadata["new_base"])
            + ", evaluate, then subtract one. Write the result in hereditary base-"
            + str(metadata["new_base"])
            + " form. Answer with the expression only, using non-negative integer "
            "digits, +, *, ^, and parentheses (no spaces, no equals)."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip()
        if not a:
            return 0.0
        gold = entry.answer
        if a.replace(" ", "") == gold.replace(" ", ""):
            return 1.0
        try:
            va = _parse_hereditary(a, entry.metadata["new_base"])
        except Exception:
            return 0.0
        return 1.0 if va == entry.metadata["target_value"] else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'hereditary_base_rewrite (draw 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_hierarchical_recursive_r1/hereditary_base_rewrite',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3867019559,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
