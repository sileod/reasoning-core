"""Encoder valuation: the value of a task for a cross-encoder, read on a battery's MCQ legs.

Same estimand as the decoder arms -- arm minus baseline under one recipe -- with a cross-encoder in
place of the language model. Every item is (prompt, choices, gold) and training is a softmax over the
choices' logits, so the battery's MCQ legs score the model directly (cost = -logit) and need no change.

    baseline: tasksource_dpo_pairs (prompt, [chosen, rejected])
    arm:      the same stream, with a share `mix` of the task's rows; negatives are other answers of the
              same task at the same level, so they are in-format and cannot be told apart by surface

Inits: `encoder` (raw Ettin encoder, fresh 1-logit head), `reranker` (Ettin reranker, already a pair
scorer), `decider` (the reranker fine-tuned on typed choices), or a local dir saved by `warm`.

    python -m reasoning_core.evaluation.encoder warm  --init encoder --steps 2000 --out ckpt/
    python -m reasoning_core.evaluation.encoder value --init ckpt/ --rows task_rows/<cid> --out cell.json
"""
import argparse
import collections
import glob
import json
import random
from pathlib import Path

import torch
import torch.nn.functional as F

from .battery import load_battery_manifest
from .metrics import load_eval_suite, score_mcq

INITS = {"encoder": ("jhu-clsp/ettin-encoder-150m", "45d08642849e5c5701b162671ac811b7654bfd9f"),
         "reranker": ("cross-encoder/ettin-reranker-150m-v1", "025501c4e0f9bbeb4c5b198318e0089ff061cc14"),
         "decider": ("tasksource/tasksource-decider-nano", "2c7c01ffe5aba74dd15968cf38b0fdc83d1f3810")}
DPO = ("tasksource/tasksource_dpo_pairs", "0b16d8574d3fc771320a32eab85ae405ea86207c")
VERSION = 1


def dpo_items(n, seed=0):
    from reasoning_core.utils.hf_sample import sample_rows
    rows = sample_rows(*DPO, n=n, seed=seed, columns=["prompt", "chosen", "rejected"])
    return [(r["prompt"], (r["chosen"], r["rejected"]), 0) for r in rows if r["chosen"] != r["rejected"]]


def task_items(rows, negatives, seed=0, policy="random"):
    """{task: [(prompt, choices, gold)]}; choices = gold plus up to `negatives` verified-wrong answers drawn
    by a distractors policy from the same task and level. Rows with no negative are dropped."""
    from .distractors import negatives as draw
    rng, pools = random.Random(seed), collections.defaultdict(set)
    for r in rows:
        pools[r["task"], r["level"]].add(r["answer"])
    out = collections.defaultdict(list)
    for i, r in enumerate(rows):
        negs = draw(r, sorted(pools[r["task"], r["level"]]), negatives, policy, seed=seed * 100003 + i)
        if negs:
            choices = [r["answer"], *negs]
            rng.shuffle(choices)
            out[r["task"]].append((r["prompt"], tuple(choices), choices.index(r["answer"])))
    return dict(out)


def load_rows(path):
    import pyarrow.parquet as pq
    files = sorted(glob.glob(str(Path(path) / "data" / "*.parquet")))
    return [r for f in files for r in pq.read_table(f, columns=["task", "level", "prompt", "answer", "metadata"]).to_pylist()]


