import json
from collections import Counter
from functools import cache

import verifiers as vf
from datasets import Dataset, DatasetDict, get_dataset_split_names, load_dataset
from easydict import EasyDict as edict
from reasoning_core import get_score_answer_fn, score_answer

DEFAULT_DATASET = "reasoning-core/procedural-pile"
DEFAULT_SYSTEM_PROMPT = (
    "A conversation between User and Assistant. The user asks a question, and the Assistant solves it.\n"
    "The assistant first thinks about the reasoning process in the mind and then provides the user with "
    "the answer. The reasoning process and answer are enclosed within <think> </think> and "
    "<answer> </answer> tags, respectively, i.e., <think> reasoning process here </think>\n"
    "<answer>answer here</answer>\n"
    "Do not explain your reasoning inside the answer tags, provide only the final answer. When an example "
    "is provided, you should strictly follow the format of the output/answer in that example.\n"
)


def _metadata_dict(example):
    metadata = example.get("metadata", {})
    if isinstance(metadata, str):
        try:
            metadata = json.loads(metadata)
        except json.JSONDecodeError:
            metadata = {}
    return metadata or {}


def _example_task_name(example):
    metadata = _metadata_dict(example)
    return metadata.get("_task") or example.get("task") or metadata.get("task")


@cache
def is_scorable(task_name):
    """True when the installed reasoning-core has a scorer for this task (roster or parked)."""
    try:
        get_score_answer_fn(task_name)
        return True
    except (ValueError, KeyError, ImportError):
        return False


def _filter_available_tasks(dataset, available_tasks=None):
    keep = (lambda t: t in available_tasks) if available_tasks is not None else is_scorable
    dropped = Counter(t for t in map(_example_task_name, dataset) if not keep(t))
    if dropped:
        print(f"Ignored {sum(dropped.values())} examples whose task has no scorer here: {dict(dropped)}")
        dataset = dataset.filter(lambda example: keep(_example_task_name(example)))
    return dataset


def _prepare_env_dataset(dataset, available_tasks=None):
    dataset = _filter_available_tasks(dataset, available_tasks).rename_columns({"prompt": "question"})

    def parse_entry(example):
        # metadata stays a JSON string: per-task schemas differ and would not unify into one Arrow struct.
        # "task_name", not "task": verifiers >= 0.3 reserves info["task"] for its own task payload.
        return {"info": {"task_name": _example_task_name(example), "answer": example["answer"],
                         "metadata": json.dumps(_metadata_dict(example))}}

    dataset = dataset.map(parse_entry)
    return dataset.select_columns(
        [column for column in ("question", "answer", "info") if column in dataset.column_names]
    )


def extract_answer(s, tag="answer"):
    if s.strip().startswith('<prompt>'):
        s = s.split('</prompt>')[-1]
    return s.split(f'<{tag}>')[-1].split(f'</{tag}>')[0]


def rc_ds_to_env(ds, system_prompt=DEFAULT_SYSTEM_PROMPT, do_extract_answer=True):
    """Convert a Dataset or DatasetDict (train + test/validation/eval/dev) into a verifiers SingleTurnEnv."""
    if isinstance(ds, DatasetDict):
        main_ds = ds["train"] if "train" in ds else ds[list(ds.keys())[0]]
        eval_ds = next((ds[s] for s in ("test", "validation", "eval", "dev") if s in ds), None)
    else:
        main_ds, eval_ds = ds, None

    dataset = _prepare_env_dataset(main_ds)
    eval_dataset = _prepare_env_dataset(eval_ds) if eval_ds is not None else None

    def score_answer_vf(completion, info, **kwargs) -> float:
        answer = completion[-1]["content"] if isinstance(completion, list) else completion
        if do_extract_answer:
            answer = extract_answer(answer)
        entry = edict(task=info["task_name"], answer=info["answer"], metadata=info["metadata"])
        return float(score_answer(answer, entry))

    rubric = vf.Rubric(funcs=[score_answer_vf])
    return vf.SingleTurnEnv(
        dataset=dataset,
        eval_dataset=eval_dataset,
        rubric=rubric,
        system_prompt=system_prompt,
    )


def load_environment(
    num_train_examples: int = 500,
    num_eval_examples: int = 50,
    do_extract_answer=True,
    dataset_name: str = DEFAULT_DATASET,
    seed: int = 0,
    revision: str | None = None,
) -> vf.SingleTurnEnv:
    """Sample train/eval rows from the pile (pin `revision` to a tag or commit for reproducibility)."""
    available_splits = get_dataset_split_names(dataset_name, revision=revision)
    eval_source_split = next(
        (split for split in ("test", "validation", "eval", "dev") if split in available_splits),
        "train",
    )
    splits = {
        "train": ("train", num_train_examples, seed),
        "test": (eval_source_split, num_eval_examples, seed + int(eval_source_split == "train")),
    }
    ds = DatasetDict({
        split: Dataset.from_list(list(
            load_dataset(dataset_name, split=source_split, streaming=True, revision=revision)
            .shuffle(seed=split_seed)
            .take(n)
        ))
        for split, (source_split, n, split_seed) in splits.items()
    })
    return rc_ds_to_env(ds, do_extract_answer=do_extract_answer)


if __name__ == "__main__":
    env = load_environment(num_train_examples=500, num_eval_examples=50, seed=42)
    print(f"Environment created with {len(env.dataset)} training examples")
    if env.eval_dataset is not None:
        print(f"and {len(env.eval_dataset)} eval examples")
