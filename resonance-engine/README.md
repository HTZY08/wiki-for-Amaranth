# Resonance Engine

Self-organizing multi-plane skill/memory discovery engine for AI agents.

## One Line

Things used together stay close in space; they reappear together automatically.

## What It Does

Most AI agents manage tools via flat text search or hardcoded routing. The resonance engine takes a different approach: **skills self-organize based on usage patterns**. Co-occurrence statistics drive Hebbian-style updates, producing emergent spatial clusters without a central controller.

When activated, the engine runs a PageRank-style iteration in <10ms and returns the top-K skills for the current context — no LLM routing call needed.

## Architecture

```
Session logs  →  cooc.db (co-occurrence)
                     ↓
                  Transition matrix
                  (hub-penalty + L1)
                     ↓
               ResonanceEngine.compute(v₀)
                     ↓
               Context assembler → prompt
```

## Quick Start

```bash
# Install
pip install numpy scipy

# Build manifest from skill metadata
python scripts/generate_manifest.py

# Rebuild matrix
python scripts/resonance_cron.py

# Query (Python)
from resonance import ResonanceEngine, NodeRegistry
engine = ResonanceEngine()
v0 = engine.build_v0("我需要查一篇论文的引用")
result = engine.compute(v0)
# → ['arxiv', 'precision-review-search', 'web_search', ...]
```

## Files

| File | Purpose |
|------|---------|
| `resonance/node_registry.py` | Node index management |
| `resonance/anti_collapse.py` | Hub-penalty + normalization |
| `resonance/matrix_engine.py` | CSR matrix + resonance compute |
| `resonance/embeddings.py` | Embedding store + v₀ initialization |
| `resonance/cold_start.py` | Bootstrap from metadata |
| `resonance/temporal.py` | Time decay + momentum |
| `resonance/context_assembler.py` | Threshold → top-K → prompt |
| `resonance/cross_plane.py` | Cross-plane edges (memory/soul) |
| `resonance_cron.py` | Cron pipeline |
| `resonance_viz.py` | UMAP → interactive HTML |

## Performance

| Operation | Target | Measured |
|-----------|--------|----------|
| Matrix build (N=500, 5% density) | <100ms | ~36ms |
| Resonance compute (50 iterations) | <10ms | ~1ms |
| Precision@5 | >0.35 | 0.912 |

## Design

- **No LLM routing**: retrieval is matrix × vector multiplication
- **Anti-collapse**: IDF-style hub suppression prevents topology collapse
- **Multi-plane**: skills, memories, and behavioral rules share one matrix with cross-discount
- **Hot reload**: matrix updates on disk by cron, live-loaded by running agent
- **Atomic saves**: tmp + os.replace() prevents partial reads

## Config

Paths are configured via environment variables:
- `RESONANCE_STATE_DB` — session database path
- `RESONANCE_COOC_DB` — co-occurrence database
- `RESONANCE_MATRIX_DIR` — matrix output directory
- `RESONANCE_MANIFEST` — skill manifest YAML

Defaults are set for local development. See `resonance_cron.py` for full list.
