import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'default_logic_extension (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_systematic_generalization_r4/default_logic_extension',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

MODE_ALL = 'all'
MODE_SOME = 'some'
MODE_APPLICABLE = 'applicable'


def neg(lit):
    if lit.startswith('not '):
        return lit[4:]
    return 'not ' + lit


def consistent(lits):
    s = set(lits)
    for l in lits:
        if neg(l) in s:
            return False
    return True


def gamma_closure(facts, deltas, e):
    """Compute Gamma(e): least set containing facts closed under defaults whose
    prerequisite is in e and whose justification is consistent with e."""
    s = set(facts)
    changed = True
    while changed:
        changed = False
        for prereq, just, cons in deltas:
            if not set(prereq).issubset(e):
                continue
            if any(neg(j) in e for j in just):
                continue
            if not set(cons).issubset(s):
                s.update(cons)
                changed = True
    return s


def all_extensions(facts, deltas, atoms):
    """All extensions of the default theory via fixed-point characterization
    E = Gamma(E), enumerated over consistent subsets of the vocabulary."""
    exts = []
    per_atom = []
    for a in atoms:
        per_atom.append((None, a, 'not ' + a))
    from itertools import product
    for combo in product(*per_atom):
        e = set(l for l in combo if l is not None)
        if not set(facts).issubset(e):
            continue
        if gamma_closure(facts, deltas, e) == e:
            exts.append(frozenset(e))
    return set(exts)


def applicable_default(ext, d):
    prereq, just, cons = d
    if not set(prereq).issubset(ext):
        return False
    if any(neg(j) in ext for j in just):
        return False
    if set(cons).issubset(ext):
        return False
    return True


def lit_sort_key(lit):
    return (0, lit) if not lit.startswith('not ') else (1, lit[4:])


def render_set(s):
    return ', '.join(sorted(s, key=lit_sort_key))


def render_extension(e):
    return '{' + render_set(e) + '}'


def render_default(d):
    prereq, just, cons = d
    return ('(' + render_set(prereq) + ' : ' + render_set(just)
            + ' : ' + render_set(cons) + ')')


@dataclass
class DefaultLogicConfig(Config):
    atoms: int = 3
    num_defaults: int = 2
    mode: str = MODE_ALL

    def apply_difficulty(self, level):
        self.atoms = 3 + level // 2
        self.num_defaults = 2 + level


