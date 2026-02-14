#!/bin/bash
#SBATCH --job-name=ollama-server
#SBATCH --output=slurm/logs/ollama_%j.out
#SBATCH --error=slurm/logs/ollama_%j.err
#SBATCH --time=72:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu

# ============================================================
# Start Ollama server on an HPC GPU node
#
# Usage:
#   sbatch slurm/start_ollama.slurm
#
# After starting, note the hostname and set OLLAMA_HOST in
# your experiment jobs.
# ============================================================

echo "============================================"
echo "Ollama Server"
echo "Job ID:    $SLURM_JOB_ID"
echo "Node:      $HOSTNAME"
echo "Start:     $(date)"
echo "============================================"

# Load GPU modules
module load cuda 2>/dev/null || true

# Set Ollama data directory to a location with sufficient storage
export OLLAMA_MODELS=${OLLAMA_MODELS:-"$HOME/.ollama/models"}
export OLLAMA_HOST="0.0.0.0:11434"

# ---- Concurrency settings ----
# OLLAMA_NUM_PARALLEL controls how many requests the server handles at once.
# Must match the --workers value used in experiment jobs.
# Tune based on GPU VRAM:
#   8  = safe for most GPUs (24GB+)
#   4  = conservative (16GB)
#   16 = aggressive (48GB+ A100/H100)
export OLLAMA_NUM_PARALLEL=${OLLAMA_NUM_PARALLEL:-8}

echo "Ollama host:         $HOSTNAME:11434"
echo "OLLAMA_NUM_PARALLEL: $OLLAMA_NUM_PARALLEL"
echo "Use this in experiment jobs:"
echo "  export OLLAMA_HOST=http://$HOSTNAME:11434"

# Pull required models before serving
ollama pull llama3.2:latest 2>/dev/null || true
ollama pull mistral:latest 2>/dev/null || true

# Start the server (blocks until job ends)
ollama serve
