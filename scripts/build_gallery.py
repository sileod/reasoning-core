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
    "math_geometry", "math_metamath", "binding",
    "probabilistic_reasoning", "causal_reasoning", "logic_semantics",
    "logic_depth", "planning", "set_operations", "sequential_induction",
    "qstr", "navigation", "tracking", "coreference",
    "constraint_satisfaction", "graph_operations", "regex",
    "formal_analogies", "grammar", "knowledge", "table_qa",
    "string_transduction", "code_execution", "game_playing",
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


def sort_tasks(names):
    registry_rank = {name: i for i, name in enumerate(list_tasks())}
    return sorted(
        (get_task(name) for name in names),
        key=lambda task: (category_rank(task), registry_rank.get(task.task_name, 10**9)),
    )


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


def section_text(name, example):
    task = get_task(name)
    return (
        f"## [{name}]({source_link(task)})\n\n"
        f"**Prompt:**\n{fence(example.prompt)}\n\n"
        f"**Answer:**\n{fence(example.answer)}"
    )


def read_sections(path):
    path = Path(path)
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^## \[([^\]]+)\].*$", text, re.M))
    sections = {}
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section = text[start:end].strip()
        if section.endswith("---"):
            section = section[:-3].rstrip()
        sections[match.group(1)] = section
    return sections


def write_gallery(task_names, examples, out_path, existing_sections=None):
    out_path = Path(out_path)
    existing_sections = existing_sections or {}
    with out_path.open("w", encoding="utf-8") as f:
        menu = " · ".join(f"[`{t}`](#{slug(t)})" for t in task_names)
        f.write(f"# 📖 Task Gallery\n\n{menu}\n\n---\n\n")
        for name in task_names:
            if name in examples:
                section = section_text(name, examples[name])
            else:
                section = existing_sections[name]
            f.write(f"{section}\n\n---\n\n")


def gallery_menu(task_names):
    return " · ".join(f"[`{name}`](GALLERY.md#{slug(name)})" for name in task_names)


def refresh_readme_menu(task_names, readme_path):
    readme_path = Path(readme_path)
    text = readme_path.read_text(encoding="utf-8")
    menu = gallery_menu(task_names)
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
    tasks = sort_tasks(names)
    examples = build_examples(tasks, cache=not args.no_cache,
                              refresh_cache=args.refresh_cache,
                              allow_missing=args.allow_missing)
    task_names = [task.task_name for task in tasks]
    existing_sections = read_sections(args.out)
    missing = [name for name in task_names if name not in examples and name not in existing_sections]
    if missing:
        raise RuntimeError(f"no generated or existing gallery section for: {', '.join(missing)}")
    write_gallery(task_names, examples, args.out, existing_sections)
    update_readme = args.update_readme == "always" or (
        args.update_readme == "auto" and args.tasks is None and
        Path(args.out).name == "GALLERY.md"
    )
    if update_readme:
        refresh_readme_menu(task_names, args.readme)


if __name__ == "__main__":
    main()
