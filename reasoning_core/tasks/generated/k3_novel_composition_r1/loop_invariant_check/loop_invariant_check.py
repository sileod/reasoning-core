import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class LoopInvariantCheckConfig(Config):
    num_vars: int = 2
    bound: int = 8
    max_retries: int = 600

    def apply_difficulty(self, level):
        self.num_vars = 2 + level // 2
        self.bound = 4 + level
        self.max_retries = 600


TASK_META = {'parent_source_id': None,
 'idea': 'loop_invariant_check (draw 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_novel_composition_r1/loop_invariant_check',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}


def _affine_str(coeffs, const):
    terms = []
    for i, c in enumerate(coeffs):
        if c == 0:
            continue
        if c == 1:
            terms.append(f"x{i}")
        elif c == -1:
            terms.append(f"-x{i}")
        else:
            terms.append(f"{c}*x{i}")
    if const != 0 or not terms:
        terms.append(str(const))
    s = "+".join(terms)
    return s.replace("+-", "-")


def _eval(coeffs, const, vals):
    return const + sum(c * v for c, v in zip(coeffs, vals))


def _holds(coeffs, const, kind, vals):
    v = _eval(coeffs, const, vals)
    return v == 0 if kind == "eq" else v <= 0


def _render_constraint(coeffs, const, kind):
    return f"{_affine_str(coeffs, const)} == 0" if kind == "eq" else f"{_affine_str(coeffs, const)} <= 0"


class LoopInvariantCheck(Task):
    summary = "Verify whether a candidate loop invariant is inductive and implies the postcondition for a while loop with linear arithmetic; ranges over invariant strength, loop complexity, and counterexample types; answer is valid or a violating state."
    design_choice = "Generate loops where the invariant is inductive but too weak, requiring a counterexample state that satisfies the invariant and loop condition yet violates the postcondition."
    config_cls = LoopInvariantCheckConfig

    def _rand_coeffs(self, n):
        coeffs = [random.randint(-2, 2) for _ in range(n)]
        if all(c == 0 for c in coeffs):
            coeffs[random.randrange(n)] = 1
        return coeffs

    def _gen_constraint(self, n, induct=False):
        while True:
            coeffs = self._rand_coeffs(n)
            kind = random.choice(["eq", "le"])
            s = sum(coeffs)
            if induct:
                if kind == "eq" and s != 0:
                    continue
                if kind == "le" and s > 0:
                    continue
            const = 0 if (induct and kind == "eq") else random.randint(-self.config.bound, self.config.bound)
            return coeffs, const, kind

    def _find_witness(self, inv, cond, post, n):
        for _ in range(self.config.max_retries):
            vals = tuple(random.randint(-2 * self.config.bound, 2 * self.config.bound) for _ in range(n))
            if _holds(*inv, vals) and _holds(*cond, vals) and not _holds(*post, vals):
                return vals
        return None

    def generate_entry(self):
        n = self.config.num_vars
        while True:
            cond = self._gen_constraint(n)
            inv = self._gen_constraint(n, induct=True)
            post = self._gen_constraint(n)

            init = tuple(random.randint(0, 3) for _ in range(n))
            if not _holds(*inv, init):
                continue

            witness = self._find_witness(inv, cond, post, n)
            if witness is None:
                continue
            if _holds(*inv, witness) and _holds(*cond, witness) and _holds(*post, witness):
                continue
            answer = ";".join(str(v) for v in witness)
            break

        metadata = {
            "num_vars": n,
            "init": init,
            "cond_coeffs": cond[0], "cond_const": cond[1], "cond_kind": cond[2],
            "inv_coeffs": inv[0], "inv_const": inv[1], "inv_kind": inv[2],
            "post_coeffs": post[0], "post_const": post[1], "post_kind": post[2],
            "witness": witness,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        n = metadata["num_vars"]
        invars = ", ".join(f"x{i}" for i in range(n))
        init_str = ", ".join(str(metadata["init"][i]) for i in range(n))
        cond_repr = _render_constraint(metadata["cond_coeffs"], metadata["cond_const"], metadata["cond_kind"])
        inv_repr = _render_constraint(metadata["inv_coeffs"], metadata["inv_const"], metadata["inv_kind"])
        post_repr = _render_constraint(metadata["post_coeffs"], metadata["post_const"], metadata["post_kind"])
        return (
            f"A while loop over state variables {{{invars}}}, initialized to ({init_str}). "
            f"Each iteration updates every x_i to x_i + 1. The loop continues while {cond_repr}.\n\n"
            f"Candidate loop invariant: {inv_repr}.\n"
            f"Postcondition: {post_repr}.\n\n"
            f"Is the candidate invariant inductive (true initially and preserved by each iteration) and, together "
            f"with the loop condition, does it imply the postcondition? Answer exactly 'valid' if yes, or give one "
            f"violating state as comma-separated {invars} values that satisfies the invariant and the loop condition "
            f"but violates the postcondition."
        )

    def score_answer(self, answer, entry):
        a = answer.strip()
        return 1.0 if a == entry.answer else 0.0
