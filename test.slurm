#!/bin/bash

#SBATCH --job-name=ollama_testjob
#SBATCH --partition=gpu_standard   
#SBATCH --nodes=1 --ntasks=1       # single‐node, single‐task is enough for testing
#SBATCH --account=tylermillhouse
#SBATCH --gres=gpu:2               # ask for 2× P100
#SBATCH --mem-per-cpu=8G
#SBATCH --time=01:00:00            # you only need a few minutes for a smoke test
#SBATCH -e %j.err
#SBATCH -o %j.out
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=anudeepappikatla@arizona.edu

# 1) Modules & env
module load python/3.11
module load cuda11 cuda11-sdk cuda11-dnn
module load micromamba
module load tensorflow/nvidia/2.9.1
export CUDA_DIR=/opt/ohpc/pub/apps/cuda/11.8/
export XLA_FLAGS=--xla_gpu_cuda_data_dir=/opt/ohpc/pub/apps/cuda/11.8/
# Activate your micromamba env (which has transformers/torch, etc.)
eval "$(micromamba shell hook --shell bash)"
micromamba activate /groups/tylermillhouse/micromamba_envs/myenv

# 2) (Optional) Sanity-check: can Python see the GPUs?
python3 - <<EOF
import torch
print("Torch sees GPUs:", torch.cuda.device_count(), torch.cuda.get_device_name(0))
EOF

# 3) Start Ollama *with* GPU support exposed
singularity exec --nv \
  --home /groups/tylermillhouse/ollama/home \
  -B /groups/tylermillhouse/ollama/models:/root/.ollama \
  /groups/tylermillhouse/ollama/image/ollama.sif \
  ollama serve &
OLLAMA_PID=$!

singularity exec --nv \
  --home /groups/tylermillhouse/ollama/home \
  -B /groups/tylermillhouse/ollama/models:/root/.ollama \
  /groups/tylermillhouse/ollama/image/ollama.sif \
  ollama list

# Give the server a moment to load the model & bind CUDA
sleep 15

# 4) Export the API endpoint so client calls go to the local server
export OLLAMA_HOST="http://localhost:11434"

# 5) Trigger a real inference using the correct syntax for your Ollama version
# Method 1: Using echo to pipe the prompt
echo "Hello, world!" | singularity exec --nv \
  --home /groups/tylermillhouse/ollama/home \
  -B /groups/tylermillhouse/ollama/models:/root/.ollama \
  /groups/tylermillhouse/ollama/image/ollama.sif \
  ollama run gemma3:27b


# 6) Now monitor within the job to confirm:
nvidia-smi -L
nvidia-smi

# 7) (Your real workload)
python3 /groups/tylermillhouse/capstoneproject/Quantifying-Cognitive-Bias-in-LLMs/main.py

# 8) Tear down Ollama
kill $OLLAMA_PID

echo "✔︎ Done at $(date)"