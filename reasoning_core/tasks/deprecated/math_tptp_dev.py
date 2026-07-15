from dataclasses import dataclass
from itertools import combinations
from math import comb
import ast
import os
import random
import re
import tempfile

import networkx as nx
from easydict import EasyDict as edict

from reasoning_core.template import Config, DevTask, Problem, TimeoutException
from reasoning_core.tasks.math_tptp import (
    TptpEntailment, DOMAIN_MAP, apply_subst_literal, canonical,
    check_clause_set_satisfiability, clause_term_depth, extract_problem_from_graph,
    extract_useful_axioms, generate_derivation_graph, make_cot, normalize_formula,
    parse_clause, prove_conjecture, rename_apart, render_clause, resolvents,
    run_vampire_fmb_signed, serialize_model, validate_formula,
    model_is_nondegenerate, requirement_holds, requirements_hold,
    _inference_rule, _strip_answer_ticks, _walk_literal_variables, logger,
)

def _verdict_answer(verdicts):
    return "\n".join(
        f"{index}: {'True' if verdict else 'False'}"
        for index, verdict in enumerate(verdicts, 1)
    )


def _parse_verdict_answer(answer, count):
    rows = {}
    for line in str(answer).strip().splitlines():
        match = re.fullmatch(r"\s*(\d+)\s*:\s*(true|false)\s*", line, re.IGNORECASE)
        if not match:
            return None
        index = int(match.group(1))
        if index in rows or not 1 <= index <= count:
            return None
        rows[index] = match.group(2).lower() == "true"
    if set(rows) != set(range(1, count + 1)):
        return None
    return [rows[index] for index in range(1, count + 1)]


@dataclass
class FiniteInterpretationCheckConfig(Config):
    proof_depth: int = 1
    perturbation: int = 1
    min_interesting_score: float = 0.6
    false_requirement_ratio: float = 0.7
    positive_problem_ratio: float = 0.5
    fmb_time_limit: str = "8"
    max_attempts: int = 50
    max_context_axioms: int = 0
    min_domain_size: int = 2
    max_domain_size: int = 3
    allow_constant_symbols: int = 0
    sparse_model_ratio: float = 0.75
    domains = ['ALG', 'ANA', 'FLD', 'GEO', 'GRP', 'LCL', 'NUM', 'RNG', 'SET', 'TOP']

    def update(self, c):
        self.proof_depth += c
        self.perturbation += c


