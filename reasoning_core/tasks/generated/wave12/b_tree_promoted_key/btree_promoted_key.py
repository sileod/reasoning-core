import random

from reasoning_core.template import Config, Entry, Task

DESIGN_CHOICE = "Encode the B-tree as nested lists with explicit node capacities; answer is the key that moves up one level."

TASK_META = {'parent_source_id': None,
 'idea': 'btree_promoted_key (draw 2 of 3)',
 'hypothesis': 'external:btree_promoted_key',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/btree_promoted_key',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1007633176,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


class BTreeConfig(Config):
    min_degree: int = 2

    def apply_difficulty(self, level):
        self.min_degree = min(3, max(2, 2 + (level >= 3) + (level >= 6)))


def _node(keys, children):
    return [keys, children]


def _tree_to_lists(node):
    keys, children = node
    return [list(keys), [_tree_to_lists(c) for c in children]]


def _split_node(node, t, promos):
    keys, children = node
    mid = t - 1
    promoted = keys[mid]
    left = _node(list(keys[:mid]), list(children[:mid + 1]))
    right = _node(list(keys[mid + 1:]), list(children[mid + 1:]))
    promos.append(promoted)
    return left, promoted, right


def _insert_into(node, t, key, promos):
    keys, children = node
    idx = 0
    while idx < len(keys) and keys[idx] < key:
        idx += 1
    if idx < len(keys) and keys[idx] == key:
        return None
    if not children:
        keys.insert(idx, key)
        keys.sort()
        if len(keys) > 2 * t - 1:
            return _split_node(node, t, promos)
        return None
    result = _insert_into(children[idx], t, key, promos)
    if result is None:
        return None
    left, promoted, right = result
    pi = 0
    while pi < len(keys) and keys[pi] < promoted:
        pi += 1
    keys.insert(pi, promoted)
    children[pi:pi + 1] = [left, right]
    if len(keys) > 2 * t - 1:
        return _split_node(node, t, promos)
    return None


def _insert_btree(root, t, key):
    promos = []
    result = _insert_into(root, t, key, promos)
    if result is not None:
        left, promoted, right = result
        root[0] = [promoted]
        root[1] = [left, right]
        promos.append(promoted)
    return promos


def _sample_tree(min_degree, n_nodes):
    pool = list(range(1, 500))

    def build(n):
        t = min_degree
        if n <= 1:
            cnt = random.randint(1, 2 * t - 1)
            return _node(sorted(random.sample(pool, cnt)), []), 1
        lo = min(t - 1, n - 1)
        hi = min(2 * t - 1, n - 1)
        cnt = random.randint(lo, hi)
        cnt = min(cnt, 2 * t - 1)
        keys = sorted(random.sample(pool, cnt))
        nc = len(keys) + 1
        alloc = [1] * nc
        rem = n - nc
        i = 0
        while rem > 0:
            alloc[i] += 1
            rem -= 1
            i = (i + 1) % nc
        children = []
        for a in alloc:
            if a <= 0:
                continue
            child, _ = build(a)
            children.append(child)
        return _node(list(keys), children), n

    root, _ = build(n_nodes)
    return root


class BTreePromotedKey(Task):
    summary = ("Given a small order-(min-degree) B-tree encoded as nested [keys, "
               "children] lists and a single insertion key, apply B-tree insertion "
               "with node splits and output the first key promoted one level up, or "
               "None if no split is needed.")
    config_cls = BTreeConfig
    design_choice = DESIGN_CHOICE
    task_version = 2

    def generate_entry(self):
        min_degree = self.config.min_degree
        want_promoted = random.random() < 0.7
        promotions = None
        original = None
        key = None
        root = None
        for _ in range(400):
            n_nodes = random.randint(2, 5)
            root = _sample_tree(min_degree, n_nodes)
            original = _tree_to_lists(root)
            key = random.randrange(1, 500)
            promotions = _insert_btree(root, min_degree, key)
            if bool(promotions) == want_promoted:
                break
        answer = promotions[0] if promotions else None
        promoted = bool(promotions)
        return Entry(
            metadata={
                "root": original,
                "order": min_degree,
                "inserted_key": key,
                "answer": answer,
                "promoted": promoted,
                "cot": None,
            },
            answer=str(answer),
        )

    def render_prompt(self, metadata):
        return (
            "A B-tree of minimum degree {order} (each node can hold at most {maxkeys} "
            "keys) is stored as nested lists [keys, children], where keys is a sorted "
            "increasing list of the node's integer keys and children is the list of its "
            "child nodes in key order (children is empty for a leaf). Insert the single "
            "key {key} using the standard B-tree insertion algorithm: descend to the "
            "correct leaf, add the key, then split any node that overflows by moving its "
            "median key up to its parent, repeating upward and splitting the root if it "
            "overflows. Output the first promoted key -- the median key from the lowest "
            "(leaf-most) split that moves up one level -- or None if no key is promoted.\n\n"
            "Root: {root}\n\n"
            "Answer: one integer, or the word None if there is no promotion."
        ).format(
            order=metadata["order"],
            maxkeys=2 * metadata["order"] - 1,
            key=metadata["inserted_key"],
            root=metadata["root"],
        )

    def score_answer(self, answer, entry):
        gold = entry.answer.lower() if isinstance(entry.answer, str) else entry.answer
        candidate = str(answer).strip().lower()
        if gold == "none":
            return 1.0 if candidate == "none" else 0.0
        if candidate in ("none", ""):
            return 0.0
        try:
            return 1.0 if int(candidate) == int(gold) else 0.0
        except (ValueError, TypeError):
            return 0.0
