#!/usr/bin/env python3
"""
per_task_influence.py — controlled per-task mixed-data ablation (generic).

For each RC task X, measure the *marginal* effect of mixing it into a main
training stream — one task at a time, fixed baseline, direct loss measurement,
no regression fitting on noisy windowed signals.

Setup (parameterized):
  MAIN_DATA    fw | dolci          (which corpus dominates training)
  FROM_SCRATCH 0 = pretrained      (correct for dolci; FW is in pretraining)
               1 = random init     (correct for fw; matches run_sft.py default)
  Baseline:    train on MAIN_DATA only, TRAIN_STEPS steps (packed full-LM loss)
  Per-task:    interleave(MAIN_DATA 1-MIX_AUX, RC_task_X MIX_AUX), same config
  Compare:     Δ NLL = with_X − baseline_main_only on held-out BBH/Dolci/FW

Env vars:
  SEED        (default 43)
  TRAIN_STEPS (default 500)
  MIX_AUX     (default 0.2)
  MAIN_DATA   (default dolci)         fw | dolci
  FROM_SCRATCH (default 0 if dolci else 1)
  LR          (default 1e-4)
  TASKS       comma-separated subset (default all 40)
"""
import os, sys, json, datetime, logging, warnings, time
from pathlib import Path
import torch

sys.stdout.reconfigure(line_buffering=True)
HF_CACHE = os.environ.get("HF_CACHE", str(Path.home() / "tmp/hf_cache"))
os.environ.update({"HF_HOME": HF_CACHE, "HF_DATASETS_CACHE": HF_CACHE,
                   "TOKENIZERS_PARALLELISM": "false", "WANDB_DISABLED": "true"})
warnings.filterwarnings("ignore")
logging.getLogger("trl").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)

from datasets import load_dataset, interleave_datasets, IterableDataset
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig, TrainerCallback
from trl import SFTConfig, SFTTrainer

ALL_TASKS = [
    'arithmetics', 'bayesian_association', 'bayesian_intervention', 'code_execution',
    'conjecture_entailment', 'constrained_continuation', 'constraint_satisfaction',
    'continuation', 'coreference', 'count_elements', 'diff_prediction',
    'equation_system', 'evidence_retrieval', 'graph_dependencies', 'graph_isomorphism',
    'graph_pathfinding', 'graph_successors', 'lambda_reduction', 'lexical_knowledge',
    'locate_error', 'logic_formalization', 'logic_nli', 'navigation', 'parsability',
    'parsing', 'planning', 'proof_reconstruction', 'qualitative_reasoning',
    'reference_tracking', 'regex_following', 'regex_induction', 'regex_reasoning',
    'sequential_induction', 'set_equality', 'set_intersection', 'set_missing_element',
    'table_conversion', 'table_qa',
]   # NB: diff_patching + term_unification REMOVED from the rc dataset on 2026-06-04 — dropped
    # here so a streamed run doesn't scan the whole pile forever hunting a non-existent task.
_DEFAULT_RC_TASKS = list(ALL_TASKS)   # full pool for PEER sampling (survives a TASKS filter)

SEED         = int(os.environ.get("SEED", 43))
TRAIN_STEPS  = int(os.environ.get("TRAIN_STEPS", 500))
MIX_AUX      = float(os.environ.get("MIX_AUX", 0.2))
# OVERSAMPLE: measure MARGINAL value of upweighting a task IN a full aux mixture.
#   baseline = main(1-MIX) + all-aux(MIX);  treatment_X = main(1-MIX) + X(MIX/2) + all-aux(MIX/2)
#   delta = NLL(treatment_X) - NLL(baseline_mix). Total aux stays MIX (fair compute).
OVERSAMPLE   = os.environ.get("OVERSAMPLE", "0") != "0"
# OVS_X_FRAC: fraction of the aux budget (MIX) given to the measured task X; the rest goes to the
# all-rc background. Default 0.5 (the classic 50/50 split). Small values (e.g. 0.1) = the REALISTIC
# marginal setting: a large all-rc mixture + a small extra dose of X (X is already ~1/N in the mix).
OVS_X_FRAC   = float(os.environ.get("OVS_X_FRAC", "0.5"))
# PEER_MIX: like OVERSAMPLE but the aux background is a SMALL fixed sample of N_PEERS
#   peer tasks (not the full pile) — a more realistic "this task among a few others"
#   mixture. baseline = main(1-MIX) + peers(MIX) [trained once, peer set fixed by SEED];
#   treatment_X = main(1-MIX) + X(MIX/2) + peers(MIX/2); delta isolates upweighting X
#   on top of a realistic K-peer background. Default off.
PEER_MIX     = os.environ.get("PEER_MIX", "0") != "0"
N_PEERS      = int(os.environ.get("N_PEERS", 8))
# COMPLETION_ONLY: mask the prompt in the loss (answer-only), MATCHING run_sft.py
# production (completion_only_loss=True). Default ON. Set 0 for legacy full-LM loss.
COMPLETION_ONLY = os.environ.get("COMPLETION_ONLY", "1") != "0"
# DEDUP_PROMPT: drop repeated prompts within each aux generator (per-task and the
# all-aux / peer backgrounds), so a task can't gain/lose influence merely by repeating
# the same examples. Off = canonical. On = controlled "unique-examples-only" rerun.
DEDUP_PROMPT = os.environ.get("DEDUP_PROMPT", "0") != "0"
# MODE_FILTER: restrict the per-task aux stream to one answer style from the rc `mode`
# column (instruct | cot | few_shot | verification). Empty = pool all modes (canonical).
# cot answers embed the reasoning trace (longer/structured target); instruct emits only the
# final answer. Lets us isolate whether cot vs instruct examples help or hurt.
MODE_FILTER  = os.environ.get("MODE_FILTER", "").strip()
# MODE_MIX: realistic FULL-MIXTURE answer-format ablation — aux = ALL tasks, but the mode column
# blended at given weights (e.g. "verification:0.5,instruct:0.5"). Runs ONE pseudo-task __ALLMIX__
# (main + the blended all-aux stream at MIX_AUX) vs the main-only baseline. Empty = off.
MODE_MIX     = os.environ.get("MODE_MIX", "").strip()
_mode_mix    = []
if MODE_MIX:
    for _p in MODE_MIX.split(","):
        _m, _w = _p.split(":"); _mode_mix.append((_m.strip(), float(_w)))
    _ws = sum(w for _, w in _mode_mix); _mode_mix = [(m, w/_ws) for m, w in _mode_mix]
