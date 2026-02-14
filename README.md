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

## Quick Start

```bash
# Install
pip install -r requirements.txt
ollama pull llama3.2:latest

# Generate prompts (553 total across 7 games)
python generate_prompts.py

# Run an experiment
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
- **HPC-ready** with SLURM job arrays for UA Puma cluster (V100S GPUs)
- **Ollama integration** for local/HPC LLM inference
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
