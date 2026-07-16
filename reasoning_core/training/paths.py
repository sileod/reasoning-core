import os
import tempfile
from pathlib import Path


HOME = Path.home().resolve()
RC_HOME = Path(os.environ.get("RC_HOME", HOME / ".reasoning_core")).expanduser().resolve()


def home_path(path, *, name="path"):
    path = Path(path).expanduser().resolve()
    if path != HOME and HOME not in path.parents:
        raise ValueError(f"{name} must be inside ~ ({HOME}), got {path}")
    return path


home_path(RC_HOME, name="RC_HOME")
RUNS_HOME = RC_HOME / "runs"
CACHE_HOME = RC_HOME / "cache"
TMP_HOME = RC_HOME / "tmp"
LOCKS_HOME = RC_HOME / "locks"


def env_path(name, default):
    return home_path(os.environ.get(name, default), name=name)


def configure_runtime_env():
    tmp = env_path("RC_TMP", TMP_HOME)
    hf = env_path("HF_CACHE", CACHE_HOME / "huggingface")
    for path in (tmp, hf):
        path.mkdir(parents=True, exist_ok=True)
    os.environ.update({
        "HF_HOME": str(hf),
        "HF_DATASETS_CACHE": str(hf / "datasets"),
        "TORCHINDUCTOR_CACHE_DIR": str(tmp / "torchinductor"),
        "TRITON_CACHE_DIR": str(tmp / "triton"),
        "WANDB_DIR": str(RUNS_HOME / "wandb"),
        "WANDB_CACHE_DIR": str(CACHE_HOME / "wandb"),
        "TMPDIR": str(tmp),
        "TEMP": str(tmp),
        "TMP": str(tmp),
        "TOKENIZERS_PARALLELISM": "false",
    })
    tempfile.tempdir = str(tmp)
