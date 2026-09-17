import random
from pathlib import Path

from distance_based_belief_merge import DistanceBasedBeliefMerge


def main():
    random.seed(2267388306)
    task = DistanceBasedBeliefMerge()
    out = ['# Samples for distance_based_belief_merge (seed 2267388306)', '']
    for lvl in (0, 2, 5):
        out.append('## Level %d' % lvl)
        out.append('')
        for i in range(2):
            task.config.set_level(lvl)
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            out.append('### Example %d' % (i + 1))
            out.append('')
            out.append('Prompt:')
            out.append('')
            out.append(prompt)
            out.append('')
            out.append('Answer: %s' % ex.answer)
            out.append('')
    path = Path(__file__).with_name('samples_P003v1.md')
    path.write_text('\n'.join(out))


if __name__ == '__main__':
    main()
