from reasoning_core.template import Problem, Task, DevTask, edict, Config, stochastic_rounding as sround
from reasoning_core.utils import score_scalar
from gramforge import init_grammar
from dataclasses import dataclass
import random
import gramforge
import re
import math
from decimal import Decimal, getcontext, ROUND_HALF_UP
import ast, operator
from fractions import Fraction
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

getcontext().prec = 50

def _as_int(x):
    x = Fraction(x)
    if x.denominator != 1:
        raise ValueError("integer operation received a non-integer")
    return x.numerator

def _num_divisors(n):
    n = abs(_as_int(n))
    if n == 0:
        raise ValueError("divisor count undefined for 0")
    return int(sympy.divisor_count(n))

SAFE_FUNCS = {
    "max": max,
    "min": min,
    "abs": abs,
    "round": lambda x: Fraction(round(float(x))),
    "gcd": lambda a, b: math.gcd(_as_int(a), _as_int(b)),
    "lcm": lambda a, b: math.lcm(_as_int(a), _as_int(b)),
    "bit_count": lambda x: abs(_as_int(x)).bit_count(),
    "is_prime": lambda x: int(sympy.isprime(abs(_as_int(x)))),
    "prime_count": lambda x: int(sympy.primepi(abs(_as_int(x)))),
    "num_divisors": _num_divisors,
}

def _grammar(symbolic=False, division=True):
    g = init_grammar(['py'], name="arith", preprocess_template=lambda s:s)
    g('start(expr)',      '{0}')
    g('expr(expr)',       '({0})',              weight=1)
    g('expr(expr,expr)',  '{0} + {1}',          weight=2)
    g('expr(expr,expr)',  '{0} - {1}',          weight=1)
    g('expr(expr,expr)',  '{0} % {1}',          weight=1)
    g('expr(expr,expr)',  '{0} * {1}')
    g('expr(expr,expr)',  'max({0}, {1})',      weight=0.3)
    g('expr(expr,expr)',  'min({0}, {1})',      weight=0.3)
    g('expr(expr)',       'abs({0})',           weight=0.3)
    g('expr(expr)',       'round({0})',         weight=0.2)
    if not symbolic:
        g('expr(int,int)',   'gcd({0}, {1})',   weight=0.25)
        g('expr(pos,pos)',   'lcm({0}, {1})',   weight=0.2)
        g('expr(nat)',       'bit_count({0})',  weight=0.2)
        g('expr(nat)',       'is_prime({0})',   weight=0.15)
        g('expr(nat)',       'prime_count({0})', weight=0.15)
        g('expr(pos)',       'num_divisors({0})', weight=0.15)
    
    if division and not symbolic:
        g('expr(expr,expr)', '{0} / {1}')
    if division:
        g('expr(expr,expr)', '{0} // {1}')
        
    g('expr(expr)',       '({0})**2',           weight=0.5 if symbolic else 0.25)
    g('expr(atom)',       '{0}',                weight=8 if symbolic else 10)
    
    g('atom', 'NUM')
    g('int', 'INT')
    g('nat', 'NAT')
    g('pos', 'POS')
    if symbolic: g('atom', 'VAR')
    return g

g=_grammar()

@dataclass
class ArithmeticsConfig(Config):
    min_depth: int = 3
    max_depth: int = 5
    gramforge_algorithm = "sequential"
    float_prob: float = 0.25
    in_decimals: int = 1
    out_decimals: int = 3
    out_digits: int = 6
    n_trials: int = 50_000
    trailing_zero_prob: float = 0.2
    trivial_prob = 0.01
    bool_prob = 0.1
    spaced_digits_prob: float = 0.25
    reversed_spaced_digits_prob: float = 0.25

    def apply_difficulty(self, level):
        self.min_depth = sround(self.min_depth + level)
        self.max_depth = sround(self.max_depth + level)
        self.out_digits = sround(self.out_digits + level)
        self.out_decimals = sround(self.out_decimals + level)

def _add_trailing_zeros(s, prob=0.2):
    """Add trailing zeros to decimals with exponentially decreasing probability."""
    if '.' not in s: return s
    while random.random() < prob: s += '0'
    return s


