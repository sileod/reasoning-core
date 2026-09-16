import random
from collections import deque
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


def compose_after(m, gen):
    """(gen o m)(x) = gen(m(x)): apply m first, then gen."""
    return tuple(gen[x] for x in m)


def enumerate_closure(gens):
    """All distinct maps reachable as a nonempty finite composition of gens."""
    seen = set(gens)
    queue = list(gens)
    while queue:
        m = queue.pop(0)
        for gen in gens:
            nm = compose_after(m, gen)
            if nm not in seen:
                seen.add(nm)
                queue.append(nm)
    return seen


def shortest_word(gens, target):
    """A shortest word (tuple of generator indices) composing to target, or None."""
    seen = set()
    dq = deque()
    for i, gi in enumerate(gens):
        if gi not in seen:
            seen.add(gi)
            dq.append((gi, (i,)))
    while dq:
        m, word = dq.popleft()
        if m == target:
            return word
        for i in range(len(gens)):
            nm = compose_after(m, gens[i])
            if nm in seen:
                continue
            seen.add(nm)
            dq.append((nm, word + (i,)))
    return None


def orbit_of(f, n, s):
    """Number of distinct elements visited by iterating f from s until a repeat."""
    cur = s
    visited = set()
    while cur not in visited:
        visited.add(cur)
        cur = f[cur]
    return len(visited)


def build_generators(n, k, g):
    """Return g maps on {0..n-1} whose images lie in a shared k-element image set."""
    domain = list(range(n))
    image = sorted(random.sample(domain, k))
    for _attempt in range(200):
        gens = [tuple(random.choice(image) for _ in range(n)) for _ in range(g)]
        nonconstant = sum(1 for m in gens if len(set(m)) > 1)
        used = set()
        for m in gens:
            used |= set(m)
        if nonconstant >= 1 and len(used) == k:
            return tuple(gens), image
    raise RuntimeError("failed to build varied generators")


