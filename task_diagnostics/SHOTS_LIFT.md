# In-context learnability (ICL lift) — llama-3.1-8b-instruct

Reward = free-gen `score_answer` on the frozen model. **lift@K = reward@K − reward@0** — how much the model picks the task up from K worked examples (in-context learnability). Sorted by lift@3 (most ICL-learnable first).

| task | 0-shot | 1-shot | 3-shot | lift@1 | lift@3 | infl% |
|---|---|---|---|---|---|---|
| mgu_implied_equality | 0.27 | 0.45 | 0.67 | +0.19 | +0.40 | — |
| defeasible_nli | 0.27 | 0.53 | 0.60 | +0.27 | +0.33 | — |
| analogical_case_matching | 0.00 | 0.20 | 0.33 | +0.20 | +0.33 | — |
| multistep_nli | 0.40 | 0.47 | 0.73 | +0.07 | +0.33 | +9.7 |
| code_analysis | 0.20 | 0.20 | 0.47 | +0.00 | +0.27 | — |
| planning | 0.35 | 0.51 | 0.58 | +0.15 | +0.23 | +2.9 |
| game_forced_win | 0.33 | 0.47 | 0.47 | +0.13 | +0.13 | +10.3 |
| code_input_deduction | 0.00 | 0.07 | 0.13 | +0.07 | +0.13 | +3.0 |
| regex_following | 0.46 | 0.56 | 0.59 | +0.10 | +0.12 | +4.1 |
| count_elements | 0.97 | 1.00 | 1.00 | +0.03 | +0.03 | +7.5 |
| set_expression | 0.54 | 0.41 | 0.54 | -0.13 | +0.01 | +3.3 |
| arithmetics | 0.32 | 0.20 | 0.32 | -0.12 | +0.00 | +5.5 |
| program_synthesis | 0.00 | 0.00 | 0.00 | +0.00 | +0.00 | +0.6 |
| belief_tracking | 0.53 | 0.67 | 0.53 | +0.13 | +0.00 | — |

- **Spearman(zero-shot reward, lift@3) = -0.34** (p=0.228, n=14) — negative ⇒ ICL helps most where zero-shot is weakest (headroom effect).
- **Spearman(train-time influence global%, lift@3) = +0.37** (p=0.332, n=9) — positive ⇒ tasks that are learnable *in context* are also the ones useful when *trained on* (two learnability probes agree).
