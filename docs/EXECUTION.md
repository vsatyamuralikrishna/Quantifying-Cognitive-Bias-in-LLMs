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
|   |-- start_ollama.slurm         # Start Ollama server on GPU node
|   |-- run_all_games.slurm        # Job array: all 7 games in parallel
|   |-- run_single_game.slurm      # Run one game as a SLURM job
|   +-- submit_all.sh              # Convenience: generate + submit all
|
|-- docs/                          # Documentation
|   +-- EXECUTION.md               # This file
|
|-- prompts/                       # Generated (gitignored)
|   +-- <game_key>/*.json
|
|-- results/                       # Experiment outputs (gitignored)
|   +-- <game_key>/<model>__<prompt_id>.json
|
|-- analytics/                     # Aggregated summaries (gitignored)
|   +-- <game_key>/summary.{json,csv}
|
+-- images/                        # Generated plots (gitignored)
    +-- <game_key>/<model>/*.png
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

For each `(game, model, prompt)` combination:

| Output | Location |
|--------|----------|
| Individual result | `results/<game_key>/<model>__<prompt_id>.json` |
| Combined results | `results/<game_key>/all_results.json` |
| Per-prompt plots | `images/<game_key>/<model>/*.png` |

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
| **GPU Partition** | `gpu_standard` | Requires `--account=YOUR_GROUP` |
| **GPU Type** | NVIDIA V100S | 32 GB VRAM, request via `--gres=gpu:volta:1` |
| **CUDA Module** | `cuda11/11.8` | Loaded in all scripts |
| **Python Env** | micromamba | `micromamba activate qcbai` |
| **Model Storage** | `/xdisk/` | Avoid 50GB `/home` limit |
| **Max Walltime** | 10 days | Scripts use 48-72h |

**Before first use:** Update `--account=YOUR_GROUP` in all `.slurm` files with your PI group name.

### Step-by-Step Workflow

```bash
# ---- Step 1: Start Ollama server on a GPU node ----
sbatch slurm/start_ollama.slurm

# Check the log for the assigned hostname:
cat slurm/logs/ollama_<jobid>.out
# Look for: "Connect from experiment jobs with:
#   export OLLAMA_HOST=http://<hostname>:11434"

# ---- Step 2: Set OLLAMA_HOST ----
export OLLAMA_HOST=http://<hostname>:11434

# ---- Step 3: Submit experiments ----

# Option A: All 7 games via job array (recommended)
bash slurm/submit_all.sh

# Option B: Single game
sbatch slurm/run_single_game.slurm prisoners_dilemma

# Option C: Single game, specific model
sbatch slurm/run_single_game.slurm dictator_game llama3.2:latest
```

### SLURM Scripts Reference

| Script | Purpose | Resources |
|--------|---------|-----------|
| `start_ollama.slurm` | Launch Ollama server on Puma GPU node | 1x V100S, 64gb, 8 CPUs, 72h |
| `run_all_games.slurm` | Job array (indices 0-6) for all 7 games | 1x V100S, 32gb, 4 CPUs, 48h each |
| `run_single_game.slurm` | Single game experiment job | 1x V100S, 32gb, 4 CPUs, 48h |
| `submit_all.sh` | Generate prompts + submit job array | Runs on login node |

### Job Array Mapping

The `run_all_games.slurm` maps `$SLURM_ARRAY_TASK_ID` to games:

| Index | Game |
|:-----:|------|
| 0 | `prisoners_dilemma` |
| 1 | `dictator_game` |
| 2 | `chicken_game` |
| 3 | `public_goods_game` |
| 4 | `public_goods_game_boolean` |
| 5 | `ultimatum_game` |
| 6 | `trust_game` |

### Before You Submit (Checklist)

1. Update `--account=YOUR_GROUP` in all `.slurm` files
2. Create your micromamba environment: `micromamba create -n qcbai python=3.11`
3. Install requirements: `pip install -r requirements.txt`
4. Set Ollama model storage path in `~/.bashrc`:
   ```bash
   export OLLAMA_MODELS="/xdisk/YOUR_PI_GROUP/$USER/.ollama/models"
   ```
5. Start Ollama server first and note the hostname
6. Set `OLLAMA_HOST` before submitting experiment jobs
7. Create log directory: `mkdir -p slurm/logs`

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
| `sbatch: error: Batch job submission failed: Invalid account` | Update `--account=YOUR_GROUP` in `.slurm` files |
| Out of disk space on `/home` | Move models/caches to `/xdisk` or `/groups` |
| `No module named 'ollama'` | Activate environment: `source ~/.bashrc && micromamba activate qcbai` |
| GPU job pending long time | Try `gpu_windfall` partition (preemptible but starts faster) |
| Ollama connection refused | Check that `OLLAMA_HOST` matches the server node hostname |

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

### Performance Estimate

| Scenario | Prompts | Runs | Concurrent | Total Calls | Est. Time |
|----------|:-------:|:----:|:----------:|:-----------:|:---------:|
| 1 game, 1 model | 79 | 100 | 8 | 7,900 | ~30 min |
| 1 game, 2 models | 79 | 100 | 8 | 15,800 | ~1 hour |
| 7 games, 2 models | 553 | 100 | 8 | 110,600 | ~7 hours* |

*With SLURM job array, 7 games run in parallel on separate nodes --> ~1 hour wall-clock.*

---

## Configuration

### Models

Edit `qcbai/llm/models.yaml` to add, remove, or configure models:

```yaml
ollama:
  - name: "llama3.2:latest"
    slug: "llama3.2"
    temperature: 0.7

  - name: "mistral:latest"
    slug: "mistral"
    temperature: 0.7

  # Uncomment to enable additional models:
  # - name: "llama3.3:latest"
  #   slug: "llama3.3"
  #   temperature: 0.7
  # - name: "phi4:latest"
  #   slug: "phi4"
  #   temperature: 0.7
  # - name: "gemma3:27b"
  #   slug: "gemma3-27b"
  #   temperature: 0.7
```

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
