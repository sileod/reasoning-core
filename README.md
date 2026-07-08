# Reasoning Core ◉


reasoning-core is a suite of textual procedural data generators for language model pre-training and post-training.
It is centered on expressive formal and algorithmic tasks, including full fledged first-order-logic, formal mathematics with Lean/TPTP, planning, and CFG syntax tasks.

We release pre-generated data scaled to more than 10B tokens  
🤗 [https://hf.co/collections/reasoning-core/datasets](https://huggingface.co/collections/reasoning-core/datasets)

# Standalone
```python
uv pip install reasoning-core

from reasoning_core import list_tasks, get_task, score_answer

T = get_task('arithmetics')
x = T.generate_example()
assert score_answer(x.answer, x)==1
```

# Task examples and task authoring guide
[GALLERY](https://github.com/sileod/reasoning-core/blob/main/GALLERY.md) (names link to gallery examples)  

[`arithmetics`](GALLERY.md#arithmetics) · [`math_word_problem`](GALLERY.md#math_word_problem) · [`equation_system`](GALLERY.md#equation_system) · [`lean_missing_proof_line_selection`](GALLERY.md#lean_missing_proof_line_selection) · [`lean_candidate_compilation`](GALLERY.md#lean_candidate_compilation) · [`planar_geometry_relations`](GALLERY.md#planar_geometry_relations) · [`metamath_entailment`](GALLERY.md#metamath_entailment) · [`metamath_core_select`](GALLERY.md#metamath_core_select) · [`lambda_reduction`](GALLERY.md#lambda_reduction) · [`rewrite_system`](GALLERY.md#rewrite_system) · [`mgu_implied_equality`](GALLERY.md#mgu_implied_equality) · [`most_probable_evidence`](GALLERY.md#most_probable_evidence) · [`most_probable_outcome`](GALLERY.md#most_probable_outcome) · [`logic_nli`](GALLERY.md#logic_nli) · [`logic_formalization`](GALLERY.md#logic_formalization) · [`multistep_nli`](GALLERY.md#multistep_nli) · [`defeasible_nli`](GALLERY.md#defeasible_nli) · [`multistep_evidence_retrieval`](GALLERY.md#multistep_evidence_retrieval) · [`multistep_abduction`](GALLERY.md#multistep_abduction) · [`logic_qa`](GALLERY.md#logic_qa) · [`planning`](GALLERY.md#planning) · [`set_missing_element`](GALLERY.md#set_missing_element) · [`set_expression`](GALLERY.md#set_expression) · [`sequential_induction`](GALLERY.md#sequential_induction) · [`qualitative_reasoning`](GALLERY.md#qualitative_reasoning) · [`navigation`](GALLERY.md#navigation) · [`reference_tracking`](GALLERY.md#reference_tracking) · [`coreference`](GALLERY.md#coreference) · [`constraint_satisfaction`](GALLERY.md#constraint_satisfaction) · [`graph_pathfinding`](GALLERY.md#graph_pathfinding) · [`graph_successors`](GALLERY.md#graph_successors) · [`graph_dependencies`](GALLERY.md#graph_dependencies) · [`regex_following`](GALLERY.md#regex_following) · [`regex_reasoning`](GALLERY.md#regex_reasoning) · [`analogical_case_retrieval`](GALLERY.md#analogical_case_retrieval) · [`parsing_derivation`](GALLERY.md#parsing_derivation) · [`locate_error`](GALLERY.md#locate_error) · [`constrained_continuation`](GALLERY.md#constrained_continuation) · [`table_qa`](GALLERY.md#table_qa) · [`table_equivalence`](GALLERY.md#table_equivalence) · [`table_statistics`](GALLERY.md#table_statistics) · [`string_transduction`](GALLERY.md#string_transduction) · [`code_runnability`](GALLERY.md#code_runnability) · [`code_execution`](GALLERY.md#code_execution) · [`game_best_move`](GALLERY.md#game_best_move) · [`game_forced_win`](GALLERY.md#game_forced_win) · [`theory_of_mind`](GALLERY.md#theory_of_mind) · [`code_analysis`](GALLERY.md#code_analysis) · [`qualitative_causal`](GALLERY.md#qualitative_causal) · [`program_synthesis`](GALLERY.md#program_synthesis)

[TASK_AUTHORING_GUIDE](https://github.com/sileod/reasoning-core/blob/main/TASK_AUTHORING_GUIDE.md)


# Parallel generation script
Run `bash run_generate.sh` for multi-threaded generation to json files (readable by Huggingface Datasets).


# Integrations

### Prime Environment Hub
```python
#!pip install uv #install uv if needed
!uv tool install prime --with openai  -q
!uv tool run prime -- env install sileod/reasoning-core-env

from verifiers import load_environment
import os; from openai import OpenAI

env = load_environment("reasoning-core-env")

client = OpenAI( base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY")) #🔑
results = env.evaluate(client=client, model="gpt-4.1-mini", num_examples=20, rollouts_per_example=1)
df=env.make_dataset(results).to_pandas()
```
### Reasoning gym

We use a custom interface but compatible interface. Our tasks, which are mostly orthogonal to RG, can be imported in it.
```python
import reasoning_gym, reasoning_core
from reasoning_gym.composite import DatasetSpec

reasoning_core.register_to_reasoning_gym() # registers RC tasks into RG

specs = [
    DatasetSpec(name='leg_counting', weight=1, config={}),  #from reasoning_gym 🏋
    DatasetSpec(name='arithmetics', weight=1, config={}),  #from reasoning_core ◉
]
D=reasoning_gym.create_dataset('composite', size=10, seed=42, datasets=specs)
```

And the other way around:
```python
from reasoning_core import get_task
t=get_task('reasoning_gym')
t.generate_example(level=1, rg_task='lcm') #or unspecified for random task
```
### Openreward
https://openreward.ai/dsileo/reasoning-core

## Citation and paper
```bibtex
@article{reasoningcore2026,
  title={Reasoning Core: A Scalable Procedural Data Generation Suite for Symbolic Pre-training and Post-Training},
  author={Lacombe, Valentin and Quesnel, Valentin and Sileo, Damien},
  journal={arXiv preprint arXiv:2603.02208},
  year={2026},
  url={https://arxiv.org/abs/2603.02208}
}
```
https://arxiv.org/abs/2603.02208  
Contact: damien.sileo@inria.fr
