import networkx as nx
import re
import os
import sys
import tempfile
import random
import json
import gzip
import logging
from easydict import EasyDict as edict
from dataclasses import dataclass
from appdirs import AppDirs
from pathlib import Path
from reasoning_core.utils.udocker_process import get_prover_session
from ._tptp_finite_interpretation import (
    model_is_nondegenerate,
    requirement_holds,
    requirements_hold,
    run_vampire_fmb_signed,
    serialize_model,
    universally_quantify,
    validate_formula,
)
from ._tptp_sat_graph import generate_derivation_graph
from reasoning_core.template import Task, Problem, Config
import ast
from reasoning_core.template import TimeoutException
from itertools import combinations
from math import comb


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TPTPTerm:
    name: str
    args: tuple = ()


@dataclass(frozen=True)
class TPTPLiteral:
    sign: bool
    pred: str
    args: tuple = ()


_TPTP_TOKEN = re.compile(
    r"""\s*(?:(?P<quoted>'(?:\\.|''|[^'\\])*'|"(?:\\.|""|[^"\\])*")|"""
    r"(?P<op>!=|[()|~,=])|"
    r"(?P<word>\$?[A-Za-z0-9_]+))"
)


def _tokenize_clause(text):
    tokens = []
    pos = 0
    while pos < len(text):
        match = _TPTP_TOKEN.match(text, pos)
        if not match:
            raise ValueError(f"Unexpected TPTP syntax at position {pos}: {text[pos:pos + 20]!r}")
        tokens.append(match.group("quoted") or match.group("op") or match.group("word"))
        pos = match.end()
    return tokens


def _matching_outer_parens(tokens):
    if len(tokens) < 2 or tokens[0] != "(" or tokens[-1] != ")":
        return False
    depth = 0
    for index, token in enumerate(tokens):
        if token == "(":
            depth += 1
        elif token == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("Unbalanced parentheses")
            if depth == 0 and index != len(tokens) - 1:
                return False
    if depth:
        raise ValueError("Unbalanced parentheses")
    return True


def _strip_outer_parens(tokens):
    while _matching_outer_parens(tokens):
        tokens = tokens[1:-1]
    return tokens


def _split_top_level(tokens, separator):
    parts = []
    start = 0
    depth = 0
    for index, token in enumerate(tokens):
        if token == "(":
            depth += 1
        elif token == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("Unbalanced parentheses")
        elif token == separator and depth == 0:
            parts.append(tokens[start:index])
            start = index + 1
    if depth:
        raise ValueError("Unbalanced parentheses")
    parts.append(tokens[start:])
    if any(not part for part in parts):
        raise ValueError(f"Missing expression around {separator!r}")
    return parts


def _parse_term_tokens(tokens, start=0):
    if start >= len(tokens) or tokens[start] in {"(", ")", "|", "~", ",", "=", "!="}:
        raise ValueError("Expected a term")
    name = tokens[start]
    index = start + 1
    args = []
    if index < len(tokens) and tokens[index] == "(":
        index += 1
        if index < len(tokens) and tokens[index] == ")":
            return TPTPTerm(name, ()), index + 1
        while True:
            arg, index = _parse_term_tokens(tokens, index)
            args.append(arg)
            if index >= len(tokens):
                raise ValueError("Unclosed term argument list")
            if tokens[index] == ")":
                index += 1
                break
            if tokens[index] != ",":
                raise ValueError("Expected ',' or ')' in term")
            index += 1
    return TPTPTerm(name, tuple(args)), index


def _parse_complete_term(tokens):
    term, index = _parse_term_tokens(tokens)
    if index != len(tokens):
        raise ValueError("Unexpected tokens after term")
    return term


def _find_top_level_equality(tokens):
    depth = 0
    found = []
    for index, token in enumerate(tokens):
        if token == "(":
            depth += 1
        elif token == ")":
            depth -= 1
        elif token in {"=", "!="} and depth == 0:
            found.append((index, token))
    if len(found) > 1:
        raise ValueError("A literal may contain only one top-level equality")
    return found[0] if found else None