def fill_num(expr, cfg=ArithmeticsConfig()):
    pat = re.compile(r'\b(NUM|INT|NAT|POS)\b')
    tokens = pat.findall(expr)

    def to_decimal(v):
        f = Fraction(v)
        d = f.denominator
        while d % 2 == 0: d //= 2
        while d % 5 == 0: d //= 5
        if d != 1: return None                                # non-terminating decimal
        dec = (Decimal(f.numerator) / Decimal(f.denominator)).normalize()
        _, _, exp = dec.as_tuple()
        if max(0, -exp) > cfg.out_decimals: return None
        s = f'{dec:.{cfg.out_decimals}f}'
        return dec if len(s.replace('-','').replace('.','')) <= cfg.out_digits else None

    has_division = '/' in expr
    for _ in range(cfg.n_trials):
        vals_str = []
        for tok in tokens:
            r = random.random()
            if tok == "INT":                           num = random.randint(-30, 30)
            elif tok == "NAT":                         num = random.randint(0, 80)
            elif tok == "POS":                         num = random.randint(1, 80)
            elif r < cfg.bool_prob:                    num = random.randint(0, 1)
            elif r < cfg.bool_prob + cfg.float_prob:   num = round(random.uniform(-12, 12), random.randint(1, cfg.in_decimals))
            else:                                      num = random.randint(-15, 15)
            if tok == "NUM" and has_division and num == 0: num = random.choice([-1, 1])
            vals_str.append(str(num))

        it = iter(f"Fraction('{x}')" for x in vals_str)
        try:
            v = eval(pat.sub(lambda _: next(it), expr),
                     {"Fraction": Fraction, **SAFE_FUNCS})
        except Exception: continue

        dec = to_decimal(v)
        if dec is not None:
            it_str = iter(_add_trailing_zeros(s, cfg.trailing_zero_prob) for s in vals_str)
            return pat.sub(lambda _: next(it_str), expr), dec
    raise RuntimeError('No assignment found; increase n_trials or widen pool.')

def _space_number(m, reverse=False):
    s = m.group()
    chars = list(reversed(s)) if reverse else list(s)
    return " ".join(chars)


def _display_expr(expr, cfg):
    r = random.random()
    if r < cfg.spaced_digits_prob:
        return re.sub(r"\d+(?:\.\d+)?", _space_number, expr), "spaced"
    if r < cfg.spaced_digits_prob + cfg.reversed_spaced_digits_prob:
        return re.sub(r"\d+(?:\.\d+)?", lambda m: _space_number(m, True), expr), "reversed_spaced"
    return expr, "normal"


def _format_number(s, mode):
    if mode == "spaced":
        return re.sub(r"\d+(?:\.\d+)?", _space_number, s)
    if mode == "reversed_spaced":
        return re.sub(r"\d+(?:\.\d+)?", lambda m: _space_number(m, True), s)
    return s


