# tasks/dev: notes from the 2026-09-29 lunch session

Nothing here is in `list_tasks()`: these are `DevTask`s. The registry still discovers them
(`task_catalog(include_dev=True)`), so names must stay unique.

## `inverse_math` (`math_inverse.py`)

**Principle.** Sample the *answer* from a small grammar, apply the easy direction, and ask for
the hard one. One expression grammar feeds every mode, so a handful of seeds yields a very wide
distribution. There is no prover in the loop: every answer is a **certificate** that is checked
semantically, so any correct form scores, not just the reference string.

| mode | easy direction (generation) | asked (inverse) | check |
|---|---|---|---|
| integral | differentiate a random F (backward), or sympy-integrate a random short f (forward, which avoids derivative-shaped integrands) | antiderivative | d/dx(answer) = f at random points |
| factor | multiply random irreducible integer polynomials (1-2 variables) | complete factorization | expands to P, every factor irreducible and primitive |
| equation | polynomial with chosen roots, then substitute a chain of invertible maps (exp, 2^x, log, sqrt, 1/x, x^3, affine) | all real solutions | numeric set equality |
| sum | take differences of a random F (poly, geometric, n*2^n, rational) | closed form of the sum | exact partial sums for n = 1..7 |
| recurrence | a closed form with roots, multiplicities and a forcing term, turned into its linear recurrence | closed form | exact values for n = 0..11 |
| ode | a family y(x, C), with C eliminated (separable or linear first order); or y'' + p y' + q y = g from a chosen spectrum (distinct / repeated / complex roots) and particular solution, resonance included | general solution | ODE residual = 0 for several constant values; for order 2, the C1 and C2 directions must be independent |
| minimum | c + sum of w*q^2, each q vanishing at a hidden point, expanded | minimum value | exact |
| sos | same construction | **a proof** of f >= c as a sum of squares | expansion + shape check |
| eigen | A = P D P^-1 with P a unimodular integer matrix (so A is an integer matrix); repeated eigenvalues allowed; triangular and scalar matrices rejected | eigenvalues with multiplicity | exact multiset |
| claim | same, with the bound shifted up or down | **prove or refute**: an SOS proof, or a counterexample point | both sides certificate-checked, so no True/False guessing |

`sos` and `claim` are the proof side: an inequality's proof *is* an SOS certificate, and a false
universal claim's refutation *is* a witness point. Both are checked by expansion or evaluation,
with no kernel.

Scoring accepts LaTeX and textbook notation (`\frac`, `\cdot`, `log_2`, `\left(`...): the first
probe lost correct answers to format alone. Parsing is guarded: allowlisted names only, no `__`,
length-capped.

**Checks run.** `python -m reasoning_core.tasks.dev._check_math_inverse` (scorer: equivalent
forms pass, near misses fail; gold answers score 1 at levels 0/3/6) passes. `validate()` passes.
`pytest tests/*.py`: 92 passed. `list_tasks()` is unchanged (53 tasks). Generation averages
0.02 s (L0) to 0.16 s (L6) per example, worst case about 2.3 s (forward integration / ODE), and
prompts are at most about 180 tokens. Unique prompts: 191/200 at L0, 200/200 at L6. Modes are
balanced: the mode is drawn once per example.

**Difficulty (zero-shot probes, albert):** see "Probe results" at the bottom.

## Known weaknesses / next steps

- Backward generation gives long, derivative-shaped problems. Integrals and sums are now half
  forward (sympy `integrate` / `summation` on short natural terms, elementary results only, 1 s
  timeouts). Artefacts such as `atan(tan(u))` and `log(exp(a)*b)` are rejected.
- At low levels the SOS instances are often just completing the square; richer instances need
  quadratic forms with several independent squares.
- Not yet covered: second-order ODEs; diagonalization certificates; inverse functions; definite
  integrals.
- Timing: L6 averages 0.13-0.18 s, worst case about 2.6 s (forward integration). That is under the
  3 s limit, but integration is the mode to watch.

