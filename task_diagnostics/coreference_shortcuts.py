import argparse

from reasoning_core.tasks.coreference import (
    Coreference,
    CoreferenceConfig,
    generate_balanced_batch,
    shortcut_report,
)


def _print_report(title, rows):
    print(title)
    print("heuristic\tstratum\tn\taccuracy\tcoverage")
    for row in rows:
        acc = "NA" if row["accuracy"] is None else f"{row['accuracy']:.3f}"
        print(
            f"{row['heuristic']}\t{row['stratum']}\t{row['n']}\t"
            f"{acc}\t{row['coverage']:.3f}"
        )
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--n", type=int, default=1000)
    parser.add_argument("--oversample", type=int, default=20)
    parser.add_argument("--n-ambiguous-mentions", type=int, default=0)
    parser.add_argument("--n-constraints", type=int, default=0)
    parser.add_argument("--n-rules", type=int, default=0)
    parser.add_argument("--n-identity-links", type=int, default=0)
    parser.add_argument("--n-state-changes", type=int, default=0)
    args = parser.parse_args()

    overrides = dict(
        n_ambiguous_mentions=args.n_ambiguous_mentions,
        n_constraints=args.n_constraints,
        n_rules=args.n_rules,
        n_identity_links=args.n_identity_links,
        n_state_changes=args.n_state_changes,
    )

    task = Coreference(CoreferenceConfig(balanced_generation=False, **overrides))
    raw = [task.generate_raw_candidate() for _ in range(args.n)]
    _print_report("unbalanced raw generation", shortcut_report(raw))

    task = Coreference(CoreferenceConfig(balanced_generation=True,
                                         oversample=args.oversample,
                                         **overrides))
    balanced = generate_balanced_batch(task, args.n, oversample=args.oversample,
                                       eps=task.config.shortcut_eps)
    _print_report("balanced subsample", shortcut_report(balanced))


if __name__ == "__main__":
    main()
