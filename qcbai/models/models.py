from typing import Dict, List, Optional
from pydantic import BaseModel

class TrustGameResults(BaseModel):
    gender: Optional[str] = None
    race: Optional[str] = None
    ethnicity: Optional[str] = None
    persona: Optional[str] = None
    trust_game_type: str
    trust_game_results: List[int]
    trust_estimate: int
    distrust_estimate: int
    total_runs: int

class Response(BaseModel):
    trust_game_type: str
    trust_game_results: List[TrustGameResults]