def _parse_literal_tokens(tokens):
    tokens = _strip_outer_parens(tokens)
    sign = True
    if tokens and tokens[0] == "~":
        sign = False
        tokens = _strip_outer_parens(tokens[1:])
    if not tokens:
        raise ValueError("Empty literal")

    equality = _find_top_level_equality(tokens)
    if equality:
        index, operator = equality
        left = _parse_complete_term(tokens[:index])
        right = _parse_complete_term(tokens[index + 1:])
        return TPTPLiteral(sign=(sign if operator == "=" else not sign), pred="=", args=(left, right))

    atom = _parse_complete_term(tokens)
    if _is_variable(atom):
        raise ValueError("A variable cannot be used as a predicate")
    return TPTPLiteral(sign=sign, pred=atom.name, args=atom.args)


def parse_clause(text):
    """Parse the first-order CNF subset emitted by E prover."""
    tokens = _strip_outer_parens(_tokenize_clause(str(text).strip()))
    if tokens == ["$false"]:
        return []
    return [_parse_literal_tokens(part) for part in _split_top_level(tokens, "|")]


def _is_variable(term):
    return not term.args and bool(re.fullmatch(r"[A-Z][A-Za-z0-9_]*", term.name))


def _walk_term_variables(term):
    if _is_variable(term):
        yield term.name
    for arg in term.args:
        yield from _walk_term_variables(arg)


def _walk_literal_variables(literal):
    for arg in literal.args:
        yield from _walk_term_variables(arg)


def _replace_variables_term(term, replacements):
    if _is_variable(term) and term.name in replacements:
        return TPTPTerm(replacements[term.name])
    return TPTPTerm(
        term.name,
        tuple(_replace_variables_term(arg, replacements) for arg in term.args),
    )


def _replace_variables_literal(literal, replacements):
    return TPTPLiteral(
        literal.sign,
        literal.pred,
        tuple(_replace_variables_term(arg, replacements) for arg in literal.args),
    )


def rename_apart(clause, prefix="Y", forbidden=()):
    forbidden = set(forbidden)
    replacements = {}
    next_index = 1
    for literal in clause:
        for variable in _walk_literal_variables(literal):
            if variable in replacements:
                continue
            candidate = f"{prefix}{next_index}"
            while candidate in forbidden:
                next_index += 1
                candidate = f"{prefix}{next_index}"
            replacements[variable] = candidate
            forbidden.add(candidate)
            next_index += 1
    return [_replace_variables_literal(literal, replacements) for literal in clause]


def _dereference(term, subst):
    seen = set()
    while _is_variable(term) and term.name in subst and term.name not in seen:
        seen.add(term.name)
        term = subst[term.name]
    return term


def _occurs(variable, term, subst):
    term = _dereference(term, subst)
    if _is_variable(term):
        return term.name == variable
    return any(_occurs(variable, arg, subst) for arg in term.args)


def unify(left, right, subst=None):
    """Return an MGU for two terms, with an occurs check, or None."""
    subst = {} if subst is None else dict(subst)
    pending = [(left, right)]
    while pending:
        first, second = pending.pop()
        first = _dereference(first, subst)
        second = _dereference(second, subst)
        if first == second:
            continue
        if _is_variable(first):
            if _occurs(first.name, second, subst):
                return None
            subst[first.name] = second
            continue
        if _is_variable(second):
            if _occurs(second.name, first, subst):
                return None
            subst[second.name] = first
            continue
        if first.name != second.name or len(first.args) != len(second.args):
            return None
        pending.extend(zip(first.args, second.args))
    return subst


def _unify_args(left_args, right_args):
    if len(left_args) != len(right_args):
        return None
    subst = {}
    for left, right in zip(left_args, right_args):
        subst = unify(left, right, subst)
        if subst is None:
            return None
    return subst


