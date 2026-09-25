import random

import numpy as np

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'rigidity_brace_design (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_planning_backtracking_r4/rigidity_brace_design',
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

design_choice = "Instance form: joints on a regular grid with integer coordinates; answer is a list of bar indices (e.g., '1-4,2-5') chosen to satisfy a target infinitesimal motion subspace, with cost equal to bar length squared."


def _rigidity_matrix(bars, joint_ids, coords, grounded):
    """Rows = active bars, columns = free joints' (x,y) velocities.

    A grounded joint has its velocity fixed to zero, so it contributes no
    columns and a bar incident to it constrains only the free endpoint.
    """
    free = sorted(j for j in joint_ids if j not in grounded)
    f_index = {j: i for i, j in enumerate(free)}
    rows = []
    for (i, j) in bars:
        xi, yi = coords[i]
        xj, yj = coords[j]
        row = [0.0] * (2 * len(free))
        if i in grounded and j in grounded:
            continue
        if i not in grounded:
            r = f_index[i]
            row[2 * r] = xi - xj
            row[2 * r + 1] = yi - yj
        if j not in grounded:
            r = f_index[j]
            row[2 * r] = xj - xi
            row[2 * r + 1] = yj - yi
        rows.append(row)
    return np.array(rows, dtype=float) if rows else np.zeros((0, 2 * len(free)))


def _nullspace_basis(mat):
    """Orthonormal basis of the (right) nullspace of a small matrix via SVD."""
    if mat.shape[1] == 0 or mat.shape[0] == 0:
        dim = mat.shape[1]
        return np.eye(dim) if dim else np.zeros((mat.shape[1], 0))
    u, s, vh = np.linalg.svd(mat, full_matrices=True)
    tol = max(mat.shape) * s[0] * 1e-12 if s.size else 0.0
    rank = int(np.sum(s > tol))
    null_dim = mat.shape[1] - rank
    if null_dim <= 0:
        return np.zeros((mat.shape[1], 0))
    return vh[rank:].T


def _motion_dim_target_ok(bars, joint_ids, coords, grounded, k_target, tol=1e-8):
    """Final grounded motion space equals span(k_target)? Colls = free joints x2.

    Requires: every bar is orthogonal to the target subspace (target freedoms
    are preserved) and the total number of independent bars reaches 2F - dim(K).
    """
    free = sorted(j for j in joint_ids if j not in grounded)
    f = len(free)
    if k_target.shape[0] != 2 * f:
        raise ValueError("target subspace dimension mismatch")
    d = k_target.shape[1]
    r = _rigidity_matrix(bars, joint_ids, coords, grounded)
    if r.size == 0:
        r = np.zeros((0, 2 * f))
    if k_target.shape[1] and np.max(np.abs(r @ k_target)) > tol:
        return False
    u, s, _ = np.linalg.svd(r, full_matrices=False)
    tol2 = max(r.shape) * (s[0] if s.size else 0.0) * 1e-12
    rank = int(np.sum(s > tol2)) if s.size else 0
    return rank == 2 * f - d


def _format_bars(bars):
    parts = sorted(f"{i}-{j}" for (i, j) in bars)
    return ",".join(parts)


class RigidityBraceConfig(Config):
    n_joints: int = 5
    pool_extra: int = 3
    impossible_prob: float = 0.30

    def apply_difficulty(self, level):
        self.n_joints = 4 + level
        self.pool_extra = 1 + (level + 1) // 2
        self.impossible_prob = 0.25


