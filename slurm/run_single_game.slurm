#!/bin/bash
#SBATCH --job-name=qcbai-game
#SBATCH --output=slurm/logs/%x_%j.out
#SBATCH --error=slurm/logs/%x_%j.err
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu

# ============================================================
# Run a single game experiment
#
# Usage:
#   sbatch slurm/run_single_game.slurm prisoners_dilemma
#   sbatch slurm/run_single_game.slurm chicken_game llama3.2:latest
#
# Args:
#   $1 = game key (required)
#   $2 = model name filter (optional)
# ============================================================

GAME=${1:?"Usage: sbatch run_single_game.slurm <game_key> [model_name]"}
MODEL=${2:-""}

echo "============================================"
echo "Job ID:    $SLURM_JOB_ID"
echo "Node:      $HOSTNAME"
echo "Game:      $GAME"
echo "Model:     ${MODEL:-all}"
echo "Start:     $(date)"
echo "============================================"

# Load modules (adjust for your HPC environment)
module load anaconda3 2>/dev/null || true
module load cuda 2>/dev/null || true

# Activate conda environment (adjust name as needed)
source activate qcbai 2>/dev/null || conda activate qcbai 2>/dev/null || true

# Navigate to project root
cd $SLURM_SUBMIT_DIR/..

# Ensure Ollama is accessible
export OLLAMA_HOST=${OLLAMA_HOST:-"http://localhost:11434"}

# ---- Concurrency settings ----
# Number of parallel requests Ollama handles simultaneously.
# Must match --workers passed to main.py. Tune based on GPU VRAM:
#   8  = safe for most GPUs (24GB+)
#   4  = conservative (16GB)
#   16 = aggressive (48GB+ A100/H100)
WORKERS=${WORKERS:-8}
export OLLAMA_NUM_PARALLEL=$WORKERS

echo "Workers:   $WORKERS (OLLAMA_NUM_PARALLEL=$OLLAMA_NUM_PARALLEL)"

# Generate prompts if not already present
if [ ! -d "prompts/$GAME" ]; then
    echo "Generating prompts for $GAME..."
    python generate_prompts.py --game "$GAME"
fi

# Run the experiment with concurrent workers
if [ -n "$MODEL" ]; then
    python main.py --game "$GAME" --model "$MODEL" --runs 100 --temperature 0.7 --workers $WORKERS
else
    python main.py --game "$GAME" --runs 100 --temperature 0.7 --workers $WORKERS
fi

echo "============================================"
echo "End:       $(date)"
echo "============================================"
