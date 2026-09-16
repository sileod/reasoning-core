import random
from pathlib import Path

from reasoning_core.template import Config
from reasoning_core.tasks.generated.k3_formal_semantics_r1.tag_adjunction_derivation.tag_adjunction_derivation import (
    TagAdjunctionDerivation,
)

SEED = 682015719


def build_samples():
    random.seed(SEED)
    out = []
    for level in (0, 2, 5):
        out.append(f"\n## Level {level}\n")
        t = TagAdjunctionDerivation()
        t.config.set_level(level)
        for _ in range(2):
            e = t.generate_example()
            prompt = t.render_prompt(e.metadata)
            out.append(prompt.strip())
            out.append("")
            out.append(f"Answer: {e.answer}")
            out.append("")
    return "\n".join(out)


def main():
    text = build_samples()
    path = Path(__file__).with_name("samples_P008v1.md")
    path.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
