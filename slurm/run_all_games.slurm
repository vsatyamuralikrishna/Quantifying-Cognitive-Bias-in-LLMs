#!/bin/bash
#SBATCH --job-name=qcbai-games
#SBATCH --partition=gpu_standard
#SBATCH --account=tylermillhouse
#SBATCH --ntasks=28
#SBATCH --nodes=1
#SBATCH --gres=gpu:2
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=4-00:00:00
#SBATCH -e slurm/logs/%x_%A_%a.err
#SBATCH -o slurm/logs/%x_%A_%a.out
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=anudeepappikatla@arizona.edu
#SBATCH --array=0-48

# ============================================================
# SLURM Job Array: 7 games × 7 models = 49 jobs (indices 0-48)
# University of Arizona HPC - Puma Cluster
#
# Each array task runs ONE model on ONE game, so that:
#   - Each model gets full GPU VRAM (no model swapping)
#   - Async concurrent requests maximize throughput
#   - Jobs are independent and can run in parallel across nodes
#
# Array index mapping (index = game_idx * 7 + model_idx):
#   Games (0-6):
#     0=prisoners_dilemma  1=dictator_game       2=chicken_game
#     3=public_goods_game  4=public_goods_game_boolean
#     5=ultimatum_game     6=trust_game
#
#   Models (0-6):
#     0=llama3.2:latest         (2 GB)
#     1=mistral:latest          (4.1 GB)
#     2=llama3.3:latest         (42 GB)
#     3=mistral-small3.1:latest (15 GB)
#     4=phi4:latest             (9.1 GB)
#     5=gemma3:27b              (17 GB)
#     6=qwen2.5:32b             (19 GB)
#
# Usage:
#   sbatch slurm/run_all_games.slurm           # all 49 jobs
#   sbatch --array=0-6  slurm/run_all_games.slurm  # all models, game 0 only
#   sbatch --array=0,7,14,21,28,35,42 slurm/run_all_games.slurm  # model 0, all games
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

MODELS=(
    "llama3.2:latest"
    "mistral:latest"
    "llama3.3:latest"
    "mistral-small3.1:latest"
    "phi4:latest"
    "gemma3:27b"
    "qwen2.5:32b"
)

NUM_MODELS=${#MODELS[@]}

# Decode 2D index: index = game_idx * NUM_MODELS + model_idx
GAME_IDX=$(( SLURM_ARRAY_TASK_ID / NUM_MODELS ))
MODEL_IDX=$(( SLURM_ARRAY_TASK_ID % NUM_MODELS ))

GAME=${GAMES[$GAME_IDX]}
MODEL=${MODELS[$MODEL_IDX]}
CONCURRENT=${CONCURRENT:-8}

echo "============================================"
echo "QCBAI Experiment"
echo "Job ID:       $SLURM_JOB_ID"
echo "Array Index:  $SLURM_ARRAY_TASK_ID"
echo "Game Index:   $GAME_IDX  → $GAME"
echo "Model Index:  $MODEL_IDX → $MODEL"
echo "Cluster:      $SLURM_CLUSTER_NAME"
echo "Node:         $HOSTNAME"
echo "Concurrent:   $CONCURRENT"
echo "Start:        $(date)"
echo "============================================"

# ---- Load modules ----
module load python/3.11
module load cuda11 cuda11-sdk cuda11-dnn
module load micromamba

export CUDA_DIR=/opt/ohpc/pub/apps/cuda/11.8/
export XLA_FLAGS=--xla_gpu_cuda_data_dir=/opt/ohpc/pub/apps/cuda/11.8/

# ---- Environment variables ----
export HF_HOME=/groups/tylermillhouse/huggingface
export TRANSFORMERS_CACHE=/groups/tylermillhouse/huggingface
export HF_DATASETS_CACHE=/groups/tylermillhouse/huggingface/datasets

# ---- Activate micromamba environment ----
eval "$(micromamba shell hook --shell bash)"
micromamba activate /groups/tylermillhouse/micromamba_envs/myenv

echo ""
python3 --version
nvidia-smi -L
echo ""

# ---- Start Ollama server via Singularity ----
echo "Starting Ollama server via Singularity..."
export OLLAMA_NUM_PARALLEL=$CONCURRENT

singularity exec --nv \
  --home /groups/tylermillhouse/ollama/home \
  -B /groups/tylermillhouse/ollama/models:/root/.ollama \
  /groups/tylermillhouse/ollama/image/ollama.sif \
  ollama serve &

OLLAMA_PID=$!
sleep 10

# Verify Ollama is running
echo "Testing Ollama connection..."
curl -s http://localhost:11434/api/tags | head -c 200
echo ""

export OLLAMA_HOST="http://localhost:11434"

# ---- Navigate to project directory ----
PROJECT_DIR="/groups/tylermillhouse/capstoneproject/Quantifying-Cognitive-Bias-in-LLMs"
cd "$PROJECT_DIR" || exit 1

# ---- Generate prompts if not present ----
if [ ! -d "prompts/$GAME" ]; then
    echo "Generating prompts for $GAME..."
    python3 generate_prompts.py --game "$GAME"
fi

# ---- Run experiment (single model, single game) ----
echo ""
echo "Running experiment: $GAME with model $MODEL"
echo "============================================"

python3 main.py \
    --game "$GAME" \
    --model "$MODEL" \
    --runs 100 \
    --temperature 0.7 \
    --concurrent $CONCURRENT

# ---- Cleanup ----
echo ""
echo "Stopping Ollama server..."
kill $OLLAMA_PID 2>/dev/null || kill $(pgrep ollama) 2>/dev/null || true

echo "============================================"
echo "End:          $(date)"
echo "============================================"
