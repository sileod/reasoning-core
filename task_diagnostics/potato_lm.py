#!/usr/bin/env python3
"""Tiny cue-conditioned BPE GRU answer LM for shortcut probing."""

from __future__ import annotations

import argparse, contextlib, io, json, os, re, sys, tempfile, time
from collections import Counter, defaultdict

os.environ.setdefault("KERAS_BACKEND", "torch")

import keras
import numpy as np
import sentencepiece as spm
from datasets import load_dataset
from sklearn.feature_extraction.text import CountVectorizer

TOK = re.compile(r"(?u)\b[\w./+*<>=-]{2,}\b")


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


def encode_answers_char(answers, max_len, vocab_size):
    chars = [c for a in answers for c in a]
    vocab = ["<pad>", "<bos>", "<eos>", "<unk>"] + [c for c, _ in Counter(chars).most_common(vocab_size - 4)]
    stoi = {c: i for i, c in enumerate(vocab)}
    y = np.zeros((len(answers), max_len), dtype=np.int64)
    for i, a in enumerate(answers):
        ids = [1] + [stoi.get(c, 3) for c in a[: max_len - 2]] + [2]
        y[i, : len(ids)] = ids
    def decode(ids):
        return "".join(vocab[i] for i in ids if i > 3)
    return y, vocab, decode


def train_bpe(answers, vocab_size):
    buf = io.BytesIO()
    with open(os.devnull, "w") as devnull, contextlib.redirect_stderr(devnull):
        spm.SentencePieceTrainer.train(
            sentence_iterator=iter(answers),
            model_writer=buf,
            vocab_size=vocab_size,
            model_type="bpe",
            pad_id=0,
            bos_id=1,
            eos_id=2,
            unk_id=3,
            character_coverage=1.0,
            train_extremely_large_corpus=False,
            hard_vocab_limit=False,
        )
    return buf.getvalue()


def encode_answers_bpe(answers, max_len, vocab_size, proto=None):
    proto = proto or train_bpe(answers, vocab_size)
    sp = spm.SentencePieceProcessor(model_proto=proto)
    y = np.zeros((len(answers), max_len), dtype=np.int64)
    for i, a in enumerate(answers):
        ids = [1] + sp.encode(str(a), out_type=int)[: max_len - 2] + [2]
        y[i, : len(ids)] = ids
    return y, [sp.id_to_piece(i) for i in range(sp.get_piece_size())], sp.decode, proto


def encode_answers(answers, args):
    if args.tokenizer == "char":
        y, vocab, decode = encode_answers_char(answers, args.max_len, args.vocab_size)
        return y, vocab, decode, None
    try:
        return encode_answers_bpe(answers, args.max_len, args.vocab_size, getattr(args, "bpe_proto", None))
    except Exception as e:
        if not args.bpe_fallback:
            raise
        print(f"bpe_fallback={type(e).__name__}: {e}", file=sys.stderr, flush=True)
        y, vocab, decode = encode_answers_char(answers, args.max_len, min(args.vocab_size, 256))
        return y, vocab, decode, None


class StopAfter(keras.callbacks.Callback):
    def __init__(self, seconds):
        self.deadline = time.time() + seconds

    def on_epoch_end(self, epoch, logs=None):
        if time.time() > self.deadline:
            self.model.stop_training = True


def projected_loss(allowed, penalty):
    keep = np.zeros(int(max(allowed)) + 1, dtype="float32")
    keep[allowed] = 1.0
    loss = keras.losses.SparseCategoricalCrossentropy(from_logits=True)

    def fn(y_true, y_pred):
        if len(keep) < int(y_pred.shape[-1]):
            pad = np.zeros(int(y_pred.shape[-1]) - len(keep), dtype="float32")
            mask = keras.ops.convert_to_tensor(np.concatenate([keep, pad]))
        else:
            mask = keras.ops.convert_to_tensor(keep[: int(y_pred.shape[-1])])
        return loss(y_true, y_pred - (1.0 - mask) * penalty)

    return fn


def make_model(vocab, h=64, cue_dim=0, allowed=None, projection_penalty=20.0):
    y = keras.Input((None,), dtype="int32", name="answer")
    z = keras.layers.Embedding(vocab, h, mask_zero=True, name="tok_emb")(y)
    if cue_dim:
        cue = keras.Input((cue_dim,), name="cue")
        h0 = keras.layers.Dense(h, activation="tanh", name="cue_h0")(cue)
        z = keras.layers.GRU(h, return_sequences=True, name="answer_gru")(z, initial_state=h0)
        inputs = [cue, y]
    else:
        z = keras.layers.GRU(h, return_sequences=True, name="answer_gru")(z)
        inputs = y
    out = keras.layers.Dense(vocab, name="tok_out")(z)
    model = keras.Model(inputs, out)
    loss = projected_loss(allowed, projection_penalty) if allowed is not None else keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    model.compile(keras.optimizers.AdamW(learning_rate=3e-3), loss)
    return model


