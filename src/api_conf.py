"""
API endpoints and keys for LLM view generation.
Keys are read from environment variables or the repository's .env file (gitignored); never hardcode them here.
"""
import os

from paths import ROOT

# Load ROOT/.env without overriding variables already set in the shell
_env_file = ROOT / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _key, _value = _line.split("=", 1)
            os.environ.setdefault(_key.strip(), _value.strip().strip('"').strip("'"))

OPENAI_URL = "https://api.openai.com/v1"

API_URL = {
    "llama": os.environ.get("LLAMA_API_URL", "http://localhost:3000/v1"),
    "gemma": os.environ.get("GEMMA_API_URL", "http://localhost:3000/v1"),
    "qwen": os.environ.get("QWEN_API_URL", "http://localhost:8000/v1"),
    "gpt": OPENAI_URL,
}

API_KEY = {
    "llama": os.environ.get("LLAMA_API_KEY", "EMPTY"),
    "gemma": os.environ.get("GEMMA_API_KEY", "EMPTY"),
    "qwen": os.environ.get("QWEN_API_KEY", "EMPTY"),
    "gpt": os.environ.get("OPENAI_API_KEY"),
}
