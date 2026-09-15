import itertools
import json
import math
import random

from reasoning_core.template import Entry

from reasoning_core.tasks.generated.k3_novel_composition_r1.topological_sort_count import topological_sort_count as m


def _task(level=0):
    cfg = m.TopologicalSortCountV2Config()
    cfg.set_level(level)
    return m.TopologicalSortCount(config=cfg)


def test_summary_and_meta():
    assert isinstance(m.TopologicalSortCount.summary, str)
    assert m.TopologicalSortCount.summary.strip() == m.TopologicalSortCount.summary
    assert "\n" not in m.TopologicalSortCount.summary
    assert m.design_choice
    assert m.TASK_META["hypothesis"] == "P004"
    assert m.TASK_META["idea"] == "topological_sort_count (draw 2 of 3)"


def test_sp_count_leaf():
    assert m._sp_count(("L", 0)) == (1, 1)


def test_sp_count_series_chain():
    tree = ("S", ("L", 0), ("S", ("L", 1), ("L", 2)))
    assert m._sp_count(tree) == (1, 3)


def test_sp_count_parallel_two():
    tree = ("P", ("L", 0), ("L", 1))
    assert m._sp_count(tree) == (2, 2)


def test_sp_count_diamond():
    # a < b, a < c, b < d, c < d -> exactly 2 extensions
    tree = ("S", ("S", ("L", 0), ("P", ("L", 1), ("L", 2))), ("L", 3))
    assert m._sp_count(tree) == (2, 4)


def _brute_force(rels, n):
    order = list(range(n))
    cnt = [0]

    def valid(perm):
        pos = {v: i for i, v in enumerate(perm)}
        return all(pos[a] < pos[b] for a, b in rels)

    for perm in itertools.permutations(order):
        if valid(perm):
            cnt[0] += 1
    return cnt[0]


def test_ideal_dp_matches_brute_force():
    tree = ("P", ("P", ("L", 0), ("L", 1)), ("P", ("L", 2), ("L", 3)))
    elements, rels = m._sp_to_poset(tree)
    n = len(elements)
    ide = m._count_linear_extensions_by_ideals(rels, n)
    assert ide == 24
    assert _brute_force(rels, n) == 24


def test_relabel_preserves_count():
    tree = ("S", ("S", ("L", 0), ("P", ("L", 1), ("L", 2))), ("L", 3))
    perm = [3, 0, 2, 1]
    r = m._relabel(tree, perm)
    assert m._sp_count(r)[0] == m._sp_count(tree)[0] == 2


def _parse_expr(expr):
    toks = expr.replace('(', ' ( ').replace(')', ' ) ').replace('->', ' -> ').replace('|', ' | ').split()
    pos = [0]

    def parse():
        t = toks[pos[0]]
        if t == '(':
            pos[0] += 1
            left = parse()
            op = toks[pos[0]]
            pos[0] += 1
            right = parse()
            assert toks[pos[0]] == ')'
            pos[0] += 1
            op = 'S' if op == '->' else 'P'
            return (op, left, right)
        pos[0] += 1
        return ('L', int(t))
    return parse()


def test_generate_and_score_all_levels():
    for level in (0, 1, 2, 3, 4, 5, 6):
        t = _task(level)
        ex = t.generate_example()
        assert isinstance(ex, Entry)
        assert int(ex.answer) >= 1
        assert t.score_answer(ex.answer, ex) == 1.0
        assert t.score_answer(str(int(ex.answer) + 1), ex) == 0.0
        assert t.score_answer("", ex) == 0.0
        assert t.score_answer("abc", ex) == 0.0
        assert t.score_answer(str(random.random()), ex) == 0.0


def test_generated_answer_verified_independently():
    for _ in range(30):
        t = _task(random.randint(2, 6))
        ex = t.generate_example()
        count = int(ex.answer)
        assert count == ex.metadata["count"]
        parsed = _parse_expr(ex.metadata["sp_expression"])
        elements, rels = m._sp_to_poset(parsed)
        n = len(elements)
        assert n == ex.metadata["elements"]
        assert m._count_linear_extensions_by_ideals(rels, n) == count
        assert m._sp_count(parsed)[0] == count


def test_levels_differ():
    c0 = m.TopologicalSortCountV2Config()
    c0.set_level(0)
    c6 = m.TopologicalSortCountV2Config()
    c6.set_level(6)
    assert c0 != c6


def test_answer_not_readable_off_prompt_surface():
    answers = []
    surface_hits = 0
    for _ in range(80):
        ex = _task(6).generate_example()
        answers.append(int(ex.answer))
        nums = []
        for tok in ex.prompt.split():
            t = tok.strip("(),' ")
            if t.lstrip('-').isdigit():
                nums.append(int(t))
        if nums and max(nums) == int(ex.answer):
            surface_hits += 1
    # the answer must not routinely be the largest number shown in the prompt
    assert surface_hits / 80 < 0.4
    assert len(set(answers)) >= 8


def test_metadata_json_serializable():
    ex = _task(6).generate_example()
    json.dumps(dict(ex.metadata))


def test_count_not_constant():
    t = _task(6)
    seen = set()
    for _ in range(50):
        ex = t.generate_example()
        seen.add(int(ex.answer))
    assert len(seen) >= 8


def test_validate_passes():
    t = _task(0)
    ys = t.validate(n_samples=6)
    assert len(ys) == 6


def test_level6_stable_and_domain_valid():
    t = _task(6)
    sizes = set()
    for _ in range(60):
        ex = t.generate_example()
        count = int(ex.answer)
        # a count of a finite poset is a positive integer; also for n elements it can
        # never exceed n! (a fully incomparable set), enforcing a hard upper bound.
        n = ex.metadata["elements"]
        assert 1 <= count <= math.factorial(n)
        sizes.add(n)
    assert len(sizes) >= 3


def test_expression_and_poset_consistent():
    t = _task(4)
    for _ in range(20):
        ex = t.generate_example()
        expr = ex.metadata["sp_expression"]
        p = _parse_expr(expr)
        leaves = []
        def collect(node):
            if node[0] == 'L':
                leaves.append(node[1])
            else:
                collect(node[1]); collect(node[2])
        collect(p)
        assert sorted(leaves) == list(range(len(leaves)))
        assert len(leaves) == ex.metadata["elements"]
        els, rels = m._sp_to_poset(p)
        assert len(els) == len(leaves)
