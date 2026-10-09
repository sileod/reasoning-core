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
| `reasoning_core` (default) | [procedural-pretraining-pile](https://huggingface.co/datasets/reasoning-core/procedural-pretraining-pile) @ `rc14` | 54 | 49,092 | 4,909 |
| `reasoning_gym` | [reasoning-gym](https://huggingface.co/datasets/reasoning-core/reasoning-gym) @ `531e215` | 68 | 47,073 | 4,581 |

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
- `id`: a stable row id, unique within each config: the source row's deduplication key for `reasoning_core`, and a hash of task and prompt for `reasoning_gym`.

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
  option exists. In `reasoning_gym` this empties some tasks entirely:
  - the stored answer never scores 1 under reasoning-gym's own scorer: `arc_agi`, `graph_color`,
    `propositional_logic`, `rearc`, `rubiks_cube`, `rush_hour`;
  - answers that rearrange the prompt's own words leave no grounded mined option: `group_anagrams`,
    `number_sorting`, `word_sorting`.
- **Shortcut gate:** three solver-free rules are checked per task: pick the longest option, the shortest, or
  the one with the most prompt overlap. A task is dropped whole when the best rule beats chance
  (1 / number of options) by more than 0.25 on its train rows. Mined options can still differ from the reference
  in scale or vocabulary: in `word_ladder`, only the reference starts and ends with the prompt's words.
  - dropped from `reasoning_core`: `constrained_continuation`;
  - dropped from `reasoning_gym`: `knights_knaves`, `number_format`, `puzzle24`, `word_ladder`.

  Among the kept tasks, the best rule beats chance by a median of about 0.01–0.02. The largest remaining excess
  is `regex_reasoning` (0.39 vs 0.18). Per-task values are in each config's `build_stats.json`.
- **No train/test overlap, no repeats:** test rows whose prompt also occurs in train are dropped, and so are repeated prompts within a split (the reasoning-gym pool repeats prompts in tasks with few instances, such as `tower_of_hanoi`).
- **Excluded reasoning-gym generators:** the semantic audit in the Reasoning Core paper (Appendix G) found 13
  generators with wrong scorers, wrong labels or prompt–oracle mismatches. These are left out: `game_of_life_halting`,
  `intermediate_integration`, `boxnet`, `tsumego`, `mahjong_puzzle`, `syllogism`, `family_relationships`,
  `calendar_arithmetic`, `time_intervals`, `aiw`, `simple_geometry`, `rectangle_count`, `power_function`. Also left
  out are generators whose gold answer is one sampled solution among several valid ones, because another valid
  answer could then appear as a wrong option: `codeio`, `needle_haystack`, `sentence_reordering`, `letter_jumble`,
  `caesar_cipher` (`survo` is not in the source pool).

Build: `python scripts/build_procedural_choices.py --out <dir> --source {reasoning_core,reasoning_gym}`
(seed 0; 2 train shards of the source are sampled per config; tasks are balanced; `reasoning_gym` is built with
`--n 59616 --test-n 5994`, a per-task quota that offsets the tasks dropped above).

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
