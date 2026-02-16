import json
import uuid
import time
import asyncio
from pathlib import Path
from typing import List
from tqdm import tqdm

from qcbai.llm.base import ModelRunner
from qcbai.analytics.types import ExperimentResult
from qcbai.analytics.formatter import create_result_entry
from qcbai.games.game_config import GameConfig
from qcbai.utils.visualizer import plot_prompt_result, plot_model_summary


def load_prompt_files(prompt_dir: Path) -> List[Path]:
    return sorted(prompt_dir.glob("*.json"))


async def _async_single_run(runner: ModelRunner, messages: list, temperature: float, run_idx: int) -> dict:
    """Execute a single async LLM call."""
    start_time = time.perf_counter()
    output = await runner.arun_prompt(messages, temperature=temperature)
    end_time = time.perf_counter()

    return {
        "id": str(uuid.uuid4()),
        "response_text": output.get("text", ""),
        "response": output.get("response", None),
        "decision": output.get("decision", ""),
        "reason": output.get("reason", ""),
        "response_time": round(end_time - start_time, 4),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "run_index": run_idx,
    }


async def run_prompt_with_model_async(
    runner: ModelRunner,
    model_type: str,
    prompt_data: dict,
    game_config: GameConfig,
    runs: int,
    temperature: float,
    batch_size: int = 5,
) -> ExperimentResult:
    """
    Run a prompt N times against a model using async batched execution.

    Processes runs in batches (like the working pattern):
    - Each batch fires batch_size concurrent requests via asyncio.gather
    - Small sleep between batches to avoid overwhelming the server
    - All runs happen within the SAME event loop (no asyncio.run per prompt)
    """
    messages = prompt_data["prompt"]
    responses = []
    num_batches = (runs + batch_size - 1) // batch_size

    for batch_idx in range(num_batches):
        batch_start = batch_idx * batch_size
        batch_end = min(batch_start + batch_size, runs)
        batch_iters = list(range(batch_start, batch_end))

        tasks = [
            _async_single_run(runner, messages, temperature, i)
            for i in batch_iters
        ]
        batch_results = await asyncio.gather(*tasks, return_exceptions=False)

        for result in batch_results:
            if isinstance(result, Exception):
                responses.append({
                    "id": str(uuid.uuid4()),
                    "response_text": "",
                    "response": None,
                    "decision": "",
                    "reason": f"Error: {result}",
                    "response_time": 0.0,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                })
            else:
                responses.append(result)

        if batch_idx < num_batches - 1:
            await asyncio.sleep(0.1)

    return create_result_entry(
        model_slug=runner.get_slug(),
        model_name=runner.get_name(),
        model_type=model_type,
        prompt_id=prompt_data["prompt_id"],
        persona_dict=prompt_data,
        prompt_style=prompt_data.get("style", "neutral"),
        prompt_responses=responses,
        execution_id=str(uuid.uuid4()),
        game_type=game_config.key,
        game_config=game_config,
        temperature=temperature,
        additional_config=runner.get_metadata(),
    )


def _append_to_json_file(filepath: Path, entry: dict):
    """Load a JSON array file, append an entry, and write it back."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    if not isinstance(data, list):
        data = []

    data.append(entry)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def save_result(result: ExperimentResult, results_dir: Path, combined_path: Path):
    """
    Save an individual experiment result and append to combined files.

    Directory structure:
        results/<game_key>/<model_slug>/<prompt_id>.json     (individual)
        results/<game_key>/<model_slug>/all_results.json     (combined for this model)
        results/<game_key>/all_results.json                  (combined across all models)
    """
    model_dir = results_dir / result.model_slug
    model_dir.mkdir(parents=True, exist_ok=True)
    combined_path.parent.mkdir(parents=True, exist_ok=True)

    result_dict = result.dict()

    filename = f"{result.prompt_id}.json"
    with open(model_dir / filename, "w") as f:
        json.dump(result_dict, f, indent=2)

    model_combined_path = model_dir / "all_results.json"
    _append_to_json_file(model_combined_path, result_dict)

    _append_to_json_file(combined_path, result_dict)


async def run_all_experiments_async(
    prompt_dir: Path,
    results_dir: Path,
    all_results_file: Path,
    images_dir: Path,
    model_runners: List[ModelRunner],
    model_type: str,
    game_config: GameConfig,
    runs: int = 100,
    temperature: float = 0.7,
    max_concurrent: int = 1,
):
    """
    Run experiments for a single game across all models and prompts.
    Fully async: runs inside a single event loop with batched execution.
    """
    prompt_files = load_prompt_files(prompt_dir)
    total_prompts = len(prompt_files)
    total_calls = total_prompts * runs * len(model_runners)

    mode = "async" if max_concurrent > 1 else "sequential"
    print(f"  Loaded {total_prompts} prompts and {len(model_runners)} models")
    print(f"  Game: {game_config.name} | Runs per prompt: {runs}")
    print(f"  Concurrency: {max_concurrent} ({mode}) | Total LLM calls: {total_calls}")

    for runner in model_runners:
        print(f"\n  Running: {runner.get_name()}")
        model_results = []
        start_model = time.time()

        for prompt_path in tqdm(prompt_files, desc=f"  {runner.get_slug()}"):
            with open(prompt_path, "r") as f:
                prompt_data = json.load(f)

            result = await run_prompt_with_model_async(
                runner, model_type, prompt_data, game_config,
                runs, temperature, batch_size=max_concurrent,
            )
            save_result(result, results_dir, all_results_file)

            if game_config.response_type == "binary":
                model_results.append({
                    "prompt_id": result.prompt_id,
                    "choice_a_label": game_config.trust_choice,
                    "choice_b_label": game_config.distrust_choice,
                    "choice_a_percent": round(
                        result.trust_estimate_probability_distribution * 100, 1
                    ),
                    "choice_b_percent": round(
                        result.distrust_estimate_probability_distribution * 100, 1
                    ),
                })
            else:
                model_results.append({
                    "prompt_id": result.prompt_id,
                    "mean_amount": result.mean_amount,
                    "max_amount": game_config.max_amount,
                    "generosity_percent": round(
                        result.trust_estimate_probability_distribution * 100, 1
                    ),
                })

            plot_prompt_result(
                prompt_id=result.prompt_id,
                model_slug=runner.get_slug(),
                game_config=game_config,
                result=result,
                images_dir=images_dir,
            )

        elapsed = time.time() - start_model
        print(f"  {runner.get_slug()} completed in {elapsed:.1f}s "
              f"({elapsed/total_prompts:.1f}s/prompt, "
              f"{total_prompts*runs/elapsed:.1f} calls/sec)")

        plot_model_summary(
            model_slug=runner.get_slug(),
            summaries=model_results,
            game_config=game_config,
            images_dir=images_dir,
        )

    print(f"\n  Results saved to '{results_dir}'")
    print(f"  Plots saved to '{images_dir}'")
