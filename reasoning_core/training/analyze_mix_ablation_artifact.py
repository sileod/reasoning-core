import argparse
import shutil
import tempfile
from pathlib import Path

from reasoning_core.training.analyze_mix_ablation import (
    analyze_log_path,
    format_recommendations,
)


def main():
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--artifact", help="W&B artifact ref, e.g. entity/rc-sft/taskmix-windows:latest")
    source.add_argument("--run", help="W&B run path, e.g. entity/rc-sft/run_id; uses latest taskmix artifact")
    source.add_argument("--log_path", help="Local taskmix JSONL path")
    parser.add_argument("--artifact_name", default="taskmix-windows")
    parser.add_argument("--baseline", choices=("power", "poly"), default="power")
    parser.add_argument("--power_skip", type=int, default=10)
    parser.add_argument("--min_count", type=int, default=2)
    parser.add_argument("--top_k", type=int, default=20)
    parser.add_argument("--csv", default="", help="Optional path to write full result CSV")
    args = parser.parse_args()

    tmp_dir = None
    try:
        if args.log_path:
            log_path = Path(args.log_path)
        else:
            log_path, tmp_dir = _download_log(args)
        result = analyze_log_path(
            log_path,
            baseline=args.baseline,
            power_skip=args.power_skip,
            min_count=args.min_count,
        )
        print(format_recommendations(result, top_k=args.top_k))
        if args.csv:
            result.to_csv(args.csv, index=False)
    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)


def _download_log(args):
    import wandb

    api = wandb.Api()
    tmp_dir = tempfile.mkdtemp(prefix="taskmix_artifact_")
    artifact = api.artifact(args.artifact) if args.artifact else _latest_run_artifact(api, args)
    root = Path(artifact.download(root=tmp_dir))
    matches = sorted(root.rglob("taskmix_windows.jsonl"))
    if not matches:
        matches = sorted(root.rglob("*.jsonl"))
    if not matches:
        raise FileNotFoundError(f"No JSONL taskmix log found in {artifact.name}")
    return matches[0], tmp_dir


def _latest_run_artifact(api, args):
    artifacts = [
        artifact for artifact in api.run(args.run).logged_artifacts()
        if artifact.type == "taskmix" and artifact.name.startswith(args.artifact_name)
    ]
    if not artifacts:
        raise ValueError(f"No taskmix artifact found on run {args.run}")
    return sorted(artifacts, key=lambda artifact: artifact.updated_at or "")[-1]


if __name__ == "__main__":
    main()
