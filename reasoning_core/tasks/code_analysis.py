import hashlib
import random
import re
from collections import deque
from dataclasses import dataclass
from itertools import product

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround


@dataclass
class CodeAnalysisConfig(Config):
    n_vars: int = 2
    domain_size: int = 2
    n_modes: int = 2
    n_predicates: int = 3
    formula_depth: int = 2
    branchiness: int = 2
    max_states: int = 32
    min_witness_len: int = 2
    max_retries: int = 200

    def apply_difficulty(self, level):
        self.n_vars = sround(self.n_vars + 0.45 * level)
        self.domain_size = sround(self.domain_size + 0.2 * level)
        self.n_modes = sround(self.n_modes + 0.45 * level)
        self.n_predicates = sround(self.n_predicates + 0.5 * level)
        self.formula_depth = sround(self.formula_depth + 0.55 * level)
        self.branchiness = sround(self.branchiness + 0.25 * level)
        self.max_states = sround(self.max_states + 20 * level)
        self.min_witness_len = sround(self.min_witness_len + 0.25 * level)


PHASE_NAMES = ("idle", "wait", "done", "fail", "check", "hold", "retry", "exit")


def _state_name(i):
    return f"s{i}"


def _formula(op, *args):
    return (op,) + args


def _depth(f):
    if f[0] == "atom":
        return 1
    if f[0] in ("!", "EX", "AX", "EF", "AF", "EG", "AG"):
        return 1 + _depth(f[1])
    return 1 + max(_depth(f[1]), _depth(f[2]))