def apply_subst_term(term, subst):
    term = _dereference(term, subst)
    if _is_variable(term):
        return term
    return TPTPTerm(
        term.name,
        tuple(apply_subst_term(arg, subst) for arg in term.args),
    )


def apply_subst_literal(literal, subst):
    return TPTPLiteral(
        literal.sign,
        literal.pred,
        tuple(apply_subst_term(arg, subst) for arg in literal.args),
    )


def resolvents(clause_a, clause_b):
    out = []
    for index_a, literal_a in enumerate(clause_a):
        for index_b, literal_b in enumerate(clause_b):
            if literal_a.sign == literal_b.sign or literal_a.pred != literal_b.pred:
                continue
            subst = _unify_args(literal_a.args, literal_b.args)
            if subst is None:
                continue
            remaining = [
                apply_subst_literal(literal, subst)
                for index, literal in enumerate(clause_a)
                if index != index_a
            ] + [
                apply_subst_literal(literal, subst)
                for index, literal in enumerate(clause_b)
                if index != index_b
            ]
            out.append(list(dict.fromkeys(remaining)))
    return out


def _render_term(term, variable_mask=None):
    name = variable_mask if variable_mask is not None and _is_variable(term) else term.name
    if not term.args:
        return name
    return f"{name}({','.join(_render_term(arg, variable_mask) for arg in term.args)})"


def _render_literal(literal, variable_mask=None):
    if literal.pred == "=":
        operator = "=" if literal.sign else "!="
        return (
            f"{_render_term(literal.args[0], variable_mask)} {operator} "
            f"{_render_term(literal.args[1], variable_mask)}"
        )
    atom = literal.pred
    if literal.args:
        atom += f"({','.join(_render_term(arg, variable_mask) for arg in literal.args)})"
    return atom if literal.sign else f"~{atom}"


def render_clause(clause):
    if not clause:
        return "$false"
    return f"({' | '.join(_render_literal(literal) for literal in clause)})"


def canonical(clause):
    """Sort literals and alpha-normalize variables, rejecting order ties."""
    if not clause:
        return "$false"
    masked = [_render_literal(literal, variable_mask="X") for literal in clause]
    if len(set(masked)) != len(masked):
        return None
    ordered = [literal for _, literal in sorted(zip(masked, clause), key=lambda item: item[0])]
    replacements = {}
    for literal in ordered:
        for variable in _walk_literal_variables(literal):
            if variable not in replacements:
                replacements[variable] = f"X{len(replacements) + 1}"
    return render_clause([_replace_variables_literal(literal, replacements) for literal in ordered])


def _term_depth(term):
    if not term.args:
        return 0
    return 1 + max(_term_depth(arg) for arg in term.args)


def clause_term_depth(clause):
    return max(
        (_term_depth(arg) for literal in clause for arg in literal.args),
        default=0,
    )


def _strip_answer_ticks(answer):
    answer = str(answer).strip()
    if answer.startswith("```") and answer.endswith("```"):
        answer = answer[3:-3].strip()
        if answer.startswith("tptp"):
            answer = answer[4:].lstrip()
    return answer.strip().strip("`").strip()


def _inference_rule(inference):
    inference = inference or ""
    match = re.search(r"inference\(([A-Za-z0-9_]+)", inference)
    if match:
        return match.group(1)
    match = re.match(r"([A-Za-z0-9_]+)", inference)
    return match.group(1) if match else "inference"