class rigidity_brace_design(Task):
    summary = ("Grounded integer-grid frameworks: add a minimum-cost bar brace (cost = squared "
               "length) so the infinitesimal motions equal a prescribed subspace that keeps a "
               "single joint-rotation freedom or is fully rigid, or report impossibility; answer "
               "is a canonical sorted bar-list, 'none', or 'impossible'.")
    config_cls = RigidityBraceConfig

    def generate_entry(self):
        n_joints = self.config.n_joints
        pool_extra = max(0, self.config.pool_extra)
        impossible_prob = self.config.impossible_prob

        while True:
            # Integer coordinates on a small grid.
            pairs = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2), (1, 2), (2, 1),
                     (2, 2), (3, 0), (0, 3)]
            coords_list = random.sample(pairs, n_joints)
            joint_ids = list(range(n_joints))
            coords = {j: coords_list[j] for j in joint_ids}

            # Two grounded anchors; the rest are free.
            anchor_a, anchor_b = random.sample(joint_ids, 2)
            grounded = {anchor_a, anchor_b}
            free = sorted(j for j in joint_ids if j not in grounded)
            f = len(free)

            # Pivot joint whose rotation is the intended freedom (or rigid target).
            pivot = random.choice(free)
            rigid_target = random.random() < 0.30
            keep_dof = 0 if rigid_target else 1

            if rigid_target:
                # target = fully rigid (no mechanism); every free joint pinned to both anchors.
                base_bars = sorted((j, a) for j in free for a in (anchor_a, anchor_b))
            else:
                # target = single rotation freedom for the pivot about anchor_a;
                # all other free joints pinned fully rigid.
                base_bars = [(pivot, anchor_a)]
                for q in free:
                    if q != pivot:
                        base_bars.append((q, anchor_a))
                        base_bars.append((q, anchor_b))
                base_bars = sorted(base_bars)

            k_base = _nullspace_basis(
                _rigidity_matrix(base_bars, joint_ids, coords, grounded))
            if k_base.shape[1] != keep_dof:
                continue

            # Current framework F_0: remove some bars from the base so there is real
            # freedom to trim back (guaranteeing a non-empty minimum brace set).
            remove = []
            for (i, j) in base_bars:
                if pivot in (i, j) and not rigid_target and random.random() < 0.60:
                    remove.append((i, j))
                elif rigid_target and random.random() < 0.40:
                    remove.append((i, j))
            remove = sorted(set(remove))
            if not remove:
                continue
            current_bars = sorted(set(base_bars) - set(remove))

            # Permitted additions = removed bars plus random extras not already present.
            all_pairs = [(i, j) for i in joint_ids for j in joint_ids if i < j]
            absent = sorted(set(all_pairs) - set(current_bars))
            extra = random.sample(absent, min(pool_extra, len(absent)))
            extra = sorted(set(extra) - set(remove))
            pool = sorted(set(remove) | set(extra))

            # For impossible instances, drop every bar touching the pivot, which the
            # target must constrain -> unreachable. Guaranteed impossible: the target
            # needs the pivot constrained, and no permitted bar touches it. Only the
            # mechanism (non-rigid) mode can be genuinely impossible.
            want_impossible = (not rigid_target) and random.random() < impossible_prob
            if want_impossible:
                pool = [b for b in pool if pivot not in b]

            # Exhaustive minimum-cost search over subsets of the pool.
            result = _min_brace_set(current_bars, pool, joint_ids, coords, grounded,
                                    k_base, pivot, rigid_target)
            if result is None:
                continue
            bars_to_add, cost, unreachable = result
            if want_impossible and not unreachable:
                continue
            if not want_impossible and unreachable:
                continue
            # Keep 'impossible' and 'none' from dominating the label distribution.
            break

        if unreachable:
            answer = "impossible"
        elif not bars_to_add:
            answer = "none"
        else:
            answer = _format_bars(bars_to_add)

        return Entry(
            metadata={
                "joints": {str(j): (int(x), int(y)) for j, (x, y) in coords.items()},
                "grounded": sorted(int(g) for g in grounded),
                "current_bars": sorted((int(i), int(j)) for (i, j) in current_bars),
                "pool": sorted((int(i), int(j)) for (i, j) in pool),
                "pivot": int(pivot),
                "anchor_a": int(anchor_a),
                "rigid_target": bool(rigid_target),
                "added_bars": sorted((int(i), int(j)) for (i, j) in bars_to_add),
                "cost": int(cost),
                "unreachable": bool(unreachable),
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        joints = metadata["joints"]
        lines = []
        lines.append("A pin-jointed truss in the plane has joints (index: x,y):")
        jline = ", ".join(f"{i}:({x},{y})" for i, (x, y) in sorted(
            joints.items(), key=lambda kv: int(kv[0])))
        lines.append(jline + ".")
        lines.append(f"Joints {', '.join(str(g) for g in metadata['grounded'])} are "
                     f"anchored to the ground (their velocity is fixed to zero).")
        cur = metadata["current_bars"]
        if cur:
            lines.append("The bars already present are: "
                         + ", ".join(f"{i}-{j}" for (i, j) in sorted(cur)) + ".")
        else:
            lines.append("No bars are present initially.")
        if metadata["pool"]:
            pline = ", ".join(
                f"{i}-{j}(cost={_cost(metadata['joints'], (i, j))})"
                for (i, j) in sorted(metadata["pool"]))
            lines.append("You may add any of these permitted bars (cost = squared "
                         f"bar length, given in parentheses): {pline}.")
        else:
            lines.append("No bars may be added.")
        if metadata["rigid_target"]:
            lines.append("The completed truss must be infinitesimally rigid: the only "
                         "infinitesimal motion of its free joints is the zero motion "
                         "(no remaining freedom).")
        else:
            p = str(metadata["pivot"])
            a = str(metadata["anchor_a"])
            lines.append(f"The completed truss must have exactly one infinitesimal "
                         f"freedom: joint {p} may rotate about fixed joint {a}, and no "
                         "other joint may move (no other freedom).")
        lines.append(
            "With the smallest possible total cost, give the bar(s) to add so the "
            "completed truss has precisely that motion space. If it is impossible, "
            "answer 'impossible'. If the current truss already realizes it, answer "
            "'none'. Otherwise answer the added bars as a comma-separated list of "
            "'i-j' pairs sorted increasingly (fewest bars first on cost ties, then "
            "lexicographic), e.g. '1-4,2-5'.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry.answer
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip()
        return 1.0 if a == gold else 0.0


def _cost(joints, bar):
    (x1, y1) = joints[str(bar[0])]
    (x2, y2) = joints[str(bar[1])]
    return (x1 - x2) ** 2 + (y1 - y2) ** 2


def _min_brace_set(current_bars, pool, joint_ids, coords, grounded, k_target,
                   pivot, rigid_target):
    """Exhaustively find the min-cost subset of `pool` that realizes k_target.

    Returns (bars_to_add, cost, unreachable). Tie-break: fewest bars then
    lexicographic bar order (by canonical sorted enumeration). If no subset
    realizes the target, returns ([], 0, True).
    """
    n = len(pool)
    # Enumerate subsets by bitmap; filter to candidate-bar sets.
    pool_costs = {bar: (coords[bar[0]][0] - coords[bar[1]][0]) ** 2
                  + (coords[bar[0]][1] - coords[bar[1]][1]) ** 2 for bar in pool}
    base_distinct = set(current_bars)
    best = None
    for mask in range(1 << n):
        added = [pool[k] for k in range(n) if (mask >> k) & 1]
        bars = sorted(base_distinct | set(added))
        if _motion_dim_target_ok(bars, joint_ids, coords, grounded, k_target):
            cost = sum(pool_costs[b] for b in added)
            if best is None or cost < best[0] or (
                    cost == best[0] and (len(added) < len(best[1])
                                         or (len(added) == len(best[1])
                                             and sorted(added) < sorted(best[1])))):
                best = (cost, sorted(added))
    if best is None:
        return ([], 0, True)
    return (best[1], best[0], False)
