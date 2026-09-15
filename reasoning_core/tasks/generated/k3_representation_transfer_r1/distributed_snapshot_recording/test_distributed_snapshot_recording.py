from reasoning_core.tasks.generated.k3_representation_transfer_r1.distributed_snapshot_recording.distributed_snapshot_recording import (  # noqa: E501
    DistributedSnapshotRecording,
    SnapshotConfig,
)


def _check_consistency(entry):
    n = entry.metadata["num_processes"]
    channels = entry.metadata["channels"]
    send_before = entry.metadata["send_before"]
    recv_before = entry.metadata["recv_before"]
    recv_counts = entry.metadata["recv_counts"]
    channel_record = entry.metadata["channel_record"]

    assert n >= 3
    # consistency: recv_before <= send_before
    for sb, rb in zip(send_before, recv_before):
        assert rb <= sb
    # channel record = indexes rb..sb-1
    for (s, t, k), sb, rb, inflight in zip(
        channels, send_before, recv_before, channel_record
    ):
        assert 0 <= rb <= sb <= k
        assert inflight == list(range(rb, sb))
    # recv_counts matches incoming sum
    counts = [0] * n
    for (s, t, k), rb in zip(channels, recv_before):
        counts[t] += rb
    assert counts == recv_counts
    # no message is both sent-and-recorded-as-received (consistent): inflight disjoint
    # from received set handled by rb<=sb
    return True


def test_gold_scores_one():
    task = DistributedSnapshotRecording()
    for _ in range(20):
        entry = task.generate_example()
        assert _check_consistency(entry)
        assert task.score_answer(entry.answer, entry) == 1.0


def test_wrong_scores_zero():
    task = DistributedSnapshotRecording()
    for _ in range(10):
        entry = task.generate_example()
        assert task.score_answer("garbage", entry) == 0.0
        assert task.score_answer("", entry) == 0.0


def test_difficulty_changes():
    task = DistributedSnapshotRecording()
    base = task.config.num_processes
    task.config.set_level(6)
    assert task.config.num_processes > base


def test_deterministic_seed():
    import random

    random.seed(7)
    task = DistributedSnapshotRecording()
    e1 = task.generate_example().answer
    random.seed(7)
    task2 = DistributedSnapshotRecording()
    e2 = task2.generate_example().answer
    assert e1 == e2
