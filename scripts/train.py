import argparse
import torch
from datasets import load_from_disk
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from trl import SFTTrainer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_dir", type=str, required=True, help="Path to mixed dataset")
    parser.add_argument("--output_model", type=str, required=True, help="Directory to save the fine-tuned model")
    parser.add_argument("--epochs", type=int, default=1, help="Number of training epochs")
    args = parser.parse_args()

    model_id = "HuggingFaceTB/SmolLM2-135M"

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id, 
        device_map="auto",
        torch_dtype=torch.bfloat16
    )

    dataset = load_from_disk(args.dataset_dir)

    training_args = TrainingArguments(
        output_dir=args.output_model,
        per_device_train_batch_size=8,
        gradient_accumulation_steps=4,
        learning_rate=2e-5,
        logging_steps=10,
        num_train_epochs=args.epochs,
        save_strategy="epoch",
        bf16=True,
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="messages", # Automatically parses ChatML messages list
        max_seq_length=2048,
        args=training_args,
    )

    print(f"Starting training for {args.epochs} epochs...")
    trainer.train()
    
    print(f"Saving final model to {args.output_model}...")
    trainer.save_model(args.output_model)
    tokenizer.save_pretrained(args.output_model)

if __name__ == "__main__":
    main()
