import itertools
import json
import random

from reasoning_core.tasks.generated.k3_controlled_nli_r1.spatial_frame_relation_verdicts.spatial_frame_relation_verdicts import (
    FRAMES, RELATIONS, SpatialFrameRelationVerdicts, canonical,
    encode_pose, project, resolve, verify_verdicts,
)


def test_exhaustive_axes_and_boundary():
    for dx, dy, heading, relation in itertools.product(range(-2, 3), range(-2, 3), range(4), RELATIONS):
        metadata = {'records': [
            {'name': 'A', 'parent': 'map', 'offset': [dx, dy], 'turn': 0},
            {'name': 'B', 'parent': 'map', 'offset': [0, 0], 'turn': heading},
            {'name': 'O', 'parent': 'map', 'offset': [7, -3], 'turn': heading},
        ], 'subject': 'A', 'reference': 'B', 'observer': 'O', 'relation': relation}
        expected = project((dx, dy), heading, relation) > 0
        assert verify_verdicts(metadata) == [expected, expected, project((dx, dy), 0, relation) > 0]
    assert project((0, 3), 0, 'left of') == 0
    assert project((-2, 9), 0, 'left of') == 2
    assert project((3, -8), 1, 'left of') == -8


def test_nested_pose_composition():
    records = [
        {'name': 'P', 'parent': 'map', 'offset': [2, 3], 'turn': 1},
        {'name': 'Q', 'parent': 'P', 'offset': [4, 5], 'turn': 3},
    ]
    poses = resolve(records)
    assert poses['P'] == (2, 3, 1)
    assert poses['Q'] == (7, -1, 0)
    for heading in range(4):
        target = (-5, 8, heading)
        record = encode_pose('R', 'Q', target, poses)
        assert resolve(records + [record])['R'] == target


def test_all_answer_patterns_and_strict_order():
    task = SpatialFrameRelationVerdicts()
    entry = task.generate_entry()
    class NoAttributes:
        def __getattribute__(self, name):
            raise AssertionError(name)
    for verdicts in itertools.product((False, True), repeat=3):
        for mode in ('verdicts', 'licensing'):
            entry.metadata['verdicts'] = list(verdicts)
            entry.metadata['mode'] = mode
            gold = canonical(verdicts, mode)
            assert task.score_answer(gold, entry) == 1
            assert SpatialFrameRelationVerdicts.score_answer(NoAttributes(), gold, entry) == 1
            for garbage in ('', 'junk', gold + ' extra', None, 'yes no'):
                assert task.score_answer(garbage, entry) == 0
            if mode == 'licensing' and sum(verdicts) > 1:
                assert task.score_answer(', '.join(reversed(gold.split(', '))), entry) == 0
    assert canonical([False, False, False], 'licensing') == 'none'
    assert canonical([True, True, True], 'licensing') == ', '.join(FRAMES)


def test_generation_all_levels_and_label_balance():
    state = random.getstate()
    try:
        random.seed(94127)
        task = SpatialFrameRelationVerdicts()
        for level in range(7):
            task.config.set_level(level)
            patterns = set()
            counts = [0, 0, 0]
            for _ in range(160):
                entry = task.generate_entry()
                metadata = json.loads(json.dumps(entry.metadata))
                verdicts = verify_verdicts(metadata)
                assert verdicts == metadata['verdicts']
                assert task.score_answer(entry.answer, entry) == 1
                assert task.render_prompt(metadata) == task.render_prompt(entry.metadata)
                assert len(task.render_prompt(metadata)) < 6500
                patterns.add(tuple(verdicts))
                counts = [count + value for count, value in zip(counts, verdicts)]
            assert len(patterns) == 8
            assert all(50 < count < 110 for count in counts)
    finally:
        random.setstate(state)


def test_seed_replay():
    state = random.getstate()
    try:
        task = SpatialFrameRelationVerdicts()
        task.config.set_level(6)
        random.seed(1259343118)
        first = task.generate_entry()
        random.seed(1259343118)
        second = task.generate_entry()
        assert first.answer == second.answer
        assert task.render_prompt(first.metadata) == task.render_prompt(second.metadata)
    finally:
        random.setstate(state)
