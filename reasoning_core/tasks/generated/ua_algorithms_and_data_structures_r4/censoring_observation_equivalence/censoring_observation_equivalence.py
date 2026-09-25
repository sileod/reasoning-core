import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'censoring_observation_equivalence (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_algorithms_and_data_structures_r4/censoring_observation_equivalence',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1259343118,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _satisfies_obs(hist, o):
    """hist is a tuple of length n (time 1..n); o is an observation dict."""
    a, b = o['a'], o['b']
    sl = hist[a - 1:b]
    typ = o['type']
    if typ == 'const':
        return all(x == o['v'] for x in sl)
    if typ == 'range':
        return all(o['lo'] <= x <= o['hi'] for x in sl)
    if typ == 'ge':
        return all(x >= o['lo'] for x in sl)
    if typ == 'le':
        return all(x <= o['hi'] for x in sl)
    if typ == 'mx':
        return max(sl) == o['M']
    if typ == 'mn':
        return min(sl) == o['m']
    raise ValueError(typ)


def _satisfying_set(report, length, maxval):
    out = set()
    for hist in itertools.product(range(maxval + 1), repeat=length):
        if all(_satisfies_obs(hist, o) for o in report):
            out.add(hist)
    return frozenset(out)


def _render_obs(o):
    if o['type'] == 'const':
        if o['a'] == o['b']:
            return f"At time {o['a']} the reading was exactly {o['v']}."
        return (f"From time {o['a']} to time {o['b']} the reading was exactly "
                f"{o['v']}.")
    if o['type'] == 'range':
        if o['a'] == o['b']:
            return (f"At time {o['a']} the reading was between {o['lo']} and "
                    f"{o['hi']}.")
        return (f"From time {o['a']} to time {o['b']} the reading stayed within "
                f"{o['lo']} and {o['hi']}.")
    if o['type'] == 'ge':
        if o['a'] == o['b']:
            return f"At time {o['a']} the reading was at least {o['lo']}."
        return (f"From time {o['a']} to time {o['b']} the reading never fell "
                f"below {o['lo']}.")
    if o['type'] == 'le':
        if o['a'] == o['b']:
            return f"At time {o['a']} the reading was at most {o['hi']}."
        return (f"From time {o['a']} to time {o['b']} the reading never exceeded "
                f"{o['hi']}.")
    if o['type'] == 'mx':
        if o['a'] == o['b']:
            return f"The maximum reading at time {o['a']} was {o['M']}."
        return (f"The maximum reading between time {o['a']} and time {o['b']} "
                f"was {o['M']}.")
    if o['type'] == 'mn':
        if o['a'] == o['b']:
            return f"The minimum reading at time {o['a']} was {o['m']}."
        return (f"The minimum reading between time {o['a']} and time {o['b']} "
                f"was {o['m']}.")
    raise ValueError(o['type'])


