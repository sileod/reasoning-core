import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, DevTask, Problem, Task, edict, stochastic_rounding as sround
from reasoning_core.tasks._rocq_common import ROCQ_IMAGE, check_rocq, eval_rocq


BANNED_ROCQ_TOKENS = (
    "admit", "admitted", "axiom", "parameter", "variable", "definition",
    "theorem", "lemma", "fixpoint", "cofixpoint", "ltac", "module",
    "require", "load", "declare", "qed", "defined", "save", "abort",
    "fail", "timeout", "redirect", "extraction",
)


def _safe(text):
    low = str(text).lower()
    return not any(tok in low for tok in BANNED_ROCQ_TOKENS)


def _mget(metadata, key):
    return metadata[key] if isinstance(metadata, dict) else getattr(metadata, key)


def _score_index(answer, entry):
    s = str(answer).strip().strip("`")
    return float(bool(re.fullmatch(r"\d+", s)) and int(s) == int(entry.answer))


def _zlist(values):
    return "[" + "; ".join(map(str, values)) + "]"


@dataclass
class RocqConfig(Config):
    n_candidates: int = 4
    n_hyps: int = 3
    expr_depth: int = 2
    list_len: int = 5
    certify_timeout: int = 20
    payload_cap: int = 5000

    def apply_difficulty(self, level):
        self.n_hyps = sround(self.n_hyps + level)
        self.expr_depth = sround(self.expr_depth + 0.5 * level)
        self.list_len = sround(self.list_len + level)
        self.certify_timeout = sround(self.certify_timeout + level)
        self.payload_cap = sround(self.payload_cap + 400 * level)


# ============================================================================
# Rocq proof repair
# ============================================================================


def _theorem(header, proof):
    return f"{header.rstrip()}\nProof.\n  {_cmd(proof)}\nQed.\n"


def _cmd(proof):
    proof = str(proof).strip()
    return proof if proof.endswith(".") else proof + "."


def _ltac(proof):
    return str(proof).strip().rstrip(".").strip()


def _candidate_labels_batched(header, candidates, timeout):
    chunks = []
    for i, cand in enumerate(candidates, 1):
        named = re.sub(r"\bTheorem\s+target\b", f"Theorem target_{i}", header.rstrip(), count=1)
        chunks.append(
            f'{named}\nProof.\n'
            f'  tryif solve [{_ltac(cand)}] then idtac "RC_CAND_{i}_TRUE" else idtac "RC_CAND_{i}_FALSE".\n'
            "Abort.\n"
        )
    ok, out, err = check_rocq("\n".join(chunks), timeout=timeout)
    if not ok:
        return []
    text = out + "\n" + err
    labels = []
    for i in range(1, len(candidates) + 1):
        if f"RC_CAND_{i}_TRUE" in text:
            labels.append(True)
        elif f"RC_CAND_{i}_FALSE" in text:
            labels.append(False)
        else:
            return []
    return labels


def _proof_lia_chain(config):
    n = max(2, min(6, int(config.n_hyps)))
    names = [chr(ord("a") + i) for i in range(n + 1)]
    hyps = []
    strict_at = random.randrange(n)
    for i in range(n):
        op = "<" if i == strict_at else "<="
        hyps.append((f"h{i}", f"{names[i]} {op} {names[i + 1]}"))
    goal_op = "<"
    decl = " ".join(f"({v} : Z)" for v in names)
    hyp_src = " ".join(f"({h} : {p})" for h, p in hyps)
    header = (
        "From Stdlib Require Import ZArith Lia.\n"
        "Open Scope Z_scope.\n\n"
        f"Theorem target {decl} {hyp_src} : {names[0]} {goal_op} {names[-1]}."
    )
    distractors = [
        "exact h0.",
        f"exact h{n - 1}.",
        "eapply Z.le_trans; eauto.",
        "eapply Z.lt_le_trans; eauto.",
        "ring.",
        "tauto.",
    ]
    return edict(kind="lia_chain", header=header, primary="lia.", distractors=distractors)


