import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_synthetic_grammars_r2.trace_monoid_canonization.trace_monoid_canonization import TraceMonoidCanonization


def main():
    random.seed(382564971)
    task = TraceMonoidCanonization()
    sections = ['# P003v2 samples', '']
    for level in (0, 2, 5):
        task.config.set_level(level)
        sections.extend([f'## Level {level}', ''])
        seen = set()
        for _ in range(100):
            entry = task.generate_entry()
            mode = entry.metadata['mode']
            if mode in seen:
                continue
            seen.add(mode)
            sections.extend([
                f'### {mode}', '', '**Prompt:**', '```',
                task.render_prompt(entry.metadata), '```', '',
                '**Answer:**', '```', entry.answer, '```', '',
            ])
            if len(seen) == 3:
                break
        assert len(seen) == 3
    Path(__file__).with_name('samples_P003v2.md').write_text('\n'.join(sections), encoding='utf-8')


if __name__ == '__main__':
    main()
