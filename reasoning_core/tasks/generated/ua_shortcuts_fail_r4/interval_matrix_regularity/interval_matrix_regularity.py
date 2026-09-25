import random
from dataclasses import dataclass
from itertools import product

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'interval_matrix_regularity (variant 2 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_shortcuts_fail_r4/interval_matrix_regularity',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3577985643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _det(mat):
    n = len(mat)
    if n == 1:
        return mat[0][0]
    if n == 2:
        return mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0]
    return (mat[0][0] * (mat[1][1] * mat[2][2] - mat[1][2] * mat[2][1])
            - mat[0][1] * (mat[1][0] * mat[2][2] - mat[1][2] * mat[2][0])
            + mat[0][2] * (mat[1][0] * mat[2][1] - mat[1][1] * mat[2][0]))


def _cell_value(cell, assign):
    if isinstance(cell, int):
        return cell
    return assign[cell['g']]


def _regular_at(matrix, groups, radius):
    n = len(matrix)
    ndim = len(groups)
    sign = None
    neg = radius if radius >= 0 else 0
    for combo in product((0, 1), repeat=ndim):
        assign = [groups[i]['center'] - neg if combo[i] == 0 else groups[i]['center'] + neg
                  for i in range(ndim)]
        m = [[_cell_value(matrix[i][j], assign) for j in range(n)] for i in range(n)]
        d = _det(m)
        s = 1 if d > 0 else (-1 if d < 0 else 0)
        if s == 0:
            return False
        if sign is None:
            sign = s
        elif s != sign:
            return False
    return True


def _first_singular_radius(matrix, groups, R0):
    for r in range(0, R0 + 1):
        if not _regular_at(matrix, groups, r):
            return r
    return None


def _gen_regular(n, R0):
    diag = 20 + random.randint(0, 6)
    groups = []
    matrix = [[None for _ in range(n)] for _ in range(n)]
    for i in range(n):
        matrix[i][i] = diag
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if matrix[i][j] is not None:
                continue
            if i < j and random.random() < 0.5:
                center = random.randint(-2, 2)
                gi = len(groups)
                groups.append({'center': center})
                matrix[i][j] = {'g': gi}
                matrix[j][i] = {'g': gi}
            else:
                center = random.randint(-2, 2)
                gi = len(groups)
                groups.append({'center': center})
                matrix[i][j] = {'g': gi}
    return matrix, groups


def _gen_singular(n, R0):
    a = random.randint(1, 5)
    d = random.randint(1, 5)
    num = a * d
    divisors = [x for x in range(1, 6) if num % x == 0]
    b = random.choice(divisors)
    cstar = num // b
    rt = random.randint(1, R0)
    c0 = cstar + random.choice((-1, 1)) * rt
    groups = [{'center': c0}]
    if n == 2:
        matrix = [[a, {'g': 0}], [b, d]]
    else:
        matrix = [[a, {'g': 0}, 0],
                  [b, d, 0],
                  [0, 0, 1]]
    return matrix, groups


@dataclass
class IntervalMatrixConfig(Config):
    level: int = 0
    seed: int = None
    n: int = 2
    max_radius: int = 2

    def apply_difficulty(self, level):
        self.n = 2 if level <= 3 else 3
        self.max_radius = 2 + (level // 2)


class IntervalMatrixRegularity(Task):
    summary = ("Decide robust regularity of interval integer matrices under a shared radius, "
               "with independent and shared uncertainties, answering regular or the first "
               "radius admitting a singular matrix.")
    design_choice = ("Answer as a canonical string like 'regular' when all matrices in the box "
                     "are nonsingular, or 'singular_at_r' where r is the first integer radius "
                     "admitting a singular matrix.")
    config_cls = IntervalMatrixConfig
    task_version = 2

    def generate_entry(self):
        n = self.config.n
        R0 = random.randint(1, self.config.max_radius)
        for _ in range(200):
            if random.random() < 0.35:
                matrix, groups = _gen_regular(n, R0)
                r = _first_singular_radius(matrix, groups, R0)
                if r is None:
                    return Entry(metadata={
                        'n': n, 'radius': R0, 'matrix': matrix, 'groups': groups,
                        'outcome': 'regular'}, answer='regular')
            else:
                matrix, groups = _gen_singular(n, R0)
                r = _first_singular_radius(matrix, groups, R0)
                if r is not None and 1 <= r <= R0:
                    return Entry(metadata={
                        'n': n, 'radius': R0, 'matrix': matrix, 'groups': groups,
                        'outcome': 'singular'}, answer='singular_at_%d' % r)
        raise RuntimeError('interval_matrix_regularity: failed to build an admissible example')

    def render_prompt(self, metadata):
        n = metadata['n']
        R0 = metadata['radius']
        groups = metadata['groups']
        matrix = metadata['matrix']
        lines = []
        lines.append(
            ("Consider %d\u00d7%d integer matrices. A cell shown as a fixed integer is a "
             "constant. A cell labelled u_j may take any integer value in that u_j's interval, "
             "and any two cells carrying the same label u_j must take the same value (they are "
             "shared).") % (n, n))
        for gi, g in enumerate(groups):
            c = g['center']
            lines.append('u%d \u2208 [%d, %d]' % (gi, c - R0, c + R0))
        rows = []
        for i in range(n):
            cells = []
            for j in range(n):
                cell = matrix[i][j]
                cells.append(str(cell) if isinstance(cell, int) else 'u%d' % cell['g'])
            rows.append('[' + ', '.join(cells) + ']')
        lines.append('Matrix: ' + ' ; '.join(rows))
        lines.append(
            ("Every interval above has radius %d. At a smaller integer radius r with "
             "0 \u2264 r \u2264 %d the same matrix instead restricts each u_j to "
             "[c_j \u2212 r, c_j + r] (integers).") % (R0, R0))
        lines.append(
            ("If, for the full intervals above, every choice of the u_j yields a matrix with "
             "nonzero determinant, answer exactly: regular. Otherwise find the smallest integer "
             "radius r with 0 \u2264 r \u2264 %d at which that restricted box first admits a "
             "singular matrix, and answer exactly: singular_at_r (for example singular_at_2).")
            % R0)
        return '\n'.join(lines)

    def score_answer(self, answer, entry):
        ref = entry['answer']
        return 1.0 if str(answer).strip() == ref else 0.0
