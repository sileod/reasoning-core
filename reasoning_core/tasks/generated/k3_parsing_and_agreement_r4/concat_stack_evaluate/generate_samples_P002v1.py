import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_parsing_and_agreement_r4.concatenative_stack_evaluation.concatenative_stack_evaluation import (
    ConcatStackConfig,
    ConcatStackEvaluate,
)

SEED = 1475571465
OUT = Path(__file__).with_name('samples_P002v1.md')


def main():
    random.seed(SEED)
    lines = []
    for level in (0, 2, 5):
        lines.append('# Level %d\n' % level)
        config = ConcatStackConfig()
        config.set_level(level)
        task = ConcatStackEvaluate(config=config)
        shown = 0
        probes = 0
        while shown < 2 and probes < 500:
            probes += 1
            ex = task.generate_example()
            if not ex.answer:
                continue
            shown += 1
            lines.append('### Example %d\n' % shown)
            lines.append('**Prompt**\n')
            lines.append(ex.prompt + '\n')
            lines.append('**Answer**: %s\n' % ex.answer)
        if probes >= 500:
            raise RuntimeError('could not generate samples for level %d' % level)
    OUT.write_text('\n'.join(lines))
    print('wrote', OUT)


if __name__ == '__main__':
    main()