def extract_problem_from_graph(G: nx.DiGraph, node_id_str: str, max_length_proof: int):
    theorem = G.nodes[node_id_str]['data'].clause_formula
    frontier = {node_id_str}
    collected_hypotheses = set()
    
    for _ in range(max_length_proof):
        nxt = set()
        for v in frontier:
            parents = list(G.predecessors(v))
            if parents:
                # Continue traversing up the graph
                nxt.update(parents)
            else:
                # FIX: Capture leaves (axioms) encountered on short branches
                collected_hypotheses.add(v)

        if not nxt:
            break
        frontier = nxt
    
    # The final frontier (nodes at max_depth) are also hypotheses
    collected_hypotheses.update(frontier)
    
    hypotheses = [G.nodes[n]['data'].clause_formula for n in collected_hypotheses]
    hypotheses = [h for h in hypotheses if normalize_formula(h) != normalize_formula(theorem)]
    return hypotheses, theorem

def extract_useful_axioms(G: nx.DiGraph, node_id_str: str) : 
    ancestors = nx.ancestors(G, node_id_str)

    initial_ax = {n for n, in_degree in G.in_degree() if in_degree == 0}

    useful_ax = ancestors.intersection(initial_ax)

    return useful_ax


def normalize_formula(f: str) -> str:
    """Canonicalize formula: remove whitespace and anonymize variables."""
    if not f: return ""
    # Remove whitespace
    f = re.sub(r"\s+", "", f)
    # Replace variables (e.g., X123) with generic V to handle alpha-equivalence
    f = re.sub(r"X\d+", "V", f)
    return f

# 2. FIX: Clean CoT generation with step collapsing and better labeling
def make_cot(G: nx.DiGraph, target_node: str, formula_map: dict) -> str:
    sub = G.subgraph(nx.ancestors(G, target_node) | {target_node})
    lines = []
    node_to_label = {}
    step_counter = 0
    sys_ax_counter = 0  # Fixed variable name

    # Topological sort ensures we process parents before children
    for node in nx.topological_sort(sub):
        
        # Optimization: Skip intermediate 1-parent nodes (normalization/copy steps)
        # This removes "c_0_X" noise unless it's the final theorem
        parents = sorted(list(sub.predecessors(node)))
        if len(parents) == 1 and node != target_node:
            # Inherit label from the single parent (collapse step)
            p_lbl = node_to_label.get(parents[0])
            if p_lbl:
                node_to_label[node] = p_lbl
                continue

        data = sub.nodes[node]['data']
        f_norm = normalize_formula(data.clause_formula)
        
        val = formula_map.get(f_norm)
        is_theorem = (node == target_node)
        
        # Determine Label
        if not parents:
            # Leaf / Axiom
            if is_theorem:
                label = "THEOREM"
                lines.append(f"THEOREM [ '{data.clause_formula.strip()}' ] (axiom)")
            elif val is not None and str(val) != "THEOREM":
                label = f"premise_{val}"
            else:
                # Fallback for unmapped system axioms
                label = f"sys_ax_{sys_ax_counter}"
                sys_ax_counter += 1
            node_to_label[node] = label
            continue

        # Derived Node
        # Get parent labels
        p_labels = [node_to_label.get(p) for p in parents if p in node_to_label]
        if not p_labels: continue

        if is_theorem:
            label = "THEOREM"
        else:
            label = f"step_{step_counter}"
            step_counter += 1
        
        node_to_label[node] = label

        # Clean Inference Rule Name
        # Extract 'res', 'pm', 'rw' from string like "inference(rw,[status...])"
        inf_str = data.inference or ""
        rule_match = re.search(r'inference\(([a-zA-Z0-9_]+)', inf_str)
        if rule_match:
            rule_name = rule_match.group(1)
        else:
            # Fallback cleanup for non-standard formats
            rule_name = re.match(r'([a-zA-Z0-9_]+)', inf_str).group(1) if inf_str else "inference"
            if rule_name.startswith("c_0"): rule_name = "processing"

        lines.append(f"{label} {rule_name}({', '.join(p_labels)}): [ '{data.clause_formula.strip()}' ]")

    return "\n".join(lines).strip()

