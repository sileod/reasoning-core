import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _source_label(idx):
    return chr(ord("A") + idx)


def _label_index(label):
    return ord(label) - ord("A")


def _antichain(node_spec, s, target):
    """Inclusion-minimal subsets of sources whose activation fires `target`.

    Monotone network: a gate fires iff at least `th` of its (already evaluated)
    parents fire. Enumerate all source subsets, keep only the inclusion-minimal
    ones that make the target fire, absorbing supersets as they are found.
    """
    cache = {}

    def fires(gate, active):
        if gate < s:
            return gate in active
        if gate in cache:
            return cache[gate]
        parents, th = node_spec[gate]
        count = sum(1 for p in parents if fires(p, active))
        res = count >= th
        cache[gate] = res
        return res

    minima = set()
    for mask in range(1 << s):
        active = frozenset(i for i in range(s) if (mask >> i) & 1)
        cache.clear()
        if not fires(target, active):
            continue
        if any(sub < active for sub in minima):
            continue
        minima = {sub for sub in minima if not (active < sub)}
        minima.add(active)
    return minima


def _canonical(antichain):
    """Antichain (set of frozensets) -> deterministic sorted label string."""
    if not antichain:
        return "-"
    ordered = sorted(tuple(sorted(ss)) for ss in antichain)
    return ";".join(",".join(_source_label(i) for i in ss) for ss in ordered)


def _write_network(gate_spec, s, m, target, target_th, output_gates):
    """node_spec for the whole network (middle gates pre-seeded by caller)."""
    node_spec = dict(gate_spec)
    node_spec[target] = (tuple(range(s, s + m)), int(target_th))
    return node_spec


def _flip_extreme(current, lo, hi):
    return hi if current == lo else lo


def _parse_antichain(text):
    out = set()
    text = (text or "").strip()
    if not text or text == "-":
        return out
    for chunk in text.split(";"):
        chunk = chunk.strip()
        if not chunk or chunk == "-":
            continue
        out.add(frozenset(_label_index(p.strip()) for p in chunk.split(",") if p.strip()))
    return out


def _split_answer(raw):
    try:
        text = str(raw).strip()
    except Exception:
        return None
    i_add = text.upper().find("ADDED")
    i_rem = text.upper().find("REMOVED")
    if i_add < 0 or i_rem < 0 or i_rem < i_add:
        return None
    added_part = text[i_add + len("ADDED"):i_rem]
    removed_part = text[i_rem + len("REMOVED"):]
    if ":" in added_part:
        added_part = added_part.split(":", 1)[1]
    if ":" in removed_part:
        removed_part = removed_part.split(":", 1)[1]
    return _parse_antichain(added_part), _parse_antichain(removed_part)


@dataclass
class MinimalTriggerAntichainRepairConfig(Config):
    sources: int = 4
    gates: int = 3

    def apply_difficulty(self, level):
        self.sources = 4 + level
        self.gates = 3 + level