class CodeAnalysis(Task):
    summary = "Analyze toy finite-state Python-like programs with CTL temporal formulas."
    config_cls = CodeAnalysisConfig

    def __init__(self, config=None):
        super().__init__(config=config)
        self._query_i = 0
        self.balancing_key_ratio = 0.35

    def generate_entry(self):
        cfg = self.config
        modes = ("holds", "states", "rank", "witness")
        start = self._query_i % len(modes)
        self._query_i += 1

        for query_type in modes[start:] + modes[:start]:
            for _ in range(max(1, cfg.max_retries // len(modes))):
                kripke = self._make_kripke()
                predicates = self._make_predicates(kripke)
                formula = self._make_formula_for_query(query_type, kripke, predicates)
                solved = self._solve_query(query_type, formula, kripke, predicates)
                if solved is None:
                    continue
                answer, metrics = solved
                if self._accept(query_type, answer, metrics, kripke):
                    metadata = self._metadata(query_type, formula, kripke, predicates, metrics)
                    return Entry(metadata=metadata, answer=answer)

        raise RuntimeError(f"Failed to generate code_analysis task. Config: {cfg}")

    def render_prompt(self, m):
        parts = [
            "Program:",
            "```python",
            m.program,
            "```",
            "",
            "Reachable states:",
            m.state_table,
            "",
            "Predicates:",
            m.predicates,
            "",
            "Property:",
            m.property_text,
            "",
        ]
        if m.query_type == "holds":
            parts.append("Question: Considering all possible random choices, does the property hold from the initial state?")
            parts.append("Answer with exactly Yes or No.")
        elif m.query_type == "states":
            parts.append("Question: List all reachable states where the property holds.")
            parts.append("Answer as a sorted set like {s0,s2}.")
        elif m.query_type == "rank":
            parts.append(
                "Question: At which fixed-point iteration does the initial state first enter the satisfying set?"
            )
            parts.append("Iteration 0 is the states where the inner condition already holds.")
            parts.append("Answer with a nonnegative integer, or never.")
        else:
            if m.witness_kind == "counterexample":
                parts.append(
                    "Question: Give the shortest path with the smallest state indexes showing that the property fails from the initial state."
                )
            else:
                parts.append(
                    "Question: Give the shortest path with the smallest state indexes reaching a state where the property holds."
                )
            parts.append("Answer as comma-separated state names, like s0,s2,s5.")
        return "\n".join(parts)

    def score_answer(self, answer, entry):
        metadata = entry["metadata"] if isinstance(entry, dict) else entry.metadata
        q = metadata["query_type"]
        ref = entry["answer"] if isinstance(entry, dict) else entry.answer
        if q == "holds":
            return float(_norm_yesno(answer) == ref)
        if q == "states":
            return float(_parse_state_set(answer) == _parse_state_set(ref))
        if q == "rank":
            return float(str(answer).strip().lower().rstrip(".") == ref)
        if q == "witness":
            return float(_parse_path(answer) == _parse_path(ref))
        return 0.0

    def balancing_key(self, problem):
        m = problem.metadata
        if m.query_type == "holds":
            return f"holds:{problem.answer}"
        return f"{m.query_type}:{m.difficulty_bucket}"

    def deduplication_key(self, problem):
        m = problem.metadata
        raw = "|".join([m.query_type, m.formula, m.program])
        return hashlib.sha1(raw.encode()).hexdigest()

    def _make_kripke(self):
        cfg = self.config
        n_modes = max(2, min(int(cfg.n_modes), len(PHASE_NAMES)))
        vars_ = [("phase", PHASE_NAMES[:n_modes])]
        if cfg.n_vars >= 2:
            vars_.append(("x", tuple(map(str, range(max(2, int(cfg.domain_size)))))))
        if cfg.n_vars >= 3:
            vars_.append(("flag", ("False", "True")))
        if cfg.n_vars >= 4:
            vars_.append(("y", tuple(map(str, range(2 + min(2, int(cfg.domain_size) // 2))))))

        while _domain_size(vars_) > cfg.max_states and len(vars_) > 2:
            vars_.pop()
        states = list(product(*[range(len(domain)) for _, domain in vars_]))
        index = {state: i for i, state in enumerate(states)}
        program = self._make_program(vars_)
        succ = []
        for state in states:
            choices = [index[s] for s in self._program_successors(program, vars_, state)]
            succ.append(sorted(set(choices)) or [index[state]])

        reachable = _reachable(succ, 0)
        return edict(vars=vars_, states=states, succ=succ, initial=0, reachable=reachable, program=program)

    def _make_program(self, vars_):
        domains = dict(vars_)
        phases = domains["phase"]
        available = ["workflow", "cooldown"]
        if "fail" in phases:
            available += ["retry_fail", "alarm"]
        if "flag" in domains:
            available += ["lock", "coupled_flag"]
        if "y" in domains:
            available += ["buffer"]
        motif = random.choice(available)
        actions = ["advance"]
        if "fail" in phases and random.random() < 0.75:
            actions.append("fail")
        if "x" in domains:
            actions.append("reset")
        if "flag" in domains:
            actions.append("toggle")
        return edict(
            motif=motif,
            idle_can_wait=random.random() < 0.85,
            wait_actions=actions[: max(1, min(len(actions), int(self.config.branchiness) + 1))],
            done_on_max="done" in phases,
            fail_sticky=random.random() < 0.75,
        )

    def _program_successors(self, program, vars_, state):
        domains = dict(vars_)
        values = _state_values(vars_, state)
        phase = values["phase"]
        if program.motif == "cooldown":
            nxt = dict(values)
            if phase == "idle":
                nxt["phase"] = "wait"
            elif phase == "wait" and "x" in nxt:
                x_max = len(domains["x"]) - 1
                nxt["x"] = str(min(int(nxt["x"]) + 1, x_max))
                if int(nxt["x"]) == x_max and "done" in domains["phase"]:
                    nxt["phase"] = "done"
            elif phase == "done":
                nxt["phase"] = "idle"
                if "x" in nxt:
                    nxt["x"] = "0"
            else:
                nxt["phase"] = "idle"
            return [_state_from_values(vars_, nxt)]
        if program.motif == "retry_fail":
            if phase == "idle":
                return [_state_from_values(vars_, {**values, "phase": "wait"})]
            if phase == "wait":
                out = []
                for target in ("wait", "fail"):
                    nxt = dict(values)
                    nxt["phase"] = target
                    if target == "wait" and "x" in nxt:
                        x_max = len(domains["x"]) - 1
                        nxt["x"] = str(min(int(nxt["x"]) + 1, x_max))
                    out.append(_state_from_values(vars_, nxt))
                return out
            if phase == "fail":
                if program.fail_sticky:
                    return [state]
                return [_state_from_values(vars_, {**values, "phase": "idle"})]
            return [_state_from_values(vars_, {**values, "phase": "idle"})]
        if program.motif == "lock" and "flag" in values:
            if phase == "idle":
                return [_state_from_values(vars_, {**values, "phase": "wait", "flag": "True"})]
            if phase == "wait":
                target = "done" if "done" in domains["phase"] else "idle"
                return [
                    _state_from_values(vars_, {**values, "phase": target}),
                    _state_from_values(vars_, {**values, "flag": "False"}),
                ]
            if phase == "done":
                return [_state_from_values(vars_, {**values, "phase": "idle", "flag": "False"})]
            return [_state_from_values(vars_, {**values, "phase": "idle"})]
        if program.motif == "buffer" and "y" in values:
            y_max = len(domains["y"]) - 1
            out = []
            for delta in (1, -1):
                nxt = dict(values)
                nxt["y"] = str(max(0, min(int(nxt["y"]) + delta, y_max)))
                if int(nxt["y"]) == y_max and "done" in domains["phase"]:
                    nxt["phase"] = "done"
                out.append(_state_from_values(vars_, nxt))
            return out
        if program.motif == "alarm":
            if phase == "idle":
                return [_state_from_values(vars_, {**values, "phase": "wait"})]
            if phase == "wait":
                return [
                    _state_from_values(vars_, {**values, "phase": "idle"}),
                    _state_from_values(vars_, {**values, "phase": "fail"}),
                ]
            if phase == "fail":
                if program.fail_sticky:
                    return [state]
                return [_state_from_values(vars_, {**values, "phase": "idle"})]
            return [_state_from_values(vars_, {**values, "phase": "idle"})]
        if program.motif == "coupled_flag" and "flag" in values:
            nxt = dict(values)
            if phase == "idle":
                nxt["phase"] = "wait"
            elif phase == "wait":
                nxt["flag"] = "False" if nxt["flag"] == "True" else "True"
                if nxt["flag"] == "False" and "done" in domains["phase"]:
                    nxt["phase"] = "done"
            elif phase == "done":
                nxt["phase"] = "idle"
            else:
                nxt["phase"] = "idle"
            return [_state_from_values(vars_, nxt)]
        if phase == "idle":
            targets = ["idle", "wait"] if program.idle_can_wait else ["wait"]
            return [_state_from_values(vars_, {**values, "phase": target}) for target in targets]
        if phase == "wait":
            out = []
            for action in program.wait_actions:
                nxt = dict(values)
                if action == "advance" and "x" in nxt:
                    x_max = len(dict(vars_)["x"]) - 1
                    nxt["x"] = str(min(int(nxt["x"]) + 1, x_max))
                    if program.done_on_max and int(nxt["x"]) == x_max:
                        nxt["phase"] = "done"
                elif action == "reset":
                    nxt["phase"] = "idle"
                    if "x" in nxt:
                        nxt["x"] = "0"
                elif action == "fail":
                    nxt["phase"] = "fail"
                elif action == "toggle":
                    nxt["flag"] = "False" if nxt["flag"] == "True" else "True"
                out.append(_state_from_values(vars_, nxt))
            return out
        if phase == "done":
            nxt = {**values, "phase": "idle"}
            if "x" in nxt:
                nxt["x"] = "0"
            return [_state_from_values(vars_, nxt)]
        if phase == "fail":
            if program.fail_sticky:
                return [state]
            return [_state_from_values(vars_, {**values, "phase": "idle"})]
        return [_state_from_values(vars_, {**values, "phase": "idle"})]

    def _make_predicates(self, k):
        candidates = []
        for vi, (name, domain) in enumerate(k.vars):
            for value_i, value in enumerate(domain):
                sat = {sid for sid, state in enumerate(k.states) if state[vi] == value_i}
                expr = f"{name} == {value!r}" if name == "phase" else f"{name} == {value}"
                candidates.append((expr, sat))
            if name != "phase" and all(v.isdigit() for v in domain) and len(domain) > 2:
                hi = len(domain) - 1
                sat = {sid for sid, state in enumerate(k.states) if state[vi] < hi}
                candidates.append((f"{name} < {domain[hi]}", sat))
        random.shuffle(candidates)
        preds = []
        seen = set()
        for expr, sat in candidates:
            key = tuple(sorted(sat))
            if key in seen or len(sat) in (0, len(k.states)):
                continue
            seen.add(key)
            preds.append((f"p{len(preds)}", expr, sat))
            if len(preds) >= self.config.n_predicates:
                break
        return preds

    def _make_formula_for_query(self, query_type, k, preds):
        if query_type == "rank":
            inner = self._random_formula(k, preds, max(1, self.config.formula_depth - 1), temporal=False)
            return _formula(random.choice(("EF", "AF")), inner)
        if query_type == "witness":
            inner = self._random_formula(k, preds, max(1, self.config.formula_depth - 1), temporal=False)
            return _formula(random.choice(("EF", "AG")), inner)
        return self._random_formula(k, preds, max(1, self.config.formula_depth), temporal=True)

    def _random_formula(self, k, preds, depth, temporal=True):
        if depth <= 1 or random.random() < 0.25:
            return _formula("atom", random.choice(preds)[0])
        if temporal and random.random() < 0.55:
            return _formula(random.choice(("EX", "AX", "EF", "AF", "EG", "AG")), self._random_formula(k, preds, depth - 1))
        if random.random() < 0.2:
            return _formula("!", self._random_formula(k, preds, depth - 1, temporal))
        return _formula(
            random.choice(("&", "|", "->")),
            self._random_formula(k, preds, depth - 1, temporal),
            self._random_formula(k, preds, depth - 1, temporal),
        )

    def _solve_query(self, query_type, formula, k, preds):
        pred_map = {name: sat for name, _, sat in preds}
        sat, fp_iters = self._sat(formula, k.succ, pred_map)
        reachable_sat = sat & k.reachable
        if query_type == "holds":
            return ("Yes" if k.initial in sat else "No"), self._metrics(k, formula, reachable_sat, fp_iters)
        if query_type == "states":
            answer = "{" + ",".join(_state_name(i) for i in sorted(reachable_sat)) + "}"
            return answer, self._metrics(k, formula, reachable_sat, fp_iters)
        if query_type == "rank":
            rank = self._entry_rank(formula, k.succ, pred_map, k.initial)
            answer = "never" if rank is None else str(rank)
            metrics = self._metrics(k, formula, reachable_sat, fp_iters)
            metrics.fp_iterations = -1 if rank is None else rank
            return answer, metrics
        path = self._witness_path(formula, k, pred_map)
        if path is None:
            return None
        metrics = self._metrics(k, formula, reachable_sat, fp_iters)
        metrics.shortest_witness_len = len(path) - 1
        return ",".join(_state_name(i) for i in path), metrics

    def _sat(self, f, succ, preds):
        n = len(succ)
        all_states = set(range(n))
        op = f[0]
        if op == "atom":
            return set(preds[f[1]]), 0
        if op == "!":
            s, it = self._sat(f[1], succ, preds)
            return all_states - s, it
        if op in ("&", "|", "->"):
            a, ia = self._sat(f[1], succ, preds)
            b, ib = self._sat(f[2], succ, preds)
            if op == "&":
                return a & b, max(ia, ib)
            if op == "|":
                return a | b, max(ia, ib)
            return (all_states - a) | b, max(ia, ib)

        inner, inner_i = self._sat(f[1], succ, preds)
        if op == "EX":
            return {i for i, ss in enumerate(succ) if any(j in inner for j in ss)}, inner_i
        if op == "AX":
            return {i for i, ss in enumerate(succ) if all(j in inner for j in ss)}, inner_i
        if op == "EF":
            return _least_fixed_point(inner, succ, existential=True, base=inner_i)
        if op == "AF":
            return _least_fixed_point(inner, succ, existential=False, base=inner_i)
        if op == "EG":
            return _greatest_fixed_point(inner, succ, existential=True, base=inner_i)
        if op == "AG":
            return _greatest_fixed_point(inner, succ, existential=False, base=inner_i)
        raise ValueError(op)

    def _entry_rank(self, formula, succ, preds, init):
        op = formula[0]
        if op not in ("EF", "AF"):
            return None
        inner, _ = self._sat(formula[1], succ, preds)
        current = set(inner)
        if init in current:
            return 0
        for iteration in range(1, len(succ) + 1):
            if op == "EF":
                add = {i for i, ss in enumerate(succ) if any(j in current for j in ss)}
            else:
                add = {i for i, ss in enumerate(succ) if all(j in current for j in ss)}
            new = current | add
            if init in new:
                return iteration
            if new == current:
                return None
            current = new
        return None

    def _witness_path(self, formula, k, preds):
        op = formula[0]
        if op == "EF":
            target, _ = self._sat(formula[1], k.succ, preds)
        elif op == "AG":
            good, _ = self._sat(formula[1], k.succ, preds)
            target = set(range(len(k.states))) - good
        else:
            return None
        return _shortest_lex_path(k.succ, k.initial, target)

    def _metrics(self, k, formula, sat, fp_iters):
        reachable = k.reachable
        branch_counts = [len(k.succ[i]) for i in reachable]
        sat_fraction = len(sat) / max(1, len(k.reachable))
        return edict(
            n_states=len(k.states),
            n_edges=sum(len(s) for s in k.succ),
            reachable_states=len(reachable),
            formula_depth=_depth(formula),
            temporal_depth=_temporal_depth(formula),
            fp_iterations=fp_iters,
            shortest_witness_len=0,
            sat_count=len(sat),
            sat_fraction=round(sat_fraction, 3),
            branching_entropy=round(sum(branch_counts) / max(1, len(branch_counts)), 3),
        )

    def _accept(self, query_type, answer, metrics, k):
        if metrics.reachable_states < min(3, metrics.n_states):
            return False
        if query_type == "states" and metrics.sat_count in (0, metrics.reachable_states):
            return False
        if query_type == "states" and metrics.temporal_depth == 0:
            return random.random() < 0.2
        if query_type == "rank":
            if answer == "never":
                return random.random() < 0.25
            return int(answer) >= max(1, int(self.config.min_witness_len) - 1)
        if query_type == "witness":
            return metrics.shortest_witness_len >= max(1, int(self.config.min_witness_len))
        if query_type == "holds":
            return metrics.temporal_depth > 0 and 0 < metrics.sat_count < metrics.reachable_states
        return True

    def _metadata(self, query_type, formula, k, preds, metrics):
        formula_text = self._render_formula(formula)
        state_table = "; ".join(
            f"{_state_name(i)}=({', '.join(f'{name}={k.vars[j][1][state[j]]}' for j, (name, _) in enumerate(k.vars))})"
            for i, state in enumerate(k.states)
            if i in k.reachable
        )
        pred_text = "\n".join(f"{name} := {expr}" for name, expr, _ in preds)
        program = self._render_program(k)
        compile(program, "<code_analysis_program>", "exec")
        bucket = f"d{metrics.formula_depth}:s{metrics.n_states}:t{metrics.temporal_depth}"
        return edict(
            program=program,
            predicates=pred_text,
            formula=formula_text,
            property_text=self._render_property(formula),
            query_type=query_type,
            witness_kind="counterexample" if query_type == "witness" and formula[0] == "AG" else "witness",
            initial_state=_state_name(k.initial),
            state_table=state_table,
            answer_format=query_type,
            motif=k.program.motif,
            difficulty_bucket=bucket,
            n_states=metrics.n_states,
            n_edges=metrics.n_edges,
            reachable_states=metrics.reachable_states,
            formula_depth=metrics.formula_depth,
            temporal_depth=metrics.temporal_depth,
            fp_iterations=metrics.fp_iterations,
            shortest_witness_len=metrics.shortest_witness_len,
            sat_count=metrics.sat_count,
            sat_fraction=metrics.sat_fraction,
            branching_entropy=metrics.branching_entropy,
        )

    def _render_program(self, k):
        lines = ["import random", ""]
        names = ", ".join(name for name, _ in k.vars)
        lhs = names
        init_values = ", ".join(
            _literal(domain[k.states[k.initial][i]])
            for i, (_, domain) in enumerate(k.vars)
        )
        lines.append(f"{lhs} = {init_values}")
        lines.append("")
        lines.append("def step():")
        lines.append(f"    global {names}")
        domains = dict(k.vars)
        phases = domains["phase"]
        if k.program.motif == "cooldown":
            lines.append("    if phase == 'idle':")
            lines.append("        phase = 'wait'")
            lines.append("    elif phase == 'wait':")
            if "x" in domains:
                x_max = len(domains["x"]) - 1
                lines.append(f"        x = min(x + 1, {x_max})")
                if "done" in phases:
                    lines.append(f"        if x == {x_max}:")
                    lines.append("            phase = 'done'")
            else:
                lines.append("        phase = 'wait'")
            if "done" in phases:
                lines.append("    elif phase == 'done':")
                lines.append("        phase, x = 'idle', 0" if "x" in domains else "        phase = 'idle'")
            lines.append("    else:")
            lines.append("        phase = 'idle'")
            return "\n".join(lines)
        if k.program.motif == "retry_fail":
            lines.append("    if phase == 'idle':")
            lines.append("        phase = 'wait'")
            lines.append("    elif phase == 'wait':")
            lines.append("        if random.choice([True, False]):")
            if "x" in domains:
                lines.append(f"            x = min(x + 1, {len(domains['x']) - 1})")
            else:
                lines.append("            phase = 'wait'")
            lines.append("        else:")
            lines.append("            phase = 'fail'")
            lines.append("    elif phase == 'fail':")
            lines.append("        phase = 'fail'" if k.program.fail_sticky else "        phase = 'idle'")
            lines.append("    else:")
            lines.append("        phase = 'idle'")
            return "\n".join(lines)
        if k.program.motif == "lock":
            target = "done" if "done" in phases else "idle"
            lines.append("    if phase == 'idle':")
            lines.append("        phase, flag = 'wait', True")
            lines.append("    elif phase == 'wait':")
            lines.append("        if random.choice([True, False]):")
            lines.append(f"            phase = {target!r}")
            lines.append("        else:")
            lines.append("            flag = False")
            if "done" in phases:
                lines.append("    elif phase == 'done':")
                lines.append("        phase, flag = 'idle', False")
            lines.append("    else:")
            lines.append("        phase = 'idle'")
            return "\n".join(lines)
        if k.program.motif == "buffer":
            y_max = len(domains["y"]) - 1
            lines.append("    if random.choice([True, False]):")
            lines.append(f"        y = min(y + 1, {y_max})")
            lines.append("    else:")
            lines.append("        y = max(y - 1, 0)")
            if "done" in phases:
                lines.append(f"    if y == {y_max}:")
                lines.append("        phase = 'done'")
            return "\n".join(lines)
        if k.program.motif == "alarm":
            lines.append("    if phase == 'idle':")
            lines.append("        phase = 'wait'")
            lines.append("    elif phase == 'wait':")
            lines.append("        phase = random.choice(['idle', 'fail'])")
            lines.append("    elif phase == 'fail':")
            lines.append("        phase = 'fail'" if k.program.fail_sticky else "        phase = 'idle'")
            lines.append("    else:")
            lines.append("        phase = 'idle'")
            return "\n".join(lines)
        if k.program.motif == "coupled_flag":
            lines.append("    if phase == 'idle':")
            lines.append("        phase = 'wait'")
            lines.append("    elif phase == 'wait':")
            lines.append("        flag = not flag")
            if "done" in phases:
                lines.append("        if not flag:")
                lines.append("            phase = 'done'")
                lines.append("    elif phase == 'done':")
                lines.append("        phase = 'idle'")
            lines.append("    else:")
            lines.append("        phase = 'idle'")
            return "\n".join(lines)
        lines.append("    if phase == 'idle':")
        if k.program.idle_can_wait:
            lines.append("        phase = random.choice(['idle', 'wait'])")
        else:
            lines.append("        phase = 'wait'")
        lines.append("    elif phase == 'wait':")
        if len(k.program.wait_actions) == 1:
            lines.append(f"        action = {k.program.wait_actions[0]!r}")
        else:
            lines.append(f"        action = random.choice({list(k.program.wait_actions)!r})")
        if "x" in domains:
            x_max = len(domains["x"]) - 1
            lines.append("        if action == 'advance':")
            lines.append(f"            x = min(x + 1, {x_max})")
            if k.program.done_on_max:
                lines.append(f"            if x == {x_max}:")
                lines.append("                phase = 'done'")
        else:
            lines.append("        if action == 'advance':")
            lines.append("            phase = 'wait'")
        if "reset" in k.program.wait_actions:
            lines.append("        elif action == 'reset':")
            if "x" in domains:
                lines.append("            phase, x = 'idle', 0")
            else:
                lines.append("            phase = 'idle'")
        if "fail" in k.program.wait_actions:
            lines.append("        elif action == 'fail':")
            lines.append("            phase = 'fail'")
        if "toggle" in k.program.wait_actions:
            lines.append("        elif action == 'toggle':")
            lines.append("            flag = not flag")
        if "done" in phases:
            lines.append("    elif phase == 'done':")
            if "x" in domains:
                lines.append("        phase, x = 'idle', 0")
            else:
                lines.append("        phase = 'idle'")
        if "fail" in phases:
            lines.append("    elif phase == 'fail':")
            if k.program.fail_sticky:
                lines.append("        phase = 'fail'")
            else:
                lines.append("        phase = 'idle'")
        lines.append("    else:")
        lines.append("        phase = 'idle'")
        return "\n".join(lines)

    def _render_formula(self, f):
        op = f[0]
        if op == "atom":
            return f[1]
        if op == "!":
            return f"!({self._render_formula(f[1])})"
        if op in ("EX", "AX", "EF", "AF", "EG", "AG"):
            return f"{op}({self._render_formula(f[1])})"
        return f"({self._render_formula(f[1])} {op} {self._render_formula(f[2])})"

    def _render_property(self, f):
        op = f[0]
        if op == "atom":
            return f[1]
        if op == "!":
            return f"not ({self._render_property(f[1])})"
        if op == "&":
            return f"({self._render_property(f[1])}) and ({self._render_property(f[2])})"
        if op == "|":
            return f"({self._render_property(f[1])}) or ({self._render_property(f[2])})"
        if op == "->":
            return f"if {self._render_property(f[1])}, then {self._render_property(f[2])}"
        if op == "EX":
            return f"some next step can reach a state where {self._render_property(f[1])}"
        if op == "AX":
            return f"every next step reaches a state where {self._render_property(f[1])}"
        if op == "EF":
            return f"some execution can eventually reach a state where {self._render_property(f[1])}"
        if op == "AF":
            return f"every execution eventually reaches a state where {self._render_property(f[1])}"
        if op == "EG":
            return f"from the current state, there is some infinite execution where {self._render_property(f[1])} remains true forever"
        if op == "AG":
            return f"from the current state, {self._render_property(f[1])} holds now and after every possible sequence of steps"
        return self._render_formula(f)


def _domain_size(vars_):
    size = 1
    for _, domain in vars_:
        size *= len(domain)
    return size


def _literal(value):
    if value in ("True", "False") or value.isdigit():
        return value
    return repr(value)


def _state_values(vars_, state):
    return {name: domain[state[i]] for i, (name, domain) in enumerate(vars_)}


def _state_from_values(vars_, values):
    return tuple(domain.index(str(values[name])) for name, domain in vars_)


def _least_fixed_point(base_set, succ, existential, base=0):
    current = set(base_set)
    for iteration in range(1, len(succ) + 1):
        if existential:
            add = {i for i, ss in enumerate(succ) if any(j in current for j in ss)}
        else:
            add = {i for i, ss in enumerate(succ) if all(j in current for j in ss)}
        new = current | add
        if new == current:
            return current, base + iteration - 1
        current = new
    return current, base + len(succ)


def _greatest_fixed_point(base_set, succ, existential, base=0):
    current = set(base_set)
    for iteration in range(1, len(succ) + 1):
        if existential:
            new = {i for i in current if any(j in current for j in succ[i])}
        else:
            new = {i for i in current if all(j in current for j in succ[i])}
        if new == current:
            return current, base + iteration - 1
        current = new
    return current, base + len(succ)


def _reachable(succ, start):
    seen = {start}
    q = deque([start])
    while q:
        i = q.popleft()
        for j in succ[i]:
            if j not in seen:
                seen.add(j)
                q.append(j)
    return seen


def _shortest_lex_path(succ, start, targets):
    if start in targets:
        return [start]
    q = deque([(start, [start])])
    seen = {start}
    while q:
        node, path = q.popleft()
        for nxt in sorted(succ[node]):
            if nxt in seen:
                continue
            npath = path + [nxt]
            if nxt in targets:
                return npath
            seen.add(nxt)
            q.append((nxt, npath))
    return None


def _temporal_depth(f):
    if f[0] == "atom":
        return 0
    if f[0] in ("EX", "AX", "EF", "AF", "EG", "AG"):
        return 1 + _temporal_depth(f[1])
    if f[0] == "!":
        return _temporal_depth(f[1])
    return max(_temporal_depth(f[1]), _temporal_depth(f[2]))


def _norm_yesno(answer):
    text = str(answer).strip().lower().rstrip(".")
    if text in {"yes", "y", "true"}:
        return "Yes"
    if text in {"no", "n", "false"}:
        return "No"
    return text


def _parse_state_set(answer):
    text = str(answer).strip()
    sets = re.findall(r"\{[^{}]*\}", text)
    if sets:
        text = sets[-1]
    else:
        text = text.splitlines()[-1] if text else ""
    if text in {"{}", "set()", ""}:
        return set()
    return set(re.findall(r"\bs\d+\b", text))


def _parse_path(answer):
    text = str(answer).strip()
    text = text.splitlines()[-1] if text else ""
    return re.findall(r"\bs\d+\b", text)
