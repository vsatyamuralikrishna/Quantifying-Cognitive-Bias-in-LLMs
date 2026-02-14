#!/bin/bash
# ============================================================
# Convenience script to submit all game experiments
# University of Arizona HPC - Puma Cluster
#
# Usage:
#   bash slurm/submit_all.sh                    # all models
#   bash slurm/submit_all.sh llama3.2:latest    # specific model
#
# Prerequisites:
#   1. Ollama server must be running (sbatch slurm/start_ollama.slurm)
#   2. Set OLLAMA_HOST to the server node hostname
#   3. Update --account in SLURM scripts with your PI group
# ============================================================

set -e

MODEL=${1:-""}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Create log directory
mkdir -p slurm/logs

echo "============================================"
echo "QCBAI - Submit All Games"
echo "Project: $PROJECT_DIR"
echo "Model:   ${MODEL:-all}"
echo "============================================"
echo ""

# Step 1: Generate all prompts first (fast, runs on login node)
echo "Step 1: Generating prompts for all games..."
python generate_prompts.py
echo ""

# Step 2: Submit the job array (one job per game)
if [ -n "$MODEL" ]; then
    echo "Step 2: Submitting SLURM job array with model filter: $MODEL"
    sbatch slurm/run_all_games.slurm "$MODEL"
else
    echo "Step 2: Submitting SLURM job array for all models"
    sbatch slurm/run_all_games.slurm
fi

echo ""
echo "============================================"
echo "Jobs submitted successfully."
echo ""
echo "Monitor with:"
echo "  squeue -u \$USER"
echo "  squeue -r --job <job_id>"
echo ""
echo "View logs:"
echo "  cat slurm/logs/qcbai-games_<jobid>_<arrayidx>.out"
echo ""
echo "Check allocation usage:"
echo "  va"
echo "============================================"