**Broader direction, "certificate mathematics":** pick areas where proofs have compact,
cheaply checkable certificates. Each one adds proof-level tasks without a kernel:
- SOS (done);
- counterexamples (done);
- ideal-membership / Nullstellensatz cofactors (g = a*f1 + b*f2, checked by expansion);
- Farkas / LP duals for linear infeasibility;
- WZ pairs for binomial-sum identities;
- Bezout coefficients;
- Lyapunov functions.

The saturate-and-cut-proofs recipe (TPTP, Metamath) was already tried and did not pan out; this
direction avoids it.

## Probe results

Mistral-Small-24B on albert, allowed to show working (max 3k tokens), temperature 0. Each failure
was audited by hand, and the scorer was fixed wherever it rejected a correct answer (LaTeX,
`log_2`, `|u|`, squares written as products). Re-scoring with the final scorer changes nothing.

| version | L0 | L2 / L3 | L4 | L6 |
|---|---|---|---|---|
| v2 (4 modes, before the LaTeX fix, so it undercounts) | 0.71 | 0.38 (L3) | - | 0.00 |
| v4 (9 modes, n ≈ 28/level) | 0.80 | 0.64 | 0.63 | 0.50 |
| v5 (11 modes, after steepening integral and minimum) | 0.83 | 0.48 (L3) | - | 0.37 |
| **v6 (final: + second-order ODEs, n ≈ 26/level)** | **0.79** | **0.44 (L3)** | - | **0.25** |

v4 was monotone but too shallow. Per mode, `integral` and `minimum` barely got harder: many L4-L6
instances were a single square or `2x + sin x + 3`. Both were steepened afterwards: at least as
many squares as variables, each with 2+ terms, and 1.5x size for backward integrals. `factor`,
`sum`, `sos` and `ode` did get harder with level. deepseek-v4-flash with reasoning: 5/5 at L0,
and too slow on the free tier to measure more.

v5 per mode, L0 / L3 / L6. `factor` (0/2, 0/1, 0/3) and `ideal` (0/1, 0/3, 0/2) are hard even at
L0; every failure was audited and is a genuine wrong answer. `eigen` goes 3/3, 0/3, 0/3. `ode` was
flat at 100%: in the linear case the right-hand side shows B*A' outright, so it was just reading
off the integrating factor. It was then given a larger inner function plus the second-order mode,
and v6 measures that.

**Caution for editors:** `registry._parse_task_file` calls `ast.parse` without a guard. A syntax
error in *any* file under `tasks/`, dev included, breaks discovery for everyone using this
checkout. Check syntax before writing.

v6 audit: two ODE answers written `C_1`/`C_2` or `±sqrt(...)` were correct but rejected; the
normalizer now handles both, and the numbers above are re-scored. At L6, 5 of the 11 modes are 0
for Mistral-Small with working. A stronger model is still needed to calibrate the top levels:
deepseek-v4-flash with reasoning was too slow on the free tier to measure.

## `planted_witness` (moved to `tasks/generated/planted_witness.py`: narrow, undetermined-coefficients algebra)

The abstraction behind `inverse_math`, without named problem types. `inverse_math` is honestly
eleven hand-picked generators behind one name; here there is one generator:

1. Sample a hidden witness W* of a type: number, integer polynomial, or sequence (poly x exp x (-1)^n).
2. Sample random terms from one typed operator grammar over the unknowns: shift / scale /
   point-evaluation arguments (`p(x+1)`, `a(2n)`, `p(0)`), `d/dx` (polynomials), `+`, `*`, powers, known
   constants and expressions. Right-hand sides are y = T(W*), expanded so the structure of W* is not printed.
3. **Keep only well-posed systems.** Each type reduces to finitely many unknowns (the numbers; the
   coefficients of a degree deg(W*)+1 ansatz; the sequence values a(0..M) with the equations at n = 0..6),
   an exact Jacobian test at W* rejects non-isolated solutions cheaply, and `sympy.solve` over the whole
   system must return W* alone (no free constant, no free a(0), no ± branch). Since W* is planted, extra
   equations never contradict: equations are added until the solution is unique (at most k + 2), then any
   equation the others imply is dropped, so the system is minimal.
