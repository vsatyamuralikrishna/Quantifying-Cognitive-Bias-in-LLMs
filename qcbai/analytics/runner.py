import json
import uuid
import time
import asyncio
import random
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
    """Execute a single async LLM call. Used for concurrent batches."""
    start_time = time.time()
    await asyncio.sleep(random.uniform(0.001, 0.01))
    output = await runner.arun_prompt(messages, temperature=temperature)
    end_time = time.time()

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


def _sync_single_run(runner: ModelRunner, messages: list, temperature: float, run_idx: int) -> dict:
    """Execute a single synchronous LLM call. Used for sequential mode."""
    start_time = time.time()
    output = runner.run_prompt(messages, temperature=temperature)
    end_time = time.time()

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


async def _run_concurrent_batch(
    runner: ModelRunner,
    messages: list,
    temperature: float,
    runs: int,
    max_concurrent: int,
) -> list:
    """
    Fire N async LLM calls with a concurrency limit using asyncio.Semaphore.

    This is the core concurrency engine:
    - Creates a semaphore with max_concurrent slots
    - Launches all N runs as async tasks
    - Semaphore ensures at most max_concurrent are in-flight at once
    - Results are collected in order via asyncio.gather
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _limited_run(idx: int) -> dict:
        async with semaphore:
            try:
                return await _async_single_run(runner, messages, temperature, idx)
            except Exception as e:
                return {
                    "id": str(uuid.uuid4()),
                    "response_text": "",
                    "response": None,
                    "decision": "",
                    "reason": f"Error: {e}",
                    "response_time": 0.0,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "run_index": idx,
                }

    tasks = [_limited_run(i) for i in range(runs)]
    return await asyncio.gather(*tasks)


def run_prompt_with_model(
    runner: ModelRunner,
    model_type: str,
    prompt_data: dict,
    game_config: GameConfig,
    runs: int,
    temperature: float,
    max_concurrent: int = 1,
) -> ExperimentResult:
    """
    Run a prompt N times against a model.

    When max_concurrent > 1, uses asyncio to fire concurrent async requests
    to the Ollama server, significantly reducing wall-clock time.
    When max_concurrent <= 1, falls back to simple sequential execution.

    Args:
        max_concurrent: Number of simultaneous async requests.
                        Must match OLLAMA_NUM_PARALLEL on the server.
    """
    messages = prompt_data["prompt"]

    if max_concurrent <= 1:
        # Sequential (original behavior)
        responses = []
        for i in range(runs):
            responses.append(_sync_single_run(runner, messages, temperature, i))
    else:
        # Async concurrent execution
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Already inside an event loop (e.g. Jupyter notebook)
            # Fall back to thread-based execution
            import nest_asyncio
            nest_asyncio.apply()
            responses = list(asyncio.get_event_loop().run_until_complete(
                _run_concurrent_batch(runner, messages, temperature, runs, max_concurrent)
            ))
        else:
            responses = list(asyncio.run(
                _run_concurrent_batch(runner, messages, temperature, runs, max_concurrent)
            ))

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
    # Create model-specific subdirectory under game results
    model_dir = results_dir / result.model_slug
    model_dir.mkdir(parents=True, exist_ok=True)
    combined_path.parent.mkdir(parents=True, exist_ok=True)

    result_dict = result.dict()

    # Save individual result under model subdirectory
    filename = f"{result.prompt_id}.json"
    with open(model_dir / filename, "w") as f:
        json.dump(result_dict, f, indent=2)

    # Append to per-model combined results
    model_combined_path = model_dir / "all_results.json"
    _append_to_json_file(model_combined_path, result_dict)

    # Append to game-level combined results (across all models)
    _append_to_json_file(combined_path, result_dict)


def run_all_experiments(
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

    Args:
        max_concurrent: Number of concurrent async requests per prompt batch.
                        Set to 1 for sequential, 4-8 for concurrent on HPC.
                        Ollama server must have OLLAMA_NUM_PARALLEL >= max_concurrent.
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

            result = run_prompt_with_model(
                runner, model_type, prompt_data, game_config,
                runs, temperature, max_concurrent=max_concurrent,
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
