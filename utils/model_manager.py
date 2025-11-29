"""
Model Manager for LLM calls
Supports both Google Gemini API and Ollama local models.
Reads configuration from config/profiles.yaml and config/models.json
"""

import os
import json
import yaml
import requests
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import sys

# Add utils to path for backoff utility
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from utils.backoff import with_exponential_backoff

try:
    from google import genai
    from google.genai.errors import ServerError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

load_dotenv()

ROOT = Path(__file__).parent.parent
MODELS_JSON = ROOT / "config" / "models.json"
PROFILE_YAML = ROOT / "config" / "profiles.yaml"


class ModelManager:
    """Manages LLM calls, supporting both Google Gemini and Ollama."""
    
    def __init__(self, model_key: Optional[str] = None):
        """
        Initialize ModelManager.
        
        Args:
            model_key: Override model key from config (e.g., "phi4", "gemini", "gemma3:12b")
        """
        self.config = json.loads(MODELS_JSON.read_text())
        self.profile = yaml.safe_load(PROFILE_YAML.read_text())
        
        # Get model key from parameter or config
        self.text_model_key = model_key or self.profile["llm"]["text_generation"]
        self.model_info = self.config["models"][self.text_model_key]
        self.model_type = self.model_info["type"]
        
        # Initialize client based on model type
        if self.model_type == "gemini":
            if not GOOGLE_AVAILABLE:
                raise ImportError("Google genai library not available. Install with: pip install google-genai")
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")
            self.client = genai.Client(api_key=api_key)
        elif self.model_type == "ollama":
            # Verify Ollama is running
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                response.raise_for_status()
            except Exception as e:
                print(f"[WARN] Ollama may not be running: {e}")
                print("[WARN] Falling back to Google API if available")
                # Fallback to gemini if available
                if GOOGLE_AVAILABLE:
                    api_key = os.getenv("GEMINI_API_KEY")
                    if api_key:
                        self.text_model_key = "gemini"
                        self.model_info = self.config["models"]["gemini"]
                        self.model_type = "gemini"
                        self.client = genai.Client(api_key=api_key)
                        print("[INFO] Using Google Gemini as fallback")
                    else:
                        raise ValueError("Neither Ollama nor Google API available")
                else:
                    raise ValueError("Ollama not available and Google API not configured")
    
    def generate_text(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Generate text using the configured model.
        
        Args:
            prompt: Input prompt
            model: Optional model override (for Gemini, e.g., "gemini-2.0-flash-lite")
        
        Returns:
            Generated text
        """
        if self.model_type == "gemini":
            return self._gemini_generate(prompt, model)
        elif self.model_type == "ollama":
            return self._ollama_generate(prompt)
        else:
            raise NotImplementedError(f"Unsupported model type: {self.model_type}")
    
    def _gemini_generate_sync(self, prompt: str, model: Optional[str] = None) -> str:
        """Internal sync method for Gemini API call (used with backoff)."""
        model_name = model or self.model_info.get("model", "gemini-2.0-flash-lite")
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        
        # Safely extract response text
        try:
            return response.text.strip()
        except AttributeError:
            try:
                return response.candidates[0].content.parts[0].text.strip()
            except Exception:
                return str(response)
    
    def _gemini_generate(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate text using Google Gemini API with exponential backoff for 429 errors."""
        # Google API client is synchronous, so use sync backoff
        return with_exponential_backoff(
            self._gemini_generate_sync,
            prompt,
            model=model,
            max_retries=3,
            initial_delay=1.0,
            max_delay=60.0,
            backoff_multiplier=2.0
        )
    
    def _ollama_generate(self, prompt: str) -> str:
        """Generate text using Ollama API."""
        url = self.model_info["url"]["generate"]
        model_name = self.model_info["model"]
        
        try:
            response = requests.post(
                url,
                json={"model": model_name, "prompt": prompt, "stream": False},
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Ollama API error: {e}")
            raise

