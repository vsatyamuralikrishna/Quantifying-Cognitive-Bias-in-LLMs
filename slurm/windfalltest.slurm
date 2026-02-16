#!/bin/bash
#SBATCH --job-name=qcbai-chicken-wgemma27b
#SBATCH --partition=gpu_windfall
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:volta:1
#SBATCH --mem-per-cpu=5gb
#SBATCH --time=20:00:00
#SBATCH -e slurm/logs/%x_%j.err
#SBATCH -o slurm/logs/%x_%j.out
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=anudeepappikatla@arizona.edu

# ============================================================
# Run a single game experiment with ONE specific model.
# Cluster: Puma | Partition: gpu_windfall (free, preemptible)
# GPU: 1x V100S (32GB) | Model: qwen2.5:32b (~20GB)
#
# Usage:
#   RUNS=25 CONCURRENT=4 sbatch slurm/run_single_game.slurm chicken_game qwen2.5:32b
# ============================================================

set -euo pipefail

GAME=${1:?"Usage: sbatch slurm/run_single_game.slurm <game_key> <model_name>"}
MODEL=${2:?"Usage: sbatch slurm/run_single_game.slurm <game_key> <model_name>"}

RUNS=${RUNS:-25}
CONCURRENT=${CONCURRENT:-4}

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
echo "GPUs:        ${CUDA_VISIBLE_DEVICES:-unknown}"
echo "Start:       $(date)"
echo "============================================"

# ---- Load modules ----
module purge
module load anaconda/2024.06
module load cuda11 cuda11-sdk cuda11-dnn
# NOTE: Apptainer is pre-installed on all compute nodes — no module needed

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

# ---- Install/update packages ----
echo "Installing packages from requirements.txt..."
conda install -c conda-forge -y numpy matplotlib pydantic tqdm pyyaml || true
pip install -q --upgrade pip
pip install -q -r requirements.txt

# ---- Install PyTorch with CUDA 11.8 support ----
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo ""
python3 --version
echo "Visible GPUs:"
nvidia-smi -L
echo ""
nvidia-smi

# ---- Verify torch sees GPUs with correct CUDA ----
python3 - <<'EOF'
import torch
print(f"PyTorch version:  {torch.__version__}")
print(f"CUDA available:   {torch.cuda.is_available()}")
print(f"CUDA version:     {torch.version.cuda}")
print(f"GPU count:        {torch.cuda.device_count()}")
for i in range(torch.cuda.device_count()):
    print(f"  GPU {i}: {torch.cuda.get_device_name(i)} ({torch.cuda.get_device_properties(i).total_memory / 1e9:.1f} GB)")
EOF

# ---- Ollama environment ----
export OLLAMA_HOST="http://127.0.0.1:11434"
export OLLAMA_NUM_PARALLEL=$CONCURRENT
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_GPU=999
export OLLAMA_KEEP_ALIVE="60m"

# ---- Start Ollama server via Apptainer ----
echo ""
echo "Starting Ollama server via Apptainer..."
apptainer exec --nv \
  --home /groups/tylermillhouse/ollama/home \
  -B /groups/tylermillhouse/ollama/models:/root/.ollama \
  --env OLLAMA_HOST="$OLLAMA_HOST" \
  --env OLLAMA_NUM_GPU=999 \
  --env OLLAMA_NUM_PARALLEL="$CONCURRENT" \
  --env OLLAMA_MAX_LOADED_MODELS=1 \
  --env OLLAMA_KEEP_ALIVE="60m" \
  --env CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" \
  --env LD_LIBRARY_PATH="/usr/local/cuda-11.8/lib64:/opt/ohpc/pub/apps/cuda/11.8/lib64:${LD_LIBRARY_PATH:-}" \
  /groups/tylermillhouse/ollama/image/ollama.sif \
  ollama serve &

OLLAMA_PID=$!

# ---- Wait for server to be ready ----
echo "Waiting for Ollama server..."
MAX_WAIT=120
WAITED=0
while ! curl -s http://127.0.0.1:11434/ > /dev/null 2>&1; do
    sleep 2
    WAITED=$((WAITED + 2))
    if [ $WAITED -ge $MAX_WAIT ]; then
        echo "ERROR: Ollama server failed to start after ${MAX_WAIT}s"
        tail -50 slurm/logs/${SLURM_JOB_NAME}_${SLURM_JOB_ID}.err 2>/dev/null || true
        kill $OLLAMA_PID 2>/dev/null || true
        exit 1
    fi
done
echo "Ollama server ready after ${WAITED}s"

# ---- Test connection ----
echo "Testing Ollama connection..."
curl -s http://127.0.0.1:11434/api/tags | head -c 300
echo ""

# ---- Pull model if not cached ----
echo ""
echo "Pulling model: $MODEL"
apptainer exec --nv \
  --home /groups/tylermillhouse/ollama/home \
  -B /groups/tylermillhouse/ollama/models:/root/.ollama \
  --env OLLAMA_HOST="$OLLAMA_HOST" \
  /groups/tylermillhouse/ollama/image/ollama.sif \
  ollama pull "$MODEL"

# ---- Warmup: preload model into GPU VRAM ----
echo ""
echo "Warming up model: $MODEL"
curl -s http://127.0.0.1:11434/api/generate \
    -d "{\"model\": \"$MODEL\", \"prompt\": \"hello\", \"stream\": false}" \
    > /dev/null 2>&1
echo "Warmup complete."

# ---- Verify GPU utilization ----
echo ""
echo "=== GPU Status After Model Load ==="
nvidia-smi
echo ""
echo "=== Ollama Model Status ==="
apptainer exec --nv \
  --home /groups/tylermillhouse/ollama/home \
  -B /groups/tylermillhouse/ollama/models:/root/.ollama \
  --env OLLAMA_HOST="$OLLAMA_HOST" \
  /groups/tylermillhouse/ollama/image/ollama.sif \
  ollama ps
echo ""

# ---- GPU monitor in background ----
(
    while true; do
        echo "--- GPU Monitor $(date) ---" >> slurm/logs/gpu_monitor_${SLURM_JOB_ID}.log
        nvidia-smi >> slurm/logs/gpu_monitor_${SLURM_JOB_ID}.log 2>&1
        sleep 30
    done
) &
MONITOR_PID=$!

# ---- Generate prompts if not present ----
if [ ! -d "prompts/$GAME" ]; then
  echo "Generating prompts for $GAME..."
  python3 generate_prompts.py --game "$GAME"
fi

# ---- Run experiment ----
echo ""
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
kill "$MONITOR_PID" 2>/dev/null || true
kill "$OLLAMA_PID" 2>/dev/null || true
sleep 2
pkill -f "ollama serve" 2>/dev/null || true

echo "============================================"
echo "End:         $(date)"
echo "============================================"