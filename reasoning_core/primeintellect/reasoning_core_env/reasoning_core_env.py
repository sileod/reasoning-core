import pandas as pd
from datasets import Dataset, load_dataset, DatasetDict, get_dataset_split_names
import verifiers as vf
import reasoning_gym as rg
from reasoning_core import score_answer
from easydict import EasyDict as edict

DEFAULT_SYSTEM_PROMPT = rg.utils.SYSTEM_PROMPTS["DeepSeekZero"]
DEFAULT_DATASET_NAME = "reasoning-core/formal-reasoning-env"
DEFAULT_ALLOWED_MODES = ("instruct", "few_shot")


def extract_answer(s, tag="answer"):
    if s.strip().startswith('<prompt>'):
        s = s.split('</prompt>')[-1]
    return s.split(f'<{tag}>')[-1].split(f'</{tag}>')[0]


def rc_ds_to_env(
    ds, 
    system_prompt=DEFAULT_SYSTEM_PROMPT, 
    do_extract_answer=True,
    allowed_modes=DEFAULT_ALLOWED_MODES,
):
    """
    Convert Dataset or DatasetDict into a verifiers SingleTurnEnv.
    Properly handles DatasetDict by separating train and eval splits.
    """
    if isinstance(ds, DatasetDict):
        # Main dataset (used for training/sampling)
        if "train" in ds:
            main_ds = ds["train"]
        else:
            main_ds = ds[list(ds.keys())[0]]  # fallback

        # Evaluation dataset
        eval_ds = None
        for split_name in ["test", "validation", "eval", "dev"]:
            if split_name in ds:
                eval_ds = ds[split_name]
                break
    else:
        # If a single Dataset is passed
        main_ds = ds
        eval_ds = None

    def filter_modes(dataset):
        if allowed_modes and "mode" in dataset.column_names:
            return dataset.filter(lambda example: example.get("mode") in allowed_modes)
        return dataset

    main_ds = filter_modes(main_ds)
    if eval_ds is not None:
        eval_ds = filter_modes(eval_ds)

    # Process main dataset
    dataset = main_ds.rename_columns({"prompt": "question"})

    def parse_entry(example):
        entry = edict(
            metadata=example.get('metadata', {}),
            answer=example['answer']
        )
        return {'info': entry}

    dataset = dataset.map(parse_entry)

    # Process eval dataset if it exists
    eval_dataset = None
    if eval_ds is not None:
        eval_dataset = eval_ds.rename_columns({"prompt": "question"})
        eval_dataset = eval_dataset.map(parse_entry)

    def score_answer_vf(prompt, completion, info) -> float:
        answer = completion[0]['content']
        if do_extract_answer:
            answer = extract_answer(answer)
        return score_answer(answer, edict(info))

    rubric = vf.Rubric(funcs=[score_answer_vf])

    env = vf.SingleTurnEnv(
        dataset=dataset,
        eval_dataset=eval_dataset,      # ← Important: use eval_dataset
        rubric=rubric,
        system_prompt=system_prompt
    )
    return env


def load_environment(
    num_train_examples: int = 500,
    num_eval_examples: int = 50,
    do_extract_answer=True,
    dataset_name: str = DEFAULT_DATASET_NAME,
    allowed_modes=DEFAULT_ALLOWED_MODES,
    seed: int = 0,
) -> vf.SingleTurnEnv:
    """
    Load the dataset and return a ready-to-use SingleTurnEnv.
    """
    split_names = get_dataset_split_names(dataset_name)

    def load_stream(split: str, n: int, skip: int = 0) -> Dataset:
        stream = load_dataset(dataset_name, split=split, streaming=True).shuffle(seed=seed)
        if skip:
            stream = stream.skip(skip)
        return Dataset.from_list(list(stream.take(n)))

    if "test" in split_names:
        eval_split = "test"
    elif "validation" in split_names:
        eval_split = "validation"
    else:
        eval_split = None

    ds = DatasetDict({"train": load_stream("train", num_train_examples)})
    if eval_split is not None:
        ds["test"] = load_stream(eval_split, num_eval_examples)
    else:
        ds["test"] = load_stream("train", num_eval_examples, skip=num_train_examples)

    return rc_ds_to_env(ds, do_extract_answer=do_extract_answer, allowed_modes=allowed_modes)


# ============================
# Usage Example
# ============================

if __name__ == "__main__":
    env = load_environment(
        num_train_examples=500,
        num_eval_examples=50,
        seed=42
    )
    
    print(f"Environment created with {len(env.dataset)} training examples")
    if env.eval_dataset is not None:
        print(f"and {len(env.eval_dataset)} eval examples")
