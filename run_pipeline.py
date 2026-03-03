import subprocess
import sys
import os

SCRIPTS = [
    "data_cleaner.py",
    "pair_generator.py",
    "crafting_recovery.py",
    "pair_count.py",
]

TRAINING_FILE = "data/training/terraria_training_pairs.jsonl"


def run_pipeline():
    # Delete existing training file to start fresh
    if os.path.exists(TRAINING_FILE):
        os.remove(TRAINING_FILE)
        print(f"Deleted {TRAINING_FILE}")

    print("=" * 50)

    for script in SCRIPTS:
        print(f"\nRunning {script}...")
        print("-" * 50)
        result = subprocess.run(
            [sys.executable, script],
            capture_output=False
        )
        if result.returncode != 0:
            print(f"\nERROR: {script} failed with exit code {result.returncode}")
            print("Pipeline stopped.")
            sys.exit(1)
        print(f"{script} completed successfully.")
        print("=" * 50)

    print("\nPipeline complete!")


if __name__ == "__main__":
    run_pipeline()