class PairScorer(torch.nn.Module):
    """Backbone + pooling + head -> one logit per (prompt, choice) pair. Rebuilt from each checkpoint's own
    layout: AutoModelForSequenceClassification silently re-initialises the head of a sentence-transformers
    CrossEncoder (CLS -> Dense+GELU -> LayerNorm -> Dense) and of the decider (mean -> Linear)."""

    def __init__(self, backbone, head, pooling, template="{}"):
        super().__init__()
        self.backbone, self.head, self.pooling, self.template = backbone, head, pooling, template

    @property
    def device(self):
        return next(self.parameters()).device

    def forward(self, input_ids, attention_mask, **_):
        h = self.backbone(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        if self.pooling == "cls":
            h = h[:, 0]
        else:
            m = attention_mask.unsqueeze(-1).to(h.dtype)
            h = (h * m).sum(1) / m.sum(1).clamp_min(1)
        return collections.namedtuple("Out", "logits")(self.head(h))

    def save_pretrained(self, path):
        Path(path).mkdir(parents=True, exist_ok=True)
        torch.save({"pooling": self.pooling, "template": self.template, "head": self.head,
                    "state": self.state_dict(), "config": self.backbone.config.to_dict()}, Path(path) / "pair_scorer.pt")


def _head(path, hidden):
    """The head a checkpoint ships: ST CrossEncoder modules, the decider's scorer, or a fresh linear head.
    `path` = a local dir or (repo, revision); a file the layout needs but cannot be read is an error."""
    from huggingface_hub import hf_hub_download, list_repo_files
    from safetensors.torch import load_file
    nn = torch.nn
    if isinstance(path, tuple):
        files = set(list_repo_files(path[0], revision=path[1]))
        get = lambda f: hf_hub_download(path[0], f, revision=path[1])
    else:
        files = {str(p.relative_to(path)) for p in Path(path).rglob("*")}
        get = lambda f: str(Path(path) / f)
    if "4_Dense/model.safetensors" in files:              # CrossEncoder: Pooling, Dense+GELU, LayerNorm, Dense
        pooling = json.loads(Path(get("1_Pooling/config.json")).read_text())["pooling_mode"]
        dense, norm, out = nn.Linear(hidden, hidden, bias=False), nn.LayerNorm(hidden), nn.Linear(hidden, 1)
        dense.load_state_dict({"weight": load_file(get("2_Dense/model.safetensors"))["linear.weight"]})
        norm.load_state_dict({k[5:]: v for k, v in load_file(get("3_LayerNorm/model.safetensors")).items()})
        out.load_state_dict({k[7:]: v for k, v in load_file(get("4_Dense/model.safetensors")).items()})
        return nn.Sequential(dense, nn.GELU(), norm, out), pooling, None, "{}"
    if "decider_config.json" in files:                    # decider: mean over the pair -> Linear
        weights = load_file(get("model.safetensors"))
        head = nn.Linear(hidden, 1)
        head.load_state_dict({k[7:]: v for k, v in weights.items() if k.startswith("scorer.")})
        return (head, "mean", {k[9:]: v for k, v in weights.items() if k.startswith("backbone.")},
                "Question: Which answer is correct?\nOption: {}")              # its training pair format
    return nn.Linear(hidden, 1), "mean", None, "{}"       # raw encoder: fresh head


def load(init, device):
    from transformers import AutoConfig, AutoModel, AutoTokenizer
    name, revision = INITS.get(init, (init, None))
    tok = AutoTokenizer.from_pretrained(name, revision=revision)
    tok.truncation_side = "left"            # keep the question at the end of a long prompt
    if (Path(name) / "pair_scorer.pt").exists():          # saved by `warm`
        saved = torch.load(Path(name) / "pair_scorer.pt", map_location="cpu", weights_only=False)
        cfg = AutoConfig.for_model(**saved["config"])
        model = PairScorer(AutoModel.from_config(cfg), saved["head"], saved["pooling"], saved["template"])
        model.load_state_dict(saved["state"])
        return model.to(device), tok
    path = name if Path(name).exists() else (name, revision)
    cfg = AutoConfig.from_pretrained(name, revision=revision)
    head, pooling, backbone_state, template = _head(path, cfg.hidden_size)
    if backbone_state is None:
        backbone = AutoModel.from_pretrained(name, revision=revision)
    else:
        backbone = AutoModel.from_config(cfg)
        backbone.load_state_dict(backbone_state, strict=True)
    return PairScorer(backbone, head, pooling, template).to(device), tok


def logits(model, tok, prompts, choices, max_length):
    """One logit per (prompt, choice) pair."""
    batch = tok(list(prompts), [model.template.format(c) for c in choices], truncation="longest_first", max_length=max_length,
                padding=True, return_tensors="pt").to(model.device)
    with torch.autocast(model.device.type, dtype=torch.bfloat16, enabled=model.device.type == "cuda"):
        return model(**batch).logits.squeeze(-1).float()


def train(model, tok, streams, steps, batch, lr, seed, max_length, micro=4):
    """`streams` = [(items, weight)]; each step draws `batch` items by weight, forwarded `micro` items
    at a time (gradient accumulation). Loss = cross-entropy of the gold among its item's choices."""
    rng = random.Random(seed)
    torch.manual_seed(seed)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / max(1, steps // 25)))
    pools, weights = [s for s, _ in streams], [w for _, w in streams]
    model.train()
    for _ in range(steps):
        items = [rng.choice(rng.choices(pools, weights)[0]) for _ in range(batch)]
        for start in range(0, batch, micro):
            chunk = items[start:start + micro]
            flat = [(p.rstrip("\n"), c) for p, cs, _ in chunk for c in cs]
            out = logits(model, tok, [p for p, _ in flat], [c for _, c in flat], max_length)
            loss, at = 0.0, 0
            for _, cs, gold in chunk:
                loss = loss + F.cross_entropy(out[at:at + len(cs)][None], torch.tensor([gold], device=out.device))
                at += len(cs)
            (loss / batch).backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step(), sched.step(), opt.zero_grad()
    model.eval()
    return model


@torch.no_grad()
def evaluate(model, tok, battery, max_length):
    """The battery's MCQ legs only; accuracy and margin under the battery's own metric keys."""
    model.eval()
    costs = lambda ex: (-logits(model, tok, [ex.prompt.rstrip("\n")] * len(ex.choices), ex.choices,
                                max_length)).tolist()
    metrics = {}
    for leg in battery.legs:
        if leg.kind != "mcq":
            continue
        suite = load_eval_suite(leg.path, "", name=leg.name, limit=leg.limit, keep=leg.keep)
        result = score_mcq(suite.examples, costs, max_length)
        _, acc_key, margin_key = leg.metric_keys
        metrics[acc_key], metrics[margin_key] = result["accuracy"], result["margin"]
    return metrics


def _value(a, device):
    battery = load_battery_manifest(a.battery, data_dir=a.data_dir, max_length=a.max_length)
    dpo = dpo_items(a.dpo_n)
    tasks = task_items(load_rows(a.rows), a.negatives, seed=a.seed, policy=a.distractors)
    tasks = {t: tasks[t] for t in (a.tasks or sorted(tasks))}

    def arm(streams):
        model, tok = load(a.init, device)
        train(model, tok, streams, a.steps, a.batch, a.lr, a.seed, a.max_length, a.micro)
        return evaluate(model, tok, battery, a.max_length)

    base = arm([(dpo, 1.0)])
    cell = {"scorer": f"cross_encoder@v{VERSION}", "init": a.init, "init_revision": INITS.get(a.init, (0, None))[1],
            "battery_id": battery.identifier, "dpo": {"repo": DPO[0], "revision": DPO[1], "n": a.dpo_n},
            "rows": str(a.rows), "steps": a.steps, "batch": a.batch, "lr": a.lr, "mix": a.mix,
            "negatives": a.negatives, "distractors": a.distractors, "seed": a.seed, "max_length": a.max_length, "baseline": base, "tasks": {}}
    for name, items in tasks.items():
        got = arm([(dpo, 1 - a.mix), (items, a.mix)])
        cell["tasks"][name] = {**got, **{f"{k}_delta": got[k] - base[k] for k in got
                                         if got[k] is not None and base[k] is not None}}
        print(f"[encoder] {name}: " + ", ".join(f"{k}={v:+.4f}" for k, v in cell["tasks"][name].items()
                                                 if k.endswith("acc_delta")), flush=True)
        Path(a.out).write_text(json.dumps(cell, indent=1))        # rewritten per task: a partial run is still readable
    return cell


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=("warm", "value"))
    ap.add_argument("--init", default="encoder", help="encoder | reranker | decider | a local dir saved by warm")
    ap.add_argument("--rows", help="a task_rows cache dir (value)")
    ap.add_argument("--tasks", nargs="*", help="default: every task in --rows")
    ap.add_argument("--battery", default=str(Path(__file__).resolve().parents[1]
                                             / "resources/batteries/copyfree_battery_v13_tiny.json"))
    ap.add_argument("--data-dir", default="data_cache")
    ap.add_argument("--steps", type=int, default=300)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--micro", type=int, default=4, help="items per forward; gradient accumulation")
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--mix", type=float, default=0.5)
    ap.add_argument("--negatives", type=int, default=3)
    ap.add_argument("--distractors", default="random", choices=("random", "hard"), help="see distractors.py")
    ap.add_argument("--dpo-n", type=int, default=50_000)
    ap.add_argument("--max-length", type=int, default=512)
    ap.add_argument("--seed", type=int, default=43)
    ap.add_argument("--out", required=True, help="warm: a model dir; value: a cell json")
    a = ap.parse_args(argv)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if a.command == "warm":
        model, tok = load(a.init, device)
        train(model, tok, [(dpo_items(a.dpo_n), 1.0)], a.steps, a.batch, a.lr, a.seed, a.max_length, a.micro)
        model.save_pretrained(a.out), tok.save_pretrained(a.out)
        return
    if not a.rows:
        ap.error("value needs --rows")
    _value(a, device)


if __name__ == "__main__":
    main()
