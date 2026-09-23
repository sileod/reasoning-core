"""Generate samples_P005v1.md for the registration-waitlist-replay task."""

import random
from pathlib import Path

random.seed(729651269)

from registration_waitlist_replay import RegistrationWaitlistReplay

OUT = Path(__file__).with_name("samples_P005v1.md")


def main():
    t = RegistrationWaitlistReplay()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}\n")
        for _ in range(2):
            t.config.set_level(level)
            entry = t.generate_example()
            prompt = t.render_prompt(entry.metadata)
            lines.append("### Example\n")
            lines.append(prompt.strip() + "\n")
            lines.append("\n**Answer:** " + entry.answer + "\n")
        lines.append("\n")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
