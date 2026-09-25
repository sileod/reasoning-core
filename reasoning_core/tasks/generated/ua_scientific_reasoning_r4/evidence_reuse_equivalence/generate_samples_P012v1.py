import random
from pathlib import Path

from evidence_reuse_equivalence import EvidenceReuseEquivalence

SEED = 1277236794


def main():
    random.seed(SEED)
    task = EvidenceReuseEquivalence()

    out_path = Path(__file__).with_name('samples_P012v1.md')

    lines = []
    lines.append('# Samples: evidence_reuse_equivalence (P012v1)')
    lines.append('')
    lines.append('Each pair of derivations cites sentence identifiers from a fixed '
                 'universe; the task asks whether their support sets coincide as '
                 'sets of identifiers, answering yes or no.')
    lines.append('')

    for level in (0, 2, 5):
        lines.append(f'## Level {level}')
        lines.append('')
        task.config.set_level(level)
        for i in range(2):
            ex = task.generate_example()
            lines.append(f'### Example {i + 1}')
            lines.append('')
            lines.append('**Prompt**')
            lines.append('')
            lines.append(task.render_prompt(ex.metadata))
            lines.append('')
            lines.append('**Answer**: ' + ex.answer)
            lines.append('')

    out_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {out_path}')


if __name__ == '__main__':
    main()
