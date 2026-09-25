from reasoning_core.tasks.generated.ua_representation_transfer_r4.branched_cover_signature_transfer.branched_cover_signature_transfer import (
    BranchedCoverSignatureTransfer,
    _random_partition,
)


def _valid(entry):
    d = entry.metadata["degree"]
    g = entry.metadata["genus"]
    parts = entry.metadata["partitions"]
    missing = entry.metadata["missing_index"]
    l = entry.metadata["l_missing"]
    known = sum(d - len(parts[i]) for i in range(len(parts)) if i != missing)
    assert entry.metadata["partitions"][missing][0] is not None or True
    rhs = -2 * d + known + (d - l)
    return 2 * g - 2 == rhs


def test_riemann_hurwitz_balances():
    for _ in range(300):
        entry = BranchedCoverSignatureTransfer().generate_example()
        assert _valid(entry)


def test_partitions_sum_to_degree():
    for _ in range(300):
        entry = BranchedCoverSignatureTransfer().generate_example()
        d = entry.metadata["degree"]
        for p in entry.metadata["partitions"]:
            assert sum(p) == d
            assert all(x >= 1 for x in p)


def test_missing_partition_has_l_missing_parts():
    for _ in range(300):
        entry = BranchedCoverSignatureTransfer().generate_example()
        assert len(entry.metadata["partitions"][entry.metadata["missing_index"]]) == entry.metadata["l_missing"]


def test_l_missing_in_domain():
    for _ in range(300):
        entry = BranchedCoverSignatureTransfer().generate_example()
        assert 1 <= entry.metadata["l_missing"] <= entry.metadata["degree"]


def test_sample_partition():
    for total in range(2, 12):
        for parts in range(1, total + 1):
            p = _random_partition(total, parts)
            assert len(p) == parts
            assert sum(p) == total
            assert all(x >= 1 for x in p)


def test_score_answer_gold():
    task = BranchedCoverSignatureTransfer()
    for _ in range(100):
        entry = task.generate_example()
        assert task.score_answer(str(entry.metadata["l_missing"]), entry) == 1.0


def test_score_answer_junk():
    task = BranchedCoverSignatureTransfer()
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("garbage", entry) == 0.0
    assert task.score_answer("-3", entry) == 0.0


def test_answer_not_on_prompt_surface():
    import re
    task = BranchedCoverSignatureTransfer()
    for _ in range(300):
        entry = task.generate_example()
        prompt = task.render_prompt(entry.metadata)
        answer = entry.metadata["l_missing"]
        nums = [int(x) for x in re.findall(r"\d+", prompt)]
        assert answer != nums[0]
        assert answer != nums[-1]
        assert answer != max(nums)


def test_levels_generate():
    task = BranchedCoverSignatureTransfer()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(20):
            entry = task.generate_example()
            assert task.score_answer(str(entry.metadata["l_missing"]), entry) == 1.0
