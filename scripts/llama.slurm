#!/bin/bash

#SBATCH --job-name=qwen_job
#SBATCH --partition=gpu_standard
#SBATCH --account=tylermillhouse
#SBATCH --ntasks=28
#SBATCH --nodes=2                             
#SBATCH --gres=gpu:2
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=4-00:00:00
#SBATCH -e %j.err
#SBATCH -o %j.out
#SBATCH --mail-type=BEGIN,END,FAIL,ALL
#SBATCH --mail-user=anudeepappikatla@arizona.edu

# Load necessary modules
#source  
module load python/3.11
module load cuda11 cuda11-sdk cuda11-dnn
module load micromamba
# Try loading modules with --ignore-cache if they exist but aren't loading properly
module load tensorflow/nvidia/2.9.1
export CUDA_DIR=/opt/ohpc/pub/apps/cuda/11.8/
export XLA_FLAGS=--xla_gpu_cuda_data_dir=/opt/ohpc/pub/apps/cuda/11.8/
# Set environment variables
export HF_HOME=/groups/tylermillhouse/huggingface
export TRANSFORMERS_CACHE=/groups/tylermillhouse/huggingface
export HF_DATASETS_CACHE=/groups/tylermillhouse/huggingface/datasets

# Activate your existing environment
eval "$(micromamba shell hook --shell bash)"
micromamba activate /groups/tylermillhouse/micromamba_envs/myenv

python3 --version
python3 <<EOF
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))
EOF

python3 - <<EOF
import torch
print("Torch sees GPUs:", torch.cuda.device_count(), torch.cuda.get_device_name(0))
EOF

# Start Ollama server using Singularity with your specific paths
singularity exec --nv \
  --home /groups/tylermillhouse/ollama/home \
  -B /groups/tylermillhouse/ollama/models:/root/.ollama \
  /groups/tylermillhouse/ollama/image/ollama.sif \
  ollama serve &

# Store the Ollama server PID to kill it later
OLLAMA_PID=$!

# Give Ollama server time to start
sleep 10


# Alternative Method 2: Using the API directly
echo "Testing API call to Ollama:"
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "llama3.3:latest",
  "prompt": "Hello, world!"
}'

# 6) Now monitor within the job to confirm:
nvidia-smi -L
nvidia-smi

# Check if the main.py file exists in the correct directory (case-sensitive)
if [ -f "/groups/tylermillhouse/capstoneproject/Quantifying-Cognitive-Bias-in-LLMs/main.py" ]; then
  # Run your main script from the corrected path with proper case
  python3 /groups/tylermillhouse/capstoneproject/Quantifying-Cognitive-Bias-in-LLMs/main.py --model llama3.3
else
  echo "ERROR: main.py not found at expected location."
  echo "Searching for main.py in the project directory:"
  find /groups/tylermillhouse/capstoneproject/Quantifying-Cognitive-Bias-in-LLMs -name "*.py" -type f
fi

# Cleanup - kill the Ollama server when done
kill $OLLAMA_PID || kill $(pgrep ollama)

# Print completion message
echo "Job completed at $(date)"