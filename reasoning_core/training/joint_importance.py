"""joint_importance.py — per-task JOINT importance for a pretraining mix.

Scores each aux task by how much it helps BOTH regimes at once:
  • fine-tuning   : SmolLM2-135M *pretrained*  + 80% dolci   + 20% task  (300 steps)
  • pretraining   : SmolLM2-135M *from scratch* + 80% fineweb + 20% task  (600 steps)
Influence = ΔNLL on held-out BBH = NLL(80% main + 20% task) − NLL(main-only baseline);
negative = the task helps. We also track the from-scratch fineweb-retention tax (ΔNLL on
fineweb). Per regime we z-score Δ across tasks, then average the z's → one "joint goodness"
number (lower = better in both regimes). 2 seeds, averaged. Mirrors run_sft.py's mix
(aux_ratio=0.2, completion-only loss, smol135).

  python joint_importance.py --tasks arithmetics,regex_following,proof_reconstruction
  python joint_importance.py --tasks <...> --hf reasoning-core/procedural-pretraining-pile --seeds 0,1
"""
import os; os.environ.setdefault("HF_HUB_DISABLE_XET", "1")          # xet bridge stalls streaming
import argparse, json, itertools, statistics as st
from pathlib import Path
import torch
from datasets import load_dataset, IterableDataset, interleave_datasets
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
from trl import SFTConfig, SFTTrainer
from tabulate import tabulate

MODEL = "HuggingFaceTB/SmolLM2-135M"; MIX = 0.2; MAXLEN = 512; BATCH = 8; LR = 1e-4
DEV = "cuda" if torch.cuda.is_available() else "cpu"
DT  = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float32
REGIMES = [("finetune", "dolci", False, 300), ("pretrain", "fw", True, 600)]   # (name, main, from_scratch, steps)
BBH = ["boolean_expressions", "causal_judgement", "date_understanding", "formal_fallacies",
       "logical_deduction_five_objects", "multistep_arithmetic_two", "navigate", "object_counting",
       "tracking_shuffled_objects_three_objects", "web_of_lies", "word_sorting", "sports_understanding"]

def fmt(p, a, eos): return {"prompt": f"{p}\n", "completion": f"{a}{eos}"}
def cycle_gen(rows):                                               # generator factory over a fixed list
    def g():
        for r in itertools.cycle(rows): yield r
    return g

def bbh_eval(tok):
    out = []
    for s in BBH:
        try:
            for ex in list(load_dataset("lukaemon/bbh", s, split="test"))[5:20]:
                out.append((f"{ex['input']}\n", f"{ex['target']}{tok.eos_token}"))
        except Exception: pass
    return out

def fw_eval(n=120):
    out = []
    for x in load_dataset("HuggingFaceFW/fineweb-edu", split="train", streaming=True).skip(800_000):
        if len(x["text"]) > 100: out.append(x["text"][:1500])
        if len(out) >= n: break
    return out

@torch.no_grad()
def nll_qa(model, tok, ex):
    model.eval(); tl = tn = 0.0
    for p, a in ex:
        pi = tok(p, add_special_tokens=False).input_ids; ai = tok(a, add_special_tokens=False).input_ids
        if len(pi) + len(ai) > MAXLEN or not ai: continue
        ids = torch.tensor([pi + ai], device=DEV); lab = ids.clone(); lab[0, :len(pi)] = -100
        o = model(ids, labels=lab); k = (lab[0, 1:] != -100).sum().item(); tl += o.loss.item() * k; tn += k
    return tl / max(tn, 1)

@torch.no_grad()
def nll_lm(model, tok, texts):
    model.eval(); tl = tn = 0.0
    for t in texts:
        ids = tok(t, add_special_tokens=False, truncation=True, max_length=MAXLEN, return_tensors="pt").input_ids.to(DEV)
        if ids.shape[1] < 2: continue
        o = model(ids, labels=ids); k = ids.shape[1] - 1; tl += o.loss.item() * k; tn += k
    return tl / max(tn, 1)

def main_gen(main, tok):
    eos = tok.eos_token
    if main == "dolci":
        def g():
            for x in load_dataset("tasksource/dolci-instruct", split="train", streaming=True):
                if x.get("answer"): yield fmt(x["prompt"], x["answer"], eos)
    else:
        def g():
            for x in load_dataset("HuggingFaceFW/fineweb-edu", split="train", streaming=True):
                yield {"prompt": "", "completion": x["text"][:1200] + eos}
    return g

def task_rows(hf, task, tok, n, scan_cap=400_000):
    """Deduplicated (by prompt) aux rows for one task, streamed from the HF source."""
    eos = tok.eos_token; seen = set(); rows = []
    for i, x in enumerate(load_dataset(hf, split="train", streaming=True)):
        if i > scan_cap: break                                    # guard: absent task → don't scan forever
        if (x.get("task") or "") != task or not x.get("answer"): continue
        p = x.get("prompt") or ""
        if p in seen: continue
        seen.add(p); rows.append(fmt(p, x["answer"], eos))
        if len(rows) >= n: break
    if not rows: raise ValueError(f"no rows for task '{task}' in {hf} (removed/renamed?)")
    return rows

