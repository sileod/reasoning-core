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


# ------------------------------------------------------------------ scales --
# A protocol is not scale-free. The knob that does NOT travel is the learning rate: 1e-4 is right
# at 360M and DIVERGES at 1B -- measured, loss 0.68 -> 12.02 by step 2, and the run exits 0 leaving
# a damaged checkpoint, so nothing about the failure is loud. Every scale therefore names its own
# `std_lr`, and a protocol asks the scale for its rate rather than carrying one.
#
# `warm` is the checkpoint the 75-step protocols carry Adam moments out of. None means those
# protocols are simply unavailable at that scale until a warm-up has been run there -- not a
# preference, an absence.
SCALES = {
    "360M": {"model": "HuggingFaceTB/SmolLM2-360M",
             "revision": "f8027fd0eaeea54caa13c31d31b9fdc459c38b49",
             "std_lr": 1e-4, "batch_size": 4, "gradient_accumulation_steps": 2,
             "warm": "checkpoints/warm_33432f34c7cf_adam"},
    "1B":   {"model": "allenai/OLMo-1B-0724-hf",
             "revision": "d7cbab742d80589e714b1a2d7f838dcd21cbe143",
             # 2e-5, the rate its 54 shipped std cells were measured at. Not a preference: see above.
             "std_lr": 2e-5, "batch_size": 2, "gradient_accumulation_steps": 2,
             # Tuned 2026-09-09 over {5e-6, 1e-5, 2e-5} x 300 steps, seed 43. 1e-5 and 2e-5 end on
             # top of each other (loss 1.192 vs 1.194, min 0.420 vs 0.428) and BOTH hump at step 88
             # -- that hump is the seed-43 data order, not instability. The separator is the gradient
             # spike: 2e-5 hits grad_norm 66.5 at step 2, the early-step signature of the divergent
             # 1e-4; 1e-5 peaks at 37 late. So 1e-5, which is also exactly learning_rate("rg75","1B").
             # This dir carries optimizer.pt, so carry is satisfiable here -- seed 43 only; the
             # seed 44/45 1B warms predate carry and have no moments.
             "warm": "checkpoints/warm_1e323f8a24e1"},
}

# Both scales by default: a single-scale ranking is a claim about one model, and the ladder work
# showed rankings that are stable at 360M can fail to settle at 1B.
DEFAULT_SCALES = ("360M", "1B")


def learning_rate(protocol, scale):
    """The rate for this protocol AT THIS SCALE.

    The 75-step protocols run a constant rate behind a short ramp. Linear decay from peak p to 0
    over T steps integrates to p*T/2, so a constant p/2 matches the same total update budget -- the
    same derivation that produced 5e-5 against 360M's 1e-4 linear, applied per scale rather than
    frozen at one. Derived, not swept.
    """
    std_lr = SCALES[scale]["std_lr"]
    return std_lr if protocol == "std" else std_lr / 2


def available(protocol, scale):
    """(ok, reason). A protocol that carries moments needs a warm checkpoint at that scale."""
    if PROTOCOLS[protocol]["carry_optimizer_state"] and not SCALES[scale]["warm"]:
        return False, (f"{protocol} carries Adam moments and {scale} has no warm checkpoint; "
                       f"run the warm-up at {scale} first, or use --protocol std")
    return True, ""


# ------------------------------------------------------------------- bands --
# Difficulty bands: WHICH levels the auxiliary rows are drawn from. Transfer is not monotone in
# difficulty -- it peaks around mid saturation -- so one number pooled over the whole ladder averages
# across the shape it is trying to measure.
#
# The bands below are chosen so that a comparison isolates SPAN from COUNT. `0-1-2` and `0-2-4` both
# draw three levels, so they cost the same and see the same number of distinct difficulties; they
# differ only in how far up the ladder they reach. A band that changed both at once would confound
# "harder helps" with "more variety helps".
#
# A band needs nothing new in the arm engine: it is a row cache built at those levels, passed as its
# own collection. Each task x band therefore gets its own arm, its own cell column, and can be
# calibrated separately.
BANDS = {
    "0-4":   [0, 1, 2, 3, 4],   # the whole ladder -- the current default
    "0-1-2": [0, 1, 2],         # three levels, bottom of the ladder
    "0-2-4": [0, 2, 4],         # three levels, full span at stride 2
}
DEFAULT_BANDS = ("0-4",)
