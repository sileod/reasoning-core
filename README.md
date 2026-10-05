# Reasoning Core ◉

**Procedural reasoning data for language-model pre-training, post-training, evaluation, and RL.**

Reasoning Core generates verifiable textual tasks across first-order logic, formal mathematics with Lean and TPTP, planning, algorithms, syntax, and more. Use it as a Python library, generate datasets at scale, or plug it into modern reinforcement-learning environments.

More than **10B tokens** of pre-generated data are available in the 🤗 [Reasoning Core dataset collection](https://huggingface.co/collections/reasoning-core/datasets).

Tasks target compact, canonical answers and expose task-native scorers—clean targets for supervised fine-tuning (SFT), with deterministic rewards for RL and evaluation. The public [training and influence API](docs/evaluation.md) provides reproducible paired baseline/treatment experiments. Follow the [task influence guide](docs/influence.md) to measure a new or changed task, and compare it with the [reference results](docs/results/influence.md).

## Quickstart

```bash
uv pip install "reasoning-core[gen]"   # generate and score
uv pip install reasoning-core          # score only, e.g. as an RL reward over the procedural pile
```

```python
from reasoning_core import get_task, score_answer

task = get_task("arithmetics")
example = task.generate_example()

print(example.prompt)
assert score_answer(example.answer, example) == 1
```

## Everyday workflows

Python 3.10+. From a checkout, use `python -m pip install -e '.[gen]'` or
`bash scripts/install_authoring.sh` for lightweight task authoring.

| I want to… | Start here |
|---|---|
| Find a task by capability | `python -m reasoning_core catalog 'graph' --all --json` |
| Generate examples | `python -m reasoning_core sample arithmetics --count 3 --output /tmp/rc-samples.jsonl` |
| Implement or validate a task | [Authoring guide](TASK_AUTHORING_GUIDE.md) |
| Evaluate a model or score predictions | [Evaluation recipes](docs/workflows.md#evaluate-a-model) |
| Measure task influence | [Runnable paired smoke](docs/workflows.md#run-a-paired-influence-smoke) |
| Propose and implement tasks with agents | [Task-search guide](reasoning_core/task_search/README.md) |

[Repository layout](docs/layout.md) explains package boundaries and compatibility.
[Workflow recipes](docs/workflows.md) cover prerequisites, commands, output files,
and local checks. Catalogue queries read source metadata without importing tasks.

## Representative example

[`function_manipulation`](GALLERY.md#function_manipulation) combines symbolic operations with short, exact answers:

**Prompt**

```text
Define h(x) = d/dx (1/x).
Compute h'(1).
The answer is a reduced rational number.
```

**Answer:** `2`

Browse all [55 task examples](GALLERY.md).

## Task catalogue

[GALLERY](https://github.com/sileod/reasoning-core/blob/main/GALLERY.md) (names link to gallery examples)

[`arithmetics`](GALLERY.md#arithmetics) · [`math_word_problem`](GALLERY.md#math_word_problem) · [`equation_system`](GALLERY.md#equation_system) · [`combinatorics_formula`](GALLERY.md#combinatorics_formula) · [`function_manipulation`](GALLERY.md#function_manipulation) · [`planar_geometry_relations`](GALLERY.md#planar_geometry_relations) · [`metamath_entailment`](GALLERY.md#metamath_entailment) · [`metamath_core_select`](GALLERY.md#metamath_core_select) · [`lambda_reduction`](GALLERY.md#lambda_reduction) · [`rewrite_system`](GALLERY.md#rewrite_system) · [`unification_entailment`](GALLERY.md#unification_entailment) · [`most_probable_evidence`](GALLERY.md#most_probable_evidence) · [`most_probable_outcome`](GALLERY.md#most_probable_outcome) · [`multistep_nli`](GALLERY.md#multistep_nli) · [`defeasible_nli`](GALLERY.md#defeasible_nli) · [`multistep_evidence_retrieval`](GALLERY.md#multistep_evidence_retrieval) · [`multistep_abduction`](GALLERY.md#multistep_abduction) · [`logic_qa`](GALLERY.md#logic_qa) · [`logic_derivation`](GALLERY.md#logic_derivation) · [`planning`](GALLERY.md#planning) · [`set_missing_element`](GALLERY.md#set_missing_element) · [`set_expression`](GALLERY.md#set_expression) · [`sequential_induction`](GALLERY.md#sequential_induction) · [`qualitative_reasoning`](GALLERY.md#qualitative_reasoning) · [`grid_navigation`](GALLERY.md#grid_navigation) · [`reference_tracking`](GALLERY.md#reference_tracking) · [`belief_tracking`](GALLERY.md#belief_tracking) · [`coreference`](GALLERY.md#coreference) · [`constraint_satisfaction`](GALLERY.md#constraint_satisfaction) · [`graph_pathfinding`](GALLERY.md#graph_pathfinding) · [`graph_successors`](GALLERY.md#graph_successors) · [`regex_following`](GALLERY.md#regex_following) · [`regex_reasoning`](GALLERY.md#regex_reasoning) · [`analogical_case_matching`](GALLERY.md#analogical_case_matching) · [`parsing_derivation`](GALLERY.md#parsing_derivation) · [`syntax_error_detection`](GALLERY.md#syntax_error_detection) · [`constrained_continuation`](GALLERY.md#constrained_continuation) · [`table_qa`](GALLERY.md#table_qa) · [`table_equivalence`](GALLERY.md#table_equivalence) · [`table_statistics`](GALLERY.md#table_statistics) · [`string_transduction`](GALLERY.md#string_transduction) · [`game_best_move`](GALLERY.md#game_best_move) · [`game_forced_win`](GALLERY.md#game_forced_win) · [`qualitative_causal_reasoning`](GALLERY.md#qualitative_causal_reasoning) · [`code_analysis`](GALLERY.md#code_analysis) · [`code_runnability`](GALLERY.md#code_runnability) · [`attribute_grammar`](GALLERY.md#attribute_grammar) · [`inverse_math`](GALLERY.md#inverse_math) · [`process_inversion`](GALLERY.md#process_inversion) · [`systems_trace`](GALLERY.md#systems_trace) · [`controlled_code_execution`](GALLERY.md#controlled_code_execution) · [`dynamic_programming`](GALLERY.md#dynamic_programming) · [`rule_switching`](GALLERY.md#rule_switching) · [`shift_reduce_parsing`](GALLERY.md#shift_reduce_parsing) · [`finite_automaton_execution`](GALLERY.md#finite_automaton_execution)


## Task authoring guidelines

A task authoring guide describes the interface and guidelines.  
[TASK_AUTHORING_GUIDE](https://github.com/sileod/reasoning-core/blob/main/TASK_AUTHORING_GUIDE.md)
[TASK_MUTATION_GUIDE](TASK_MUTATION_GUIDE.md)
[TRAINING_AND_INFLUENCE](docs/evaluation.md)
[TASK_INFLUENCE](docs/influence.md)

## Ecosystem and integrations

- **[Prime Intellect](https://app.primeintellect.ai/dashboard/environments)** — install Reasoning Core from the Environments Hub for evaluation and RL workflows.
- **[OpenReward](https://openreward.ai/dsileo/reasoning-core)** — run Reasoning Core as an OpenReward-compatible environment.
- **[OpenEnv](https://huggingface.co/spaces/reasoning-core/reasoning-core-openenv)** — explore the interactive Reasoning Core OpenEnv on Hugging Face Spaces.
- **[reasoning-gym](https://github.com/open-thought/reasoning-gym)** — mix Reasoning Core and reasoning-gym tasks through either library's interface.
- **[SynLogic](https://github.com/MiniMax-AI/SynLogic)** — generate SynLogic games through the same task API, backed by SynLogic's native verifiers.

See the [integration guide](INTEGRATIONS.md) for runnable examples.



## Generate datasets at scale

Go from a single example to large pre-training, post-training, and evaluation corpora with balanced difficulty, token budgets, and verifiable answers. The generation pipeline supports parallel workers, resumable jobs, JSONL shards, and postprocessing for Hugging Face Datasets. Start with the [sampling and collection recipe](docs/workflows.md#sample-data).


## Citation and paper

```bibtex
@article{sileo2026reasoning,
  title={Reasoning Core: Designing Broad Procedural Data for Completion-Supervised Reasoning Training},
  author={Sileo, Damien and Lacombe, Valentin and Kachler, Dimitri},
  journal={arXiv preprint arXiv:2608.05148},
  year={2026},
  url={https://arxiv.org/abs/2608.05148}
}
```
https://arxiv.org/abs/2608.05148  
Contact: damien.sileo@inria.fr