def perturb_list(input_l: list, base_domain: list, n_perturbations: int = 1) -> list:
    """Applies cumulative perturbations to a list."""
    lst = list(input_l) 
    base_set = set(base_domain)

    for _ in range(n_perturbations):
        complementary = base_set - set(lst)
        
        possible_ops = []
        if complementary:
            possible_ops.append('add')
            if lst: 
                possible_ops.append('replace')
        if len(lst) > 1:
            possible_ops.append('remove')
        if not possible_ops:
            break
            
        op_type = random.choice(possible_ops)
        
        if op_type == 'add':
            lst.insert(random.randint(0, len(lst)), random.choice(list(complementary)))
        elif op_type == 'remove':
            lst.pop(random.randint(0, len(lst) - 1))
        elif op_type == 'replace':
            index_to_replace = random.randint(0, len(lst) - 1)
            lst[index_to_replace] = random.choice(list(complementary))
            
    return lst


def prove_conjecture(axioms: list[str], conjecture: str,
                        time_limit_seconds: str ="30", verb: bool = False,
                        disprove_first: bool = False,
                        disprove_time_limit_seconds = None,
                        log_errors: bool = True):
    """
    Uses Vampire to prove or disprove a conjecture given a set of axioms.
    Returns True (provable), False (disprovable/countersatisfiable), or an error string.
    """
    with tempfile.NamedTemporaryFile(mode='w+', delete=True, suffix='.p') as temp_f:
        for i, axiom in enumerate(axioms, 1):
            temp_f.write(f"cnf(axiom_{i}, axiom, {axiom}).\n")
        temp_f.write(f"fof(conjecture_1, conjecture, {universally_quantify(conjecture)}).\n")
        temp_f.flush()
        
        if verb == True:
            print(f"---- proof file :-------------------------")
            temp_f.seek(0)  
            print(temp_f.read()) 
            print("-------------------------------------------------")


        prove_limit = str(time_limit_seconds)
        disprove_limit = str(disprove_time_limit_seconds or time_limit_seconds)
        vampire_command_proove = ["-t", prove_limit]
        vampire_command_disproove = ["-t", disprove_limit, "-sa", "fmb"]

        result_proove = None
        result_disproove = None

        if disprove_first:
            result_disproove = get_prover_session().run_prover('vampire', vampire_command_disproove, temp_f.name)

            if verb == True:
                print(f"output disproove vampire :  {result_disproove.stdout} ")

            if "Finite Model Found!" in result_disproove.stdout or "% SZS status CounterSatisfiable" in result_disproove.stdout:
                return False

        result_proove = get_prover_session().run_prover('vampire',vampire_command_proove,temp_f.name)

        if verb == True:
            print(f"output proove vampire :  {result_proove.stdout} ")

        if "% SZS status Theorem" in result_proove.stdout :
            return True
        if "% SZS status CounterSatisfiable" in result_proove.stdout :
            return False

        if result_disproove is None:
            result_disproove = get_prover_session().run_prover('vampire',vampire_command_disproove,temp_f.name)
    
        if verb == True:
            print(f"output disproove vampire :  {result_disproove.stdout} ")

        if "Finite Model Found!" in result_disproove.stdout or "% SZS status CounterSatisfiable" in result_disproove.stdout:
            return False
        if "% Time limit reached!" in result_proove.stdout and "% Time limit reached!" in result_disproove.stdout  :
            return f"ERROR : TIME LIMIT in both tentative to proove AND to disproove"
        if log_errors:
            print(f"[prove_conjecture] vampire failed:"
                  f"\n  prove: rc={result_proove.returncode} stdout={result_proove.stdout[:200]!r} stderr={result_proove.stderr[:200]!r}"
                  f"\n  disprove: rc={result_disproove.returncode} stdout={result_disproove.stdout[:200]!r} stderr={result_disproove.stderr[:200]!r}",
                  file=sys.stderr)
        return f"ERROR : {result_proove.stderr}{result_disproove.stderr}"


