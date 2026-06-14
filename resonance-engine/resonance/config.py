"""
Configuration for the resonance engine.

All paths are configurable via environment variables with sensible defaults
for local development. Override for production deployments.
"""

import os
from pathlib import Path

# Default base: assume project root (parent of resonance/ directory)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

def _env(key: str, default: str) -> str:
    return os.environ.get(key, default)

# --- Session & co-occurrence DB ---
STATE_DB      = _env("RESONANCE_STATE_DB",  str(_PROJECT_ROOT / "state.db"))
COOC_DB       = _env("RESONANCE_COOC_DB",   str(_PROJECT_ROOT / "cooc.db"))
RESONANCE_DB  = _env("RESONANCE_DB",        str(_PROJECT_ROOT / "resonance.db"))

# --- Manifest ---
MANIFEST_PATH = _env("RESONANCE_MANIFEST",  str(_PROJECT_ROOT / "skill_manifest.yaml"))

# --- Matrix directory ---
MATRIX_DIR    = _env("RESONANCE_MATRIX_DIR", str(_PROJECT_ROOT / "matrix"))

# --- Embedding model ---
EMBEDDING_MODEL = _env("RESONANCE_EMBEDDING_MODEL", "BAAI/bge-m3")

# --- Soul/Memory paths (for cross-plane) ---
SOUL_PATHS    = [
    _env("RESONANCE_SOUL_MD",  str(_PROJECT_ROOT / "SOUL.md")),
    _env("RESONANCE_MEMORY_MD", str(_PROJECT_ROOT / "MEMORY.md")),
    _env("RESONANCE_USER_MD",  str(_PROJECT_ROOT / "USER.md")),
]

# --- Performance ---
TOP_K         = int(_env("RESONANCE_TOP_K", "5"))
ACTIVATION_THRESHOLD = float(_env("RESONANCE_THRESHOLD", "0.02"))
NUM_ITERATIONS = int(_env("RESONANCE_ITERATIONS", "50"))
DAMPING_FACTOR = float(_env("RESONANCE_DAMPING", "0.85"))
