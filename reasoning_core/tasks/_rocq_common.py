import os
import re
import tempfile

from reasoning_core.utils import udocker_process


ROCQ_IMAGE = "rocq/rocq-prover:9.2"
ROCQ_BINARY = "/home/rocq/.opam/4.14.2+flambda/bin/rocq"


def run_rocq(code, timeout=10):
    with tempfile.NamedTemporaryFile("w", suffix=".v", delete=False) as f:
        f.write(code)
        path = f.name
    try:
        sess = udocker_process.get_prover_session(docker_image=ROCQ_IMAGE)
        return sess.run_prover(ROCQ_BINARY, ["compile", "-q"], path, timeout=timeout)
    finally:
        os.remove(path)


def certify(code, timeout=10):
    try:
        res = run_rocq(code, timeout=timeout)
    except Exception as e:
        return False, "", str(e)
    return res.returncode == 0, res.stdout, res.stderr


def check_rocq(code, timeout=10):
    """Compile a Rocq source string."""
    return certify(code, timeout=timeout)


def eval_rocq(expr_source, target_name="target", timeout=10):
    """Evaluate a target definition with Rocq and return its printed value."""
    ok, out, err = check_rocq(
        f"{expr_source.rstrip()}\n\nEval vm_compute in {target_name}.\n",
        timeout=timeout,
    )
    if not ok:
        raise RuntimeError(err)
    m = re.search(r"=\s*(.*?)\n\s*:", out, re.S)
    if not m:
        raise RuntimeError(f"could not parse Rocq Eval output: {out!r}")
    return " ".join(m.group(1).split())


def candidate_labels(header, candidates, timeout=10):
    """Check each proof body against one theorem header."""
    labels = []
    for cand in candidates:
        ok, _, _ = check_rocq(f"{header.rstrip()}\nProof.\n  {cand}\nQed.\n", timeout=timeout)
        labels.append(bool(ok))
    return labels