MAIN_DATA    = os.environ.get("MAIN_DATA", "dolci").lower()
assert MAIN_DATA in ("fw", "dolci", "flan", "fw_recent", "tasksource", "fwdolci", "fwtasksource", "codealpaca", "fwdolcicode"), MAIN_DATA
# Default to the local cache when present so EVERY run is stream-free (HF xet-bridge 408s crash long
# streaming runs). Set MAIN_LOCAL="" to force HF streaming. Training data = same first-20k docs as the
# stream; only the eval slice differs (skip 25k) → BBH (primary) identical, dolci/fw deltas shift slightly.
MAIN_LOCAL   = os.environ.get("MAIN_LOCAL", "data_cache" if Path("data_cache/fw_main.jsonl").exists() else "")
def _read_jsonl(p):
    return [json.loads(l) for l in open(p)]
_default_scratch = "1" if MAIN_DATA == "fw" else "0"
FROM_SCRATCH = os.environ.get("FROM_SCRATCH", _default_scratch) != "0"
LR           = float(os.environ.get("LR", 1e-4))
MAX_LEN      = 512
BATCH        = int(os.environ.get("BATCH", 8))   # reduce for larger decoders (e.g. BATCH=2 for 400-600M)
GRAD_ACCUM   = int(os.environ.get("GRAD_ACCUM", 1))  # effective batch = BATCH*GRAD_ACCUM; raise for cleaner PRETRAINING-regime gradients (max_steps counts optimizer steps → N× more tokens)

# Aux-task source: rc (procedural-pretraining-pile) | rgym (reasoning-gym).
AUX_DATASET  = os.environ.get("AUX_DATASET", "rc").lower()
assert AUX_DATASET in ("rc", "rgym"), AUX_DATASET
# AUX_HF overrides the HF repo the aux stream pulls from (e.g. a freshly cluster-built
# staging repo). Default = the canonical repo for AUX_DATASET.
_AUX_HF      = os.environ.get("AUX_HF") or {"rc": "reasoning-core/procedural-pretraining-pile",
                "rgym": "reasoning-core/reasoning-gym"}[AUX_DATASET]
_RESULTS_SUB = {"rc": "per_task_results", "rgym": "per_task_results_rgym"}[AUX_DATASET]
if AUX_DATASET == "rgym":  # task list discovered/cached separately (98 tasks)
    ALL_TASKS = json.loads(Path("rgym_tasks.json").read_text())["tasks"]
_filter      = os.environ.get("TASKS", "").strip()
if _filter: ALL_TASKS = [t.strip() for t in _filter.split(",") if t.strip()]
if MODE_MIX: ALL_TASKS = ["__ALLMIX__"]     # single full-mixture arm under the mode blend
# GROUP mode: measure a CHOSEN SET of tasks POOLED into ONE aux arm at the SAME total MIX budget
# (round-robin so each member gets MIX/|group| dose), to test complementarity against the individual
# per-task deltas. e.g. GROUP_TASKS=logic_nli,multistep_nli  → one arm, comparable to each alone.
GROUP_TASKS = [t.strip() for t in os.environ.get("GROUP_TASKS", "").split(",") if t.strip()]
if GROUP_TASKS: ALL_TASKS = ["__GROUP__"]
# PEER_MIX background: fixed seeded sample of N_PEERS tasks (independent of target).
import random as _random
_FULL_TASKS  = (json.loads(Path("rgym_tasks.json").read_text())["tasks"]
                if AUX_DATASET == "rgym" else list(_DEFAULT_RC_TASKS))
PEER_TASKS   = sorted(_random.Random(SEED).sample(
                   _FULL_TASKS, min(N_PEERS, len(_FULL_TASKS)))) if PEER_MIX else []

MODEL_NAME = os.environ.get("MODEL", "HuggingFaceTB/SmolLM2-135M")  # e.g. jhu-clsp/ettin-decoder-400m, Qwen/Qwen3-0.6B (use a distinct RUN_TAG)
# WARMED_CKPT_DIR is only used for the fw-pretraining warm-start baseline; env-overridable.
WARMED_CKPT_DIR = Path(os.environ.get("WARMED_CKPT_DIR",
                      "/mnt/nfs_share_magnet2/dsileo/sandboxes/rc_grad/model_checkpoints/"
                      "HuggingFaceTB_SmolLM2-135M_fw_rc_W300"))
