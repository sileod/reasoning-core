---
pretty_name: Procedural Choices
license: cc-by-4.0
task_categories:
- multiple-choice
- question-answering
language:
- en
configs:
- config_name: reasoning_core
  default: true
  data_files:
  - split: train
    path: reasoning_core/train.parquet
  - split: test
    path: reasoning_core/test.parquet
- config_name: reasoning_gym
  data_files:
  - split: train
    path: reasoning_gym/train.parquet
  - split: test
    path: reasoning_gym/test.parquet
tags:
- reasoning
- procedural
- synthetic
- multiple-choice
- verifiers
size_categories:
- 10K<n<100K
---

# Procedural Choices

Multiple-choice questions over procedural reasoning tasks. Every question is a prompt from a procedural
dataset with its verified reference answer plus up to 12 wrong options. Every wrong option is rejected by the
task's own scorer.

| config | source | tasks | train | test |
|---|---|---|---|---|
| `reasoning_core` (default) | [procedural-pretraining-pile](https://huggingface.co/datasets/reasoning-core/procedural-pretraining-pile) @ `rc14` | 55 | 50,000 | 5,000 |
| `reasoning_gym` | [reasoning-gym](https://huggingface.co/datasets/reasoning-core/reasoning-gym) @ `531e215` | __RG_TASKS__ | __RG_TRAIN__ | __RG_TEST__ |

```python
from datasets import load_dataset
ds = load_dataset("reasoning-core/procedural-choices")                   # reasoning_core
rg = load_dataset("reasoning-core/procedural-choices", "reasoning_gym")
```

## Fields

- `task`, `level`: source task and difficulty level.
- `prompt`: the source prompt, unchanged, including its answer-format instruction.
- `options`: the reference answer and the wrong options, shuffled.
- `label`: the index of the reference answer in `options`.
- `option_scores`: the task scorer's score for each option. The reference scores 1. A wrong option scores
  below 1, and a few keep partial credit (for example a numeric answer close to the reference).
- `answer`: the reference answer.
- `id`: the source row's deduplication key (`reasoning_core` only).

## How the options are made

Wrong options come from `Task.generate_distractors` in [reasoning-core](https://github.com/sileod/reasoning-core). Nothing new is generated.

- **Candidates:**
  - first, the task's own near misses (most `reasoning_core` tasks define them);
  - then, answers to other questions of the same task at the same level.
- **Filter:** a candidate is kept only if the task's scorer rejects it.
- **Ranking:** candidates are ranked by surface similarity to the reference, and the closest ones are used.
- **Grounding:** when every word of the reference appears in the prompt, every word of a wrong option must
  too. Otherwise an option naming people or objects the prompt never mentions can be eliminated without
  solving. Before this filter, picking the option that overlaps the prompt most chose the reference 93% of
  the time on `planning`.
- **Option count varies:** each question has 2 to 13 options, depending on how many distinct wrong answers
  the task allows. Yes/no tasks have 2 options; open-ended answers usually have 13.
- **Dropped questions:** a question is dropped when its reference does not score 1, or when no grounded wrong
  option exists. For that reason `knights_knaves` is nearly absent from `reasoning_gym`: mined answers name
  other people, and reasoning-gym has no near-miss generator.
- **Checked shortcuts:** picking the longest option, the shortest option, or the option with the most prompt
  overlap. Per task, these stay close to chance for that task's option count.

Build: `python scripts/build_procedural_choices.py --out <dir> --source {reasoning_core,reasoning_gym}`
(seed 0; 2 train shards of the source are sampled per config; tasks are balanced).

## Citation

```bibtex
@article{sileo2026reasoning,
  title={Reasoning Core: Designing Broad Procedural Data for Completion-Supervised Reasoning Training},
  author={Sileo, Damien and Lacombe, Valentin and Kachler, Dimitri},
  journal={arXiv preprint arXiv:2608.05148},
  year={2026},
  url={https://arxiv.org/abs/2608.05148}
}
```