class FiniteInterpretationCheck(DevTask):
    """Evaluate signed first-order requirements in a finite interpretation."""
    def __init__(self, config=None):
        super().__init__(config=config or FiniteInterpretationCheckConfig(), timeout=180)
        from reasoning_core.utils.udocker_process import initialize_prover_session
        initialize_prover_session()

    _initialize_graph = TptpEntailment._initialize_graph

    def _make_requirements(self, hypotheses, theorem):
        use_false_goal = random.random() < self.config.false_requirement_ratio
        selected_hypotheses = list(hypotheses)
        if use_false_goal:
            distractions = list(set(self.all_formulas) - set(hypotheses) - {theorem})
            for _ in range(self.config.perturbation):
                if len(selected_hypotheses) > 1 and (not distractions or random.random() < 0.5):
                    selected_hypotheses.pop(random.randrange(len(selected_hypotheses)))
                elif selected_hypotheses and distractions:
                    selected_hypotheses[random.randrange(len(selected_hypotheses))] = random.choice(
                        distractions
                    )
            selected_hypotheses = list(dict.fromkeys(selected_hypotheses))

        requirements = [
            {"formula": hypothesis, "should_be": True}
            for hypothesis in selected_hypotheses
        ]
        requirements.append({"formula": theorem, "should_be": not use_false_goal})
        return requirements

    def _context_axioms(self, theorem_node_id, requirements):
        if self.config.max_context_axioms <= 0:
            return []
        req_norm = {normalize_formula(req["formula"]) for req in requirements}
        axioms = [
            self.graph.nodes[node_id]["data"].full_cnf_clause
            for node_id in extract_useful_axioms(self.graph, theorem_node_id)
            if normalize_formula(self.graph.nodes[node_id]["data"].clause_formula) not in req_norm
        ]
        random.shuffle(axioms)
        return axioms[:min(3, self.config.max_context_axioms)]

    def _generate_model(self, requirements, make_negative):
        solver_requirements = [dict(requirement) for requirement in requirements]
        flipped_index = None
        if make_negative:
            flipped_index = random.randrange(len(solver_requirements))
            solver_requirements[flipped_index]["should_be"] = not solver_requirements[
                flipped_index
            ]["should_be"]

        domain_size = random.randint(
            self.config.min_domain_size,
            max(self.config.min_domain_size, self.config.max_domain_size),
        )
        model = run_vampire_fmb_signed(
            solver_requirements,
            time_limit_seconds=self.config.fmb_time_limit,
            min_domain_size=domain_size,
        )
        if not model_is_nondegenerate(
            model,
            min_domain_size=domain_size,
            allow_constant_symbols=self.config.allow_constant_symbols,
        ):
            return None
        if not requirements_hold(solver_requirements, model):
            return None

        verdicts = [requirement_holds(requirement, model) for requirement in requirements]
        if make_negative:
            if all(verdicts) or verdicts[flipped_index]:
                return None
        elif not all(verdicts):
            return None
        return model, verdicts, flipped_index

    def generate(self):
        self._initialize_graph()
        if not self.interesting_thm:
            return None

        for _ in range(self.config.max_attempts):
            theorem_node_id = random.choice(self.interesting_thm)
            hypotheses, theorem = extract_problem_from_graph(
                self.graph,
                theorem_node_id,
                self.config.proof_depth,
            )
            if not hypotheses:
                continue
            requirements = self._make_requirements(hypotheses, theorem)
            try:
                for requirement in requirements:
                    validate_formula(requirement["formula"])
            except ValueError:
                continue

            make_negative = random.random() >= self.config.positive_problem_ratio
            generated = self._generate_model(requirements, make_negative)
            if generated is None:
                continue
            model, verdicts, flipped_index = generated
            largest_table = max(
                [len(table) for table in model.functions.values()]
                + [len(table) for table in model.predicates.values()]
                + [0]
            )
            sparse = (
                largest_table > 16
                or random.random() < self.config.sparse_model_ratio
            )
            metadata = edict({
                "requirements": requirements,
                "model": serialize_model(model, sparse=sparse),
                "model_format": "default-with-exceptions" if sparse else "full-table",
                "context_axioms": self._context_axioms(theorem_node_id, requirements),
                "axiom_set": self.axiom_set,
                "proof_depth": self.config.proof_depth,
                "domain_size": len(model.domain),
                "flipped_requirement": (
                    flipped_index + 1 if flipped_index is not None else None
                ),
                "verdicts": verdicts,
            })
            return Problem(metadata, _verdict_answer(verdicts))
        return None

    def prompt(self, metadata):
        domain_name = DOMAIN_MAP.get(metadata["axiom_set"][:3], metadata["axiom_set"])
        requirements = "\n".join(
            f"{i}. Must be {'True' if req['should_be'] else 'False'}: {req['formula']}"
            for i, req in enumerate(metadata["requirements"], 1)
        )
        context = metadata.get("context_axioms", [])
        context_text = ""
        if context:
            context_text = "Context:\n" + "\n".join(f"- {axiom}" for axiom in context) + "\n\n"
        return (
            "Evaluate each signed requirement in the finite interpretation.\n"
            f"Domain area: {domain_name}\n"
            "Variables are universally quantified. `Must be False` holds when the formula "
            "is false for at least one variable assignment.\n"
            "In compact tables, `default` applies to every tuple not listed.\n\n"
            f"{context_text}Requirements:\n{requirements}\n\n"
            f"Interpretation:\n{metadata['model']}\n\n"
            "Answer one line per requirement: `N: True` if its signed requirement holds, "
            "otherwise `N: False`."
        )

    def score_answer(self, answer, entry):
        expected = entry.metadata.get("verdicts")
        if expected is None:
            expected = _parse_verdict_answer(entry.answer, len(entry.metadata["requirements"]))
        predicted = _parse_verdict_answer(answer, len(expected))
        return float(predicted == list(expected))

    def balancing_key(self, problem):
        return "all_true" if all(problem.metadata.verdicts) else "has_false"


