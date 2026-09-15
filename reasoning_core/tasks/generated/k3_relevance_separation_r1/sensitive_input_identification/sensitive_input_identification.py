import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, edict

TASK_META = {'parent_source_id': None,
 'idea': 'sensitive_input_identification (draw 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_relevance_separation_r1/sensitive_input_identification',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}


@dataclass
class SensitiveInputIdentificationConfig(Config):
    n: int = 5
    not_prob: float = 0.3

    def apply_difficulty(self, level):
        self.n = 5 + 2 * level
        self.not_prob = 0.25 + 0.05 * level


def build_tree(idx):
    if len(idx) == 1:
        i = idx[0]
        if random.random() < 0.3:
            return ('not', ('var', i))
        return ('var', i)
    k = random.randint(1, len(idx) - 1)
    left = build_tree(idx[:k])
    right = build_tree(idx[k:])
    op = random.choice(('and', 'or'))
    if random.random() < 0.15:
        return ('not', (op, left, right))
    return (op, left, right)


def eval_tree(node, assign):
    t = node[0]
    if t == 'var':
        return assign[node[1]]
    if t == 'not':
        return 1 - eval_tree(node[1], assign)
    l = eval_tree(node[1], assign)
    r = eval_tree(node[2], assign)
    return (l & r) if t == 'and' else (l | r)


def render_tree(node):
    t = node[0]
    if t == 'var':
        return f"x{node[1]}"
    if t == 'not':
        return f"(not {render_tree(node[1])})"
    return f"({render_tree(node[1])} {t.upper()} {render_tree(node[2])})"


def format_answer(bits, pairs):
    bits_s = "[" + ",".join(str(b) for b in bits) + "]"
    pairs_s = "[" + ",".join(f"({a} {b})" for a, b in pairs) + "]"
    return bits_s + ";" + pairs_s


def parse_answer(answer):
    s = str(answer).strip()
    m = re.fullmatch(r"\[([^\]]*)\];\[([^\]]*)\]", s)
    if not m:
        return None
    bits_str, pairs_str = m.group(1), m.group(2)
    bits = tuple(sorted(int(x) for x in re.findall(r"\d+", bits_str)))
    pairs = []
    for pm in re.finditer(r"\((\d+)\s+(\d+)\)", pairs_str):
        a, b = int(pm.group(1)), int(pm.group(2))
        if a < b:
            pairs.append((a, b))
    pairs = tuple(sorted(set(pairs)))
    return (bits, pairs)


def compute_critical(tree, assign, n):
    base = eval_tree(tree, assign)
    crit = []
    for i in range(n):
        a2 = list(assign)
        a2[i] ^= 1
        if eval_tree(tree, a2) != base:
            crit.append(i)
    crit_set = set(crit)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if i in crit_set or j in crit_set:
                continue
            a2 = list(assign)
            a2[i] ^= 1
            a2[j] ^= 1
            if eval_tree(tree, a2) != base:
                pairs.append((i, j))
    return crit, pairs, base


class SensitiveInputIdentification(Task):
    summary = "Given a read-once Boolean formula with one input assignment, evaluate single flips and then pairs of input bits to report the output-changing critical bits and the joint-only critical pairs, ignoring inputs that cannot matter."
    design_choice = "Restrict circuits to read-once formulas (each input appears once) so every input is potentially critical, making the task to find which single flips actually matter under the given assignment."
    config_cls = SensitiveInputIdentificationConfig

    def generate_entry(self):
        n = self.config.n
        assign = [random.randint(0, 1) for _ in range(n)]
        tree = build_tree(list(range(n)))
        crit, pairs, base = compute_critical(tree, assign, n)
        for i in crit:
            assert 0 <= i < n
        for (a, b) in pairs:
            assert 0 <= a < b < n
        return Entry(metadata=edict(
            n=n,
            tree=tree,
            assign=assign,
            base=int(base),
            crit_bits=[int(b) for b in crit],
            crit_pairs=[[int(a), int(b)] for a, b in pairs],
        ), answer=format_answer(crit, pairs))

    def render_prompt(self, metadata):
        n = metadata["n"]
        lines = [
            f"A read-once Boolean formula over {n} input bits uses each input exactly once. Its parse tree (AND, OR, NOT gates) is:",
            "",
            f"  {render_tree(metadata['tree'])}",
            "",
            "Current assignment:",
            "  " + ", ".join(f"x{i} = {metadata['assign'][i]}" for i in range(n)),
            f"The formula evaluates to {metadata['base']} under this assignment.",
            "",
            "Define:",
            "  * A single bit i is 'critical' if flipping only bit i (leaving all others as assigned) changes the formula's output.",
            "  * An unordered pair {i,j} with i<j is a 'critical pair' if flipping both i and j together changes the output, but neither i alone nor j alone is critical.",
            "",
            "Find:",
            "  1. the sorted list of critical bits,",
            "  2. the sorted list of critical pairs, ordered lexicographically by (i,j).",
            "",
            "Answer exactly in this format, with [] for an empty list:",
            "  [critical bits...];[(pair1),(pair2),...]",
            "where each bit is an index and each pair is (i j) with i<j. Example (for a different instance): if bits 0 and 3 are critical and pairs (1 2), (2 4) are critical, answer:",
            "  [0,3];[(1 2),(2 4)]",
        ]
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        parsed = parse_answer(answer)
        if parsed is None:
            return 0.0
        want_bits = tuple(int(b) for b in entry.metadata["crit_bits"])
        want_pairs = tuple((int(a), int(b)) for a, b in entry.metadata["crit_pairs"])
        return 1.0 if parsed == (want_bits, want_pairs) else 0.0

    def distractor_candidates(self, entry):
        bits = tuple(int(b) for b in entry.metadata["crit_bits"])
        pairs = tuple((int(a), int(b)) for a, b in entry.metadata["crit_pairs"])
        gold = format_answer(bits, pairs)
        cands = []
        if len(bits) > 1:
            cands.append(format_answer(bits[:-1], pairs))
            cands.append(format_answer(bits[1:], pairs))
        elif len(bits) == 1:
            cands.append(format_answer((), pairs))
        if len(pairs) > 1:
            cands.append(format_answer(bits, pairs[:-1]))
            cands.append(format_answer(bits, pairs[1:]))
        elif len(pairs) == 1:
            cands.append(format_answer(bits, ()))
        empty = format_answer((), ())
        if empty != gold:
            cands.append(empty)
        return [c for c in cands if c != gold]