def check_clause_set_satisfiability(clauses, time_limit_seconds="5", log_errors=True):
    with tempfile.NamedTemporaryFile(mode="w+", delete=True, suffix=".p") as temp_f:
        for i, clause in enumerate(clauses, 1):
            temp_f.write(f"cnf(c{i}, axiom, {clause}).\n")
        temp_f.flush()

        sat = get_prover_session().run_prover(
            "vampire", ["-t", str(time_limit_seconds), "-sa", "fmb"], temp_f.name
        )
        if (
            "Finite Model Found!" in sat.stdout
            or "% SZS status Satisfiable" in sat.stdout
            or "% SZS status CounterSatisfiable" in sat.stdout
        ):
            return True

        unsat = get_prover_session().run_prover(
            "vampire", ["-t", str(time_limit_seconds)], temp_f.name
        )
        if "% SZS status Unsatisfiable" in unsat.stdout or "% SZS status Theorem" in unsat.stdout:
            return False

        if log_errors:
            print(
                "[check_clause_set_satisfiability] inconclusive:"
                f"\n  sat stdout={sat.stdout[:200]!r} stderr={sat.stderr[:200]!r}"
                f"\n  unsat stdout={unsat.stdout[:200]!r} stderr={unsat.stderr[:200]!r}",
                file=sys.stderr,
            )
        return None


dirs = AppDirs("Axioms_TPTP")
BASE_DIR = Path(__file__).resolve().parent.parent
AXIOM_ARCHIVE_PATH = BASE_DIR / "resources" / "axioms_filtered.json.gz"
DOMAIN_MAP = {
    'ALG': 'Algebra',
    'ANA': 'Analysis',
    'FLD': 'Field Theory',
    'GEO': 'Geometry',
    'GRP': 'Group Theory',
    'LCL': 'Logic Calculi',
    'NUM': 'Number Theory',
    'RNG': 'Ring Theory',
    'SET': 'Set Theory',
    'TOP': 'Topology'
}

def get_random_tptp_axioms(
    axiom_archive=AXIOM_ARCHIVE_PATH,
    prefixes=None,
    cache_dir=dirs.user_cache_dir ):

    try:
        with gzip.open(axiom_archive, 'rt', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, EOFError):
        return None, None

    keys = list(data.keys())
    if prefixes:
        keys = [k for k in keys if k.startswith(tuple(prefixes))]

    if not keys:
        return None, None
        
    chosen_key = random.choice(keys)
    content = data[chosen_key]

    try:
        os.makedirs(cache_dir, exist_ok=True)
        tempfile.TemporaryFile(dir=cache_dir).close()
    except OSError:
        cache_dir = tempfile.gettempdir()

    temp_file = tempfile.NamedTemporaryFile(
        mode='w+', 
        encoding='utf-8', 
        suffix='.p', 
        dir=cache_dir,
        delete=False  
    )
    
    with temp_file:
        temp_file.write(content)
        temp_file.flush()

    return temp_file.name, chosen_key

@dataclass
class EntailConfig(Config):
    proof_depth: int = 1
    perturbation: int = 1
    max_hypotheses: int = 8
    max_payload_chars: int = 2400
    min_interesting_score: float = 0.6
    positive_problem_ratio: float = 0.25
    domains = ['ALG', 'ANA', 'FLD', 'GEO', 'GRP', 'LCL', 'NUM', 'RNG', 'SET', 'TOP']

    def update(self, c):
        self.proof_depth += c
        self.perturbation += c
        self.max_hypotheses += c
        self.max_payload_chars += 500 * c

