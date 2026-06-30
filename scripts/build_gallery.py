#!/usr/bin/env python
import argparse
import inspect
import re
from collections import OrderedDict
from pathlib import Path

from tqdm.auto import tqdm

from reasoning_core import get_task, list_tasks


CATEGORY_ORDER = [
    "arithmetics", "equation_system", "math_lean", "math_tptp",
    "math_geometry", "binding", "probabilistic_reasoning",
    "causal_reasoning", "logic_semantics", "logic_depth", "planning",
    "set_operations", "sequential_induction", "qstr", "navigation",
    "tracking", "coreference", "constraint_satisfaction",
    "graph_operations", "regex", "knowledge", "grammar", "table_qa",
    "string_transduction", "code_execution",
]

SINGLE_EXAMPLE_TASKS = {
    "conjecture_entailment",
    "theorem_premise_selection",
    "proof_reconstruction",
    "parsing",
    "tptp_consistency_repair",
}

GITHUB_BASE = "https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks"
README_MENU_RE = re.compile(
    r"(\[GALLERY\]\([^)]+\)[^\n]*\n\n)(.*?)(\n\n\[TASK_AUTHORING_GUIDE\]\([^)]+\))",
    re.S,
)


def fence(text):
    text = str(text)
    max_run = max((len(m) for m in re.findall(r"`+", text)), default=2)
    ticks = "`" * max(max_run + 1, 3)
    return f"{ticks}\n{text}\n{ticks}"


def slug(name):
    return re.sub(r"[^\w\s-]", "", name.lower()).replace(" ", "-")


def category_rank(task):
    try:
        return CATEGORY_ORDER.index(task.category_name)
    except ValueError:
        return len(CATEGORY_ORDER)


def pick_example(task, batch_size, cache=False, refresh_cache=False):
    if cache:
        batch = task.validate(n_samples=batch_size, cache=True,
                              refresh=refresh_cache)
    else:
        batch = task.generate_balanced_batch(batch_size=batch_size)
    return sorted(batch, key=lambda x: len(x.prompt) - len(str(x.answer)))[0]


def source_link(task):
    rel_path = inspect.getfile(task.__class__).split("/tasks")[-1]
    return f"{GITHUB_BASE}{rel_path}"


def build_examples(tasks, cache=False, refresh_cache=False, allow_missing=False):
    examples = OrderedDict()
    failures = []
    for task in tqdm(tasks):
        name = task.task_name
        if name in examples:
            continue
        print(name)
        try:
            batch_size = 1 if name in SINGLE_EXAMPLE_TASKS else 4
            examples[name] = pick_example(task, batch_size, cache,
                                          refresh_cache)
        except Exception as e:
            failures.append((name, e))
            print(f"{name}: {e}")
    if failures and not allow_missing:
        names = ", ".join(name for name, _ in failures)
        raise RuntimeError(f"failed to build gallery examples for: {names}")
    return examples


def write_gallery(examples, out_path):
    out_path = Path(out_path)
    with out_path.open("w", encoding="utf-8") as f:
        menu = " · ".join(f"[`{t}`](#{slug(t)})" for t in examples)
        f.write(f"# 📖 Task Gallery\n\n{menu}\n\n---\n\n")
        for name, example in examples.items():
            task = get_task(name)
            f.write(
                f"## [{name}]({source_link(task)})\n\n"
                f"**Prompt:**\n{fence(example.prompt)}\n\n"
                f"**Answer:**\n{fence(example.answer)}\n\n---\n\n"
            )


def gallery_menu(examples):
    return " · ".join(f"[`{name}`](GALLERY.md#{slug(name)})" for name in examples)


def refresh_readme_menu(examples, readme_path):
    readme_path = Path(readme_path)
    text = readme_path.read_text(encoding="utf-8")
    menu = gallery_menu(examples)
    new_text, n = README_MENU_RE.subn(rf"\1{menu}\3", text, count=1)
    if n != 1:
        raise RuntimeError(
            f"could not find README gallery menu block in {readme_path}"
        )
    readme_path.write_text(new_text, encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="GALLERY.md")
    parser.add_argument("--readme", default="README.md")
    parser.add_argument("--update-readme", choices=["auto", "always", "never"],
                        default="auto",
                        help=("Refresh README gallery menu. auto updates only for "
                              "full GALLERY.md builds."))
    parser.add_argument("--no-cache", action="store_true",
                        help="Use generate_balanced_batch instead of cached validation examples.")
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--allow-missing", action="store_true")
    parser.add_argument("--tasks", nargs="*", default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    names = args.tasks or list_tasks()
    tasks = sorted((get_task(name) for name in names), key=category_rank)
    examples = build_examples(tasks, cache=not args.no_cache,
                              refresh_cache=args.refresh_cache,
                              allow_missing=args.allow_missing)
    write_gallery(examples, args.out)
    update_readme = args.update_readme == "always" or (
        args.update_readme == "auto" and args.tasks is None and
        Path(args.out).name == "GALLERY.md"
    )
    if update_readme:
        refresh_readme_menu(examples, args.readme)


if __name__ == "__main__":
    main()