# OUT_DIR: where raw result JSONs are written. Default = <repo>/per_task_results (this file
# lives in <repo>/task_diagnostics/). The orchestrator passes OUT_DIR explicitly so the two always agree.
OUT_DIR     = Path(os.environ.get("OUT_DIR") or (Path(__file__).resolve().parent.parent / _RESULTS_SUB))
OUT_DIR.mkdir(parents=True, exist_ok=True)
_init_tag   = "scratch" if FROM_SCRATCH else "pretrained"
_ovs_tag    = ("_OVS" + (f"x{int(OVS_X_FRAC*100)}" if OVS_X_FRAC != 0.5 else "")) if OVERSAMPLE else ""
_peer_tag   = f"_PEERS{N_PEERS}" if PEER_MIX else ""
_co_tag     = "" if COMPLETION_ONLY else "_FULLLM"   # answer-only = canonical clean name
_dedup_tag  = "_DEDUP" if DEDUP_PROMPT else ""
_mode_tag   = f"_MODE-{MODE_FILTER}" if MODE_FILTER else ""
_grp_tag    = ("_GRP-" + "+".join(GROUP_TASKS)) if GROUP_TASKS else ""   # distinct file per group
# RUN_TAG: optional free-form suffix to write to distinct files without overwriting canonical
# results (e.g. re-measuring tasks after the rc dataset was updated on HF). Default OFF.
_run_tag    = os.environ.get("RUN_TAG", "")
if _run_tag and not _run_tag.startswith("_"): _run_tag = "_" + _run_tag
_tag        = f"{_ovs_tag}{_peer_tag}{_co_tag}{_dedup_tag}{_mode_tag}{_grp_tag}{_run_tag}"
OUT_FILE    = OUT_DIR / f"influence{_tag}_S{SEED}_T{TRAIN_STEPS}_M{int(MIX_AUX*100)}_{MAIN_DATA}_{_init_tag}.json"
LOG_PER_EX  = os.environ.get("LOG_PER_EX", "0") != "0"
PEREX_FILE  = OUT_DIR / f"perex{_tag}_S{SEED}_T{TRAIN_STEPS}_M{int(MIX_AUX*100)}_{MAIN_DATA}_{_init_tag}.json"
# LOG_SAT: record per-task answer-token-accuracy curve DURING the treatment run
# (in-mixture saturation — measured while the 80% main/FW background is present, which
# is the realistic difficulty signal we want; supersedes the standalone profiler).
# Default ON: merged into the influence run so we don't retrain each task twice.
LOG_SAT     = os.environ.get("LOG_SAT", "1") != "0"
SAT_EVERY   = int(os.environ.get("SAT_EVERY", 50))
SAT_NEVAL   = int(os.environ.get("SAT_NEVAL", 40))
SAT_FILE    = OUT_DIR / f"sat{_ovs_tag}{_peer_tag}{_dedup_tag}{_mode_tag}{_run_tag}_S{SEED}_T{TRAIN_STEPS}_M{int(MIX_AUX*100)}_{MAIN_DATA}_{_init_tag}.json"
# CKPT_EVAL: budget-convergence study — eval BBH/Dolci/FW every CKPT_EVAL steps DURING training
# (baseline + each task), so influence@T = task_nll@T - baseline_nll@T from ONE run per task. 0=off.
CKPT_EVAL   = int(os.environ.get("CKPT_EVAL", "0"))
CKPT_FILE   = OUT_DIR / f"ckpt{_run_tag}_S{SEED}_T{TRAIN_STEPS}_M{int(MIX_AUX*100)}_{MAIN_DATA}_{_init_tag}.json"
DEVICE      = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE       = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float32

torch.manual_seed(SEED)
_mode_str = ("PEER_MIX(%d peers)" % N_PEERS if PEER_MIX else
             "OVERSAMPLE" if OVERSAMPLE else "single-task")
print(f"\n=== Controlled ablation — seed={SEED}  steps={TRAIN_STEPS}  "
      f"mix={1-MIX_AUX:.0%} {MAIN_DATA} + {MIX_AUX:.0%} aux | init={_init_tag} | "
      f"mode={_mode_str} ===\n")
if PEER_MIX: print(f"  peer background ({N_PEERS}): {PEER_TASKS}\n")

# ── Tokenizer + model + init snapshot ───────────────────────────────────────────
try:
    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
except Exception as _tok_e:
    # Some recent models (e.g. LiquidAI LFM2.5, tokenizer_class="TokenizersBackend") are not in this
    # transformers version's tokenizer registry. Load the fast tokenizer straight from tokenizer.json
    # and restore special tokens from tokenizer_config.json.
    from transformers import PreTrainedTokenizerFast
    from huggingface_hub import hf_hub_download
    _tj = hf_hub_download(MODEL_NAME, "tokenizer.json")
    _tc = json.loads(Path(hf_hub_download(MODEL_NAME, "tokenizer_config.json")).read_text())
    _val = lambda v: (v.get("content") if isinstance(v, dict) else v)
    _specials = {k: _val(_tc[k]) for k in ("bos_token", "eos_token", "unk_token", "pad_token") if _tc.get(k)}
    tok = PreTrainedTokenizerFast(tokenizer_file=_tj, **_specials)
    print(f"⚠️ Fallback PreTrainedTokenizerFast for {MODEL_NAME} (specials={list(_specials)}); reason: {repr(_tok_e)[:80]}")
if tok.pad_token is None: tok.pad_token = tok.eos_token
EOS = tok.eos_token

if FROM_SCRATCH:
    cfg = AutoConfig.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_config(cfg, dtype=DTYPE,
                                              attn_implementation="sdpa").to(DEVICE)
    print(f"🆕 Random-init {MODEL_NAME} ({sum(p.numel() for p in model.parameters())/1e6:.1f}M params)")
