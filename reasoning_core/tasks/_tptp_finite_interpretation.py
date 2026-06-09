"""Finite interpretations for the CNF fragment emitted by the TPTP tasks."""

import copy
import os
import random
import re
import tempfile
from dataclasses import dataclass, field
from itertools import product

import z3

from reasoning_core.utils.udocker_process import get_prover_session


@dataclass
class FiniteInterpretation:
    domain: list
    constants: dict = field(default_factory=dict)
    functions: dict = field(default_factory=dict)
    predicates: dict = field(default_factory=dict)


def universally_quantify(formula):
    variables = sorted(set(re.findall(r"\b([A-Z][A-Za-z0-9_]*)\b", formula)))
    return f"![{','.join(variables)}] : ({formula})" if variables else formula


_TOKEN_RE = re.compile(
    r"\s*(?:(?P<neq>!=)|(?P<name>'(?:[^'\\]|\\.)*'|[A-Za-z$][A-Za-z0-9_$]*)|"
    r"(?P<symbol>[=~|&(),]))"
)
_SYMBOLS = {"=", "!=", "~", "|", "&", "(", ")", ","}


def _unquote(symbol):
    if len(symbol) >= 2 and symbol[0] == symbol[-1] == "'":
        return symbol[1:-1].replace("\\'", "'").replace("\\\\", "\\")
    return symbol


class _Parser:
    def __init__(self, text):
        text = text.strip()
        self.tokens = []
        pos = 0
        while pos < len(text):
            match = _TOKEN_RE.match(text, pos)
            if not match:
                raise ValueError(f"Unsupported TPTP syntax near {text[pos:pos + 30]!r}")
            self.tokens.append(match.group(match.lastgroup))
            pos = match.end()
        self.pos = 0

    def parse(self):
        result = self._junction("|", self._parse_and)
        if self.pos != len(self.tokens):
            raise ValueError(f"Unexpected token {self.tokens[self.pos]!r}")
        return result

    def _peek(self, token=None):
        current = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        return current == token if token is not None else current

    def _take(self, token=None):
        current = self._peek()
        if current is None or (token is not None and current != token):
            raise ValueError(f"Expected {token!r}, got {current!r}")
        self.pos += 1
        return current

    def _junction(self, token, parse_operand):
        parts = [parse_operand()]
        while self._peek(token):
            self._take(token)
            parts.append(parse_operand())
        return parts[0] if len(parts) == 1 else ({"|": "or", "&": "and"}[token], tuple(parts))

    def _parse_and(self):
        return self._junction("&", self._parse_unary)

    def _parse_unary(self):
        if self._peek("~"):
            self._take("~")
            return ("not", self._parse_unary())
        if self._peek("("):
            self._take("(")
            result = self._junction("|", self._parse_and)
            self._take(")")
            return result
        return self._parse_atom()

    def _parse_atom(self):
        left = self._parse_term()
        if self._peek() in {"=", "!="}:
            return (self._take(), left, self._parse_term())
        if left[0] != "call":
            raise ValueError("A bare term is not a formula")
        return ("pred", left[1], left[2])

    def _parse_term(self):
        token = self._take()
        if token in _SYMBOLS:
            raise ValueError(f"Expected a term, got {token!r}")
        name = _unquote(token)
        if not self._peek("("):
            return ("var", name) if name[0].isupper() else ("const", name)
        self._take("(")
        args = []
        while not self._peek(")"):
            args.append(self._parse_term())
            if not self._peek(","):
                break
            self._take(",")
        self._take(")")
        return ("call", name, tuple(args))


def _parse_formula(formula):
    return _Parser(formula).parse()


def validate_formula(formula):
    """Raise ValueError unless formula belongs to the supported CNF fragment."""
    _parse_formula(formula)


def _children(node):
    kind = node[0]
    if kind in {"call", "pred"}:
        return node[2]
    if kind == "not":
        return (node[1],)
    if kind in {"=", "!="}:
        return node[1:]
    if kind in {"and", "or"}:
        return node[1]
    return ()


