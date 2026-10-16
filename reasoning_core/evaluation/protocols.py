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
# rg75 from 2026-09-27: v8_tiny with ts_dpo replaced by the four tasksource legs. Every other leg is
# byte-identical, so ext (which excludes the tasksource legs) pools across the two.
_TINY11 = "reasoning_core/resources/batteries/copyfree_battery_v11_tiny.json"
# rg75 from 2026-09-29: v11_tiny minus uf_short, tulu3_short, ultramix_short (SNR < 1, 23% of eval
# tokens). Every remaining leg is byte-identical, so ext pools across v8, v11 and v12.
_TINY12 = "reasoning_core/resources/batteries/copyfree_battery_v12_tiny.json"
_FULL = "reasoning_core/resources/batteries/copyfree_battery_v8.json"
# The paper roster (2026-10-16): menu-free legs with free-text options, split into dev and test groups.
_TINY13 = "reasoning_core/resources/batteries/copyfree_battery_v13_tiny.json"

PROTOCOLS = {
    "rg75": {"main": "fwdolcirg", "steps": 75, "mix": 0.5, "learning_rate": 5e-5,
             "lr_scheduler_type": "constant_with_warmup", "warmup_steps": 4,
             "carry_optimizer_state": True, "max_length": 1024, "batch_size": 4,
             "gradient_accumulation_steps": 2, "token_ratio": True, "eval_manifest": _TINY12},
    # rg75 with the plain fw+dolci background. This one existed and was USED long before it had a
    # name -- the Influence Atlas and the contrast atlas are both built on it -- and being unnamed
    # is exactly how it gets mistaken for rg75, which it matches on every knob but the background.
    "carry": {"main": "fwdolci", "steps": 75, "mix": 0.5, "learning_rate": 5e-5,
              "lr_scheduler_type": "constant_with_warmup", "warmup_steps": 4,
              "carry_optimizer_state": True, "max_length": 1024, "batch_size": 4,
              "gradient_accumulation_steps": 2, "token_ratio": True, "eval_manifest": _TINY},
    # rg75 scored on the paper roster instead of v12_tiny. Every training knob is rg75's, so an
    # rg75v13 cell differs from an rg75 cell only in what it is evaluated on.
    "rg75v13": {"main": "fwdolcirg", "steps": 75, "mix": 0.5, "learning_rate": 5e-5,
                "lr_scheduler_type": "constant_with_warmup", "warmup_steps": 4,
                "carry_optimizer_state": True, "max_length": 1024, "batch_size": 4,
                "gradient_accumulation_steps": 2, "token_ratio": True, "eval_manifest": _TINY13},
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
# rg75v13 is rg75's training with a smaller battery (1,056 items vs ~6,300 sequences): an ESTIMATE until measured.
ARM_SECONDS = {"rg75": 917, "carry": 917, "std": 2228, "rg75v13": 800}

# The battery identities these protocols record, at max_length 1024. max_length is hashed into a
# battery identifier, so the same manifest at 512 is a DIFFERENT battery; every shipped result is
# at 1024.
BATTERY_IDS = {"rg75": "copyfree_battery_v12_tiny/battery@v1:14f00ecfceba",
               "carry": "copyfree_battery_v8_tiny/battery@v1:c94e9ad44be0",
               "std":  "copyfree_battery_v8/battery@v1:1a482a2aeb5d",
               "rg75v13": "copyfree_battery_v13_tiny/battery@v1:8721e42db0ed"}

# Protocols whose coverage is keyed on the battery as well as (checkpoint, rate): an arm counts only if
# it was scored on THIS battery. rg75 is left unkeyed on purpose -- its coverage spans the v8/v11/v12
# tiny batteries and keying it now would re-owe every task measured before v12.
BATTERY_KEYED = {"rg75v13"}

# The same battery scored through the chat template, for scales with chat_template set (instruct
# models). Only a battery-keyed protocol has one: a chat cell must never count as raw coverage.
CHAT_BATTERY_IDS = {"rg75v13": "copyfree_battery_v13_tiny_chat/battery@v1:c1d446a84e93"}

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
             "std_lr": 2e-5, "tail_lr": 5e-6, "batch_size": 2, "gradient_accumulation_steps": 2,
             # Tuned 2026-09-09 over {5e-6, 1e-5, 2e-5} x 300 steps, seed 43. 1e-5 and 2e-5 end on
             # top of each other (loss 1.192 vs 1.194, min 0.420 vs 0.428) and BOTH hump at step 88
             # -- that hump is the seed-43 data order, not instability. The separator is the gradient
             # spike: 2e-5 hits grad_norm 66.5 at step 2, the early-step signature of the divergent
             # 1e-4; 1e-5 peaks at 37 late. So 1e-5, which is also exactly learning_rate("rg75","1B").
             # This dir carries optimizer.pt, so carry is satisfiable here -- seed 43 only; the
             # seed 44/45 1B warms predate carry and have no moments.
             "warm": "checkpoints/warm_1e323f8a24e1"},
    # Scale-up scales (2026-10-16). Warmed with the 360M recipe -- fwdolci + rgA 22de0e25573f @0.10,
    # 300 steps, seed 43, optimizer saved -- at warm LR 1e-5 and effective batch 8 (BS2 GA4, as at
    # 360M). tail_lr is NOT measured here: std_lr/2 gives 5e-6, which is what the 1B sweep measured
    # for OLMo-1B, but no sweep has been run at these models.
    # Instruct at 360M, scored through its chat template (the _chat battery); trained on the same
    # raw-format rows as every other scale. Warmed with the 360M recipe, so it takes 360M's rates.
    "360Mi": {"model": "HuggingFaceTB/SmolLM2-360M-Instruct",
              "revision": "a10cc1512eabd3dde888204e902eca88bddb4951",
              "std_lr": 1e-4, "batch_size": 4, "gradient_accumulation_steps": 2,
              "warm": "checkpoints/warm_6cde1ec171b7_adam", "chat_template": True},
    "OLMo2": {"model": "allenai/OLMo-2-0425-1B",
              "revision": "a1847dff35000b4271fa70afc5db10fd29fedbdf",
              "std_lr": 1e-5, "batch_size": 2, "gradient_accumulation_steps": 4,
              "warm": "checkpoints/warm_4284e38c6195_adam"},
}

