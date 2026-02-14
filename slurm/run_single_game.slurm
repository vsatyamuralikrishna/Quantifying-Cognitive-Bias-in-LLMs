#!/bin/bash
#SBATCH --job-name=qcbai-game
#SBATCH --output=slurm/logs/%x_%j.out
#SBATCH --error=slurm/logs/%x_%j.err
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32gb
#SBATCH --gres=gpu:volta:1
#SBATCH --partition=gpu_standard
#SBATCH --account=YOUR_GROUP

# ============================================================
# Run a single game experiment
# University of Arizona HPC - Puma Cluster
#
# Usage:
#   sbatch slurm/run_single_game.slurm prisoners_dilemma
#   sbatch slurm/run_single_game.slurm chicken_game llama3.2:latest
#
# Args:
#   $1 = game key (required)
#   $2 = model name filter (optional)
# ============================================================

GAME=${1:?"Usage: sbatch slurm/run_single_game.slurm <game_key> [model_name]"}
MODEL=${2:-""}

# Number of concurrent async requests per prompt batch.
# Must match OLLAMA_NUM_PARALLEL on the server.
CONCURRENT=${CONCURRENT:-8}

echo "============================================"
echo "QCBAI Experiment"
echo "Job ID:      $SLURM_JOB_ID"
echo "Cluster:     $SLURM_CLUSTER_NAME"
echo "Node:        $HOSTNAME"
echo "Game:        $GAME"
echo "Model:       ${MODEL:-all}"
echo "Concurrent:  $CONCURRENT"
echo "Start:       $(date)"
echo "============================================"

# Load UA HPC modules
module load cuda11/11.8

# Activate environment (micromamba is recommended on UA HPC)
source ~/.bashrc
micromamba activate qcbai 2>/dev/null || true

# Navigate to project root
cd "$SLURM_SUBMIT_DIR" || exit 1

# Ensure Ollama is accessible
export OLLAMA_HOST=${OLLAMA_HOST:-"http://localhost:11434"}

# Generate prompts if not already present
if [ ! -d "prompts/$GAME" ]; then
    echo "Generating prompts for $GAME..."
    python generate_prompts.py --game "$GAME"
fi

# Run the experiment with async concurrency
if [ -n "$MODEL" ]; then
    python main.py --game "$GAME" --model "$MODEL" --runs 100 --temperature 0.7 --concurrent $CONCURRENT
else
    python main.py --game "$GAME" --runs 100 --temperature 0.7 --concurrent $CONCURRENT
fi

echo "============================================"
echo "End:         $(date)"
echo "============================================"
