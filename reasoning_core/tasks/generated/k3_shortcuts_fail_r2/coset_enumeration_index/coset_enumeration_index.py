import random
import re
from dataclasses import dataclass

from sympy.combinatorics.coset_table import coset_enumeration_r
from sympy.combinatorics.fp_groups import FpGroup
from sympy.combinatorics.free_groups import free_group

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'coset_enumeration_index (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_shortcuts_fail_r2/coset_enumeration_index',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2639544549,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def multiply(p, q):
    return tuple(q[i] for i in p)


def inverse(p):
    return tuple(p.index(i) for i in range(len(p)))


def closure(generators):
    identity = tuple(range(len(generators[0])))
    seen = {identity}
    queue = [identity]
    for p in queue:
        for g in generators:
            q = multiply(p, g)
            if q not in seen:
                seen.add(q)
                queue.append(q)
    return seen


def evaluate(word, images):
    value = tuple(range(len(images[0])))
    for letter in word:
        image = images[abs(letter) - 1]
        value = multiply(value, image if letter > 0 else inverse(image))
    return value


def invert_word(word):
    return [-x for x in reversed(word)]


def reduce_word(word):
    result = []
    for x in word:
        if result and result[-1] == -x:
            result.pop()
        else:
            result.append(x)
    return result


def substitute(word, replacements):
    return reduce_word([letter for x in word for letter in
                        (replacements[abs(x) - 1] if x > 0 else
                         invert_word(replacements[abs(x) - 1]))])


def format_word(word):
    if not word:
        return 'e'
    chunks = []
    for x in word:
        if chunks and chunks[-1][0] == x:
            chunks[-1][1] += 1
        else:
            chunks.append([x, 1])
    return '*'.join(('a' if abs(x) == 1 else 'b') +
                    ('' if x * count == 1 or x == 2 and count == 1 else
                     '^' + str(count if x > 0 else -count))
                    for x, count in chunks)


