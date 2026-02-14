#!/usr/bin/env python3
"""
Aggregate and analyze results across all games.

Reads the all_results.json from each game's results folder and produces
summary analytics CSV and JSON files.

Usage:
    python analyze_results.py                          # all games
    python analyze_results.py --game prisoners_dilemma
"""

import sys
import json
import csv
import argparse
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qcbai.games.game_config import ALL_GAME_KEYS, GAME_CONFIGS


def load_results(game_key: str) -> list:
    results_file = ROOT / "results" / game_key / "all_results.json"
    if not results_file.exists():
        print(f"  No results found for {game_key} at {results_file}")
        return []
    with open(results_file, "r") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def analyze_binary_game(results: list, game_key: str) -> list:
    """Analyze binary-choice games (Prisoner's Dilemma, Chicken)."""
    game_config = GAME_CONFIGS[game_key]
    summary_rows = []

    # Group by model -> persona
    grouped = defaultdict(list)
    for r in results:
        key = (r.get("model_name", "unknown"), r.get("persona", "neutral"), r.get("style", "base"))
        grouped[key].append(r)

    for (model, persona, style), entries in sorted(grouped.items()):
        all_results = []
        for entry in entries:
            all_results.extend(entry.get("result", []))

        total = len(all_results)
        trust_count = sum(all_results)
        distrust_count = total - trust_count

        summary_rows.append({
            "game": game_key,
            "model": model,
            "persona": persona,
            "style": style,
            "total_runs": total,
            f"{game_config.trust_choice}_count": trust_count,
            f"{game_config.distrust_choice}_count": distrust_count,
            f"{game_config.trust_choice}_pct": round(trust_count / total * 100, 2) if total else 0,
            f"{game_config.distrust_choice}_pct": round(distrust_count / total * 100, 2) if total else 0,
            "trust_estimate": round(trust_count / total, 4) if total else 0,
        })

    return summary_rows


def analyze_amount_game(results: list, game_key: str) -> list:
    """Analyze amount-based games (Dictator, Public Goods, Ultimatum, Trust)."""
    game_config = GAME_CONFIGS[game_key]
    summary_rows = []

    grouped = defaultdict(list)
    for r in results:
        key = (r.get("model_name", "unknown"), r.get("persona", "neutral"), r.get("style", "base"))
        grouped[key].append(r)

    for (model, persona, style), entries in sorted(grouped.items()):
        all_amounts = []
        for entry in entries:
            all_amounts.extend(entry.get("result", []))

        total = len(all_amounts)
        if total == 0:
            continue

        mean_amt = round(sum(all_amounts) / total, 2)
        max_amt = game_config.max_amount or 1
        generosity = round(mean_amt / max_amt * 100, 2)

        summary_rows.append({
            "game": game_key,
            "model": model,
            "persona": persona,
            "style": style,
            "total_runs": total,
            "mean_amount": mean_amt,
            "min_amount": min(all_amounts),
            "max_amount_given": max(all_amounts),
            "max_possible": max_amt,
            "generosity_pct": generosity,
        })

    return summary_rows


def save_analytics(rows: list, game_key: str):
    """Save analytics to CSV and JSON."""
    analytics_dir = ROOT / "analytics" / game_key
    analytics_dir.mkdir(parents=True, exist_ok=True)

    # JSON
    json_path = analytics_dir / "summary.json"
    with open(json_path, "w") as f:
        json.dump(rows, f, indent=2)

    # CSV
    if rows:
        csv_path = analytics_dir / "summary.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    print(f"  Analytics saved to {analytics_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Analyze experiment results")
    parser.add_argument("--game", type=str, action="append", default=None)
    args = parser.parse_args()

    games = args.game if args.game else ALL_GAME_KEYS

    for game_key in games:
        if game_key not in GAME_CONFIGS:
            print(f"Unknown game: {game_key}")
            continue

        game_config = GAME_CONFIGS[game_key]
        print(f"\n{'='*60}")
        print(f"Analyzing: {game_config.name}")
        print(f"{'='*60}")

        results = load_results(game_key)
        if not results:
            continue

        if game_config.response_type == "binary":
            rows = analyze_binary_game(results, game_key)
        else:
            rows = analyze_amount_game(results, game_key)

        save_analytics(rows, game_key)
        print(f"  {len(rows)} summary rows generated")

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
