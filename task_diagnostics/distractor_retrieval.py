#!/usr/bin/env python3
"""Cheap lexical distractor retrieval with low-bit SimHash buckets."""

from __future__ import annotations

import json
import os
import random
import re
from dataclasses import dataclass

import mmh3
import numpy as np


_WS_RE = re.compile(r"\s+")


def _norm(text) -> str:
    return _WS_RE.sub(" ", str(text or "").lower()).strip()


class DistractorRetrieval:
    """Array-backed inverted buckets over low-dimensional char-ngram SimHash."""

    def __init__(
        self,
        texts=None,
        n_bits: int = 12,
        ngram_range: tuple[int, int] = (3, 5),
        seed: int = 0,
        store_texts: bool = False,
    ):
        if not (1 <= int(n_bits) <= 16):
            raise ValueError("n_bits must be in [1, 16] so codes fit in uint16")
        self.n_bits = int(n_bits)
        self.ngram_range = tuple(int(x) for x in ngram_range)
        self.seed = int(seed)
        self.store_texts = bool(store_texts)
        self.texts = None
        self.codes = None
        self.counts = None
        self.offsets = None
        self.ids = None
        self._neighbors = {}
        if texts is not None:
            self.fit(texts)

    @property
    def n_docs(self) -> int:
        return 0 if self.codes is None else int(self.codes.shape[0])

    @property
    def n_buckets(self) -> int:
        return 1 << self.n_bits

    def _ngrams(self, text: str):
        padded = f" {_norm(text)} "
        lo, hi = self.ngram_range
        emitted = False
        for n in range(lo, hi + 1):
            stop = len(padded) - n + 1
            for i in range(max(0, stop)):
                emitted = True
                yield padded[i:i + n]
        if not emitted:
            yield padded

    def encode_one(self, text) -> int:
        acc = [0] * self.n_bits
        for gram in self._ngrams(text):
            h = mmh3.hash64(gram, seed=self.seed, signed=False)[0]
            for bit in range(self.n_bits):
                acc[bit] += 1 if (h >> bit) & 1 else -1
        code = 0
        for bit, val in enumerate(acc):
            if val >= 0:
                code |= 1 << bit
        return code

    def encode(self, texts, batch_size: int = 100_000) -> np.ndarray:
        try:
            n = len(texts)
        except TypeError:
            texts = list(texts)
            n = len(texts)
        out = np.empty(n, dtype=np.uint16)
        for start in range(0, n, max(1, int(batch_size))):
            end = min(start + int(batch_size), n)
            for j, text in enumerate(texts[start:end], start):
                out[j] = self.encode_one(text)
        return out

    def fit(self, texts):
        if self.store_texts:
            texts = list(texts)
            self.texts = texts
        self.codes = self.encode(texts)
        self.counts = np.bincount(self.codes, minlength=self.n_buckets).astype(np.int64, copy=False)
        self.offsets = np.empty(self.n_buckets + 1, dtype=np.int64)
        self.offsets[0] = 0
        np.cumsum(self.counts, out=self.offsets[1:])
        id_dtype = np.uint32 if self.n_docs < (1 << 32) else np.uint64
        self.ids = np.empty(self.n_docs, dtype=id_dtype)
        cursor = self.offsets[:-1].copy()
        for doc_id, code in enumerate(self.codes):
            pos = cursor[int(code)]
            self.ids[pos] = doc_id
            cursor[int(code)] += 1
        return self

    def _codes_within_radius(self, code: int, radius: int) -> np.ndarray:
        radius = int(radius)
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self.n_bits:
            radius = self.n_bits
        key = (int(code), radius)
        cached = self._neighbors.get(key)
        if cached is not None:
            return cached

        vals = [int(code)]
        masks = [1 << i for i in range(self.n_bits)]
        if radius >= 1:
            vals.extend(int(code) ^ m for m in masks)
        if radius >= 2:
            for i in range(self.n_bits):
                mi = masks[i]
                for j in range(i + 1, self.n_bits):
                    vals.append(int(code) ^ mi ^ masks[j])
        if radius >= 3:
            import itertools

            for r in range(3, radius + 1):
                for combo in itertools.combinations(masks, r):
                    mask = 0
                    for m in combo:
                        mask ^= m
                    vals.append(int(code) ^ mask)
        out = np.asarray(vals, dtype=np.uint16)
        self._neighbors[key] = out
        return out

    def query_code(self, code: int, k: int = 16, exclude=None, radius: int = 0, rng=None) -> np.ndarray:
        if self.ids is None:
            raise RuntimeError("fit must be called before query")
        k = int(k)
        if k <= 0:
            return np.empty(0, dtype=self.ids.dtype)
        gen = np.random.default_rng(rng)
        codes = self._codes_within_radius(int(code), radius)
        total = int(self.counts[codes].sum())
        if total == 0:
            return np.empty(0, dtype=self.ids.dtype)

        candidates = np.empty(total, dtype=self.ids.dtype)
        pos = 0
        for code in codes:
            start, end = int(self.offsets[int(code)]), int(self.offsets[int(code) + 1])
            n = end - start
            if n:
                candidates[pos:pos + n] = self.ids[start:end]
                pos += n
        if pos != total:
            candidates = candidates[:pos]

        if exclude is not None and candidates.size:
            if np.isscalar(exclude):
                candidates = candidates[candidates != int(exclude)]
            else:
                excluded = np.asarray(list(exclude), dtype=candidates.dtype)
                if excluded.size:
                    candidates = candidates[~np.isin(candidates, excluded, assume_unique=False)]

        if candidates.size <= k:
            return gen.permutation(candidates)
        take = gen.choice(candidates.size, size=k, replace=False)
        return candidates[take]

    def query(self, text, k: int = 16, exclude=None, radius: int = 0, rng=None) -> np.ndarray:
        return self.query_code(self.encode_one(text), k=k, exclude=exclude, radius=radius, rng=rng)

    def batch_query(self, texts, k: int = 16, exclude=None, radius: int = 0, rng=None) -> list[np.ndarray]:
        gen = np.random.default_rng(rng)
        codes = self.encode(texts)
        out = []
        for i, code in enumerate(codes):
            ex = None if exclude is None else (exclude[i] if isinstance(exclude, (list, tuple)) else exclude)
            out.append(self.query_code(int(code), k=k, exclude=ex, radius=radius, rng=gen))
        return out

    def query_texts(self, text, *args, **kwargs) -> list[str]:
        if not self.store_texts or self.texts is None:
            raise RuntimeError("query_texts requires store_texts=True")
        return [self.texts[int(i)] for i in self.query(text, *args, **kwargs)]

    def bucket_stats(self) -> dict:
        if self.counts is None:
            raise RuntimeError("fit must be called before bucket_stats")
        return {
            "n_docs": self.n_docs,
            "n_bits": self.n_bits,
            "n_buckets": self.n_buckets,
            "min": int(self.counts.min()) if self.counts.size else 0,
            "mean": float(self.counts.mean()) if self.counts.size else 0.0,
            "max": int(self.counts.max()) if self.counts.size else 0,
            "empty": int((self.counts == 0).sum()),
        }

    def save(self, path: str):
        meta = {
            "n_bits": self.n_bits,
            "ngram_range": self.ngram_range,
            "seed": self.seed,
            "store_texts": self.store_texts,
            "texts": self.texts if self.store_texts else None,
        }
        np.savez_compressed(
            path,
            codes=self.codes,
            counts=self.counts,
            offsets=self.offsets,
            ids=self.ids,
            meta=np.asarray(json.dumps(meta), dtype=object),
        )

    @classmethod
    def load(cls, path: str) -> "DistractorRetrieval":
        data = np.load(path, allow_pickle=True)
        meta = json.loads(str(data["meta"].item()))
        obj = cls(
            n_bits=meta["n_bits"],
            ngram_range=tuple(meta["ngram_range"]),
            seed=meta["seed"],
            store_texts=meta["store_texts"],
        )
        obj.texts = meta.get("texts")
        obj.codes = data["codes"]
        obj.counts = data["counts"]
        obj.offsets = data["offsets"]
        obj.ids = data["ids"]
        return obj

    def fit_to_memmap(self, texts, path: str, batch_size: int = 100_000):
        os.makedirs(path, exist_ok=True)
        self.fit(texts)
        np.save(os.path.join(path, "codes.npy"), self.codes)
        np.save(os.path.join(path, "counts.npy"), self.counts)
        np.save(os.path.join(path, "offsets.npy"), self.offsets)
        np.save(os.path.join(path, "ids.npy"), self.ids)
        with open(os.path.join(path, "meta.json"), "w", encoding="utf-8") as f:
            json.dump({
                "n_bits": self.n_bits,
                "ngram_range": self.ngram_range,
                "seed": self.seed,
                "store_texts": False,
                "batch_size": batch_size,
            }, f)
        return self


