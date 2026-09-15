import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'schema_migration_execution (draw 1 of 3)',
 'hypothesis': 'manual_high_value_80:schema_migration_execution',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/schema_migration_execution',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 469753138,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class MigrationConfig(Config):
    n_ops: int = 2
    n_fields: int = 3

    def apply_difficulty(self, level):
        self.n_fields = self.n_fields + level
        self.n_ops = 2 + level


def _apply(record, ops):
    rec = dict(record)
    for kind, args in ops:
        if kind == 'rename':
            src, dst = args
            val = rec.pop(src)
            rec[dst] = val
        elif kind == 'split':
            src, dsts = args
            val = rec.pop(src)
            vals = str(val).split(',')
            for i, d in enumerate(dsts):
                rec[d] = int(vals[i]) if vals[i].strip('-').isdigit() else vals[i]
        elif kind == 'merge':
            srcs, dst = args
            rec[dst] = '-'.join(str(rec.pop(s)) for s in srcs)
        elif kind == 'default':
            src, val = args
            if src not in rec:
                rec[src] = val
        elif kind == 'convert':
            src, typ = args
            rec[src] = int(rec[src])
    return rec


def _fmt(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    return str(v)


class SchemaMigrationExecution(Task):
    summary = ("Apply ordered field rename, split, merge, default, and type-conversion "
               "operations to flat JSON records with string/int/bool fields, returning the "
               "canonical migrated record as a compact dotted-path list of new field values.")
    config_cls = MigrationConfig
    design_choice = ("Instances are flat JSON records; answer is a compact dotted-path list "
                     "of new field values in a fixed order.")

    def generate_entry(self):
        while True:
            keys = ['a', 'b', 'c', 'd', 'e']
            random.shuffle(keys)
            fields = keys[:self.config.n_fields]
            record = {}
            for i, k in enumerate(fields):
                choice = random.choice(range(4))
                if choice == 0:
                    record[k] = random.randint(-20, 20)
                elif choice == 1:
                    record[k] = random.choice(['x', 'y', 'z'])
                elif choice == 2:
                    record[k] = random.choice([True, False])
                else:
                    record[k] = ','.join(str(random.randint(-9, 9)) for _ in range(random.randint(1, 3)))

            ops = []
            sim = dict(record)
            pool = [f'f{i}' for i in range(20)]
            for _ in range(self.config.n_ops):
                kind = random.choice(['rename', 'split', 'merge', 'default', 'convert'])
                if kind == 'rename' and sim:
                    src = random.choice(list(sim.keys()))
                    dst = random.choice(pool)
                    while dst in sim:
                        dst = random.choice(pool)
                    ops.append(('rename', (src, dst)))
                    sim[dst] = sim.pop(src)
                elif kind == 'split':
                    srcs = [k for k in sim if isinstance(sim[k], str) and ',' in sim[k]]
                    if srcs:
                        src = random.choice(srcs)
                        parts = sim[src].split(',')
                        dsts = []
                        for _ in parts:
                            d = random.choice(pool)
                            while d in sim:
                                d = random.choice(pool)
                            dsts.append(d)
                        ops.append(('split', (src, dsts)))
                        del sim[src]
                        for d, p in zip(dsts, parts):
                            sim[d] = int(p) if p.strip('-').isdigit() else p
                    else:
                        d = random.choice(pool)
                        while d in sim:
                            d = random.choice(pool)
                        sim[d] = 0
                        ops.append(('default', (d, 0)))
                elif kind == 'merge':
                    str_keys = [k for k in sim
                                if isinstance(sim[k], str) and ',' not in sim[k]]
                    int_keys = [k for k in sim if isinstance(sim[k], (int, bool))]
                    cand = str_keys + int_keys
                    if len(cand) >= 2:
                        pair = random.sample(cand, 2)
                        dst = random.choice(pool)
                        while dst in sim:
                            dst = random.choice(pool)
                        joined = '-'.join(str(sim.pop(s)) for s in pair)
                        sim[dst] = joined
                        ops.append(('merge', (pair, dst)))
                        continue
                    d = random.choice(pool)
                    while d in sim:
                        d = random.choice(pool)
                    sim[d] = 0
                    ops.append(('default', (d, 0)))
                elif kind == 'default':
                    d = random.choice(pool)
                    while d in sim:
                        d = random.choice(pool)
                    sim[d] = random.choice([0, 'null', 1])
                    ops.append(('default', (d, random.choice([0, 'null', 1]))))
                elif kind == 'convert':
                    srcs = [k for k in sim if isinstance(sim[k], str)
                            and sim[k].strip('-').isdigit()]
                    if srcs:
                        src = random.choice(srcs)
                        sim[src] = int(sim[src])
                        ops.append(('convert', (src, 'int')))
                    else:
                        d = random.choice(pool)
                        while d in sim:
                            d = random.choice(pool)
                        sim[d] = 0
                        ops.append(('default', (d, 0)))

            result = _apply(record, ops)

            out_names = []
            for o in ops:
                if o[0] == 'rename':
                    out_names.append(o[1][1])
                elif o[0] == 'split':
                    out_names.extend(o[1][1])
                elif o[0] == 'merge':
                    out_names.append(o[1][1])
                elif o[0] == 'default':
                    out_names.append(o[1][0])
                elif o[0] == 'convert':
                    out_names.append(o[1][0])

            if not out_names:
                continue

            out_paths = sorted(set(out_names))
            if any(p not in result for p in out_paths):
                continue

            answers = [_fmt(result[p]) for p in out_paths]

            return Entry(
                metadata={
                    'record': record,
                    'ops': ops,
                    'out_paths': out_paths,
                    'result': result,
                },
                answer='; '.join(f'{p}={a}' for p, a in zip(out_paths, answers)),
            )

    def render_prompt(self, metadata):
        rec = metadata['record']
        rec_str = ', '.join(f"'{k}': {v}" for k, v in rec.items())
        ops_lines = []
        for idx, o in enumerate(metadata['ops'], 1):
            kind, args = o
            if kind == 'rename':
                ops_lines.append(f"{idx}. rename field '{args[0]}' to '{args[1]}'")
            elif kind == 'split':
                ops_lines.append(f"{idx}. split field '{args[0]}' on commas into fields {args[1]}")
            elif kind == 'merge':
                ops_lines.append(f"{idx}. merge fields {list(args[0])} into '{args[1]}' joined by '-'")
            elif kind == 'default':
                ops_lines.append(f"{idx}. if field '{args[0]}' is absent, set it to {args[1]}")
            elif kind == 'convert':
                ops_lines.append(f"{idx}. convert field '{args[0]}' to integer")
        ops_str = '\n'.join(ops_lines)
        out = ', '.join(f"'{p}'" for p in metadata['out_paths'])
        return (f"Apply these migration operations, in the given order, to the flat record "
                f"{{ {rec_str} }}:\n{ops_str}\n"
                f"Report the final value of each of the fields in the fixed order "
                f"{out}, as 'path=value' pairs separated by '; ' "
                f"(booleans as true/false).")

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        try:
            parts = [p.strip() for p in answer.split(';')]
        except Exception:
            return 0.0
        result = entry.metadata['result']
        paths = entry.metadata['out_paths']
        if len(parts) != len(paths):
            return 0.0
        expected = []
        for i, p in enumerate(paths):
            expected.append(f'{p}={_fmt(result[p])}')
        return 1.0 if parts == expected else 0.0
