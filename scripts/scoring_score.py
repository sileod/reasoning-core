"""
Scoring-only core for HumanEval / CRUXEval, kept separate from model
generation so it can be unit-tested without a model or GPU.

Deliberately reuses the SAME sandboxed run_code() the rest of the
reasoning-core pipeline already trusts (forked subprocess, CPU/AS rlimits,
timeout) instead of the unsandboxed HF `evaluate` code_eval metric, which
the HF docs themselves warn requires HF_ALLOW_CODE_EVAL=1 and runs largely
unguarded in-process. Model-generated code from an under-trained checkpoint
is exactly the kind of untrusted input that sandbox was built for.
"""
import ast
import math
import re

from reasoning_core.tasks.code_execution import run_code


_FENCE_RE = re.compile(r"^```(?:python)?\s*\n(.*?)\n?```$", re.DOTALL)


def strip_code_fence(text: str) -> str:
    """Unwrap a ```...``` fence if present. Does NOT strip() the unfenced
    case: HumanEval completions are appended directly after a function
    signature and must keep their leading indentation, or every correct
    completion will register as a syntax error."""
    m = _FENCE_RE.match(text.strip())
    return m.group(1) if m else text


def entry_point_name(code: str) -> str:
    """Dynamically find the function under test instead of assuming a
    fixed name like `f` — robust if a benchmark's schema or naming changes."""
    tree = ast.parse(code)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            return node.name
    raise ValueError("no top-level function definition found in code")


def values_equal(a_text: str, b_text: str) -> bool:
    """Compare via literal_eval when possible (so '7' == ' 7 ' == 7), else
    fall back to normalised string equality."""
    def parse(x):
        try:
            return ast.literal_eval(x.strip())
        except Exception:
            return x.strip()
    return parse(a_text) == parse(b_text)


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased pass@k estimator from the Codex/HumanEval paper:
    1 - C(n-c, k) / C(n, k), computed via the equivalent running product to
    avoid large-factorial overflow."""
    if n - c < k:
        return 1.0
    return 1.0 - math.prod((n - c - i) / (n - i) for i in range(k))


def score_humaneval_completion(prompt: str, completion: str, test: str, entry_point: str, timeout: float) -> bool:
    """HumanEval grading: prompt + completion must define entry_point such
    that check(entry_point) (the benchmark's own assertions) raises nothing."""
    completion = strip_code_fence(completion)
    program = f"{prompt}{completion}\n{test}\ncheck({entry_point})\n"
    r = run_code(program, timeout=timeout, exec_only=True)
    return bool(r.ok)


def score_cruxeval_output(predicted_text: str, true_output: str) -> bool:
    """CRUXEval-O grading: model predicted the return value directly, no
    execution needed to check it (the dataset already gives the true value)."""
    return values_equal(strip_code_fence(predicted_text), true_output)


def score_cruxeval_input(code: str, predicted_call_text: str, true_output: str, timeout: float) -> bool:
    """CRUXEval-I grading: model predicts a full call expression, e.g.
    `f([1, 1, 3])`. Graded by FUNCTIONAL EQUIVALENCE (does the call actually
    reproduce true_output), not by string-matching the original input —
    many different inputs can map to the same output, and CRUXEval's own
    grading accepts any of them. We execute the candidate against the real
    function rather than trust the model's claim."""
    answer = strip_code_fence(predicted_call_text).strip()
    program = f"{code}\nresult = {answer}\nprint(repr(result))\n"
    r = run_code(program, timeout=timeout, exec_only=True)
    if not r.ok:
        return False
    return values_equal(r.stdout.strip(), true_output)