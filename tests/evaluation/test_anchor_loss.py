"""Ambient SFT anchor: identity, the matching loss, and an end-to-end arm on a tiny model."""

from collections import defaultdict
from dataclasses import replace
from types import SimpleNamespace

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("trl")

from datasets import Dataset  # noqa: E402
from tokenizers import Tokenizer, models, pre_tokenizers  # noqa: E402
from transformers import GPT2Config, GPT2LMHeadModel, PreTrainedTokenizerFast  # noqa: E402

from reasoning_core.evaluation.training.arm import ArmSpec, run_arm  # noqa: E402

BASE = dict(initialization_id="sha256:init", main_data_id="sha256:main")


def test_anchor_fields_leave_existing_identities_alone():
    spec = ArmSpec("e", "a", **BASE)
    assert spec.spec_id == replace(spec, anchor_temperature=None, anchor_prob=0.0).spec_id
    assert spec.spec_id != replace(spec, anchor_temperature=2.5, anchor_prob=0.25).spec_id
    with pytest.raises(ValueError):
        replace(spec, anchor_temperature=2.5)
    with pytest.raises(ValueError):
        replace(spec, anchor_prob=0.25)


def _tiny():
    words = ["[UNK]", "[PAD]", "[EOS]", "value", "0", "1", "2", "3"]
    backend = Tokenizer(models.WordLevel(dict(zip(words, range(len(words)))), unk_token="[UNK]"))
    backend.pre_tokenizer = pre_tokenizers.WhitespaceSplit()
    tok = PreTrainedTokenizerFast(tokenizer_object=backend, unk_token="[UNK]",
                                  pad_token="[PAD]", eos_token="[EOS]")
    torch.manual_seed(0)
    model = GPT2LMHeadModel(GPT2Config(vocab_size=len(words), n_positions=32, n_embd=16, n_layer=1,
                                       n_head=1, resid_pdrop=0.0, embd_pdrop=0.0,
                                       attn_pdrop=0.0, eos_token_id=2, bos_token_id=2, pad_token_id=1))
    return model, tok


def test_anchored_arm_trains_logs_kl_and_leaves_the_start_frozen(tmp_path, monkeypatch):
    import reasoning_core.evaluation.training.arm as arm
    monkeypatch.setattr(arm, "RUNS_HOME", tmp_path)
    monkeypatch.setattr(arm, "home_path", lambda path, **_: path)
    model, tok = _tiny()
    start = {k: v.clone() for k, v in model.state_dict().items()}
    rows = [{"prompt": f"value {n} ", "completion": f"{n} [EOS]"} for n in (0, 1, 2, 3)] * 4
    spec = ArmSpec("anchor-test", "a", optimizer="adamw_torch", learning_rate=0.05, max_steps=6,
                   batch_size=2, gradient_accumulation_steps=2, max_length=32, packing=False,
                   formatter="smoke_text_v1", anchor_temperature=2.5, anchor_prob=0.5, **BASE)
    trainer, metrics = run_arm(model, tok, Dataset.from_list(rows), spec)
    assert metrics["global_step"] == 6
    anchor_steps = [s for s in range(6) if _draw(trainer, s)]
    assert 0 < len(anchor_steps) < 6  # p=0.5 under the fixed (seed, step) draw
    logged = [row["anchor/kl"] for row in trainer.state.log_history if "anchor/kl" in row]
    assert logged and all(kl >= 0 for kl in logged)
    for name, tensor in trainer.anchor.state_dict().items():
        assert torch.equal(tensor, start[name]), name
    assert not all(torch.equal(v, start[k]) for k, v in model.state_dict().items())


def _draw(trainer, step):
    from reasoning_core.evaluation.training.arm import AnchorLossMixin
    fake = SimpleNamespace(args=trainer.args, anchor_prob=trainer.anchor_prob,
                           state=SimpleNamespace(global_step=step))
    return AnchorLossMixin._anchor_step(fake)


def test_matching_loss_is_zero_against_itself_and_positive_after_drift():
    from reasoning_core.evaluation.training.arm import AnchorLossMixin, _frozen_copy

    model, _ = _tiny()
    holder = type("H", (AnchorLossMixin,), {"__init__": lambda self: None})()
    holder.anchor, holder.anchor_temperature, holder.anchor_prob = _frozen_copy(model), 2.5, 0.999
    holder.args = type("A", (), {"seed": 0})()
    holder.state = type("S", (), {"global_step": 0})()
    holder.model_accepts_loss_kwargs = False
    holder._metrics = {"train": defaultdict(list)}
    ids = torch.tensor([[3, 4, 2, 3, 5, 2]])
    labels = torch.tensor([[-100, 4, 2, -100, 5, 2]])
    model.train()
    loss = holder.compute_loss(model, {"input_ids": ids, "labels": labels})
    assert loss.item() == pytest.approx(0.0, abs=1e-6)
    with torch.no_grad():
        model.lm_head.weight.add_(torch.randn_like(model.lm_head.weight))
    loss = holder.compute_loss(model, {"input_ids": ids, "labels": labels})
    assert loss.item() > 0
    loss.backward()
    assert model.lm_head.weight.grad.abs().sum() > 0
