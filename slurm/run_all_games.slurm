#!/bin/bash
#SBATCH --job-name=qcbai-games
#SBATCH --output=slurm/logs/%x_%A_%a.out
#SBATCH --error=slurm/logs/%x_%A_%a.err
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32gb
#SBATCH --gres=gpu:volta:1
#SBATCH --partition=gpu_standard
#SBATCH --account=YOUR_GROUP
#SBATCH --array=0-6

# ============================================================
# SLURM Job Array: one job per game (7 games total)
# University of Arizona HPC - Puma Cluster
#
# Usage:
#   sbatch slurm/run_all_games.slurm
#   sbatch slurm/run_all_games.slurm llama3.2:latest
#
# Each array index maps to a game:
#   0 = prisoners_dilemma
#   1 = dictator_game
#   2 = chicken_game
#   3 = public_goods_game
#   4 = public_goods_game_boolean
#   5 = ultimatum_game
#   6 = trust_game
# ============================================================

GAMES=(
    "prisoners_dilemma"
    "dictator_game"
    "chicken_game"
    "public_goods_game"
    "public_goods_game_boolean"
    "ultimatum_game"
    "trust_game"
)

GAME=${GAMES[$SLURM_ARRAY_TASK_ID]}
MODEL=${1:-""}

# Number of concurrent async requests per prompt batch.
# Must match OLLAMA_NUM_PARALLEL on the server.
# V100S (32GB): 8 safe for 7B models, 4 for 13B models.
CONCURRENT=${CONCURRENT:-8}

echo "============================================"
echo "QCBAI Experiment"
echo "Job ID:       $SLURM_JOB_ID"
echo "Array Index:  $SLURM_ARRAY_TASK_ID"
echo "Cluster:      $SLURM_CLUSTER_NAME"
echo "Node:         $HOSTNAME"
echo "Game:         $GAME"
echo "Model:        ${MODEL:-all}"
echo "Concurrent:   $CONCURRENT"
echo "Start:        $(date)"
echo "============================================"

# Load UA HPC modules
module load cuda11/11.8

# Activate environment (micromamba is recommended on UA HPC)
# Option A: micromamba (recommended)
source ~/.bashrc
micromamba activate qcbai 2>/dev/null || true

# Option B: fallback to conda if micromamba not available
# conda activate qcbai 2>/dev/null || true

# Navigate to project root
cd "$SLURM_SUBMIT_DIR" || exit 1

# Ensure Ollama is accessible
# UPDATE: Set this to the hostname of your Ollama server job
export OLLAMA_HOST=${OLLAMA_HOST:-"http://localhost:11434"}

# Generate prompts if not present
if [ ! -d "prompts/$GAME" ]; then
    echo "Generating prompts for $GAME..."
    python generate_prompts.py --game "$GAME"
fi

# Run experiment with async concurrency
if [ -n "$MODEL" ]; then
    python main.py --game "$GAME" --model "$MODEL" --runs 100 --temperature 0.7 --concurrent $CONCURRENT
else
    python main.py --game "$GAME" --runs 100 --temperature 0.7 --concurrent $CONCURRENT
fi

echo "============================================"
echo "End:          $(date)"
echo "============================================"
