import random

from reasoning_core.template import Task, Entry, Config, edict, stochastic_rounding as sround


TASK_META = {'parent_source_id': None,
 'idea': 'set_associative_cache (draw 1 of 2)',
 'hypothesis': 'W1-044',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave8/set_associative_cache',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1952221362,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1500,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


_LAST = None


def _set_label(block, n_sets):
    return block % n_sets


def _compute_gold(n_sets, n_ways, accesses, policy):
    """(hit, set, way) for the last access. Ways are slots 0..n_ways-1: a miss fills the
    lowest empty one, else overwrites the victim -- least recently used (policy 0) or
    oldest loaded (policy 1). Only LRU counts a hit as a use."""
    sets = [[None] * n_ways for _ in range(n_sets)]   # each way: [block, stamp] or None

    def locate(block):
        ways = sets[block % n_sets]
        for way, slot in enumerate(ways):
            if slot and slot[0] == block:
                return ways, way, True
        if None in ways:
            return ways, ways.index(None), False
        return ways, min(range(n_ways), key=lambda way: ways[way][1]), False

    for idx, block in enumerate(accesses[:-1]):
        ways, way, hit = locate(block)
        if not hit:
            ways[way] = [block, idx]
        elif policy == 0:
            ways[way][1] = idx
    _ways, way, hit = locate(accesses[-1])
    return int(hit), accesses[-1] % n_sets, way


_pattern_cache = None
import re
_pattern_cache = re.compile(r"^(HIT|MISS) set (\d+) way (\d+)$")


def _compare(answer, entry):
    am = _pattern_cache.match(answer.strip())
    if am is None:
        return 0.0
    try:
        hit = am.group(1)
        s = int(am.group(2))
        w = int(am.group(3))
    except ValueError:
        return 0.0
    gold_hit, gold_s, gold_w = entry.metadata["resolved"]
    if hit == "HIT":
        if gold_hit != 1:
            return 0.0
    else:
        if gold_hit != 0:
            return 0.0
    if (s, w) == (gold_s, gold_w):
        return 1.0
    return 0.0


class SetAssociativeCacheConfig(Config):
    n_sets: int = 2
    n_ways: int = 2
    n_pre: int = 4

    def apply_difficulty(self, level):
        self.n_sets = sround(3 + level)
        self.n_ways = sround(3 + (level // 2))
        self.n_pre = sround(4 + 2 * level)


class SetAssociativeCache(Task):
    summary = ("Given cache state and an access, output hit or miss and the affected way; "
               "set-associative LRU/FIFO placement with varied sets, ways and access sequences.")

    config_cls = SetAssociativeCacheConfig
    # v2: a way is a slot, filled lowest-empty-first; v1 answered block mod ways, and its LRU
    # evicted the most recently used block.
    task_version = 2

    def generate_entry(self):
        c = self.config
        n_sets = max(2, int(c.n_sets))
        n_ways = max(2, int(c.n_ways))
        n_pre = max(3, int(c.n_pre))
        n_blocks = n_sets * n_ways * random.choice([1, 2, 3])
        block_pool = list(range(n_blocks))
        policy = random.choice([0, 1])

        gold = None
        for _attempt in range(3000):
            accesses = []
            for i in range(n_pre + 1):
                if i == n_pre:
                    accesses.append(random.choice(block_pool))
                    break
                if random.random() < 0.65:
                    s = random.randrange(n_sets)
                    b = s + n_sets * random.randrange(max(1, n_blocks // n_sets))
                    b = b % n_blocks
                else:
                    b = random.choice(block_pool)
                accesses.append(b)

            hit, gs, gw = _compute_gold(n_sets, n_ways, accesses, policy)
            if not (0 <= gs < n_sets and 0 <= gw < n_ways):
                continue
            gold = f"{'HIT' if hit else 'MISS'} set {gs} way {gw}"
            break
        else:
            raise RuntimeError("failed to construct instance")

        policy_name = "LRU" if policy == 0 else "FIFO"
        metadata = edict({
            "n_sets": n_sets,
            "n_ways": n_ways,
            "block_count": n_blocks,
            "policy": policy_name,
            "accesses": list(accesses),
            "resolved": (hit, gs, gw),
        })
        metadata.payload = {
            "accesses": list(accesses),
            "n_sets": n_sets,
            "n_ways": n_ways,
            "block_count": n_blocks,
            "policy": policy_name,
        }
        return Entry(metadata=metadata, answer=gold)

    def render_prompt(self, metadata):
        block_lst = ", ".join(str(b) for b in metadata.payload["accesses"])
        policy = metadata.payload["policy"]
        victim_desc = ("the least recently used block (a hit counts as a use)" if policy == "LRU"
                       else "the block loaded longest ago (a hit changes nothing)")
        return (
            f"A {metadata.payload['n_sets']}-set {metadata.payload['n_ways']}-way set-associative "
            f"cache with {policy} replacement holds blocks numbered 0.."
            f"{metadata.payload['block_count'] - 1}. Block B maps to set B mod "
            f"{metadata.payload['n_sets']}, and each set has ways numbered 0.."
            f"{metadata.payload['n_ways'] - 1}. A block not in its set is loaded into the "
            f"lowest-numbered empty way; in a full set it overwrites {victim_desc}. "
            f"The cache starts empty. The access sequence is\n\n{block_lst}\n\n"
            f"Process every access except the last to settle the cache state, then read the final "
            f"access against that state. The answer is 'HIT set S way W' if the final access's "
            f"block is cached (S is its set, W the way holding it), or 'MISS set S way W' if not "
            f"(S is its set, W the way it overwrites)."
        )

    def score_answer(self, answer, entry):
        return _compare(answer, entry)
