# Reasoning Core ◉


reasoning-core is a suite of textual procedural data generators for language model pre-training and post-training.
It is centered on expressive formal and algorithmic tasks, including full fledged first-order-logic, formal mathematics with Lean/TPTP, planning, and CFG syntax tasks.

We release pre-generated data scaled to more than 10B tokens  
🤗 [https://hf.co/collections/reasoning-core/datasets](https://huggingface.co/collections/reasoning-core/datasets)

# Standalone
```python
uv pip install reasoning-core

from reasoning_core import list_tasks, get_task, score_answer

T = get_task('arithmetics')()
x = T.generate_example()
assert score_answer(x.answer, x)==1
```

# Task examples and task authoring guide
[GALLERY](https://github.com/sileod/reasoning-core/blob/main/GALLERY.md) (names link to task code)  

[`metamath_entailment`](#metamath_entailment) · [`metamath_core_select`](#metamath_core_select) · [`string_transduction`](#string_transduction) · [`constraint_satisfaction`](#constraint_satisfaction) · [`qualitative_reasoning`](#qualitative_reasoning) · [`lambda_reduction`](#lambda_reduction) · [`rewrite_system`](#rewrite_system) · [`planning`](#planning) · [`table_qa`](#table_qa) · [`multistep_nli`](#multistep_nli) · [`multistep_evidence_retrieval`](#multistep_evidence_retrieval) · [`multistep_abduction`](#multistep_abduction) · [`logic_qa`](#logic_qa) · [`equation_system`](#equation_system) · [`logic_nli`](#logic_nli) · [`evidence_retrieval`](#evidence_retrieval) · [`game_best_move`](#game_best_move) · [`game_forced_win`](#game_forced_win) · [`navigation`](#navigation) · [`graph_pathfinding`](#graph_pathfinding) · [`graph_successors`](#graph_successors) · [`graph_dependencies`](#graph_dependencies) · [`code_runnability`](#code_runnability) · [`code_execution`](#code_execution) · [`code_input_deduction`](#code_input_deduction) · [`most_probable_evidence`](#most_probable_evidence) · [`most_probable_outcome`](#most_probable_outcome) · [`coreference`](#coreference) · [`arithmetics`](#arithmetics) · [`math_word_problem`](#math_word_problem) · [`sequential_induction`](#sequential_induction) · [`conjecture_entailment`](#conjecture_entailment) · [`tptp_consistency_repair`](#tptp_consistency_repair) · [`planar_geometry_relations`](#planar_geometry_relations) · [`regex_following`](#regex_following) · [`regex_induction`](#regex_induction) · [`regex_reasoning`](#regex_reasoning) · [`analogical_case_retrieval`](#analogical_case_retrieval) · [`parsing_derivation`](#parsing_derivation) · [`locate_error`](#locate_error) · [`constrained_continuation`](#constrained_continuation) · [`stress_constrained_continuation`](#stress_constrained_continuation) · [`lean_missing_proof_line_selection`](#lean_missing_proof_line_selection) · [`lean_candidate_compilation`](#lean_candidate_compilation) · [`reference_tracking`](#reference_tracking) · [`set_missing_element`](#set_missing_element) · [`count_elements`](#count_elements) · [`set_expression`](#set_expression)

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
