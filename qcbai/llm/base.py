from typing import List, Dict
from abc import ABC, abstractmethod


class ModelRunner(ABC):
    @abstractmethod
    def run_prompt(self, messages: List[Dict], temperature: float = 0.7) -> Dict:
        """Run a prompt synchronously and return a dictionary with 'text' key."""
        pass

    async def arun_prompt(self, messages: List[Dict], temperature: float = 0.7) -> Dict:
        """Run a prompt asynchronously. Falls back to sync by default."""
        return self.run_prompt(messages, temperature)

    @abstractmethod
    def get_name(self) -> str:
        """Return the full model name."""
        pass

    @abstractmethod
    def get_slug(self) -> str:
        """Return a short slugified name for filenames."""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict:
        """Return model configuration metadata."""
        pass
