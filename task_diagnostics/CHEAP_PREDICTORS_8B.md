# Cheap predictors of GPU influence — model llama-3.1-8b-instruct

Each cheap signal's Spearman ρ vs the expensive per-task influence (`global%` = mean 6-leg NLL reduction; `bbh%`). Ranked by |ρ vs global|. Positive ρ ⇒ higher signal predicts more-useful task.

| cheap signal | ρ(global) | p | n | ρ(bbh) | p | n |
|:--|--:|--:|--:|--:|--:|--:|
| ans_chars | -0.40 | +0.009 | 41 | -0.47 | +0.002 | 41 |
| judge_reasoning_depth | +0.34 | +0.043 | 36 | +0.34 | +0.042 | 36 |
| judge_training_usefulness | +0.19 | +0.275 | 36 | +0.20 | +0.247 | 36 |
| judge_interestingness | +0.17 | +0.330 | 36 | +0.21 | +0.208 | 36 |
| zs_reward | +0.16 | +0.322 | 41 | +0.36 | +0.020 | 41 |
| prompt_chars | +0.11 | +0.500 | 41 | +0.06 | +0.709 | 41 |
| judge_learnability | -0.09 | +0.585 | 36 | -0.26 | +0.133 | 36 |
| judge_difficulty | +0.08 | +0.639 | 36 | +0.18 | +0.292 | 36 |
| r3 | +0.05 | +0.766 | 41 | +0.20 | +0.201 | 41 |
| judge_diversity | -0.02 | +0.902 | 36 | +0.05 | +0.785 | 36 |
| lift3 | -0.02 | +0.921 | 41 | -0.04 | +0.814 | 41 |

_zs_reward=zero-shot reward, r3=reward@3-shot, lift3=ICL lift (r3−r0), ans/prompt_chars=answer/prompt length, judge_*=LLM data-quality rating axis._
