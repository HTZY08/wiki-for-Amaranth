"""Temporal transforms for resonance matrix updates."""

from __future__ import annotations

import numpy as np

from resonance.node_registry import NodeRegistry


def exponential_decay(
    W_raw: np.ndarray,
    delta_t_days: float,
    lambda_decay: float = 0.01,
) -> np.ndarray:
    """Apply exponential decay to a raw weight matrix."""

    W = np.asarray(W_raw, dtype=np.float64)
    if delta_t_days <= 0:
        return W.copy()
    return W * np.exp(-float(lambda_decay) * float(delta_t_days))


def momentum_update(
    W_old: np.ndarray,
    delta_W: np.ndarray,
    beta: float = 0.9,
    drift_threshold: float = 2.0,
) -> tuple[np.ndarray, float]:
    """Blend an old matrix with a new delta matrix using momentum."""

    old = np.asarray(W_old, dtype=np.float64)
    delta = np.asarray(delta_W, dtype=np.float64)
    if old.shape != delta.shape or old.ndim != 2 or old.shape[0] != old.shape[1]:
        raise ValueError("W_old and delta_W must be square matrices of the same shape")

    n = old.shape[0]
    if n == 0:
        return old.copy(), 0.0

    drift = float(np.linalg.norm(delta - old, ord="fro") / np.sqrt(n))
    beta_used = 0.5 if drift > drift_threshold else float(beta)
    W_new = beta_used * old + (1.0 - beta_used) * delta
    return W_new, drift


def compute_delta_W(
    new_pairs: list[tuple[str, str, int]],
    registry: NodeRegistry,
    N: int,
) -> np.ndarray:
    """Convert co-occurrence pairs to a symmetric delta matrix."""

    delta = np.zeros((N, N), dtype=np.float64)
    for skill_a, skill_b, count in new_pairs:
        idx_a = registry.get_idx(skill_a)
        if idx_a is None:
            idx_a = registry.get_idx(f"skill:{skill_a}")
        idx_b = registry.get_idx(skill_b)
        if idx_b is None:
            idx_b = registry.get_idx(f"skill:{skill_b}")
        if idx_a is None or idx_b is None or idx_a == idx_b:
            continue
        weight = float(count)
        delta[idx_a, idx_b] += weight
        delta[idx_b, idx_a] += weight
    return delta
