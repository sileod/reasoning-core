import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_inference_modes_r4.bounded_loop_deformation.bounded_loop_deformation import (
    BoundedLoopDeformation,
)

random.seed(3536382515)


def gen(level, n):
    task = BoundedLoopDeformation()
    task.config.set_level(level)
    out = []
    for _ in range(n):
        e = task.generate_example()
        prompt = task.render_prompt(e.metadata)
        out.append((prompt, e.answer))
    return out


def main():
    lines = []
    for level, n in ((0, 2), (2, 2), (5, 2)):
        lines.append(f"# Level {level}")
        for prompt, answer in gen(level, n):
            lines.append("## Prompt")
            lines.append("```")
            lines.append(prompt)
            lines.append("```")
            lines.append("## Answer")
            lines.append("```")
            lines.append(answer)
            lines.append("```")
    path = Path(__file__).with_name("samples_P004v1.md")
    path.write_text('\n'.join(lines))


if __name__ == "__main__":
    main()
