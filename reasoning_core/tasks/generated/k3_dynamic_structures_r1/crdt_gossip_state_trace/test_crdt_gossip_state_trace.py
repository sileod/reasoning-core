import random

from reasoning_core.tasks.generated.k3_dynamic_structures_r1.crdt_gossip_state_trace.crdt_gossip_state_trace import (
    CRDTGossipStateTrace,
)

def test_gold_scores_one():
    random.seed(7)
    task = CRDTGossipStateTrace()
    for _ in range(20):
        task.config.set_level(random.randint(0, 6))
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_junk_scores_zero():
    random.seed(9)
    task = CRDTGossipStateTrace()
    for _ in range(20):
        task.config.set_level(random.randint(0, 6))
        entry = task.generate_example()
        assert task.score_answer('', entry) == 0.0
        assert task.score_answer('garbage', entry) == 0.0
        assert task.score_answer('42', entry) == 0.0


def test_answer_roundtrip_is_reproducible():
    random.seed(11)
    task = CRDTGossipStateTrace()
    task.config.set_level(3)
    e1 = task.generate_entry()
    random.seed(11)
    task2 = CRDTGossipStateTrace()
    task2.config.set_level(3)
    e2 = task2.generate_entry()
    assert e1.answer == e2.answer
    assert e1.metadata == e2.metadata


def test_all_levels_generate():
    random.seed(13)
    task = CRDTGossipStateTrace()
    for level in range(7):
        task.config.set_level(level)
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_answer_format_matches_type():
    random.seed(17)
    task = CRDTGossipStateTrace()
    for _ in range(30):
        task.config.set_level(random.randint(0, 6))
        entry = task.generate_example()
        ctype = entry.metadata['ctype']
        a = entry.answer
        if ctype == 'gcounter':
            assert a.startswith('counter:') and a[8:].isdigit()
        elif ctype == 'pncounter':
            assert a.startswith('pn:') and (a[3:].isdigit() or a[3:].lstrip('-').isdigit())
        elif ctype == 'lwwreg':
            assert a.startswith('reg:')
        else:
            assert a.startswith('set:[') and a.endswith(']')


def test_tombstone_awset_correct():
    random.seed(23)
    task = CRDTGossipStateTrace()
    task.config.set_level(5)
    for _ in range(30):
        entry = task.generate_entry()
        m = entry.metadata
        if m['ctype'] == 'awset':
            assert m['answer'].startswith('set:[')
            assert m['answer'].endswith(']')
            body = m['answer'][5:-1]
            items = body.split(',') if body else []
            assert len(items) == len(set(items))

