import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"
import torch
torch._dynamo.disable()
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
import torch._dynamo
torch._dynamo.config.suppress_errors = True

# ----------------------------------------------------------------
# Model config
# ----------------------------------------------------------------
MAX_SEQ_LENGTH = 384  # Keep low for 8GB VRAM
MODEL_NAME = "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit"
OUTPUT_DIR = "models/terraria-guide"

# ----------------------------------------------------------------
# Load base model
# ----------------------------------------------------------------
print("Loading base model...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,          # Auto-detect
    load_in_4bit=True,   # Essential for 8GB VRAM
)

# ----------------------------------------------------------------
# Apply LoRA
# ----------------------------------------------------------------
model = FastLanguageModel.get_peft_model(
    model,
    r=4,                          # LoRA rank — real low
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",  # Saves VRAM
    random_state=42,
)

# ----------------------------------------------------------------
# Format dataset
# ----------------------------------------------------------------
def format_prompt(example):
    return {
        "text": f"""### Instruction:
{example['instruction']}

### Response:
{example['output']}<|end_of_text|>"""
    }

print("Loading dataset...")
dataset = load_dataset(
    "json",
    data_files="data/training/terraria_training_pairs.jsonl",
    split="train"
)
dataset = dataset.map(format_prompt)
dataset = dataset.filter(lambda x: len(x["text"]) < 2000)
print(f"Dataset size: {len(dataset)} pairs")

# ----------------------------------------------------------------
# Training arguments
# ----------------------------------------------------------------
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=1,       # Must be 1 for 8GB
    gradient_accumulation_steps=4,       # Effective batch size = 8
    warmup_steps=50,
    num_train_epochs=1,
    learning_rate=2e-4,
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    logging_steps=25,
    save_steps=500,
    save_total_limit=2,
    optim="adamw_8bit",                  # 8-bit optimizer saves VRAM
    weight_decay=0.01,
    lr_scheduler_type="cosine",
    seed=42,
    report_to="none",
    torch_compile=False,
)

# ----------------------------------------------------------------
# Train
# ----------------------------------------------------------------
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    dataset_num_proc=2,
    args=training_args,
    packing=False,
)

print("Starting training...")
trainer.train()

# ----------------------------------------------------------------
# Save
# ----------------------------------------------------------------
print("Saving model...")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"Model saved to {OUTPUT_DIR}")
