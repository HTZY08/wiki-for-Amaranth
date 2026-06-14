"""Embedding persistence and v0 initialization helpers."""

from __future__ import annotations

import sqlite3
import time
from typing import Optional

import numpy as np

from resonance.node_registry import NodeRegistry


EMBEDDING_DIM = 1536


class EmbeddingStore:
    """SQLite-backed store for node embeddings."""

    def __init__(self, db_path: str):
        """Create the embedding store and ensure its table exists."""

        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS node_embeddings (
                    node_id TEXT PRIMARY KEY,
                    embedding BLOB NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )
            conn.commit()

    def get(self, node_id: str) -> Optional[np.ndarray]:
        """Return a node embedding as float32, or None if missing."""

        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT embedding FROM node_embeddings WHERE node_id = ?",
                (node_id,),
            ).fetchone()
        if row is None:
            return None

        embedding = np.frombuffer(row[0], dtype=np.float32).copy()
        if embedding.shape != (EMBEDDING_DIM,):
            return None
        return embedding

    def set(self, node_id: str, embedding: np.ndarray) -> None:
        """Upsert a node embedding."""

        vector = np.asarray(embedding, dtype=np.float32).reshape(-1)
        if vector.shape != (EMBEDDING_DIM,):
            raise ValueError(f"embedding must have shape ({EMBEDDING_DIM},)")

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                INSERT INTO node_embeddings (node_id, embedding, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(node_id) DO UPDATE SET
                    embedding = excluded.embedding,
                    updated_at = excluded.updated_at
                """,
                (node_id, vector.tobytes(), time.time()),
            )
            conn.commit()

    def get_all_matrix(self, registry: NodeRegistry) -> np.ndarray:
        """Return all embeddings in registry index order."""

        matrix = np.zeros((registry.size(), EMBEDDING_DIM), dtype=np.float32)
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT node_id, embedding FROM node_embeddings"
            ).fetchall()

        for node_id, blob in rows:
            idx = registry.get_idx(node_id)
            if idx is None:
                continue
            embedding = np.frombuffer(blob, dtype=np.float32)
            if embedding.shape == (EMBEDDING_DIM,):
                matrix[idx] = embedding
        return matrix

    def get_all_ids(self) -> list[str]:
        """Return all node ids that have stored embeddings."""

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT node_id FROM node_embeddings ORDER BY node_id"
            ).fetchall()
        return [row[0] for row in rows]


def compute_v0_cosine(
    task_embedding: np.ndarray,
    node_embeddings: np.ndarray,
    registry: NodeRegistry,
    threshold: float = 0.1,
) -> np.ndarray:
    """Compute an L1-normalized v0 from cosine similarity."""

    n = registry.size()
    if n == 0:
        return np.zeros(0, dtype=np.float64)

    query = np.asarray(task_embedding, dtype=np.float32).reshape(-1)
    matrix = np.asarray(node_embeddings, dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[0] != n:
        raise ValueError("node_embeddings must have shape (N, D)")
    if query.shape != (matrix.shape[1],):
        raise ValueError("task_embedding dimension must match node embeddings")

    norms = np.linalg.norm(matrix, axis=1)
    task_norm = float(np.linalg.norm(query))
    sims = (matrix @ query) / (norms * task_norm + 1e-10)
    v0 = np.maximum(sims.astype(np.float64) - float(threshold), 0.0)

    total = v0.sum()
    if np.isclose(total, 0.0):
        return np.full(n, 1.0 / n, dtype=np.float64)
    return v0 / total


def compute_v0_keyword(
    keywords: list[str],
    registry: NodeRegistry,
    threshold: float = 0.0,
) -> np.ndarray:
    """Compute a simple keyword-overlap v0 from node labels."""

    n = registry.size()
    if n == 0:
        return np.zeros(0, dtype=np.float64)

    normalized_keywords = [
        keyword.strip().lower() for keyword in keywords if keyword and keyword.strip()
    ]
    v0 = np.zeros(n, dtype=np.float64)
    for idx in range(n):
        node = registry.get_node(idx)
        if node is None:
            continue
        haystack = f"{node.node_id} {node.label}".lower()
        count = sum(1 for keyword in normalized_keywords if keyword in haystack)
        v0[idx] = max(float(count) - float(threshold), 0.0)

    total = v0.sum()
    if np.isclose(total, 0.0):
        return np.full(n, 1.0 / n, dtype=np.float64)
    return v0 / total
