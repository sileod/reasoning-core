import random
from pathlib import Path

from event_driven_gate_simulation import EventDrivenGateSimulation

random.seed(2302342651)

OUT = Path(__file__).with_name('samples_P001v2.md')


def main():
    lines = []
    task = EventDrivenGateSimulation()
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append('## Level %d' % level)
        lines.append('')
        n = 0
        while n < 2:
            ex = task.generate_example()
            if task.score_answer(ex.answer, ex) != 1.0:
                continue
            lines.append('**Example %d**' % (n + 1))
            lines.append('')
            lines.append('**Prompt**')
            lines.append('')
            lines.append('```')
            lines.append(task.render_prompt(ex.metadata))
            lines.append('```')
            lines.append('')
            lines.append('**Answer**')
            lines.append('')
            lines.append('```')
            lines.append(ex.answer)
            lines.append('```')
            lines.append('')
            n += 1
    OUT.write_text('\n'.join(lines))
    print('wrote', OUT)


if __name__ == '__main__':
    main()
