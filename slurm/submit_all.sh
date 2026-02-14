#!/bin/bash
# ============================================================
# Convenience script to submit all game × model experiments
# University of Arizona HPC - Puma Cluster
#
# This submits ONE SLURM job array that spawns 49 tasks:
#   7 games × 7 models = 49 independent jobs
#
# Each task runs a single (game, model) pair with its own
# Ollama Singularity server, maximizing GPU utilization
# and concurrent inference.
#
# Models (indices 0-6):
#   0: llama3.2:latest         (2 GB)
#   1: mistral:latest          (4.1 GB)
#   2: llama3.3:latest         (42 GB)
#   3: mistral-small3.1:latest (15 GB)
#   4: phi4:latest             (9.1 GB)
#   5: gemma3:27b              (17 GB)
#   6: qwen2.5:32b             (19 GB)
#
# Usage:
#   bash slurm/submit_all.sh                # all 49 jobs (7 games × 7 models)
#   bash slurm/submit_all.sh --games-only   # array 0-6 (all models, game 0)
#   bash slurm/submit_all.sh --test         # single job (game 0, model 0) for testing
# ============================================================

set -e

PROJECT_DIR="/groups/tylermillhouse/capstoneproject/Quantifying-Cognitive-Bias-in-LLMs"
MODE=${1:-"all"}

cd "$PROJECT_DIR"

# Create log directory
mkdir -p slurm/logs

echo "============================================"
echo "QCBAI - Submit All Experiments"
echo "Project: $PROJECT_DIR"
echo "Mode:    $MODE"
echo "============================================"
echo ""

# Step 1: Generate all prompts first (fast, runs on login node)
echo "Step 1: Generating prompts for all games..."
python3 generate_prompts.py
echo ""

# Step 2: Submit the job array
case "$MODE" in
    "--test")
        echo "Step 2: Submitting TEST job (game=prisoners_dilemma, model=llama3.2:latest)"
        sbatch --array=0 slurm/run_all_games.slurm
        ;;
    "--games-only")
        echo "Step 2: Submitting jobs for all 7 models on prisoners_dilemma only"
        sbatch --array=0-6 slurm/run_all_games.slurm
        ;;
    *)
        echo "Step 2: Submitting full job array (49 tasks: 7 games × 7 models)"
        sbatch slurm/run_all_games.slurm
        ;;
esac

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
echo "Array index decoder (index = game_idx * 7 + model_idx):"
echo "  Index  0 = prisoners_dilemma  + llama3.2:latest"
echo "  Index  1 = prisoners_dilemma  + mistral:latest"
echo "  Index  6 = prisoners_dilemma  + qwen2.5:32b"
echo "  Index  7 = dictator_game     + llama3.2:latest"
echo "  Index 48 = trust_game        + qwen2.5:32b"
echo ""
echo "Check allocation usage:"
echo "  va"
echo "============================================"
