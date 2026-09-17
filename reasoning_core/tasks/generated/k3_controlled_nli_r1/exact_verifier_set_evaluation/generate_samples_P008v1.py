import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_controlled_nli_r1.exact_verifier_set_evaluation.exact_verifier_set_evaluation import ExactVerifierSetEvaluation


def main():
    random.seed(682015719)
    sections = ["# P008v1 exact verifier-set evaluation samples\n"]
    for level in (0, 2, 5):
        sections.append(f"## Level {level}\n")
        task = ExactVerifierSetEvaluation()
        task.config.set_level(level)
        for index in range(2):
            entry = task.generate_entry()
            prompt = task.render_prompt(entry.metadata)
            sections.append(f"### Example {index + 1}\n\nPrompt:\n```\n{prompt}\n```\n\nAnswer:\n```\n{entry.answer}\n```\n")
    Path(__file__).with_name("samples_P008v1.md").write_text("\n".join(sections), encoding="utf-8")


if __name__ == "__main__":
    main()
