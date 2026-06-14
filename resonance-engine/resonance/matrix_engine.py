"""Sparse resonance matrix persistence and PageRank-style computation."""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.sparse import csr_matrix, load_npz, save_npz
from scipy.sparse.linalg import spsolve

from resonance.node_registry import NodeRegistry


@dataclass
class ResonanceConfig:
    """Runtime configuration for resonance computation."""

    alpha: float = 0.85
    t_max: int = 50
    epsilon: float = 1e-5
    theta: float = 0.02
    k_skills: int = 7
    k_memories: int = 5
    k_soul: int = 3


@dataclass
class ResonanceResult:
    """Result of a resonance computation."""

    v_final: np.ndarray
    iterations: int
    converged: bool
    activated: list[tuple[str, str, float]]


class ResonanceEngine:
    """Read-only sparse resonance engine."""

    def __init__(
        self,
        M: csr_matrix,
        registry: NodeRegistry,
        config: Optional[ResonanceConfig] = None,
    ) -> None:
        """Create a resonance engine from a CSR matrix and registry."""

        if M.shape[0] != M.shape[1]:
            raise ValueError("M must be a square matrix")
        if M.shape[0] != registry.size():
            raise ValueError("matrix dimension must match registry size")

        self.M = M.tocsr().astype(np.float64)
        self.registry = registry
        self.config = config or ResonanceConfig()
        self._last_loaded: float = time.time()

    @classmethod
    def load(
        cls,
        matrix_path: str,
        registry_path: str,
        config: Optional[ResonanceConfig] = None,
    ) -> Optional["ResonanceEngine"]:
        """Load serialized matrix.npz and registry.pkl from disk."""

        if not os.path.exists(matrix_path) or not os.path.exists(registry_path):
            return None
        try:
            M = load_npz(matrix_path)
            registry = NodeRegistry.load(registry_path)
            engine = cls(M, registry, config)
            engine._last_loaded = max(
                os.path.getmtime(matrix_path),
                os.path.getmtime(registry_path),
            )
            return engine
        except (OSError, ValueError, TypeError, EOFError):
            return None

    def _check_and_reload(self, matrix_path: str, registry_path: str) -> bool:
        """
        Reload matrix and registry if on-disk files are newer than this engine.

        On load failure the existing in-memory state is kept.
        """

        try:
            newest_mtime = max(
                os.path.getmtime(matrix_path),
                os.path.getmtime(registry_path),
            )
        except OSError:
            return False

        if newest_mtime <= self._last_loaded:
            return False

        try:
            M = load_npz(matrix_path)
            registry = NodeRegistry.load(registry_path)
            if M.shape[0] != M.shape[1] or M.shape[0] != registry.size():
                raise ValueError("matrix dimension must match registry size")
        except Exception:
            print(
                f"[resonance] WARNING: failed to reload matrix from {matrix_path}, keeping existing",
                file=sys.stderr,
            )
            return False

        self.M = M.tocsr().astype(np.float64)
        self.registry = registry
        self._last_loaded = newest_mtime
        return True

    def get_matrix_info(self) -> dict:
        """Return current matrix shape, sparsity, and load timestamp."""

        n = self.registry.size() if self.registry else 0
        nnz = self.M.nnz if hasattr(self, "M") else 0
        return {
            "nodes": n,
            "nnz": nnz,
            "density": nnz / (n * n) * 100 if n > 0 else 0,
            "last_loaded": self._last_loaded,
        }

    def save(self, matrix_path: str, registry_path: str) -> None:
        """Atomically save matrix and registry using temp files and os.replace."""

        matrix_dir = os.path.dirname(matrix_path)
        registry_dir = os.path.dirname(registry_path)
        if matrix_dir:
            os.makedirs(matrix_dir, exist_ok=True)
        if registry_dir:
            os.makedirs(registry_dir, exist_ok=True)

        matrix_tmp = f"{matrix_path}.tmp.npz"
        registry_tmp = f"{registry_path}.tmp"
        save_npz(matrix_tmp, self.M)
        self.registry.save(registry_tmp)
        os.replace(matrix_tmp, matrix_path)
        os.replace(registry_tmp, registry_path)

    def compute(self, v0: np.ndarray) -> ResonanceResult:
        """Run the resonance loop and return activated nodes above threshold."""

        n = self.registry.size()
        if n == 0:
            return ResonanceResult(
                v_final=np.zeros(0, dtype=np.float64),
                iterations=0,
                converged=True,
                activated=[],
            )

        initial = np.asarray(v0, dtype=np.float64).reshape(-1)
        if initial.shape != (n,):
            raise ValueError("v0 must have shape (N,)")

        initial_sum = initial.sum()
        if np.isclose(initial_sum, 0.0):
            initial = np.full(n, 1.0 / n, dtype=np.float64)
        else:
            initial = initial / initial_sum

        alpha = self.config.alpha
        v = initial.copy()
        converged = False
        iterations = 0

        for t in range(self.config.t_max):
            v_next = alpha * (self.M.T @ v) + (1.0 - alpha) * initial
            total = v_next.sum()
            if np.isclose(total, 0.0):
                v_next = np.full(n, 1.0 / n, dtype=np.float64)
            else:
                v_next = v_next / total

            iterations = t + 1
            if np.abs(v_next - v).sum() < self.config.epsilon:
                converged = True
                v = v_next
                break
            v = v_next

        if not converged:
            solved = self._solve_fixed_point(initial)
            if solved is not None:
                v = solved
                residual = np.abs(
                    alpha * (self.M.T @ v) + (1.0 - alpha) * initial - v
                ).sum()
                converged = residual < self.config.epsilon

        activated: list[tuple[str, str, float]] = []
        for idx, score in enumerate(v):
            if score >= self.config.theta:
                node = self.registry.get_node(idx)
                if node is not None:
                    activated.append((node.node_id, node.plane.value, float(score)))
        activated.sort(key=lambda item: item[2], reverse=True)

        return ResonanceResult(
            v_final=v,
            iterations=iterations,
            converged=converged,
            activated=activated,
        )

    def _solve_fixed_point(self, initial: np.ndarray) -> Optional[np.ndarray]:
        """Solve the damped fixed-point equation as a deterministic fallback."""

        n = self.registry.size()
        try:
            from scipy.sparse import eye as speye

            lhs = speye(n, format="csr", dtype=np.float64) - self.config.alpha * self.M.T
            rhs = (1.0 - self.config.alpha) * initial
            solved = np.asarray(spsolve(lhs, rhs), dtype=np.float64)
        except Exception:
            return None

        if solved.shape != (n,) or not np.all(np.isfinite(solved)):
            return None
        solved = np.maximum(solved, 0.0)
        total = solved.sum()
        if np.isclose(total, 0.0):
            return None
        return solved / total

    def build_v0_from_scores(
        self,
        scores: dict[str, float],
        threshold: float = 0.1,
    ) -> np.ndarray:
        """Convert node similarity scores to an L1-normalized activation vector."""

        n = self.registry.size()
        if n == 0:
            return np.zeros(0, dtype=np.float64)

        v0 = np.zeros(n, dtype=np.float64)
        for node_id, score in scores.items():
            idx = self.registry.get_idx(node_id)
            if idx is not None:
                v0[idx] = max(float(score) - threshold, 0.0)

        total = v0.sum()
        if np.isclose(total, 0.0):
            return np.full(n, 1.0 / n, dtype=np.float64)
        return v0 / total
