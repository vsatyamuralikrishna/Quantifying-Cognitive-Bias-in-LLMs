#!/usr/bin/env python3
"""
Main experiment runner for cognitive bias in LLMs.

Runs experiments for one or more games across all configured Ollama models.
Designed to work on HPC with SLURM job arrays (one game per job).

Usage:
    python main.py --game prisoners_dilemma
    python main.py --game prisoners_dilemma --model llama3.2:latest
    python main.py --game all
    python main.py --game prisoners_dilemma --runs 100 --temperature 0.7
"""

import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qcbai.analytics.runner import run_all_experiments
from qcbai.llm.registry import get_all_model_runners
from qcbai.games.game_config import GAME_CONFIGS, ALL_GAME_KEYS, get_game_config


def main():
    parser = argparse.ArgumentParser(
        description="Run LLM bias experiments for game-theory scenarios"
    )
    parser.add_argument(
        "--game",
        type=str,
        required=True,
        help=f"Game to run. Use 'all' for all games. Available: {ALL_GAME_KEYS}",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Specific model name filter (e.g., 'llama3.2:latest')",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=100,
        help="Number of runs per prompt (default: 100)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature (default: 0.7)",
    )
    parser.add_argument(
        "--model-type",
        type=str,
        default="ollama",
        choices=["ollama", "transformers", "all"],
        help="Model backend type (default: ollama)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help=(
            "Concurrent threads for the N runs per prompt (default: 8). "
            "Set to 1 for sequential. On HPC, match to OLLAMA_NUM_PARALLEL."
        ),
    )
    args = parser.parse_args()

    # Determine which games to run
    if args.game == "all":
        games_to_run = ALL_GAME_KEYS
    else:
        games_to_run = [args.game]

    # Load models
    all_runners = get_all_model_runners(args.model_type)
    if args.model:
        runners = [r for r in all_runners if args.model in r.get_name()]
        if not runners:
            print(f"Model '{args.model}' not found. Available: {[r.get_name() for r in all_runners]}")
            sys.exit(1)
    else:
        runners = all_runners

    print(f"Models:  {[r.get_name() for r in runners]}")
    print(f"Games:   {games_to_run}")
    print(f"Runs:    {args.runs} per prompt")
    print(f"Workers: {args.workers} concurrent threads")
    print(f"Temp:    {args.temperature}")

    # Run each game
    for game_key in games_to_run:
        game_config = get_game_config(game_key)

        prompt_dir = ROOT / "prompts" / game_key
        results_dir = ROOT / "results" / game_key
        images_dir = ROOT / "images" / game_key
        all_results_file = results_dir / "all_results.json"

        if not prompt_dir.exists():
            print(f"\nPrompts not found for '{game_key}' at {prompt_dir}")
            print("Run: python generate_prompts.py --game", game_key)
            continue

        print(f"\n{'='*60}")
        print(f"GAME: {game_config.name}")
        print(f"  Prompts:  {prompt_dir}")
        print(f"  Results:  {results_dir}")
        print(f"  Images:   {images_dir}")
        print(f"{'='*60}")

        run_all_experiments(
            prompt_dir=prompt_dir,
            results_dir=results_dir,
            all_results_file=all_results_file,
            images_dir=images_dir,
            model_runners=runners,
            model_type=args.model_type,
            game_config=game_config,
            runs=args.runs,
            temperature=args.temperature,
            max_workers=args.workers,
        )

    print("\nAll experiments complete.")


if __name__ == "__main__":
    main()
