"""Legacy data models — kept for backward compatibility."""

from pydantic import BaseModel
from typing import Optional


class TrustGameResults(BaseModel):
    prompt_id: str
    model_name: str
    trust_percent: float
    distrust_percent: float


class Response(BaseModel):
    text: str
    decision: Optional[str] = None
    reason: Optional[str] = None