elif MAIN_DATA in ("dolci", "flan", "tasksource", "fw_recent", "fwdolci", "fwtasksource", "codealpaca", "fwdolcicode"):
    # Use raw pretrained model. dolci/flan/tasksource = instruction FT (novel data);
    # fw_recent = continued pretraining on FRESH post-cutoff FineWeb; fwdolci/fwtasksource = realistic
    # BLEND of continued-pretraining text + instruction (mid-training regime). All start from pretrained.
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, dtype=DTYPE, attn_implementation="sdpa",
    ).to(DEVICE)
    print(f"📦 Pretrained {MODEL_NAME}")
else:
    # MAIN_DATA=fw + pretrained: use cached FW-warmed checkpoint for fair baseline
    model = AutoModelForCausalLM.from_pretrained(
        WARMED_CKPT_DIR, dtype=DTYPE, attn_implementation="sdpa",
    ).to(DEVICE)
    print(f"♻️  FW-warmed checkpoint from {WARMED_CKPT_DIR.name}")

INIT_STATE = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
def reset_model():
    model.load_state_dict({k: v.to(DEVICE) for k, v in INIT_STATE.items()})

# ── Held-out evals (BBH, Dolci, FW) — eval all three regardless of main_data ──
BBH_SUBTASKS = [
    "boolean_expressions", "causal_judgement", "date_understanding",
    "formal_fallacies", "logical_deduction_five_objects",
    "multistep_arithmetic_two", "navigate", "object_counting",
    "tracking_shuffled_objects_three_objects", "web_of_lies",
    "word_sorting", "sports_understanding",
]
print("📊 Building eval sets…")
BBH_EVAL = []
for sub in BBH_SUBTASKS:
    try:
        for ex in list(load_dataset("lukaemon/bbh", sub, split="test"))[5:25]:
            BBH_EVAL.append((f"{ex['input']}\n", f"{ex['target']}{EOS}"))
    except Exception as e: print(f"  ⚠ {sub}: {e}")
DOLCI_EVAL, FW_EVAL = [], []
if MAIN_LOCAL:                                   # stream-free eval slices
    for r in _read_jsonl(Path(MAIN_LOCAL) / "dolci_eval.jsonl"):
        if r.get("answer"): DOLCI_EVAL.append((f"{r['prompt']}\n", f"{r['answer']}{EOS}"))
    _fw_eval_name = "fw_recent_eval.jsonl" if MAIN_DATA == "fw_recent" else "fw_eval.jsonl"
    for r in _read_jsonl(Path(MAIN_LOCAL) / _fw_eval_name):
        txt = r["text"][:1500]
        if len(txt) >= 100: FW_EVAL.append(txt)
    DOLCI_EVAL, FW_EVAL = DOLCI_EVAL[:200], FW_EVAL[:200]
else:
    for x in load_dataset("tasksource/dolci-instruct", split="train", streaming=True).skip(50_000):
        if not x.get("answer"): continue
        DOLCI_EVAL.append((f"{x['prompt']}\n", f"{x['answer']}{EOS}"))
        if len(DOLCI_EVAL) >= 200: break
    for x in load_dataset("HuggingFaceFW/fineweb-edu", split="train", streaming=True).skip(800_000):
        txt = x["text"][:1500]
        if len(txt) < 100: continue
        FW_EVAL.append(txt)
        if len(FW_EVAL) >= 200: break

# Optional held-out TRANSFER targets beyond the always-on BBH/Dolci/FW. Each is a QA-NLL (answer-only)
# eval gated by EVAL_<NAME>=1, loaded from a {prompt,answer} jsonl. Adding a capability leg = one line
# in _EXTRA_SPEC. Output schema per task: <name>_nll / <name>_delta. Capability map for the aggregate:
#   fw=WEB_LM, bbh=REASONING, mmlu_math=MATH, mmlu_logic=LOGIC, mbpp=CODING, dolci=CONVERSATION.
_EXTRA_SPEC = [   # (name, default_jsonl, cap)
    ("flan",       "data_cache/flan_eval.jsonl",       200),
    ("mbpp",       "data_cache/mbpp_eval.jsonl",       257),
    ("mmlu_math",  "data_cache/mmlu_math_eval.jsonl",  400),
    ("mmlu_logic", "data_cache/mmlu_logic_eval.jsonl", 200),
    ("mmlu_math_cloze",  "data_cache/mmlu_math_cloze_eval.jsonl",  400),   # format-fair: answer-text NLL
    ("mmlu_logic_cloze", "data_cache/mmlu_logic_cloze_eval.jsonl", 200),   # (no listed options in prompt)
]
EXTRA_EVALS = {}   # name -> [(prompt, answer)]
for _nm, _path, _cap in _EXTRA_SPEC:
    if os.environ.get(f"EVAL_{_nm.upper()}", "0") == "1":
        _p = os.environ.get(f"{_nm.upper()}_EVAL_PATH", _path)
        _rows = [(f"{r['prompt']}\n", f"{r['answer']}{EOS}")
                 for r in _read_jsonl(Path(_p)) if r.get("prompt") and r.get("answer")]
        EXTRA_EVALS[_nm] = _rows[:_cap]
print(f"  BBH={len(BBH_EVAL)}  Dolci={len(DOLCI_EVAL)}  FW={len(FW_EVAL)}"
      + "".join(f"  {k}={len(v)}" for k, v in EXTRA_EVALS.items()) + "\n")


@torch.no_grad()
def eval_qa(examples):
    model.eval()
    total_loss, total_tok = 0., 0
    per_ex = []
    for prompt, answer in examples:
        p_ids = tok(prompt, add_special_tokens=False).input_ids
        a_ids = tok(answer, add_special_tokens=False).input_ids
        if len(p_ids) + len(a_ids) > MAX_LEN: continue
        ids = torch.tensor([p_ids + a_ids], device=DEVICE)
        labels = ids.clone(); labels[0, :len(p_ids)] = -100
        out = model(ids, labels=labels)
        n = (labels[0, 1:] != -100).sum().item()
        total_loss += out.loss.item() * n
        total_tok  += n
        per_ex.append(out.loss.item())
    return total_loss / max(total_tok, 1), total_tok, per_ex

