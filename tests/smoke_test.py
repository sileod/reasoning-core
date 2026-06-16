import pytest
from reasoning_core import list_tasks, get_task
import time

def test_all_tasks_validate():
    failed = []
    for t in list_tasks():
        t0 = time.time()
        try:
            task = get_task(t)
            task.validate(n_samples=5)
            print(f"{t.ljust(30, '.')}", end=' ')
            print(f"{time.time() - t0:.5f}")
        except Exception as e:
            print(f"{t.ljust(30, '.')}", end=' ')
            print(f"EXCEPTION: {e}")
            failed.append(t)

    if failed:
        raise RuntimeError(f"Failed tasks: {failed}")