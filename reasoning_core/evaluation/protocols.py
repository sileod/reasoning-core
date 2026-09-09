"""Named influence protocols: the knob bundles a run is measured under.

ONE definition, imported by both the runner that applies it (`task_diagnostics.collection_influence`)
and the report that displays it (`reasoning_core.reports.protocol_card`). It used to be spelled out
in each, which is how a "same protocol" claim quietly stops being true.

`rg75` is the house default. It is the fast one, and the difference is almost entirely eval: the
full battery is about 69% of an arm's wall clock against the tiny battery's 24%.

`rg75` is legal for everything EXCEPT a comparison against reasoning-gym. Its background mixture is
`fwdolcirg`, which already contains reasoning-gym, so an rg arm measured on rg75 is scored against a
background containing itself and "rg helps" is true by construction. Measure rg on `std`.

A protocol is not a preference where the init forbids it: `rg75` carries Adam moments out of a warm
checkpoint, so a job training from a cold base cannot use it at all and must pin `std`.
"""
from __future__ import annotations

_TINY = "reasoning_core/resources/batteries/copyfree_battery_v8_tiny.json"
_FULL = "reasoning_core/resources/batteries/copyfree_battery_v8.json"

PROTOCOLS = {
    "rg75": {"main": "fwdolcirg", "steps": 75, "mix": 0.5, "learning_rate": 5e-5,
             "lr_scheduler_type": "constant_with_warmup", "warmup_steps": 4,
             "carry_optimizer_state": True, "max_length": 1024, "batch_size": 4,
             "gradient_accumulation_steps": 2, "token_ratio": True, "eval_manifest": _TINY},
    # rg75 with the plain fw+dolci background. This one existed and was USED long before it had a
    # name -- the Influence Atlas and the contrast atlas are both built on it -- and being unnamed
    # is exactly how it gets mistaken for rg75, which it matches on every knob but the background.
    "carry": {"main": "fwdolci", "steps": 75, "mix": 0.5, "learning_rate": 5e-5,
              "lr_scheduler_type": "constant_with_warmup", "warmup_steps": 4,
              "carry_optimizer_state": True, "max_length": 1024, "batch_size": 4,
              "gradient_accumulation_steps": 2, "token_ratio": True, "eval_manifest": _TINY},
    "std":  {"main": "fwdolci", "steps": 300, "mix": 0.2, "learning_rate": 1e-4,
             "lr_scheduler_type": "linear", "warmup_steps": 0,
             "carry_optimizer_state": False, "max_length": 1024, "batch_size": 4,
             "gradient_accumulation_steps": 2, "token_ratio": True, "eval_manifest": _FULL},
}

# Seconds per arm, MEASURED same-node and back to back in one job (4092169), which is the only
# sound comparison: an arm record carries no host, so cross-arm timings otherwise compare GPUs
# rather than batteries -- the same tiny battery spans 120s to 947s per arm on different nodes.
# Consecutive completed arms in that job: std 2225s and 2231s, rg75 916s and 918s.
# `carry` shares rg75's steps and battery, which is what the cost is made of, so it shares the
# measurement; the background mixture does not change how long an arm takes.
ARM_SECONDS = {"rg75": 917, "carry": 917, "std": 2228}

# The battery identities these protocols record, at max_length 1024. max_length is hashed into a
# battery identifier, so the same manifest at 512 is a DIFFERENT battery; every shipped result is
# at 1024.
BATTERY_IDS = {"rg75": "copyfree_battery_v8_tiny/battery@v1:c94e9ad44be0",
               "carry": "copyfree_battery_v8_tiny/battery@v1:c94e9ad44be0",
               "std":  "copyfree_battery_v8/battery@v1:1a482a2aeb5d"}

DEFAULT = "rg75"
