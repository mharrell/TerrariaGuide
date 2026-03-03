import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"
import torch
torch._dynamo.disable()

from unsloth import FastLanguageModel

MODEL_DIR = "models/terraria-guide"
MAX_SEQ_LENGTH = 1024

print("Loading model...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_DIR,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,
    load_in_4bit=True,
)
FastLanguageModel.for_inference(model)
print("Model loaded! Type 'quit' to exit.\n")

while True:
    question = input("Ask a Terraria question: ").strip()
    if question.lower() == "quit":
        break
    if not question:
        continue

    prompt = f"""### Instruction:
{question}

### Response:
"""

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Strip the prompt from the response
    response = response[len(prompt):].strip()

    print(f"\nAnswer: {response}\n")
    print("-" * 50 + "\n")