def presentation(family, size):
    if family == 'dihedral':
        n = random.randint(4, size)
        images = [tuple((i + 1) % n for i in range(n)),
                  tuple((-i) % n for i in range(n))]
        relators = [[1] * n, [2, 2], [1, 2] * 2]
    elif family == 'abelian':
        m, n = random.randint(2, 5), random.randint(3, 6)
        images = [tuple(((i // n + 1) % m) * n + i % n for i in range(m * n)),
                  tuple((i // n) * n + (i + 1) % n for i in range(m * n))]
        relators = [[1] * m, [2] * n, [1, 2, -1, -2]]
    else:
        images, orders = {
            'tetrahedral': ([(1, 2, 0, 3), (1, 3, 2, 0)], (3, 3, 2)),
            'octahedral': ([(1, 2, 3, 0), (1, 0, 2, 3)], (4, 2, 3)),
            'icosahedral': ([(1, 2, 3, 4, 0), (1, 0, 3, 2, 4)], (5, 2, 3)),
        }[family]
        p, q, r = orders
        relators = [[1] * p, [2] * q, [1, 2] * r]
    return relators, images


def enumerate_index(relators, subgroup):
    free, a, b = free_group('a b')
    def convert(word):
        value = free.identity
        for x in word:
            value *= (a if abs(x) == 1 else b) ** (1 if x > 0 else -1)
        return value
    group = FpGroup(free, [convert(w) for w in relators])
    table = coset_enumeration_r(group, [convert(w) for w in subgroup], max_cosets=512)
    assert table.is_complete()
    table.compress()
    table.standardize()
    rows = table.table
    columns = {1: 0, -1: 1, 2: 2, -2: 3}
    def walk(start, word):
        for letter in word:
            start = rows[start][columns[letter]]
        return start
    for i, row in enumerate(rows):
        assert len(row) == 4 and all(0 <= j < len(rows) for j in row)
        for letter in columns:
            assert walk(i, [letter, -letter]) == i
        assert all(walk(i, w) == i for w in relators)
    assert all(walk(0, w) == 0 for w in subgroup)
    reached = {0}
    queue = [0]
    for i in queue:
        for j in rows[i]:
            if j not in reached:
                reached.add(j)
                queue.append(j)
    assert len(reached) == len(rows)
    return len(rows), rows


@dataclass
class CosetEnumerationIndexV3Config(Config):
    max_rotation: int = 10
    basis_changes: int = 0
    word_length: int = 4

    def apply_difficulty(self, level):
        self.max_rotation = 10 + int(2 * level)
        self.basis_changes = min(2, int(level // 3))
        self.word_length = 4 + int(level)


class CosetEnumerationIndex(Task):
    summary = "Enumerate subgroup cosets in varied dihedral, abelian and spherical triangle presentations, defining generator and relator rows and cascading coincidence collapses through changed bases; answer the subgroup index."
    config_cls = CosetEnumerationIndexV3Config
    task_version = 2

    def generate_entry(self):
        for _ in range(48):
            family = random.choice(['dihedral', 'abelian', 'tetrahedral', 'octahedral', 'icosahedral'])
            relators, images = presentation(family, self.config.max_rotation)
            group_elements = closure(images)
            subgroup = [reduce_word(random.choices([1, -1, 2, -2], k=random.randint(2, self.config.word_length)))
                        for _ in range(random.choices([1, 2], weights=[5, 1])[0])]
            subgroup_elements = closure([evaluate(w, images) for w in subgroup])
            index, remainder = divmod(len(group_elements), len(subgroup_elements))
            assert remainder == 0 and index > 0
            if index == 1:
                continue
            for _ in range(self.config.basis_changes):
                axis = random.randrange(2)
                replacements = [[1], [2]]
                replacements[axis] += [random.choice([-1, 1]) * (2 - axis)]
                relators = [substitute(w, replacements) for w in relators]
                subgroup = [substitute(w, replacements) for w in subgroup]
                other = replacements[axis][-1]
                images[axis] = multiply(images[axis], evaluate([-other], images))
            relators = [w if random.randrange(2) else invert_word(w) for w in relators]
            random.shuffle(relators)
            identity = tuple(range(len(images[0])))
            assert all(evaluate(w, images) == identity for w in relators)
            assert closure(images) == group_elements
            assert closure([evaluate(w, images) for w in subgroup]) == subgroup_elements
            try:
                actual, table = enumerate_index(relators, subgroup)
            except ValueError:
                continue
            assert actual == index
            return Entry(metadata={'relators': relators, 'subgroup': subgroup,
                                   'family': family, 'images': [list(p) for p in images],
                                   'group_order': len(group_elements),
                                   'subgroup_order': len(subgroup_elements), 'coset_table': table},
                         answer=str(index))
        raise RuntimeError('Could not complete a verified coset enumeration in 48 attempts')

    def render_prompt(self, metadata):
        relators = ', '.join(format_word(w) for w in metadata['relators'])
        subgroup = ', '.join(format_word(w) for w in metadata['subgroup'])
        return (
            'In a finitely presented group G generated by a and b, impose exactly the relations '
            f'{relators}, each equal to the identity e. Products are read left to right; '
            'negative exponents mean inverses. No other relations are imposed.\n'
            f'Let H be the subgroup generated by the words {subgroup} (not their normal closure).\n'
            'Use Todd–Coxeter coset enumeration: begin with H, define missing generator entries, '
            'close relator rows at every coset and subgroup rows at H, and merge coincidences '
            'including all consequences in the generator table. What is the index [G:H], '
            'the number of distinct right cosets Hg?\n'
            'Return only a positive integer, for example 7.'
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str) or not re.fullmatch(r'\s*\+?[0-9]+\s*', answer):
            return 0.0
        return float(answer.strip().lstrip('+').lstrip('0') == entry.answer)
