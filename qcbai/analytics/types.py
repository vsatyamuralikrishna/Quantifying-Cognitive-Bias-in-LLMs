from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict


class ResponseItem(BaseModel):
    """Represents a single LLM response in an experiment."""
    id: str
    response_text: str
    decision: str
    reason: str
    response: bool
    amount: Optional[int] = None
    iteration: int
    response_time: float
    timestamp: str


class ModelMetadata(BaseModel):
    """Encapsulates model configuration details per model type."""
    name: str
    ollama_config: Optional[Dict] = None
    transformer_model_config: Optional[Dict] = None
    enterprise_model_config: Optional[Dict] = None


class ExperimentResult(BaseModel):
    """
    Structured output for a full set of LLM responses to a single prompt.
    Supports both binary-choice and amount-based games.
    """
    model_config = ConfigDict(protected_namespaces=())
    gender: Optional[str] = None
    race: Optional[str] = None
    ethnicity: Optional[str] = None
    persona: Optional[str] = None

    style: Optional[str] = None
    prompt_name: Optional[str] = None
    persona_uid: Optional[str] = None
    prompt_id: str
    execution_id: str

    date: str
    time: str
    timestamp: str

    prompt_responses: Dict[str, List[ResponseItem]]
    result: List[int]  # binary (0/1) for binary games, amounts for amount games

    trust_estimate_probability_distribution: float
    distrust_estimate_probability_distribution: float
    mean_amount: Optional[float] = None  # for amount-based games
    total_runs: int

    model_name: str
    game_type: str
    response_type: str = "binary"  # "binary" or "amount"

    metadata: ModelMetadata
    is_ollama_model: bool = False
    is_transformer_model: bool = False
    is_enterprise_model: bool = False
