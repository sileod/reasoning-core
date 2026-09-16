import json
import random

from reasoning_core.tasks.generated.k3_dynamic_structures_r1.transformation_semigroup_closure.transformation_semigroup_closure import (
    TransformationSemigroupClosure,
    compose_after,
    enumerate_closure,
    orbit_of,
    shortest_word,
)


def _fresh(config=None):
    return TransformationSemigroupClosure(config=config)


def make_all():
    ex = []
    for level in range(7):
        t = _fresh()
        t.config.set_level(level)
        for _ in range(30):
            ex.append((level, t.generate_example()))
    return ex


def test_generation_and_scoring():
    ok = 0
    for level, x in make_all():
        assert x.prompt
        assert x.answer
        assert x.metadata['_level'] == level
        assert x.metadata['mode'] in ('size', 'member', 'idem', 'orbit', 'witness')
        assert x.metadata['answer'] == x.answer
        assert json.loads(json.dumps(dict(x.metadata))) == dict(x.metadata)
        assert x.metadata['mode'] == x.metadata['mode']
        assert _fresh().score_answer(x.answer, x) == 1.0
        ok += 1
    assert ok >= 7 * 30


def test_wrong_answers_score_zero():
    for level, x in make_all():
        assert _fresh().score_answer('', x) == 0.0
        assert _fresh().score_answer('garbage!!', x) < 1.0
        if x.metadata['mode'] == 'member':
            wrong = 'No' if x.metadata['answer'] == 'Yes' else 'Yes'
            assert _fresh().score_answer(wrong, x) == 0.0
        elif x.metadata['mode'] == 'witness':
            assert _fresh().score_answer('', x) == 0.0
            assert _fresh().score_answer('7,7,7', x) == 0.0


def test_membership_balanced():
    counts = {'Yes': 0, 'No': 0}
    for level in (0, 3, 6):
        t = _fresh()
        t.config.set_level(level)
        for _ in range(60):
            x = t.generate_example()
            if x.metadata['mode'] == 'member':
                counts[x.answer] += 1
    total = counts['Yes'] + counts['No']
    assert total >= 20, total
    assert min(counts.values()) / max(total, 1) > 0.2


def test_closure_nontrivial():
    for level, x in make_all():
        if x.metadata['mode'] == 'size':
            assert int(x.answer) >= 1


def test_witness_valid():
    for level, x in make_all():
        if x.metadata['mode'] == 'witness':
            gens = [tuple(g) for g in x.metadata['generators']]
            target = tuple(x.metadata['target'])
            idx = [int(t) for t in x.answer.split(',')]
            m = None
            for i in idx:
                m = gens[i] if m is None else compose_after(m, gens[i])
            assert m == target


def test_reproducible_seeded():
    random.seed(1259343118)
    t = _fresh()
    t.config.set_level(3)
    a = [(t.generate_entry().answer, t.generate_entry().prompt) for _ in range(5)]
    random.seed(1259343118)
    t2 = _fresh()
    t2.config.set_level(3)
    b = [(t2.generate_entry().answer, t2.generate_entry().prompt) for _ in range(5)]
    assert a == b


def test_orbit_bounded():
    for level, x in make_all():
        if x.metadata['mode'] == 'orbit':
            n = x.metadata['n']
            assert 1 <= int(x.answer) <= n
