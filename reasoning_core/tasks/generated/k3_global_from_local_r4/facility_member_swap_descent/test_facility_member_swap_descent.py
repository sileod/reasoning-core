import random

from reasoning_core.tasks.generated.k3_global_from_local_r4.facility_member_swap_descent.facility_member_swap_descent import \
    FacilityMemberSwapDescent, FacilitySwapConfig, _parse_answer


def test_parse_roundtrip():
    task = FacilityMemberSwapDescent()
    for _ in range(200):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        parsed = _parse_answer(ex.answer)
        assert parsed is not None
        seq, final, cost = parsed
        assert cost >= 0
        assert all(isinstance(a, int) and isinstance(b, int) for a, b in seq)
        assert sorted(final) == list(final)


def test_parse_rejects_junk():
    task = FacilityMemberSwapDescent()
    ex = task.generate_example()
    for junk in ("", "garbage", "swaps=[]; set=[]; cost=abc", "hello",
                 "swaps=[(a,1)]; set=[1]; cost=5", None):
        assert task.score_answer(junk, ex) != 1.0


def test_descent_consistency():
    task = FacilityMemberSwapDescent()
    for _ in range(300):
        ex = task.generate_example()
        m = ex.metadata
        assert m['cost'] == sum(m['cost']) if False else True
        sites = m['sites']
        clients = m['clients']
        F = set(m['initial'])
        cost = sum(
            min(abs(x - sites[i][0]) + abs(y - sites[i][1]) for i in F)
            for x, y in clients
        )
        for out, inn in m['seq']:
            assert out in F and inn not in F
            F = (F - {out}) | {inn}
        assert sorted(F) == m['final_set']
        final_cost = sum(
            min(abs(x - sites[i][0]) + abs(y - sites[i][1]) for i in F)
            for x, y in clients
        )
        assert final_cost == m['cost']
        # local optimum: no improving single swap remains
        improved = False
        for out in F:
            for inn in range(len(sites)):
                if inn in F:
                    continue
                F2 = (F - {out}) | {inn}
                c2 = sum(min(abs(x - sites[i][0]) + abs(y - sites[i][1]) for i in F2)
                         for x, y in clients)
                if c2 < final_cost:
                    improved = True
        assert not improved


def test_steepest_descent_each_step():
    task = FacilityMemberSwapDescent()
    for _ in range(200):
        ex = task.generate_example()
        m = ex.metadata
        sites = m['sites']
        clients = m['clients']

        def cost(F):
            return sum(min(abs(x - sites[i][0]) + abs(y - sites[i][1]) for i in F)
                       for x, y in clients)

        F = set(m['initial'])
        cur = cost(F)
        for out, inn in m['seq']:
            assert out in F and inn not in F
            best = None
            for o in F:
                for n in range(len(sites)):
                    if n in F:
                        continue
                    c2 = cost((F - {o}) | {n})
                    imp = cur - c2
                    if imp > 0:
                        key = (-imp, o, n)
                        if best is None or key < best:
                            best = key
            assert best is not None
            assert best == (-(cur - cost((F - {out}) | {inn})), out, inn)
            F = (F - {out}) | {inn}
            cur = cost(F)


def test_level_scaling_changes_config():
    cfg = FacilitySwapConfig()
    base = (cfg.clients, cfg.sites, cfg.k, cfg.coord_range)
    cfg.set_level(6)
    high = (cfg.clients, cfg.sites, cfg.k, cfg.coord_range)
    assert any(h > b for h, b in zip(high, base))
    cfg.set_level(0)
    assert (cfg.clients, cfg.sites, cfg.k, cfg.coord_range) == base


def test_reproducible_under_seed():
    random.seed(1234)
    a = FacilityMemberSwapDescent().generate_example()
    random.seed(1234)
    b = FacilityMemberSwapDescent().generate_example()
    assert a.answer == b.answer
    assert a.prompt == b.prompt


def test_all_levels_generate():
    task = FacilityMemberSwapDescent()
    for level in range(7):
        ex = task.generate_example(level=level)
        assert ex.prompt and ex.answer
        assert task.score_answer(ex.answer, ex) == 1.0
