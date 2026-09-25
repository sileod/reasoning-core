import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_state_tracking_r4.stencil_depth_compositing.stencil_depth_compositing import (
    StencilDepthCompositing,
)


def main():
    random.seed(1277236794)
    out = Path(__file__).with_name("samples_P012v1.md")
    lines = []
    lines.append("# Stencil/depth compositing samples\n")
    lines.append(
        "Each example simulates a fragment compositing pipeline (stencil test, depth test, "
        "masked writes, integer blending) and asks for the final color/depth/stencil of a "
        "compact list of queried pixels.\n"
    )
    for level in (0, 2, 5):
        t = StencilDepthCompositing()
        t.config.set_level(level)
        lines.append(f"## Level {level}\n")
        for _ in range(2):
            e = t.generate_example()
            prompt = t.render_prompt(e.metadata)
            lines.append("### Example\n")
            lines.append(prompt)
            lines.append("\n**Answer:**\n")
            lines.append(e.answer)
            lines.append("\n")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
