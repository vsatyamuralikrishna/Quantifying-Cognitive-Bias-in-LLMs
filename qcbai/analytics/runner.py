import json
import uuid
import time
from pathlib import Path
from typing import List
from tqdm import tqdm

from qcbai.llm.base import ModelRunner
from qcbai.analytics.types import ExperimentResult
from qcbai.analytics.formatter import create_result_entry
from qcbai.utils.visualizer import plot_prompt_result, plot_model_summary


def load_prompt_files(prompt_dir: Path) -> List[Path]:
    return list(prompt_dir.glob("*.json"))


def run_prompt_with_model(
    runner: ModelRunner,
    model_type: str,
    prompt_data: dict,
    runs: int,
    temperature: float,
) -> ExperimentResult:
    responses = []
    for i in range(runs):
        start_time = time.time()
        output = runner.run_prompt(prompt_data["prompt"], temperature=temperature)
        end_time = time.time()

        responses.append({
            "id": str(uuid.uuid4()),
            "response_text": output.get("text", ""),
            "response": output.get("response", None),
            "decision": output.get("decision", ""),
            "reason": output.get("reason", ""),
            "response_time": round(end_time - start_time, 4),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })

    return create_result_entry(
        model_slug=runner.get_slug(),
        model_name=runner.get_name(),
        model_type=model_type,
        prompt_id=prompt_data["prompt_id"],
        persona_dict=prompt_data,
        prompt_style=prompt_data.get("style", "neutral"),
        prompt_responses=responses,
        execution_id=str(uuid.uuid4()),
        game_type="prisoners_dilemma",
        temperature=temperature,
        additional_config=runner.get_metadata()
    )


def save_result(result: ExperimentResult, results_dir: Path, combined_path: Path):
    results_dir.mkdir(parents=True, exist_ok=True)
    combined_path.parent.mkdir(parents=True, exist_ok=True)

    # Save individual result
    filename = f"{result.model_name}__{result.prompt_id}.json"
    with open(results_dir / filename, "w") as f:
        json.dump(result.dict(), f, indent=2)

    # Load or initialize combined results
    try:
        with open(combined_path, "r") as f:
            combined_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        combined_data = []

    # Ensure combined_data is a list
    if not isinstance(combined_data, list):
        combined_data = []

    # Append new result
    combined_data.append(result.dict())

    # Save combined results
    with open(combined_path, "w") as f:
        json.dump(combined_data, f, indent=2)


def run_all_experiments(
    prompt_dir: Path,
    results_dir: Path,
    all_results_file: Path,
    images_dir: Path,
    model_runners: List[ModelRunner],
    model_type: str,
    runs: int = 100,
    temperature: float = 0.7,
):
    prompt_files = load_prompt_files(prompt_dir)
    print(f"📋 Loaded {len(prompt_files)} prompts and {len(model_runners)} models")

    for runner in model_runners:
        print(f"\n🧪 Running: {runner.get_name()}")
        model_results = []

        for prompt_path in tqdm(prompt_files, desc=f"Model: {runner.get_slug()}"):
            with open(prompt_path, "r") as f:
                prompt_data = json.load(f)

            result = run_prompt_with_model(runner, model_type, prompt_data, runs, temperature)
            save_result(result, results_dir, all_results_file)

            model_results.append({
                "prompt_id": result.prompt_id,
                "implicate_percent": round((1 - result.trust_estimate_probability_distribution) * 100, 1),
                "silent_percent": round(result.trust_estimate_probability_distribution * 100, 1)
            })

            plot_prompt_result(
                prompt_id=result.prompt_id,
                model_slug=runner.get_slug(),
                implicate=model_results[-1]["implicate_percent"],
                silent=model_results[-1]["silent_percent"]
            )

        plot_model_summary(runner.get_slug(), model_results)

    print(f"\n✅ All results saved to '{results_dir}' and plots to '{images_dir}'")
