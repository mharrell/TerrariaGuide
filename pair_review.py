import json
import os
import random


def review_pairs(jsonl_path):
    # Load all pairs
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        pairs = [json.loads(line) for line in f if line.strip()]

    print(f"Total pairs: {len(pairs)}")
    print("Sampling 200 random pairs for review.")
    print("Commands: [A]ccept, [R]eject, [E]dit answer, [S]kip, [Q]uit\n")

    sample = random.sample(pairs, min(200, len(pairs)))

    accepted = []
    rejected = []
    edited = []
    skipped = []

    for i, pair in enumerate(sample):
        print(f"\n{'=' * 60}")
        print(f"Pair {i + 1}/200")
        print(f"{'=' * 60}")
        print(f"Q: {pair['instruction']}")
        print(f"\nA: {pair['output'][:500]}")
        if len(pair['output']) > 500:
            print("... [truncated]")
        print(f"{'=' * 60}")

        while True:
            choice = input("\n[A]ccept / [R]eject / [E]dit / [S]kip / [Q]uit: ").strip().lower()

            if choice == 'a':
                accepted.append(pair)
                break
            elif choice == 'r':
                reason = input("Reason (optional): ").strip()
                pair['reject_reason'] = reason
                rejected.append(pair)
                break
            elif choice == 'e':
                print(f"Current answer: {pair['output']}")
                new_answer = input("New answer (or press Enter to keep): ").strip()
                if new_answer:
                    pair['output'] = new_answer
                edited.append(pair)
                break
            elif choice == 's':
                skipped.append(pair)
                break
            elif choice == 'q':
                print("\nQuitting review early...")
                break
            else:
                print("Invalid choice, try again.")

        if choice == 'q':
            break

    # Save review results
    os.makedirs("data/review", exist_ok=True)

    with open("data/review/accepted.json", 'w', encoding='utf-8') as f:
        json.dump(accepted + edited, f, indent=2, ensure_ascii=False)

    with open("data/review/rejected.json", 'w', encoding='utf-8') as f:
        json.dump(rejected, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"REVIEW SUMMARY")
    print(f"{'=' * 60}")
    print(f"Accepted: {len(accepted)}")
    print(f"Edited:   {len(edited)}")
    print(f"Rejected: {len(rejected)}")
    print(f"Skipped:  {len(skipped)}")

    if len(accepted) + len(rejected) > 0:
        accept_rate = len(accepted) / (len(accepted) + len(rejected)) * 100
        print(f"Accept rate: {accept_rate:.1f}%")

    # Common rejection reasons
    if rejected:
        print(f"\nRejection reasons:")
        reasons = [p.get('reject_reason', 'none') for p in rejected if p.get('reject_reason')]
        for r in reasons:
            print(f"  - {r}")

    print(f"\nResults saved to data/review/")


if __name__ == "__main__":
    review_pairs("data/training/terraria_training_pairs.jsonl")