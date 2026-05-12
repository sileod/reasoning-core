"""
big_o_validator.py
==================
Cross-validates ComplexityProfiler labels against the `big_O` library.

Design notes
------------
- big_O is timing-based, not op-counting; it can be slow on O(n^2)
  programs at large n. We therefore cap max_n aggressively and enforce
  a per-call wall-clock timeout.
- Import is lazy: if big_O is absent, validator returns 'unavailable'
  and generation proceeds without cross-validation.
"""

import io
import contextlib
import threading
from typing import Optional


def _try_import_big_o():
    try:
        import big_o
        return big_o
    except ImportError:
        return None


_BIG_O_NAME_MAP = {
    'Constant':      'O(1)',
    'Logarithmic':   'O(log n)',
    'Linear':        'O(n)',
    'Linearithmic':  'O(n log n)',
    'Quadratic':     'O(n^2)',
    'Polynomial':    'other',
    'Cubic':         'other',
    'Exponential':   'other',
}


class BigOValidator:
    """
    Parameters
    ----------
    min_n, max_n : int
        Probe range. Keep max_n modest — big_O will invoke solve() at max_n
        for several repeats, and pure-Python arithmetic scales badly.
    n_measures, n_repeats : int
        Measurement density. Defaults are deliberately small for speed.
    timeout : float
        Wall-clock cap per classify() call in seconds. Programs that exceed
        this return 'error'. This is the safety net for pathological cases.
    """

    def __init__(self,
                 min_n: int = 50,
                 max_n: int = 1000,
                 n_measures: int = 10,
                 n_repeats: int = 3,
                 timeout: float = 15.0):
        self.min_n = min_n
        self.max_n = max_n
        self.n_measures = n_measures
        self.n_repeats = n_repeats
        self.timeout = timeout

    def classify(self, code: str, entry: str = 'solve') -> str:
        big_o = _try_import_big_o()
        if big_o is None:
            return 'unavailable'

        # Extract the entry function
        try:
            env: dict = {}
            exec(code, env)
        except Exception:
            return 'error'

        if entry not in env:
            return 'error'
        func = env[entry]

        # Run big_o under a timeout
        result = {'label': 'error'}

        def _worker():
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    best, _others = big_o.big_o(
                        func,
                        lambda n: n,
                        min_n=self.min_n,
                        max_n=self.max_n,
                        n_measures=self.n_measures,
                        n_repeats=self.n_repeats,
                    )
                result['label'] = _BIG_O_NAME_MAP.get(
                    type(best).__name__, 'other'
                )
            except Exception:
                result['label'] = 'error'

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        t.join(self.timeout)

        if t.is_alive():
            # Thread leak is acceptable here — it's daemon and will die
            # with the parent process. We just give up and return 'error'.
            return 'error'

        return result['label']
