"""Anti-collapse transforms for resonance transition matrices."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from scipy.sparse import csr_matrix

if TYPE_CHECKING:
    from resonance.node_registry import NodeRegistry


def apply_hub_penalty(W_raw: np.ndarray, frequencies: np.ndarray) -> np.ndarray:
    """Apply target-frequency hub penalty to an unnormalized dense matrix."""

    W = np.asarray(W_raw, dtype=np.float64).copy()
    freqs = np.asarray(frequencies)
    if W.ndim != 2 or W.shape[0] != W.shape[1]:
        raise ValueError("W_raw must be a square 2D matrix")
    if freqs.shape != (W.shape[1],):
        raise ValueError("frequencies must have shape (N,)")

    penalties = np.ones(W.shape[1], dtype=np.float64)
    positive = freqs > 0
    penalties[positive] = np.log1p(freqs[positive].astype(np.float64))
    return W / penalties


def apply_cross_plane_discount(
    W: np.ndarray,
    registry: "NodeRegistry",
    gamma: float = 0.5,
) -> np.ndarray:
    """Multiply cross-plane matrix entries by gamma before normalization."""

    discounted = np.asarray(W, dtype=np.float64).copy()
    if discounted.ndim != 2 or discounted.shape[0] != discounted.shape[1]:
        raise ValueError("W must be a square 2D matrix")
    if registry.size() != discounted.shape[0]:
        raise ValueError("registry size must match matrix dimensions")

    planes = [registry.get_node(i).plane for i in range(registry.size())]
    for i, source_plane in enumerate(planes):
        for j, target_plane in enumerate(planes):
            if source_plane != target_plane:
                discounted[i, j] *= gamma
    return discounted


def l1_row_normalize(W: np.ndarray) -> csr_matrix:
    """L1-normalize rows and replace zero rows with a uniform distribution."""

    dense = np.asarray(W, dtype=np.float64).copy()
    if dense.ndim != 2 or dense.shape[0] != dense.shape[1]:
        raise ValueError("W must be a square 2D matrix")

    n = dense.shape[0]
    if n == 0:
        return csr_matrix((0, 0), dtype=np.float64)

    row_sums = dense.sum(axis=1)
    zero_rows = np.isclose(row_sums, 0.0)
    if np.any(~zero_rows):
        dense[~zero_rows] = dense[~zero_rows] / row_sums[~zero_rows, np.newaxis]
    if np.any(zero_rows):
        dense[zero_rows] = 1.0 / n
    return csr_matrix(dense)


def build_transition_matrix(
    W_raw: np.ndarray,
    frequencies: np.ndarray,
    registry: "NodeRegistry",
    cross_plane_gamma: float = 0.5,
) -> csr_matrix:
    """Build the CSR transition matrix from raw weights and node metadata."""

    W = apply_hub_penalty(W_raw, frequencies)
    W = apply_cross_plane_discount(W, registry, cross_plane_gamma)
    return l1_row_normalize(W)