@dataclass
class ResolutionStepConfig(Config):
    min_total_literals: int = 3
    min_term_depth: int = 1
    min_interesting_score: float = 0.6
    allow_superposition: bool = False
    domains = ['ALG', 'ANA', 'FLD', 'GEO', 'GRP', 'LCL', 'NUM', 'RNG', 'SET', 'TOP']

    def update(self, c):
        self.min_total_literals += c
        self.min_term_depth += c


class ResolutionStep(DevTask):
    """Reconstruct one validated binary-resolution step from an E derivation."""
    def __init__(self, config=None):
        super().__init__(config=config or ResolutionStepConfig(), timeout=120)
        from reasoning_core.utils.udocker_process import initialize_prover_session
        initialize_prover_session()
        self.pool = []

    def on_config_level_change(self):
        self.pool = []

    _initialize_graph = TptpEntailment._initialize_graph

    def _mine_pool(self):
        candidates = 0
        parsed = 0
        unique = 0
        accepted = []

        for child_id, in_degree in self.graph.in_degree():
            if in_degree != 2:
                continue
            candidates += 1
            parent_a_id, parent_b_id = sorted(self.graph.predecessors(child_id), key=str)
            parent_a = self.graph.nodes[parent_a_id]["data"]
            parent_b = self.graph.nodes[parent_b_id]["data"]
            child = self.graph.nodes[child_id]["data"]

            try:
                clause_a = parse_clause(parent_a.clause_formula)
                original_b = parse_clause(parent_b.clause_formula)
                child_clause = parse_clause(child.clause_formula)
            except (TypeError, ValueError):
                continue
            parsed += 1

            variables_a = {
                variable
                for literal in clause_a
                for variable in _walk_literal_variables(literal)
            }
            clause_b = rename_apart(original_b, forbidden=variables_a)
            possible = resolvents(clause_a, clause_b)
            if len(possible) != 1:
                continue
            unique += 1

            answer = canonical(possible[0])
            child_canonical = canonical(child_clause)
            if answer is None or child_canonical is None or answer != child_canonical:
                continue

            total_literals = len(clause_a) + len(clause_b)
            term_depth = max(clause_term_depth(clause_a), clause_term_depth(clause_b))
            if total_literals < self.config.min_total_literals:
                continue
            if term_depth < self.config.min_term_depth:
                continue

            metadata = edict({
                "clause_a": render_clause(clause_a),
                "clause_b": render_clause(clause_b),
                "rule": _inference_rule(child.inference),
                "axiom_set": self.axiom_set,
                "total_literals": total_literals,
                "term_depth": term_depth,
                "resolvent_literals": len(possible[0]),
            })
            accepted.append(Problem(metadata, answer))

        random.shuffle(accepted)
        self.pool = accepted
        mean_literals = (
            sum(problem.metadata.total_literals for problem in accepted) / len(accepted)
            if accepted else 0.0
        )
        mean_depth = (
            sum(problem.metadata.term_depth for problem in accepted) / len(accepted)
            if accepted else 0.0
        )
        logger.info(
            "ResolutionStep level=%s candidates=%d parsed=%d unique=%d accepted=%d "
            "yield=%.3f mean_literals=%.2f mean_term_depth=%.2f",
            self.config.level,
            candidates,
            parsed,
            unique,
            len(accepted),
            len(accepted) / candidates if candidates else 0.0,
            mean_literals,
            mean_depth,
        )

    def generate(self):
        if not self.pool:
            self._initialize_graph()
            self._mine_pool()
        if not self.pool:
            return None
        return self.pool.pop()

    def prompt(self, metadata):
        domain_name = DOMAIN_MAP.get(metadata["axiom_set"][:3], metadata["axiom_set"])
        return (
            "Apply one step of binary resolution.\n"
            f"Domain: {domain_name}\n\n"
            f"Clause A: {metadata['clause_a']}\n"
            f"Clause B: {metadata['clause_b']}\n\n"
            "A and B share no variables. Exactly one pair of complementary literals is unifiable.\n"
            "The answer is the canonicalized resolvent: literals sorted alphabetically after replacing variables by 'X', "
            "then variables renamed X1, X2, ... by first occurrence; e.g. (p(X1,f(X2)) | ~q(X1))."
        )

    def score_answer(self, answer, entry):
        prediction = _strip_answer_ticks(answer)
        try:
            parsed = canonical(parse_clause(prediction))
        except (TypeError, ValueError):
            compact_prediction = re.sub(r"\s+", "", prediction)
            compact_reference = re.sub(r"\s+", "", str(entry.answer))
            return float(compact_prediction == compact_reference)
        return float(parsed is not None and parsed == entry.answer)


