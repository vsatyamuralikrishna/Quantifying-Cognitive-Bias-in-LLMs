# vLLM Integration Guide

This guide explains how to use vLLM for high-performance batch inference, which is **6-15x faster** than Ollama API calls.

## Overview

vLLM provides:
- **Batch inference**: All 100 runs per prompt in 1 call (100x fewer API calls)
- **Continuous batching**: Automatically batches requests for maximum throughput
- **Better GPU utilization**: Optimized kernels for NVIDIA GPUs
- **Same models**: Uses Hugging Face versions of your Ollama models

## Performance Comparison

| Metric | Ollama API | vLLM |
|--------|------------|------|
| Calls per prompt (100 runs) | 100 | 1 |
| Total calls (79 prompts) | 7,900 | 79 |
| Time per game | ~30 min | ~2-5 min |
| Speedup | 1x | **6-15x** |

## Installation

### 1. Install vLLM

```bash
# In your conda environment
conda activate qcbai
pip install vllm
```

**Note**: vLLM requires CUDA and may take a while to install. On HPC, you may need to build from source or use a pre-built wheel.

### 2. Download Models

Models are automatically downloaded from Hugging Face on first use. They'll be cached to:
- `/groups/tylermillhouse/huggingface` (configured in SLURM scripts)

**Model sizes** (approximate):
- Llama 3.2 3B: ~6 GB
- Mistral 7B: ~14 GB
- Llama 3.3 70B: ~140 GB
- Total: ~300-400 GB

## Usage

### Command Line

```bash
# Use vLLM backend instead of Ollama
python main.py --game chicken_game --model-type vllm

# Run all games with vLLM
python main.py --game all --model-type vllm

# Specific model with vLLM
python main.py --game prisoners_dilemma --model llama3.2:latest --model-type vllm
```

### SLURM Scripts

Update your SLURM scripts to use vLLM:

```bash
# In slurm/run_single_game.slurm, change:
python3 main.py --game "$GAME" --model-type vllm --runs $RUNS --temperature 0.7
```

**Note**: `--concurrent` is ignored for vLLM (batching is automatic).

## How It Works

### Ollama (Current)
```
Prompt → 100 API calls → 100 responses
Time: ~30 min for 7,900 calls
```

### vLLM (New)
```
Prompt → 1 batch call (100 runs) → 100 responses
Time: ~2-5 min for 79 batch calls
```

## Model Mapping

vLLM automatically maps Ollama model names to Hugging Face:

| Ollama | Hugging Face |
|--------|--------------|
| `llama3.2:latest` | `meta-llama/Llama-3.2-3B-Instruct` |
| `mistral:latest` | `mistralai/Mistral-7B-Instruct-v0.3` |
| `llama3.3:latest` | `meta-llama/Llama-3.3-70B-Instruct` |
| `mistral-small3.1:latest` | `mistralai/Mistral-Small-Instruct-3.1` |
| `phi4:latest` | `microsoft/Phi-4` |
| `gemma3:27b` | `google/gemma-2-27b-it` |
| `qwen2.5:32b` | `Qwen/Qwen2.5-32B-Instruct` |

## GPU Configuration

vLLM automatically uses available GPUs. For 2 GPUs:

```python
# In qcbai/llm/vllm.py, tensor_parallel_size is set to 1 by default
# For 2 GPUs, modify load_vllm_model_configs():
load_vllm_model_configs(tensor_parallel_size=2)
```

## Troubleshooting

### vLLM not found
```bash
pip install vllm
```

### CUDA out of memory
- Reduce `tensor_parallel_size` to 1
- Use smaller models first
- Check GPU memory: `nvidia-smi`

### Model download fails
- Check Hugging Face access (some models require approval)
- Verify `HF_HOME` environment variable
- Check disk space: `df -h /groups/tylermillhouse/huggingface`

### Slow first run
- First run downloads models (one-time, ~300GB)
- Subsequent runs use cached models

## Code Structure

- `qcbai/llm/vllm.py`: vLLM model runner implementation
- `qcbai/llm/registry.py`: Updated to support vLLM models
- `qcbai/analytics/runner.py`: Updated to use batch inference for vLLM

## Switching Back to Ollama

Simply use `--model-type ollama` or omit the flag (default):

```bash
python main.py --game chicken_game --model-type ollama
```

Both backends can coexist - choose based on your needs!

