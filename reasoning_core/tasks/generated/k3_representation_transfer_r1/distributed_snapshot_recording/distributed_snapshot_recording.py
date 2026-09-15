"""Marker-driven snapshot recording over processes with directed channels.

Represents process local states as integer counters that increment per
received message and channel contents as ordered message lists. The snapshot
must capture a consistent cut where no message is both sent and recorded as
received.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class SnapshotConfig(Config):
    num_processes: int = 3
    max_channels: int = 3
    max_msgs: int = 3

    def apply_difficulty(self, level):
        self.num_processes = stochastic_rounding(self.num_processes + 2 * level)
        self.max_channels = stochastic_rounding(self.max_channels + 2 * level)
        self.max_msgs = stochastic_rounding(self.max_msgs + 2 * level)


class DistributedSnapshotRecording(Task):
    summary = (
        "Execute marker-driven snapshots over processes with directed channels and "
        "in-flight messages, returning recorded process local states (integer "
        "counters incrementing per received message) and channel contents (ordered "
        "message lists), capturing a consistent cut where no message is both sent "
        "and recorded as received, with varying channel counts, per-channel message "
        "counts, and marker positions."
    )

    design_choice = (
        "Represent process states as integer counters that increment per received "
        "message, with channel contents as ordered message lists, and require the "
        "snapshot to capture a consistent cut where no message is both sent and "
        "recorded as received."
    )

    config_cls = SnapshotConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.num_processes

        nch = random.randrange(2, cfg.max_channels + 1)
        channels = []
        for _ in range(nch):
            s = random.randrange(n)
            t = random.randrange(n - 1)
            if t >= s:
                t += 1
            channels.append((s, t))

        per_chan = [random.randrange(1, cfg.max_msgs + 1) for _ in range(nch)]

        send_before = [random.randrange(0, k + 1) for k in per_chan]
        recv_before = [random.randrange(0, sb + 1) for sb in send_before]

        recv_counts = {p: 0 for p in range(n)}
        for (s, t), rb in zip(channels, recv_before):
            recv_counts[t] += rb

        channel_record = []
        for (s, t), k, sb, rb in zip(channels, per_chan, send_before, recv_before):
            inflight = list(range(rb, sb))
            channel_record.append(inflight)

        answer_parts = [f"{p}:{recv_counts[p]}" for p in range(n)]
        chan_strs = []
        for (s, t), inflight in zip(channels, channel_record):
            chan_strs.append(f"({s}->{t}):{inflight}")
        answer = "; ".join(answer_parts) + " | " + " ".join(chan_strs)

        metadata = {
            "num_processes": n,
            "channels": [(s, t, k) for (s, t), k in zip(channels, per_chan)],
            "send_before": send_before,
            "recv_before": recv_before,
            "recv_counts": [recv_counts[p] for p in range(n)],
            "channel_record": channel_record,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        n = metadata["num_processes"]
        chans = []
        for (s, t, k) in metadata["channels"]:
            chans.append(f"{s}->{t} carrying {k} message(s)")
        line = "; ".join(chans)
        return (
            f"A distributed system has {n} processes indexed 0..{n-1} with directed "
            f"channels between them. Each process's local state is a counter equal to "
            f"the number of messages it has received. Each channel carries an ordered "
            f"list of messages (indexed 0,1,2,... in send order). A Chandy-Lamport "
            f"marker is sent on every channel and each process records its state when "
            f"the marker reaches it. In the resulting consistent cut: a message sent "
            f"before the sender recorded its state AND delivered to the receiver "
            f"before the receiver recorded its state is recorded as received; a "
            f"message sent before the sender recorded its state but delivered to the "
            f"receiver after the receiver recorded its state is in-flight and is "
            f"recorded as the channel's content. No message is both recorded as "
            f"received and in-flight. Channels: {line}. Give the recorded snapshot "
            f"as: each process's received-message counter, then each channel's "
            f"in-flight message indexes. Answer format: "
            f"p0:c0; p1:c1; ... | (s0->t0):[i,..] (s1->t1):[...] ... — processes in "
            f"increasing index order, channels in the listed order, each channel's "
            f"in-flight indexes as a bracketed list in increasing index order."
        )

    def score_answer(self, answer, entry):
        return 1.0 if answer == entry.answer else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'distributed_snapshot_recording (draw 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_representation_transfer_r1/distributed_snapshot_recording',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}