def _walk(node):
    yield node
    for child in _children(node):
        yield from _walk(child)


def _variables(ast):
    return sorted({node[1] for node in _walk(ast) if node[0] == "var"})


def _signature(formulas):
    signature = {"constants": set(), "functions": {}, "predicates": {}}
    for ast in formulas:
        for node in _walk(ast):
            kind = node[0]
            if kind == "const":
                signature["constants"].add(node[1])
            elif kind in {"call", "pred"}:
                group = "functions" if kind == "call" else "predicates"
                arity = len(node[2])
                previous = signature[group].setdefault(node[1], arity)
                if previous != arity:
                    raise ValueError(f"Inconsistent arity for {node[1]!r}")
    return signature


def _eval_term(node, model, assignment):
    kind = node[0]
    if kind == "var":
        return assignment[node[1]]
    if kind == "const":
        return model.constants[node[1]]
    if kind == "call":
        args = tuple(_eval_term(arg, model, assignment) for arg in node[2])
        return model.functions[node[1]][args]
    raise ValueError(f"Expected term, got {kind!r}")


def _eval(node, model, assignment):
    kind = node[0]
    if kind == "pred":
        args = tuple(_eval_term(arg, model, assignment) for arg in node[2])
        return model.predicates[node[1]][args]
    if kind == "not":
        return not _eval(node[1], model, assignment)
    if kind in {"=", "!="}:
        equal = _eval_term(node[1], model, assignment) == _eval_term(node[2], model, assignment)
        return equal if kind == "=" else not equal
    if kind in {"and", "or"}:
        values = (_eval(arg, model, assignment) for arg in node[1])
        return all(values) if kind == "and" else any(values)
    raise ValueError(f"Expected formula, got {kind!r}")


def eval_cnf_clause(formula, model):
    ast = _parse_formula(formula)
    variables = _variables(ast)
    return all(
        _eval(ast, model, dict(zip(variables, values)))
        for values in product(model.domain, repeat=len(variables))
    )


def requirement_holds(requirement, model):
    return eval_cnf_clause(requirement["formula"], model) == requirement["should_be"]


def requirements_hold(requirements, model):
    try:
        return all(requirement_holds(requirement, model) for requirement in requirements)
    except (KeyError, ValueError):
        return False


def write_signed_fmb_problem(requirements):
    handle = tempfile.NamedTemporaryFile(mode="w+", suffix=".p", delete=False)
    try:
        for i, requirement in enumerate(requirements):
            formula = requirement["formula"]
            if requirement["should_be"]:
                handle.write(f"cnf(r_{i}, axiom, {formula}).\n")
            else:
                handle.write(f"fof(r_{i}, axiom, ~({universally_quantify(formula)})).\n")
        handle.flush()
        return handle.name
    finally:
        handle.close()


def _model_blocks(text, prefix):
    return re.findall(
        rf"tff\({re.escape(prefix)}([^,]*),axiom,(.*?)\n\)\.",
        text,
        re.DOTALL,
    )


def _split_conjunction(text):
    parts, start, depth = [], 0, 0
    for i, char in enumerate(text):
        depth += (char == "(") - (char == ")")
        if char == "&" and depth == 0:
            parts.append(text[start:i])
            start = i + 1
    parts.append(text[start:])
    return [part.strip() for part in parts if part.strip()]


def _ground_term(text):
    node = _parse_formula(f"{text.strip()} = {text.strip()}")[1]
    if node[0] == "const":
        return node[1], ()
    if node[0] == "call" and all(arg[0] == "const" for arg in node[2]):
        return node[1], tuple(arg[1] for arg in node[2])
    raise ValueError("Model table entries must be flat ground terms")


