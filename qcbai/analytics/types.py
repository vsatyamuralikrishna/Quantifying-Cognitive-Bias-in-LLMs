from pydantic import BaseModel
from typing import List, Optional, Dict

class ResponseItem(BaseModel):
    id: str
    response_text: str
    response: bool

class ModelMetadata(BaseModel):
    name: str
    ollama_config: Optional[Dict] = None
    transformer_model_config: Optional[Dict] = None
    enterprise_model_config: Optional[Dict] = None

class ExperimentResult(BaseModel):
    gender: Optional[str]
    race: Optional[str]
    ethnicity: Optional[str]
    persona: Optional[str]
    style: Optional[str]
    prompt_name: Optional[str]
    persona_uid: Optional[str]
    prompt_id: str
    execution_id: str
    date: str
    time: str
    timestamp: str
    prompt_responses: Dict[str, List[ResponseItem]]
    result: List[int]
    trust_estimate_probability_distribution: float
    distrust_estimate_probability_distribution: float
    total_runs: int
    model_name: str
    game_type: str
    metadata: ModelMetadata
    is_ollama_model: bool
    is_transformer_model: bool
    is_enterprise_model: bool