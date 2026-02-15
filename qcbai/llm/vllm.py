"""
vLLM model runner for high-throughput batch inference.

This module provides a vLLM-based ModelRunner that can batch multiple
prompts together for much faster inference compared to API calls.
"""
import os
from typing import List, Dict, Any, Optional
from qcbai.llm.base import ModelRunner
from pathlib import Path
import yaml

try:
    from vllm import LLM, SamplingParams
    VLLM_AVAILABLE = True
except ImportError:
    VLLM_AVAILABLE = False
    LLM = None
    SamplingParams = None

MODEL_CONFIG_PATH = Path(__file__).parent / "models.yaml"

# Mapping from Ollama model names to Hugging Face model IDs
OLLAMA_TO_HF_MAPPING = {
    "llama3.2:latest": "meta-llama/Llama-3.2-3B-Instruct",
    "mistral:latest": "mistralai/Mistral-7B-Instruct-v0.3",
    "llama3.3:latest": "meta-llama/Llama-3.3-70B-Instruct",
    "mistral-small3.1:latest": "mistralai/Mistral-Small-Instruct-3.1",
    "phi4:latest": "microsoft/Phi-4",
    "gemma3:27b": "google/gemma-2-27b-it",
    "qwen2.5:32b": "Qwen/Qwen2.5-32B-Instruct",
}


class VLLMModel(ModelRunner):
    """
    Model runner using vLLM for high-throughput batch inference.
    
    Supports batching multiple prompts together for much faster inference.
    """
    
    # Class-level cache for loaded models (shared across instances)
    _model_cache: Dict[str, Any] = {}
    
    def __init__(
        self,
        name: str,
        slug: str,
        hf_model_id: str,
        temperature: float = 0.7,
        tensor_parallel_size: int = 1,
        max_model_len: Optional[int] = None,
    ):
        """
        Initialize vLLM model runner.
        
        Args:
            name: Original model name (for compatibility)
            slug: Short slugified name
            hf_model_id: Hugging Face model ID
            temperature: Default sampling temperature
            tensor_parallel_size: Number of GPUs to use (1 or 2)
            max_model_len: Maximum sequence length
        """
        if not VLLM_AVAILABLE:
            raise ImportError(
                "vLLM is not installed. Install with: pip install vllm"
            )
        
        self.name = name
        self.slug = slug
        self.hf_model_id = hf_model_id
        self.temperature = temperature
        self.tensor_parallel_size = tensor_parallel_size
        self.max_model_len = max_model_len
        
        # Load model (cached per model ID)
        self.llm = self._get_or_load_model()
        self.sampling_params = SamplingParams(
            temperature=temperature,
            top_p=0.9,
            max_tokens=2048,
        )
    
    def _get_or_load_model(self):
        """Get cached model or load new one."""
        cache_key = f"{self.hf_model_id}_{self.tensor_parallel_size}"
        
        if cache_key not in VLLMModel._model_cache:
            print(f"Loading vLLM model: {self.hf_model_id}")
            
            # Set Hugging Face cache directory
            hf_home = os.environ.get("HF_HOME", os.environ.get("TRANSFORMERS_CACHE"))
            if hf_home:
                os.environ["HF_HOME"] = hf_home
                os.environ["TRANSFORMERS_CACHE"] = hf_home
            
            kwargs = {
                "model": self.hf_model_id,
                "tensor_parallel_size": self.tensor_parallel_size,
                "trust_remote_code": True,
            }
            
            if self.max_model_len:
                kwargs["max_model_len"] = self.max_model_len
            
            VLLMModel._model_cache[cache_key] = LLM(**kwargs)
            print(f"✓ Model loaded: {self.hf_model_id}")
        
        return VLLMModel._model_cache[cache_key]
    
    def get_name(self) -> str:
        return self.name
    
    def get_slug(self) -> str:
        return self.slug
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "temperature": self.temperature,
            "hf_model_id": self.hf_model_id,
            "tensor_parallel_size": self.tensor_parallel_size,
            "backend": "vllm",
        }
    
    def run_prompt(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        """
        Run a single prompt synchronously.
        
        Note: For vLLM, batching is more efficient. Use run_batch() for multiple prompts.
        """
        # Convert messages to prompt string
        prompt = self._messages_to_prompt(messages)
        
        # Update temperature if different
        sampling_params = SamplingParams(
            temperature=temperature,
            top_p=0.9,
            max_tokens=2048,
        )
        
        try:
            outputs = self.llm.generate([prompt], sampling_params)
            result = outputs[0]
            
            return {
                "text": result.outputs[0].text,
                "raw": {
                    "finish_reason": result.outputs[0].finish_reason,
                    "token_ids": result.outputs[0].token_ids,
                },
            }
        except Exception as e:
            return {"text": "", "error": str(e)}
    
    def run_batch(
        self,
        messages_list: List[List[Dict[str, str]]],
        temperature: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Run multiple prompts in a single batch (much faster than individual calls).
        
        This is the key advantage of vLLM - batching all runs together.
        
        Args:
            messages_list: List of message lists (one per prompt)
            temperature: Sampling temperature
            
        Returns:
            List of response dictionaries
        """
        # Convert all messages to prompt strings
        prompts = [self._messages_to_prompt(msgs) for msgs in messages_list]
        
        # Update temperature if different
        sampling_params = SamplingParams(
            temperature=temperature,
            top_p=0.9,
            max_tokens=2048,
        )
        
        try:
            outputs = self.llm.generate(prompts, sampling_params)
            
            results = []
            for output in outputs:
                results.append({
                    "text": output.outputs[0].text,
                    "raw": {
                        "finish_reason": output.outputs[0].finish_reason,
                        "token_ids": output.outputs[0].token_ids,
                    },
                })
            
            return results
        except Exception as e:
            # Return error for all if batch fails
            return [{"text": "", "error": str(e)}] * len(messages_list)
    
    async def arun_prompt(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        """
        Async wrapper for single prompt (for compatibility).
        
        Note: vLLM doesn't have true async, but we can run in executor.
        For best performance, use run_batch() instead.
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run_prompt, messages, temperature)
    
    @staticmethod
    def _messages_to_prompt(messages: List[Dict[str, str]]) -> str:
        """
        Convert OpenAI-style messages to a single prompt string.
        
        Handles system, user, and assistant messages.
        """
        prompt_parts = []
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts)


