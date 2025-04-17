import json
import uuid
from pathlib import Path
from typing import List
from tqdm import tqdm

from qcbai.llm.base import ModelRunner
from qcbai.analytics.types import ExperimentResult
from qcbai.analytics.formatter import create_result_entry
from qcbai.utils.visualizer import plot_prompt_result, plot_model_summary


def load_prompt_files(prompt_dir: Path) -> List[Path]:
    """
    Load all .json prompt files from a directory.
    """
    return list(prompt_dir.glob("*.json"))


def run_prompt_with_model(
    runner: ModelRunner,
    model_type: str,
    prompt_data: dict,
    runs: int,
    temperature: float,
) -> ExperimentResult:
    """
    Run a single prompt N times through a given model.
    """
    responses = []
    for _ in range(runs):
        output = runner.run_prompt(prompt_data["prompt"], temperature=temperature)
        responses.append(output.get("text", ""))

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
    """
    Save a single result to its own file and append to all_results.json.
    """
    results_dir.mkdir(parents=True, exist_ok=True)
    combined_path.parent.mkdir(parents=True, exist_ok=True)

    # ✅ Save individual JSON result
    file_name = f"{result.model_name}__{result.prompt_id}.json"
    with open(results_dir / file_name, "w") as f:
        json.dump(result.dict(), f, indent=2)

    # ✅ Append to all_results.json (without deduplication)
    if combined_path.exists():
        with open(combined_path, "r") as f:
            combined_data = json.load(f)
    else:
        combined_data = []

    combined_data.append(result.dict())

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
    """
    Run all prompts through all model runners and save full structured results + plots.
    """
    prompt_files = load_prompt_files(prompt_dir)
    print(f"📋 Loaded {len(prompt_files)} prompts and {len(model_runners)} models")

    for runner in model_runners:
        model_name = runner.get_name()
        print(f"\n🧪 Running: {model_name}")
        model_results = []

        for prompt_path in tqdm(prompt_files, desc=f"Model: {runner.get_slug()}"):
            with open(prompt_path, "r") as f:
                prompt_data = json.load(f)

            # Run the model on this prompt
            result = run_prompt_with_model(
                runner,
                model_type,
                prompt_data,
                runs,
                temperature
            )

            # Save the result (individual + combined)
            save_result(result, results_dir, all_results_file)

            # 📊 Plot for this prompt
            plot_prompt_result(
                prompt_id=result.prompt_id,
                model_slug=result.model_name,
                implicate=round((1 - result.trust_estimate_probability_distribution) * 100, 1),
                silent=round(result.trust_estimate_probability_distribution * 100, 1)
            )

            model_results.append({
                "prompt_id": result.prompt_id,
                "implicate_percent": round((1 - result.trust_estimate_probability_distribution) * 100, 1),
                "silent_percent": round(result.trust_estimate_probability_distribution * 100, 1)
            })

        # 📊 Summary chart for model
        plot_model_summary(runner.get_slug(), model_results)

    print(f"\n✅ All results saved to '{results_dir}' and plots to '{images_dir}'")