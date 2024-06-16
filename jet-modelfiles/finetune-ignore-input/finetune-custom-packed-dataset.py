from transformers import AutoModelForCausalLM
from datasets import load_dataset
from trl import SFTTrainer

dataset = load_dataset("your_dataset", split="train")


def formatting_func(example):
    text = f"### Question: {example['question']}\n ### Answer: {example['answer']}"
    return text


trainer = SFTTrainer(
    "facebook/opt-350m",
    train_dataset=dataset,
    packing=True,
    formatting_func=formatting_func,
    max_seq_length=512,
)

trainer.train()
