import argparse
from datasets import load_dataset, concatenate_datasets


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aux_data", type=str, default=None,
                         help="Path to generated aux_data JSONL. Omit to build a "
                              "main_data-only dataset (used for the no-aux baseline arm).")
    parser.add_argument("--out_dir", type=str, required=True, help="Output directory for Hugging Face dataset")
    args = parser.parse_args()

    print("Loading Magicoder-OSS-Instruct-75K...")
    magicoder_ds = load_dataset("ise-uiuc/Magicoder-OSS-Instruct-75K")["train"]

    print("Formatting Magicoder to ChatML...")
    def format_magicoder(example):
        return {
            "messages": [
                {"role": "user", "content": example["problem"]},
                {"role": "assistant", "content": example["solution"]}
            ]
        }
    magicoder_formatted = magicoder_ds.map(format_magicoder, remove_columns=magicoder_ds.column_names)

    if args.aux_data:
        print(f"Loading aux data from {args.aux_data}")
        aux_ds = load_dataset("json", data_files=args.aux_data)["train"]
        # remove extra columns from aux_ds (like 'task') so the schemas match
        cols_to_remove = [col for col in aux_ds.column_names if col != "messages"]
        aux_ds = aux_ds.remove_columns(cols_to_remove)
        print("Mixing and shuffling datasets...")
        mixed_ds = concatenate_datasets([magicoder_formatted, aux_ds])
    else:
        print("No --aux_data given: building main_data-only (baseline) dataset...")
        mixed_ds = magicoder_formatted

    mixed_ds = mixed_ds.shuffle(seed=42)
    print(f"Saving dataset ({len(mixed_ds)} rows) to {args.out_dir}")
    mixed_ds.save_to_disk(args.out_dir)


if __name__ == "__main__":
    main()