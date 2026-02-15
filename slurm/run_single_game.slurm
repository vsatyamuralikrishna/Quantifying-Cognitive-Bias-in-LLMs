#!/bin/bash
#SBATCH --job-name=qcbai-game
#SBATCH --partition=gpu_standard
#SBATCH --account=tylermillhouse
#SBATCH --ntasks=28
#SBATCH --nodes=1
#SBATCH --gres=gpu:2
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=4-00:00:00
#SBATCH -e slurm/logs/%x_%j.err
#SBATCH -o slurm/logs/%x_%j.out
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=anudeepappikatla@arizona.edu

# ============================================================
# Run a single game experiment with ONE specific model.
# University of Arizona HPC - Puma Cluster
#
# Starts Ollama via Singularity, runs the experiment, cleans up.
# Each job runs exactly ONE model so it gets full GPU VRAM and
# maximum concurrent inference throughput.
#
# Usage:
#   sbatch slurm/run_single_game.slurm prisoners_dilemma llama3.2:latest
#   sbatch slurm/run_single_game.slurm chicken_game mistral:latest
#   sbatch slurm/run_single_game.slurm trust_game   # runs ALL models (sequential swap)
#   RUNS=25 CONCURRENT=5 sbatch slurm/run_single_game.slurm chicken_game llama3.3:latest
#
# Args:
#   $1 = game key (required)
#   $2 = model name (optional; if omitted, runs all models sequentially)
#
# Environment overrides:
#   RUNS=25         Number of runs per prompt (default: 100)
#   CONCURRENT=5    Max concurrent async requests (default: 8)
# ============================================================

GAME=${1:?"Usage: sbatch slurm/run_single_game.slurm <game_key> [model_name]"}
MODEL=${2:-""}
RUNS=${RUNS:-100}
CONCURRENT=${CONCURRENT:-8}

echo "============================================"
echo "QCBAI Experiment"
echo "Job ID:      $SLURM_JOB_ID"
echo "Cluster:     $SLURM_CLUSTER_NAME"
echo "Node:        $HOSTNAME"
echo "Game:        $GAME"
echo "Model:       ${MODEL:-all (sequential)}"
echo "Runs:        $RUNS"
echo "Concurrent:  $CONCURRENT"
echo "Start:       $(date)"
echo "============================================"

# ---- Load modules ----
module load anaconda/2024.06
module load cuda11 cuda11-sdk cuda11-dnn
module load gnu8/8.3.0  # For C++17 support if needed

export CUDA_DIR=/opt/ohpc/pub/apps/cuda/11.8/
export XLA_FLAGS=--xla_gpu_cuda_data_dir=/opt/ohpc/pub/apps/cuda/11.8/

# ---- Environment variables ----
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

# ---- Navigate to project directory (already done above) ----
# PROJECT_DIR already set and cd done above

# ---- Generate prompts if not present ----
if [ ! -d "prompts/$GAME" ]; then
    echo "Generating prompts for $GAME..."
    python3 generate_prompts.py --game "$GAME"
fi

# ---- Run experiment ----
echo ""
echo "Running experiment: $GAME"
echo "============================================"

if [ -n "$MODEL" ]; then
    python3 main.py --game "$GAME" --model "$MODEL" --runs $RUNS --temperature 0.7 --concurrent $CONCURRENT
else
    python3 main.py --game "$GAME" --runs $RUNS --temperature 0.7 --concurrent $CONCURRENT
fi

# ---- Cleanup ----
echo ""
echo "Stopping Ollama server..."
kill $OLLAMA_PID 2>/dev/null || kill $(pgrep ollama) 2>/dev/null || true

echo "============================================"
echo "End:         $(date)"
echo "============================================"
