import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'spatial_frame_relation_verdicts (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_controlled_nli_r1/spatial_frame_relation_verdicts',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
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

FRAMES = ('intrinsic', 'relative', 'absolute')
DIRECTIONS = ((0, 1), (1, 0), (0, -1), (-1, 0))
RELATIONS = ('left of', 'right of', 'in front of', 'behind')
NAMES = ('Aster', 'Birch', 'Cedar', 'Dahlia', 'Elm', 'Fern', 'Hazel', 'Iris')


def project(delta, heading, relation):
    fx, fy = DIRECTIONS[heading]
    front = delta[0] * fx + delta[1] * fy
    right = delta[0] * fy - delta[1] * fx
    return {'left of': -right, 'right of': right,
            'in front of': front, 'behind': -front}[relation]


def resolve(records):
    poses = {'map': (0, 0, 0)}
    for record in records:
        x, y, heading = poses[record['parent']]
        fx, fy = DIRECTIONS[heading]
        right, front = record['offset']
        poses[record['name']] = (x + right * fy + front * fx,
                                 y - right * fx + front * fy,
                                 (heading + record['turn']) % 4)
    return poses


def verify_verdicts(metadata):
    records = {r['name']: r for r in metadata['records']}

    def pose(name):
        if name == 'map':
            return 0j, 1j
        record = records[name]
        origin, facing = pose(record['parent'])
        right, front = record['offset']
        return origin + facing * complex(front, -right), facing * (-1j) ** record['turn']

    a, _ = pose(metadata['subject'])
    b, intrinsic = pose(metadata['reference'])
    _, relative = pose(metadata['observer'])
    rotation = {'left of': 1j, 'right of': -1j, 'in front of': 1, 'behind': -1}
    result = []
    for facing in (intrinsic, relative, 1j):
        axis = facing * rotation[metadata['relation']]
        result.append(((a - b) * axis.conjugate()).real > 0)
    return result


def canonical(verdicts, mode):
    if mode == 'verdicts':
        return ' '.join('yes' if value else 'no' for value in verdicts)
    return ', '.join(frame for frame, value in zip(FRAMES, verdicts) if value) or 'none'


def encode_pose(name, parent, target, poses):
    px, py, heading = poses[parent]
    dx, dy = target[0] - px, target[1] - py
    fx, fy = DIRECTIONS[heading]
    return {'name': name, 'parent': parent,
            'offset': [dx * fy - dy * fx, dx * fx + dy * fy],
            'turn': (target[2] - heading) % 4}


@dataclass
class SpatialFrameRelationVerdictsV3Config(Config):
    depth: int = 0
    span: int = 4

    def apply_difficulty(self, level):
        self.depth = min(7, max(0, stochastic_rounding(level)))
        self.span = 4 + max(0, int(level))


class SpatialFrameRelationVerdicts(Task):
    summary = "Scenes specify objects, nested poses and observers; explicit intrinsic, relative and absolute axes determine left/right and front/behind claims, answered as three verdicts or the ordered frames licensing the sentence."
    config_cls = SpatialFrameRelationVerdictsV3Config
    task_version = 3

    def generate_entry(self):
        span = self.config.span
        records = []
        for index in range(self.config.depth):
            records.append({'name': f'plate{index + 1}',
                            'parent': f'plate{index}' if index else 'map',
                            'offset': [random.randint(-span, span), random.randint(-span, span)],
                            'turn': random.randrange(4)})
        poses = resolve(records)
        subject, reference, observer = random.sample(NAMES, 3)
        relation = random.choice(RELATIONS)
        desired = [bool(random.getrandbits(1)) for _ in FRAMES]
        deltas = [(x, y) for x in range(-span, span + 1)
                  for y in range(-span, span + 1) if (x or y)
                  and (project((x, y), 0, relation) > 0) == desired[2]]
        delta = random.choice(deltas)
        headings = [random.choice([h for h in range(4)
                                  if (project(delta, h, relation) > 0) == value])
                    for value in desired[:2]]
        bx, by = random.randint(-span, span), random.randint(-span, span)
        targets = [(subject, (bx + delta[0], by + delta[1], random.randrange(4))),
                   (reference, (bx, by, headings[0])),
                   (observer, (random.randint(-span, span), random.randint(-span, span), headings[1]))]
        random.shuffle(targets)
        for name, target in targets:
            parents = list(poses)[-2:]
            parent = random.choice(parents)
            record = encode_pose(name, parent, target, poses)
            records.append(record)
        metadata = {'records': records, 'subject': subject, 'reference': reference,
                    'observer': observer, 'relation': relation,
                    'mode': random.choice(('verdicts', 'licensing'))}
        resolved = resolve(records)
        for name, target in targets:
            assert resolved[name] == target
        a, b = resolved[subject], resolved[reference]
        actual_delta = (a[0] - b[0], a[1] - b[1])
        verdicts = [project(actual_delta, heading, relation) > 0
                    for heading in (b[2], resolved[observer][2], 0)]
        assert verdicts == desired == verify_verdicts(metadata)
        assert all(type(value) is bool for value in verdicts)
        metadata['verdicts'] = verdicts
        return Entry(metadata=metadata, answer=canonical(verdicts, metadata['mode']))

    def render_prompt(self, metadata):
        lines = [
            'A stage map has east as +x and north as +y. All objects are treated as points.',
            'The map pose is (0, 0), facing north. Each pose below gives its position as '
            '(right, forward) offsets in its parent pose, and its facing as a number of '
            'clockwise quarter-turns from the parent facing. These are fixed nested poses, '
            'not successive movements. Compose the coordinate transforms from the map outward.',
        ]
        for record in metadata['records']:
            right, front = record['offset']
            lines.append(f"{record['name']}: parent {record['parent']}; offset ({right}, {front}); "
                         f"turns {record['turn']}.")
        lines.extend([
            f"{metadata['observer']} is the observer. Evaluate: '{metadata['subject']} is "
            f"{metadata['relation']} {metadata['reference']}'.",
            'Use the displacement from the reference (second named object) to the subject. '
            'The front axis is the reference facing for intrinsic, the observer facing for '
            'relative, and north for absolute. In every frame, right is 90 degrees clockwise '
            'from front; left and behind are the opposites of right and front. A claim is true '
            'exactly when the displacement has a strictly positive dot product with its '
            'named axis; zero is false. Other components and distances do not matter. '
            'Observer position does not change the axes.',
        ])
        if metadata['mode'] == 'verdicts':
            lines.append('Give yes/no verdicts in intrinsic, relative, absolute order, '
                         'separated by spaces. Format example: yes no yes.')
        else:
            lines.append('List exactly the frames making the claim true, in intrinsic, relative, '
                         'absolute order, comma-separated; use none if no frame does. '
                         'Format example: intrinsic, absolute.')
        return '\n'.join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        normalized = ' '.join(answer.strip().lower().split())
        if entry.metadata['mode'] == 'licensing':
            normalized = ', '.join(part.strip() for part in normalized.split(','))
        return float(normalized == canonical(entry.metadata['verdicts'], entry.metadata['mode']))