def copy_decoder(dst, src):
    for name in ("tok_emb", "answer_gru", "tok_out"):
        dst.get_layer(name).set_weights(src.get_layer(name).get_weights())


def task_vocab_ids(Y, tr):
    ids = set(np.unique(Y[tr]).tolist()) | {0, 1, 2, 3}
    return np.asarray(sorted(i for i in ids if i >= 0), dtype=np.int64)


def eval_loss(model, X, Y, idx, conditioned, allowed=None):
    return float(example_nll(model, X, Y, idx, conditioned, allowed).mean())


def keras_eval_loss(model, X, Y, idx, conditioned):
    yin, yout = Y[:, :-1], Y[:, 1:]
    sw = (yout != 0).astype("float32")
    test_in = [X[idx], yin[idx]] if conditioned else yin[idx]
    return float(model.evaluate(test_in, yout[idx], sample_weight=sw[idx], verbose=0))


def example_nll(model, X, Y, idx, conditioned, allowed=None, penalty=20.0):
    yin, yout = Y[:, :-1], Y[:, 1:]
    test_in = [X[idx], yin[idx]] if conditioned else yin[idx]
    logits = np.asarray(model.predict(test_in, batch_size=256, verbose=0))
    if allowed is not None:
        keep = np.zeros(logits.shape[-1], dtype=bool)
        keep[allowed] = True
        logits[..., ~keep] -= penalty
    logits = logits - logits.max(-1, keepdims=True)
    logp = logits - np.log(np.exp(logits).sum(-1, keepdims=True))
    gold = yout[idx]
    mask = gold != 0
    tok = np.take_along_axis(logp, gold[..., None], -1).squeeze(-1)
    return -(tok * mask).sum(1) / np.maximum(mask.sum(1), 1)


def fit_eval(X, Y, vocab, args, conditioned, init_model=None):
    n = len(Y)
    rng = np.random.default_rng(args.seed)
    te = rng.choice(n, max(1, int(n * args.test_size)), replace=False)
    tr = np.setdiff1d(np.arange(n), te)
    allowed = task_vocab_ids(Y, tr) if (args.project_vocab or args.train_project_vocab) else None
    train_allowed = allowed if args.train_project_vocab else None
    model = make_model(len(vocab), args.hidden, X.shape[1] if conditioned else 0, train_allowed, args.projection_penalty)
    if init_model is not None:
        copy_decoder(model, init_model)
    model.optimizer.learning_rate = args.lr
    yin, yout = Y[:, :-1], Y[:, 1:]
    sw = (yout != 0).astype("float32")
    train_in = [X[tr], yin[tr]] if conditioned else yin[tr]
    model.fit(
        train_in, yout[tr], sample_weight=sw[tr],
        epochs=args.epochs, batch_size=args.batch_size, verbose=0,
        callbacks=[StopAfter(args.seconds_per_task / 2)],
    )
    eval_allowed = allowed if args.project_vocab else None
    return eval_loss(model, X, Y, te, conditioned), eval_loss(model, X, Y, te, conditioned, eval_allowed), model, te, eval_allowed


def ablated_cues(model, X, Y, te, names, args):
    if args.ablate_cues <= 0:
        return ""
    w = np.abs(model.get_layer("cue_h0").get_weights()[0]).sum(1)
    base = eval_loss(model, X, Y, te, True)
    cand = np.argsort(w)[-min(args.ablate_cues, len(w)):][::-1]
    rows = []
    for j in cand:
        x0 = X.copy()
        x0[:, j] = 0
        rows.append((eval_loss(model, x0, Y, te, True) - base, names[j]))
    return ", ".join(f"{name}:{delta:+.3f}" for delta, name in sorted(rows, reverse=True)[:args.top_cues])


