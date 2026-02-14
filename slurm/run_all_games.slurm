#!/bin/bash
#SBATCH --job-name=qcbai-all
#SBATCH --output=slurm/logs/%x_%A_%a.out
#SBATCH --error=slurm/logs/%x_%A_%a.err
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --array=0-6

# ============================================================
# SLURM Job Array: one job per game (7 games total)
#
# Usage:
#   sbatch slurm/run_all_games.slurm
#   sbatch slurm/run_all_games.slurm llama3.2:latest
#
# Each array index maps to a game:
#   0 = prisoners_dilemma
#   1 = dictator_game
#   2 = chicken_game
#   3 = public_goods_game          (amount version: N=4, ENDOWMENT=20, MULTIPLIER=1.2)
#   4 = public_goods_game_boolean  (binary: Contribute / Not Contribute)
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

echo "============================================"
echo "Job ID:       $SLURM_JOB_ID"
echo "Array Index:  $SLURM_ARRAY_TASK_ID"
echo "Node:         $HOSTNAME"
echo "Game:         $GAME"
echo "Model:        ${MODEL:-all}"
echo "Start:        $(date)"
echo "============================================"

# Load modules
module load anaconda3 2>/dev/null || true
module load cuda 2>/dev/null || true

source activate qcbai 2>/dev/null || conda activate qcbai 2>/dev/null || true

cd $SLURM_SUBMIT_DIR/..

export OLLAMA_HOST=${OLLAMA_HOST:-"http://localhost:11434"}

# ---- Concurrency settings ----
# Number of parallel requests Ollama handles simultaneously.
# Must match --workers passed to main.py. Tune based on GPU VRAM:
#   8  = safe for most GPUs (24GB+)
#   4  = conservative (16GB)
#   16 = aggressive (48GB+ A100/H100)
WORKERS=${WORKERS:-8}
export OLLAMA_NUM_PARALLEL=$WORKERS

echo "Workers:      $WORKERS (OLLAMA_NUM_PARALLEL=$OLLAMA_NUM_PARALLEL)"

# Generate prompts if not present
if [ ! -d "prompts/$GAME" ]; then
    echo "Generating prompts for $GAME..."
    python generate_prompts.py --game "$GAME"
fi

# Run experiment with concurrent workers
if [ -n "$MODEL" ]; then
    python main.py --game "$GAME" --model "$MODEL" --runs 100 --temperature 0.7 --workers $WORKERS
else
    python main.py --game "$GAME" --runs 100 --temperature 0.7 --workers $WORKERS
fi

echo "============================================"
echo "End:          $(date)"
echo "============================================"
