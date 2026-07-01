#!/usr/bin/env python3
"""Tiny T5 shallow-cue answer probe for shortcut mining."""

from __future__ import annotations

import argparse, contextlib, io, os, sys, time
from collections import Counter, defaultdict

import numpy as np
import sentencepiece as spm
import torch
from datasets import load_dataset
from sklearn.feature_extraction.text import CountVectorizer
from transformers import T5Config, T5ForConditionalGeneration


def collect(args):
    want = set(args.tasks.split(",")) if args.tasks else None
    rows, counts = defaultdict(list), Counter()
    for seen, ex in enumerate(load_dataset(args.dataset, split=args.split, streaming=True), 1):
        if seen > args.scan_limit:
            break
        if ex.get("mode") not in set(args.modes.split(",")):
            continue
        task = ex.get("task")
        if not task or (want and task not in want) or counts[task] >= args.per_task:
            continue
        counts[task] += 1
        rows[task].append((str(ex.get("prompt") or ""), str(ex.get("answer") or "")))
        if sum(counts.values()) >= args.max_examples:
            break
    return rows


def train_bpe(texts, vocab_size):
    buf = io.BytesIO()
    with open(os.devnull, "w") as devnull, contextlib.redirect_stderr(devnull):
        spm.SentencePieceTrainer.train(
            sentence_iterator=iter(texts), model_writer=buf, vocab_size=vocab_size,
            model_type="bpe", pad_id=0, bos_id=1, eos_id=2, unk_id=3,
            character_coverage=1.0, hard_vocab_limit=False,
        )
    return spm.SentencePieceProcessor(model_proto=buf.getvalue())


def enc(sp, texts, max_len):
    x = np.zeros((len(texts), max_len), dtype=np.int64)
    for i, s in enumerate(texts):
        ids = [1] + sp.encode(str(s), out_type=int)[: max_len - 2] + [2]
        x[i, :len(ids)] = ids
    return x


def cue_texts(prompts, args):
    vec = CountVectorizer(token_pattern=r"(?u)\b[\w:./+*<>=-]{2,}\b", ngram_range=(1, 2),
                          min_df=2, max_features=args.max_cues, binary=True)
    X = vec.fit_transform(prompts).astype(bool)
    names = np.asarray(vec.get_feature_names_out())
    texts = ["cues: " + " ".join(names[X[i].toarray()[0]]) for i in range(X.shape[0])]
    return texts, X.astype("float32").toarray(), names


def make_t5(vocab, args):
    cfg = T5Config(
        vocab_size=vocab, d_model=args.d_model, d_ff=args.d_ff, num_layers=args.layers,
        num_decoder_layers=args.layers, num_heads=args.heads, dropout_rate=args.dropout,
        pad_token_id=0, decoder_start_token_id=0, eos_token_id=2,
    )
    return T5ForConditionalGeneration(cfg).to(args.device)


def batches(ix, bs):
    for i in range(0, len(ix), bs):
        yield ix[i:i + bs]


def fit(model, X, Y, tr, args, epochs=None, seconds=None):
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    labels = Y.copy()
    labels[labels == 0] = -100
    deadline = time.time() + (args.seconds_per_model if seconds is None else seconds)
    model.train()
    for _ in range(args.epochs if epochs is None else epochs):
        for b in batches(np.random.permutation(tr), args.batch_size):
            xb = torch.tensor(X[b], device=args.device)
            yb = torch.tensor(labels[b], device=args.device)
            loss = model(input_ids=xb, attention_mask=xb.ne(0), labels=yb).loss
            opt.zero_grad(); loss.backward(); opt.step()
        if time.time() > deadline:
            break


@torch.no_grad()
def nll(model, X, Y, ix, args):
    labels = Y.copy()
    labels[labels == 0] = -100
    out = []
    model.eval()
    for b in batches(ix, args.batch_size):
        xb = torch.tensor(X[b], device=args.device)
        yb = torch.tensor(labels[b], device=args.device)
        logits = model(input_ids=xb, attention_mask=xb.ne(0), labels=yb).logits[:, :-1]
        gold = torch.tensor(Y[b, 1:], device=args.device)
        mask = gold.ne(0)
        lp = logits.log_softmax(-1).gather(-1, gold[..., None]).squeeze(-1)
        out.extend((-(lp * mask).sum(1) / mask.sum(1).clamp_min(1)).cpu().numpy().tolist())
    return np.asarray(out)


@torch.no_grad()
def greedy(model, X, ix, sp, args):
    model.eval()
    preds = []
    for i in ix:
        xb = torch.tensor(X[[i]], device=args.device)
        y = model.generate(input_ids=xb, attention_mask=xb.ne(0), max_new_tokens=args.gen_len)
        ids = [int(t) for t in y[0].cpu().tolist() if int(t) not in (0, 1, 2)]
        preds.append(sp.decode(ids))
    return preds