class DefaultLogicExtension(Task):
    summary = ("Compute extensions of normal and semi-normal default theories over "
               "propositional facts; modes ask for all extensions, whether a formula "
               "is in some extension, or whether a default is applicable in a given extension.")
    design_choice = ("Represent defaults as prerequisite:justification:consequent triples over a "
                     "fixed propositional vocabulary, with extensions computed via a fixed-point "
                     "closure over grounded defaults.")
    config_cls = DefaultLogicConfig

    def generate_defaults(self, atoms):
        """Generate consistent defaults over the shared vocabulary; return list of (P,J,C)."""
        deltas = []
        for _ in range(self.config.num_defaults):
            pool = atoms
            prereq = []
            just = []
            cons = []
            used = set()
            n = random.randint(1, 2)
            for _ in range(n):
                a = random.choice(pool)
                lit = a if random.random() < 0.5 else 'not ' + a
                if neg(lit) in used or lit in used:
                    continue
                prereq.append(lit)
                used.add(lit)
            n = random.randint(1, 2)
            for _ in range(n):
                a = random.choice(pool)
                lit = a if random.random() < 0.5 else 'not ' + a
                if neg(lit) in used or lit in used:
                    continue
                just.append(lit)
                used.add(lit)
            n = random.randint(1, 2)
            for _ in range(n):
                a = random.choice(pool)
                lit = a if random.random() < 0.5 else 'not ' + a
                if neg(lit) in used or lit in used:
                    continue
                cons.append(lit)
                used.add(lit)
            p = tuple(sorted(set(prereq), key=lit_sort_key))
            j = tuple(sorted(set(just), key=lit_sort_key))
            c = tuple(sorted(set(cons), key=lit_sort_key))
            if not c:
                continue
            if not consistent(list(j) + list(c)):
                continue
            deltas.append((p, j, c))
        if not deltas:
            # refill with a single guaranteed non-empty grounded default
            a = random.choice(atoms)
            lit = a if random.random() < 0.5 else 'not ' + a
            deltas.append(((), (lit,), (lit if random.random() < 0.5 else 'not ' + a,)))
        return deltas

    def build_instance(self):
        atoms = [chr(ord('a') + i) for i in range(self.config.atoms)]
        facts = []
        for a in atoms:
            if random.random() < 0.5:
                facts.append(a)
        facts = tuple(sorted(set(facts), key=lit_sort_key))
        deltas = self.generate_defaults(atoms)
        return atoms, list(facts), deltas

    def _gen_all(self):
        """Guarantee a valid all-extensions entry with a non-empty answer."""
        for _ in range(300):
            atoms, facts, deltas = self.build_instance()
            exts = all_extensions(facts, deltas, atoms)
            if len(exts) >= 1:
                exts = sorted(exts, key=lambda e: (len(e), sorted(e, key=lit_sort_key)))
                answer = ' ; '.join(render_extension(e) for e in exts)
                metadata = {'mode': MODE_ALL, 'atoms': atoms, 'facts': facts,
                            'defaults': [list(d) for d in deltas],
                            'extensions': [list(e) for e in exts]}
                return Entry(metadata=metadata, answer=answer)
        raise RuntimeError('failed to produce a default theory with an extension')

    def generate_entry(self):
        mode = random.choice([MODE_ALL, MODE_SOME, MODE_APPLICABLE])
        want_yes = None
        if mode != MODE_ALL:
            want_yes = random.random() < 0.5
        for _ in range(300):
            atoms, facts, deltas = self.build_instance()
            exts = all_extensions(facts, deltas, atoms)
            if len(exts) < 1:
                continue
            exts = sorted(exts, key=lambda e: (len(e), sorted(e, key=lit_sort_key)))
            if mode == MODE_ALL:
                answer = ' ; '.join(render_extension(e) for e in exts)
                metadata = {'mode': MODE_ALL, 'atoms': atoms, 'facts': facts,
                            'defaults': [list(d) for d in deltas],
                            'extensions': [list(e) for e in exts]}
                return Entry(metadata=metadata, answer=answer)
            if mode == MODE_SOME:
                chosen = None
                present = None
                for _ in range(80):
                    lit = random.choice(atoms + ['not ' + a for a in atoms])
                    p = any(lit in e for e in exts)
                    if (p == want_yes):
                        chosen = lit
                        present = p
                        break
                if chosen is not None:
                    answer = 'Yes' if present else 'No'
                    metadata = {'mode': mode, 'atoms': atoms, 'facts': facts,
                                'defaults': [list(d) for d in deltas],
                                'extensions': [list(e) for e in exts],
                                'formula': [chosen]}
                    return Entry(metadata=metadata, answer=answer)
            else:
                target_ext = exts[0]
                chosen_d = None
                app = None
                for _ in range(80):
                    idx = random.randrange(len(deltas))
                    d = deltas[idx]
                    a = applicable_default(target_ext, d)
                    if (a == want_yes):
                        chosen_d = idx
                        app = a
                        break
                if chosen_d is not None:
                    answer = 'Yes' if app else 'No'
                    metadata = {'mode': mode, 'atoms': atoms, 'facts': facts,
                                'defaults': [list(d) for d in deltas],
                                'extensions': [list(e) for e in exts],
                                'given_extension': sorted(target_ext, key=lit_sort_key),
                                'checked_default': chosen_d}
                    return Entry(metadata=metadata, answer=answer)
        return self._gen_all()

    def render_prompt(self, metadata):
        mode = metadata['mode']
        lines = []
        facts = metadata['facts']
        lines.append('Consider a default logic theory over propositional atoms '
                     + ', '.join(metadata['atoms']) + '.')
        lines.append('The known facts are ' + (render_set(facts) if facts else '{}')
                     + '.')
        defaults = metadata['defaults']
        rendered = []
        shown = sorted(range(len(defaults)), key=lambda i: (len(defaults[i][0]),
                                                            defaults[i][0]))
        for i in shown:
            d = defaults[i]
            rendered.append(f'{i}: {render_default(tuple(d))}')
        lines.append('The defaults are (index: Prerequisite : Justification : Consequent): '
                     + ' '.join(rendered) + '.')
        if mode == MODE_ALL:
            lines.append('An extension is a set of literals E containing the facts such that '
                         'E = Gamma(E), where Gamma(E) is the least superset of the facts closed '
                         'under applying every default whose prerequisite is in E and whose '
                         'justification is consistent with E (adds its consequent).')
            lines.append('List all extensions of this theory. Write each extension as a '
                         'braced, comma-separated set of literals in alphabetical order '
                         '(negated literals after positive ones), and separate distinct '
                         'extensions with a semicolon.')
        elif mode == MODE_SOME:
            formula = metadata['formula']
            lines.append('Imagine iterating to extensions as fixed points E = Gamma(E) as '
                         'described, one extension at a time (in any order).')
            lines.append('Is the formula ' + render_set(formula)
                         + ' true in at least one extension of the theory? '
                         'Answer Yes or No only.')
        else:
            gi = metadata['given_extension']
            d = defaults[metadata['checked_default']]
            lines.append('Consider the extension E = ' + render_set(gi) + '.')
            lines.append('A default is applicable in E when E contains its prerequisite, E '
                         'is consistent with its justification, and E does not already contain '
                         'its consequent.')
            lines.append('In this extension E, is the following default applicable: '
                         + f"{metadata['checked_default']}: "
                         + render_default(tuple(d))
                         + '? Answer Yes or No only.')
        return '\n'.join(lines)

    def score_answer(self, answer, entry):
        mode = entry['metadata']['mode']
        ref = entry['answer']
        if mode == MODE_ALL:
            norm = lambda s: ' '.join(s.split())
            return 1.0 if norm(str(answer)) == norm(str(ref)) else 0.0
        return 1.0 if str(answer).strip().lower() == str(ref).strip().lower() else 0.0
