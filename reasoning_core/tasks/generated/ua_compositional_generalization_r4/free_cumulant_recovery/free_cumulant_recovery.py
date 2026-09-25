"""Recover free cumulants from supplied moments by removing contributions of
noncrossing partitions; vary scalar and ordered mixed moments, returning a
queried cumulant or missing moment."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class FreeCumulantConfig(Config):
    max_order: int = 2

    def apply_difficulty(self, level):
        self.max_order = min(7, 2 + level)


def _all_partitions(n):
    """All set partitions of {0..n-1} as tuples of frozenset blocks."""
    partitions = []

    def rec(i, blocks):
        if i == n:
            partitions.append(tuple(frozenset(b) for b in blocks))
            return
        for idx in range(len(blocks)):
            blocks[idx].append(i)
            rec(i + 1, blocks)
            blocks[idx].pop()
        blocks.append([i])
        rec(i + 1, blocks)
        blocks.pop()

    rec(0, [])
    return partitions


def _is_nc(n, bid):
    """True if block-id array `bid` describes a noncrossing partition."""
    for i in range(n):
        for j in range(i + 1, n):
            if bid[j] == bid[i]:
                continue
            for k in range(j + 1, n):
                if bid[k] != bid[i]:
                    continue
                for l in range(k + 1, n):
                    if bid[l] == bid[j]:
                        return False
    return True


def _moment(word, kappa_by_label):
    """Moment of `word` (tuple of labels) via free moment-cumulant relation.

    Sum over noncrossing partitions of the product over blocks of
    kappa_by_label[label][len(block)-1]; a block containing two labels
    contributes zero (freely independent variables).
    """
    n = len(word)
    if n == 0:
        return 0
    total = 0
    for part in _all_partitions(n):
        bid_arr = [0] * n
        for bidx, block in enumerate(part):
            for x in block:
                bid_arr[x] = bidx
        if not _is_nc(n, bid_arr):
            continue
        prod = 1
        ok = True
        for block in part:
            labels = {word[x] for x in block}
            if len(labels) > 1:
                ok = False
                break
            lab = word[next(iter(block))]
            prod *= kappa_by_label[lab][len(block) - 1]
        if ok:
            total += prod
    return total


def _present_str(w):
    return "m[" + ",".join(w) + "]"


class FreeCumulantRecovery(Task):
    summary = ("Recover free cumulants from supplied moments by removing contributions of "
               "noncrossing partitions; vary scalar and ordered mixed moments, returning a "
               "queried cumulant or missing moment.")
    design_choice = ("Return the missing moment value as an integer, derived from the "
                     "cumulant-moment relation with noncrossing partitions.")
    config_cls = FreeCumulantConfig
    task_version = 2

    def generate_entry(self):
        max_order = self.config.max_order
        mixed = max_order >= 3 and random.random() < 0.45

        if not mixed:
            n = random.randint(2, max_order)
            mag = 2 + max_order * 2
            kappa = [random.randint(-mag, mag) or 1]
            while len(kappa) < n:
                v = random.randint(-mag, mag)
                if v != 0:
                    kappa.append(v)
            moments = [_moment(("X",) * i, {"X": kappa}) for i in range(1, n + 1)]
            q = random.randint(2, n)
            answer = moments[q - 1]
            presented_vals = {str(v) for v in kappa} | {str(m) for idx, m in enumerate(moments) if idx != q - 1}
            if str(answer) in presented_vals:
                return None
            missing_idx = q
            metadata = {
                "mode": "scalar",
                "cumulants": {"X": kappa},
                "moments": {str(i): moments[i - 1] for i in range(1, n + 1)},
                "query": f"m_{q}",
                "query_index": missing_idx,
                "answer": answer,
            }
        else:
            L = random.randint(2, max_order)
            mag = 2 + max_order * 2
            kappaA = [random.randint(-mag, mag) or 1]
            kappaB = [random.randint(-mag, mag) or 1]
            while len(kappaA) < L or len(kappaB) < L:
                if len(kappaA) < L:
                    v = random.randint(-mag, mag)
                    if v != 0:
                        kappaA.append(v)
                if len(kappaB) < L:
                    v = random.randint(-mag, mag)
                    if v != 0:
                        kappaB.append(v)
            kby = {"A": kappaA, "B": kappaB}
            words = []
            for _ in range(random.randint(3, 4)):
                wlen = random.randint(2, L)
                while True:
                    w = tuple(random.choice("AB") for _ in range(wlen))
                    if w not in words:
                        break
                words.append(w)
            word_map = {}
            for w in words:
                word_map[w] = _moment(w, kby)
            qi = random.randrange(len(words))
            query_word = words[qi]
            answer = word_map[query_word]
            presented_vals = {str(v) for v in kappaA + kappaB} | {
                str(v) for idx, v in enumerate(word_map.values()) if idx != qi
            }
            if str(answer) in presented_vals:
                return None
            metadata = {
                "mode": "mixed",
                "cumulants": {"A": kappaA, "B": kappaB},
                "moments": {_present_str(w): word_map[w] for w in words},
                "query": _present_str(query_word),
                "query_index": qi,
                "answer": answer,
            }

        return Entry(metadata=metadata, answer=str(int(answer)))

    def render_prompt(self, metadata):
        if metadata["mode"] == "scalar":
            n = len(metadata["cumulants"]["X"])
            kappa = metadata["cumulants"]["X"]
            kstr = ", ".join(f"k_{i} = {v}" for i, v in enumerate(kappa, start=1))
            qidx = metadata["query_index"]
            parts = []
            for i in range(1, n + 1):
                if i == qidx:
                    parts.append(f"m_{i} = ???")
                else:
                    parts.append(f"m_{i} = {metadata['moments'][str(i)]}")
            mstr = ", ".join(parts)
            return (
                f"Let X be a free random variable with free cumulants:\n{kstr}.\n"
                f"Its moments follow the moment-cumulant relation, where moment m_n is the sum over "
                f"noncrossing partitions of {n} points of the product of cumulants indexed by block "
                f"size.\nThe computed moments are:\n{mstr}.\n"
                f"What is the integer value of the missing moment m_{qidx}? Answer with the integer only."
            )
        else:
            kA = metadata["cumulants"]["A"]
            kB = metadata["cumulants"]["B"]
            kstrA = ", ".join(f"kA_{i} = {v}" for i, v in enumerate(kA, start=1))
            kstrB = ", ".join(f"kB_{i} = {v}" for i, v in enumerate(kB, start=1))
            qi = metadata["query_index"]
            parts = []
            for idx, (wname, val) in enumerate(metadata["moments"].items()):
                if idx == qi:
                    parts.append(f"{wname} = ???")
                else:
                    parts.append(f"{wname} = {val}")
            mstr = ", ".join(parts)
            return (
                f"Two freely independent random variables A and B have free cumulants:\n"
                f"{kstrA}\n{kstrB}\n.\n"
                f"An ordered mixed moment is the sum over noncrossing partitions of the positions of "
                f"the word of the product over blocks of the cumulant of the block's sole symbol, "
                f"indexed by block size; any block that mixes A and B contributes zero.\n"
                f"The following mixed moments are known:\n{mstr}.\n"
                f"What is the integer value of the missing moment {metadata['query']}? "
                f"Answer with the integer only."
            )

    def score_answer(self, answer, entry):
        ref = entry["answer"]
        a = str(answer).strip()
        if a == ref:
            return 1.0
        try:
            if int(a) == int(ref):
                return 1.0
        except (ValueError, TypeError):
            pass
        return 0.0

    def distractor_candidates(self, entry):
        base = entry.metadata
        if base["mode"] == "scalar":
            for v in base["moments"].values():
                yield str(v)
            for v in base["cumulants"]["X"]:
                yield str(v)
        else:
            for w, v in base["moments"].items():
                yield str(v)
            for v in base["cumulants"]["A"] + base["cumulants"]["B"]:
                yield str(v)


TASK_META = {'parent_source_id': None,
 'idea': 'free_cumulant_recovery (variant 2 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_compositional_generalization_r4/free_cumulant_recovery',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 241712510,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