def mine_rules(X, te, gain, names, args):
    high = gain >= np.quantile(gain, args.rule_quantile)
    base, rows, Xt = high.mean(), [], X[te] > 0
    for j, name in enumerate(names):
        on = Xt[:, j]
        if on.mean() < args.min_rule_support or not on.any():
            continue
        prec = high[on].mean()
        rows.append((prec / max(base, 1e-9), prec, on.mean(), name))
    return ", ".join(f"{n}:prec={p:.2f},sup={s:.2f},lift={l:.1f}" for l, p, s, n in sorted(rows, reverse=True)[:args.top_rules])


def run_task(task, rows, args, ex_f):
    prompts, answers = zip(*rows)
    cues, Xbin, names = cue_texts(prompts, args)
    sp = train_bpe(list(cues) + list(answers) + ["base"], args.vocab_size)
    Xc, Xb = enc(sp, cues, args.max_input_len), enc(sp, ["base"] * len(cues), args.max_input_len)
    Y = enc(sp, answers, args.max_answer_len)
    rng = np.random.default_rng(args.seed)
    te = rng.choice(len(Y), max(1, int(len(Y) * args.test_size)), replace=False)
    tr = np.setdiff1d(np.arange(len(Y)), te)
    base, cue = make_t5(sp.get_piece_size(), args), make_t5(sp.get_piece_size(), args)
    if args.pretrain_epochs:
        init = make_t5(sp.get_piece_size(), args)
        fit(init, Xb, Y, tr, args, args.pretrain_epochs, args.pretrain_seconds)
        base.load_state_dict(init.state_dict())
        cue.load_state_dict(init.state_dict())
    fit(base, Xb, Y, tr, args); fit(cue, Xc, Y, tr, args)
    nb, nc = nll(base, Xb, Y, te, args), nll(cue, Xc, Y, te, args)
    gain = nb - nc
    preds = greedy(cue, Xc, te, sp, args)
    exact = np.mean([p.strip() == answers[i].strip() for p, i in zip(preds, te)])
    qs = np.quantile(gain, [0.5, 0.9, 0.95])
    rules = mine_rules(Xbin, te, gain, names, args)
    print(f"{task}\t{len(rows)}\t{sp.get_piece_size()}\t{nb.mean():.3f}\t{nc.mean():.3f}\t{gain.mean():+.3f}\t{qs[0]:+.3f}\t{qs[1]:+.3f}\t{qs[2]:+.3f}\t{(gain>args.gain_threshold).mean():.2f}\t{exact:.2f}\t{rules}", flush=True)
    if ex_f:
        for j in np.argsort(gain)[-args.keep_examples:][::-1]:
            clean = lambda s: str(s).replace("\t", " ").replace("\n", "\\n")[:2000]
            print(f"{task}\t{int(te[j])}\t{gain[j]:.4f}\t{clean(answers[te[j]])}\t{clean(preds[j])}\t{clean(prompts[te[j]])}", file=ex_f, flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset", default="reasoning-core/procedural-pretraining-pile")
    p.add_argument("--split", default="train")
    p.add_argument("--modes", default="instruct")
    p.add_argument("--tasks", default="")
    p.add_argument("--max-examples", type=int, default=2000)
    p.add_argument("--scan-limit", type=int, default=500000)
    p.add_argument("--per-task", type=int, default=120)
    p.add_argument("--min-examples", type=int, default=60)
    p.add_argument("--vocab-size", type=int, default=512)
    p.add_argument("--max-cues", type=int, default=384)
    p.add_argument("--max-input-len", type=int, default=192)
    p.add_argument("--max-answer-len", type=int, default=128)
    p.add_argument("--gen-len", type=int, default=64)
    p.add_argument("--d-model", type=int, default=64)
    p.add_argument("--d-ff", type=int, default=128)
    p.add_argument("--layers", type=int, default=1)
    p.add_argument("--heads", type=int, default=2)
    p.add_argument("--dropout", type=float, default=0.0)
    p.add_argument("--epochs", type=int, default=8)
    p.add_argument("--pretrain-epochs", type=int, default=0)
    p.add_argument("--pretrain-seconds", type=float, default=30)
    p.add_argument("--seconds-per-model", type=float, default=25)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--lr", type=float, default=3e-3)
    p.add_argument("--test-size", type=float, default=0.25)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--gain-threshold", type=float, default=0.5)
    p.add_argument("--rule-quantile", type=float, default=0.9)
    p.add_argument("--min-rule-support", type=float, default=0.05)
    p.add_argument("--top-rules", type=int, default=8)
    p.add_argument("--keep-examples", type=int, default=5)
    p.add_argument("--examples-out", default="")
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = p.parse_args()
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    ex_f = open(args.examples_out, "w", encoding="utf-8") if args.examples_out else None
    if ex_f:
        print("task\tidx\tgain\tanswer\tprediction\tprompt", file=ex_f)
    print("task\tn\tvocab\tbase_nll\tcue_nll\tgain\tp50\tp90\tp95\tfrac_gt\texact\trules", flush=True)
    for task, rows in sorted(collect(args).items()):
        if len(rows) >= args.min_examples:
            try:
                run_task(task, rows, args, ex_f)
            except Exception as e:
                print(f"{task}\tSKIP\t{type(e).__name__}: {e}", file=sys.stderr, flush=True)
    if ex_f:
        ex_f.close()


if __name__ == "__main__":
    main()
