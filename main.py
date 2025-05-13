#!/usr/bin/env python3

import sys
from pathlib import Path
import argparse

def main(target_model=None):
    # Root directory setup
    ROOT = Path(__file__).parent
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))

    # Import QCBai modules
    from qcbai.analytics.runner import run_all_experiments
    from qcbai.llm.registry import get_all_model_runners

    # Configuration
    PROMPT_DIR = ROOT / "prompts"
    RESULTS_DIR = ROOT / "results"
    ALL_RESULTS_FILE = RESULTS_DIR / "all_results.json"
    IMAGES_DIR = ROOT / "images"
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    NUM_RUNS = 100
    TEMPERATURE = 0.7
    MODEL_TYPES = ["ollama"]

    for model_type in MODEL_TYPES:
        print(f"\n🔧 Loading models of type: {model_type}")
        all_model_runners = get_all_model_runners(model_type)

        # Filter based on --model argument (match slug or name)
        if target_model:
            model_runners = [
                m for m in all_model_runners
                if target_model == m.get_slug() or target_model == m.get_name()
            ]
            if not model_runners:
                print(f"❌ Model '{target_model}' not found among available models:")
                for m in all_model_runners:
                    print(f"  - name: {m.get_name()}, slug: {m.get_slug()}")
                return
        else:
            model_runners = all_model_runners

        print(f"📋 Loaded {len(model_runners)} model(s): {[m.get_name() for m in model_runners]}")
        print(f"🧪 Running: {[m.get_slug() for m in model_runners]}")

        run_all_experiments(
            prompt_dir=PROMPT_DIR,
            results_dir=RESULTS_DIR,
            all_results_file=ALL_RESULTS_FILE,
            images_dir=IMAGES_DIR,
            model_runners=model_runners,
            model_type=model_type,
            runs=NUM_RUNS,
            temperature=TEMPERATURE
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        type=str,
        help="Run a specific model by name or slug (e.g., 'phi4' or 'phi4:latest')"
    )
    args = parser.parse_args()
    main(target_model=args.model)