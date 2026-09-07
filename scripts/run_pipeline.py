import os
import sys
import argparse
import subprocess

def run_step(cmd_list, description):
    print(f"\n==========================================")
    print(f">> {description}")
    print(f"Command: {' '.join(cmd_list)}")
    print(f"==========================================")
    res = subprocess.run(cmd_list, check=True)
    if res.returncode != 0:
        print(f"Error in step: {description}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="End-to-end RecoverAI Pipeline Runner")
    parser.add_argument("--patients", type=int, default=1000, help="Number of patients")
    parser.add_argument("--observations", type=int, default=50000, help="Target observation count")
    args = parser.parse_args()

    python_exe = sys.executable

    # Step 1: Generate Synthetic Dataset
    run_step(
        [python_exe, "-u", "scripts/generate_data.py", "--patients", str(args.patients), "--observations", str(args.observations)],
        "Step 1: Generating Realistic Multi-Trajectory Synthetic Dataset"
    )

    # Step 2: Train Model & Register in Registry
    run_step(
        [python_exe, "-u", "scripts/train_model.py"],
        "Step 2: Training Explainable Risk Machine Learning Model"
    )

    # Step 3: Run Cohort Benchmark Evaluation
    run_step(
        [python_exe, "-u", "scripts/run_evaluation.py"],
        "Step 3: Benchmarking RecoverAI against Single-Threshold Baseline"
    )

    # Step 4: Seed SQLite Database
    run_step(
        [python_exe, "-u", "scripts/seed_database.py"],
        "Step 4: Seeding SQLite Database with Patients, Baselines, Tasks & Audit Logs"
    )

    print("\n[SUCCESS] End-to-end RecoverAI pipeline completed successfully!")
    print("Run `uvicorn backend.app.main:app --port 8000` to start the backend API server.")

if __name__ == "__main__":
    main()