def parse_vampire_model(stdout):
    """Parse Vampire's TPTP FiniteModel block into a partial interpretation."""
    match = re.search(
        r"% SZS output start FiniteModel.*?\n(.*?)% SZS output end FiniteModel",
        stdout,
        re.DOTALL,
    )
    if not match:
        return None
    text = match.group(1)
    domain = re.search(r"tff\('finite_domain_[^']+',axiom,(.*?)\n\)\.", text, re.DOTALL)
    if not domain:
        return None
    symbols = re.findall(
        r"\b[A-Z][A-Za-z0-9_$]*\s*=\s*('[^']+'|[a-z$][A-Za-z0-9_$]*)",
        domain.group(1),
    )
    symbols = list(dict.fromkeys(map(_unquote, symbols)))
    if not symbols:
        return None

    values = {symbol: i for i, symbol in enumerate(symbols)}
    model = FiniteInterpretation(list(range(len(symbols))), constants=dict(values))

    for _, body in _model_blocks(text, "function_"):
        body = "\n".join(line for line in body.splitlines() if not line.lstrip().startswith("%"))
        for entry in _split_conjunction(body):
            if "=" not in entry:
                continue
            (name, args), (value, value_args) = map(_ground_term, entry.split("=", 1))
            if value_args or value not in values:
                raise ValueError("Unsupported function value in Vampire model")
            if args:
                model.functions.setdefault(name, {})[tuple(values[arg] for arg in args)] = values[value]
            else:
                model.constants[name] = values[value]

    for _, body in _model_blocks(text, "predicate_"):
        body = "\n".join(line for line in body.splitlines() if not line.lstrip().startswith("%"))
        for entry in _split_conjunction(body):
            positive = not entry.startswith("~")
            name, args = _ground_term(entry.lstrip("~").strip())
            model.predicates.setdefault(name, {})[tuple(values[arg] for arg in args)] = positive
    return model


def _z3_term(node, assignment, constants, functions):
    kind = node[0]
    if kind == "var":
        return z3.IntVal(assignment[node[1]])
    if kind == "const":
        return constants[node[1]]
    if kind == "call":
        return functions[node[1]](*(
            _z3_term(arg, assignment, constants, functions) for arg in node[2]
        ))
    raise ValueError(f"Expected term, got {kind!r}")


def _z3_formula(node, assignment, constants, functions, predicates):
    kind = node[0]
    if kind == "pred":
        return predicates[node[1]](*(
            _z3_term(arg, assignment, constants, functions) for arg in node[2]
        ))
    if kind == "not":
        return z3.Not(_z3_formula(node[1], assignment, constants, functions, predicates))
    if kind in {"=", "!="}:
        lhs = _z3_term(node[1], assignment, constants, functions)
        rhs = _z3_term(node[2], assignment, constants, functions)
        return lhs == rhs if kind == "=" else lhs != rhs
    args = [_z3_formula(arg, assignment, constants, functions, predicates) for arg in node[1]]
    if kind == "and":
        return z3.And(args)
    if kind == "or":
        return z3.Or(args)
    raise ValueError(f"Expected formula, got {kind!r}")


def complete_model(requirements, partial):
    """Totalize a partial Vampire model while preserving its explicit entries."""
    if partial is None or not partial.domain:
        return None
    parsed = [(_parse_formula(req["formula"]), req["should_be"]) for req in requirements]
    signature = _signature(ast for ast, _ in parsed)
    size = len(partial.domain)
    domain = range(size)
    solver = z3.Solver()

    constants = {
        name: z3.Int(f"fic_c_{i}")
        for i, name in enumerate(sorted(signature["constants"]))
    }
    functions = {
        name: z3.Function(f"fic_f_{i}", *([z3.IntSort()] * arity), z3.IntSort())
        for i, (name, arity) in enumerate(sorted(signature["functions"].items()))
    }
    predicates = {
        name: z3.Function(f"fic_p_{i}", *([z3.IntSort()] * arity), z3.BoolSort())
        for i, (name, arity) in enumerate(sorted(signature["predicates"].items()))
    }

    for value in constants.values():
        solver.add(value >= 0, value < size)
    for name, arity in signature["functions"].items():
        for args in product(domain, repeat=arity):
            value = functions[name](*map(z3.IntVal, args))
            solver.add(value >= 0, value < size)

    for name, value in partial.constants.items():
        if name in constants:
            solver.add(constants[name] == value)
    for name, table in partial.functions.items():
        if name in functions:
            for args, value in table.items():
                solver.add(functions[name](*map(z3.IntVal, args)) == value)
    for name, table in partial.predicates.items():
        if name in predicates:
            for args, value in table.items():
                solver.add(predicates[name](*map(z3.IntVal, args)) == value)

    for ast, should_be in parsed:
        variables = _variables(ast)
        instances = [
            _z3_formula(ast, dict(zip(variables, values)), constants, functions, predicates)
            for values in product(domain, repeat=len(variables))
        ]
        universal = z3.And(instances)
        solver.add(universal if should_be else z3.Not(universal))

    if solver.check() != z3.sat:
        return None
    solution = solver.model()
    evaluate = lambda expr: solution.eval(expr, model_completion=True)
    model = FiniteInterpretation(list(domain))
    model.constants = {name: evaluate(value).as_long() for name, value in constants.items()}
    model.functions = {
        name: {
            args: evaluate(function(*map(z3.IntVal, args))).as_long()
            for args in product(domain, repeat=signature["functions"][name])
        }
        for name, function in functions.items()
    }
    model.predicates = {
        name: {
            args: z3.is_true(evaluate(predicate(*map(z3.IntVal, args))))
            for args in product(domain, repeat=signature["predicates"][name])
        }
        for name, predicate in predicates.items()
    }
    return model