@dataclass
class TransformSemigroupClosureConfig(Config):
    n: int = 3
    k: int = 2
    num_generators: int = 2

    def apply_difficulty(self, level):
        self.n = 3 + min(level, 4)
        self.k = 2 + min(level // 2, 1)
        self.num_generators = 2 + min(level, 2)
        if self.k >= self.n:
            self.k = self.n - 1 if self.n > 1 else 1


class TransformationSemigroupClosure(Task):
    summary = ("Close finite transformation sets (tuple-encoded maps) under composition "
               "levelwise; modes ask closure size, membership yes/no, a witness word for a "
               "reachable target, idempotent count, or the orbit size of a given element.")
    config_cls = TransformSemigroupClosureConfig
    task_version = 2

    def generate_entry(self):
        n = self.config.n
        k = self.config.k
        g = self.config.num_generators
        gens, image = build_generators(n, k, g)
        closure = sorted(enumerate_closure(gens))
        mode = random.choice(['size', 'member', 'idem', 'orbit', 'witness'])
        gen_lists = [list(m) for m in gens]

        if mode == 'size':
            answer = str(len(closure))
            payload = {
                'mode': mode,
                'n': n,
                'generators': gen_lists,
            }
        elif mode == 'idem':
            count = sum(1 for m in closure if compose_after(m, m) == m)
            answer = str(count)
            payload = {
                'mode': mode,
                'n': n,
                'generators': gen_lists,
            }
        elif mode == 'member':
            reachable = random.random() < 0.5
            if reachable:
                target = random.choice(closure)
                answer = 'Yes'
            else:
                target = self._unreachable(gens, image, closure, n)
                answer = 'No'
            payload = {
                'mode': mode,
                'n': n,
                'generators': gen_lists,
                'target': list(target),
            }
        elif mode == 'orbit':
            f = random.choice(closure)
            s = random.randrange(n)
            answer = str(orbit_of(f, n, s))
            payload = {
                'mode': mode,
                'n': n,
                'generators': gen_lists,
                'f': list(f),
                'start': s,
            }
        else:  # witness
            deeper = [m for m in closure if len(shortest_word(gens, m)) >= 2]
            pool = deeper if deeper else closure
            target = random.choice(pool)
            word = shortest_word(gens, target)
            answer = ','.join(str(i) for i in word)
            payload = {
                'mode': mode,
                'n': n,
                'generators': gen_lists,
                'target': list(target),
            }

        metadata = dict(payload)
        metadata['answer'] = answer
        return Entry(metadata=metadata, answer=answer)

    @staticmethod
    def _unreachable(gens, image, closure, n):
        closure_set = set(closure)
        for _attempt in range(2000):
            cand = tuple(random.choice(image) for _ in range(n))
            if cand not in closure_set:
                return cand
        # fall back: construct a map not in closure by using a value outside image
        outside = [v for v in range(n) if v not in image]
        if outside:
            cand = tuple(random.choice(image) for _ in range(n))
            cand = list(cand)
            cand[0] = outside[0]
            cand = tuple(cand)
            if cand not in closure_set:
                return cand
        raise RuntimeError("could not find an unreachable map")

    @staticmethod
    def _fmt_map(m):
        return '(' + ','.join(str(x) for x in m) + ')'

    def render_prompt(self, metadata):
        gens = metadata['generators']
        gstr = ', '.join(self._fmt_map(g) for g in gens)
        mode = metadata['mode']
        head = (
            f"A transformation on the set {{0,...,{metadata['n'] - 1}}} is recorded as a tuple "
            f"(f(0),f(1),...,f({metadata['n'] - 1})), so tuple t means t[i] is the image of i. "
            f"Given generators {gstr}, composing two maps a then b sends x to b(a(x))."
        )
        if mode == 'size':
            return head + (
                f" Consider every map reachable as a nonempty composition of the generators "
                f"(the closure). How many distinct maps are in this closure? Answer one integer."
            )
        if mode == 'idem':
            return head + (
                f" A map e is idempotent when composing it with itself leaves it unchanged, "
                f"e(e(i))=e(i) for all i. Among the maps in the closure, how many are "
                f"idempotent? Answer one integer."
            )
        if mode == 'member':
            return head + (
                f" Is the map {self._fmt_map(metadata['target'])} reachable as a nonempty "
                f"composition of the generators? Answer Yes or No only."
            )
        if mode == 'orbit':
            return head + (
                f" The orbit of an element i under the map {self._fmt_map(metadata['f'])} is "
                f"the set of distinct values reached by repeatedly applying the map, "
                f"{{i, f(i), f(f(i)), ...}} until a value repeats. Starting from element "
                f"{metadata['start']}, how many distinct elements are in its orbit? "
                f"Answer one integer."
            )
        # witness
        return head + (
            f" Give a nonempty word of generator numbers, 0-indexed, whose composition equals "
            f"the map {self._fmt_map(metadata['target'])}. A word 'i1,i2,...,im' means apply "
            f"generator i1 first, then i2, ..., then im. Give numbers separated by commas, "
            f"e.g. '2,0,1'."
        )

    def score_answer(self, answer, entry):
        metadata = entry.metadata
        mode = metadata['mode']
        if mode == 'member':
            return 1.0 if str(answer).strip().lower() == metadata['answer'].lower() else 0.0
        if mode == 'witness':
            tokens = str(answer).replace('[', ' ').replace(']', ' ').replace(',', ' ')
            try:
                idx = [int(t) for t in tokens.split() if t.strip()]
            except Exception:
                return 0.0
            if not idx:
                return 0.0
            gens = [tuple(g) for g in metadata['generators']]
            m = None
            for i in idx:
                if not (0 <= i < len(gens)):
                    return 0.0
                m = gens[i] if m is None else compose_after(m, gens[i])
            return 1.0 if m == tuple(metadata['target']) else 0.0
        try:
            return 1.0 if int(str(answer).strip()) == int(metadata['answer']) else 0.0
        except Exception:
            return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'transformation_semigroup_closure (draw 3 of 3, unguided baseline)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_dynamic_structures_r1/transformation_semigroup_closure',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1259343118,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