@torch.no_grad()
def eval_lm(texts):
    model.eval()
    total_loss, total_tok = 0., 0
    per_ex = []
    for txt in texts:
        ids = tok(txt, add_special_tokens=False, truncation=True,
                  max_length=MAX_LEN, return_tensors="pt").input_ids.to(DEVICE)
        if ids.shape[1] < 2: continue
        out = model(ids, labels=ids)
        n = ids.shape[1] - 1
        total_loss += out.loss.item() * n
        total_tok  += n
        per_ex.append(out.loss.item())
    return total_loss / max(total_tok, 1), total_tok, per_ex

def eval_all():
    bbh_m,   _, bbh_px   = eval_qa(BBH_EVAL)
    dolci_m, _, dolci_px = eval_qa(DOLCI_EVAL)
    fw_m,    _, fw_px    = eval_lm(FW_EVAL)
    perex = {"bbh": bbh_px, "dolci": dolci_px, "fw": fw_px}
    extra = {}
    for _nm, _ex in EXTRA_EVALS.items():
        m, _, px = eval_qa(_ex)
        extra[_nm] = m
        perex[_nm] = px
    return (bbh_m, dolci_m, fw_m, extra), perex

def save_perex(key, perex):
    if not LOG_PER_EX: return
    data = json.loads(PEREX_FILE.read_text()) if PEREX_FILE.exists() else {}
    data[key] = perex
    PEREX_FILE.write_text(json.dumps(data))

# ── In-mixture saturation logging (LOG_SAT) ─────────────────────────────────────
_SAT_SAMPLES = Path(f"{AUX_DATASET}_samples.json")
_SAT_CACHE   = json.loads(_SAT_SAMPLES.read_text()) if (LOG_SAT and _SAT_SAMPLES.exists()) else None

def sat_eval_rows(task):
    """Held-out (prompt, answer) rows for measuring task token-accuracy."""
    if _local_aux is not None:                 # local aux (e.g. lean): sat from the same local data
        return [(r[0], r[1]) for r in _local_aux.get(task, [])[:SAT_NEVAL]
                if isinstance(r, (list, tuple)) and len(r) >= 2 and r[1]]
    if _SAT_CACHE is not None:
        return [(r[0], r[1]) for r in _SAT_CACHE.get(task, [])[:SAT_NEVAL]
                if isinstance(r, (list, tuple)) and len(r) >= 2 and r[1]]
    out = []
    for x in load_dataset(_AUX_HF, split="train", streaming=True):
        if (x.get("task") or "") != task or not x.get("answer"): continue
        out.append((x.get("prompt") or "", x["answer"]))
        if len(out) >= SAT_NEVAL: break
    return out

@torch.no_grad()
def token_acc(rows):
    """Teacher-forced argmax==gold over answer tokens (TRL's mean_token_accuracy)."""
    model.eval(); correct = total = 0
    for prompt, answer in rows:
        p_ids = tok(f"{prompt}\n", add_special_tokens=False).input_ids
        a_ids = tok(f"{answer}{EOS}", add_special_tokens=False).input_ids
        if len(p_ids) + len(a_ids) > MAX_LEN or not a_ids: continue
        ids = torch.tensor([p_ids + a_ids], device=DEVICE)
        start = len(p_ids) - 1
        pred = model(ids).logits[0][start:-1].argmax(-1)
        gold = ids[0, start + 1:]
        correct += (pred == gold).sum().item(); total += gold.numel()
    model.train(); return correct / max(total, 1)

class SatCurveCB(TrainerCallback):
    def __init__(self, rows, curve): self.rows, self.curve = rows, curve
    def on_step_end(self, args, state, control, **kw):
        if state.global_step % SAT_EVERY == 0:
            self.curve.append([state.global_step, token_acc(self.rows)])

class CkptEvalCB(TrainerCallback):
    """Eval BBH/Dolci/FW every CKPT_EVAL steps during training → budget-convergence curve."""
    def __init__(self, curve): self.curve = curve
    def on_step_end(self, args, state, control, **kw):
        if CKPT_EVAL and state.global_step % CKPT_EVAL == 0:
            (b, d, f, _fl), _ = eval_all()
            self.curve.append([state.global_step, b, d, f])

def save_ckpt(key, curve):
    data = json.loads(CKPT_FILE.read_text()) if CKPT_FILE.exists() else \
        {"main": MAIN_DATA, "init": _init_tag, "seed": SEED, "ckpt_every": CKPT_EVAL, "curves": {}}
    data["curves"][key] = curve
    CKPT_FILE.write_text(json.dumps(data))

def derive_sat(curve):
    if not curve: return {}
    accs = [a for _, a in curve]; final = accs[-1]; thr = 0.95 * final
    sat = next((s for s, a in curve if a >= thr), curve[-1][0])
    return {"acc0": curve[0][1], "acc_final": final,
            "auc": sum(accs) / len(accs), "sat_step": sat, "n_points": len(curve)}

def save_sat(task, rec):
    data = json.loads(SAT_FILE.read_text()) if SAT_FILE.exists() else \
        {"aux": AUX_DATASET, "main": MAIN_DATA, "init": _init_tag, "seed": SEED,
         "train_steps": TRAIN_STEPS, "mix_aux": MIX_AUX, "sat_every": SAT_EVERY,
         "oversample": OVERSAMPLE, "tasks": {}}
    data["tasks"][task] = rec
    SAT_FILE.write_text(json.dumps(data, indent=2))


