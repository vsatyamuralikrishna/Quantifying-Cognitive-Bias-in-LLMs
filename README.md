# Quantifying Cognitive Bias in LLMs

Measuring demographic bias in Large Language Model decision-making through game-theory experiments.

## About

This framework tests whether LLMs change their decisions in classic economic games based on a partner's described **gender**, **race**, or **ethnicity**. Each game is played with 26 demographic personas across 3 prompt styles, and every prompt is repeated 100 times to build statistical distributions.

## Games

| Game | Type | Decision |
|------|:----:|----------|
| Prisoner's Dilemma | Binary | Silent or Implicate |
| Chicken Game | Binary | Swerve or Stay |
| Public Goods Game | Binary / Amount | Contribute or Not / $0-$20 |
| Dictator Game | Amount | $0-$10 |
| Ultimatum Game | Amount | $0-$10 |
| Trust Game | Amount | $0-$10 |

## Models

All 7 Ollama models used in the study:

| Model | Size | Slug |
|-------|-----:|------|
| llama3.2:latest | 2 GB | llama3.2 |
| mistral:latest | 4.1 GB | mistral |
| phi4:latest | 9.1 GB | phi4 |
| mistral-small3.1:latest | 15 GB | mistral-small3.1 |
| gemma3:27b | 17 GB | gemma3-27b |
| qwen2.5:32b | 19 GB | qwen2.5-32b |
| llama3.3:latest | 42 GB | llama3.3 |

## Quick Start

```bash
# Install
pip install -r requirements.txt
ollama pull llama3.2:latest

# Generate prompts (553 total across 7 games)
python generate_prompts.py

# Run a single experiment (1 game, 1 model)
python main.py --game prisoners_dilemma --model llama3.2:latest --runs 100 --concurrent 8

# Run all models on a game
python main.py --game prisoners_dilemma --runs 100 --concurrent 8

# Analyze results
python analyze_results.py --game prisoners_dilemma
```

## Project Structure

```
main.py                  # Run experiments
generate_prompts.py      # Generate prompt files
analyze_results.py       # Aggregate results
qcbai/                   # Core package
  games/                 #   Game configs & prompt templates
  generators/            #   Persona prompt generator
  analytics/             #   Experiment runner & response parsers
  llm/                   #   Ollama model interface & config
  constants/             #   Demographic persona definitions
  utils/                 #   Visualization
slurm/                   # HPC job scripts
docs/                    # Detailed documentation
```

## Key Features

- **7 game-theory scenarios** covering cooperation, fairness, trust, and risk
- **79 prompts per game** (26 personas x 3 styles + 1 neutral baseline)
- **Async concurrent execution** via asyncio + ollama.AsyncClient
- **HPC-ready** with SLURM 2D job arrays (7 games × 7 models = 49 jobs) for UA Puma cluster
- **Singularity-based Ollama** for GPU inference on HPC nodes (V100S)
- **Structured JSON output** with automated CSV analytics

## Documentation

See [`docs/EXECUTION.md`](docs/EXECUTION.md) for detailed documentation covering:

- Full CLI reference and examples
- UA HPC (Puma) setup, SLURM workflow, and troubleshooting
- Concurrency tuning and performance estimates
- Model and game configuration
- Response parsing internals

## Tech Stack

- **Python 3.10+** with Pydantic, Matplotlib, NumPy
- **Ollama** for LLM inference
- **SLURM** for HPC job scheduling

## License

Academic research project. Contact the authors for usage and citation information.