def _proof_ring(config):
    vars_ = list("abcd")[: max(2, min(4, int(config.expr_depth) + 1))]
    x, y = vars_[0], vars_[1]
    cases = [
        (f"({x} + {y}) * ({x} + {y})", f"{x} * {x} + 2 * {x} * {y} + {y} * {y}"),
        (f"({x} - {y}) * ({x} + {y})", f"{x} * {x} - {y} * {y}"),
        (f"({x} + 1) * ({x} + 1)", f"{x} * {x} + 2 * {x} + 1"),
        (f"({x} + {y}) + ({y} + {x})", f"2 * {x} + 2 * {y}"),
    ]
    lhs, rhs = random.choice(cases)
    decl = " ".join(f"({v} : Z)" for v in vars_)
    header = (
        "From Stdlib Require Import ZArith Ring.\n"
        "Open Scope Z_scope.\n\n"
        f"Theorem target {decl} : {lhs} = {rhs}."
    )
    distractors = ["reflexivity.", "assumption.", "tauto.", "easy."]
    return edict(kind="ring", header=header, primary="ring.", distractors=distractors)


def _proof_tauto(config):
    atoms = [f"P{i}" for i in range(max(3, min(7, int(config.n_hyps) + 2)))]
    p, q, r = atoms[:3]
    cases = [
        (f"({p} -> {q}) -> ({q} -> {r}) -> {p} -> {r}", "intros h0 h1 hp; exact h1 (h0 hp)."),
        (f"({p} /\\ {q}) -> ({q} /\\ {p})", "intro h; exact conj (proj2 h) (proj1 h)."),
        (f"({p} \\/ {q}) -> ({p} -> {r}) -> ({q} -> {r}) -> {r}", "intros h hp hq; destruct h as [a|b]; exact hp a; exact hq b."),
        (f"(({p} /\\ {q}) \\/ ({p} /\\ {r})) -> {p}", "intro h; destruct h as [h|h]; exact (proj1 h); exact (proj1 h)."),
    ]
    goal, specific = random.choice(cases)
    decl = " ".join(f"({a} : Prop)" for a in atoms)
    header = f"From Stdlib Require Import Logic.\n\nTheorem target {decl} : {goal}."
    distractors = ["exact I.", "reflexivity.", "assumption.", "firstorder.", "intuition.", specific]
    return edict(kind="tauto", header=header, primary="tauto.", distractors=distractors)


def _proof_list(config):
    names = list("xs ys zs")[:2]
    cases = [
        (
            "length (xs ++ rev ys) = length xs + length ys",
            "rewrite app_length, rev_length; lia",
            ["rewrite app_length; reflexivity", "rewrite rev_length; reflexivity", "simpl; reflexivity", "ring"],
        ),
        (
            "rev (xs ++ ys) = rev ys ++ rev xs",
            "rewrite rev_app_distr; reflexivity",
            ["rewrite app_nil_r; reflexivity", "simpl; reflexivity", "rewrite rev_involutive; reflexivity", "lia"],
        ),
        (
            "map (fun x => x + 0) xs = xs",
            "induction xs as [|x xs IH]; simpl; [reflexivity|rewrite IH; f_equal; lia]",
            ["reflexivity", "simpl; reflexivity", "rewrite map_length; reflexivity", "lia"],
        ),
    ]
    goal, primary, distractors = random.choice(cases)
    header = (
        "From Stdlib Require Import List Arith Lia.\n"
        "Import ListNotations.\n\n"
        f"Theorem target (xs ys : list nat) : {goal}."
    )
    return edict(kind="list", header=header, primary=primary, distractors=distractors)


_PROOF_BUILDERS = (_proof_lia_chain, _proof_ring, _proof_tauto, _proof_list)