def run_vampire_fmb_signed(requirements, time_limit_seconds="5"):
    path = write_signed_fmb_problem(requirements)
    try:
        result = get_prover_session().run_prover(
            "vampire",
            ["-t", str(time_limit_seconds), "-sa", "fmb", "--show_fmb_sort_info", "on"],
            path,
        )
        if not any(status in result.stdout for status in (
            "Finite Model Found!",
            "% SZS status CounterSatisfiable",
            "% SZS status Satisfiable",
        )):
            return None
        try:
            return complete_model(requirements, parse_vampire_model(result.stdout))
        except (ValueError, z3.Z3Exception):
            return None
    finally:
        if os.path.exists(path):
            os.remove(path)


def serialize_model(model):
    lines = ["Domain:", "{" + ", ".join(map(str, model.domain)) + "}", "", "Constants:"]
    lines.extend(
        (f"{name} = {value}" for name, value in sorted(model.constants.items()))
        if model.constants else ["(none)"]
    )
    lines.extend(["", "Functions:"])
    if not model.functions:
        lines.append("(none)")
    for name, table in sorted(model.functions.items()):
        lines.append(f"{name}:")
        lines.extend(f"  {args} -> {value}" for args, value in sorted(table.items()))
    lines.extend(["", "Predicates:"])
    if not model.predicates:
        lines.append("(none)")
    for name, table in sorted(model.predicates.items()):
        lines.append(f"{name}:")
        lines.extend(f"  {args} -> {str(value).lower()}" for args, value in sorted(table.items()))
    return "\n".join(lines)


def mutate_model(model):
    candidate = copy.deepcopy(model)
    choices = []
    if len(candidate.domain) > 1:
        choices.extend(("constant", name) for name in candidate.constants)
        choices.extend(("function", name) for name, table in candidate.functions.items() if table)
    choices.extend(("predicate", name) for name, table in candidate.predicates.items() if table)
    if not choices:
        return candidate

    kind, name = random.choice(choices)
    if kind == "constant":
        old = candidate.constants[name]
        candidate.constants[name] = random.choice([value for value in candidate.domain if value != old])
    elif kind == "function":
        args = random.choice(list(candidate.functions[name]))
        old = candidate.functions[name][args]
        candidate.functions[name][args] = random.choice(
            [value for value in candidate.domain if value != old]
        )
    else:
        args = random.choice(list(candidate.predicates[name]))
        candidate.predicates[name][args] = not candidate.predicates[name][args]
    return candidate


def make_near_miss_model(requirements, model, max_tries=100):
    for target_failures in (1, 2):
        for _ in range(max_tries):
            candidate = mutate_model(model)
            failures = sum(not requirement_holds(req, candidate) for req in requirements)
            if failures == target_failures:
                return candidate
    return None