4. Checker: parse `p(x) = ..., q(x) = ...`, plug in, compare (exact / at points / at n = 0..6).

What is chosen by hand: the three types, the operator list, and filter constants. Semantics are
sympy's. Problems such as polynomial division, functional composition equations, and shifted or dilated
sequence equations with initial conditions emerge from the grammar rather than being coded as modes.

**Functions dropped.** Arbitrary-function unknowns have no finite reduction, so uniqueness cannot be
certified (f' leaves a constant free, f(x^2) says nothing on x < 0). Kept out rather than faked.

**Checks.** `python -m reasoning_core.tasks.dev._check_planted_witness`: 0 mismatches, gold 1 and
perturbed gold 0 at levels 0/3/6. `validate()` OK. `list_tasks()` unchanged.

**Timing (open issue).** Mean 0.1 s (L0), 0.4 s (L3), about 2 s (L6), with worst cases over 10 s. The
cost is the rejection loop around `sympy.solve` for L6 polynomials and sequences, which is over the
1 s mean budget at the top levels. Options: cap witness size, or replace the global solve by
resultants / Groebner bases with a degree bound.

## `mathlib_rewrite` (`mathlib_rewrite.py` + `mathlib_rewrite.lean`)

**Why Lean, and why rewrites.** Mathlib's computable vocabulary is thin: 201 executable functions with
simple types, almost all ℕ/ℤ number theory. Its generality is in its theorems: 139,520 equational
theorems across every area (algebra 30k, category theory 22k, data 13k, analysis 11k, ring theory
8.6k, topology 8.4k, linear algebra 7k, order 7k, group theory 4.6k, measure theory 4.5k, …).

**Generation (all in Lean, via the REPL).** Start from the left-hand side of a random Mathlib
equation, with its binders as the context. Apply k random rewrites found by core Lean's `rw?` engine
(`Lean.Meta.Rewrites.findRewrites`, a lazy discrimination tree over every equational lemma). Generic
filters, with no per-domain lists:
- never revisit a term, as an expression or as printed; each lemma at most once; the start lemma excluded;
- bounded growth per step, stricter for right-to-left steps; a total size cap;
- skip steps where old and new terms are definitionally equal at default transparency
  (`toLex`, `OrderDual.toDual`, `+ᵥ` vs `+`, …);
- a vocabulary budget: at most 1 + k/3 new non-instance constants per walk;
- the rewritten side must match exactly one subterm, so "rewrite with lemma L" is unambiguous;
- canonical binder names by nesting depth (x₁, x₂, …), so the printed answer is unique up to alpha-renaming;
- no `⋯` or `✝` in printed terms;
- the produced side has no variable absent from the matched side (`← mul_zero` turning `0` into `? * 0` is out);
- no padding: the produced side may not contain the matched side (`← compl_compl_compl : aᶜ ↦ aᶜᶜᶜ`,
  `← sup_left_idem`, `← mul_one`);
- at most one pure reordering per walk (old and new terms have the same leaves): commutativity and swaps
  were a third of all steps before this rule;
- no class-axiom projections (`AddCommMagma.add_comm`, `Distrib.left_distrib`): `rw?` also finds the theorem
  forms (`add_comm`, `left_distrib`);
- every printed term must round-trip: pasted back into Lean (in the `variable` context shown), it elaborates
  to the same term up to instances. A walk is cut before its first term that does not, so every prefix
  of a walk is a walk. Walks always aim for 6 steps; a k-step example takes the shortest buffered walk with
  k or more steps, cut to k (task_version 4). Before this, a level-3 example waited for a walk of exactly
  about 3 steps, and level 3 was slower than level 6 in the scaling benchmark.
- each walk in a batch has its own heartbeat budget (50k), and running out of it drops that walk only.
  Before this, 6 of 28 Lean calls (21%) died entirely on one walk's `maxHeartbeats` timeout, which plain
  `try` does not catch, and one such call took 317 s. Measured survival from viable starts: 93% of walks
  reach 1 step, 63% reach 2, 37% reach 3, 28% reach 4, 19% reach 6; from random starts only 32% take a step.

**Task.** Given the context, the start term and the lemma sequence (with ← for right-to-left), give the
resulting term as Lean prints it (`mathlib_rewrite`, forward execution). `mathlib_rewrite_middle` uses the same
walks (2+ steps), also shows the final term, and asks for the term right after step i < k: it can be
worked forward or backward. They are separate tasks so each gets its own value and difficulty curve. Both answers are unique
(`rw` is deterministic, one match per step). A third format, naming the lemma for a given step, was dropped:
Mathlib aliases (`Nat.add_comm`, `AddCommMonoidWithOne.add_comm`) make that answer non-unique.

**Scoring** is pure Python, with no Lean, at 0.09 ms per answer. Both terms are parsed with Lean's precedences
for the notation walks produce (`+ - * / % ^ • ∪ ∩ \ ⊔ ⊓ ⇨ ∘ ⁻¹' '' :: +ᵥ -ᵥ ×ˢ`, comparisons, prefix `-`, postfix
`⁻¹ ᶜ ⁺`, field projections, bracket groups, the binders `∑ ∏ ⋃ ⋂ ⨆ ⨅ fun`), and the trees are compared, so
spacing and redundant parentheses do not matter. Anything else (unknown or decorated operators, `if`, `∫`,
`{x | p}`) falls back to whitespace-normalized string equality, so two different terms are never merged.
Coercion arrows are part of the tree: `↑a / ↑b` is not `↑(a / b)`. Dropping arrows, as the earlier normalizer
did, merged exactly that pair. Arrows in the answer are ignored only when the gold has none.
- Validated against Lean, on 834 walk terms printed with `pp.parens true`: 742 parse. Every term's tree equals its
  fully parenthesized print's tree, except one `∑ … with p` header, a false negative only. No two distinct terms
  share a tree.
- A Lean term-equality fallback was tried earlier and removed. On the 90 old probe answers, the parser now
  accepts a redundant-parentheses answer that the Lean fallback also rescued. It rejects `n + 1` for `n.succ`:
  defeq, but not the term `rw` produces.

**Glossary** (`glossary=True`, the default). Steps give lemma names only. A glossary, sorted by name, states
the lemmas used plus `distractors` × steps others. Distractors are the other `rw?` candidates that also
rewrote the walk's terms (e.g. `neg_eq_neg_one_mul` beside `mul_neg`), else lemmas from other walks. They
never restate an equation already listed, so aliases count once. The skill is composing given rules, not
recalling Mathlib. `glossary=False` gives names only, for models that know Mathlib by heart.
Difficulty: steps 1 → 6 (+0.4 per level) is the only driver. Distractors are fixed at 1 per step, with
equations of at most 120 characters, so the glossary grows linearly with steps (about 2 × steps entries).

**Eval (task_diagnostics, 2026-10-01, task_version 3; rank of 54 roster tasks).**
| task | ext | margin |
|---|---|---|
| `mathlib_rewrite_middle` (C) | +11.3 (#41) | +1.04 (#19) |
| `mathlib_rewrite` (A) | +9.9 (#45) | +0.69 (#29) |
| `mathlib_rewrite` v2 (names hidden, no glossary) | +10.3 (#44) | +0.86 (#23) |
| `lean_missing_line` | +10.4 (#44) | +0.61 (#32) |

C, read both ways, is the most valuable form; A with a glossary scores below v2.

**Where Lean time goes** (64 walks, 2026-10-01). Walks that end in an error or exception took 65% of the
time (10 walks; one took 98 s within a 50k-heartbeat budget), walks with no step 13%, and walks of 2+
steps only 17%. Inside walks, executing candidate rewrites (`rwLemma`) dominates (20 s), then the `rw?`
index lookup (10 s); the lazy index itself costs nothing to create per walk.
`mathlib_rewrite_middle_fast` is the same task with tight per-walk limits (20k heartbeats; a walk stops
extending after 5 s and keeps its prefix). It is a separate task because the limits change which walks get
generated. The list of viable starts was re-explored under the current filters; the earlier one is kept
as `mathlib_rewrite_viable.pre_v4.tsv`. Re-exploration: 16 workers × 20 min, 848 calls, 2,230 distinct starts,
of which 773 reach at most 1 step, 460 reach 2, 216 reach 3, 131 reach 4, 55 reach 5 and 595 reach 6.
- Even with the fast limits, 4 of the 16 workers hit the REPL's 360 s call timeout: some Lean operations are
  not bounded by heartbeats. `_eval` now replaces a REPL that timed out (its late reply would otherwise answer
  the next call) and closes it on the caller's per-example alarm, as `LeanRunner.check` does.
- Scaling benchmark after the refresh (12 samples per cell, fresh process; warm seconds per example at
  L0 / L3 / L6): `mathlib_rewrite_middle` 1.6 / 3.2 / 4.4 (before: 6.8 / 4.6 / 5.0); `_fast` 1.5 / 2.8 / 2.7.
  First example: 31–57 s (REPL start plus the first Lean call).
- Through `generate_balanced_batch` at L3 (`_fast`): 32 rows in 126 s (3.9 s/row with startup; Lean calls
  3.4 s/row); 64 rows in 208 s (3.25 s/row). Bigger batches spread the ~18 s startup but cannot go below the
  Lean time per row. An earlier 64-row batch took 632 s: about 0.5% of calls stall until the runner's 360 s
  timeout, as some Lean operations ignore heartbeats. `_fast` gives each call 90 s (healthy calls take under
  25 s), so a stall costs about 2 minutes instead of 7.

**Scoring has no Lean dependency.** The task module imports the Lean runner (`math_lean`, which pulls in about
3.4 s of nltk/gramforge imports) only when generating, so a scorer process never loads it.

**Cost.**
- One-time: the lemma scan takes 225 s (cached in `~/.local/share/reasoning_core/lean/mathlib_eq_lemmas.tsv`).
- Per process: about 35 s (REPL start, walk code, `rw?` index).
- Per example, measured 2026-10-01: 0.9 ex/s at L0 and 0.5 ex/s at L3 with a cold viable list. With heavy start reuse
  it reached 3 ex/s, but that made duplicates. Before batching it was 0.29 ex/s at L0.
- Where the time went: most start lemmas fail (about 60% find no acceptable first rewrite), and every REPL call
  has about 0.25 s of overhead.
- What fixed it:
  - one REPL call runs a batch of 16 walks, sharing a cache of which (lemma, direction) leave variables undetermined;
  - candidate rewrites are tried lazily: shuffle, then keep the first one that passes;
  - finished walks of any length are buffered by length;
  - starts that produced walks go to a shared list (`mathlib_rewrite_viable.tsv`). Reuse of that list scales with its
    size (75% × viable/2000), each start is used at most 4 times per process, and a walk is never emitted twice.
- Scoring is pure Python: 0.09 ms.
- Remaining lever: pre-warm the viable list (a one-time exploration job) so that reuse is high from the start.

**Probe (36 instances, 12 per level, schedule +0.6 steps / −0.2 statements per level, before softening).**
Mistral-Small, step by step: 0.58 / 0.17 / 0.00 at L0 / L3 / L6. deepseek-v4-flash with reasoning: 0.33 / 0.08 / 0.00, but
20 of its 36 calls errored on the free tier, so it is not calibrated. A Lean fallback scorer (since removed) rescued 4
answers that differed only by notation. The remaining L0 failures are genuine: wrong occurrence rewritten,
wrong direction, or simplifying past what `rw` does. Afterwards the schedule was softened to +0.4 / −0.1 per level.
