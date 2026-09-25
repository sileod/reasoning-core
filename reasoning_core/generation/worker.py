"""Generate one batch of one task and write it atomically. Scheduling lives in build.py."""
import random, os, time, json
from pathlib import Path

# Thread controls (must be before numpy/scipy imports)
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

from reasoning_core import get_task
import numpy as np

def serialize_example(example):
    row = example.to_dict()
    metadata = row.get('metadata')
    if metadata:
        row['task'] = metadata.get('source_task', row.get('task'))
        row['metadata'] = json.dumps(metadata)
    return row

def log_batch(log_path, name, level, dt, n, status):
    '''One line per BATCH attempt, including the ones that produce no rows.

    Row-level `_time` only covers accepted rows, so it silently omits rejected candidates and
    entirely-failed batches -- i.e. exactly the tasks that are expensive. This is the honest cost.
    '''
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({'task': name, 'level': level, 'batch_time_s': round(dt, 4),
                                'rows': n, 'status': status, 'ts': time.time()}) + '\n')
    except Exception:
        pass


def run_task(name, idx, level, out_path, batch_size, max_tokens, log_path=None):
    '''Run a single task batch, return (success, message).'''
    log_path = log_path or Path(out_path).parent / 'batches.jsonl'
    t0 = time.perf_counter()
    try:
        T = get_task(name)
        random.seed(None)
        np.random.seed(None)

        examples = T.generate_balanced_batch(
            batch_size=batch_size,
            max_tokens=max_tokens,
            level=level,
            timeout=20 * (1 + level) ** 2,
        )
        dt = time.perf_counter() - t0

        if not examples:
            log_batch(log_path, name, level, dt, 0, 'EMPTY')
            return False, 'EMPTY'

        for x in examples:
            m = x.metadata if isinstance(x.metadata, dict) else None
            if m is not None:
                m['_batch_time_s'] = round(dt, 4)
                m['_batch_n'] = len(examples)
                m['_batch_time_per_row_s'] = round(dt / len(examples), 5)

        # Serialise EVERYTHING before creating the file. The old code opened the file and then
        # serialised row by row, so a raise mid-write (coreference: 'Object of type Entity is not
        # JSON serializable') left a 0-byte .jsonl indistinguishable from a real empty batch --
        # and because the file existed, the worker never retried that batch.
        payload = ''.join(json.dumps(serialize_example(x)) + '\n' for x in examples)
        # Atomic: a worker killed mid-write must not leave a partial file that exists() skips.
        final = Path(out_path) / f'{name}-{idx}.jsonl'
        staged = final.with_suffix(f'.{os.getpid()}.tmp')
        staged.write_text(payload)
        os.replace(staged, final)
        log_batch(log_path, name, level, dt, len(examples), 'OK')
        return True, 'OK'
    except Exception as e:
        log_batch(log_path, name, level, time.perf_counter() - t0, 0, 'ERR:' + type(e).__name__)
        return False, f'ERR: {type(e).__name__}: {e}'