def mine_rules(X, te, gain, names, args):
    high = gain >= np.quantile(gain, args.rule_quantile)
    base = high.mean()
    rows = []
    Xt = X[te] > 0
    for j, name in enumerate(names):
        on = Xt[:, j]
        sup = on.mean()
        if sup < args.min_rule_support or not on.any():
            continue
        prec = high[on].mean()
        rows.append((prec / max(base, 1e-9), prec, sup, name))
    return ", ".join(
        f"{name}:prec={prec:.2f},sup={sup:.2f},lift={lift:.1f}"
        for lift, prec, sup, name in sorted(rows, reverse=True)[:args.top_rules]
    )


def greedy_decode(model, X, idx, decode, args):
    preds = []
    for i in idx:
        ids = [1]
        for _ in range(args.gen_len - 1):
            y = np.asarray([ids], dtype=np.int64)
            logits = np.asarray(model.predict([X[[i]], y], verbose=0))[0, -1]
            nxt = int(logits.argmax())
            if nxt in (0, 2):
                break
            ids.append(nxt)
        preds.append(decode(ids[1:]))
    return preds


def pretrain_answer_lm(rows_by_task, args):
    answers = [a for rows in rows_by_task.values() for _, a in rows]
    Y, vocab, _, _ = encode_answers(answers, args)
    model = make_model(len(vocab), args.hidden, 0)
    model.optimizer.learning_rate = args.pretrain_lr
    yin, yout = Y[:, :-1], Y[:, 1:]
    sw = (yout != 0).astype("float32")
    model.fit(
        yin, yout, sample_weight=sw,
        epochs=args.pretrain_epochs, batch_size=args.batch_size, verbose=0,
        callbacks=[StopAfter(args.pretrain_seconds)],
    )
    return model


def run_task(task, rows, args, init_model=None):
    prompts, answers = zip(*rows)
    vec = CountVectorizer(token_pattern=r"(?u)\b[\w:./+*<>=-]{2,}\b", ngram_range=(1, 2),
                          min_df=2, max_features=args.max_cues, binary=True)
    X = vec.fit_transform(prompts).astype("float32").toarray()
    Y, vocab, decode, _ = encode_answers(answers, args)
    base, base_proj, base_model, te, allowed = fit_eval(X, Y, vocab, args, False, init_model)
    cond, cond_proj, model, te, allowed = fit_eval(X, Y, vocab, args, True, init_model)
    base_ex = example_nll(base_model, X, Y, te, False)
    cond_ex = example_nll(model, X, Y, te, True)
    base_ex_proj = example_nll(base_model, X, Y, te, False, allowed, args.projection_penalty) if allowed is not None else base_ex
    cond_ex_proj = example_nll(model, X, Y, te, True, allowed, args.projection_penalty) if allowed is not None else cond_ex
    gain_ex = base_ex - cond_ex
    gain_ex_proj = base_ex_proj - cond_ex_proj
    preds = greedy_decode(model, X, te, decode, args)
    exact = np.mean([p.strip() == answers[i].strip() for p, i in zip(preds, te)])
    names = np.asarray(vec.get_feature_names_out())
    cues = ablated_cues(model, X, Y, te, names, args)
    rules = mine_rules(X, te, gain_ex, names, args)
    top_pos = np.argsort(gain_ex)[-args.keep_examples:][::-1]
    examples = [(task, int(te[j]), float(gain_ex[j]), prompts[te[j]], answers[te[j]], preds[j]) for j in top_pos]
    qs = np.quantile(gain_ex, [0.5, 0.9, 0.95])
    return task, len(rows), len(vocab), base, cond, base - cond, base_proj, cond_proj, base_proj - cond_proj, gain_ex.mean(), gain_ex_proj.mean(), *qs, (gain_ex > args.gain_threshold).mean(), exact, cues, rules, examples