def train(model, tok, ds, steps, seed):
    cfg = SFTConfig(output_dir="/tmp/joint_imp", overwrite_output_dir=True, max_steps=steps,
                    per_device_train_batch_size=BATCH, learning_rate=LR, weight_decay=0.01,
                    max_length=MAXLEN, packing=False, completion_only_loss=True,
                    bf16=(DT == torch.bfloat16), report_to="none", save_strategy="no",
                    logging_steps=10_000, seed=seed, disable_tqdm=True)
    SFTTrainer(model=model, processing_class=tok, train_dataset=ds, args=cfg).train()

def zscore(d):
    v = list(d.values()); m = st.mean(v); s = st.pstdev(v) or 1.0
    return {k: (x - m) / s for k, x in d.items()}

def run():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True, help="comma-separated aux task names")
    ap.add_argument("--hf", default="reasoning-core/procedural-pretraining-pile", help="HF aux source")
    ap.add_argument("--seeds", default="0,1")
    ap.add_argument("--n", type=int, default=1500, help="unique examples per task")
    ap.add_argument("--out", default=str(Path(__file__).parent / "joint_importance.json"))
    a = ap.parse_args()
    tasks = [t.strip() for t in a.tasks.split(",") if t.strip()]
    seeds = [int(s) for s in a.seeds.split(",")]
    tok = AutoTokenizer.from_pretrained(MODEL)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    bbh, fwe = bbh_eval(tok), fw_eval()
    rows = {t: task_rows(a.hf, t, tok, a.n) for t in tasks}        # dedup once; reused across regimes/seeds
    raw = {name: {"bbh": {t: [] for t in tasks}, "fw": {t: [] for t in tasks}} for name, *_ in REGIMES}
    for name, main, scratch, steps in REGIMES:
        mg = main_gen(main, tok)
        for seed in seeds:
            torch.manual_seed(seed)
            model = (AutoModelForCausalLM.from_config(AutoConfig.from_pretrained(MODEL), dtype=DT)
                     if scratch else AutoModelForCausalLM.from_pretrained(MODEL, dtype=DT)).to(DEV)
            init = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            reset = lambda: model.load_state_dict({k: v.to(DEV) for k, v in init.items()})
            reset(); train(model, tok, IterableDataset.from_generator(mg), steps, seed)
            b_bbh, b_fw = nll_qa(model, tok, bbh), nll_lm(model, tok, fwe)
            for t in tasks:
                reset()
                ds = interleave_datasets([IterableDataset.from_generator(mg),
                                          IterableDataset.from_generator(cycle_gen(rows[t]))],
                                         probabilities=[1 - MIX, MIX], seed=seed, stopping_strategy="first_exhausted")
                train(model, tok, ds, steps, seed)
                raw[name]["bbh"][t].append(nll_qa(model, tok, bbh) - b_bbh)
                raw[name]["fw"][t].append(nll_lm(model, tok, fwe) - b_fw)
            del model
            if DEV == "cuda": torch.cuda.empty_cache()
    comp = {"finetune_bbh":  {t: st.mean(raw["finetune"]["bbh"][t]) for t in tasks},
            "pretrain_bbh":  {t: st.mean(raw["pretrain"]["bbh"][t]) for t in tasks},
            "pretrain_fwtax":{t: st.mean(raw["pretrain"]["fw"][t])  for t in tasks}}
    Z = {k: zscore(v) for k, v in comp.items()}
    joint = {t: st.mean([Z[k][t] for k in Z]) for t in tasks}      # lower = helps both regimes
    order = sorted(tasks, key=lambda t: joint[t])
    hdr = ["task", "joint_z", "ft_BBH", "pt_BBH", "pt_FWtax"]
    table = [[t, round(joint[t], 2), round(comp["finetune_bbh"][t], 3),
              round(comp["pretrain_bbh"][t], 3), round(comp["pretrain_fwtax"][t], 3)] for t in order]
    print(tabulate(table, headers=hdr, tablefmt="github"))
    json.dump({"seeds": seeds, "hf": a.hf, "joint": joint, **comp}, open(a.out, "w"), indent=2)
    md = Path(__file__).parent / "joint_importance.md"
    head = md.read_text().split("<!-- RESULTS -->")[0].rstrip() if md.exists() else "# Joint task importance\n"
    md.write_text(f"{head}\n\n<!-- RESULTS -->\n## Latest run (`{a.hf}`, seeds {seeds}) — lower `joint_z` = helps both regimes\n\n"
                  + tabulate(table, headers=hdr, tablefmt="github") + "\n")
    print(f"\nwrote {a.out} and {md}")

if __name__ == "__main__":
    run()