# Both scales by default: a single-scale ranking is a claim about one model, and the ladder work
# showed rankings that are stable at 360M can fail to settle at 1B.
DEFAULT_SCALES = ("360M", "1B")


def learning_rate(protocol, scale):
    """The rate for this protocol AT THIS SCALE: measured where a sweep exists, derived otherwise.

    The derivation: the 75-step protocols run a constant rate behind a short ramp, and linear decay
    from peak p to 0 over T steps integrates to p*T/2, so a constant p/2 matches the same total
    update budget. That is where 360M's 5e-5 comes from, and 336 measured cells corroborate it --
    they average +14.6 external gain against a main-mixture tax of +0.4, i.e. essentially no
    displacement.

    At 1B the same derivation gives 1e-5 and is WRONG, measured 2026-09-15 on the two anchor tasks.
    The anchor pool is fixed, so the same two tasks at five rates differ only by the rate -- no draw
    noise, no task selection:

        LR      metamath_core_select    program_synthesis   main tax (mean of the two)
        2e-6         +17.81                  +3.95              +0.18
        5e-6         +17.90                  +1.34              -1.26
        1e-5         +12.62                  -2.22              -3.14   <- the derived value
        2e-5          -5.94                 -45.67              -4.07
        5e-5        -108.29                 (+11.46 at tax -17.70, an arm that blew up)

    Degradation is monotone from 5e-6 up, which is why the first 25 1B cells came back mostly
    negative and looked like a scale inversion of the 360M ranking. It is not: it is this.

    5e-6 rather than 2e-6 because the pair PLATEAUS between them (+17.90 vs +17.81 on the anchor
    that carries signal) rather than continuing to climb, so the low end is not simply washing the
    measurement out toward zero -- and 5e-6 keeps the wider anchor spread (16.6 vs 13.9, against
    12.2 for the 360M reference), which is the thing a per-task ranking actually spends.

    A scale with a `tail_lr` has been swept; one without it is running the derivation.
    """
    if protocol == "std":
        return SCALES[scale]["std_lr"]
    measured = SCALES[scale].get("tail_lr")
    return measured if measured is not None else SCALES[scale]["std_lr"] / 2


def eval_manifest(protocol, scale):
    """The battery manifest this protocol is scored on at this scale: the _chat sibling for chat scales."""
    path = PROTOCOLS[protocol]["eval_manifest"]
    return path.replace(".json", "_chat.json") if SCALES[scale].get("chat_template") else path


def battery_id(protocol, scale):
    """The battery id an arm of this protocol carries at this scale, or None if not battery-keyed."""
    if protocol not in BATTERY_KEYED:
        return None
    return CHAT_BATTERY_IDS[protocol] if SCALES[scale].get("chat_template") else BATTERY_IDS[protocol]


def available(protocol, scale):
    """(ok, reason). A protocol that carries moments needs a warm checkpoint at that scale."""
    if SCALES[scale].get("chat_template") and protocol not in CHAT_BATTERY_IDS:
        return False, f"{scale} is scored through its chat template and {protocol} has no chat battery"
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
    # Single levels, for per-difficulty transfer (does training on hard instances transfer better?).
    # Write their cells OUTSIDE per_task_results/ (--results-subdir): measured_ext reads that
    # directory as the canonical 0-4 score, and a one-level arm is a different question.
    "0": [0], "1": [1], "4": [4], "6": [6],
}
DEFAULT_BANDS = ("0-4",)