class Arithmetics(Task):
    config_cls = ArithmeticsConfig
    summary = "Compositional arithmetics with float/int/bool, varied operators, number theory."

    def generate(self):
        while True:
            x = gramforge.generate(g, depth=self.config.max_depth, min_depth=self.config.min_depth, mode=self.config.gramforge_algorithm)
            expr = x@'py'
            if expr.count('NUM') > 1 or random.random() < self.config.trivial_prob: break
        final_expr, value = fill_num(expr, cfg=self.config)
        quantizer = Decimal('1e-' + str(self.config.out_decimals))
        ans_str = f"{value.quantize(quantizer):f}".rstrip('0').rstrip('.')
        shown_expr, digit_mode = _display_expr(final_expr, self.config)
        meta = edict(expr=final_expr, display_expr=shown_expr, digit_mode=digit_mode, height=x.height, cot=self.get_cot(final_expr))
        return Problem(metadata=meta, answer=_format_number(ans_str, digit_mode))
    
    def prompt(self, metadata):
        note = {
            "spaced": " Digits are spaced; answer likewise.",
            "reversed_spaced": " Digits are reversed and spaced; answer likewise.",
        }.get(metadata.get("digit_mode"), "")
        return f"Evaluate {metadata.get('display_expr', metadata.expr)}.{note}\nThe answer is a number."

    def score_answer(self, answer, entry):
        if entry.metadata.get("digit_mode", "normal") == "normal":
            return score_scalar(answer, entry)
        return float(str(answer).strip() == str(entry.answer).strip())

    def get_cot(self, expr):
        ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, 
               ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Pow: operator.pow, ast.Mod: operator.mod}
        syms = {ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/', ast.FloorDiv: '//', ast.Pow: '**', ast.Mod: '%'}
        steps = []
        
        def fmt(n):
            d = n.denominator
            while d % 2 == 0: d //= 2
            while d % 5 == 0: d //= 5
            return f"{float(n):g}" if d == 1 else str(n)

        def visit(node):
            if isinstance(node, ast.Constant): return Fraction(str(node.value))
            if isinstance(node, ast.UnaryOp): return -visit(node.operand)
            if isinstance(node, ast.Call):
                fname = node.func.id
                args = [visit(a) for a in node.args]
                res = Fraction(SAFE_FUNCS[fname](*args))
                steps.append(f"{fname}({', '.join(fmt(a) for a in args)}) = {fmt(res)}")
                return res
            l, r = visit(node.left), visit(node.right)
            res = ops[type(node.op)](l, r)
            steps.append(f"{fmt(l)} {syms[type(node.op)]} {fmt(r)} = {fmt(res)}")
            return res

        visit(ast.parse(expr, mode='eval').body)
        return "\n".join(steps)



import random, sympy as sp
from dataclasses import dataclass
from reasoning_core.template import Task, Problem, Config, edict
from reasoning_core.utils import score_scalar


UNITS = "stamps marbles coins books apples cards tokens beads tiles cookies shells stickers pebbles buttons".split()
NAMES = ("Mara Jon Aisha Wei Sofia Diego Priya Tom Lena Omar Yuki Hana Carlos Nina "
         "Zara Ravi Mei Iris Noah Amara Leo Sana Kof Tara").split()

ORD = {2: "half", 3: "a third", 4: "a quarter", 5: "a fifth"}
MUL = {2: "doubled", 3: "tripled", 4: "quadrupled"}


@dataclass
class WordProblemMathConfig(Config):
    n_rel: int = 2
    max_n: int = 12
    inverse_p: float = .30
    relational_p: float = .50

    def apply_difficulty(self, level):
        self.n_rel = sround(self.n_rel + level)
        self.max_n = sround(self.max_n + 12 * level)
        self.inverse_p = min(.70, self.inverse_p + .08 * level)


def ri(a, b):
    return random.randint(int(a), int(b))


def unique(expr, observed, x, expect):
    sols = sp.solve(sp.Eq(expr, observed), x, dict=True)
    if len(sols) != 1 or x not in sols[0]:
        return False
    xv = sp.nsimplify(sols[0][x])
    return bool(xv.is_integer) and int(xv) == expect


def clean_answer(a):
    return isinstance(a, int) and 0 < a < 6000


def process_step_text(step, unit):
    op, k = step
    if op == "mul":
        return MUL[k] if random.random() < .6 else f"multiplied by {k}"
    if op == "div":
        return f"cut to {ORD[k]}"
    if op == "add":
        return f"{k} more {unit} added"
    return f"{k} {unit} removed"


def relation_text(rel, unit):
    op, a, b, k, c = rel
    if op == "times":
        return f"{a} has {k} times as many {unit} as {b}"
    if op == "more":
        return f"{a} has {k} more {unit} than {b}"
    if op == "fewer":
        return f"{a} has {k} fewer {unit} than {b}"
    if op == "frac":
        return f"{a} has {ORD[k]} as many {unit} as {b}"
    return f"{a} has as many {unit} as {b} and {c} combined"


def gen_process(config):
    unit = random.choice(UNITS)
    x = sp.Symbol("x", positive=True)
    base = ri(2, config.max_n)
    expr, cur, steps = x, sp.Integer(base), []

    for _ in range(ri(2, 2 + config.n_rel)):
        op = random.choice(["add", "sub", "mul", "div"])

        if op == "mul":
            k = ri(2, 4)
            expr, cur = k * expr, k * cur

        elif op == "div":
            ks = [k for k in (2, 3, 4, 5) if int(cur) % k == 0 and int(cur) // k >= 2]
            if not ks:
                continue
            k = random.choice(ks)
            expr, cur = expr / k, cur // k

        elif op == "add":
            k = ri(2, config.max_n)
            expr, cur = expr + k, cur + k

        else:
            if int(cur) <= 3:
                continue
            k = ri(2, int(cur) - 1)
            expr, cur = expr - k, cur - k

        steps.append((op, k))

    if len(steps) < 2 or int(cur) < 2:
        return None

    observed = int(cur)
    inverse = random.random() < config.inverse_p
    answer = base if inverse else observed

    if inverse and not unique(expr, observed, x, base):
        return None

    metadata = edict(
        family="process",
        unit=unit,
        base=base,
        observed=observed,
        inverse=inverse,
        steps=steps,
        expr=str(expr),
        equation=str(sp.Eq(expr, observed)),
        cot=f"Solve {sp.Eq(expr, observed)} for x; x = {base}.",
    )
    return Problem(metadata=metadata, answer=str(answer))


def gen_relational(config):
    unit = random.choice(UNITS)
    m = ri(3, min(6, 3 + config.n_rel))
    names = random.sample(NAMES, m)

    x = sp.Symbol("x", positive=True)
    val, rels = {names[0]: x}, []

    for i in range(1, m):
        a = names[i]
        parents = names[:i]
        ops = ["times", "more", "fewer", "frac"] + (["combine"] if len(parents) >= 2 else [])
        op = random.choice(ops)

        if op == "times":
            b, k = random.choice(parents), ri(2, 4)
            val[a] = k * val[b]
            rels.append((op, a, b, k, None))

        elif op == "more":
            b, k = random.choice(parents), ri(2, config.max_n)
            val[a] = val[b] + k
            rels.append((op, a, b, k, None))

        elif op == "fewer":
            b, k = random.choice(parents), ri(2, config.max_n)
            val[a] = val[b] - k
            rels.append((op, a, b, k, None))

        elif op == "frac":
            b, k = random.choice(parents), random.choice([2, 3, 4])
            val[a] = val[b] / k
            rels.append((op, a, b, k, None))

        else:
            b, c = random.sample(parents, 2)
            val[a] = val[b] + val[c]
            rels.append((op, a, b, None, c))

    base = nums = None
    candidates = list(range(2, int(config.max_n) + 1))
    random.shuffle(candidates)

    for cand in candidates[:24]:
        cur = {k: sp.nsimplify(v.subs(x, cand)) for k, v in val.items()}
        if all(t.is_integer and t > 0 for t in cur.values()):
            base = cand
            nums = {k: int(v) for k, v in cur.items()}
            break

    if base is None:
        return None

    revealable = [z for z in names if nums[z] >= 2]
    if not revealable:
        return None

    given = random.choice(revealable)
    asked = random.choice([z for z in names if z != given])

    if not unique(val[given], nums[given], x, base):
        return None

    random.shuffle(rels)

    metadata = edict(
        family="relational",
        unit=unit,
        names=names,
        relations=rels,
        given=given,
        asked=asked,
        given_value=nums[given],
        values=nums,
        base=base,
        equation=str(sp.Eq(val[given], nums[given])),
        cot=f"Solve {sp.Eq(val[given], nums[given])}; then compute {asked} = {nums[asked]}.",
    )
    return Problem(metadata=metadata, answer=str(nums[asked]))


class MathWordProblem(Task):
    def __init__(self, config=WordProblemMathConfig()):
        super().__init__(config=config)

    def generate(self):
        for _ in range(100):
            gen = gen_relational if random.random() < self.config.relational_p else gen_process
            problem = gen(self.config)
            if problem and clean_answer(int(problem.answer)):
                return problem
        return None

    def prompt(self, m):
        if m.family == "process":
            chain = "; then ".join(process_step_text(s, m.unit) for s in m.steps)
            if m.inverse:
                return (
                    f"A jar holds some {m.unit}. {chain}. "
                    f"The jar now holds {m.observed} {m.unit}. "
                    f"How many {m.unit} did it start with? Answer with a number."
                )
            return (
                f"A jar holds {m.base} {m.unit}. {chain}. "
                f"How many {m.unit} are in the jar now? Answer with a number."
            )

        lines = ". ".join(relation_text(r, m.unit) for r in m.relations)
        return (
            f"{lines}. {m.given} has {m.given_value} {m.unit}. "
            f"How many {m.unit} does {m.asked} have? Answer with s a number."
        )

    def score_answer(self, answer, entry):
        return score_scalar(answer, entry)

    def balancing_key(self, problem):
        m = problem.metadata
        if m.family == "process":
            ops = ",".join(op for op, _ in m.steps)
            return f"process:{'inverse' if m.inverse else 'forward'}:{ops}"
        ops = ",".join(r[0] for r in m.relations)
        return f"relational:{ops}"

    def deduplication_key(self, problem):
        m = problem.metadata
        if m.family == "process":
            return str((m.family, m.unit, m.base, m.observed, tuple(map(tuple, m.steps)), m.inverse))
        return str((m.family, m.unit, tuple(map(tuple, m.relations)), m.given, m.given_value, m.asked))