class ConjectureEntailment(Task):
    """
    A task that generates problems to determine if a set of hypotheses
    proves a given conjecture.
    """
    def __init__(self, config=EntailConfig()):
        super().__init__(config)
        # Initialize prover session at task init (pulls docker image if needed)
        # This ensures docker setup happens before any generation timing
        from reasoning_core.utils.udocker_process import initialize_prover_session
        initialize_prover_session()

    def _initialize_graph(self):
        for _ in range(100):
            axiom_file_path, axiom_file_name = get_random_tptp_axioms(prefixes=self.config.domains)

            if axiom_file_path:
                self.axiom_set = axiom_file_name
            self.graph = generate_derivation_graph( 
                    axiom_file = axiom_file_path, 
                    save_output=False, 
                    ranking=True, 
                    e_limit=2
                )
            if os.path.exists(axiom_file_path):
                os.remove(axiom_file_path)
            

            self.all_formulas = [data['data'].clause_formula for _, data in self.graph.nodes(data=True)]
            self.interesting_thm = []

            for i in self.graph.nodes() : 
                if self.graph.nodes[i]['data'].interesting_score > self.config.min_interesting_score and self.graph.in_degree(i) > 1 :
                    self.interesting_thm.append(i)
            if len(self.interesting_thm) >= 5 :
                break

    def generate(self):
        self._initialize_graph()

        for attempt in range(50):
            theorem_node_id = random.choice(list(self.interesting_thm))
            correct_hypotheses, theorem = extract_problem_from_graph(self.graph, theorem_node_id, self.config.proof_depth)
            if random.random() < self.config.positive_problem_ratio:
                hypotheses = correct_hypotheses
                if len(hypotheses) > self.config.max_hypotheses or sum(map(len, hypotheses)) + len(theorem) > self.config.max_payload_chars:
                    continue
                try:
                    if prove_conjecture(hypotheses, theorem, time_limit_seconds="15") is not True:
                        continue
                except TimeoutError:
                    continue
                answer = True
            else:
                distraction_pool = list(set(self.all_formulas) - {theorem})
                hypotheses = perturb_list(correct_hypotheses, distraction_pool ,self.config.perturbation)
                if len(hypotheses) > self.config.max_hypotheses or sum(map(len, hypotheses)) + len(theorem) > self.config.max_payload_chars:
                    continue
                try:
                    answer = prove_conjecture(hypotheses, theorem, time_limit_seconds="15")
                except TimeoutError:
                    continue

            if isinstance(answer, bool):
                metadata = edict({'hypotheses': hypotheses,
                            'conjecture': theorem,
                            'correct_hypotheses': correct_hypotheses ,
                            'proof_depth' : self.config.proof_depth,
                            'perturbation' : self.config.perturbation ,
                            'axiom_set' : self.axiom_set})
                return Problem(metadata, str(answer))
        return None

    def prompt(self, metadata):

        hypotheses_text = "\n".join([f"- {h}" for h in metadata['hypotheses']])
        domain_name = DOMAIN_MAP.get(metadata['axiom_set'][:3], metadata['axiom_set'])

        return (
            f"Decide if the premises entail the conjecture.\n\n"
            f"Domain: {domain_name}\n\n"
            f"Premises:\n{hypotheses_text}\n\n"
            f"Conjecture: `{metadata['conjecture']}`\n\n"
            f"The answer is `True` (provable) or `False` (not provable)."
        )
    
    def score_answer(self, answer, entry):
        ref = entry.answer.lower()
        pred = str(answer).lower().strip().strip('"').strip("'")
        return float(ref==pred)


def negate_clause_formula(formula):
    try:
        clause = parse_clause(formula)
    except (TypeError, ValueError):
        return None
    if len(clause) != 1:
        return None
    lit = clause[0]
    return render_clause([TPTPLiteral(not lit.sign, lit.pred, lit.args)])


@dataclass
class ConsistencyRepairConfig(Config):
    proof_depth: int = 1
    perturbation: int = 1
    max_axioms: int = 8
    max_payload_chars: int = 2400
    min_interesting_score: float = 0.6
    sat_time_limit: str = "5"
    unsat_time_limit: str = "8"
    max_attempts: int = 50
    domains = ['ALG', 'ANA', 'FLD', 'GEO', 'GRP', 'LCL', 'NUM', 'RNG', 'SET', 'TOP']

    def update(self, c):
        self.proof_depth += c
        self.perturbation += c
        self.max_axioms += c
        self.max_payload_chars += 500 * c


