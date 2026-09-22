import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'query_cardinality_estimation (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_language_implementation_r4/query_cardinality_estimation',
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


DOMAIN = 100
JOIN_DOMAIN = 100


def _weights(nbins):
    parts = [1] * nbins
    extra = DOMAIN - nbins
    for _ in range(extra):
        parts[random.randrange(nbins)] += 1
    return parts


def sel_pct(bins, lo, hi):
    covered = 0.0
    for blo, bhi, w in bins:
        s = max(blo, lo)
        e = min(bhi, hi)
        if e > s:
            covered += (e - s) * w / (bhi - blo)
    return min(covered, 100.0)


@dataclass
class QCEConfig(Config):
    ntables: int = 2
    depth: int = 1

    def apply_difficulty(self, level):
        self.ntables = 2 + (level // 2)
        self.depth = 1 + (level // 3)


class QueryCardinalityEstimation(Task):
    summary = "Propagate table sizes through histogram-guided equality and range predicates, conjunctions, disjunctions, and joins with declared independence or containment assumptions; report the estimated cardinality at queried nodes."
    design_choice = "Represent histograms as fixed-width bins with uniform density; predicates reference explicit bin edges, and estimates are sums of bin overlaps."

    config_cls = QCEConfig

    def generate_entry(self):
        while True:
            try:
                tables, hists = self._data()
                node = self._root(tables, hists)
                if self._count_sels(node) < 1:
                    raise AssertionError
                ans = self._card(node, tables, hists, {})
                assert type(ans) is int and ans >= 0, ans
                metadata = {
                    'tables': {k: v for k, v in sorted(tables.items())},
                    'hists': {k: [list(b) for b in hists[k]] for k in sorted(hists)},
                    'tree': self._serialize(node, tables, hists),
                    'answer': ans,
                }
                return Entry(metadata=metadata, answer=str(ans))
            except (AssertionError, ZeroDivisionError, RecursionError, KeyError):
                continue

    def _data(self):
        tables = {}
        for i in range(self.config.ntables):
            tables[f"T{i}"] = random.randint(40, 400)
        hists = {}
        for i in range(self.config.ntables):
            t = f"T{i}"
            nbins = random.randint(4, 6)
            width = DOMAIN // nbins
            w = _weights(nbins)
            bins = [(j * width, (j + 1) * width, w[j]) for j in range(nbins)]
            hists[t] = bins
        return tables, hists

    def _single(self, tables, depth, table, used):
        r = random.random()
        if r < 0.45 or depth <= 0:
            lo = random.randint(0, DOMAIN - 1)
            hi = random.randint(lo + 1, DOMAIN)
            return {'k': 'sel', 'T': table, 'lo': lo, 'hi': hi}
        if r < 0.9:
            c1 = self._single(tables, depth - 1, table, used)
            c2 = self._single(tables, depth - 1, table, used)
            kind = 'and' if random.random() < 0.6 else 'or'
            return {'k': kind, 'c1': c1, 'c2': c2}
        return {'k': 'base', 'T': table}

    def _root(self, tables, hists):
        all_t = sorted(tables.keys())
        r = random.random()
        depth = self.config.depth
        single_t = random.choice(all_t)
        if r < 0.75 or len(all_t) < 2:
            root = self._single(tables, depth, single_t, set())
            if isinstance(root.get('c1'), dict) and root['k'] in ('and', 'or') and self._count_sels(root) < 1:
                root = self._single(tables, depth, single_t, set())
            return root
        ta, tb = random.sample(all_t, 2)
        mode = 'independence' if random.random() < 0.6 else 'containment'
        ca = self._single(tables, depth, ta, set())
        cb = self._single(tables, depth, tb, set())
        return {'k': 'join', 'mode': mode, 'c1': ca, 'c2': cb}

    def _count_sels(self, node):
        if node is None:
            return 0
        if node['k'] == 'sel':
            return 1
        if node['k'] == 'base':
            return 0
        return self._count_sels(node.get('c1')) + self._count_sels(node.get('c2'))

    def _card(self, node, tables, hists, memo):
        k = node['k']
        if k == 'sel':
            pct = sel_pct(hists[node['T']], node['lo'], node['hi'])
            return int(round(tables[node['T']] * pct / 100.0))
        if k == 'base':
            return tables[node['T']]
        if k in ('and', 'or'):
            t = node['c1']['T']
            n = tables[t]
            ca = self._card(node['c1'], tables, hists, memo)
            cb = self._card(node['c2'], tables, hists, memo)
            sa = (ca / n) if n else 0.0
            sb = (cb / n) if n else 0.0
            if k == 'and':
                sel = sa * sb
            else:
                sel = min(1.0, sa + sb - sa * sb)
            return int(round(n * sel))
        if k == 'join':
            ca = self._card(node['c1'], tables, hists, memo)
            cb = self._card(node['c2'], tables, hists, memo)
            if node['mode'] == 'independence':
                return int(round(ca * cb / JOIN_DOMAIN))
            return min(ca, cb)
        raise ValueError(k)

    def _serialize(self, node, tables, hists):
        k = node['k']
        if k == 'sel':
            return {'k': 'sel', 'T': node['T'], 'lo': node['lo'], 'hi': node['hi']}
        if k == 'base':
            return {'k': 'base', 'T': node['T']}
        d = {'k': k}
        if k in ('and', 'or'):
            d['c1'] = self._serialize(node['c1'], tables, hists)
            d['c2'] = self._serialize(node['c2'], tables, hists)
        else:
            d['mode'] = node['mode']
            d['c1'] = self._serialize(node['c1'], tables, hists)
            d['c2'] = self._serialize(node['c2'], tables, hists)
        return d

    def render_prompt(self, metadata):
        lines = ["Tables with row counts:"]
        for t, n in sorted(metadata['tables'].items()):
            lines.append(f"{t}: {n} rows")
        lines.append("")
        lines.append("Column histograms (each bin [lo, hi) holds weight% of that table's rows, uniform within the bin):")
        for t, bins in sorted(metadata['hists'].items()):
            parts = ", ".join(f"[{s},{e}) {w}%" for s, e, w in bins)
            lines.append(f"{t}: {parts}")
        lines.append("")
        lines.append("Estimate the number of result rows of the following expression:")
        lines.append(self._render(metadata['tree']))
        lines.append(f"An independence join computes left*right/{JOIN_DOMAIN}; a containment join takes the smaller side.")
        lines.append("Report the estimated cardinality as one non-negative integer.")
        return "\n".join(lines)

    def _render(self, node):
        k = node['k']
        if k == 'base':
            return node['T']
        if k == 'sel':
            return f"{node['T']} WHERE col IN [{node['lo']},{node['hi']})"
        if k == 'and':
            return f"( {self._render(node['c1'])} AND {self._render(node['c2'])} )"
        if k == 'or':
            return f"( {self._render(node['c1'])} OR {self._render(node['c2'])} )"
        if k == 'join':
            return f"( {self._render(node['c1'])} JOIN {self._render(node['c2'])} [{node['mode']}] )"
        raise ValueError(k)

    def score_answer(self, answer, entry):
        try:
            return 1.0 if int(str(answer).strip()) == int(entry.answer) else 0.0
        except (ValueError, TypeError):
            return 0.0
