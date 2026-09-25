import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_counterfactual_r4.relational_gadget_synthesis.relational_gadget_synthesis import RelationalGadgetSynthesis

random.seed(1259343118)


def main():
    out = Path(__file__).with_name("samples_P003v3.md")
    task = RelationalGadgetSynthesis()
    blocks = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        blocks.append(f"## Level {level}\n")
        for i in range(2):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            blocks.append(f"### Example i={i}\n")
            blocks.append("Prompt:\n")
            blocks.append(prompt + "\n")
            blocks.append("Answer:\n")
            blocks.append(ex.answer + "\n")
    out.write_text("\n".join(blocks) + "\n")
    print(out)


if __name__ == "__main__":
    main()
