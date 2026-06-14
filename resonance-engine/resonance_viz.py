#!/usr/bin/env python3
"""
UMAP-based 2D visualization of the resonance matrix.

Produces an interactive Plotly HTML file and a companion JSON file.
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np

from resonance.node_registry import NodeRegistry
from resonance.config import MATRIX_DIR


def build_node_embeddings_for_umap(
    matrix_dir: str | None = None,
) -> tuple[np.ndarray, NodeRegistry]:
    """
    Use rows of the transition matrix M as feature vectors for UMAP.

    For isolated nodes with zero rows, use the corresponding one-hot vector.
    """
    M_path = os.path.join(matrix_dir or MATRIX_DIR, "matrix.npz")
    registry_path = os.path.join(matrix_dir or MATRIX_DIR, "registry.pkl")
    from scipy.sparse import load_npz

    M = load_npz(M_path)
    registry = NodeRegistry.load(registry_path)
    if M.shape[0] != M.shape[1] or M.shape[0] != registry.size():
        raise ValueError("matrix dimensions must match registry size")

    X = M.toarray().astype(np.float64)
    row_sums = X.sum(axis=1)
    zero_rows = np.where(np.isclose(row_sums, 0.0))[0]
    for idx in zero_rows:
        X[idx, idx] = 1.0

    return X, registry


def run_umap(
    X: np.ndarray,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
    random_state: int = 42,
) -> np.ndarray:
    """Run UMAP projection to 2D and return an (N, 2) coordinate array."""

    import umap

    if X.ndim != 2:
        raise ValueError("X must be a 2D array")
    if X.shape[0] == 0:
        return np.zeros((0, 2), dtype=np.float64)
    if X.shape[0] == 1:
        return np.zeros((1, 2), dtype=np.float64)

    neighbors = max(2, min(int(n_neighbors), X.shape[0] - 1))
    reducer = umap.UMAP(
        n_neighbors=neighbors,
        min_dist=min_dist,
        n_components=2,
        random_state=random_state,
    )
    return reducer.fit_transform(X)


def export_plotly_html(
    coords: np.ndarray,
    registry: NodeRegistry,
    output_path: str,
) -> str:
    """
    Generate an interactive Plotly scatter plot.

    Points are colored by plane type and hover labels show node ids.
    """

    import plotly.graph_objects as go
    from plotly.colors import DEFAULT_PLOTLY_COLORS

    coords = np.asarray(coords, dtype=np.float64)
    if coords.shape != (registry.size(), 2):
        raise ValueError("coords must have shape (N, 2)")

    planes: dict[str, dict[str, list]] = {}
    for idx in range(registry.size()):
        node = registry.get_node(idx)
        plane = node.plane.value if node else "unknown"
        planes.setdefault(plane, {"x": [], "y": [], "labels": [], "ids": []})
        planes[plane]["x"].append(float(coords[idx, 0]))
        planes[plane]["y"].append(float(coords[idx, 1]))
        planes[plane]["labels"].append(node.label if node else f"node_{idx}")
        planes[plane]["ids"].append(node.node_id if node else f"n{idx}")

    fig = go.Figure()
    for idx, (plane, data) in enumerate(sorted(planes.items())):
        fig.add_trace(
            go.Scatter(
                x=data["x"],
                y=data["y"],
                mode="markers+text",
                name=plane,
                text=data["labels"],
                textposition="top center",
                textfont=dict(size=8),
                hovertext=[
                    f"{node_id}<br>{label}"
                    for node_id, label in zip(data["ids"], data["labels"])
                ],
                hoverinfo="text",
                marker=dict(
                    size=10,
                    color=DEFAULT_PLOTLY_COLORS[idx % len(DEFAULT_PLOTLY_COLORS)],
                    line=dict(width=1, color="white"),
                ),
            )
        )

    fig.update_layout(
        title="Resonance Engine - Skill Map",
        width=1200,
        height=800,
        hovermode="closest",
        template="plotly_white",
        showlegend=True,
    )

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    fig.write_html(output_path)
    return output_path


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix-dir", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--n-neighbors", type=int, default=15)
    parser.add_argument("--min-dist", type=float, default=0.1)
    args = parser.parse_args()

    matrix_dir = args.matrix_dir or MATRIX_DIR
    output_path = args.output or os.path.join(matrix_dir, "skill_map.html")

    print("Loading matrix...")
    X, registry = build_node_embeddings_for_umap(matrix_dir)
    print(f"Loaded {registry.size()} nodes, X shape: {X.shape}")

    print("Running UMAP...")
    coords = run_umap(X, n_neighbors=args.n_neighbors, min_dist=args.min_dist)

    print("Exporting HTML...")
    path = export_plotly_html(coords, registry, output_path)
    print(f"Saved to {path}")

    json_path = output_path[:-5] + ".json" if output_path.endswith(".html") else f"{args.output}.json"
    nodes_data = []
    for idx in range(registry.size()):
        node = registry.get_node(idx)
        nodes_data.append(
            {
                "node_id": node.node_id if node else f"n{idx}",
                "label": node.label if node else f"Node {idx}",
                "plane": node.plane.value if node else "unknown",
                "x": float(coords[idx, 0]),
                "y": float(coords[idx, 1]),
            }
        )
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(nodes_data, handle, ensure_ascii=False, indent=2)
    print(f"JSON: {json_path}")


if __name__ == "__main__":
    main()
