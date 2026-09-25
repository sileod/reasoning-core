import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class KnockoutConfig(Config):
    depth: int = 1
    groups: int = 2

    def apply_difficulty(self, level):
        self.depth = 1 + (level // 2)
        self.groups = 2 + (level // 2)


def _premultiply(rgba):
    r, g, b, a = rgba
    return [r * a, g * a, b * a, a]


def _over(src, dst):
    """Source-over composite in premultiplied space. src/dst = [R,G,B,A],
    returns the premultiplied result [R*A,G*A,B*A,A]."""
    sA = src[3]
    dA = dst[3]
    oA = sA + dA * (1.0 - sA)
    if oA <= 1e-9:
        return [0.0, 0.0, 0.0, 0.0]
    om = lambda i: (src[i] + dst[i] * (1.0 - sA))
    return [om(0), om(1), om(2), oA]


EMPTY = [0.0, 0.0, 0.0, 0.0]


def _node_over(acc_pm, acc_cov, node_pm, node_cov):
    """Return (pm, cov) after compositing a node over the accumulated result."""
    out_pm = _over(node_pm, acc_pm)
    out_cov = node_cov + acc_cov * (1.0 - node_cov)
    return out_pm, out_cov


def sample_color():
    return [round(random.uniform(0.0, 1.0), 3) for _ in range(3)]


def _build_leaf(index, depth):
    alpha = round(random.uniform(0.15, 1.0), 3)
    color = sample_color()
    mask = 1 if random.random() < 0.6 else 0
    return {
        'kind': 'leaf',
        'alpha': alpha,
        'color': color,
        'mask': mask,
        'name': f'g{index}',
    }


def _build_internal(index, depth):
    children = [_build_node(index * 10 + i, depth - 1) for i in range(2)]
    alpha = round(random.uniform(0.3, 1.0), 3)
    isolated = bool(random.getrandbits(1))
    knockout = bool(random.getrandbits(1))
    return {
        'kind': 'group',
        'children': children,
        'group_alpha': alpha,
        'isolated': isolated,
        'knockout': knockout,
        'name': f'g{index}',
    }


def _build_node(index, depth):
    if depth <= 0:
        return _build_leaf(index, depth)
    return _build_internal(index, depth)


def build_groups(config):
    return [_build_node(gi * 100 + 1, config.depth - 1) for gi in range(config.groups)]


def _resolve_group(group, base_pm, base_cov):
    """Resolve a group node against a base (pm, cov) backdrop.
    Returns (pm_out, cov_out)."""
    if group['kind'] == 'leaf':
        m = float(group['mask'])
        alpha = group['alpha'] * m
        node_pm = _premultiply((group['color'][0], group['color'][1],
                                group['color'][2], alpha))
        return _node_over(base_pm, base_cov, node_pm, m)

    children = group['children']
    ga = group['group_alpha']
    isolated = group['isolated']
    knockout = group['knockout']

    if isolated:
        group_base_pm = list(EMPTY)
        group_base_cov = 0.0
    else:
        group_base_pm = list(base_pm)
        group_base_cov = base_cov

    acc_pm = list(group_base_pm)
    acc_cov = group_base_cov
    for ch in children:
        ch_pm, ch_cov = _resolve_group(ch, group_base_pm, group_base_cov)
        if knockout:
            # Children paint over the group base, not over each other: the
            # latest child is what remains; coverage is 1 if any child paints.
            if ch_cov > 1e-9:
                acc_pm = list(ch_pm)
                acc_cov = max(acc_cov, ch_cov)
        else:
            acc_pm, acc_cov = _node_over(acc_pm, acc_cov, ch_pm, ch_cov)

    if isolated:
        # group opacity scales the flattened colour, then over the real base
        scaled_pm = [x * ga for x in acc_pm]
        return _node_over(base_pm, base_cov, scaled_pm, acc_cov)
    else:
        acc_pm = [x * ga for x in acc_pm]
        return acc_pm, acc_cov


def render_groups(groups):
    base_pm = _premultiply((0.0, 0.0, 0.0, 1.0))
    base_cov = 1.0
    acc_pm = list(base_pm)
    acc_cov = base_cov
    for g in groups:
        g_pm, g_cov = _resolve_group(g, list(EMPTY), 0.0)
        acc_pm, acc_cov = _node_over(acc_pm, acc_cov, g_pm, g_cov)
    a = acc_pm[3]
    if a <= 1e-9:
        r = g = b = 0.0
    else:
        r = acc_pm[0] / a
        g = acc_pm[1] / a
        b = acc_pm[2] / a
    return (round(r, 3), round(g, 3), round(b, 3), round(a, 3), round(acc_cov, 3))


def _group_desc(group, indent=0):
    pad = '  ' * indent
    if group['kind'] == 'leaf':
        return (f"{pad}{group['name']}: leaf alpha={group['alpha']} "
                f"color={tuple(group['color'])} mask={group['mask']}")
    lines = [f"{pad}{group['name']}: group alpha={group['group_alpha']} "
             f"isolated={group['isolated']} knockout={group['knockout']}"]
    for ch in group['children']:
        lines.append(_group_desc(ch, indent + 1))
    return '\n'.join(lines)


class HierarchicalKnockoutCompositing(Task):
    summary = ("Composite nested paint groups with opacity, masks, isolation, "
               "and knockout rules; distinguish inherited from local backdrops "
               "and return the resulting RGBA color and coverage at a queried "
               "point using per-group binary inclusion masks.")
    config_cls = KnockoutConfig
    design_choice = ("Represent each paint group as a fixed-size RGBA+coverage "
                     "tuple, and ask for the exact final color and coverage at "
                     "a single point, with masks expressed as per-group binary "
                     "inclusion arrays.")

    def generate_entry(self):
        groups = build_groups(self.config)
        final = render_groups(groups)
        group_desc = '\n'.join(_group_desc(g) for g in groups)
        metadata = {
            'groups': group_desc,
            'n_groups': self.config.groups,
            'depth': self.config.depth,
        }
        r, g, b, a, cov = final
        assert 0.0 <= a <= 1.0 + 1e-9, final
        assert 0.0 <= cov <= 1.0 + 1e-9, final
        assert 0.0 <= r <= 1.0 + 1e-9, final
        assert 0.0 <= g <= 1.0 + 1e-9, final
        assert 0.0 <= b <= 1.0 + 1e-9, final
        answer = f"{r},{g},{b},{a},{cov}"
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return (
            "Each paint group below has a colour, an opacity, a binary "
            "inclusion mask (1 if the point lies inside it, 0 if it is "
            "excluded), and optional isolation and knockout rules. Children "
            "are composited source-over onto the backdrop of their group; an "
            "isolated group starts its children over a transparent backdrop "
            "and only then blends onto the inherited one, while a "
            "non-isolated group's children keep compositing onto the "
            "inherited backdrop; a knockout group paints each child onto "
            "the group's own base rather than onto its siblings, so the "
            "latest painted child remains and coverage is the maximum of "
            "its children. Coverage is the fraction of the point painted, "
            "0..1.\n"
            f"{metadata['groups']}\n"
            "These groups are composited in order over an opaque black "
            "background. Report the final colour as R,G,B (0..1), the alpha "
            "(0..1) and the coverage (0..1) at the point, as "
            "`R,G,B,A,Coverage`. The answer is one tuple of five numbers."
        )

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        try:
            parts = [float(x.strip()) for x in answer.split(',')]
        except Exception:
            return 0.0
        if len(parts) != 5:
            return 0.0
        gold = [float(x) for x in entry.answer.split(',')]
        for a, b in zip(parts, gold):
            if abs(a - b) > 1e-4:
                return 0.0
        return 1.0


TASK_META = {'parent_source_id': None,
 'idea': 'hierarchical_knockout_compositing (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_latent_representation_r4/hierarchical_knockout_compositing',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