def save_artifacts(args, rows_by_task, bpe_proto, init_model):
    if not args.save_dir:
        return
    os.makedirs(args.save_dir, exist_ok=True)
    cfg = {k: v for k, v in vars(args).items() if k != "bpe_proto"} | {"tasks": sorted(rows_by_task)}
    with open(os.path.join(args.save_dir, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2, default=str)
    if bpe_proto:
        open(os.path.join(args.save_dir, "tok.model"), "wb").write(bpe_proto)
    if init_model is not None:
        init_model.save(os.path.join(args.save_dir, "answer_lm.keras"))
    readme = """# Shallow Predictor for Reasoning Core

Small cue-conditioned GRU probe for estimating whether shallow prompt-derived cues improve answer likelihood on Reasoning Core tasks.

This is an analysis artifact, not a solver model. Use the NLL gain over an unconditional answer LM, plus the emitted high-gain examples and distilled rules, to identify candidate shortcut pockets for generator balancing.
"""
    open(os.path.join(args.save_dir, "README.md"), "w").write(readme)


def push_to_hub(args):
    if not args.push_to_hub:
        return
    from huggingface_hub import HfApi
    api = HfApi()
    api.create_repo(args.push_to_hub, repo_type="model", exist_ok=True)
    api.upload_folder(repo_id=args.push_to_hub, repo_type="model", folder_path=args.save_dir)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset", default="reasoning-core/procedural-pretraining-pile")
    p.add_argument("--split", default="train")
    p.add_argument("--modes", default="instruct")
    p.add_argument("--tasks", default="")
    p.add_argument("--max-examples", type=int, default=8_000)
    p.add_argument("--scan-limit", type=int, default=200_000)
    p.add_argument("--per-task", type=int, default=400)
    p.add_argument("--min-examples", type=int, default=80)
    p.add_argument("--seconds-per-task", type=float, default=60)
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--pretrain-epochs", type=int, default=0)
    p.add_argument("--pretrain-seconds", type=float, default=300)
    p.add_argument("--pretrain-lr", type=float, default=3e-3)
    p.add_argument("--shared-tokenizer", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument("--project-vocab", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument("--train-project-vocab", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument("--projection-penalty", type=float, default=20.0)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--hidden", type=int, default=64)
    p.add_argument("--tokenizer", choices=["bpe", "char"], default="bpe")
    p.add_argument("--vocab-size", type=int, default=512)
    p.add_argument("--bpe-fallback", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--max-len", type=int, default=128)
    p.add_argument("--gen-len", type=int, default=128)
    p.add_argument("--max-cues", type=int, default=512)
    p.add_argument("--ablate-cues", type=int, default=64)
    p.add_argument("--top-cues", type=int, default=8)
    p.add_argument("--test-size", type=float, default=0.25)
    p.add_argument("--lr", type=float, default=3e-3)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--gain-threshold", type=float, default=0.5)
    p.add_argument("--rule-quantile", type=float, default=0.9)
    p.add_argument("--min-rule-support", type=float, default=0.05)
    p.add_argument("--top-rules", type=int, default=8)
    p.add_argument("--keep-examples", type=int, default=5)
    p.add_argument("--examples-out", default="")
    p.add_argument("--save-dir", default="")
    p.add_argument("--push-to-hub", default="")
    args = p.parse_args()
    keras.utils.set_random_seed(args.seed)
    rows_by_task = collect(args)
    bpe_proto = None
    if args.shared_tokenizer and args.tokenizer == "bpe":
        bpe_proto = train_bpe([a for rows in rows_by_task.values() for _, a in rows], args.vocab_size)
        args.bpe_proto = bpe_proto
    init_model = pretrain_answer_lm(rows_by_task, args) if args.pretrain_epochs > 0 else None
    save_artifacts(args, rows_by_task, bpe_proto, init_model)
    ex_f = open(args.examples_out, "w", encoding="utf-8") if args.examples_out else None
    if ex_f:
        print("task\tidx\tgain\tanswer\tprediction\tprompt", file=ex_f)
    print("task\tn\tvocab\tbase_nll\tcue_nll\tgain\tbase_proj\tcue_proj\tgain_proj\tmean_ex_gain\tmean_ex_gain_proj\tp50\tp90\tp95\tfrac_gt\texact\ttop_cues\trules")
    for task, rows in sorted(rows_by_task.items()):
        if len(rows) < args.min_examples:
            continue
        try:
            *vals, examples = run_task(task, rows, args, init_model)
            print("%s\t%d\t%d\t%.3f\t%.3f\t%+.3f\t%.3f\t%.3f\t%+.3f\t%+.3f\t%+.3f\t%+.3f\t%+.3f\t%+.3f\t%.2f\t%.2f\t%s\t%s" % tuple(vals), flush=True)
            if ex_f:
                for t, i, g, ptxt, ans, pred in examples:
                    clean = lambda s: str(s).replace("\t", " ").replace("\n", "\\n")[:2000]
                    print(f"{t}\t{i}\t{g:.4f}\t{clean(ans)}\t{clean(pred)}\t{clean(ptxt)}", file=ex_f, flush=True)
        except Exception as e:
            print(f"{task}\tSKIP\t{type(e).__name__}: {e}", file=sys.stderr, flush=True)
    if ex_f:
        ex_f.close()
    if args.push_to_hub:
        push_to_hub(args)


if __name__ == "__main__":
    main(); sys.stdout.flush(); sys.stderr.flush(); os._exit(0)
