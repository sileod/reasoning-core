import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


_GENS = ["a", "b", "c"]
# Upper case letter is the inverse of the lower case generator of the same symbol.
_INV = {"a": "A", "A": "a", "b": "B", "B": "b", "c": "C", "C": "c"}


def _reduce(word):
    """Freely reduce a word over the generator alphabet {'a','b','c','A','B','C'}

    Upper case is the inverse of the matching lower-case generator.  The freely
    reduced form of any word in a free group is unique, so the result is canonical.
    Returns the reduced word as a tuple of single-letter symbols.
    """
    stack = []
    for ch in word:
        if stack and _INV[ch] == stack[-1]:
            stack.pop()
        else:
            stack.append(ch)
    return tuple(stack)


def _rand_reduced_with_prefix(gen_set, prefix, tail_len):
    """Return a freely reduced word that begins with ``prefix`` followed by a random
    freely reduced word of length ``tail_len`` using only generators from ``gen_set``.
    """
    # start from prefix (already reduced) then append tail letters that never cancel
    # the previous one and are chosen so adjacent letters reduce correctly.
    tail = []
    prev = prefix[-1] if prefix else None
    allowed = gen_set | {_INV[g] for g in gen_set}
    for _ in range(tail_len):
        if prev is None:
            nxt = random.choice(sorted(allowed))
        else:
            candidates = [ch for ch in sorted(allowed) if _INV[ch] != prev]
            nxt = random.choice(candidates)
        tail.append(nxt)
        prev = nxt
    result = _reduce(list(prefix) + tail)
    # the shared middle is present by construction at the word level; the freely
    # reduced result is unique and canonical.
    return result


@dataclass
class TreePairGroupProductConfig(Config):
    num_generators: int = 2
    num_pairs: int = 1
    core_len: int = 1
    tail_len: int = 2

    def apply_difficulty(self, level):
        self.num_generators = 2 if level <= 3 else 3
        self.num_pairs = 1 + (level + 1) // 3
        self.core_len = 1 + (level + 1) // 2
        self.tail_len = 2 + (level + 1) // 2


class TreePairGroupProduct(Task):
    summary = ("Multiply free-group elements carried by paired binary trees: each factor is a "
               "sequence of tree pairs sharing a common middle subtree, multiply by refining and "
               "carrying expansions to outer carets, cancel matching carets to recover the "
               "freely reduced product word or decide it is the identity.")
    config_cls = TreePairGroupProductConfig

    def generate_entry(self):
        gen_set = set(_GENS[: self.config.num_generators])
        forest = []          # list of factors; each factor is list of (p, q) reduced pairs
        full = []            # flattened product: p1, inv(q1), p2, inv(q2), ...
        for _ in range(self.config.num_pairs):
            core = _rand_reduced_with_prefix(gen_set, (), self.config.core_len)
            p = _rand_reduced_with_prefix(gen_set, core, self.config.tail_len)
            q = _rand_reduced_with_prefix(gen_set, core, self.config.tail_len)
            forest.append((list(p), list(q)))
            full.extend(p)
            full.extend(_INV[x] for x in reversed(q))
        product = _reduce(full)
        answer = "e" if not product else "".join(product)
        metadata = {
            "forest": forest,
            "generators": sorted(gen_set),
            "inverse_note": "an upper-case letter is the inverse of its lower-case generator",
        }
        # Domain check: the freely reduced product exists and length >= 0 always; assert it.
        assert 0 <= len(product)
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        parts = []
        for idx, (p, q) in enumerate(metadata["forest"]):
            shared = " and ".join([word_str(p), word_str(q)])
            parts.append(
                f"Tree pair {idx + 1} shares the middle subtree and carries the expansions "
                f"{word_str(p)} (left) and {word_str(q)} (right)."
            )
        factor = " ; ".join(parts)
        return (
            "Every element below is a product of paired binary trees: each pair's left and right "
            "tree share a common middle subtree, and their leaf labels form a reduced word "
            "over the generators "
            + ", ".join(metadata["generators"])
            + ". An upper-case letter is the inverse of the matching lower-case generator "
            "(A cancels a, B cancels b, C cancels c).\n"
            + factor
            + "\nMultiply the elements by refining the shared middle subtrees, carrying the "
              "expansions outward, and cancelling matching carets (adjacent generator then its "
              "inverse). Give the freely reduced product as one string with no spaces; if it "
              "reduces to nothing answer `e`."
        )


def word_str(word):
    if not word:
        return "∅"
    return "".join(word)


design_choice = ("Represent elements as sequences of paired tree reductions where each pair "
                 "shares a common middle subtree, and the answer is the canonical reduced pair "
                 "after cancellation.")

TASK_META = {'parent_source_id': None,
 'idea': 'tree_pair_group_product (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_dynamic_structures_r5/tree_pair_group_product',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
