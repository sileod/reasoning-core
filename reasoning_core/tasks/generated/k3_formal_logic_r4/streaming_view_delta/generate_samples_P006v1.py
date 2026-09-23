import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_formal_logic_r4.streaming_view_delta.streaming_view_delta import StreamingViewDelta


def main():
    random.seed(798610012)
    task = StreamingViewDelta()
    out = []
    for level in (0, 2, 5):
        out.append(f"## Level {level}")
        task.config.set_level(level)
        counts = {}
        for i in range(2):
            x = task.generate_example()
            kind = x.metadata["kind"]
            counts[kind] = counts.get(kind, 0) + 1
            prompt = task.render_prompt(x.metadata)
            out.append(f"### Example {i+1} ({kind})")
            out.append(prompt)
            out.append("")
            out.append("Answer:")
            out.append(x.answer)
            out.append("")
    Path(__file__).with_name("samples_P006v1.md").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
