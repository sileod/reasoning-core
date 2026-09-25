import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'periodic_density_equivalence (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_state_tracking_r4/periodic_density_equivalence',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

COEFFS = [-7, -5, -3, -1, 2, 4, 6, 8]
FIELD_NAMES = ("u", "v")


def _site_sum(fields, factors, n):
    """Sum of one monomial over all n sites: coeff=1, factors=(field,offset) list."""
    total = 0
    for site in range(n):
        prod = 1
        for fi, off in factors:
            prod *= fields[fi][(site + off) % n]
        total += prod
    return total


def _total(fields, monomials, n):
    return sum(c * _site_sum(fields, facs, n) for c, facs in monomials)


def _translate(mono, t):
    coeff, facs = mono
    return (coeff, [(fi, off + t) for fi, off in facs])


def _mono_text(monos):
    return " + ".join(
        f"{c}*" + "*".join(f"{FIELD_NAMES[fi]}[{off:+d}]" for fi, off in facs)
        for c, facs in monos
    )


def _fields_text(fields):
    return "\n".join(
        f"  {FIELD_NAMES[f]} = {fields[f]}" for f in range(len(fields))
    )


@dataclass
class DensityConfig(Config):
    period: int = 5
    num_monomials: int = 3
    offset_range: int = 2
    max_degree: int = 2
    trans_max: int = 2
    vmax: int = 3

    def apply_difficulty(self, level):
        self.period = 5 + level
        self.num_monomials = 3 + level
        self.offset_range = 2 + level
        self.max_degree = 1 if level < 2 else (2 if level < 4 else 3)
        self.trans_max = 1 + level
        self.vmax = 3 + level


class PeriodicDensityEquivalence(Task):
    summary = ("Polynomial local densities on periodic sequences with varied stencil widths and "
               "two fields; group translated monomials to decide equality of total energies "
               "as EQ or NEQ.")
    design_choice = ("Answer as a canonical equality string like EQ or NEQ, with instances "
                     "generated so both outcomes occur across levels.")
    task_version = 2
    config_cls = DensityConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.period
        fields = []
        for _ in range(2):
            vals = [random.randint(-cfg.vmax, cfg.vmax) for _ in range(n)]
            if not any(v != 0 for v in vals):
                vals[random.randrange(n)] = random.choice([1, 2])
            fields.append(vals)

        while True:
            mons = []
            for _ in range(cfg.num_monomials):
                coeff = random.choice(COEFFS)
                deg = random.randint(1, cfg.max_degree)
                facs = [(random.randrange(2),
                         random.randint(-cfg.offset_range, cfg.offset_range))
                        for _ in range(deg)]
                mons.append((coeff, facs))

            is_eq = random.random() < 0.5
            if is_eq:
                ta = random.randint(0, cfg.trans_max)
                tb = random.randint(0, cfg.trans_max)
                ma = [_translate(m, ta) for m in mons]
                mb = [_translate(m, tb) for m in mons]
                random.shuffle(ma)
                random.shuffle(mb)
                total_a = _total(fields, ma, n)
                total_b = _total(fields, mb, n)
                assert total_a == total_b
                label = "EQ"
            else:
                k = random.randrange(len(mons))
                c0, cfacs = mons[k]
                if _site_sum(fields, cfacs, n) == 0:
                    fd = random.randrange(2)
                    if not any(v != 0 for v in fields[fd]):
                        fd = 1 - fd
                    off = random.randint(-cfg.offset_range, cfg.offset_range)
                    cfacs = [(fd, off), (fd, off)]
                c1 = c0
                while c1 == c0:
                    c1 = random.choice(COEFFS)
                mons_b = list(mons)
                mons_b[k] = (c1, cfacs)
                ma = [_translate(m, random.randint(0, cfg.trans_max)) for m in mons]
                mb = [_translate(m, random.randint(0, cfg.trans_max)) for m in mons_b]
                random.shuffle(ma)
                random.shuffle(mb)
                total_a = _total(fields, ma, n)
                total_b = _total(fields, mb, n)
                while total_b == total_a:
                    c1 += 1
                    mons_b[k] = (c1, cfacs)
                    mb = [_translate(m, random.randint(0, cfg.trans_max)) for m in mons_b]
                    random.shuffle(mb)
                    total_b = _total(fields, mb, n)
                assert total_a != total_b
                label = "NEQ"

            mono_a = _mono_text(ma)
            mono_b = _mono_text(mb)
            if mono_a != mono_b:
                break

        metadata = {
            "n": n,
            "fields": fields,
            "mono_a": mono_a,
            "mono_b": mono_b,
            "label": label,
            "total_a": int(total_a),
            "total_b": int(total_b),
        }
        return Entry(metadata=metadata, answer=label)

    def render_prompt(self, metadata):
        n = metadata.n
        body = (
            f"On a ring of {n} sites there are two periodic integer fields:\n"
            f"{_fields_text(metadata.fields)}\n"
            f"A local energy density at a site i is a sum of monomials. Each monomial like "
            f"c*u[a]*v[b] means coefficient c times field u read at site i+a times field v "
            f"read at site i+b; a single-field monomial like c*u[a] uses only that field. "
            f"Indices wrap modulo {n}. The total energy of an expression is the sum of its "
            f"density over every site i.\n\n"
            f"Expression A has monomials:\n{metadata.mono_a}\n\n"
            f"Expression B has monomials:\n{metadata.mono_b}\n\n"
            f"Decide whether the total energy of A equals that of B. Respond with the "
            f"single token EQ or NEQ only."
        )
        return body

    def score_answer(self, answer, entry):
        a = str(answer).strip().upper()
        if a == "EQ":
            return 1.0 if entry.answer == "EQ" else 0.0
        if a == "NEQ":
            return 1.0 if entry.answer == "NEQ" else 0.0
        return 0.0

    def distractor_candidates(self, entry):
        return ["EQ" if entry.answer == "NEQ" else "NEQ"]
