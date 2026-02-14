# Execution Guide

Detailed documentation for running the Quantifying Cognitive Bias in LLMs framework, including UA HPC (Puma cluster) setup, CLI reference, concurrency tuning, and configuration.

---

## Table of Contents

- [Overview](#overview)
- [Supported Games](#supported-games)
- [Project Structure](#project-structure)
- [Installation](#installation)
  - [Local Setup](#local-setup)
  - [UA HPC Setup (Puma)](#ua-hpc-setup-puma)
- [Quick Start](#quick-start)
- [Prompt Generation](#prompt-generation)
- [Running Experiments](#running-experiments)
- [Analyzing Results](#analyzing-results)
- [HPC Execution (SLURM)](#hpc-execution-slurm)
  - [UA HPC Specifics](#ua-hpc-specifics)
  - [Step-by-Step Workflow](#step-by-step-workflow)
  - [SLURM Scripts Reference](#slurm-scripts-reference)
  - [Before You Submit (Checklist)](#before-you-submit-checklist)
  - [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
- [Concurrency & Performance](#concurrency--performance)
- [Configuration](#configuration)
- [How It Works](#how-it-works)

---

## Overview

Each experiment follows this pipeline:

```
Generate Prompts --> Run LLM Inference (x100 per prompt) --> Parse Responses --> Aggregate & Analyze
```

- **26 demographic personas** (combinations of gender x race x ethnicity) are inserted into game prompts using **3 formatting styles** (intro, inline, neutral), plus **1 neutral base prompt** = **79 prompts per game**.
- Each prompt is sent to the LLM **100 times** (configurable) to obtain a statistical distribution of responses.
- Results are stored as structured JSON and can be aggregated into CSV summaries for downstream analysis.

---

## Supported Games

| Game | Response Type | Choices / Range | What It Measures |
|------|:------------:|:---------------:|------------------|
| **Prisoner's Dilemma** | Binary | Silent / Implicate | Cooperation vs. betrayal tendency |
| **Chicken Game** | Binary | Swerve / Stay | Risk-taking behavior |
| **Public Goods Game (Boolean)** | Binary | Contribute / Not Contribute | Free-riding vs. contribution |
| **Public Goods Game (Amount)** | Amount | $0 - $ENDOWMENT | Degree of contribution to a shared pool |
| **Dictator Game** | Amount | $0 - $10 | Fairness and generosity |
| **Ultimatum Game** | Amount | $0 - $10 | Fairness perception and offer strategy |
| **Trust Game** | Amount | $0 - $10 | Trust and investment willingness |

### Game Keys

Used as CLI arguments throughout the project:

```
prisoners_dilemma
chicken_game
public_goods_game_boolean
public_goods_game
dictator_game
ultimatum_game
trust_game
```

---

## Project Structure

```
Quantifying-Cognitive-Bias-in-LLMs/
|
|-- main.py                        # CLI: run experiments
|-- generate_prompts.py            # CLI: generate prompt JSON files
|-- analyze_results.py             # CLI: aggregate results into summaries
|-- requirements.txt               # Python dependencies
|-- README.md
|
|-- qcbai/                         # Core package
|   |-- games/
|   |   |-- game_config.py         # GameConfig registry (7 games)
|   |   +-- prompts/
|   |       +-- game_rules.py      # Prompt templates for all games
|   |
|   |-- generators/
|   |   +-- prompts.py             # PersonaPromptGenerator class
|   |
|   |-- analytics/
|   |   |-- runner.py              # Experiment runner (asyncio concurrent)
|   |   |-- formatter.py           # Response parsers (binary + amount)
|   |   |-- types.py               # Pydantic models (ExperimentResult)
|   |   +-- utils.py               # Helper utilities
|   |
|   |-- llm/
|   |   |-- base.py                # Abstract ModelRunner interface (sync + async)
|   |   |-- ollama.py              # Ollama implementation (AsyncClient)
|   |   |-- registry.py            # Model loader from YAML config
|   |   +-- models.yaml            # Model definitions
|   |
|   |-- constants/
|   |   +-- categories.py          # 26 demographic persona definitions
|   |
|   |-- models/
|   |   +-- models.py              # Shared model utilities
|   |
|   +-- utils/
|       +-- visualizer.py          # Matplotlib plot generation
|
|-- slurm/                         # HPC job scripts (UA Puma cluster)
|   |-- run_all_games.slurm        # 2D job array: 7 games × 7 models = 49 jobs
|   |-- run_single_game.slurm      # Run one game+model as a SLURM job
|   +-- submit_all.sh              # Convenience: generate + submit all
|
|-- docs/                          # Documentation
|   +-- EXECUTION.md               # This file
|
|-- prompts/                       # Generated (gitignored)
|   +-- <game_key>/*.json
|
|-- results/                       # Experiment outputs (gitignored)
|   +-- <game_key>/<model_slug>/<prompt_id>.json
|
|-- analytics/                     # Aggregated summaries (gitignored)
|   +-- <game_key>/summary.{json,csv}
|
+-- images/                        # Generated plots (gitignored)
    +-- <game_key>/<model_slug>/<prompt_id>.png
```

---

## Installation

### Local Setup

```bash
# Clone the repository
git clone <repo-url>
cd Quantifying-Cognitive-Bias-in-LLMs

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Pull Ollama models
ollama pull llama3.2:latest
ollama pull mistral:latest
```

### UA HPC Setup (Puma)

On the University of Arizona HPC, use **micromamba** (anaconda is deprecated):

```bash
# SSH into HPC
ssh netid@hpc.arizona.edu
# Select Puma shell

# Load micromamba and create environment
module load micromamba
micromamba create -n qcbai python=3.11
micromamba activate qcbai

# Install dependencies
pip install -r requirements.txt

# IMPORTANT: Move large caches off /home (50GB limit)
# Add these to your ~/.bashrc:
export OLLAMA_MODELS="/xdisk/YOUR_PI_GROUP/$USER/.ollama/models"
export PIP_CACHE_DIR="/xdisk/YOUR_PI_GROUP/$USER/.cache/pip"
```

**Storage locations on UA HPC:**

| Path | Quota | Use For |
|------|-------|---------|
| `/home/uxx/netid` | 50 GB | Code, configs |
| `/groups/pi_netid` | 500 GB | Shared data |
| `/xdisk/pi_netid` | 200 GB - 20 TB | Model weights, results |

---

## Quick Start

Run a complete experiment in three commands:

```bash
# 1. Generate prompts for all games
python generate_prompts.py

# 2. Run experiment (Prisoner's Dilemma, 100 runs/prompt, 8 concurrent)
python main.py --game prisoners_dilemma --runs 100 --concurrent 8

# 3. Analyze results
python analyze_results.py --game prisoners_dilemma
```

---

## Prompt Generation

Generate structured JSON prompt files for each game:

```bash
# Generate prompts for all 7 games (553 total: 79 per game)
python generate_prompts.py

# Generate for specific games
python generate_prompts.py --game prisoners_dilemma
python generate_prompts.py --game dictator_game --game trust_game
```

**Output:** `prompts/<game_key>/` directory with 79 JSON files per game:
- `base_prompt.json` -- Neutral prompt (no demographic information)
- `<style>__gender-<g>__race-<r>__ethnicity-<e>.json` -- 78 persona-based prompts

### Prompt Structure (JSON)

```json
{
  "prompt_id": "intro__gender-Male__race-White__ethnicity-Hispanic",
  "prompt_uid": "gre-a1b2c3d4",
  "game_type": "prisoners_dilemma",
  "style": "intro",
  "persona": "Male, White, Hispanic",
  "gender": "Male",
  "race": "White",
  "ethnicity": "Hispanic",
  "prompt": [
    {"role": "system", "content": "You are playing the Prisoner's Dilemma..."},
    {"role": "user", "content": "Your partner is a Male who identifies as..."}
  ]
}
```

---

## Running Experiments

### CLI Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--game` | *(required)* | Game key or `all` for all 7 games |
| `--model` | `None` | Filter to a specific model (e.g., `llama3.2:latest`) |
| `--runs` | `100` | Number of LLM calls per prompt |
| `--temperature` | `0.7` | Sampling temperature |
| `--model-type` | `ollama` | Backend: `ollama`, `transformers`, or `all` |
| `--concurrent` | `8` | Max concurrent async requests per prompt batch |

### Examples

```bash
# Run Prisoner's Dilemma with all configured models
python main.py --game prisoners_dilemma

# Run a specific model on the Dictator Game
python main.py --game dictator_game --model llama3.2:latest

# Run all 7 games sequentially
python main.py --game all

# Conservative: fewer runs, lower concurrency
python main.py --game trust_game --runs 50 --concurrent 4

# Sequential mode (no concurrency)
python main.py --game trust_game --concurrent 1

# Full experiment: all games, all models, 100 runs
python main.py --game all --runs 100 --concurrent 8
```

### Output

Results and plots are organized by game → model → prompt:

```
results/<game_key>/
  ├── llama3.2/
  │   ├── all_results.json      ← combined for this model
  │   ├── base_prompt.json
  │   ├── intro__gender-Male__race-White__ethnicity-Hispanic.json
  │   └── ...  (79 prompt files + all_results.json per model)
  ├── mistral/
  │   ├── all_results.json
  │   └── ...
  ├── qwen2.5-32b/
  │   ├── all_results.json
  │   └── ...
  └── all_results.json          ← combined across ALL models

images/<game_key>/
  ├── llama3.2/
  │   ├── base_prompt.png
  │   ├── intro__gender-Male__race-White__ethnicity-Hispanic.png
  │   └── summary.png
  ├── mistral/
  │   └── ...
  └── qwen2.5-32b/
      └── ...
```

| Output | Location |
|--------|----------|
| Individual result | `results/<game_key>/<model_slug>/<prompt_id>.json` |
| Per-model combined | `results/<game_key>/<model_slug>/all_results.json` |
| All-models combined | `results/<game_key>/all_results.json` |
| Per-prompt plots | `images/<game_key>/<model_slug>/<prompt_id>.png` |
| Model summary plot | `images/<game_key>/<model_slug>/summary.png` |

---

## Analyzing Results

After experiments complete, aggregate raw results into summary statistics:

```bash
# Analyze all games
python analyze_results.py

# Analyze specific games
python analyze_results.py --game prisoners_dilemma
python analyze_results.py --game dictator_game --game trust_game
```

### Output

| File | Content |
|------|---------|
| `analytics/<game_key>/summary.json` | Full structured summary |
| `analytics/<game_key>/summary.csv` | Flat table for spreadsheet/statistical analysis |

### Summary Metrics

**Binary games** (Prisoner's Dilemma, Chicken, PGG Boolean):
- Trust count and percentage
- Distrust count and percentage
- Per (model, persona, style) breakdown

**Amount games** (Dictator, Ultimatum, Trust, PGG Amount):
- Mean, min, max amount
- Generosity percentage (mean / max possible)
- Per (model, persona, style) breakdown

---

## HPC Execution (SLURM)

### UA HPC Specifics

All SLURM scripts are configured for the **University of Arizona Puma cluster**:

| Setting | Value | Notes |
|---------|-------|-------|
| **Cluster** | Puma | AMD EPYC 7642, Rocky Linux 9 |
| **GPU Partition** | `gpu_standard` | `--account=tylermillhouse` |
| **GPUs** | 2x NVIDIA V100S | 32 GB VRAM each (64 GB total), `--gres=gpu:2` |
| **CUDA Modules** | `cuda11 cuda11-sdk cuda11-dnn` | Loaded in all scripts |
| **Python Env** | micromamba | `/groups/tylermillhouse/micromamba_envs/myenv` |
| **Ollama** | Singularity container | `singularity exec --nv` with models at `/groups/tylermillhouse/ollama/models` |
| **Project Dir** | `/groups/tylermillhouse/capstoneproject/Quantifying-Cognitive-Bias-in-LLMs` | Hardcoded in scripts |
| **Max Walltime** | 4 days per job | Configurable in SLURM headers |

### Architecture: Self-Contained Jobs

Each SLURM job is **fully self-contained** — it starts its own Ollama server via Singularity, runs the experiment, and cleans up:

```
SLURM Job (one per game×model pair)
  ├── Load modules (python/3.11, cuda11, micromamba)
  ├── Activate micromamba environment
  ├── Start Ollama via Singularity (background process)
  │     └── singularity exec --nv ... ollama serve &
  ├── Run python3 main.py --game <game> --model <model> --concurrent 8
  │     └── asyncio fires 8 concurrent requests per prompt batch
  └── Kill Ollama on completion
```

No separate Ollama server job is needed.

### Step-by-Step Workflow

```bash
# ---- Option A: Run all 49 jobs (7 games × 7 models) ----
bash slurm/submit_all.sh

# ---- Option B: Run with a test first ----
bash slurm/submit_all.sh --test     # 1 job: prisoners_dilemma + llama3.2:latest
bash slurm/submit_all.sh            # then submit all 49

# ---- Option C: Single game + model ----
sbatch slurm/run_single_game.slurm prisoners_dilemma llama3.2:latest

# ---- Option D: Single game, all models (sequential swap in one job) ----
sbatch slurm/run_single_game.slurm prisoners_dilemma
```

### SLURM Scripts Reference

| Script | Purpose | Resources |
|--------|---------|-----------|
| `run_all_games.slurm` | 2D job array: 7 games × 7 models = 49 jobs | 2x V100S, 28 tasks, 8gb/cpu, 4 days |
| `run_single_game.slurm` | Single (game, model) experiment job | 2x V100S, 28 tasks, 8gb/cpu, 4 days |
| `submit_all.sh` | Generate prompts + submit job array | Runs on login node |

### 2D Job Array Mapping

The `run_all_games.slurm` uses a **2D index** where `index = game_idx × 7 + model_idx`:

**Games (rows):**

| Game Index | Game Key |
|:----------:|----------|
| 0 | `prisoners_dilemma` |
| 1 | `dictator_game` |
| 2 | `chicken_game` |
| 3 | `public_goods_game` |
| 4 | `public_goods_game_boolean` |
| 5 | `ultimatum_game` |
| 6 | `trust_game` |

**Models (columns):**

| Model Index | Model | VRAM |
|:-----------:|-------|-----:|
| 0 | `llama3.2:latest` | 2 GB |
| 1 | `mistral:latest` | 4.1 GB |
| 2 | `llama3.3:latest` | 42 GB |
| 3 | `mistral-small3.1:latest` | 15 GB |
| 4 | `phi4:latest` | 9.1 GB |
| 5 | `gemma3:27b` | 17 GB |
| 6 | `qwen2.5:32b` | 19 GB |

**Example indices:**

| Array Index | Game | Model |
|:-----------:|------|-------|
| 0 | prisoners_dilemma | llama3.2:latest |
| 6 | prisoners_dilemma | qwen2.5:32b |
| 7 | dictator_game | llama3.2:latest |
| 48 | trust_game | qwen2.5:32b |

To run a subset, override the array range:
```bash
# All models for prisoners_dilemma only (game index 0)
sbatch --array=0-6 slurm/run_all_games.slurm

# Only llama3.2 (model index 0) across all games
sbatch --array=0,7,14,21,28,35,42 slurm/run_all_games.slurm
```

### Before You Submit (Checklist)

1. Ensure micromamba env exists at `/groups/tylermillhouse/micromamba_envs/myenv`
2. Verify requirements: `pip install -r requirements.txt`
3. Confirm Singularity image: `ls /groups/tylermillhouse/ollama/image/ollama.sif`
4. Confirm Ollama models: `ls /groups/tylermillhouse/ollama/models/`
5. Create log directory: `mkdir -p slurm/logs`
6. Test with a single job first: `bash slurm/submit_all.sh --test`

### Monitoring and Troubleshooting

```bash
# Check job status
squeue -u $USER

# Check all array sub-jobs
squeue -r --job <parent_job_id>

# View job output
cat slurm/logs/qcbai-games_<jobid>_<arrayidx>.out

# Check allocation usage
va

# Check resource usage after completion
seff <job_id>

# View job limits for your group
job-limits <group_name>

# Cancel a job
scancel <job_id>
```

**Common issues on UA HPC:**

| Issue | Solution |
|-------|----------|
| `conda: command not found` | Use `micromamba` instead (anaconda is deprecated) |
| `sbatch: error: Batch job submission failed: Invalid account` | Ensure `--account=tylermillhouse` is correct |
| Out of disk space on `/home` | Move models/caches to `/groups` or `/xdisk` |
| `No module named 'ollama'` | Activate environment: `eval "$(micromamba shell hook --shell bash)" && micromamba activate /groups/tylermillhouse/micromamba_envs/myenv` |
| GPU job pending long time | Try `gpu_windfall` partition (preemptible but starts faster) |
| Ollama connection refused | Increase `sleep 10` wait time in SLURM script; check Singularity logs |
| OOM on large models | Reduce `CONCURRENT` for 27B+ models (e.g., `CONCURRENT=4 sbatch ...`) |
| 49 jobs too many for allocation | Submit in batches: `sbatch --array=0-6 ...` then `--array=7-13 ...` etc. |

---

## Concurrency & Performance

Each prompt runs **100 times** (default) against the LLM. Without concurrency, this means 100 serial HTTP requests per prompt. The framework uses **asyncio with `ollama.AsyncClient`** for true async I/O concurrency.

### Architecture

```
Main Process
  +-- For each model:
        +-- For each prompt (79 per game):
              +-- asyncio.run(_run_concurrent_batch())
                    +-- asyncio.Semaphore(N)
                          |-- Task 1 --> arun_prompt() --> Ollama AsyncClient
                          |-- Task 2 --> arun_prompt() --> Ollama AsyncClient
                          |-- ...  (semaphore limits to N in-flight)
                          +-- Task 100 --> arun_prompt() --> Ollama AsyncClient
                    +-- asyncio.gather() collects all results in order
```

**How it works:**
1. All 100 runs are launched as async tasks via `asyncio.gather()`
2. An `asyncio.Semaphore(max_concurrent)` limits how many are in-flight simultaneously
3. Each task calls `ollama.AsyncClient.chat()` for non-blocking HTTP I/O
4. Results are collected in order and returned as a list

### Configuration

| Setting | Where | Default | Description |
|---------|-------|---------|-------------|
| `--concurrent` | `main.py` CLI | 8 | Max async requests in-flight per prompt |
| `OLLAMA_NUM_PARALLEL` | Environment / SLURM | 8 | Max parallel requests Ollama server handles |
| `CONCURRENT` | SLURM scripts | 8 | Shared variable for `--concurrent` |

> **Important:** `OLLAMA_NUM_PARALLEL` (server-side) must be >= `--concurrent` (client-side) for full parallelism. Both are set automatically in the SLURM scripts.

### VRAM Tuning Guide (Puma V100S - 32GB)

| `--concurrent` | Model Size | Notes |
|:-------:|:----------:|-------|
| 4 | 13B+ | Conservative, avoids OOM |
| 8 | 7B | Safe default for V100S 32GB |
| 12 | 3B-7B | Aggressive for smaller models |

For Ocelote P100 (16GB VRAM), use `--concurrent 4` max.

### VRAM Tuning per Model (2x V100S = 64 GB)

| Model | VRAM | Recommended `--concurrent` |
|-------|-----:|:--------------------------:|
| llama3.2:latest | 2 GB | 8-12 |
| mistral:latest | 4.1 GB | 8 |
| phi4:latest | 9.1 GB | 8 |
| mistral-small3.1:latest | 15 GB | 8 |
| gemma3:27b | 17 GB | 6-8 |
| qwen2.5:32b | 19 GB | 4-6 |
| llama3.3:latest | 42 GB | 2-4 |

Override per job: `CONCURRENT=4 sbatch slurm/run_single_game.slurm trust_game llama3.3:latest`

### Performance Estimate

| Scenario | Prompts | Runs | Concurrent | Total Calls | Est. Time |
|----------|:-------:|:----:|:----------:|:-----------:|:---------:|
| 1 game, 1 model | 79 | 100 | 8 | 7,900 | ~30 min |
| 1 game, 7 models | 79 | 100 | 8 | 55,300 | ~3.5 hours* |
| 7 games, 7 models | 553 | 100 | 8 | 387,100 | ~24 hours* |

*With 2D SLURM job array (49 jobs), all (game, model) pairs run in parallel across nodes → ~30 min wall-clock if enough GPU nodes are available.*

---

## Configuration

### Models

Edit `qcbai/llm/models.yaml` to add, remove, or configure models:

```yaml
ollama:
  - name: "llama3.2:latest"       # 2 GB
    slug: "llama3.2"
    temperature: 0.7

  - name: "mistral:latest"        # 4.1 GB
    slug: "mistral"
    temperature: 0.7

  - name: "llama3.3:latest"       # 42 GB
    slug: "llama3.3"
    temperature: 0.7

  - name: "mistral-small3.1:latest"  # 15 GB
    slug: "mistral-small3.1"
    temperature: 0.7

  - name: "phi4:latest"           # 9.1 GB
    slug: "phi4"
    temperature: 0.7

  - name: "gemma3:27b"            # 17 GB
    slug: "gemma3-27b"
    temperature: 0.7

  - name: "qwen2.5:32b"           # 19 GB
    slug: "qwen2.5-32b"
    temperature: 0.7
```

All 7 models are enabled by default. To disable a model, comment it out or remove it.

### Public Goods Game Settings

The Public Goods Game has configurable economic parameters. Defaults are set in `qcbai/games/prompts/game_rules.py`:

```python
PGG_DEFAULT_SETTINGS = {
    "N": 4,              # Number of players
    "ENDOWMENT": 20,     # Starting amount per player ($)
    "MULTIPLIER": 1.2,   # Public pool multiplier
    "MIN_POSITIVE": 1,   # Min contributors for pool (boolean version)
}
```

To use custom settings programmatically:

```python
from qcbai.games.game_config import build_pgg_game_config

custom_config = build_pgg_game_config(
    settings={"N": 6, "ENDOWMENT": 50, "MULTIPLIER": 1.5, "MIN_POSITIVE": 2},
    version="amount"
)
```

### Demographic Personas

26 persona combinations are defined in `qcbai/constants/categories.py`, spanning:
- **Gender:** Male, Female
- **Race:** White, Black, Asian
- **Ethnicity:** Hispanic, Non-Hispanic

Each persona is presented in 3 formatting styles:
- **Intro:** Separate sentence before the game prompt
- **Inline:** Embedded within the game scenario text
- **Neutral:** Third-person description of the partner

---

## How It Works

### 1. Prompt Generation

The `PersonaPromptGenerator` takes a `GameConfig` and produces 79 prompts:
- Reads the game's `neutral_prompt` (base scenario) and `personality_prompt` (persona template with `{PARTNER_PERSONA}` placeholder)
- For each of the 26 personas x 3 styles, formats the persona description and injects it into the template
- Saves each prompt as a standalone JSON file with metadata

### 2. Experiment Execution

For each `(model, prompt)` pair:
1. Load the prompt JSON
2. Send to Ollama via `ollama.AsyncClient.chat()` -- repeated N times (default 100), using `asyncio` with semaphore-controlled concurrency
3. Each raw response is parsed:
   - **Binary games:** Match the response text against the two choices (longer match first to avoid substring conflicts)
   - **Amount games:** Extract dollar amount via regex `$\d+`, clamped to `[0, max_amount]`
4. Compute aggregate metrics (trust probability, mean amount, etc.)
5. Save the structured `ExperimentResult` as JSON

### 3. Results Analysis

The `analyze_results.py` script:
1. Reads the combined `all_results.json` for each game
2. Groups by `(model_name, persona, style)`
3. Computes per-group statistics
4. Outputs `summary.json` and `summary.csv` for downstream statistical testing

### Response Parsing Details

**Binary games** use longest-first matching to avoid substring conflicts:
- Choices are sorted by string length (descending) before matching
- Example: "Not Contribute" is checked before "Contribute"

**Amount games** use regex extraction:
- Pattern: `$\s*(\d+)` at the start of the response
- Values are clamped to `[0, max_amount]` for the specific game

---

## License

This project is part of an academic research effort. Please contact the authors for usage and citation information.
