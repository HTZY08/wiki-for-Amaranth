"""Evaluate cluster quality on the UMAP projection."""

from __future__ import annotations

import json
import sys

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from resonance.node_registry import NodeRegistry
from resonance.config import MATRIX_DIR


def evaluate_cluster_quality(
    coords_json_path: str,
    eps: float = 0.5,
    min_samples: int = 3,
) -> dict:
    """
    Load coordinates from JSON, run DBSCAN, and compute quality metrics.

    JSON format: [{node_id, x, y, cluster, label}, ...]
    """

    with open(coords_json_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise ValueError("coordinates JSON must contain a list of node objects")

    coords = np.asarray(
        [[float(item["x"]), float(item["y"])] for item in data], dtype=np.float64
    )
    n_nodes = int(coords.shape[0])
    if n_nodes == 0:
        return {
            "n_clusters": 0,
            "noise_fraction": 0.0,
            "silhouette_score": 0.0,
            "n_nodes": 0,
        }

    labels = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(coords)
    non_noise = labels != -1
    clusters = {int(label) for label in labels if int(label) != -1}
    n_clusters = len(clusters)
    noise_fraction = float(np.mean(labels == -1))

    silhouette = 0.0
    if n_clusters >= 2 and int(non_noise.sum()) > n_clusters:
        silhouette = float(silhouette_score(coords[non_noise], labels[non_noise]))

    return {
        "n_clusters": int(n_clusters),
        "noise_fraction": noise_fraction,
        "silhouette_score": silhouette,
        "n_nodes": n_nodes,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("coords_json", help="Path to coordinates JSON file")
    parser.add_argument("--eps", type=float, default=0.5)
    parser.add_argument("--min-samples", type=int, default=3)
    args = parser.parse_args()

    result = evaluate_cluster_quality(
        args.coords_json,
        eps=args.eps,
        min_samples=args.min_samples,
    )
    print(f"Clusters: {result['n_clusters']}")
    print(f"Noise:    {result['noise_fraction']:.1%}")
    print(f"Silhouette: {result['silhouette_score']:.3f}")
    print(f"Nodes:    {result['n_nodes']}")


if __name__ == "__main__":
    main()
