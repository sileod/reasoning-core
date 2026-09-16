import random
from pathlib import Path

from sld_resolution import SLDResolution

SEED = 368817805
OUT = Path(__file__).with_name("samples_P002v3.md")


def render_example(task, level):
    t = SLDResolution()
    t.config.set_level(level)
    e = t.generate_example()
    prompt = t.render_prompt(e.metadata)
    return prompt, e.answer


def main():
    random.seed(SEED)
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}\n")
        for idx in range(2):
            prompt, answer = render_example(SLDResolution(), level)
            lines.append(f"## Example {idx + 1}\n")
            lines.append("### Prompt\n")
            lines.append("```\n" + prompt + "\n```\n")
            lines.append("### Answer\n")
            lines.append("```\n" + answer + "\n```\n")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