@dataclass
class CensoringObsEquivConfig(Config):
    length: int = 4
    maxval: int = 4
    blocks: int = 2

    def apply_difficulty(self, level):
        self.length = 4 + (1 if level >= 3 else 0)
        self.maxval = min(4 + level, 8)
        self.blocks = min(2 + level // 2, self.length)


class CensoringObservationEquivalence(Task):
    summary = ("Compare pairs of reports over an integer time-series history using exact "
               "values, two- and one-sided censoring bounds, and interval maxima/minima; "
               "recover the compatible latent histories and decide whether two differently "
               "structured reports convey identical evidence (balanced YES/NO).")
    config_cls = CensoringObsEquivConfig
    task_version = 2

    def _build_report_a(self, length, maxval, blocks):
        n = length
        while True:
            if blocks > 1:
                cuts = sorted(random.sample(range(1, n), blocks - 1))
            else:
                cuts = []
            bounds = []
            prev = 1
            for c in cuts + [n]:
                bounds.append((prev, c))
                prev = c + 1
            f = tuple(random.randint(0, maxval) for _ in range(n))
            obs_a = []
            pool = ['const', 'range', 'ge', 'le', 'range', 'ge', 'le', 'mx', 'mn']
            for idx, (a, b) in enumerate(bounds):
                block = f[a - 1:b]
                mn = min(block)
                mx = max(block)
                if idx == 0:
                    typ = random.choice(['const', 'range'])
                else:
                    typ = random.choice(pool)
                if typ == 'const':
                    if mn == mx:
                        obs_a.append({'type': 'const', 'a': a, 'b': b, 'v': mn})
                    else:
                        obs_a.append({'type': 'range', 'a': a, 'b': b,
                                      'lo': mn, 'hi': mx})
                elif typ == 'range':
                    obs_a.append({'type': 'range', 'a': a, 'b': b,
                                  'lo': mn, 'hi': mx})
                elif typ == 'ge':
                    obs_a.append({'type': 'ge', 'a': a, 'b': b,
                                  'lo': random.randint(0, mn)})
                elif typ == 'le':
                    obs_a.append({'type': 'le', 'a': a, 'b': b,
                                  'hi': random.randint(mx, maxval)})
                elif typ == 'mx':
                    obs_a.append({'type': 'mx', 'a': a, 'b': b, 'M': mx})
                elif typ == 'mn':
                    obs_a.append({'type': 'mn', 'a': a, 'b': b, 'm': mn})
            o0 = obs_a[0]
            if o0['type'] in ('const', 'range'):
                return bounds, obs_a
        return bounds, obs_a

    def generate_entry(self):
        length = self.config.length
        maxval = self.config.maxval
        blocks = self.config.blocks
        n = length

        bounds, obs_a = self._build_report_a(length, maxval, blocks)
        a0, b0 = bounds[0]
        o0 = obs_a[0]

        same = random.random() < 0.5
        if same:
            if o0['type'] == 'const':
                v = o0['v']
                opts = ['T1', 'T2']
                if b0 - a0 >= 1:
                    opts.append('T3s')
                choice = random.choice(opts)
                if choice == 'T1':
                    b0_obs = [{'type': 'mx', 'a': a0, 'b': b0, 'M': v},
                              {'type': 'mn', 'a': a0, 'b': b0, 'm': v}]
                elif choice == 'T2':
                    b0_obs = [{'type': 'range', 'a': a0, 'b': b0, 'lo': v, 'hi': v}]
                else:
                    c = random.randint(a0, b0 - 1)
                    b0_obs = [{'type': 'const', 'a': a0, 'b': c, 'v': v},
                              {'type': 'const', 'a': c + 1, 'b': b0, 'v': v}]
            else:
                lo, hi = o0['lo'], o0['hi']
                if b0 - a0 >= 1 and random.random() < 0.5:
                    c = random.randint(a0, b0 - 1)
                    b0_obs = [{'type': 'range', 'a': a0, 'b': c, 'lo': lo, 'hi': hi},
                              {'type': 'range', 'a': c + 1, 'b': b0, 'lo': lo,
                               'hi': hi}]
                else:
                    b0_obs = [{'type': 'ge', 'a': a0, 'b': b0, 'lo': lo},
                              {'type': 'le', 'a': a0, 'b': b0, 'hi': hi}]
        else:
            if o0['type'] == 'const':
                v = o0['v']
                l = random.randint(0, v)
                h = random.randint(v, maxval)
                if (l, h) == (v, v):
                    if v < maxval:
                        h = v + 1
                    else:
                        l = v - 1
                b0_obs = [{'type': 'range', 'a': a0, 'b': b0, 'lo': l, 'hi': h}]
            else:
                lo, hi = o0['lo'], o0['hi']
                if lo == 0 and hi == maxval:
                    l = random.randint(0, maxval - 1)
                    h = random.randint(l, maxval)
                else:
                    l = max(0, lo - 1)
                    h = min(maxval, hi + 1)
                b0_obs = [{'type': 'ge', 'a': a0, 'b': b0, 'lo': l},
                          {'type': 'le', 'a': a0, 'b': b0, 'hi': h}]

        obs_b = b0_obs + obs_a[1:]

        sa = _satisfying_set(obs_a, length, maxval)
        sb = _satisfying_set(obs_b, length, maxval)
        gold = 'YES' if sa == sb else 'NO'
        assert sa and sb
        assert (sa == sb) == (gold == 'YES')

        metadata = {
            'n': length,
            'maxval': maxval,
            'A': obs_a,
            'B': obs_b,
            'gold': gold,
        }
        return Entry(metadata=metadata, answer=gold)

    def render_prompt(self, metadata):
        lines_a = "\n".join(f"- {_render_obs(o)}" for o in metadata['A'])
        lines_b = "\n".join(f"- {_render_obs(o)}" for o in metadata['B'])
        return (
            f"A sensor logs one reading per time step from time 1 to time "
            f"{metadata['n']}; every reading is an integer from 0 to "
            f"{metadata['maxval']}. A hidden history is one assignment of those "
            f"readings over time.\n\n"
            f"Report A:\n{lines_a}\n\n"
            f"Report B:\n{lines_b}\n\n"
            f"Do reports A and B carry identical evidence -- do they permit exactly "
            f"the same set of reading histories? Reply by writing only YES or NO as "
            f"the answer."
        )

    def score_answer(self, answer, entry):
        gold = entry.answer
        a = str(answer).strip().upper()
        g = str(gold).strip().upper()
        return 1.0 if a == g else 0.0
