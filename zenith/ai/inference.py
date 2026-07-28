import os
import json
import sys
import time
import requests
from functools import lru_cache

# Singletons to keep FastAPI hot and responsive
_GLOBAL_MODEL = None
_GLOBAL_TOKENIZER = None
_GLOBAL_SESSION = None
_GLOBAL_DEVICE = None

def _parse_output_static(generated_text: str, code_snippet: str) -> dict:
    try:
        json_str = generated_text.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()
        return json.loads(json_str)
    except Exception:
        is_test = "test" in code_snippet.lower() or "example" in code_snippet.lower()
        return {
            "is_live": not is_test,
            "confidence": 0.5,
            "reason": f"AI Parsing Error. Output: {generated_text[:50]}..."
        }

@lru_cache(maxsize=2000)
def _cached_inference(prompt: str, code_snippet: str, is_mac: bool, match_str: str = "") -> dict:
    global _GLOBAL_SESSION
    if not _GLOBAL_SESSION:
        return {
            "is_live": True, 
            "confidence": 0.0, 
            "reason": "Ollama unavailable - defaulting to flagging as live for safety"
        }
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": _GLOBAL_SESSION,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0}
            },
            timeout=30
        )
        response.raise_for_status()
        resp_json = response.json()
        generated_text = resp_json.get("response", "")
        return _parse_output_static(generated_text, code_snippet)
    except Exception as e:
        return {
            "is_live": True, 
            "confidence": 0.0, 
            "reason": "Ollama unavailable - defaulting to flagging as live for safety"
        }

class ZenithClassifier:
    def __init__(self):
        self.os_type = sys.platform
        self.is_mac = self.os_type == "darwin"
        
        if self.is_mac:
            self.model_path = "phi3:mini"
            self.engine = "Ollama (Phi-3-mini, Q4 quantized, local)"
        else:
            self.model_path = "models/zenith_phi3_int4.onnx"
            self.onnx_providers = ["VitisAIExecutionProvider", "OpenVINOExecutionProvider", "DmlExecutionProvider", "CPUExecutionProvider"]
            self.engine = "ONNX Runtime (AMD/Intel NPU)"

    def _init_session(self):
        global _GLOBAL_MODEL, _GLOBAL_TOKENIZER, _GLOBAL_SESSION, _GLOBAL_DEVICE
        if _GLOBAL_MODEL is None and _GLOBAL_SESSION is None:
            _GLOBAL_MODEL = "INITIALIZING"
            try:
                # Check if Ollama is reachable
                res = requests.get("http://localhost:11434/api/tags", timeout=3)
                res.raise_for_status()
                
                # Warm-up request
                requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": self.model_path, "prompt": "Hello", "stream": False},
                    timeout=30
                )
                _GLOBAL_SESSION = self.model_path
            except Exception as e:
                _GLOBAL_SESSION = False

    def is_live_secret(self, code_snippet: str, pattern_name: str, match_str: str = "") -> dict:
        self._init_session()
        
        prompt = f"""<|system|>
You are a highly precise security analyzer. You look at code snippets and determine if a string is a live production secret or a mock/test variable. Reply ONLY in JSON format: {{"is_live": true/false, "confidence": 0-1, "reason": "short explanation"}}. Do not write markdown blocks around the JSON.
<|user|>
Analyze this code snippet. Is '{pattern_name}' a LIVE production secret or a harmless test/example value?
Code:
{code_snippet}
<|assistant|>
"""
        return _cached_inference(prompt, code_snippet, self.is_mac, match_str)