# ── Training-data builders (parameterized by MAIN_DATA) ─────────────────────────
def _fmt_qa(prompt, answer):
    """prompt/completion (answer-only loss) when COMPLETION_ONLY, else packed text.
    Format matches run_sft.py get_formatter: prompt = f"{prompt}\n", completion = answer+EOS."""
    if COMPLETION_ONLY:
        return {"prompt": f"{prompt}\n", "completion": f"{answer}{EOS}"}
    return {"text": f"{prompt}\n{answer}{EOS}"}

def _fmt_text(text):
    if COMPLETION_ONLY:                 # raw text: matches run_sft fw (prompt="")
        return {"prompt": "", "completion": text + EOS}
    return {"text": text + EOS}

def main_gen():
    if MAIN_LOCAL:                               # stream-free: cycle the local cache (no HF stream)
        import itertools as _it
        rows = _read_jsonl(Path(MAIN_LOCAL) / f"{MAIN_DATA}_main.jsonl")
        for r in _it.cycle(rows):
            # Dispatch by ROW content, not the global MAIN_DATA, so a BLENDED main jsonl that mixes
            # qa rows ({prompt,answer}) and raw-text rows ({text}) trains each with its correct loss
            # mask (answer-only vs full-text). Single-main jsonls are unaffected (homogeneous rows).
            if r.get("answer"):
                yield _fmt_qa(r.get("prompt", ""), r["answer"])
            elif r.get("text"):
                yield _fmt_text(r["text"][:1200])
        return
    if MAIN_DATA == "dolci":
        for x in load_dataset("tasksource/dolci-instruct", split="train", streaming=True):
            if not x.get("answer"): continue
            yield _fmt_qa(x["prompt"], x["answer"])
    elif MAIN_DATA == "flan":
        for x in load_dataset("tasksource/flan", split="train", streaming=True):
            if not x.get("answer"): continue
            yield _fmt_qa(x["prompt"], x["answer"])
    else:  # fw
        for x in load_dataset("HuggingFaceFW/fineweb-edu", split="train", streaming=True):
            yield _fmt_text(x["text"][:1200])

CONFIG_YAML = os.environ.get("CONFIG_YAML", "0") != "0"   # A/B: emit config_edition answers as YAML
def _to_yaml(ans):
    try:
        import yaml, json as _j
        return yaml.safe_dump(_j.loads(ans), default_flow_style=False, sort_keys=False).strip()
    except Exception:
        return ans

LOCAL_AUX = os.environ.get("LOCAL_AUX", "")   # path to {task:[[prompt,answer],...]} (e.g. lean_samples.json)
_local_aux = json.loads(Path(LOCAL_AUX).read_text()) if LOCAL_AUX and Path(LOCAL_AUX).exists() else None

def rc_gen_factory(task_name):
    if _local_aux is not None:                 # local instruct data (cycled), no HF stream
        def gl():
            rows = _local_aux.get(task_name, [])
            import itertools as _it
            for r in _it.cycle(rows):
                if len(r) >= 2 and r[1]: yield _fmt_qa(r[0], r[1])
        return gl
    def g():
        seen = set()
        for x in load_dataset(_AUX_HF, split="train", streaming=True):
            if (x.get("task") or "") != task_name: continue
            if not x.get("answer"): continue
            if MODE_FILTER and (x.get("mode") or "") != MODE_FILTER: continue
            p = x.get("prompt") or ""
            if DEDUP_PROMPT:
                if p in seen: continue
                seen.add(p)
            ans = x["answer"]
            if CONFIG_YAML and task_name == "config_edition": ans = _to_yaml(ans)
            yield _fmt_qa(p, ans)
    return g

def all_aux_gen():
    """Every aux example (all tasks), natural rate — the 'full mixture' component."""
    seen = set()
    for x in load_dataset(_AUX_HF, split="train", streaming=True):
        if (x.get("task") or "") in ("", "reasoning_gym"): continue
        if not x.get("answer"): continue
        p = x.get("prompt") or ""
        if DEDUP_PROMPT:
            if p in seen: continue
            seen.add(p)
        yield _fmt_qa(p, x["answer"])

def all_aux_gen_mode(mode):
    """All-tasks aux stream restricted to one answer mode (for MODE_MIX full-mixture blends)."""
    def g():
        for x in load_dataset(_AUX_HF, split="train", streaming=True):
            if (x.get("task") or "") in ("", "reasoning_gym"): continue
            if not x.get("answer"): continue
            if (x.get("mode") or "") != mode: continue
            yield _fmt_qa(x.get("prompt") or "", x["answer"])
    return g

def peer_aux_gen():
    """PEER_MIX background: only the fixed N_PEERS sampled tasks."""
    peers = list(PEER_TASKS)
    if _local_aux is not None:                 # local data (no HF stream): round-robin the peers
        import itertools as _it
        iters = [_it.cycle(_local_aux[t]) for t in peers if _local_aux.get(t)]
        if not iters: return
        for it in _it.cycle(iters):
            r = next(it)
            if len(r) >= 2 and r[1]: yield _fmt_qa(r[0], r[1])
        return
    peers = set(peers)
    seen = set()
    for x in load_dataset(_AUX_HF, split="train", streaming=True):
        if (x.get("task") or "") not in peers: continue
        if not x.get("answer"): continue
        p = x.get("prompt") or ""
        if DEDUP_PROMPT:
            if p in seen: continue
            seen.add(p)
        yield _fmt_qa(p, x["answer"])

