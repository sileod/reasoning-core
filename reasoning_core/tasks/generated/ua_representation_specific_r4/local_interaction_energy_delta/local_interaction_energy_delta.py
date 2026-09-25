import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Task, Entry, Config, edict, stochastic_rounding as sround

TASK_META = {'parent_source_id': None,
 'idea': 'local_interaction_energy_delta (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_representation_specific_r4/local_interaction_energy_delta',
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


@dataclass
class LatticeConfig(Config):
    n_sites: int = 4
    n_pair: int = 3
    n_ms: int = 2
    n_edits: int = 2
    charge_max: int = 2
    cp_max: int = 4
    cd_max: int = 4

    def apply_difficulty(self, level):
        self.n_sites = sround(self.n_sites + level)
        self.n_pair = sround(self.n_pair + 2 * level)
        self.n_ms = sround(self.n_ms + level)
        self.n_edits = sround(self.n_edits + level)
        self.charge_max = sround(self.charge_max + level)
        self.cp_max = sround(self.cp_max + level)
        self.cd_max = sround(self.cd_max + level)


def _nonzero_int(maxabs):
    while True:
        v = random.randint(-maxabs, maxabs)
        if v != 0:
            return v


def _coupling(cfg, force_nonzero):
    attempts = 0
    while True:
        num = random.randint(-cfg.cp_max, cfg.cp_max)
        den = random.randint(1, cfg.cd_max)
        if num != 0 or not force_nonzero:
            return Fraction(num, den)
        attempts += 1
        if attempts > 200:
            return Fraction(1, 1)


def _energy(kind, sites, charges, coup):
    prod = 1
    for s in sites:
        prod *= charges[s]
    return coup * prod


def _parse_frac(s):
    s = s.strip()
    if '/' in s:
        a, b = s.split('/', 1)
        return Fraction(int(a.strip()), int(b.strip()))
    return Fraction(int(s), 1)


class LocalInteractionEnergyDelta(Task):
    config_cls = LatticeConfig

    summary = ("Update lattice energies after simultaneous site or interaction edits across "
               "pairwise and multisite potentials; count jointly affected terms once and return "
               "changed interaction contributions and total energy delta.")

    design_choice = ("Return the delta as a reduced fraction over a common denominator for all "
                     "edited terms, with the numerator and denominator as separate integers.")

    def _eval_all(self, site_list, pair_terms, ms_terms, charges, couplings):
        total = Fraction(0)
        per = {}
        for it in pair_terms:
            e = _energy('p', it['sites'], charges, couplings[it['id']])
            per[it['id']] = e
            total += e
        for it in ms_terms:
            e = _energy('m', it['sites'], charges, couplings[it['id']])
            per[it['id']] = e
            total += e
        return total, per

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_sites
        site_ids = list(range(n))
        charges = {s: _nonzero_int(cfg.charge_max) for s in site_ids}

        pairs_possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
        sel_pairs = random.sample(pairs_possible, min(cfg.n_pair, len(pairs_possible)))
        pair_terms = []
        for idx, (i, j) in enumerate(sel_pairs):
            cid = 'P%d' % idx
            pair_terms.append({'id': cid, 'kind': 'p', 'sites': (i, j)})

        ms_terms = []
        cidx = 0
        used_subsets = set()
        target_ms = cfg.n_ms
        attempts = 0
        while len(ms_terms) < target_ms and attempts < 300:
            attempts += 1
            k = 3 if random.random() < 0.7 else 4
            if k > n:
                continue
            subset = tuple(sorted(random.sample(site_ids, k)))
            if subset in used_subsets:
                continue
            used_subsets.add(subset)
            ms_terms.append({'id': 'M%d' % cidx, 'kind': 'm', 'sites': subset})
            cidx += 1

        pair_coupl = {}
        for it in pair_terms:
            pair_coupl[it['id']] = _coupling(cfg, True)
        ms_coupl = {}
        for it in ms_terms:
            ms_coupl[it['id']] = _coupling(cfg, True)

        old_total, old_per = self._eval_all(site_ids, pair_terms, ms_terms, charges,
                                            {**pair_coupl, **ms_coupl})

        for _att in range(60):
            new_charges = dict(charges)
            new_coupl = {**pair_coupl, **ms_coupl}

            affected = set()
            edits = []
            for _ in range(cfg.n_edits):
                kind = random.choice(['site', 'interaction'])
                if kind == 'site' or not (pair_terms or ms_terms):
                    s = random.choice(site_ids)
                    while True:
                        nc = _nonzero_int(cfg.charge_max + cfg.n_edits + 1)
                        if nc != new_charges[s]:
                            break
                    new_charges[s] = nc
                    edits.append(('site', s, nc))
                    for it in pair_terms + ms_terms:
                        if s in it['sites']:
                            affected.add(it['id'])
                else:
                    pool = pair_terms + ms_terms
                    it = random.choice(pool)
                    while True:
                        nc = _coupling(cfg, True)
                        if nc != new_coupl[it['id']]:
                            break
                    new_coupl[it['id']] = nc
                    edits.append(('interaction', it['id'], nc))
                    affected.add(it['id'])

            new_total, new_per = self._eval_all(site_ids, pair_terms, ms_terms,
                                                new_charges, new_coupl)

            delta_total = Fraction(0)
            for it in pair_terms + ms_terms:
                cid = it['id']
                if cid in affected:
                    delta_total += new_per[cid] - old_per[cid]

            consistency = new_total - old_total
            if delta_total.numerator == 0:
                continue
            num, den = delta_total.numerator, delta_total.denominator
            cnum, cden = consistency.numerator, consistency.denominator
            if (num, den) != (cnum, cden):
                continue
            if den <= 0:
                continue
            break
        else:
            raise RuntimeError("could not build a nonzero energy delta")

        site_list = [(s, charges[s]) for s in site_ids]
        payload_edits = []
        for e in edits:
            if e[0] == 'site':
                payload_edits.append(('site', e[1], e[2]))
            else:
                num_, den_ = e[2].numerator, e[2].denominator
                payload_edits.append(('interaction', e[1], num_, den_))
        payload_pairs = [{'id': it['id'], 'sites': list(it['sites']),
                          'num': pair_coupl[it['id']].numerator,
                          'den': pair_coupl[it['id']].denominator} for it in pair_terms]
        payload_ms = [{'id': it['id'], 'sites': list(it['sites']),
                       'num': ms_coupl[it['id']].numerator,
                       'den': ms_coupl[it['id']].denominator} for it in ms_terms]

        answer = "%d/%d" % (num, den)
        metadata = edict({
            'site_list': site_list,
            'pair_terms': payload_pairs,
            'ms_terms': payload_ms,
            'edits': payload_edits,
            'old_total': "%d/%d" % (old_total.numerator, old_total.denominator),
            'new_total': "%d/%d" % (new_total.numerator, new_total.denominator),
            'affected': sorted(affected),
            'num': num,
            'den': den,
        })
        metadata.payload = {
            'site_list': site_list,
            'pair_terms': payload_pairs,
            'ms_terms': payload_ms,
            'edits': payload_edits,
        }
        metadata['_answer'] = answer
        return Entry(metadata=metadata, answer=answer)

    def _render_coup(self, num, den):
        if den == 1:
            return str(num)
        return "%d/%d" % (num, den)

    def render_prompt(self, metadata):
        sites_str = ', '.join("site %d charge %d" % (s, c) for s, c in metadata.site_list)

        int_lines = []
        for it in metadata.pair_terms:
            int_lines.append("%s: pairwise potential between sites %d and %d, coupling %s" % (
                it['id'], it['sites'][0], it['sites'][1], self._render_coup(it['num'], it['den'])))
        for it in metadata.ms_terms:
            int_lines.append("%s: multisite potential over sites %s, coupling %s" % (
                it['id'], ','.join(str(x) for x in it['sites']), self._render_coup(it['num'], it['den'])))

        edit_lines = []
        for e in metadata.edits:
            if e[0] == 'site':
                edit_lines.append("change site %d charge to %d" % (e[1], e[2]))
            else:
                edit_lines.append("change coupling of interaction %s to %s" % (
                    e[1], self._render_coup(e[2], e[3])))

        body = ("A lattice is made of sites holding integer charges and a set of interaction "
                "terms. A pairwise potential between two sites contributes coupling*(c_a*c_b); "
                "a multisite potential over a set of sites contributes coupling*(product of "
                "their charges). The lattice energy is the sum of every interaction term.\n"
                "Sites: %s.\n" % sites_str)
        body += "Interaction terms:\n" + "\n".join(int_lines) + "\n"
        body += "Apply these edits simultaneously to the initial state:\n" + "\n".join(edit_lines) + "\n"
        body += ("Give the total change in lattice energy after all edits, i.e. final energy "
                 "minus initial energy, counting a term affected by more than one edit only once. "
                 "Express the result as a reduced fraction with numerator and denominator "
                 "separated by a slash (denominator positive), e.g. '7/3' or '-5/2'. If the "
                 "result is an integer, still write it as n/1.")
        return body

    def score_answer(self, answer, entry):
        try:
            got = _parse_frac(answer)
        except Exception:
            return 0.0
        gold_num = entry.metadata.num
        gold_den = entry.metadata.den
        if got == Fraction(gold_num, gold_den):
            return 1.0
        return 0.0
