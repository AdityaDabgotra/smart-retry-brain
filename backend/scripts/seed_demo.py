import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import subprocess

STEPS = [
    ("Generating synthetic transactions", ["scripts/generate_synthetic_data.py"]),
    ("Classifying + deciding", ["scripts/classify_pending.py"]),
    ("Generating merchant explanations", ["scripts/generate_explanations.py"]),
    ("Running naive baseline for comparison", ["scripts/run_naive_baseline.py"]),
]


def main():
    for label, cmd in STEPS:
        print(f"\n=== {label} ===")
        result = subprocess.run(["uv", "run", "python", *cmd])
        if result.returncode != 0:
            print(f"Step failed: {label}")
            sys.exit(1)
    print("\nDemo data seeded. Retries fire live via scripts/run_scheduler.py.")


if __name__ == "__main__":
    main()