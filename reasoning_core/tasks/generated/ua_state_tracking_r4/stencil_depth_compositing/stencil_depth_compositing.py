from dataclasses import dataclass
import random

from reasoning_core.template import Task, Entry, Config, edict

TASK_META = {'parent_source_id': None,
 'idea': 'stencil_depth_compositing (variant 1 of 3)',
 'hypothesis': 'P012',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_state_tracking_r4/stencil_depth_compositing',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1277236794,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

_CMP_NAMES = ['NEVER', 'LESS', 'LEQUAL', 'GREATER', 'GEQUAL', 'EQUAL', 'NOTEQUAL', 'ALWAYS']
_CMP = {
    'NEVER': lambda a, b: False,
    'LESS': lambda a, b: a < b,
    'LEQUAL': lambda a, b: a <= b,
    'GREATER': lambda a, b: a > b,
    'GEQUAL': lambda a, b: a >= b,
    'EQUAL': lambda a, b: a == b,
    'NOTEQUAL': lambda a, b: a != b,
    'ALWAYS': lambda a, b: True,
}
_STENCIL_OPS = ['KEEP', 'ZERO', 'REPLACE', 'INCR', 'DECR', 'INCR_WRAP', 'DECR_WRAP', 'INVERT']
_BLEND_FACTORS = ['ZERO', 'ONE', 'SRC_COLOR', 'ONE_MINUS_SRC_COLOR', 'DST_COLOR', 'ONE_MINUS_DST_COLOR']


def _clamp255(v):
    if v < 0:
        return 0
    if v > 255:
        return 255
    return v


def _factor(f, src_c, dst_c):
    if f == 'ZERO':
        return 0
    if f == 'ONE':
        return 1
    if f == 'SRC_COLOR':
        return src_c
    if f == 'ONE_MINUS_SRC_COLOR':
        return 255 - src_c
    if f == 'DST_COLOR':
        return dst_c
    if f == 'ONE_MINUS_DST_COLOR':
        return 255 - dst_c
    return 1


def _stencil_apply(s, op, ref):
    if op == 'ZERO':
        return 0
    if op == 'REPLACE':
        return ref
    if op == 'INCR':
        return min(255, s + 1)
    if op == 'DECR':
        return max(0, s - 1)
    if op == 'INCR_WRAP':
        return (s + 1) & 255
    if op == 'DECR_WRAP':
        return (s - 1) & 255
    if op == 'INVERT':
        return 255 - s
    return s


def _simulate(clear, ops, queries):
    results = []
    for (qx, qy) in queries:
        color = list(clear['color'])
        depth = clear['depth']
        stencil = clear['stencil']
        for op in ops:
            x0, y0, x1, y1 = op['region']
            if not (x0 <= qx <= x1 and y0 <= qy <= y1):
                continue
            cmp, ref, mask = op['stencil_func']
            if not _CMP[cmp]((stencil & mask), (ref & mask)):
                stencil = _stencil_apply(stencil, op['stencil_fail'], ref)
                continue
            if not _CMP[op['depth_func']](op['depth'], depth):
                stencil = _stencil_apply(stencil, op['stencil_depth_fail'], ref)
                continue
            if op['depth_write']:
                depth = op['depth']
            stencil = _stencil_apply(stencil, op['stencil_pass'], ref)
            src = op['color']
            if op['blend'] is None:
                result = list(src)
            else:
                fs, fd = op['blend']
                result = [
                    _clamp255(_factor(fs, src[i], color[i]) * src[i]
                              + _factor(fd, src[i], color[i]) * color[i])
                    for i in range(4)
                ]
            cm = op['color_mask']
            color = [result[i] if cm[i] else color[i] for i in range(4)]
        results.append((color, depth, stencil))
    return results


def _fmt_cmp(cmp, ref, mask):
    return f"{cmp} ref={ref} mask={mask}"


def _fmt_op(op):
    x0, y0, x1, y1 = op['region']
    region = f"rect ({x0},{y0})-({x1},{y1})"
    sfunc = _fmt_cmp(*op['stencil_func'])
    sops = f"fail={op['stencil_fail']} depthfail={op['stencil_depth_fail']} pass={op['stencil_pass']}"
    r, g, b, a = op['color']
    cm = op['color_mask']
    maskstr = 'RGB' if cm == [True, True, True, True] else ('color_mask=' + ''.join('1' if m else '0' for m in cm))
    if op['blend'] is None:
        blend = "overwrite"
    else:
        blend = f"blend src={op['blend'][0]} dst={op['blend'][1]}"
    depth_write = 'write' if op['depth_write'] else 'no-write'
    return (f"{region}; stencil {sfunc} [{sops}]; depth {op['depth']} {op['depth_func']} "
            f"{depth_write}; color ({r},{g},{b},{a}) {maskstr} {blend}")


@dataclass
class StencilDepthConfig(Config):
    grid_n: int = 5
    num_fragments: int = 2
    num_queries: int = 2

    def apply_difficulty(self, level):
        self.grid_n = 5 + level
        self.num_fragments = 2 + level
        self.num_queries = 2 + level // 2


class StencilDepthCompositing(Task):
    summary = ("Execute fragment streams with stencil comparisons, depth tests, masked writes, "
               "and integer blending; track distinct fail and pass updates and return queried "
               "pixels' color, depth, or stencil state.")
    config_cls = StencilDepthConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        n = cfg.grid_n
        while True:
            clear = {
                'color': [random.randint(0, 255) for _ in range(4)],
                'depth': random.randint(0, 1023),
                'stencil': random.randint(0, 255),
            }
            ops = []
            for _ in range(cfg.num_fragments):
                x0 = random.randint(0, n - 1)
                x1 = random.randint(x0, n - 1)
                y0 = random.randint(0, n - 1)
                y1 = random.randint(y0, n - 1)
                stencil_func = [
                    random.choice(_CMP_NAMES),
                    random.randint(0, 255),
                    random.choice([0, 1, 3, 7, 15, 31, 127, 255]),
                ]
                cm = [random.random() < 0.7 for _ in range(4)]
                if not any(cm):
                    cm[random.randrange(4)] = True
                blend = None
                if random.random() < 0.5:
                    blend = [random.choice(_BLEND_FACTORS), random.choice(_BLEND_FACTORS)]
                ops.append({
                    'region': [x0, y0, x1, y1],
                    'stencil_func': stencil_func,
                    'stencil_fail': random.choice(_STENCIL_OPS),
                    'stencil_depth_fail': random.choice(_STENCIL_OPS),
                    'stencil_pass': random.choice(_STENCIL_OPS),
                    'depth': random.randint(0, 1023),
                    'depth_func': random.choice(_CMP_NAMES),
                    'depth_write': random.random() < 0.7,
                    'color': [random.randint(0, 255) for _ in range(4)],
                    'color_mask': cm,
                    'blend': blend,
                })
            queries = random.sample([(x, y) for y in range(n) for x in range(n)], cfg.num_queries)
            results = _simulate(clear, ops, queries)
            ok = True
            for (color, depth, stencil) in results:
                if not all(0 <= c <= 255 for c in color):
                    ok = False
                if not (0 <= depth <= 1023):
                    ok = False
                if not (0 <= stencil <= 255):
                    ok = False
            if not ok:
                continue
            answer = ';'.join(
                f"{color[0]},{color[1]},{color[2]},{color[3]},{depth},{stencil}"
                for (color, depth, stencil) in results
            )
            metadata = edict({
                'n': n,
                'clear': clear,
                'ops': ops,
                'queries': [list(q) for q in queries],
            })
            metadata.payload = {
                'clear': f"color={clear['color']} depth={clear['depth']} stencil={clear['stencil']}",
                'fragments': '\n'.join(f"F{i}: {_fmt_op(op)}" for i, op in enumerate(ops)),
                'queries': ' '.join(f"({qx},{qy})" for (qx, qy) in queries),
            }
            return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return (
            "Simulate a graphics compositing pipeline over an "
            f"{metadata['n']}x{metadata['n']} framebuffer of pixels. Each pixel carries a color "
            "(r,g,b,a channels, each 0-255), a depth (integer 0-1023), and a stencil value "
            "(integer 0-255). The buffer starts cleared to a single color, depth, and stencil.\n\n"
            "A sequence of fragments is then applied in order. A fragment covers a rectangular "
            "region of pixels, coordinates inclusive. For each pixel the fragment covers, it "
            "applies in this order:\n"
            "1. Stencil test: compare (pixel_stencil & mask) with (ref & mask) using its "
            "comparison. If the test fails, apply the stencil-fail operation to the pixel "
            "stencil and the fragment has no further effect on the pixel.\n"
            "2. Depth test: compare the fragment depth with the pixel's current depth using its "
            "comparison. If the test fails, apply the stencil depth-fail operation to the pixel "
            "stencil and the fragment has no further effect on the pixel.\n"
            "3. If depth write is on, set the pixel depth to the fragment depth.\n"
            "4. Apply the stencil pass operation to the pixel stencil.\n"
            "5. Color: either overwrite the pixel color with the fragment color, or blend it. "
            "Blending computes, per channel, result = clamp(fragment_channel * src_factor + "
            "pixel_channel * dst_factor) to 0-255, where SRC_COLOR means the fragment's same "
            "channel, DST_COLOR the pixel's same channel, ONE_MINUS_* uses 255 minus that value, "
            "and ZERO/ONE are constants 0/1. Then apply the color write mask: only masked "
            "channels are replaced, others keep their previous value.\n\n"
            "Comparisons (stencil and depth): NEVER (never passes), LESS, LEQUAL, GREATER, GEQUAL, "
            "EQUAL, NOTEQUAL, ALWAYS.\n"
            "Stencil operations: KEEP, ZERO (set to 0), REPLACE (set to ref), INCR (add 1, "
            "saturating at 255), DECR (subtract 1, saturating at 0), INCR_WRAP (add 1, wrapping "
            "255 to 0), DECR_WRAP (subtract 1, wrapping 0 to 255), INVERT (255 minus value).\n\n"
            "Only the queried pixels below are scored.\n\n"
            "Clear:\n"
            f"{metadata.payload['clear']}\n\n"
            "Fragments in order:\n"
            f"{metadata.payload['fragments']}\n\n"
            "Queried pixels (x,y):\n"
            f"{metadata.payload['queries']}\n\n"
            "For each queried pixel in the order listed above, give its final color channels, "
            "depth, and stencil as r,g,b,a,d,s with no spaces, and join the pixels with a "
            "semicolon and no spaces. Example for two pixels: "
            "10,20,30,255,512,7;40,50,60,255,0,3\n\n"
            "Answer:"
        )

    def score_answer(self, answer, entry):
        return 1.0 if str(answer).strip() == entry.answer else 0.0