def group_aux_gen():
    """GROUP mode: pool the CHOSEN GROUP_TASKS into ONE aux arm (round-robin, equal share each)."""
    grp = list(GROUP_TASKS)
    if _local_aux is not None:                 # local data (no HF stream): round-robin the members
        import itertools as _it
        iters = [_it.cycle(_local_aux[t]) for t in grp if _local_aux.get(t)]
        if not iters: return
        for it in _it.cycle(iters):
            r = next(it)
            if len(r) >= 2 and r[1]: yield _fmt_qa(r[0], r[1])
        return
    grp = set(grp); seen = set()
    for x in load_dataset(_AUX_HF, split="train", streaming=True):
        if (x.get("task") or "") not in grp: continue
        if not x.get("answer"): continue
        p = x.get("prompt") or ""
        if DEDUP_PROMPT:
            if p in seen: continue
            seen.add(p)
        yield _fmt_qa(p, x["answer"])

def baseline_ds():
    if PEER_MIX:     # realistic K-peer background: main + peers at MIX (peer set fixed)
        return interleave_datasets(
            [IterableDataset.from_generator(main_gen),
             IterableDataset.from_generator(peer_aux_gen)],
            probabilities=[1.0 - MIX_AUX, MIX_AUX],
            seed=SEED, stopping_strategy="first_exhausted",
        )
    if OVERSAMPLE:   # full mixture: main + all-aux at MIX
        return interleave_datasets(
            [IterableDataset.from_generator(main_gen),
             IterableDataset.from_generator(all_aux_gen)],
            probabilities=[1.0 - MIX_AUX, MIX_AUX],
            seed=SEED, stopping_strategy="first_exhausted",
        )
    return IterableDataset.from_generator(main_gen)

def mixed_ds(task_name):
    if task_name == "__ALLMIX__":   # full-mixture answer-format ablation: main + blended all-aux
        parts = [IterableDataset.from_generator(main_gen)]
        probs = [1.0 - MIX_AUX]
        for m, w in _mode_mix:
            parts.append(IterableDataset.from_generator(all_aux_gen_mode(m)))
            probs.append(MIX_AUX * w)
        return interleave_datasets(parts, probabilities=probs, seed=SEED,
                                   stopping_strategy="first_exhausted")
    # x_gen = the "X" arm: a single task, or (GROUP mode) the pooled chosen set — same downstream shape.
    x_gen = group_aux_gen if task_name == "__GROUP__" else rc_gen_factory(task_name)
    if task_name == "__GROUP__" and not OVERSAMPLE:   # group pooled, alone (no background) at total MIX
        return interleave_datasets(
            [IterableDataset.from_generator(main_gen),
             IterableDataset.from_generator(x_gen)],
            probabilities=[1.0 - MIX_AUX, MIX_AUX],
            seed=SEED, stopping_strategy="first_exhausted",
        )
    if PEER_MIX:     # upweight X (task or group) on top of fixed K-peer background; total aux = MIX
        half = MIX_AUX / 2.0
        return interleave_datasets(
            [IterableDataset.from_generator(main_gen),
             IterableDataset.from_generator(x_gen),
             IterableDataset.from_generator(peer_aux_gen)],
            probabilities=[1.0 - MIX_AUX, half, half],
            seed=SEED, stopping_strategy="first_exhausted",
        )
    if OVERSAMPLE:   # upweight X (task or group) on top of the FULL all-rc background; total aux = MIX
        x_share  = MIX_AUX * OVS_X_FRAC          # extra dose of the measured task
        bg_share = MIX_AUX * (1.0 - OVS_X_FRAC)  # all-rc background (already contains X at ~1/N)
        return interleave_datasets(
            [IterableDataset.from_generator(main_gen),
             IterableDataset.from_generator(x_gen),
             IterableDataset.from_generator(all_aux_gen)],
            probabilities=[1.0 - MIX_AUX, x_share, bg_share],
            seed=SEED, stopping_strategy="first_exhausted",
        )
    return interleave_datasets(
        [IterableDataset.from_generator(main_gen),
         IterableDataset.from_generator(x_gen)],
        probabilities=[1.0 - MIX_AUX, MIX_AUX],
        seed=SEED, stopping_strategy="first_exhausted",
    )

def train_on(ds, callbacks=None):
    cfg = dict(
        output_dir="/tmp/influence_sft", overwrite_output_dir=True,
        max_steps=TRAIN_STEPS, per_device_train_batch_size=BATCH,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LR, weight_decay=0.01,
        max_length=MAX_LEN, packing=(os.environ.get("PACKING","1")!="0"),
        bf16=(DTYPE == torch.bfloat16), report_to="none",
        save_strategy="no", logging_steps=1000, dataset_num_proc=1,
        seed=SEED, disable_tqdm=True,
        optim=os.environ.get("OPTIM", "adamw_torch"),  # OPTIM=adamw_bnb_8bit to fit ~1.7B on a 23G GPU
    )
    if os.environ.get("GRAD_CKPT", "0") == "1":
        cfg["gradient_checkpointing"] = True
        cfg["gradient_checkpointing_kwargs"] = {"use_reentrant": False}
    if COMPLETION_ONLY:                 # mask prompt — matches run_sft production
        cfg["completion_only_loss"] = True
    else:
        cfg["dataset_text_field"] = "text"
    SFTTrainer(model=model, processing_class=tok, train_dataset=ds,
               args=SFTConfig(**cfg), callbacks=callbacks).train()


