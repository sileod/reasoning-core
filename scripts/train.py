import argparse

import torch
from datasets import load_from_disk
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTConfig, SFTTrainer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_dir", type=str, required=True)
    parser.add_argument("--output_model", type=str, required=True)
    parser.add_argument("--epochs", type=int, default=1)
    args = parser.parse_args()

    model_id = "HuggingFaceTB/SmolLM2-135M-Instruct"

    steps = ["Loading tokenizer", "Loading model", "Loading dataset", "Formatting dataset", "Starting training"]
    pbar = tqdm(steps, desc="Setup", unit="step")

    pbar.set_description("Loading tokenizer")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    pbar.update(1)

    pbar.set_description("Loading model")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        dtype=torch.bfloat16,
    )
    pbar.update(1)

    pbar.set_description("Loading dataset")
    dataset = load_from_disk(args.dataset_dir)
    pbar.update(1)

    pbar.set_description("Formatting dataset")
    def apply_template(example):
        return {"text": tokenizer.apply_chat_template(
            example["messages"], tokenize=False, add_generation_prompt=False
        )}
    dataset = dataset.map(apply_template, remove_columns=dataset.column_names)
    pbar.update(1)

    pbar.set_description("Starting training")
    pbar.update(1)
    pbar.close()

    print(f"Dataset size: {len(dataset)} rows")
    print(f"Training for {args.epochs} epoch(s)...")

    training_args = SFTConfig(
        output_dir=args.output_model,
        per_device_train_batch_size=8,
        gradient_accumulation_steps=4,
        learning_rate=2e-5,
        logging_steps=10,
        num_train_epochs=args.epochs,
        save_strategy="epoch",
        bf16=True,
        max_length=2048,
    )

    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=dataset,
        args=training_args,
    )

    trainer.train()

    print(f"Saving model to {args.output_model}...")
    trainer.save_model(args.output_model)
    tokenizer.save_pretrained(args.output_model)
    print("Done.")


if __name__ == "__main__":
    main()