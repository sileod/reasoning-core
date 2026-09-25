"""python -m reasoning_core.generation {init,generate,collect,submit} --run-dir DIR ...

See reasoning_core/generation/build.py and docs/release.md."""
import argparse

from reasoning_core.generation import build


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m reasoning_core.generation", description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)

    def command(name, help):
        p = sub.add_parser(name, help=help)
        p.add_argument("--run-dir", required=True)
        return p

    def run_settings(p):
        p.add_argument("--version", required=True, help="e.g. rc13; names the staging folder")
        p.add_argument("--roster", help="file with one task per line (default: list_tasks())")
        p.add_argument("--rows-per-task", type=int)
        p.add_argument("--levels", type=int, nargs="+")
        p.add_argument("--batch-size", type=int)
        p.add_argument("--max-tokens", type=int)
        p.add_argument("--dataset", help="Hub staging repo under reasoning-core (default: staging)")
        p.add_argument("--git-rev", help="revision to record when the checkout has no .git")

    run_settings(command("init", "freeze a run's configuration into run.json"))

    p = command("generate", "run this machine's workers until no batch is left")
    p.add_argument("--workers", type=int, help="default: 40%% of CPUs")
    p.add_argument("--lifetime", type=float, default=900, help="seconds before a worker is recycled")
    p.add_argument("--batch-timeout", type=float, default=1200, help="seconds before a batch is killed")
    p.add_argument("--mem-gb", type=float, default=50, help="address-space cap per worker")

    p = command("collect", "upload finished batches to <dataset>/data/<version>/")
    p.add_argument("--loop", action="store_true", help="repeat while generation runs; keep files")
    p.add_argument("--period", type=float, default=1800)
    p.add_argument("--token-file", help="read HF_TOKEN from this file when unset")

    p = command("submit", "freeze the run and queue generate + collect jobs on OAR")
    run_settings(p)
    p.add_argument("--nodes", type=int, default=16)
    p.add_argument("--walltime", default="24:00:00")
    p.add_argument("--collect-walltime", default="24:00:00")
    p.add_argument("--smoke", action="store_true", help="1 node, 2 batches per task, no upload")
    p.add_argument("--home", help="HOME for the jobs (caches for Lean, Metamath, HF)")
    p.add_argument("--token-file")
    p.add_argument("--oarsub", default="oarsub")
    p.add_argument("--dry-run", action="store_true", help="print the oarsub commands only")

    args = ap.parse_args(argv)
    settings = dict(rows_per_task=getattr(args, "rows_per_task", None),
                    levels=getattr(args, "levels", None),
                    batch_size=getattr(args, "batch_size", None),
                    max_tokens=getattr(args, "max_tokens", None),
                    dataset=getattr(args, "dataset", None))
    if args.command == "init":
        build.init(args.run_dir, args.version, roster=args.roster, git_rev=args.git_rev, **settings)
        print(f"{args.run_dir}/run.json")
    elif args.command == "generate":
        build.generate(args.run_dir, workers=args.workers, lifetime=args.lifetime,
                       batch_timeout=args.batch_timeout, mem_gb=args.mem_gb)
    elif args.command == "collect":
        build.collect(args.run_dir, loop=args.loop, period=args.period, token_file=args.token_file)
    else:
        build.submit(args.run_dir, args.version, nodes=args.nodes, walltime=args.walltime,
                     collect_walltime=args.collect_walltime, smoke=args.smoke, home=args.home,
                     token_file=args.token_file, oarsub=args.oarsub, dry_run=args.dry_run,
                     roster=args.roster, git_rev=args.git_rev, **settings)


if __name__ == "__main__":
    main()
