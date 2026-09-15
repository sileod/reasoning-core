import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class VcgPivotalConfig(Config):
    num_goods: int = 3
    min_bidders: int = 3
    max_bidders: int = 4
    max_value: int = 10
    edit_value_max: int = 12

    def apply_difficulty(self, level):
        self.num_goods = min(6, 2 + level)
        base = 3 + level
        self.max_bidders = min(9, base)
        self.min_bidders = max(3, base - 1)
        self.max_value = 4 + 3 * level
        self.edit_value_max = max(self.max_value, 2 + 2 * level)


def _opt(active):
    best_val = 0
    best_set = []
    ln = len(active)
    for r in range(ln + 1):
        for combo in itertools.combinations(range(ln), r):
            mask_acc = 0
            val = 0
            ids = []
            ok = True
            for idx in combo:
                mask, value, bid = active[idx]
                if mask_acc & mask:
                    ok = False
                    break
                mask_acc |= mask
                val += value
                ids.append(bid)
            if not ok:
                continue
            if val > best_val or (val == best_val and ids < best_set):
                best_val = val
                best_set = ids
    return best_val, best_set


def _format_answer(pairs):
    return ";".join(f"{i}:{p}" for i, p in pairs)


def _parse_answer(answer):
    if not isinstance(answer, str):
        return None
    try:
        out = []
        for part in answer.split(";"):
            part = part.strip()
            if not part:
                continue
            i, p = part.split(":")
            out.append((int(i.strip()), int(p.strip())))
        return out
    except Exception:
        return None


class VcgPivotalPayments(Task):
    summary = ("Enumerate feasible winner sets in small combinatorial auctions of "
               "single-minded bidders, compute each winner's leave-one-out externality, "
               "and answer allocations and pivotal prices under bid edits and bidder removals.")
    design_choice = ("Instances encode bids as integer triples (bundle mask, value, bidder id), "
                     "and answers are canonical sorted lists of (winner, payment) pairs after "
                     "each specified edit.")
    config_cls = VcgPivotalConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        m = random.randrange(2, cfg.num_goods + 1)
        n = random.randrange(cfg.min_bidders, cfg.max_bidders + 1)

        bids = []
        for bid in range(n):
            mask = random.randrange(1, 1 << m)
            value = random.randrange(1, cfg.max_value + 1)
            bids.append((mask, value, bid))

        edit_type = random.choice(["none", "remove", "value"])
        edit = {"type": edit_type}
        active = [(bm, v, b) for (bm, v, b) in bids]
        if edit_type == "remove":
            rem = random.randrange(n)
            edit["bidder"] = rem
            active = [b for b in active if b[2] != rem]
        elif edit_type == "value":
            target = random.randrange(n)
            old = bids[target][1]
            new = random.randrange(1, cfg.edit_value_max + 1)
            while new == old:
                new = random.randrange(1, cfg.edit_value_max + 1)
            edit["bidder"] = target
            edit["new_value"] = new
            active = [(bm, old if b != target else new, b) for (bm, vvold, b) in bids]

        active = sorted(active, key=lambda t: t[2])
        opt_val, winset = _opt(active)
        value_by_id = {b: v for (_, v, b) in active}
        pairs = []
        for w in winset:
            removed = [b for b in active if b[2] != w]
            minus_val, _ = _opt(removed)
            pay = minus_val - opt_val + value_by_id[w]
            if pay < 0:
                raise RuntimeError("negative pivotal payment")
            pairs.append((w, pay))
        pairs.sort(key=lambda t: t[0])

        bundles = []
        for (bm, v, b) in bids:
            goods = [g for g in range(m) if (bm >> g) & 1]
            bundles.append({"bidder": b, "goods": goods, "value": v})

        metadata = {
            "num_goods": m,
            "bids": bundles,
            "edit": edit,
            "answer_list": [[i, p] for (i, p) in pairs],
        }
        return Entry(metadata=metadata, answer=_format_answer(pairs))

    def render_prompt(self, metadata):
        lines = []
        lines.append(f"There are {metadata['num_goods']} goods numbered 0..{metadata['num_goods'] - 1}.")
        bid_lines = []
        for bid in metadata["bids"]:
            gs = ", ".join(str(g) for g in bid["goods"])
            bid_lines.append(f"Bidder {bid['bidder']} wants goods {{{gs}}} for value {bid['value']}.")
        lines.append("Bids: " + " ".join(bid_lines))
        edit = metadata["edit"]
        if edit["type"] == "remove":
            lines.append(f"Bidder {edit['bidder']} is removed from the auction.")
        elif edit["type"] == "value":
            lines.append(f"Bidder {edit['bidder']}'s value is changed to {edit['new_value']}.")
        elif edit["type"] == "none":
            lines.append("No bid is edited; all bidders stay.")
        lines.append(
            "Winners are a subset of single-minded bidders whose bundles are pairwise disjoint "
            "(no two winners share a good), chosen to maximize total value. For each winner w, "
            "its pivotal (leave-one-out) VCG payment is the total value of the best allocation "
            "without w, minus the total value of the best allocation where the other winners "
            "still keep their own values. Compute the winning allocation and each winner's "
            "pivotal payment."
        )
        lines.append(
            "Answer as a list of (winner, payment) pairs, each written 'winner:payment', "
            "pairs separated by semicolons, ordered by winner id ascending. "
            "For example '2:13;5:4'."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        parsed = _parse_answer(answer)
        gold = [tuple(p) for p in entry.metadata["answer_list"]]
        if parsed is None or len(parsed) != len(gold):
            return 0.0
        if sorted(parsed) != sorted(gold):
            return 0.0
        return 1.0


TASK_META = {'parent_source_id': None,
 'idea': 'vcg_pivotal_payments (draw 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_counterfactual_r1/vcg_pivotal_payments',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
