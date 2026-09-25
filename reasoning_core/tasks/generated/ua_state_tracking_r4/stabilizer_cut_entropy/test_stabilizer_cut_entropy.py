from fractions import Fraction

from reasoning_core.tasks.generated.ua_state_tracking_r4.stabilizer_cut_entropy.stabilizer_cut_entropy import (
    StabilizerCutEntropy,
    _norm_fraction,
)


def _task_for_level(level):
    t = StabilizerCutEntropy()
    t.config.set_level(level)
    return t


def test_gold_scores_one_at_all_levels():
    for level in range(7):
        t = _task_for_level(level)
        for _ in range(20):
            e = t.generate_example()
            assert t.score_answer(e.answer, e) == 1.0, (level, e.answer)


def test_answer_is_valid_reduced_fraction():
    for level in range(7):
        t = _task_for_level(level)
        for _ in range(20):
            e = t.generate_example()
            num, den = _norm_fraction(e.answer)
            assert num is not None
            assert den == 1
            assert 0 <= num <= e.metadata['rank_full']


def test_junk_and_empty_score_zero():
    t = _task_for_level(2)
    e = t.generate_example()
    assert t.score_answer('', e) == 0.0
    assert t.score_answer('junk', e) == 0.0
    assert t.score_answer('', e) == 0.0


def test_reduced_fraction_normalization():
    t = _task_for_level(2)
    e = t.generate_example()
    num, _ = _norm_fraction(e.answer)
    assert t.score_answer(f'{num}/1', e) == 1.0


def test_entropy_formula_agree():
    for level in range(7):
        t = _task_for_level(level)
        e = t.generate_example()
        gold_num, _ = _norm_fraction(e.answer)
        assert gold_num == e.metadata['k']


def test_prompt_states_bitmask_and_format():
    t = _task_for_level(2)
    e = t.generate_example()
    p = t.render_prompt(e.metadata)
    assert e.metadata['bitmask'] in p
    assert 'base-two logarithm' in p
    assert 'numerator/denominator' in p


def test_difficulty_raises_qubits():
    t0 = _task_for_level(0)
    t6 = _task_for_level(6)
    assert t6.config.qubits > t0.config.qubits


def _decode(word):
    x = []
    z = []
    for ch in word:
        if ch == 'X':
            x.append(1)
            z.append(0)
        elif ch == 'Z':
            x.append(0)
            z.append(1)
        elif ch == 'Y':
            x.append(1)
            z.append(1)
        else:
            x.append(0)
            z.append(0)
    return (x, z)


def _bruteforce_k(words, n, cut_set):
    dec = [_decode(w) for w in words]
    m = len(dec)
    best = 0
    for mask in range(1 << m):
        xv = [0] * n
        zv = [0] * n
        for i in range(m):
            if (mask >> i) & 1:
                xi, zi = dec[i]
                for q in range(n):
                    xv[q] ^= xi[q]
                    zv[q] ^= zi[q]
        supported = True
        for q in range(n):
            if q not in cut_set and (xv[q] or zv[q]):
                supported = False
                break
        if supported:
            best += 1
    return best.bit_length() - 1


def test_bruteforce_agrees_with_gold():
    for level in range(6):
        t = _task_for_level(level)
        for _ in range(25):
            e = t.generate_example()
            cut_set = set(i for i in range(e.metadata['n']) if e.metadata['bitmask'][i] == '1')
            k = _bruteforce_k(e.metadata['generators'], e.metadata['n'], cut_set)
            gold_num, _ = _norm_fraction(e.answer)
            assert gold_num == k, (level, e.metadata, gold_num, k)

