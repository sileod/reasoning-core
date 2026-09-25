import random
from dataclasses import dataclass

from sympy import divisors

from reasoning_core.template import Config, Entry, Task


@dataclass
class WittGhostConfig(Config):
    family: str = "p_typical"
    p: int = 3
    min_len: int = 3
    max_len: int = 3
    max_coord: int = 2

    def apply_difficulty(self, level):
        self.max_len = self.min_len + level
        self.max_coord = 2 + level
        self.p = random.choice([2, 3, 5])


GHOST_BOUND = 10**9


def _p_ghosts(p, a):
    n = len(a)
    w = []
    for i in range(n):
        w.append(sum((p ** j) * (a[j] ** (p ** (i - j))) for j in range(i + 1)))
    return w


def _p_coords(n, max_coord):
    a = [random.choice([-1, 0, 1]) for _ in range(n - 1)]
    a.append(random.randint(-max_coord, max_coord))
    return a


def _p_recover(p, w):
    n = len(w)
    a = [0] * n
    for i in range(n):
        s = sum((p ** j) * (a[j] ** (p ** (i - j))) for j in range(i))
        num = w[i] - s
        if num % (p ** i) != 0:
            return a, i
        a[i] = num // (p ** i)
    return a, None


def _big_coords(n, max_coord):
    a = [0] + [random.choice([-1, 0, 1]) for _ in range(n - 1)]
    a.append(random.randint(-max_coord, max_coord))
    return a


