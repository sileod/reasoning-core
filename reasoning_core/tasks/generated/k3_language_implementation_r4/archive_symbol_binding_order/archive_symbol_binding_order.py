import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'archive_symbol_binding_order (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_language_implementation_r4/archive_symbol_binding_order',
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

_SYMS = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
         'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho',
         'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega']

_STR = {'S': 3, 'C': 2, 'W': 1}


def _strength_char():
    r = random.random()
    if r < 0.56:
        return 'S'
    if r < 0.80:
        return 'C'
    return 'W'


def _link(commands):
    binding = {}
    undefined = set()
    extracted = []
    for kind, a, b in commands:
        if kind == 'obj':
            defs, uses = a, b
            for sym, t in defs:
                if t == 'I':
                    continue
                if sym not in binding or _STR[t] > _STR[binding[sym]]:
                    binding[sym] = t
                undefined.discard(sym)
            for sym in uses:
                if sym not in binding:
                    undefined.add(sym)
        else:
            members = a
            for mid, defs, uses in members:
                if any(t != 'I' and sym in undefined for sym, t in defs):
                    extracted.append(mid)
                    for sym, t in defs:
                        if t == 'I':
                            continue
                        if sym not in binding or _STR[t] > _STR[binding[sym]]:
                            binding[sym] = t
                        undefined.discard(sym)
                    for sym in uses:
                        if sym not in binding:
                            undefined.add(sym)
    table = dict(binding)
    for n in sorted(undefined):
        table[n] = 'U'
    return extracted, table


@dataclass
class ArchiveSymbolBindingConfig(Config):
    n_objects: int = 2
    n_archives: int = 1
    members_per_archive: int = 2
    sym_pool: int = 6
    defs_per_unit: int = 2
    uses_per_unit: int = 2

    def apply_difficulty(self, level):
        self.n_objects = 1 + level
        self.n_archives = 1 + level // 2
        self.members_per_archive = 2 + level // 2
        self.sym_pool = 4 + 2 * level
        self.defs_per_unit = 2 + level // 2
        self.uses_per_unit = 1 + level // 2


class ArchiveSymbolBindingOrder(Task):
    summary = ("Process object files and archives in link order with strong, weak, common, "
               "and internal symbols, extracting archive members only as references demand; "
               "report extracted members and the final binding table.")
    design_choice = ("Represent inputs as a text sequence of link-command lines and outputs "
                     "as a canonical ordered list of extracted member names and final binding table.")
    config_cls = ArchiveSymbolBindingConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        syms = random.sample(_SYMS, min(cfg.sym_pool, len(_SYMS)))
        random.shuffle(syms)
        n_int = min(2, max(0, len(syms) - 3))
        internal_syms = syms[:n_int]
        rest_all = syms[n_int:]
        n_obj_syms = max(1, int(len(rest_all) * 0.5))
        obj_syms = rest_all[:n_obj_syms]
        rest = rest_all[n_obj_syms:]
        n_orphan = max(0, min(len(rest) - 1, len(rest) // 2))
        arch_syms = rest[:len(rest) - n_orphan] if n_orphan < len(rest) else []

        def pick(seq, k):
            return random.sample(seq, min(k, len(seq)))

        commands = []
        obj_cursor = 0
        for i in range(cfg.n_objects):
            defs = []
            take = max(1, min(cfg.defs_per_unit, max(1, len(obj_syms) // cfg.n_objects)))
            if obj_cursor < len(obj_syms):
                for s in obj_syms[obj_cursor:obj_cursor + take]:
                    defs.append((s, _strength_char()))
                    obj_cursor += 1
            if internal_syms and random.random() < 0.6:
                defs.append((random.choice(internal_syms), 'I'))
            uses = pick(syms, cfg.uses_per_unit)
            commands.append(('obj', defs, uses))
        mid_counter = 1
        for _ in range(cfg.n_archives):
            members = []
            for _ in range(cfg.members_per_archive):
                pool = arch_syms if arch_syms else syms
                defs = [(s, _strength_char()) for s in pick(pool, random.randint(1, cfg.defs_per_unit))]
                if internal_syms and random.random() < 0.4:
                    defs.append((random.choice(internal_syms), 'I'))
                uses = pick(syms, cfg.uses_per_unit)
                members.append((f"m{mid_counter}", defs, uses))
                mid_counter += 1
            commands.append(('ar', members, None))
        extracted, table = _link(commands)
        assert table, "link must bound at least one symbol"
        return Entry(metadata={
            'commands': commands,
            'extracted': extracted,
            'bindings': table,
        }, answer=_format_answer(extracted, table))

    def render_prompt(self, metadata):
        lines = ['Commands (in order):']
        for kind, a, b in metadata['commands']:
            if kind == 'obj':
                defs, uses = a, b
                d = ', '.join(f"{s}={t}" for s, t in defs) or 'none'
                u = ' '.join(uses) or 'none'
                lines.append(f"object: defines {d} | uses {u}")
            else:
                lines.append('archive:')
                for mid, defs, uses in a:
                    d = ', '.join(f"{s}={t}" for s, t in defs)
                    u = ' '.join(uses)
                    lines.append(f"  member {mid}: defines {d} | uses {u}")
        rules = (
            "Object files are always loaded. An archive member is extracted only if it "
            "defines a symbol currently referenced by an already-loaded unit and not yet "
            "defined; extracted members load at that point and may satisfy or add needs.\n"
            "Def strengths: S=strong, W=weak, C=common, I=internal(local). I never binds an "
            "external symbol. When several definitions of one symbol load, S beats C beats W; "
            "among equal strength the earliest in link order wins.\n"
            "Report two lines: 'Extracted:' then the extracted members in link order (or "
            "'none' if none), then 'Bindings:' then name=strength for every symbol bound by a "
            "loaded strong/weak/common definition or left unresolved, sorted by name; "
            "unresolved symbols get strength U.\n"
            "Example format:\nExtracted: m1 m2\nBindings: alpha=S beta=U"
        )
        return "\n".join(lines) + "\n\n" + rules

    def score_answer(self, answer, entry):
        return _score(answer, entry)


def _format_answer(extracted, table):
    ex = ' '.join(extracted) if extracted else 'none'
    pairs = ' '.join(f"{n}={table[n]}" for n in sorted(table))
    return f"Extracted: {ex}\nBindings: {pairs}"


def _norm(s):
    return ' '.join(str(s).split())


def _score(answer, entry):
    ref = _norm(entry['answer'])
    ans = _norm(answer)
    return 1 if ans == ref else 0
