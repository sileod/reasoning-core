from reasoning_core.tasks.generated.k3_scope_and_binding_r1.linear_scan_register_allocation.linear_scan_register_allocation import (
    LinearScanRegisterAllocation,
    LinearScanRegisterAllocationConfig,
    _allocate,
)


def test_allocate_simple():
    intervals = [(0, 5), (3, 8)]
    out = _allocate(intervals, 1)
    assert out[0] == 0
    assert out[1] == 'S'


def test_allocate_two_regs():
    intervals = [(0, 5), (3, 8)]
    out = _allocate(intervals, 2)
    assert out == [0, 1]


def test_generate_example_default():
    task = LinearScanRegisterAllocation()
    task.config = LinearScanRegisterAllocationConfig()
    ex = task.generate_example()
    assert ex.answer
    assert task.score_answer(ex.answer, ex) == 1.0
    assert task.score_answer('', ex) < 1.0
    assert task.score_answer('junk', ex) < 1.0


def test_levels_survive():
    task = LinearScanRegisterAllocation()
    for level in range(7):
        cfg = LinearScanRegisterAllocationConfig()
        cfg.set_level(level)
        task.config = cfg
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_intervals_valid():
    task = LinearScanRegisterAllocation()
    for level in range(7):
        cfg = LinearScanRegisterAllocationConfig()
        cfg.set_level(level)
        task.config = cfg
        for _ in range(25):
            ex = task.generate_example()
            md = ex.metadata
            for s, e in md["intervals"]:
                assert s <= e
            assert len(md["outcomes"]) == len(md["intervals"])
            for o in md["outcomes"]:
                assert o == 'S' or (isinstance(o, int) and 0 <= o < md["regs"])


def test_reg_pressure_spill():
    # Two overlapping intervals forcing a spill with one register.
    out = _allocate([(0, 5), (3, 8)], 1)
    assert out[0] == 0 and out[1] == 'S'


def test_evict_farthest():
    # v0 [0,2], v1 [1,3], v2 [3,10]; only one register.
    # v0 takes reg at 0. v1 starts at 1, no free reg, victim=v0(end2);
    # 2 > 3? no so v1 spills itself. v2 starts at 3, v0 ended(2<3), free reg -> v2.
    out = _allocate([(0, 2), (1, 3), (3, 10)], 1)
    assert out[0] == 0 and out[1] == 'S' and out[2] == 0


def test_evict_victim():
    # v0 [0,10], v1 [2,8], v2 [9,20]; one register.
    # v0->0 at 0. v1 at 2: victim v0(end10), 10>8 -> evict v0 -> spill v0; v1->0.
    # v2 at 9: v1 ended(8<9), free -> v2->0.
    out = _allocate([(0, 10), (2, 8), (9, 20)], 1)
    assert out[0] == 'S' and out[1] == 0 and out[2] == 0


def test_self_spill_under_pressure():
    # v0 [0,10], v1 [2,3]; one register. v1 starts at 2, no free reg;
    # victim v0 end 10 > 3 so v0 is evicted (spilled); v1 gets the register.
    out = _allocate([(0, 10), (2, 3)], 1)
    assert out[0] == 'S' and out[1] == 0
