import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_controlled_nli_r1.spatial_frame_relation_verdicts.spatial_frame_relation_verdicts import SpatialFrameRelationVerdicts


def main():
    random.seed(1259343118)
    task = SpatialFrameRelationVerdicts()
    sections = ['# P003v3 samples']
    for level in (0, 2, 5):
        task.config.set_level(level)
        sections.append(f'## Level {level}')
        for index, mode in enumerate(('verdicts', 'licensing'), 1):
            for _ in range(100):
                entry = task.generate_entry()
                if entry.metadata['mode'] == mode:
                    break
            else:
                raise RuntimeError('sample mode not found')
            sections.append(f'### Example {index}\n\n**Prompt:**\n```\n'
                            f'{task.render_prompt(entry.metadata)}\n```\n\n'
                            f'**Answer:**\n```\n{entry.answer}\n```')
    Path(__file__).with_name('samples_P003v3.md').write_text('\n\n'.join(sections) + '\n')


if __name__ == '__main__':
    main()
