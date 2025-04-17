# qcbai/llm/base.py
from typing import List, Dict
from abc import ABC, abstractmethod

class ModelRunner(ABC):
    @abstractmethod
    def run_prompt(self, messages: List[Dict], temperature: float = 0.7) -> Dict:
        """Run a prompt and return a dictionary with 'text' key"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return a unique slugified name for the model"""
        pass