class MinimalTriggerAntichainRepair(Task):
    summary = ("Repair minimal triggering sets after gate, threshold, or shared-input "
               "edits in monotone trigger networks; combine witnesses and absorb "
               "supersets, returning added and removed minimal triggers.")
    config_cls = MinimalTriggerAntichainRepairConfig

    def generate_entry(self):
        s = int(self.config.sources)
        m = int(self.config.gates)

        for _ in range(200):
            base_gate_spec = {}
            for k in range(m):
                gid = s + k
                parents = [i for i in range(s) if random.random() < 0.45]
                if not parents:
                    parents = [random.randrange(s)]
                th = random.randint(1, len(parents))
                base_gate_spec[gid] = (tuple(parents), int(th))

            target = s + m
            target_th = random.randint(1, m)
            base_spec = _write_network(base_gate_spec, s, m, target, target_th, None)
            original = _antichain(base_spec, s, target)

            for _attempt in range(60):
                edited_spec = dict(base_spec)
                etype = random.choice(("gate", "threshold", "shared"))
                desc = None

                if etype == "gate":
                    gid = random.randrange(s, s + m)
                    parents, th = edited_spec[gid]
                    new_th = _flip_extreme(int(th), 1, len(parents))
                    edited_spec[gid] = (parents, new_th)
                    names = ", ".join(_source_label(p) for p in parents)
                    kind = ("an OR gate (fires when at least 1 fires)"
                            if new_th == 1
                            else "an AND gate (fires when all fire)")
                    desc = (f"Gate G{gid - s + 1} over inputs ({names}) is switched to "
                            f"{kind}.")

                elif etype == "threshold":
                    new_th = random.randint(1, m)
                    if new_th == int(edited_spec[target][1]):
                        continue
                    edited_spec[target] = (edited_spec[target][0], new_th)
                    in_names = ", ".join(f"G{i + 1}" for i in range(m))
                    desc = (f"The target T now fires when at least {new_th} of its inputs "
                            f"({in_names}) fire.")

                else:  # shared-input edit
                    gid = random.randrange(s, s + m)
                    parents, th = edited_spec[gid]
                    cand_missing = [i for i in range(s) if i not in parents]
                    cand_present = list(parents)
                    opts = []
                    if cand_missing:
                        opts.append("add")
                    if len(cand_present) > 1:
                        opts.append("remove")
                    if not opts:
                        continue
                    action = random.choice(opts)
                    if action == "add":
                        src = random.choice(cand_missing)
                        new_parents = tuple(sorted(parents) + [src])
                        edited_spec[gid] = (new_parents, int(th))
                        desc = (f"Source {_source_label(src)} is newly added as an input to "
                                f"gate G{gid - s + 1}; it keeps threshold {th}.")
                    else:
                        src = random.choice(cand_present)
                        rest = [p for p in parents if p != src]
                        nxt = min(int(th), len(rest))
                        edited_spec[gid] = (tuple(rest), nxt)
                        desc = (f"Source {_source_label(src)} is removed as an input from "
                                f"gate G{gid - s + 1}; its threshold becomes {nxt}.")

                repaired = _antichain(edited_spec, s, target)
                added = {ss for ss in repaired if ss not in original}
                removed = {ss for ss in original if ss not in repaired}
                if repaired != original and desc is not None:
                    break
            else:
                continue

            if repaired != original and desc is not None:
                break
        else:
            raise RuntimeError("could not construct a non-trivial trigger repair")

        src_labels = ", ".join(_source_label(i) for i in range(s))
        gate_lines = []
        for k in range(m):
            gid = s + k
            parents, th = base_spec[gid]
            names = ", ".join(_source_label(p) for p in parents)
            gate_lines.append(f"Gate G{k + 1} over inputs ({names}) fires when at least "
                              f"{th} of its inputs fire.")
        target_names = ", ".join(f"G{k + 1}" for k in range(m))
        original_str = _canonical(original)

        payload = {
            "intro": (
                f"A monotone trigger network has sources {src_labels}. Its gates are:\n"
                + "\n".join("  " + gl for gl in gate_lines)
                + f"\nThe target T fires when at least {int(base_spec[target][1])} of "
                  f"{target_names} fire."
            ),
            "known": (
                f"A minimal triggering set is an inclusion-minimal subset of sources whose "
                f"activation makes the target fire. The currently known minimal triggering "
                f"sets of T are: {original_str}."
            ),
            "edit": "One edit is applied to the network: " + desc,
            "question": (
                "After the edit, report the minimal triggering sets that were ADDED (newly "
                "minimal) and those that were REMOVED (no longer minimal). Combine witness "
                "sets from the target's inputs and absorb any set that became a superset of "
                "another. Write each minimal triggering set as a comma-separated sorted list "
                "of source labels, and the added and removed collections as label sets "
                "separated by semicolons, e.g. ADDED: A,B;D REMOVED: - (use - for an empty "
                "collection)."
            ),
        }

        metadata = {
            "sources": int(s),
            "gates": int(m),
            "base_gate_spec": {str(k): (list(base_spec[s + k][0]), int(base_spec[s + k][1]))
                               for k in range(m)},
            "target_inputs": list(range(s, s + m)),
            "target_threshold": int(base_spec[target][1]),
            "edit_type": etype,
            "edit_description": desc,
            "original": [sorted(ss) for ss in original],
            "repaired": [sorted(ss) for ss in repaired],
            "added": [sorted(ss) for ss in added],
            "removed": [sorted(ss) for ss in removed],
            "payload": payload,
        }

        answer = f"ADDED: {_canonical(added)}; REMOVED: {_canonical(removed)}"
        entry = Entry(metadata=metadata, answer=answer)
        self._assert_gold(entry)
        return entry

    def _assert_gold(self, entry):
        meta = entry.metadata
        original = {frozenset(ss) for ss in meta["original"]}
        repaired = {frozenset(ss) for ss in meta["repaired"]}
        added = {frozenset(ss) for ss in meta["added"]}
        removed = {frozenset(ss) for ss in meta["removed"]}
        assert added == {x for x in repaired if x not in original}
        assert removed == {x for x in original if x not in repaired}
        assert added | removed, "repair is trivial"

    def render_prompt(self, metadata):
        p = metadata.payload
        return (
            f"{p['intro']}\n\n{p['known']}\n\n{p['edit']}\n\n{p['question']}"
        )

    def score_answer(self, answer, entry):
        parsed = _split_answer(answer)
        gold = _split_answer(entry.answer)
        if parsed is None or gold is None:
            return 0.0
        return 1.0 if parsed == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'minimal_trigger_antichain_repair (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_incremental_recomputation_r4/minimal_trigger_antichain_repair',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1034322864,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
