#!/bin/bash
#SBATCH --job-name=qcbai-chicken-gemma27b
#SBATCH --partition=gpu_standard
#SBATCH --account=tylermillhouse
#SBATCH --nodes=4 --ntasks=24
#SBATCH --account=tylermillhouse
#SBATCH --gres=gpu:2
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=20:00:00
#SBATCH -e slurm/logs/%x_%j.err
#SBATCH -o slurm/logs/%x_%j.out
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=anudeepappikatla@arizona.edu

# ============================================================
# Run a single game experiment with ONE specific model.
# Optimized for large models (e.g., llama3.3:latest ~42GB) on Puma.
#
# Usage:
#   RUNS=25 CONCURRENT=3 sbatch slurm/run_single_game.slurm chicken_game llama3.3:latest
# ============================================================

set -euo pipefail

GAME=${1:?"Usage: sbatch slurm/run_single_game.slurm <game_key> <model_name>"}
MODEL=${2:?"Usage: sbatch slurm/run_single_game.slurm <game_key> <model_name>"}

RUNS=${RUNS:-25}
CONCURRENT=${CONCURRENT:-3}

echo "============================================"
echo "QCBAI Experiment"
echo "Job ID:      $SLURM_JOB_ID"
echo "Cluster:     ${SLURM_CLUSTER_NAME:-unknown}"
echo "Node:        $HOSTNAME"
echo "Game:        $GAME"
echo "Model:       $MODEL"
echo "Runs:        $RUNS"
echo "Concurrent:  $CONCURRENT"
echo "CPUs/task:   ${SLURM_CPUS_PER_TASK:-unknown}"
echo "GPUs:        ${SLURM_GPUS:-unknown}"
echo "Start:       $(date)"
echo "============================================"

# ---- Load modules ----
module purge
module load anaconda/2024.06
#module load python/3.11/3.11.4
module load cuda11 cuda11-sdk cuda11-dnn

export CUDA_DIR=/opt/ohpc/pub/apps/cuda/11.8/
export XLA_FLAGS=--xla_gpu_cuda_data_dir=/opt/ohpc/pub/apps/cuda/11.8/

# ---- Cache dirs ----
export HF_HOME=/groups/tylermillhouse/huggingface
export TRANSFORMERS_CACHE=/groups/tylermillhouse/huggingface
export HF_DATASETS_CACHE=/groups/tylermillhouse/huggingface/datasets


# ---- Set project directory ----
PROJECT_DIR="/groups/tylermillhouse/capstoneproject/Quantifying-Cognitive-Bias-in-LLMs"
cd "$PROJECT_DIR" || exit 1

# ---- Activate conda environment ----
source $(conda info --base)/etc/profile.d/conda.sh
conda activate qcbai

# ---- Install/update packages from requirements.txt ----

echo "Installing packages from requirements.txt..."
# Install conda packages first (pre-built binaries, faster)
conda install -c conda-forge -y numpy matplotlib pydantic tqdm pyyaml || true
# Install remaining packages via pip
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install torch

echo ""
python3 --version
echo "Visible GPUs (from Slurm allocation):"
nvidia-smi -L
echo ""
nvidia-smi -L
nvidia-smi

python3 - <<EOF
import torch
print("Torch sees GPUs:", torch.cuda.device_count(), torch.cuda.get_device_name(0))
EOF

# ---- Ensure we only use the 2 GPUs requested by Slurm ----
# (On Puma GPU nodes, there can be 4 GPUs physically.)
export CUDA_VISIBLE_DEVICES=0,1

# ---- Start Ollama server via Singularity ----
echo "Starting Ollama server via Singularity..."
export OLLAMA_NUM_PARALLEL=$CONCURRENT
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_HOST="http://localhost:11434"

singularity exec --nv \
  --home /groups/tylermillhouse/ollama/home \
  -B /groups/tylermillhouse/ollama/models:/root/.ollama \
  /groups/tylermillhouse/ollama/image/ollama.sif \
  ollama serve &

OLLAMA_PID=$!
sleep 12

echo "Testing Ollama connection..."
curl -s http://localhost:11434/api/tags | head -c 300
echo ""
echo ""

# ---- Navigate to project directory ----
PROJECT_DIR="/groups/tylermillhouse/capstoneproject/Quantifying-Cognitive-Bias-in-LLMs"
cd "$PROJECT_DIR" || { echo "Project dir not found: $PROJECT_DIR"; exit 1; }

# ---- Generate prompts if not present ----
if [ ! -d "prompts/$GAME" ]; then
  echo "Generating prompts for $GAME..."
  python3 generate_prompts.py --game "$GAME"
fi

# ---- Run experiment ----
echo "Running experiment: $GAME | $MODEL"
echo "============================================"
python3 main.py \
  --game "$GAME" \
  --model "$MODEL" \
  --runs "$RUNS" \
  --temperature 0.7 \
  --concurrent "$CONCURRENT"

# ---- Cleanup ----
echo ""
echo "Stopping Ollama server..."
kill "$OLLAMA_PID" 2>/dev/null || true
sleep 2
pkill -f "ollama serve" 2>/dev/null || true

echo "============================================"
echo "End:         $(date)"
echo "============================================"