class RocqProofRepair(DevTask):
    """Choose the unique Rocq proof body that compiles."""

    def __init__(self, config=RocqConfig(), **kwargs):
        for k, v in kwargs.items():
            setattr(config, k, v)
        super().__init__(config=config, timeout=180)

    def generate(self):
        n_cand = max(2, min(6, int(self.config.n_candidates)))
        for _ in range(80):
            inst = random.choice(_PROOF_BUILDERS)(self.config)
            pool = []
            for cand in [inst.primary, *inst.distractors]:
                if cand not in pool and _safe(cand):
                    pool.append(cand)
            random.shuffle(pool)
            pool = pool[:n_cand]
            if inst.primary not in pool:
                pool[random.randrange(len(pool))] = inst.primary
                random.shuffle(pool)
            labels = _candidate_labels_batched(inst.header, pool, timeout=int(self.config.certify_timeout))
            if sum(labels) != 1:
                continue
            answer = str(labels.index(True) + 1)
            source = _theorem(inst.header, "__BROKEN__")
            if len(source) + sum(map(len, pool)) > int(self.config.payload_cap):
                continue
            return Problem(
                metadata=edict(
                    kind=inst.kind,
                    broken=source,
                    candidates=pool,
                    labels=labels,
                    rocq_image=ROCQ_IMAGE,
                ),
                answer=answer,
            )
        raise RuntimeError("failed to generate a unique RocqProofRepair instance")

    def prompt(self, metadata):
        options = "\n".join(f"{i}. {c}" for i, c in enumerate(_mget(metadata, "candidates"), 1))
        return (
            "Fix the broken Rocq proof. Choose one candidate replacement.\n"
            "Answer with the candidate number only.\n\n"
            f"BROKEN PROOF:\n{_mget(metadata, 'broken')}\n\n"
            f"CANDIDATES:\n{options}"
        )

    def score_answer(self, answer, entry):
        return _score_index(answer, entry)

    def balancing_key(self, problem):
        return str(problem.answer)


# ============================================================================
# Rocq invariant MCQ
# ============================================================================


def _invariant_header(values, candidates, invariant):
    defs = [
        "From Stdlib Require Import List ZArith Bool Lia.",
        "Import ListNotations.",
        "Open Scope Z_scope.",
        "",
        f"Definition x0 : list Z := {_zlist(values)}.",
        "",
    ]
    for i, cand in enumerate(candidates, 1):
        defs.append(f"Definition candidate_{i} : list Z := {cand}.")
    defs.extend([
        "",
        "Definition zsum (xs : list Z) : Z := fold_left Z.add xs 0.",
        "",
        "Definition invariant (xs : list Z) : bool :=",
        f"  {invariant}.",
        "",
    ])
    for i in range(1, len(candidates) + 1):
        defs.append(f"Definition check_{i} := invariant candidate_{i}.")
    return "\n".join(defs)


def _invariant_labels(source, n_candidates, timeout):
    label_src = (
        source
        + "\n\nDefinition all_checks := ["
        + "; ".join(f"check_{i}" for i in range(1, n_candidates + 1))
        + "]."
    )
    text = eval_rocq(label_src, "all_checks", timeout=timeout)
    labels = [x == "true" for x in re.findall(r"\btrue\b|\bfalse\b", text)]
    return labels if len(labels) == n_candidates else []


def _invariant_cert(source, labels):
    parts = [f"check_{i} = {'true' if ok else 'false'}" for i, ok in enumerate(labels, 1)]
    return (
        f"{source}\n\n"
        "Goal " + "\n  /\\ ".join(parts) + ".\n"
        "Proof. vm_compute. repeat split; reflexivity. Qed.\n"
    )