# ── Resume support ──────────────────────────────────────────────────────────────
if OUT_FILE.exists():
    results = json.loads(OUT_FILE.read_text())
    print(f"♻️  Resuming — {len(results.get('tasks', {}))} task(s) done\n")
else:
    results = {"seed": SEED, "train_steps": TRAIN_STEPS, "mix_aux": MIX_AUX,
               "main_data": MAIN_DATA, "from_scratch": FROM_SCRATCH,
               "lr": LR, "batch": BATCH, "model": MODEL_NAME,
               "oversample": OVERSAMPLE, "peer_mix": PEER_MIX,
               "peer_tasks": PEER_TASKS, "n_peers": N_PEERS if PEER_MIX else 0,
               "tasks": {}, "baseline": None, "pretrained_only": None}

# Pretrained-only sanity
if results.get("pretrained_only") is None:
    (pb, pd, pf, pex), px = eval_all(); save_perex("pretrained_only", px)
    print(f"📏 Pre-training eval: BBH={pb:.4f}  Dolci={pd:.4f}  FW={pf:.4f}"
          + "".join(f"  {k}={v:.4f}" for k, v in pex.items()) + "\n")
    results["pretrained_only"] = {"bbh_nll": pb, "dolci_nll": pd, "fw_nll": pf}
    for k, v in pex.items(): results["pretrained_only"][f"{k}_nll"] = v
    OUT_FILE.write_text(json.dumps(results, indent=2))

# Baseline: train on MAIN_DATA only
if results.get("baseline") is None:
    print(f"🏃 Baseline: train on {MAIN_DATA} only ({TRAIN_STEPS} steps)…")
    t0 = time.time(); reset_model()
    _bl_cb = None
    if CKPT_EVAL:
        _bl_curve = []; _bl_cb = [CkptEvalCB(_bl_curve)]
    train_on(baseline_ds(), callbacks=_bl_cb)
    if CKPT_EVAL: save_ckpt("baseline", _bl_curve)
    (b_bbh, b_dolci, b_fw, b_ex), px = eval_all(); save_perex("baseline", px)
    dt = time.time() - t0
    print(f"  BBH={b_bbh:.4f}  Dolci={b_dolci:.4f}  FW={b_fw:.4f}"
          + "".join(f"  {k}={v:.4f}" for k, v in b_ex.items()) + f"  ({dt:.0f}s)\n")
    results["baseline"] = {"bbh_nll": b_bbh, "dolci_nll": b_dolci, "fw_nll": b_fw}
    for k, v in b_ex.items(): results["baseline"][f"{k}_nll"] = v
    OUT_FILE.write_text(json.dumps(results, indent=2))
else:
    b_bbh, b_dolci, b_fw = (results["baseline"]["bbh_nll"],
                            results["baseline"]["dolci_nll"],
                            results["baseline"]["fw_nll"])
    b_ex = {k: results["baseline"][f"{k}_nll"] for k in EXTRA_EVALS if f"{k}_nll" in results["baseline"]}
    print(f"📏 Baseline (cached): BBH={b_bbh:.4f}  Dolci={b_dolci:.4f}  FW={b_fw:.4f}"
          + "".join(f"  {k}={v:.4f}" for k, v in b_ex.items()) + "\n")


# Per-task loop
for i, task in enumerate(ALL_TASKS):
    if task in results["tasks"]:
        print(f"[{i+1}/{len(ALL_TASKS)}] {task} — already done"); continue
    if _local_aux is not None and task not in ("__ALLMIX__", "__GROUP__") and not _local_aux.get(task):
        print(f"[{i+1}/{len(ALL_TASKS)}] {task} — SKIP (no aux rows; slow-gen skipped upstream)")
        continue
    t0 = time.time(); reset_model()
    sat_cbs, sat_curve = None, None
    if LOG_SAT:
        sat_rows = sat_eval_rows(task)
        if len(sat_rows) >= 5:
            sat_curve = [[0, token_acc(sat_rows)]]
            sat_cbs = [SatCurveCB(sat_rows, sat_curve)]
    ckpt_curve = None
    if CKPT_EVAL:
        ckpt_curve = []; sat_cbs = (sat_cbs or []) + [CkptEvalCB(ckpt_curve)]
    train_on(mixed_ds(task), callbacks=sat_cbs)
    if ckpt_curve is not None: save_ckpt(task, ckpt_curve)
    (m_bbh, m_dolci, m_fw, m_ex), px = eval_all(); save_perex(task, px)
    if sat_curve is not None:
        rec = {"curve": sat_curve}; rec.update(derive_sat(sat_curve)); save_sat(task, rec)
    dt = time.time() - t0
    results["tasks"][task] = {
        "bbh_nll": m_bbh, "dolci_nll": m_dolci, "fw_nll": m_fw,
        "bbh_delta":   m_bbh - b_bbh,
        "dolci_delta": m_dolci - b_dolci,
        "fw_delta":    m_fw - b_fw,
    }
    for k, v in m_ex.items():
        if k in b_ex:
            results["tasks"][task][f"{k}_nll"]   = v
            results["tasks"][task][f"{k}_delta"] = v - b_ex[k]
    OUT_FILE.write_text(json.dumps(results, indent=2))
    print(f"[{i+1:2d}/{len(ALL_TASKS)}] {task:<26s}  "
          f"BBH Δ={m_bbh-b_bbh:+.4f}  Dolci Δ={m_dolci-b_dolci:+.4f}  "
          f"FW Δ={m_fw-b_fw:+.4f}"
          + "".join(f"  {k}Δ={m_ex[k]-b_ex[k]:+.4f}" for k in m_ex if k in b_ex)
          + f"  ({dt:.0f}s)")

print(f"\n✅ Done → {OUT_FILE}")
