import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'innocent_exclusion_exhaustification (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scope_and_binding_r4/innocent_exclusion_exhaustification',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
 'sandbox': {'name': 'bubblewrap',
                             'version': 'bubblewrap 0.8.0'}}}}


N_WORLDS = 8


@dataclass
class IEConfig(Config):
    n_alts: int = 4
    max_prejacent_worlds: int = 5
    max_block_worlds: int = 7

    def apply_difficulty(self, level):
        self.n_alts = 3 + level
        self.max_prejacent_worlds = 3 + min(level, 4)
        self.max_block_worlds = 3 + min(level, 4)


def _answer_str(answer):
    return "[" + ", ".join(str(w) for w in sorted(answer)) + "]"


def _parse_answer(answer):
    if not isinstance(answer, str):
        return None
    s = answer.strip()
    if not (s.startswith("[") and s.endswith("]")):
        return None
    inner = s[1:-1].strip()
    if inner == "":
        return []
    try:
        return [int(x) for x in inner.split(",")]
    except Exception:
        return None


def _chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def _compute_gold(prejacent, alternatives):
    prejacent_set = set(prejacent)
    exclusion_union = set()
    for a in alternatives:
        a_set = set(a)
        if a_set >= prejacent_set:
            continue
        exclusion_union.update(a_set)
    return sorted(w for w in prejacent_set if w not in exclusion_union)


class InnocentExclusionExhaustification(Task):
    summary = ("Compute exhaustified meanings from a prejacent and candidate alternatives: "
               "intersect maximal jointly consistent exclusion sets, then return the worlds "
               "satisfying the prejacent and all shared exclusions.")
    design_choice = ("Generate instances from a fixed world set and candidate set, where the "
                     "answer is the list of world indices satisfying all shared exclusions, "
                     "sorted ascending.")
    config_cls = IEConfig
    task_version = 2

    def generate_entry(self):
        all_worlds = list(range(N_WORLDS))
        n_alts = self.config.n_alts
        for _attempt in range(600):
            n_prej = random.randint(2, self.config.max_prejacent_worlds)
            prejacent_set = set(random.sample(all_worlds, n_prej))

            n_block = random.randint(1, self.config.max_block_worlds)
            block_worlds = random.sample(all_worlds, n_block)
            n_shared = random.randint(0, min(2, n_block))
            shared = set(block_worlds[:n_shared])
            free = block_worlds[n_shared:]

            n_innocent = max(1, n_alts // 2 + random.randint(0, 1))
            n_innocent = min(n_innocent, n_alts - 1)
            splits = _split_list(free, n_innocent)
            if splits is None:
                continue
            groups = [frozenset(shared | set(g)) for g in splits]
            while len(groups) < n_innocent:
                groups.append(frozenset(shared))

            innocent = groups[:n_innocent]
            n_blockers = max(0, n_alts - n_innocent)
            blockers = []
            for _ in range(n_blockers):
                inner = set(prejacent_set)
                inner |= set(random.sample(all_worlds, random.randint(1, 2)))
                blockers.append(frozenset(inner))

            all_alts = []
            for g in innocent:
                if set(g) >= prejacent_set:
                    too_big = True
                    break
                all_alts.append(sorted(g))
            else:
                too_big = False
            if too_big:
                continue
            for b in blockers:
                all_alts.append(sorted(b))

            exclusion_union = set()
            for a in innocent:
                exclusion_union |= set(a)
            answer = sorted(w for w in prejacent_set if w not in exclusion_union)
            if not answer:
                continue

            metadata = {
                "worlds": sorted(all_worlds),
                "prejacent_worlds": sorted(prejacent_set),
                "alternatives": all_alts,
            }
            if _compute_gold(metadata["prejacent_worlds"], all_alts) != answer:
                continue
            return Entry(metadata=metadata, answer=_answer_str(answer))
        raise RuntimeError("could not generate entry")

    def render_prompt(self, metadata):
        prejacent = metadata["prejacent_worlds"]
        alts = metadata["alternatives"]
        prompt = (
            "We reason about worlds indexed 0..7. A prejacent proposition is satisfied "
            "exactly in world set " + str(prejacent) + ". "
        )
        for i, a in enumerate(alts, start=1):
            prompt += "Alternative " + str(i) + " is satisfied exactly in world set " + str(a) + ". "
        prompt += (
            "Each alternative, if excluded, removes from the prejacent meaning every world in "
            "that alternative's set. A set of alternatives is jointly excludable if excluding "
            "all of them leaves at least one prejacent world. A maximal jointly consistent "
            "exclusion set is a jointly excludable set to which no further alternative can be "
            "added while remaining jointly excludable. "
            "The exhaustified meaning keeps the prejacent worlds that survive every alternative "
            "in the maximal jointly consistent exclusion set, i.e. the prejacent worlds not "
            "removed by any excluded alternative. "
            "Give the result as a bracketed, ascending list of world indices, e.g. [1, 3, 4]."
        )
        return prompt

    def score_answer(self, answer, entry):
        got = _parse_answer(answer)
        if got is None:
            return 0.0
        gold = _compute_gold(entry.metadata["prejacent_worlds"], entry.metadata["alternatives"])
        return 1.0 if got == gold else 0.0


def _split_list(free, n):
    random.shuffle(free)
    if n == 0:
        return []
    if len(free) < n:
        base = [i for i in range(n)]
        slots = [1] * n
        slots[0] += (len(free)) - n
        if slots[0] < 0:
            return None
        idx = 0
        result = []
        for s in slots:
            chunk = free[idx:idx + s]
            idx += s
            result.append(chunk)
        return result
    k = len(free)
    cuts = sorted(random.sample(range(1, k), n - 1)) if n > 1 else []
    result = []
    prev = 0
    for c in cuts:
        result.append(free[prev:c])
        prev = c
    result.append(free[prev:])
    return result