@dataclass
class SelectionConfig(Config):
    proof_depth: int = 1
    min_interesting_score: float = 0.6
    num_distractors: int = 2
    domains = ['ALG', 'ANA', 'FLD', 'GEO', 'GRP', 'LCL', 'NUM', 'RNG', 'SET', 'TOP']

    def update(self, c):
        self.proof_depth += c
        self.num_distractors += c


class TheoremPremiseSelection(DevTask):
    """
    A task that generates problems where one must select the essential hypotheses
    required to prove a given conjecture from a larger pool of axioms.
    And a minimality check to ensure the ground truth is correct.
    """
    def __init__(self, config=None):
        super().__init__(config=config or SelectionConfig(), timeout=60)
        # Initialize prover session at task init
        from reasoning_core.utils.udocker_process import initialize_prover_session
        initialize_prover_session()

    _initialize_graph = TptpEntailment._initialize_graph
    max_pool_validation_checks = 512

    def _reprove_with_minimal(self, hypotheses: list) -> nx.DiGraph:
            """
            Run E-prover on ONLY the minimal set as AXIOMS. 
            No conjecture is passed; we rely on derivation to find the theorem node.
            """
            # Change delete=True to delete=False
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.p', delete=False) as tf:
                for i, h in enumerate(hypotheses):
                    tf.write(f"cnf(h_{i}, axiom, {h}).\n")
                # No need to flush if we close immediately, but good practice
                tf.flush()
                
            # File is now closed and safe for subprocesses to read
            try:
                return generate_derivation_graph(tf.name, save_output=False, e_limit=2, ranking=False)
            finally:
                # Clean up manually
                if os.path.exists(tf.name):
                    os.remove(tf.name)
                    
    def find_minimal_hypotheses(self, initial_hypotheses: list[str], conjecture: str) -> list[str]:
        """
        Prunes an initial set of hypotheses down to a minimal subset that is
        still sufficient to prove the conjecture.
        """
        essential_hypotheses = set(initial_hypotheses)
        
        for h in initial_hypotheses:
            
            temp_set = essential_hypotheses.copy()
            if h in temp_set:
                temp_set.remove(h)
            else:
                continue 

            is_provable = prove_conjecture(
                list(temp_set),
                conjecture,
                time_limit_seconds="15",
                disprove_first=True,
                disprove_time_limit_seconds="2",
            )
            
            if is_provable is True:
                essential_hypotheses.remove(h)
                
        return list(essential_hypotheses)

    def _has_no_smaller_answer(self, pool: list[str], answer: list[str], theorem: str) -> bool:
        pool_norm = [normalize_formula(h) for h in pool]
        if len(pool_norm) != len(set(pool_norm)):
            return False

        n, k = len(pool), len(answer)
        checks = 1 if k == 1 else comb(n, k - 1)
        if checks > self.max_pool_validation_checks:
            return False

        # By monotonicity, any smaller proof extends to one with exactly k-1 premises.
        candidate_indices = [()] if k == 1 else combinations(range(n), k - 1)
        for idxs in candidate_indices:
            result = prove_conjecture(
                [pool[i] for i in idxs],
                theorem,
                time_limit_seconds="2",
                disprove_first=True,
                disprove_time_limit_seconds="2",
                log_errors=False,
            )
            if result is not False:
                return False
        return True

    def generate(self):
        self._initialize_graph()
    
        for _ in range(50):
            if not self.interesting_thm:
                self._initialize_graph()
                if not self.interesting_thm: continue

            theorem_node_id = random.choice(self.interesting_thm)
            
            # 1. Extract Superset & Minimize
            superset, theorem = extract_problem_from_graph(
                self.graph, theorem_node_id, self.config.proof_depth
            )
            if len(superset)>20:
                continue
            
            try:
                # Verify superset (optimization)
                if prove_conjecture(superset, theorem, time_limit_seconds="15") is not True: continue

                minimal = self.find_minimal_hypotheses(superset, theorem)

                # Verify minimal (safety)
                if not minimal or prove_conjecture(minimal, theorem, time_limit_seconds="15") is not True: continue
            except TimeoutException:
                raise TimeoutException
            except Exception:
                continue
            # 2. Create Distractors & Pool
            distractor_pool = list(set(self.all_formulas) - set(minimal) - {theorem})
            if len(distractor_pool) < self.config.num_distractors: continue

            distractors = random.sample(distractor_pool, self.config.num_distractors)
            pool = minimal + distractors
            random.shuffle(pool)
            if not self._has_no_smaller_answer(pool, minimal, theorem):
                continue

            # 3. RE-PROVE for Clean CoT (Forward Derivation)
            clean_graph = self._reprove_with_minimal(minimal)
            
            # Locate theorem node in new graph
            target_node = None
            clean_theorem_str = normalize_formula(theorem)
            
            for n, d in clean_graph.nodes(data=True):
                if normalize_formula(d['data'].clause_formula) == clean_theorem_str:
                    target_node = n
                    break
            
            if not target_node: continue

            # 4. Generate CoT
            # Map ONLY minimal premises to their pool indices.
            # This ensures distractors (if derived coincidentally) aren't labeled as premises.
            f_map = {normalize_formula(h): pool.index(h)+1 for h in minimal}
            f_map[clean_theorem_str] = "THEOREM"

            cot = make_cot(clean_graph, target_node, f_map)

            # 5. Metadata & Context Filtering
            pool_norm = set(normalize_formula(h) for h in pool)
            useful_axioms_norm = []
            orig_useful_ids = extract_useful_axioms(self.graph, theorem_node_id)
            
            for uid in orig_useful_ids:
                u_cnf = self.graph.nodes[uid]['data'].full_cnf_clause
                if normalize_formula(self.graph.nodes[uid]['data'].clause_formula) not in pool_norm:
                    useful_axioms_norm.append(u_cnf)

            metadata = edict({
                'hypotheses_pool': pool, 
                'theorem': theorem,
                'cot': cot,
                'len_superset': len(superset),
                'correct_indices': sorted([pool.index(h) + 1 for h in minimal]),
                'correct_minimal_hypotheses': minimal, 
                'useful_axioms': useful_axioms_norm, 
                'axiom_set': self.axiom_set
            })
            
            return Problem(metadata, str(metadata.correct_indices))

    def prompt(self, metadata):
    
        axiom_text = "\n".join([f"- {h}" for h in metadata['useful_axioms']])
        hypotheses_text = "\n".join(
            [f"{i+1}. {h}" for i, h in enumerate(metadata['hypotheses_pool'])]
        )
        domain_name = DOMAIN_MAP.get(metadata['axiom_set'][:3],metadata['axiom_set'])

        
        return (
            f"Your task is to identify a minimal set of premises sufficient for a proof.\n\n"
            f"By using the **Superposition Calculus** (which includes rules like Resolution and Paramodulation).\n"
            f"## General Context\n"
            f"The problem is set in the domain of: **{domain_name}**.\n"
            f"The following are the fundamental axioms of this domain. They provide general context. **Do not use them in the proof itself.**\n"
            f"Fundamental Axioms:\n"
            f"{axiom_text}\n\n"
            f"## Task\n"
            f"Your goal is to prove the following theorem:\n"
            f"**Theorem:**\n"
            f"`{metadata['theorem']}`\n\n"
            f"Below is a numbered pool of potential premises. Your task is to identify the **minimal subset** of numbers from this pool whose corresponding statements are **sufficient on their own** to prove the theorem.\n"
            f"**Pool of Premises:**\n"
            f"{hypotheses_text}\n\n"
            f"### Question\n"
            f"Which is the smallest set of numbered premises from the pool that is sufficient to prove the theorem, without using the fundamental axioms from the context?\n\n"
            f"### Response Format\n"
            f"The answer is a list of numbers, sorted in increasing order. For example: `[2, 5, 8]`."
        )


    def score_answer(self, answer, entry):
        """
        Scores the answer using the Jaccard Index .
        """
        metadata = entry.metadata
        hypotheses_pool = metadata.get('hypotheses_pool')
        if not hypotheses_pool:
            return 0.0


        truth_indices = set(ast.literal_eval(entry.answer))
        pred_indices = set(map(int, re.findall(r'\d+', str(answer))))


        intersection = len(truth_indices.intersection(pred_indices))
        union = len(truth_indices.union(pred_indices))

        if union == 0:
            return 1.0  

        return intersection / union


