with open("data/training/terraria_training_pairs.jsonl", "r", encoding="utf-8") as f:
    count = sum(1 for line in f if line.strip())

print(f"Total training pairs: {count}")