def _sample_mixed_zs(config):
    n = max(4, min(9, int(config.list_len)))
    vals = [random.randint(-9, 12) for _ in range(n)]
    if not any(x < 0 for x in vals):
        vals[random.randrange(n)] = -random.randint(1, 9)
    if not any(x > 0 for x in vals):
        vals[random.randrange(n)] = random.randint(1, 9)
    if not any(x % 2 for x in vals):
        vals[random.randrange(n)] += 1
    if not any(x % 2 == 0 for x in vals):
        vals[random.randrange(n)] += 1
    return vals


def _mcq_all_nonneg(config):
    k = random.randint(1, 5)
    return (
        [
            "List.rev x0",
            "List.map Z.abs x0",
            "List.filter Z.even x0",
            f"x0 ++ [{k}]",
        ],
        "List.forallb (fun z => Z.leb 0 z) xs && Nat.eqb (length xs) (length x0)",
        "nonnegative_full_length",
    )


def _mcq_even_filter(config):
    k = random.choice([1, 3, 5, 7])
    return (
        [
            "List.rev x0",
            "List.map Z.abs x0",
            "List.filter Z.even x0",
            f"x0 ++ [{k}]",
        ],
        "List.forallb Z.even xs && Nat.eqb (length xs) (length (List.filter Z.even x0))",
        "even_filter",
    )


def _mcq_reverse(config):
    return (
        [
            "List.rev x0",
            "List.map Z.abs x0",
            "List.filter Z.even x0",
            "tl x0 ++ [hd 0 x0]",
        ],
        "Z.eqb (hd 0 xs) (List.last x0 0) && Z.eqb (List.last xs 0) (hd 0 x0) && Nat.eqb (length xs) (length x0)",
        "reverse_endpoints",
    )


def _mcq_sum_shift(config):
    k = random.randint(2, 6)
    return (
        [
            "List.rev x0",
            f"List.map (fun z => z + {k}) x0",
            "List.filter Z.even x0",
            f"x0 ++ [{k}]",
        ],
        f"Z.eqb (zsum xs) (zsum x0 + {k} * Z.of_nat (length x0)) && Nat.eqb (length xs) (length x0)",
        "sum_shift",
    )


_MCQ_BUILDERS = (_mcq_all_nonneg, _mcq_even_filter, _mcq_reverse, _mcq_sum_shift)


class RocqInvariantMCQ(DevTask):
    """Choose the unique same-typed candidate satisfying a Rocq boolean invariant."""

    def __init__(self, config=RocqConfig(), **kwargs):
        for k, v in kwargs.items():
            setattr(config, k, v)
        super().__init__(config=config, timeout=180)

    def generate(self):
        n_cand = 4
        for _ in range(100):
            values = _sample_mixed_zs(self.config)
            candidates, invariant, kind = random.choice(_MCQ_BUILDERS)(self.config)
            pairs = list(enumerate(candidates, 1))
            random.shuffle(pairs)
            shuffled = [c for _, c in pairs]
            source = _invariant_header(values, shuffled, invariant)
            if len(source) > int(self.config.payload_cap):
                continue
            labels = _invariant_labels(source, n_cand, int(self.config.certify_timeout))
            if sum(labels) != 1:
                continue
            cert = _invariant_cert(source, labels)
            ok, _, _ = check_rocq(cert, timeout=int(self.config.certify_timeout))
            if not ok:
                continue
            return Problem(
                metadata=edict(
                    kind=kind,
                    source=source,
                    labels=labels,
                    rocq_image=ROCQ_IMAGE,
                    stats=edict(payload_chars=len(source), list_len=len(values)),
                ),
                answer=str(labels.index(True) + 1),
            )
        raise RuntimeError("failed to generate a unique RocqInvariantMCQ instance")

    def prompt(self, metadata):
        return (
            "Exactly one candidate makes the Rocq boolean invariant evaluate to true.\n"
            "Answer with the candidate number only.\n\n"
            f"ROCQ SOURCE:\n{_mget(metadata, 'source')}"
        )

    def score_answer(self, answer, entry):
        return _score_index(answer, entry)

    def balancing_key(self, problem):
        return str(problem.answer)