def _big_ghosts(a):
    n = len(a) - 1
    w = [0] * (n + 1)
    for m in range(1, n + 1):
        val = 0
        for d in divisors(m):
            val += d * (a[d] ** (m // d))
        w[m] = val
    return w


def _big_recover(w):
    n = len(w) - 1
    a = [0] * (n + 1)
    for m in range(1, n + 1):
        s = 0
        for d in divisors(m):
            if d < m:
                s += d * (a[d] ** (m // d))
        num = w[m] - s
        if num % m != 0:
            return a[1:], m
        a[m] = num // m
    return a[1:], None


def _fmt_vec(v):
    return ",".join(str(int(x)) for x in v)


class WittGhostCoordinateTranslation(Task):
    summary = ("Translate truncated big or p-typical Witt coordinates to ghost components and recover "
               "integer coordinates by triangular inversion; answer the vector or the first divisibility "
               "obstruction.")
    design_choice = ("Answer format: output the full integer coordinate vector as a comma-separated list "
                     "of integers, with a separate mode that outputs the first index where a required "
                     "divisibility fails as an integer index (1-based).")
    config_cls = WittGhostConfig

    def generate_entry(self):
        family = random.choice(["p_typical", "big"])
        mode = random.choice(["to_ghost", "from_ghost", "obstruction"])
        p = self.config.p
        n = random.randint(self.config.min_len, self.config.max_len)
        max_coord = self.config.max_coord
        cfg = self.config.family

        for _ in range(200):
            if family == "p_typical":
                coords = _p_coords(n, max_coord)
                ghosts = _p_ghosts(p, coords)
                recover = _p_recover
                recover_kwargs = (p,)
            else:
                coords = _big_coords(n, max_coord)
                ghosts = _big_ghosts(coords)
                recover = _big_recover
                recover_kwargs = ()

            if any(abs(int(g)) > GHOST_BOUND for g in ghosts[1:] if int(g)):
                continue

            if mode == "to_ghost":
                answer = _fmt_vec(ghosts[1:] if family == "big" else ghosts)
                given = _fmt_vec(coords[1:] if family == "big" else coords)
                obstruction_index = None
            else:
                rec_coords, fail = recover(*recover_kwargs, ghosts)
                if mode == "from_ghost":
                    if fail is not None:
                        continue
                    if rec_coords != (coords[1:] if family == "big" else coords):
                        continue
                    answer = _fmt_vec(coords[1:] if family == "big" else coords)
                    given = _fmt_vec(ghosts[1:] if family == "big" else ghosts)
                    obstruction_index = None
                else:
                    if family == "p_typical":
                        i0 = random.randint(1, n - 1)
                        ghosts[i0] += random.choice([-1, 1])
                        rec2, fail2 = _p_recover(p, ghosts)
                        if fail2 != i0:
                            continue
                        obstruction_index = i0 + 1
                        answer = str(obstruction_index)
                    else:
                        i0 = random.randint(2, n)
                        ghosts[i0] += random.choice([-1, 1])
                        rec2, fail2 = _big_recover(ghosts)
                        if fail2 != i0:
                            continue
                        obstruction_index = i0
                        answer = str(obstruction_index)
                    given = _fmt_vec(ghosts[1:] if family == "big" else ghosts)
            break
        else:
            raise RuntimeError("unable to generate a valid instance")

        metadata = {
            "family": family,
            "p": int(p) if family == "p_typical" else None,
            "mode": mode,
            "n": int(n),
            "given": given,
            "obstruction_index": obstruction_index,
        }
        return Entry(metadata=metadata, answer=answer)

    def _render_prompt(self, metadata):
        family = metadata["family"]
        mode = metadata["mode"]
        given = metadata["given"]
        n = metadata["n"]
        if family == "p_typical":
            p = metadata["p"]
            label = f"p-typical Witt vector with p={p}, truncated to {n} coordinates"
            if mode == "to_ghost":
                body = (f"You are given a truncated {label} with integer Witt coordinates "
                        f"(a_0, ..., a_{n - 1}) = ({given}). Its ghost components are "
                        f"w_i = sum_{{(j=0)}}^i p^j * a_j^(p^(i-j)) for i = 0..{n - 1}. "
                        f"Compute the ghost component vector (w_0, ..., w_{n - 1}).")
                fmt = "Answer as a comma-separated list of integers in order, e.g. '3,-5,10'."
            elif mode == "from_ghost":
                body = (f"You are given ghost components (w_0, ..., w_{n - 1}) = ({given}) of a "
                        f"truncated {label} over the integers, where "
                        f"w_i = sum_{{(j=0)}}^i p^j * a_j^(p^(i-j)). The components are consistent, so "
                        f"each a_i = (w_i - sum_{{(j<i)}} p^j * a_j^(p^(i-j))) / p^i is an integer. "
                        f"Recover the integer Witt coordinates (a_0, ..., a_{n - 1}) by triangular inversion.")
                fmt = "Answer as a comma-separated list of integers in order, e.g. '3,-5,10'."
            else:
                body = (f"You are given ghost components (w_0, ..., w_{n - 1}) = ({given}) of a truncated "
                        f"{label}, and the integer Witt coordinates (a_0, ..., a_{n - 1}) below them "
                        f"must satisfy w_i = sum_{{(j=0)}}^i p^j * a_j^(p^(i-j)). For each i the coordinate "
                        f"a_i is obtained as (w_i - sum_{{(j<i)}} p^j * a_j^(p^(i-j))) / p^i and is an "
                        f"integer only if that division by p^i is exact. Identify the FIRST index "
                        f"(counting a_0 as index 1) at which this required divisibility by p^i fails.")
                fmt = "Answer with that single 1-based integer index."
        else:
            label = f"truncated big Witt vector with coordinates a_1..a_{n}"
            if mode == "to_ghost":
                body = (f"You are given a {label} with integer Witt coordinates (a_1, ..., a_{n}) = "
                        f"({given}). Its ghost components are w_m = sum_{{(d | m)}} d * a_d^(m/d) for "
                        f"m = 1..{n}. Compute the ghost component vector (w_1, ..., w_{n}).")
                fmt = "Answer as a comma-separated list of integers in order, e.g. '3,-5,10'."
            elif mode == "from_ghost":
                body = (f"You are given ghost components (w_1, ..., w_{n}) = ({given}) of a {label} over "
                        f"the integers, where w_m = sum_{{(d | m)}} d * a_d^(m/d). The components are "
                        f"consistent, so each a_m = (w_m - sum_{{(d | m, d<m)}} d * a_d^(m/d)) / m is an "
                        f"integer. Recover the integer Witt coordinates (a_1, ..., a_{n}) by triangular "
                        f"inversion.")
                fmt = "Answer as a comma-separated list of integers in order, e.g. '3,-5,10'."
            else:
                body = (f"You are given ghost components (w_1, ..., w_{n}) = ({given}) of a {label}, and "
                        f"the integer Witt coordinates (a_1, ..., a_{n}) below them must satisfy "
                        f"w_m = sum_{{(d | m)}} d * a_d^(m/d). For each m the coordinate a_m is obtained "
                        f"as (w_m - sum_{{(d | m, d<m)}} d * a_d^(m/d)) / m and is an integer only if that "
                        f"division by m is exact. Identify the FIRST index m at which this required "
                        f"divisibility by m fails.")
                fmt = "Answer with that single 1-based integer index."
        return f"{body} {fmt}"

    def render_prompt(self, metadata):
        return self._render_prompt(metadata)


TASK_META = {'parent_source_id': None,
 'idea': 'witt_ghost_coordinate_translation (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_hierarchical_recursive_r4/witt_ghost_coordinate_translation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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
                                         'version': 'bubblewrap 0.8.0'}}}}