class TPTPConsistencyRepair(Task):
    """Find a smallest one-axiom deletion that restores satisfiability."""
    def __init__(self, config=ConsistencyRepairConfig()):
        super().__init__(config, timeout=180)
        from reasoning_core.utils.udocker_process import initialize_prover_session
        initialize_prover_session()

    _initialize_graph = ConjectureEntailment._initialize_graph

    def _fallback_problem(self):
        p, q, r = random.sample(["p", "q", "r", "s", "t"], 3)
        a = random.choice(["a", "b", "c"])
        clauses = [
            f"({p}({a}))",
            f"({q}({a}))",
            f"(~{p}({a}) | {r}({a}))",
            f"(~{q}({a}) | {r}({a}))",
            f"(~{r}({a}))",
        ]
        sats = [
            check_clause_set_satisfiability(
                clauses[:i] + clauses[i + 1:], self.config.sat_time_limit, log_errors=False
            )
            for i in range(len(clauses))
        ]
        repairs = [i + 1 for i, sat in enumerate(sats) if sat is True]
        if (
            check_clause_set_satisfiability(clauses, self.config.unsat_time_limit, log_errors=False) is False
            and sats == [False, False, False, False, True]
        ):
            return Problem(edict({"clauses": clauses, "repair_indices": repairs, "axiom_set": "SYNTHETIC"}), str(repairs))
        raise RuntimeError("failed to certify fallback TPTP consistency-repair task")

    def generate(self):
        if self.config.max_attempts <= 0:
            return self._fallback_problem()
        self._initialize_graph()
        if not self.interesting_thm:
            raise RuntimeError("no interesting TPTP theorems found")

        for _ in range(self.config.max_attempts):
            theorem_node_id = random.choice(self.interesting_thm)
            hypotheses, theorem = extract_problem_from_graph(
                self.graph, theorem_node_id, self.config.proof_depth
            )
            if not hypotheses or prove_conjecture(hypotheses, theorem, time_limit_seconds="10") is not True:
                continue
            neg_theorem = negate_clause_formula(theorem)
            if neg_theorem is None:
                continue

            clauses = list(dict.fromkeys(hypotheses + [neg_theorem]))
            if len(clauses) > self.config.max_axioms:
                continue
            if sum(map(len, clauses)) > self.config.max_payload_chars:
                continue
            if check_clause_set_satisfiability(
                clauses, self.config.unsat_time_limit, log_errors=False
            ) is not False:
                continue

            repairs = []
            for i in range(len(clauses)):
                sat = check_clause_set_satisfiability(
                    clauses[:i] + clauses[i + 1:],
                    self.config.sat_time_limit,
                    log_errors=False,
                )
                if sat is None:
                    repairs = None
                    break
                if sat:
                    repairs.append(i + 1)
            if repairs is None or len(repairs) != 1:
                continue

            metadata = edict({
                "clauses": clauses,
                "repair_indices": repairs,
                "negated_theorem": neg_theorem,
                "hypotheses": hypotheses,
                "axiom_set": self.axiom_set,
                "proof_depth": self.config.proof_depth,
            })
            return Problem(metadata, str(repairs))
        return self._fallback_problem()

    def prompt(self, metadata):
        clauses = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(metadata["clauses"]))
        return (
            "Unsatisfiable theory.\n"
            "Remove a smallest set of clauses to make it satisfiable.\n"
            "The answer is sorted clause numbers.\n\n"
            f"Clauses:\n{clauses}"
        )

    def score_answer(self, answer, entry):
        try:
            pred = set(ast.literal_eval(str(answer)))
        except Exception:
            pred = set(map(int, re.findall(r"\d+", str(answer))))
        return float(pred == set(ast.literal_eval(entry.answer)))
