"""Directional-light occlusion delta: flood light around opaque cells, then
insert or remove one occluder and report the flipped cells and each source's
covered set. Solver-backed by an explicit shadow-casting routine (no external
solver exists for this combinatorial geometry), with the gold answer derived
and the defining lit/dark-change direction asserted per delta type."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'grid_light_occlusion_delta (draw 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_counterfactual_r1/grid_light_occlusion_delta',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

_MAX_ATTEMPTS = 400


def _in_bounds(cell, h, w):
    r, c = cell
    return 0 <= r < h and 0 <= c < w


def _cast(source, occluders, h, w):
    """Covered set of one source: its own cell plus each of four cardinal rays
    extended until (not including) the first opaque cell or the grid edge."""
    sr, sc = source
    lit = {(sr, sc)}
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        r, c = sr + dr, sc + dc
        while _in_bounds((r, c), h, w):
            if (r, c) in occluders:
                break
            lit.add((r, c))
            r, c = r + dr, c + dc
    return lit


def _union_cast(sources, occluders, h, w):
    lit = set()
    for s in sources:
        lit |= _cast(s, occluders, h, w)
    return lit


def _fmt_cells(sorted_cells):
    return '[' + ','.join(f'({r},{c})' for r, c in sorted_cells) + ']'


def _parse_cell_list(text):
    inner = text.strip().strip('[]').strip()
    if not inner:
        return set()
    items = inner.split('),(')
    out = set()
    for it in items:
        digits = it.replace('(', '').replace(')', '').strip()
        if not digits:
            continue
        rr, cc = digits.split(',')
        out.add((int(rr.strip()), int(cc.strip())))
    return out


def _parse_answer(text):
    """Return dict mapping 'flipped' and each source label to a set of cells."""
    result = {}
    for part in text.split(';'):
        if ':' not in part:
            continue
        key, value = part.split(':', 1)
        result[key.strip()] = _parse_cell_list(value)
    return result


def _gold_answer(delta_type, delta_cell, h, w, sources, occluders):
    """Compute the canonical answer string. sources must already be sorted."""
    if delta_type == 'insert':
        occl_after = occluders | {delta_cell}
    else:
        occl_after = occluders - {delta_cell}
    lit_before = _union_cast(sources, occluders, h, w)
    lit_after = _union_cast(sources, occl_after, h, w)
    flipped = lit_before ^ lit_after
    parts = ['flipped:' + _fmt_cells(sorted(flipped))]
    for idx, src in enumerate(sources):
        cov = sorted(_cast(src, occl_after, h, w))
        parts.append(f'{chr(ord("A") + idx)}:' + _fmt_cells(cov))
    return ';'.join(parts)


@dataclass
class LightDeltaConfig(Config):
    size: int = 3
    num_sources: int = 1
    num_occluders: int = 2

    def apply_difficulty(self, level):
        self.size = 3 + level
        self.num_sources = 1 + (1 if level >= 2 else 0) + (1 if level >= 4 else 0)
        self.num_occluders = 2 + level


class LightOcclusionDelta(Task):
    summary = ("Flood directional light from sources around opaque cells on small "
               "grids via shadow casting, then insert or remove occluders; answer "
               "which cells flip between lit and dark and each source's covered set.")
    design_choice = ("Answer as a canonical set of flipped cell coordinates, sorted "
                     "lexicographically, with per-source covered sets as sorted "
                     "coordinate lists.")
    config_cls = LightDeltaConfig

    def generate_entry(self):
        c = self.config
        for _ in range(_MAX_ATTEMPTS):
            h = c.size + random.randint(0, 1)
            w = c.size + random.randint(0, 1)
            ns = c.num_sources
            no = c.num_occluders
            all_cells = [(r, col) for r in range(h) for col in range(w)]
            if len(all_cells) < ns + no + 1:
                continue
            sources = sorted(random.sample(all_cells, ns))
            source_set = set(sources)
            free = [cell for cell in all_cells if cell not in source_set]
            if len(free) < no + 1:
                continue
            occluders = set(random.sample(free, no))
            dtype = random.choice(('insert', 'remove'))
            if dtype == 'insert':
                lit_before = _union_cast(sources, occluders, h, w)
                avail = [cell for cell in free
                         if cell not in occluders and cell in lit_before]
                if not avail:
                    continue
                delta = random.choice(avail)
                occl_after = occluders | {delta}
            else:
                delta = random.choice(sorted(occluders))
                occl_after = occluders - {delta}
            lit_before = _union_cast(sources, occluders, h, w)
            lit_after = _union_cast(sources, occl_after, h, w)
            flipped = lit_before ^ lit_after
            if not flipped:
                continue
            if dtype == 'insert':
                assert flipped <= lit_before and not (flipped & lit_after), \
                    'insertion must only darken lit cells'
            else:
                assert flipped <= lit_after and not (flipped & lit_before), \
                    'removal must only brighten dark cells'
            answer = _gold_answer(dtype, delta, h, w, sources, occluders)
            metadata = {
                'h': h,
                'w': w,
                'sources': sources,
                'occluders': sorted(occluders),
                'delta_type': dtype,
                'delta_cell': delta,
                'num_sources': ns,
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError('LightOcclusionDelta: failed to build a valid instance')

    def render_prompt(self, metadata):
        m = metadata
        grid = [['.' for _ in range(m['w'])] for _ in range(m['h'])]
        for r, col in m['occluders']:
            grid[r][col] = '#'
        for idx, (r, col) in enumerate(m['sources']):
            grid[r][col] = chr(ord('A') + idx)
        grid_str = '\n'.join(' '.join(row) for row in grid)
        labels = ' '.join(chr(ord('A') + i) for i in range(m['num_sources']))
        kinds = ", ".join(
            f"{chr(ord('A') + i)}: source {chr(ord('A') + i)}"
            for i in range(m['num_sources']))
        if m['delta_type'] == 'insert':
            change = f"A new opaque cell is inserted at ({m['delta_cell'][0]},{m['delta_cell'][1]})."
        else:
            change = f"The opaque cell at ({m['delta_cell'][0]},{m['delta_cell'][1]}) is removed."
        return (
            f"An {m['h']}x{m['w']} grid holds opaque cells (#) and light sources "
            f"({kinds}). A source lights its own cell and every cell in a straight "
            f"line in each of the four cardinal directions (up, down, left, right) "
            f"from it, stopping when it reaches an opaque cell or the grid edge; "
            f"that opaque cell and everything beyond it in that direction stay "
            f"dark. Cells are referenced (row,column), 0-indexed.\n\n"
            f"Grid before the change:\n{grid_str}\n\n"
            f"{change}\n\n"
            f"Report (1) the set of cells whose lit status flips between lit and "
            f"dark because of this change and (2) for each source in order "
            f"{labels}, its covered set (the cells it lights) in the after "
            f"configuration. Sort every coordinate list lexicographically by "
            f"(row,column), and list each set's cells also sorted "
            f"lexicographically.\n\n"
            f"Answer as one line in the format "
            f"flipped:[(r,c),(r,c),...];A:[(r,c),...];B:[(r,c),...] ."
        )

    def score_answer(self, answer, entry):
        try:
            gold = _parse_answer(entry['answer'])
            got = _parse_answer(answer)
        except Exception:
            return 0.0
        if set(gold) != set(got):
            return 0.0
        for key in gold:
            if gold[key] != got[key]:
                return 0.0
        return 1.0
