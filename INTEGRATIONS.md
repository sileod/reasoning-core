# Reasoning Core integrations

[Back to the README](README.md)

## Environments and status

Every RL environment serves [`reasoning-core/procedural-pile`](https://huggingface.co/datasets/reasoning-core/procedural-pile)
and scores with `reasoning-core>=0.5.0`. `python scripts/check_rl_envs.py` re-checks them in fresh
venvs ([how](docs/workflows.md#check-the-rl-environments)); the last check (2026-10-02, pile
`1ad09cb`, 300 rows per split) found gold answers earn 1, wrong ones 0, and one seed serves the
same rows twice.

| Environment | Where | Version | Hosted check |
|---|---|---|---|
| Prime Intellect (verifiers) | [hub](https://app.primeintellect.ai/dashboard/environments/reasoning-core/reasoning-core-env), source in [integrations/primeintellect](integrations/primeintellect/) | 1.0.7 | installs and loads on verifiers 0.3.1; gpt-4.1-mini reward 0.78 |
| OpenEnv | [HF Space](https://huggingface.co/spaces/reasoning-core/reasoning-core-openenv), source in [integrations/openenv](integrations/openenv/) | 0.2.0 | Space episodes: gold 1, wrong 0 |
| OpenReward | [openreward.ai](https://openreward.ai/dsileo/reasoning-core), source in [sileod/reasoning-core-openreward](https://github.com/sileod/reasoning-core-openreward) (deploys on push) | `95d724b` | Hosted sessions: gold 1, wrong 0, 51 tasks in train |
| reasoning-gym, our tasks in it | `register_to_reasoning_gym()` | — | all 55 roster tasks generate and score |
| reasoning-gym and SynLogic, theirs in ours | `get_task("reasoning_gym")`, `get_task("synlogic")` | — | upstream issues, below |

Known upstream issues, not fixed here: in reasoning-gym, gold answers score below 1 on
`arc_agi`, `boxnet`, `graph_color`, `jugs`, `propositional_logic`, `rearc`, `rubiks_cube`,
`rush_hour` and `word_ladder`; `game_of_life_halting` rewards garbage; and the `caesar_cipher`
curriculum asserts. Three SynLogic games produce no concrete answer.

## Prime Intellect Environments Hub

Install the Reasoning Core environment and evaluate a model with Prime Intellect:

```python
#!pip install uv  # Install uv if needed.
!uv tool install prime -q
!uv tool run prime -- env install reasoning-core/reasoning-core-env

import verifiers as vf

env = vf.load_environment("reasoning-core-env")
client = vf.ClientConfig(api_base_url="https://openrouter.ai/api/v1", api_key_var="OPENROUTER_API_KEY")
results = env.evaluate_sync(client=client, model="openai/gpt-4.1-mini", num_examples=20)
print(sum(o["reward"] for o in results["outputs"]) / len(results["outputs"]))
```

## reasoning-gym

Reasoning Core tasks can be registered in reasoning-gym and mixed with its native tasks:

```python
import reasoning_core
import reasoning_gym
from reasoning_gym.composite import DatasetSpec

reasoning_core.register_to_reasoning_gym()

specs = [
    DatasetSpec(name="leg_counting", weight=1, config={}),  # reasoning-gym
    DatasetSpec(name="arithmetics", weight=1, config={}),  # Reasoning Core
]
dataset = reasoning_gym.create_dataset(
    "composite",
    size=10,
    seed=42,
    datasets=specs,
)
```

Reasoning-gym tasks can also be generated through Reasoning Core:

```python
from reasoning_core import get_task

task = get_task("reasoning_gym")
example = task.generate_example(level=1, rg_task="lcm")
```

Omit `rg_task` to sample a random reasoning-gym task.

## Source layout

Python adapters live in [reasoning_core/integrations/](reasoning_core/integrations/README.md).
Standalone OpenEnv and Prime Intellect distributions live in
[integrations/](integrations/README.md), outside the core wheel.
