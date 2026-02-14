#!/usr/bin/env python3
"""
Generate all prompts for all games (or a specific game).

Usage:
    python generate_prompts.py # all games
    python generate_prompts.py --game prisoners_dilemma
    python generate_prompts.py --game chicken_game --game trust_game
"""

import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qcbai.generators.prompts import PersonaPromptGenerator
from qcbai.games.game_config import GAME_CONFIGS, ALL_GAME_KEYS


def main():
    parser = argparse.ArgumentParser(description="Generate prompts for bias experiments")
    parser.add_argument(
        "--game",
        type=str,
        action="append",
        default=None,
        help=f"Game(s) to generate prompts for. Available: {ALL_GAME_KEYS}",
    )
    args = parser.parse_args()

    games = args.game if args.game else ALL_GAME_KEYS
    generator = PersonaPromptGenerator()

    for game_key in games:
        if game_key not in GAME_CONFIGS:
            print(f"Unknown game: {game_key}. Skipping.")
            continue

        game_config = GAME_CONFIGS[game_key]
        prompt_dir = ROOT / "prompts" / game_key

        print(f"\n{'='*60}")
        print(f"Generating prompts: {game_config.name}")
        print(f"  Output: {prompt_dir}")
        print(f"{'='*60}")

        generator.save_base_prompt(game_config, str(prompt_dir))
        generator.save_all_persona_prompts(game_config, str(prompt_dir))

    print(f"\nDone. Prompt directories created under: {ROOT / 'prompts'}/")


if __name__ == "__main__":
    main()