def load_vllm_model_configs(tensor_parallel_size: int = 1) -> List[VLLMModel]:
    """
    Load vLLM model configurations from models.yaml.
    
    Args:
        tensor_parallel_size: Number of GPUs to use (1 or 2)
    """
    if not VLLM_AVAILABLE:
        print("Warning: vLLM not available. Install with: pip install vllm")
        return []
    
    if not MODEL_CONFIG_PATH.exists():
        print(f"Model config not found at {MODEL_CONFIG_PATH}")
        return []
    
    with open(MODEL_CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    
    # Get Ollama models and map to HF
    ollama_models = config.get("ollama", [])
    runners = []
    
    for entry in ollama_models:
        if isinstance(entry, dict):
            ollama_name = entry.get("name")
            slug = entry.get("slug", ollama_name.replace(":", "-").replace("/", "-").lower())
            temp = entry.get("temperature", 0.7)
            
            # Map to Hugging Face model ID
            hf_model_id = OLLAMA_TO_HF_MAPPING.get(ollama_name)
            
            if hf_model_id:
                runners.append(VLLMModel(
                    name=ollama_name,
                    slug=slug,
                    hf_model_id=hf_model_id,
                    temperature=temp,
                    tensor_parallel_size=tensor_parallel_size,
                ))
            else:
                print(f"Warning: No HF mapping for {ollama_name}, skipping")
    
    return runners


VLLM_MODELS: List[ModelRunner] = load_vllm_model_configs() if VLLM_AVAILABLE else []

