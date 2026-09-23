import random
import sys

from pathlib import Path

random.seed(1277236794)

parent = Path(__file__).resolve().parent
sys.path.insert(0, str(parent))

from unary_resource_edge_finding import UnaryResourceEdgeFinding

out = Path(__file__).with_name("samples_P012v1.md")


def main():
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        t = UnaryResourceEdgeFinding()
        t.config.set_level(level)
        for k in range(2):
            e = t.generate_example()
            lines.append(f"### Example {k + 1}")
            lines.append("")
            lines.append(t.render_prompt(e.metadata))
            lines.append("")
            lines.append(f"Answer: {e.answer}")
            lines.append("")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
