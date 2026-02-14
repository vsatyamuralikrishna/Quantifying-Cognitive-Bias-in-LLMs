from typing import Any, Optional

import argparse
import asyncio
import json
import os

from pydantic import BaseModel

from ollama_run import run_simple_experiment_async
from datetime import datetime, timezone

class RunBaseArguments(BaseModel):
    """Base arguments for experiment configuration."""

    ModelName: str
    ModelAlias: str
    GameType: str
    Iterations: int
    BatchSize: int
    Temperature: float

async def run_experiment_async(arguments: RunBaseArguments):
    """Run the experiment asynchronously."""
    prompts_root_path = f"./prompts/{arguments.GameType}"

    prompt_files = [
        f for f in os.listdir(prompts_root_path)
        if os.path.isfile(os.path.join(prompts_root_path, f)) and f.endswith(".json")
    ]

    all_results = []

    for prompt_filename in prompt_files:
        prompt_path = os.path.join(prompts_root_path, prompt_filename)
        with open(prompt_path, "r") as f:
            data = json.load(f)
        # Handle base JSON structure: either simple 'prompt_id' and 'prompt', or array/list structure
        if "prompt_id" in data:
            prompt_id = data.get("prompt_id")
        else:
            raise ValueError(f"Prompt ID not found in {prompt_filename}")
        # If 'prompt' is a list of prompt messages, reconstruct the prompt text for the model
        if "prompt" in data and isinstance(data.get("prompt"), list):
            prompt = data["prompt"]
        else:
            raise ValueError(f"Prompt is not a list of prompt messages in {prompt_filename}")

        # Construct new arguments for each prompt file
        prompt_args = arguments.model_copy(update={"Prompt": prompt, "PromptID": prompt_id})
        results = await run_simple_experiment_async(arguments=prompt_args)
        all_results.append(results)
    # Save all_results to a file. Build an output filename based on the model alias, game type, and current UTC datetime.
    output_dir = f"./experiment_results/{arguments.GameType}/{arguments.ModelAlias}"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_filename = f"{arguments.GameType.lower()}_{arguments.ModelAlias.lower()}_{timestamp}_full_results.json"
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, "w") as outfile:
        json.dump(all_results, outfile, indent=2)
    print(f"All results saved to {output_path}")
    return all_results



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str, default="llama3.2:latest", help="Ollama model name")
    parser.add_argument("--model-alias", type=str, default="llama32", help="Short alias for output paths")
    parser.add_argument("--game-type", type=str, default="PrisonersDilemma", help="Game type name")
    parser.add_argument("--iterations", type=int, default=50, help="Total number of runs")
    parser.add_argument("--batch-size", type=int, default=5, help="Concurrent runs per batch")
    parser.add_argument("--temperature", type=float, default=0.7, help="Model temperature")
    args = parser.parse_args()
    arguments = RunBaseArguments(
        ModelName=args.model_name,
        ModelAlias=args.model_alias,
        GameType=args.game_type,
        Iterations=args.iterations,
        BatchSize=args.batch_size,
        Temperature=args.temperature,
    )
    results = asyncio.run(run_experiment_async(arguments=arguments))
    print(results)


# python3 main.py --model-name llama3.2:latest --model-alias llama3.2 --game-type PrisonersDillemma --iterations 10 --batch-size 5 --temperature 0.7