@dataclass
class ReconstructionConfig(Config):
    proof_depth: int = 2 #otherwise it's trivial
    min_interesting_score: float = 0
    domains = ['ALG', 'ANA', 'FLD', 'GEO', 'GRP', 'LCL', 'NUM', 'RNG', 'SET', 'TOP']

    def update(self, c):
        self.proof_depth += c


def make_parent_table(proof_graph, node_to_idx, node_order=None):
    lines = []
    if node_order is None:
        node_order = sorted(proof_graph.nodes(), key=node_to_idx.get)

    for node in node_order:
        i = node_to_idx[node]
        parents = list(proof_graph.predecessors(node))

        if not parents:
            lines.append(f"{i}: axiom")
        else:
            p1, p2 = sorted(node_to_idx[p] for p in parents)
            lines.append(f"{i}: parents {p1} {p2}")

    return lines


def parse_parent_table(answer, n):
    rows = {}
    ax_pat = re.compile(r'^\s*(\d+)\s*:\s*axiom\s*$')
    par_pat = re.compile(r'^\s*(\d+)\s*:\s*parents\s+(\d+)\s*,?\s+(\d+)\s*$')

    for line in str(answer).strip().splitlines():
        line = line.strip()

        m = ax_pat.fullmatch(line)
        if m:
            i = int(m.group(1))
            if 1 <= i <= n:
                rows[i] = ()
            continue

        m = par_pat.fullmatch(line)
        if m:
            i, p1, p2 = map(int, m.groups())
            if 1 <= i <= n and 1 <= p1 <= n and 1 <= p2 <= n:
                if p1 != p2 and i not in (p1, p2):
                    rows[i] = tuple(sorted((p1, p2)))

    return rows


