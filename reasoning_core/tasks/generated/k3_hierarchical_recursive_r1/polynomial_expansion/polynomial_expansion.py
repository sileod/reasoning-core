import random
import re
from dataclasses import dataclass

import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'polynomial_expansion (draw 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_hierarchical_recursive_r1/polynomial_expansion',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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

_transformations = standard_transformations + (implicit_multiplication_application,)


def _expand(expr_str):
    expr = parse_expr(expr_str, transformations=_transformations)
    return sympy.expand(expr)


def _answer_str(expr):
    return sympy.sstr(sympy.Poly(expr, sympy.symbols("x y z w")).as_expr())


def _seed_ctors(nvar):
    names = "xyzw"
    ctor_pool = []
    for v in names[:nvar]:
        ctor_pool.append(("k", v, random.choice([-3, -2, -1, 1, 2, 3]))
                         if random.random() < 0.5 else (None, v, None))
    return ctor_pool


def _product_expr(nvar):
    names = "xyzw"
    terms = []
    for _ in range(random.randint(1, 3)):
        mono = " ".join(f"{names[v]}" for v in sorted(random.sample(range(nvar), random.randint(1, nvar))))
        pow_ = random.randint(1, 3)
        if pow_ == 1:
            terms.append(f"{mono} " if mono else " ".join(names[:nvar]))
        else:
            terms.append(f"({mono})**{pow_}" if mono else " ".join(names[:nvar]))
    body = " * ".join(t for t in terms if t)
    if not body:
        body = random.choice(names[:nvar])
    return body


def _linear_poly(nvar):
    names = "xyzw"
    parts = []
    for i in range(nvar):
        c = random.choice([-2, -1, 1, 2])
        if c == 1:
            parts.append(f"{names[i]}")
        elif c == -1:
            parts.append(f"-{names[i]}")
        else:
            parts.append(f"{c}*{names[i]}")
    const = random.choice([-3, -2, -1, 0, 1, 2, 3])
    if const:
        parts.append(str(const))
    return " + ".join(parts)


def _atomic(nvar):
    r = random.random()
    if r < 0.6:
        return _linear_poly(nvar), 1
    base = _linear_poly(nvar)
    return f"({base})**2", 2


def _product_expr(nvar, max_degree):
    target = max(1, max_degree // 2 + random.randint(0, max_degree // 2))
    parts = []
    total_deg = 0
    for _ in range(6):
        atom, deg = _atomic(nvar)
        if total_deg + deg > target:
            if parts:
                break
            total_deg += deg
            parts.append(atom)
            break
        parts.append(atom)
        total_deg += deg
        if total_deg >= target:
            break
    if not parts:
        parts.append(_linear_poly(nvar))
    return " * ".join(parts)


@dataclass
class PolynomialExpansionConfig(Config):
    nvar_min: int = 1
    nvar_max: int = 1
    max_degree: int = 1

    def apply_difficulty(self, level):
        self.nvar_min = 1
        self.nvar_max = min(4, 1 + level)
        self.max_degree = 2 + level


class PolynomialExpansion(Task):
    summary = ("Expand nested multivariate polynomials in 1-4 variables built from products of "
               "linear sums, powers of sub-factors, and constants, collecting like monomials "
               "into lex order; the answer is the fully expanded polynomial with integer "
               "coefficients.")
    design_choice = ("Vary the number of variables per instance from 1 to 4, forcing solvers to "
                     "handle multivariate monomial ordering and coefficient aggregation.")
    config_cls = PolynomialExpansionConfig

    def generate_entry(self):
        nvar = random.randint(self.config.nvar_min, self.config.nvar_max)
        tries = 0
        while tries < 30:
            tries += 1
            expr_str = _product_expr(nvar, self.config.max_degree)
            expr_str = re.sub(r"\s+", " ", expr_str)
            try:
                expanded = _expand(expr_str)
            except Exception:
                continue
            coeffs = expanded.as_coefficients_dict().values()
            if expanded != 0 and all(int(c) == c and abs(int(c)) <= 10**8 for c in coeffs):
                break
        else:
            raise RuntimeError("could not build valid instance")

        answer = _answer_str(expanded)
        roundtrip = _expand(answer)
        assert sympy.expand(expanded - roundtrip) == 0
        return Entry(metadata={"expression": expr_str, "nvar": nvar},
                     answer=answer)

    def render_prompt(self, metadata):
        return (
            f"Expand the following polynomial expression fully, collecting like terms and "
            f"writing the answer in lexicographic monomial order (x before y before z before w) "
            f"with each coefficient an integer. The answer is just the expanded polynomial, "
            f"e.g. for (x+1)**2 the answer is x**2 + 2*x + 1.\n\n"
            f"Expression: {metadata['expression']}\n\n"
            f"Expanded polynomial:"
        )

    def score_answer(self, answer, entry):
        gold = _normalize(entry.answer)
        if gold is None:
            return 0.0
        user = _normalize(answer)
        if user is None:
            return 0.0
        return 1.0 if user == gold else 0.0


def _normalize(s):
    try:
        e = parse_expr(str(s), transformations=_transformations)
        p = sympy.Poly(sympy.expand(e), sympy.symbols("x y z w"))
    except Exception:
        return None
    return sympy.sstr(p.as_expr())
