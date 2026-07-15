# Cheap predictors of GPU influence — model llama-3.3-70b-instruct

Each cheap signal's Spearman ρ vs the expensive per-task influence (`global%` = mean 6-leg NLL reduction; `bbh%`). Ranked by |ρ vs global|. Positive ρ ⇒ higher signal predicts more-useful task.

| cheap signal | ρ(global) | p | n | ρ(bbh) | p | n |
|:--|--:|--:|--:|--:|--:|--:|
| judge_reasoning_depth | +0.46 | +0.003 | 39 | +0.51 | +0.001 | 39 |
| ans_chars | -0.38 | +0.015 | 41 | -0.44 | +0.004 | 41 |
| judge_training_usefulness | +0.32 | +0.049 | 39 | +0.33 | +0.039 | 39 |
| judge_interestingness | +0.23 | +0.163 | 39 | +0.23 | +0.154 | 39 |
| judge_difficulty | +0.23 | +0.165 | 39 | +0.29 | +0.070 | 39 |
| judge_learnability | -0.15 | +0.348 | 39 | -0.28 | +0.082 | 39 |
| prompt_chars | +0.10 | +0.522 | 41 | +0.16 | +0.309 | 41 |
| r3 | -0.08 | +0.607 | 41 | -0.09 | +0.562 | 41 |
| zs_reward | -0.07 | +0.666 | 41 | +0.05 | +0.779 | 41 |
| lift3 | +0.05 | +0.758 | 41 | -0.03 | +0.859 | 41 |
| judge_diversity | +0.04 | +0.787 | 39 | +0.05 | +0.760 | 39 |

_zs_reward=zero-shot reward, r3=reward@3-shot, lift3=ICL lift (r3−r0), ans/prompt_chars=answer/prompt length, judge_*=LLM data-quality rating axis._