@dataclass
class VerificationDistractorRetriever:
    """Candidate-answer retrieval adapter for verification task construction."""

    tasks: list[str]
    prompts: list[str]
    answers: list[str]
    min_distractors: int = 10
    n_bits: int = 12
    seed: int = 0
    radius: int = 0
    query_max_chars: int = 128

    def __post_init__(self):
        by_task = {}
        for task, prompt, answer in zip(self.tasks, self.prompts, self.answers):
            group = by_task.setdefault(task, {"prompts": [], "answers": []})
            group["prompts"].append(prompt)
            group["answers"].append(answer)

        self.task_indexes = {}
        for task, group in by_task.items():
            answers = group["answers"]
            if len(answers) <= self.min_distractors:
                continue
            self.task_indexes[task] = {
                "answers": answers,
                "answer_index": DistractorRetrieval(answers, n_bits=self.n_bits, seed=self.seed),
            }

    @classmethod
    def from_dataset(cls, ds, pools: dict[str, list[str]], **kwargs):
        allowed = {task: set(vals) for task, vals in pools.items()}
        seen = {task: set() for task in pools}
        remaining = sum(len(v) for v in allowed.values())
        tasks, prompts, answers = [], [], []
        table = ds.data.table.select(["task", "prompt", "answer"])
        for rb in table.to_batches(max_chunksize=100_000):
            rb_tasks = rb.column("task").to_pylist()
            rb_prompts = rb.column("prompt").to_pylist()
            rb_answers = rb.column("answer").to_pylist()
            for task, prompt, answer in zip(rb_tasks, rb_prompts, rb_answers):
                if answer not in allowed.get(task, ()):
                    continue
                if answer in seen[task]:
                    continue
                seen[task].add(answer)
                remaining -= 1
                tasks.append(str(task))
                prompts.append(str(prompt))
                answers.append(str(answer))
            if remaining <= 0:
                break
        return cls(tasks=tasks, prompts=prompts, answers=answers, **kwargs)

    @classmethod
    def from_pools(cls, pools: dict[str, list[str]], **kwargs):
        tasks, prompts, answers = [], [], []
        for task, pool in pools.items():
            for answer in pool:
                tasks.append(str(task))
                prompts.append("")
                answers.append(str(answer))
        return cls(tasks=tasks, prompts=prompts, answers=answers, **kwargs)

    def _random_answers(self, task, answer, k, rng):
        task_index = self.task_indexes.get(task)
        if task_index is None:
            return []
        answers = task_index["answers"]
        sample_n = min(len(answers), max(k * 4, k + 1))
        picked = rng.sample(range(len(answers)), sample_n)
        return [answers[i] for i in picked if answers[i] != answer][:k]

    def _answers_from_ids(self, task_index, ids, answer, k):
        answers = task_index["answers"]
        out = []
        for i in ids:
            cand = answers[int(i)]
            if cand != answer and cand not in out:
                out.append(cand)
                if len(out) >= k:
                    break
        return out

    def _clip_query(self, text) -> str:
        text = str(text)
        if self.query_max_chars and self.query_max_chars > 0:
            return text[:self.query_max_chars]
        return text

    def _retrieved_answers(self, task_index, query_text, answer, k, rng):
        if task_index is None:
            return []
        ids = task_index["answer_index"].query(
            self._clip_query(query_text),
            k=max(k * 8, 32),
            radius=self.radius,
            rng=rng.randrange(1 << 63),
        )
        out = self._answers_from_ids(task_index, ids, answer, k)
        if len(out) < k:
            answers = task_index["answers"]
            sample_n = min(len(answers), max((k - len(out)) * 4, k + 1))
            for i in rng.sample(range(len(answers)), sample_n):
                cand = answers[i]
                if cand != answer and cand not in out:
                    out.append(cand)
                    if len(out) >= k:
                        break
        return out[:k]

    def candidates_for_row(self, row, k: int = 2, rng=None) -> list[str]:
        rng = rng if isinstance(rng, random.Random) else random.Random(rng)
        task, prompt, answer = str(row["task"]), str(row["prompt"]), str(row["answer"])
        task_index = self.task_indexes.get(task)
        mode = rng.randrange(4)
        if mode == 0:
            return self._random_answers(task, answer, k, rng)
        if mode == 1:
            return self._retrieved_answers(task_index, prompt, answer, k, rng)
        if mode == 2:
            return self._retrieved_answers(task_index, answer, answer, k, rng)
        return self._retrieved_answers(task_index, f"{prompt}\n{answer}", answer, k, rng)

    def batch_candidates(self, rows, k: int = 2, rng=None) -> list[list[str]]:
        rng = rng if isinstance(rng, random.Random) else random.Random(rng)
        out = [[] for _ in rows]
        modes = [rng.randrange(4) for _ in rows]

        for i, (row, mode) in enumerate(zip(rows, modes)):
            if mode == 0:
                out[i] = self._random_answers(str(row["task"]), str(row["answer"]), k, rng)

        for mode, query_fn in (
            (1, lambda row: self._clip_query(row["prompt"])),
            (2, lambda row: str(row["answer"])),
            (3, lambda row: self._clip_query(row["prompt"]) + "\n" + str(row["answer"])),
        ):
            by_task = {}
            for i, (row, row_mode) in enumerate(zip(rows, modes)):
                if row_mode != mode:
                    continue
                task = str(row["task"])
                task_index = self.task_indexes.get(task)
                if task_index is None:
                    continue
                by_task.setdefault(task, []).append((i, row, task_index))

            for items in by_task.values():
                task_index = items[0][2]
                queries = [query_fn(row) for _, row, _ in items]
                codes = task_index["answer_index"].encode(queries)
                for code, (i, row, _) in zip(codes, items):
                    ids = task_index["answer_index"].query_code(
                        int(code),
                        k=max(k * 8, 32),
                        radius=self.radius,
                        rng=rng.randrange(1 << 63),
                    )
                    found = self._answers_from_ids(task_index, ids, str(row["answer"]), k)
                    if len(found) < k:
                        found.extend(
                            x for x in self._random_answers(str(row["task"]), str(row["answer"]), k - len(found), rng)
                            if x not in found
                        )
                    out[i] = found[:k]
        return out

    def stats(self) -> dict:
        task_sizes = {}
        for task in self.tasks:
            task_sizes.setdefault(task, 0)
            task_sizes[task] += 1
        sizes = list(task_sizes.values())
        eligible_sizes = [len(v["answers"]) for v in self.task_indexes.values()]
        return {
            "n_candidates": len(self.answers),
            "n_tasks": len(task_sizes),
            "eligible_tasks": len(self.task_indexes),
            "min_task_candidates": min(sizes) if sizes else 0,
            "mean_task_candidates": float(np.mean(sizes)) if sizes else 0.0,
            "max_task_candidates": max(sizes) if sizes else 0,
            "mean_eligible_task_candidates": float(np.mean(eligible_sizes)) if eligible_sizes else 0.0,
        }
