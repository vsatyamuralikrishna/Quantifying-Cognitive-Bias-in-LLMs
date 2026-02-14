#!/bin/bash
# ============================================================
# Convenience script to submit all game experiments
#
# Usage:
#   bash slurm/submit_all.sh                    # all models
#   bash slurm/submit_all.sh llama3.2:latest    # specific model
# ============================================================

set -e

MODEL=${1:-""}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Create log directory
mkdir -p slurm/logs

echo "Project: $PROJECT_DIR"
echo "Model:   ${MODEL:-all}"
echo ""

# Step 1: Generate all prompts first (fast, runs on login node)
echo "Generating prompts for all games..."
python generate_prompts.py
echo ""

# Step 2: Submit the job array (one job per game)
if [ -n "$MODEL" ]; then
    echo "Submitting SLURM job array with model filter: $MODEL"
    sbatch slurm/run_all_games.slurm "$MODEL"
else
    echo "Submitting SLURM job array for all models"
    sbatch slurm/run_all_games.slurm
fi

echo ""
echo "Jobs submitted. Monitor with: squeue -u \$USER"
echo "View logs in: slurm/logs/"
