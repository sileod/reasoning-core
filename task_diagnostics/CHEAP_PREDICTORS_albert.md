# Cheap predictors of GPU influence — model Mistral-Small-3.2-24B-Instruct-2506

Each cheap signal's Spearman ρ vs the expensive per-task influence (`global%` = mean 6-leg NLL reduction; `bbh%`). Ranked by |ρ vs global|. Positive ρ ⇒ higher signal predicts more-useful task.

| cheap signal | ρ(global) | p | n | ρ(bbh) | p | n |
|:--|--:|--:|--:|--:|--:|--:|
| judge_reasoning_depth | +0.46 | +0.003 | 39 | +0.51 | +0.001 | 39 |
| ans_chars | -0.34 | +0.087 | 27 | -0.49 | +0.010 | 27 |
| judge_training_usefulness | +0.32 | +0.049 | 39 | +0.33 | +0.039 | 39 |
| zs_reward | +0.30 | +0.130 | 27 | +0.10 | +0.618 | 27 |
| judge_interestingness | +0.23 | +0.163 | 39 | +0.23 | +0.154 | 39 |
| judge_difficulty | +0.23 | +0.165 | 39 | +0.29 | +0.070 | 39 |
| prompt_chars | +0.16 | +0.418 | 27 | +0.20 | +0.323 | 27 |
| judge_learnability | -0.15 | +0.348 | 39 | -0.28 | +0.082 | 39 |
| judge_diversity | +0.04 | +0.787 | 39 | +0.05 | +0.760 | 39 |
| r3 | — | — | 0 | — | — | 0 |
| lift3 | — | — | 0 | — | — | 0 |

_zs_reward=zero-shot reward, r3=reward@3-shot, lift3=ICL lift (r3−r0), ans/prompt_chars=answer/prompt length, judge_*=LLM data-quality rating axis._