class ProofReconstruction(DevTask):
    """
    A task that generates problems where one must reconstruct the derivation
    graph from a numbered list of shuffled clauses.
    """
    def __init__(self, config=None):
        super().__init__(config=config or ReconstructionConfig())
        # Initialize prover session at task init
        from reasoning_core.utils.udocker_process import initialize_prover_session
        initialize_prover_session()
        
    _initialize_graph = TptpEntailment._initialize_graph
    

    def generate(self):

        self._initialize_graph()
        useless_axioms = {n for n, d in self.graph.in_degree() if d == 0}

        redundant_children = set()
        for ax_id in useless_axioms:
            if self.graph.out_degree(ax_id) == 1:
                child_id = list(self.graph.successors(ax_id))[0]
                if self.graph.nodes[ax_id]['data'].clause_formula == self.graph.nodes[child_id]['data'].clause_formula:
                    redundant_children.add(child_id)
        nodes_to_remove = useless_axioms.union(redundant_children)

        self.graph.remove_nodes_from(nodes_to_remove)
            
        all_axioms = {node for node, in_degree in self.graph.in_degree() if in_degree == 0}
        
        interesting_theorems = self.interesting_thm

        valid_paths = []
        for theorem_id in interesting_theorems:
            ancestor_axioms = nx.ancestors(self.graph, theorem_id) & all_axioms
            
            for axiom_id in ancestor_axioms:
                path_length = nx.shortest_path_length(self.graph, source=axiom_id, target=theorem_id)
                
                if 0 < path_length <= self.config.proof_depth:
                    
                    proof_nodes = nx.ancestors(self.graph, theorem_id)
                    proof_nodes.add(theorem_id)
                    num_nodes = len(proof_nodes)
                    min_size = 2**(self.config.proof_depth) - 1
                    max_size = 2**(self.config.proof_depth+1) - 1
                    
                    if min_size < num_nodes <= max_size:

                        is_binary = all(
                            self.graph.in_degree(n) in (0, 2) for n in proof_nodes
                        )

                        if is_binary:
                            valid_paths.append((axiom_id, theorem_id))
                            break 

        if not valid_paths:
            return None

        axiom_id, theorem_node_id = random.choice(valid_paths)
        
        proof_nodes = nx.ancestors(self.graph, theorem_node_id)
        proof_nodes.add(theorem_node_id)
        proof_graph = self.graph.subgraph(proof_nodes)

        # 1. Shuffle clause numbers to keep reconstruction non-trivial.
        node_order = list(proof_graph.nodes())
        random.shuffle(node_order)
        node_to_idx = {n: i + 1 for i, n in enumerate(node_order)}
        
        all_clauses_in_proof = [proof_graph.nodes[n]['data'].clause_formula for n in node_order]
        
        # 2. Reject ambiguous graphs where duplicate formulas exist (unfair to the LLM)
        if len(set(all_clauses_in_proof)) != len(all_clauses_in_proof):
            return None

        theorem_formula = self.graph.nodes[theorem_node_id]['data'].clause_formula
        proof_structure_indices = []

        # 3. Build the output strings securely using the dictionary mapping
        for node_id in proof_graph.nodes():
            parents = list(proof_graph.predecessors(node_id))
            if parents:  
                child_idx = node_to_idx[node_id]
                parent_indices = sorted([node_to_idx[p] for p in parents])
                
                proof_structure_indices.append(f"{child_idx} <- {parent_indices[0]}, {parent_indices[1]}")

        proof_structure_ids = [f"{node} <- {', '.join(sorted(list(proof_graph.predecessors(node))))}" for node in proof_graph.nodes() if proof_graph.in_degree(node) > 0]
        

        f_map = {normalize_formula(c): i+1 for i, c in enumerate(all_clauses_in_proof)}
        cot = make_cot(proof_graph, theorem_node_id, f_map)
        answer_node_order = list(nx.lexicographical_topological_sort(proof_graph, key=str))
        parent_table = make_parent_table(proof_graph, node_to_idx, answer_node_order)

        metadata = edict({
            'numbered_clauses': all_clauses_in_proof, 
            'conjecture': theorem_formula,
            'cot': cot,
            'correct_proof_structure_indices' : proof_structure_indices,
            'correct_parent_table': parent_table,
            'correct_proof_structure_ids': sorted(proof_structure_ids),
            'correct_proof_graph' : str(proof_graph),
            'proof_depth' : self.config.proof_depth,
            'axiom_set': self.axiom_set
        })

        answer = "\n".join(parent_table)
        return Problem(metadata, answer)

    def prompt(self, metadata):
        clauses_text = "\n".join([f"{i+1}. {c}" for i, c in enumerate(metadata['numbered_clauses'])])
        domain_name = DOMAIN_MAP.get(metadata['axiom_set'][:3], metadata['axiom_set'])

        return (
            f"You are given the clauses from one generated proof trace, in shuffled order.\n"
            f"Domain: {domain_name}\n"
            f"Theorem: {metadata['conjecture']}\n\n"
            f"Each clause is either an axiom of this trace, or a derived clause with exactly two recorded parent clauses.\n\n"
            f"Numbered clauses:\n{clauses_text}\n\n"
            f"Response format:\n"
            f"- Write exactly one line per clause, ordered so parent clauses appear before derived clauses\n"
            f"- Use `N: axiom` if clause N has no parents\n"
            f"- Use `N: parents A B` if clause N is derived from A and B\n"
            f"- Parent numbers A and B must be sorted increasingly\n\n"
            f"Example:\n"
            f"2: axiom\n"
            f"5: axiom\n"
            f"1: parents 2 5\n"
            f"4: axiom\n"
            f"3: parents 1 4\n"
        )
    
    def score_answer(self, answer, entry):
        gold = entry.metadata.get('correct_parent_table') or []
        n = len(entry.metadata.get('numbered_clauses', []))
        if not n or not gold:
            return 0.0

        gold_rows = parse_parent_table("\n".join(gold), n)
        pred_rows = parse_parent_table(answer, n)

        return sum(pred_rows.get(i) == gold_rows.get(i) for i in range(1, n + 1)) / n
