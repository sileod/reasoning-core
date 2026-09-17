import random
from dataclasses import dataclass
from functools import lru_cache

from reasoning_core.template import Config, Entry, Task

BFS_CAP = 12000
MAX_ATTEMPTS = 80

TASK_META = {'parent_source_id': None,
 'idea': 'trace_monoid_canonization (variant 2 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_synthetic_grammars_r2/trace_monoid_canonization',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 382564971,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class TraceMonoidConfig(Config):
    n_letters: int = 4
    length: int = 6
    edge_prob: float = 0.4

    def apply_difficulty(self, level):
        self.n_letters = min(8, 4 + int(level) // 2)
        self.length = min(12, 6 + int(level))
        self.edge_prob = min(0.6, 0.4 + 0.03 * level)


def _relation(alphabet, edges):
    commutes = {c: set() for c in alphabet}
    for a, b in edges:
        commutes[a].add(b)
        commutes[b].add(a)
    return commutes


def _predecessors(word, commutes):
    return [sum(1 << j for j in range(i) if word[j] not in commutes[c])
            for i, c in enumerate(word)]


def _interleave(word, commutes, randomized=False):
    pred = _predecessors(word, commutes)
    used = 0
    result = []
    for _ in word:
        ready = [i for i, p in enumerate(pred)
                 if not used & (1 << i) and p & used == p]
        i = random.choice(ready) if randomized else min(ready, key=lambda i: (word[i], i))
        result.append(word[i])
        used |= 1 << i
    return ''.join(result)


def _count_interleavings(word, commutes):
    pred = _predecessors(word, commutes)
    full = (1 << len(word)) - 1

    @lru_cache(None)
    def count(used):
        if used == full:
            return 1
        return sum(count(used | (1 << i)) for i, p in enumerate(pred)
                   if not used & (1 << i) and p & used == p)

    return count(0)


def _trace_class(word, commutes, cap=BFS_CAP):
    seen = {word}
    frontier = [word]
    while frontier:
        w = frontier.pop()
        for i in range(len(w) - 1):
            if w[i + 1] in commutes[w[i]]:
                v = w[:i] + w[i + 1] + w[i] + w[i + 2:]
                if v not in seen:
                    seen.add(v)
                    if len(seen) > cap:
                        return None
                    frontier.append(v)
    return seen


def _depth_layers(word, commutes):
    depths = []
    for i, c in enumerate(word):
        depths.append(1 + max((depths[j] for j in range(i)
                               if word[j] not in commutes[c]), default=0))
    return [''.join(sorted(c for c, d in zip(word, depths) if d == layer))
            for layer in range(1, max(depths) + 1)]


def _strip_layers(word, commutes):
    pred = _predecessors(word, commutes)
    used = 0
    layers = []
    while used != (1 << len(word)) - 1:
        ready = [i for i, p in enumerate(pred)
                 if not used & (1 << i) and p & used == p]
        layers.append(''.join(sorted(word[i] for i in ready)))
        used |= sum(1 << i for i in ready)
    return layers


class TraceMonoidCanonization(Task):
    summary = "Canonize randomly interleaved words under a stated partial commutation relation by finding the lexicographically least word, stripping Foata layers, or counting distinct words in the class."
    design_choice = "Instance generation: derive words by random interleavings of a fixed canonical seed under the given relation, ensuring the same class has multiple correct answers."
    config_cls = TraceMonoidConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        mode = random.choice(('canonical', 'layers', 'size'))
        for _ in range(MAX_ATTEMPTS):
            alphabet = list('abcdefgh'[:cfg.n_letters])
            edges = [(a, b) for i, a in enumerate(alphabet) for b in alphabet[i + 1:]
                     if random.random() < cfg.edge_prob]
            commutes = _relation(alphabet, edges)
            letters = alphabet + random.choices(alphabet, k=cfg.length - len(alphabet))
            random.shuffle(letters)
            seed = _interleave(''.join(letters), commutes)
            word = _interleave(seed, commutes, randomized=True)
            if word == seed:
                continue
            cls = _trace_class(word, commutes)
            if cls is None or len(cls) < 3:
                continue
            count = _count_interleavings(word, commutes)
            layers = _depth_layers(word, commutes)
            assert seed in cls and seed == min(cls)
            assert count == len(cls) and count >= 3
            assert layers == _strip_layers(word, commutes)
            assert layers == _depth_layers(seed, commutes)
            assert ''.join(layers) in cls
            assert all(b in commutes[a] for layer in layers
                       for i, a in enumerate(layer) for b in layer[i + 1:])
            answer = {'canonical': seed, 'layers': '.'.join(layers), 'size': str(count)}[mode]
            return Entry(metadata={
                'alphabet': alphabet, 'word': word, 'seed': seed,
                'edges': [list(e) for e in edges], 'mode': mode,
                'layers': layers, 'class_size': count,
            }, answer=answer)
        raise RuntimeError('No bounded trace class found after 80 attempts')

    def render_prompt(self, metadata):
        pairs = ', '.join(a + b for a, b in metadata['edges']) or 'none'
        intro = (
            'A scheduler records a word of operation labels. Adjacent occurrences may be '
            'swapped exactly when their labels form one of these unordered commuting pairs: '
            f"{pairs}. No other pairs commute; equal labels are dependent. "
            'The equivalence class contains all distinct words reachable by any number of '
            'these swaps. Alphabetical order is '
            f"{' < '.join(metadata['alphabet'])}. Recorded word: {metadata['word']}.\n"
            'To reason about this trace, order each occurrence after every earlier occurrence '
            'with a dependent label (the dependency DAG). '
        )
        question = {
            'canonical': (
                'Use lexicographic Kahn topological sorting: repeatedly take the smallest '
                'available label. Give the lexicographically least word in the class. '
                'Answer with only the word, for example abac.'),
            'layers': (
                'Use Foata layering: repeatedly remove ALL currently predecessor-free '
                'occurrences simultaneously as the next layer. Sort labels alphabetically '
                'inside each layer. Give the layers in removal order, joined by dots; '
                'for example ab.c.ab. Answer with only that string.'),
            'size': (
                'Count distinct words, not swap sequences. You may use dynamic programming '
                'over completed occurrence sets in the dependency DAG. Give the class size. '
                'Answer with only an integer, for example 12.'),
        }[metadata['mode']]
        return intro + question

    def score_answer(self, answer, entry):
        return float(isinstance(answer, str) and answer.strip() == entry.answer)
