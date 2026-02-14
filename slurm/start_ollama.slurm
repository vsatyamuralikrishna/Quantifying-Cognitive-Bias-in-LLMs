#!/bin/bash
#SBATCH --job-name=ollama-server
#SBATCH --output=slurm/logs/ollama_%j.out
#SBATCH --error=slurm/logs/ollama_%j.err
#SBATCH --time=72:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:volta:1
#SBATCH --partition=gpu_standard
#SBATCH --account=YOUR_GROUP

# ============================================================
# Start Ollama server on a UA HPC GPU node (Puma - V100S 32GB)
#
# Usage:
#   sbatch slurm/start_ollama.slurm
#
# After starting, check the log for the hostname:
#   cat slurm/logs/ollama_<jobid>.out
# Then set OLLAMA_HOST in your experiment jobs.
# ============================================================

echo "============================================"
echo "Ollama Server"
echo "Job ID:    $SLURM_JOB_ID"
echo "Cluster:   $SLURM_CLUSTER_NAME"
echo "Node:      $HOSTNAME"
echo "GPUs:      $SLURM_GPUS_ON_NODE"
echo "Start:     $(date)"
echo "============================================"

# Load UA HPC modules
module load cuda11/11.8

# Ollama storage - use /groups or /xdisk to avoid filling 50GB /home
# UPDATE: Set this to your group's storage path
export OLLAMA_MODELS=${OLLAMA_MODELS:-"/xdisk/$SLURM_JOB_ACCOUNT/$USER/.ollama/models"}
mkdir -p "$OLLAMA_MODELS"

export OLLAMA_HOST="0.0.0.0:11434"

# Concurrency: how many parallel requests Ollama processes at once.
# V100S (32GB VRAM): 8 is safe for 7B models, 4 for 13B models.
export OLLAMA_NUM_PARALLEL=${OLLAMA_NUM_PARALLEL:-8}

echo ""
echo "OLLAMA_MODELS:       $OLLAMA_MODELS"
echo "OLLAMA_NUM_PARALLEL: $OLLAMA_NUM_PARALLEL"
echo ""
echo "Connect from experiment jobs with:"
echo "  export OLLAMA_HOST=http://$HOSTNAME:11434"
echo ""

# Pull required models before serving
ollama pull llama3.2:latest 2>/dev/null || true
ollama pull mistral:latest 2>/dev/null || true

# Start the server (blocks until job ends or is cancelled)
ollama serve
