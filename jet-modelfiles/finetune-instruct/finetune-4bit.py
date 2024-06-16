from trl import SFTTrainer
from unsloth import is_bfloat16_supported
from transformers import TrainingArguments
from datasets import load_dataset
from unsloth.chat_templates import get_chat_template
from unsloth import FastLanguageModel
import torch

model_name = "unsloth/llama-3-8b-Instruct-bnb-4bit"
# model_name = "../llama3-8b/Llama-3-8b-tagalog-v1.Q6_K.gguf"
dataset_name = "./bactrian-x-instruct-clean.json"
model_output_file = "llama3_jet_lora_model"

max_seq_length = 2048  # Choose any! We auto support RoPE Scaling internally!
dtype = None  # None for auto detection. Float16 for Tesla T4, V100, Bfloat16 for Ampere+
# Use 4bit quantization to reduce memory usage. Can be False.
load_in_4bit = True


print(f"Loading model to finetune: {model_name}")
model, tokenizer = FastLanguageModel.from_pretrained(
    # Choose ANY! eg teknium/OpenHermes-2.5-Mistral-7B
    model_name=model_name,
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
    # token = "hf_...", # use one if using gated models like meta-llama/Llama-2-7b-hf
)


print(f"Loading lora model using PEFT")
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # Choose any number > 0 ! Suggested 8, 16, 32, 64, 128
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj",],
    lora_alpha=16,
    lora_dropout=0,  # Supports any, but = 0 is optimized
    bias="none",    # Supports any, but = "none" is optimized
    # [NEW] "unsloth" uses 30% less VRAM, fits 2x larger batch sizes!
    use_gradient_checkpointing="unsloth",  # True or "unsloth" for very long context
    random_state=3407,
    use_rslora=False,  # We support rank stabilized LoRA
    loftq_config=None,  # And LoftQ
)


# alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

# ### Instruction:
# {}

# ### Input:
# {}

# ### Response:
# {}"""

llama3_prompt = "\nHuman: {}\nAssistant: {}"

EOS_TOKEN = tokenizer.eos_token  # Must add EOS_TOKEN
print(f"EOS_TOKEN: {EOS_TOKEN}")


def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    inputs = examples["input"]
    outputs = examples["output"]
    texts = []
    for instruction, input, output in zip(instructions, inputs, outputs):
        prompt = instruction
        if input:
            prompt += f"\n{input}"
        # Must add EOS_TOKEN, otherwise your generation will go on forever!
        text = llama3_prompt.format(prompt, output) + EOS_TOKEN
        texts.append(text)
    return {"text": texts, }


print(f"Loading dataset: {dataset_name}")
dataset = load_dataset(dataset_name, split="train")
dataset = dataset.map(formatting_prompts_func, batched=True,)


# unsloth_template = \
#     "{{ bos_token }}"\
#     "{{ 'You are a helpful assistant to the user\n' }}"\
#     "{% endif %}"\
#     "{% for message in messages %}"\
#     "{% if message['role'] == 'user' %}"\
#     "{{ '>>> User: ' + message['content'] + '\n' }}"\
#     "{% elif message['role'] == 'assistant' %}"\
#     "{{ '>>> Assistant: ' + message['content'] + eos_token + '\n' }}"\
#     "{% endif %}"\
#     "{% endfor %}"\
#     "{% if add_generation_prompt %}"\
#     "{{ '>>> Assistant: ' }}"\
#     "{% endif %}"
# unsloth_eos_token = "eos_token"

# if False:
#     tokenizer = get_chat_template(
#         tokenizer,
#         # You must provide a template and EOS token
#         chat_template=(unsloth_template, unsloth_eos_token,),
#         mapping={"role": "from", "content": "value",
#                  "user": "human", "assistant": "gpt"},  # ShareGPT style
#         map_eos_token=True,  # Maps <|im_end|> to </s> instead
#     )

print(f"Start training")
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    packing=False,  # Can make training 5x faster for short sequences.
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=60,
        learning_rate=2e-4,
        fp16=not is_bfloat16_supported(),
        bf16=is_bfloat16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="outputs",
    ),
)


print(f"Saving to: {model_output_file}")
model.save_pretrained(model_output_file)  # Local saving
# model.push_to_hub("your_name/lora_model", token = "...") # Online saving
print("DONE TRAINING!!")
