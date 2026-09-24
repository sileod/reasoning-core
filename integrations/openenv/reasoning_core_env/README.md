---
title: Reasoning Core Environment Server
emoji: 🧠
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
  - agent-environment
  - reasoning
  - reinforcement-learning
  - evaluation
  - symbolic-reasoning
---

# Reasoning Core Environment

An [OpenEnv](https://github.com/huggingface/openenv) environment for formally
verifiable symbolic reasoning across logic, mathematics, planning, syntax, and
related procedural domains.

Tasks come from
[`reasoning-core/formal-reasoning-env`](https://huggingface.co/datasets/reasoning-core/formal-reasoning-env)
and are scored by the task-specific evaluators in
[`reasoning-core`](https://github.com/sileod/reasoning_core).

## Use The Hosted Environment

```python
from reasoning_core_env import ReasoningCoreAction, ReasoningCoreEnv

with ReasoningCoreEnv(
    base_url="https://reasoning-core-reasoning-core-openenv.hf.space"
) as env:
    result = env.reset(split="train", seed=42, size=1000)
    print(result.observation.prompt)

    result = env.step(ReasoningCoreAction(answer="<answer>...</answer>"))
    print(result.reward)
```

Each episode has one action:

1. `reset()` returns a symbolic reasoning prompt.
2. `step(ReasoningCoreAction(answer=...))` scores the answer and ends the episode.

Plain answers and answers wrapped in `<answer>...</answer>` are accepted. Rewards
are task-specific scores in the range 0 to 1.

The environment only serves pre-generated examples from the Hugging Face
dataset. Rows whose task scorer is unavailable in the installed
`reasoning-core` version are skipped, preventing deprecated or unsupported task
types from reaching an episode.

## Local Development

```bash
uv sync
uv run openenv validate
uv run openenv build -t reasoning-core-openenv
```

Run without Docker:

```bash
uv run server
```

The service exposes the interactive UI at `/web`, API documentation at `/docs`,
health information at `/health`, and the persistent environment API at `/ws`.

## Citation

If you use this environment, cite the Reasoning Core paper:

```bibtex
@article{sileo2026reasoning,
  title={Reasoning Core: Designing Broad Procedural Data for Completion-Supervised Reasoning Training},
  author={Sileo, Damien and Lacombe, Valentin and Kachler, Dimitri},
  journal={arXiv preprint arXiv:2608.05148},
  year={2026},
  url={https://arxiv.org/abs/2608.05148}
}
```
