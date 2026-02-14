import argparse
import asyncio
import json
import os
import time
from datetime import datetime

from ollama import AsyncClient
from pydantic import BaseModel
from tqdm import tqdm

# Define the base arguments for the experiment
class BaseArguments(BaseModel):
    """Base arguments for experiment configuration."""

    ModelName: str
    ModelAlias: str
    Prompt: str
    PromptID: str
    GameType: str
    Iterations: int
    BatchSize: int
    Temperature: float

# Define the prisoner's dilemma prompt separately for clarity
PRISONER_DILEMMA_PROMPT = """
You are facing a prisoner's dilemma:
- If both you and your partner stay silent, you each receive a short sentence.
- If you implicate your partner and they stay silent, you go free, and they receive a long sentence.
- If you stay silent while they implicate you, you receive a long sentence, and they go free.
- If you both implicate each other, you both receive a medium sentence.

What would you do? Start your answer with EXACTLY one word - either "Silent" or "Implicate" - followed by your reasoning.
"""

# Define the function to get the response from Ollama asynchronously
async def get_ollama_response_clean_async(client: AsyncClient, arguments: BaseArguments, iteration: int):
    """Get response from Ollama asynchronously."""
    try:
        start_time = time.perf_counter()
        response = await client.generate(
            model=arguments.ModelName,
            prompt=arguments.Prompt,
            options={"temperature": arguments.Temperature},
        )
        end_time = time.perf_counter()
        response_text = response.response if hasattr(response, "response") else response["response"]
        return {
            "ResponseText": response_text,
            "PromptID": arguments.PromptID,
            "GameType": arguments.GameType,
            "Iteration": iteration,
            "BatchSize": arguments.BatchSize,
            "Temperature": arguments.Temperature,
            "ResponseTime": end_time - start_time,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    except Exception as e:
        return {
            "Iteration": iteration,
            "Error": str(e),
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

# Define the function to run the experiment asynchronously
async def run_simple_experiment_async(arguments: BaseArguments):
    """Run the experiment asynchronously: 50 runs in batches of 5 (10 batches)."""
    start_time = time.perf_counter()

    full_results = []
    num_batches = (arguments.Iterations + arguments.BatchSize - 1) // arguments.BatchSize

    print(f"Running {arguments.Iterations} iterations in {num_batches} batches of {arguments.BatchSize} (async, {arguments.ModelName}) for game type {arguments.GameType}...")
    client = AsyncClient()
    for batch_idx in tqdm(range(num_batches), desc="Batches"):
        batch_start = batch_idx * arguments.BatchSize + 1
        batch_end = min(batch_start + arguments.BatchSize, arguments.Iterations + 1)
        batch_iters = list(range(batch_start, batch_end))
        tasks = [get_ollama_response_clean_async(client, arguments=arguments, iteration=i) for i in batch_iters]
        batch_results = await asyncio.gather(*tasks, return_exceptions=False)
        full_results.extend(batch_results)
        if batch_idx < num_batches - 1:
            await asyncio.sleep(0.1)

    full_results.sort(key=lambda r: r.get("Iteration", 0))
    valid_results = [r for r in full_results if "Error" not in r]

    output_dir = f"./experiment_results/{arguments.GameType}/{arguments.ModelAlias}"
    os.makedirs(output_dir, exist_ok=True)
    output_prefix = f"{output_dir}/{arguments.PromptID}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    full_output_file = f"{output_prefix}_full_results.json"
    with open(full_output_file, "w") as f:
        json.dump(full_results, f, indent=2)

    total_elapsed = time.perf_counter() - start_time
    print(f"\nExperiment completed. {len(valid_results)}/{len(full_results)} successful.")
    print(f"Total time: {total_elapsed:.2f}s ({total_elapsed / 60:.2f} min)")
    print(f"Full results saved to: {full_output_file}")
    if full_results:
        print("\nSample raw output:")
        print(json.dumps(full_results[0], indent=2))

    return full_results, valid_results, output_prefix, total_elapsed

def parse_args() -> BaseArguments:
    """Parse command-line arguments into BaseArguments."""
    parser = argparse.ArgumentParser(description="Run Ollama experiment with configurable arguments.")
    parser.add_argument("--model-name", type=str, default="llama3.2:latest", help="Ollama model name")
    parser.add_argument("--model-alias", type=str, default="llama32", help="Short alias for output paths")
    parser.add_argument("--prompt", type=str, default=PRISONER_DILEMMA_PROMPT, help="Prompt text")
    parser.add_argument("--prompt-id", type=str, default="prisoner_dilemma", help="Prompt identifier")
    parser.add_argument("--game-type", type=str, default="PrisonersDilemma", help="Game type name")
    parser.add_argument("--iterations", type=int, default=50, help="Total number of runs")
    parser.add_argument("--batch-size", type=int, default=5, help="Concurrent runs per batch")
    parser.add_argument("--temperature", type=float, default=0.7, help="Model temperature")
    args = parser.parse_args()
    return BaseArguments(
        ModelName=args.model_name,
        ModelAlias=args.model_alias,
        Prompt=args.prompt,
        PromptID=args.prompt_id,
        GameType=args.game_type,
        Iterations=args.iterations,
        BatchSize=args.batch_size,
        Temperature=args.temperature,
    )


def main(arguments: BaseArguments):
    """Entry point: run the experiment with the given BaseArguments."""
    return asyncio.run(run_simple_experiment_async(arguments=arguments))


if __name__ == "__main__":
    arguments = parse_args()
    full_results, valid_results, output_prefix, total_elapsed = main(arguments)



