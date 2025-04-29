from pydantic import BaseModel
from typing import List, Optional, Dict


class ResponseItem(BaseModel):
    """
    Represents a single LLM response in an experiment.
    """
    id: str
    response_text: str
    decision: str           # e.g., "Silent", "Implicate", or "Unknown"
    reason: str             # Text following the decision
    response: bool          # True = trust (silent), False = distrust (implicate)
    iteration: int          # Which run (1-based index)
    response_time: float    # Time taken to get the response
    timestamp: str          # Local timestamp (e.g., 2025-04-22 19:00:00)


class ModelMetadata(BaseModel):
    """
    Encapsulates model configuration details per model type.
    """
    name: str
    ollama_config: Optional[Dict] = None
    transformer_model_config: Optional[Dict] = None
    enterprise_model_config: Optional[Dict] = None


class ExperimentResult(BaseModel):
    """
    Structured output for a full set of LLM responses to a single prompt.
    Includes metadata, aggregate results, and per-response breakdown.
    """
    gender: Optional[str]
    race: Optional[str]
    ethnicity: Optional[str]
    persona: Optional[str]

    style: Optional[str]                  # prompt style (intro, inline, neutral, etc.)
    prompt_name: Optional[str]           # original filename
    persona_uid: Optional[str]           # unique ID per persona
    prompt_id: str                       # normalized filename
    execution_id: str                    # unique UUID for this run

    date: str                            # Date of experiment
    time: str                            # Time of experiment
    timestamp: str                       # ISO timestamp

    prompt_responses: Dict[str, List[ResponseItem]]
    result: List[int]                    # binary results: 1 (trust), 0 (distrust)

    trust_estimate_probability_distribution: float
    distrust_estimate_probability_distribution: float
    total_runs: int

    model_name: str                      # Raw name or slug
    game_type: str                       # "prisoners_dilemma", etc.

    metadata: ModelMetadata              # Configs like temperature
    is_ollama_model: bool
    is_transformer_model: bool
    is_enterprise_model: bool