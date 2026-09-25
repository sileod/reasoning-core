import random
from pathlib import Path

from interval_matrix_regularity import IntervalMatrixRegularity

SEED = 3577985643


def main():
    random.seed(SEED)
    out = Path(__file__).with_name('samples_P004v2.md')
    task = IntervalMatrixRegularity()
    chunks = []
    for level in (0, 2, 5):
        chunks.append('## Level %d\n' % level)
        for k in range(2):
            ex = task.generate_example(level=level)
            chunks.append('**Example %d**\n\n' % (k + 1))
            chunks.append('**Prompt:**\n\n%s\n\n' % ex.prompt)
            chunks.append('**Answer:** %s\n\n' % ex.answer)
    out.write_text('\n'.join(chunks))
    print(out)


if __name__ == '__main__':
    main()
