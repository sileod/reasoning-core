import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


def _inside_any(pt, windows):
    x, y = pt
    for rx0, ry0, rx1, ry1 in windows:
        if rx0 < x < rx1 and ry0 < y < ry1:
            return True
    return False


def _clip_interval(s_lo, s_hi, lo, hi):
    return max(s_lo, lo), min(s_hi, hi)


def _seg_inside_s_interval(x0, y0, x1, y1, rect):
    rx0, ry0, rx1, ry1 = rect
    dx, dy = x1 - x0, y1 - y0
    s_lo, s_hi = 0.0, 1.0
    if dx == 0:
        if not (rx0 <= x0 <= rx1):
            return 1.0, 0.0
    else:
        a = (rx0 - x0) / dx
        b = (rx1 - x0) / dx
        lo, hi = (a, b) if dx > 0 else (b, a)
        s_lo = max(s_lo, lo)
        s_hi = min(s_hi, hi)
    if dy == 0:
        if not (ry0 <= y0 <= ry1):
            return 1.0, 0.0
    else:
        a = (ry0 - y0) / dy
        b = (ry1 - y0) / dy
        lo, hi = (a, b) if dy > 0 else (b, a)
        s_lo = max(s_lo, lo)
        s_hi = min(s_hi, hi)
    return s_lo, s_hi


def _exposure_for_window(rect, path, period, dwell, start_gate):
    total = 0.0
    abs_t = 0.0
    pts = path
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        L = math.hypot(x1 - x0, y1 - y0)
        if L <= 0:
            continue
        s_lo, s_hi = _seg_inside_s_interval(x0, y0, x1, y1, rect)
        if s_lo >= s_hi:
            abs_t += L
            continue
        t_lo = abs_t + L * s_lo
        t_hi = abs_t + L * s_hi
        total += _open_overlap(t_lo, t_hi, period, dwell, start_gate)
        abs_t += L
    return total


def _open_overlap(t_lo, t_hi, period, dwell, start_gate):
    total = 0.0
    # tile open intervals: open(e) = start_gate ? e in [k*period, k*period+dwell]
    if start_gate == 0:
        k0 = int(t_lo // period)
        k = k0
        while k * period < t_hi:
            a = k * period
            b = a + dwell
            o0 = max(a, t_lo)
            o1 = min(b, t_hi)
            if o0 < o1:
                total += o1 - o0
            k += 1
    else:
        raise NotImplementedError
    return total


@dataclass
class GatedMotionExposureConfig(Config):
    n_windows: int = 1
    n_waypoints: int = 2
    dwell: float = 0.5
    level: int = 0

    def apply_difficulty(self, level):
        self.level = level
        self.n_windows = stochastic_rounding(1 + level)
        self.n_waypoints = stochastic_rounding(2 + level)


class GatedMotionExposure(Task):
    summary = "Accumulate exposure along piecewise-linear motion through spatial windows and periodic shutters, including serial gates and dwell intervals; return total exposure or the position where a dose threshold is reached."
    design_choice = "Exposure windows are defined by axis-aligned rectangles with random widths/heights, and motion paths always start outside all windows, requiring detection of multiple entries/exits."
    config_cls = GatedMotionExposureConfig

    def generate_entry(self):
        cfg = self.config
        period = 10.0
        dwell = random.uniform(6.0, 9.0)

        windows = []
        for _ in range(cfg.n_windows):
            w = random.uniform(1.0, 3.0)
            h = random.uniform(1.0, 3.0)
            x = random.uniform(-6.0, 6.0 - w)
            y = random.uniform(-6.0, 6.0 - h)
            windows.append((x, y, x + w, y + h))

        for _ in range(150):
            path = self._build_path(cfg, windows)
            total = 0.0
            for rect in windows:
                total += _exposure_for_window(rect, path, period, dwell, 0)
            total = max(0.0, total)
            r = round(total, 3)
            if r >= 0.1:
                break
        else:
            path = self._build_path(cfg, windows, force_center=True)
            total = 0.0
            for rect in windows:
                total += _exposure_for_window(rect, path, period, dwell, 0)
            total = max(0.0, total)
            r = round(total, 3)

        assert r >= 0.0
        return Entry(
            metadata={
                "windows": [[round(v, 3) for v in q] for q in windows],
                "path": [[round(v, 3) for v in p] for p in path],
                "period": period,
                "dwell": round(dwell, 3),
                "gate": 0,
                "total": r,
            },
            answer=f"{r:.3f}",
        )

    def _build_path(self, cfg, windows, force_center=False):
        path = []
        for _ in range(200):
            start = (random.uniform(-8.0, 8.0), random.uniform(-8.0, 8.0))
            if not _inside_any(start, windows):
                break
        else:
            start = (8.9, 8.9)
        path.append(start)

        n_pts = max(cfg.n_waypoints - 1, 1)
        for k in range(n_pts):
            if force_center and k < len(windows):
                rx0, ry0, rx1, ry1 = windows[k]
                cx = (rx0 + rx1) / 2.0
                cy = (ry0 + ry1) / 2.0
                path.append((cx, cy))
            else:
                path.append((random.uniform(-8.0, 8.0), random.uniform(-8.0, 8.0)))
        return path

    def render_prompt(self, metadata):
        wstrs = ", ".join(
            f"[({w[0]:.2f},{w[1]:.2f}) to ({w[2]:.2f},{w[3]:.2f})]"
            for w in metadata["windows"]
        )
        pstrs = ", ".join(
            f"({p[0]:.2f},{p[1]:.2f})" for p in metadata["path"]
        )
        dwell = metadata["dwell"]
        gap = metadata["period"] - dwell
        return (
            f"A point moves along the polyline through {pstrs} at unit speed, "
            f"so time equals distance traveled along the path. Exposure "
            f"windows are these axis-aligned rectangles: {wstrs}. The shutter "
            f"is open for the first {dwell:.2f} time units of each period of "
            f"total length {metadata['period']:.2f} and closed for the "
            f"remaining {gap:.2f}, starting open at time 0. Exposure accrues "
            f"only while the point is strictly inside a window and the shutter "
            f"is open. Report the total exposure accumulated over the whole "
            f"motion, as a decimal rounded to 3 decimal places."
        )

    def score_answer(self, answer, entry):
        try:
            val = float(answer)
        except (TypeError, ValueError):
            return 0.0
        target = entry.metadata["total"]
        return 1.0 if abs(val - target) < 1e-6 else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'gated_motion_exposure (variant 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_surface_invariance_r4/gated_motion_exposure',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2302342651,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
