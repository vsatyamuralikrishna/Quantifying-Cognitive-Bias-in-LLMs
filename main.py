#!/usr/bin/env python3

import sys
from pathlib import Path
import json

# def main():
#     # Adjust path to root directory (for qcbai imports)
#     ROOT = Path(__file__).parent
#     if str(ROOT) not in sys.path:
#         sys.path.append(str(ROOT))

#     # 📁 Import from QCBai
#     from qcbai.analytics.runner import run_all_experiments
#     from qcbai.llm.registry import get_all_model_runners

#     # ✅ Experiment config
#     PROMPT_DIR = ROOT / "prompts"
#     RESULTS_DIR = ROOT / "results"
#     ALL_RESULTS_FILE = RESULTS_DIR / "all_results.json"
#     IMAGES_DIR = ROOT / "images"
#     IMAGES_DIR.mkdir(parents=True, exist_ok=True)

#     NUM_RUNS = 100 # or 100 for full
#     TEMPERATURE = 0.7
#     MODEL_TYPES = ["ollama"]  # Only Ollama models

#     # 🚀 Run all Ollama experiments
#     for model_type in MODEL_TYPES:
#         print(f"\n🔧 Loading models of type: {model_type}")
#         model_runners = get_all_model_runners(model_type)

#         run_all_experiments(
#             prompt_dir=PROMPT_DIR,
#             results_dir=RESULTS_DIR,
#             all_results_file=ALL_RESULTS_FILE,
#             images_dir=IMAGES_DIR,
#             model_runners=model_runners,
#             model_type=model_type,
#             runs=NUM_RUNS,
#             temperature=TEMPERATURE
#         )

# if __name__ == "__main__":
#     main()


def main():
    # ——— TensorFlow GPU setup ———

    # Adjust path to root directory (for qcbai imports)
    ROOT = Path(__file__).parent
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))

    # 📁 Import from QCBai
    from qcbai.analytics.runner import run_all_experiments
    from qcbai.llm.registry import get_all_model_runners

    # ✅ Experiment config
    PROMPT_DIR = ROOT / "prompts"
    RESULTS_DIR = ROOT / "results"
    ALL_RESULTS_FILE = RESULTS_DIR / "all_results.json"
    IMAGES_DIR = ROOT / "images"
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    NUM_RUNS = 100
    TEMPERATURE = 0.7
    MODEL_TYPES = ["ollama"]  # you can add other model types later

    # 🚀 Run experiments
    for model_type in MODEL_TYPES:
        print(f"\n🔧 Loading models of type: {model_type}")
        model_runners = get_all_model_runners(model_type)

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
    main()

