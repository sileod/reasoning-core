import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'rotation_system_face_tracing (draw 1 of 3)',
 'hypothesis': 'P011',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_shortcuts_fail_r1/rotation_system_face_tracing',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2305351643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}


def enumerate_faces(rotation):
    """rotation[v] = neighbors of v in counterclockwise cyclic order (a simple
    graph: no loops, no parallel edges). A dart (u,v) is followed by
    (v, next-after-u in v's cyclic list). Returns the sorted face lengths,
    summing over every dart exactly once."""
    n = len(rotation)
    pos = {}
    for v in range(n):
        for i, u in enumerate(rotation[v]):
            pos[(v, u)] = i
    seen = set()
    lengths = []
    for v in range(n):
        for u in rotation[v]:
            if (v, u) in seen:
                continue
            length = 0
            a, b = v, u
            while (a, b) not in seen:
                seen.add((a, b))
                length += 1
                idx = pos[(b, a)]
                idx = (idx + 1) % len(rotation[b])
                a, b = b, rotation[b][idx]
            lengths.append(length)
    return sorted(lengths)


def sample_rotation(n):
    """Return a random simple-graph rotation system on n vertices: a random
    tree (guaranteeing connectivity, no isolated vertex, and bridges) plus a
    random set of extra simple edges to create cycles. Varied degrees and
    bridges. Returns a list of cyclically ordered neighbor lists."""
    adj = [set() for _ in range(n)]
    perm = list(range(n))
    random.shuffle(perm)
    for i in range(1, n):
        a = perm[i]
        b = perm[random.randrange(i)]
        adj[a].add(b)
        adj[b].add(a)
    extra = random.randint(0, max(1, n))
    attempts = 0
    while extra > 0 and attempts < 8 * n:
        attempts += 1
        a = random.randrange(n)
        b = random.randrange(n)
        if a != b and b not in adj[a]:
            adj[a].add(b)
            adj[b].add(a)
            extra -= 1
    rotation = [list(s) for s in adj]
    for v in range(n):
        random.shuffle(rotation[v])
    return rotation


@dataclass
class FaceTracingConfig(Config):
    n: int = 5

    def apply_difficulty(self, level):
        self.n = 4 + level


class FaceTracing(Task):
    summary = "Given a planar embedding as each vertex's cyclic neighbor order, walk directed darts by the next-edge rule to enumerate faces; degrees and bridges vary over simple graphs; answer the sorted face-length list."
    config_cls = FaceTracingConfig
    design_choice = "Choose vertex labels as integers 0..n-1 and encode the rotation system as a list of neighbor lists; the answer is the sorted lengths of all face cycles found by dart traversal."

    def generate_entry(self):
        n = self.config.n
        while True:
            rotation = sample_rotation(n)
            lengths = enumerate_faces(rotation)
            if sum(lengths) == sum(len(v) for v in rotation):
                break
        return Entry(metadata={"rotation": rotation, "n": n},
                     answer=" ".join(str(x) for x in lengths))

    def render_prompt(self, metadata):
        n = metadata["n"]
        lines = []
        for v in range(n):
            lst = " ".join(str(x) for x in metadata["rotation"][v])
            lines.append(f"vertex {v}: {lst}")
        body = "\n".join(lines)
        return (
            "A graph is embedded on the plane with vertices labeled 0 through {}. "
            "For every vertex, its neighbors are listed in counterclockwise cyclic "
            "order as they appear around that vertex. There are no loops or "
            "parallel edges.\n"
            "{}\n"
            "Enumerate every face of this embedding. A face is bounded by a closed "
            "walk found by the next-edge rule: start from any directed dart (u,v), "
            "then after reaching v leave along the neighbor that comes immediately "
            "after u in v's cyclic neighbor list, continuing until the dart repeats. "
            "Include the outer face. A bridge edge is traversed in both directions "
            "and bounds a face of length 2.\n"
            "Report the lengths of all faces as a single list separated by single "
            "spaces, in nondecreasing order. Example: if the face lengths are "
            "{{3, 4, 3}} the answer is: 3 3 4".format(n - 1, body)
        )

    def score_answer(self, answer, entry):
        expected = enumerate_faces(entry.metadata["rotation"])
        if answer is None:
            return 0.0
        s = str(answer).strip()
        if not s:
            return 0.0
        try:
            parts = [int(x) for x in s.split()]
        except ValueError:
            return 0.0
        return 1.0 if sorted(parts) == expected else 0.0
