#!/usr/bin/env python3
"""
Precision@K evaluation harness for the resonance engine.

Uses historical session data from state.db to measure how well resonance
predicts which skills should be loaded together.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict

import numpy as np

from resonance.config import STATE_DB, COOC_DB, MATRIX_DIR

from resonance.anti_collapse import build_transition_matrix
from resonance.matrix_engine import ResonanceConfig, ResonanceEngine
from resonance.node_registry import NodeRegistry, PlaneType


COOC_WINDOW_SECONDS = 60.0
ALT_PATTERN = re.compile(r"\[skill_view\]\s*name=(\S+)")


def precision_at_k(
    state_db_path: str | None = None,
    cooc_db_path: str | None = None,
    min_pairs: int = 2,
) -> tuple[list[dict], NodeRegistry, np.ndarray]:
    """
    Load evaluation cases, a skill registry, and per-node frequencies.

    Each test case is a set of skill_view calls that occurred in the same
    session with no more than 60 seconds between consecutive calls.
    """

    groups = _load_skill_groups(state_db_path)
    filtered_groups = [group for group in groups if len(group) >= max(2, min_pairs)]

    pairs = _load_cooc_pairs(cooc_db_path)
    skill_names = set()
    for group in filtered_groups:
        skill_names.update(group)
    for a, b, _ in pairs:
        skill_names.add(a)
        skill_names.add(b)

    registry = NodeRegistry()
    for name in sorted(skill_names):
        registry.add_node(name, PlaneType.SKILL, name)

    frequencies = np.zeros(registry.size(), dtype=np.float64)
    for group in filtered_groups:
        for skill in group:
            idx = _idx_for_skill(registry, skill)
            if idx is not None:
                frequencies[idx] += 1.0

    if pairs:
        pair_counts = Counter()
        for a, b, count in pairs:
            pair_counts[a] += int(count)
            pair_counts[b] += int(count)
        for node_id, count in pair_counts.items():
            idx = _idx_for_skill(registry, node_id)
            if idx is not None:
                frequencies[idx] = max(frequencies[idx], float(count))

    test_cases = [
        {
            "id": f"case_{i:05d}",
            "task_desc": ", ".join(group),
            "skills_used": group,
        }
        for i, group in enumerate(filtered_groups, 1)
    ]

    return test_cases, registry, frequencies


def precision_at_k(
    engine: ResonanceEngine,
    test_cases: list[dict],
    k: int = 5,
) -> dict:
    """
    Activate each observed skill and score whether its companions appear in top-k.
    """

    if k <= 0:
        raise ValueError("k must be positive")

    per_case: list[float] = []
    skill_scores: dict[str, list[float]] = defaultdict(list)
    n = engine.registry.size()
    k_eff = min(k, n)

    for case in test_cases:
        skills = _known_unique_skills(engine.registry, case.get("skills_used", []))
        if len(skills) < 2:
            continue

        anchor_scores: list[float] = []
        for anchor in skills:
            expected = set(skills)
            expected.discard(anchor)
            if not expected:
                continue

            anchor_idx = _idx_for_skill(engine.registry, anchor)
            if anchor_idx is None:
                continue

            v0 = np.zeros(n, dtype=np.float64)
            v0[anchor_idx] = 1.0
            result = engine.compute(v0)
            top_ids = _top_skill_ids(engine, result.v_final, k_eff, exclude={anchor})
            hits = len(set(top_ids).intersection(expected))
            denom = min(k_eff, len(expected))
            score = float(hits / denom) if denom else 0.0
            anchor_scores.append(score)
            skill_scores[anchor].append(score)

        if anchor_scores:
            per_case.append(float(np.mean(anchor_scores)))

    per_case_arr = np.asarray(per_case, dtype=np.float64)
    skill_breakdown = {
        skill: float(np.mean(scores)) for skill, scores in skill_scores.items() if scores
    }

    return {
        "mean_precision": float(per_case_arr.mean()) if per_case else 0.0,
        "median_precision": float(np.median(per_case_arr)) if per_case else 0.0,
        "per_case": per_case,
        "k": int(k),
        "n_cases": len(per_case),
        "coverage": float(np.mean(per_case_arr > 0.0)) if per_case else 0.0,
        "skill_breakdown": skill_breakdown,
    }


def run_precision_eval(
    k: int = 5,
    theta: float = 0.01,
    matrix_dir: str | None = None,
    state_db_path: str | None = None,
    cooc_db_path: str | None = None,
) -> dict:
    """Run the full Precision@K evaluation pipeline."""

    test_cases, registry, frequencies = precision_at_k(
        state_db_path or STATE_DB, cooc_db_path or COOC_DB
    )
    if registry.size() == 0:
        result = _empty_result(k)
        _print_result(result, 0)
        return result

    matrix_dir = matrix_dir or MATRIX_DIR
    matrix_path = os.path.join(matrix_dir, "matrix.npz")
    registry_path = os.path.join(matrix_dir, "registry.pkl")
    config = ResonanceConfig(theta=theta)
    engine = ResonanceEngine.load(matrix_path, registry_path, config)

    if engine is None:
        W_raw = _build_w_raw_from_cooc(cooc_db_path or COOC_DB, registry)
        M = build_transition_matrix(W_raw, frequencies, registry)
        engine = ResonanceEngine(M, registry, config)

    result = precision_at_k(engine, test_cases, k=k)
    _print_result(result, engine.registry.size())
    return result


def main():
    """CLI entry point."""

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--theta", type=float, default=0.01)
    parser.add_argument("--matrix-dir", default=None)
    parser.add_argument("--state-db", default=None)
    parser.add_argument("--cooc-db", default=None)
    args = parser.parse_args()

    run_precision_eval(
        k=args.k, theta=args.theta,
        matrix_dir=args.matrix_dir,
        state_db_path=args.state_db,
        cooc_db_path=args.cooc_db,
    )


def _extract_skill_name(content: str | None) -> str | None:
    if not content:
        return None
    if content.lstrip().startswith("{"):
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = None
        if isinstance(data, dict) and data.get("name"):
            return str(data["name"])
    match = ALT_PATTERN.search(content)
    if match:
        return match.group(1)
    return None


def _load_skill_groups(state_db_path: str) -> list[list[str]]:
    if not os.path.exists(state_db_path):
        return []

    with sqlite3.connect(state_db_path) as conn:
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='messages'"
        ).fetchone()
        if exists is None:
            return []
        rows = conn.execute(
            """
            SELECT id, session_id, content, timestamp
            FROM messages
            WHERE tool_name = 'skill_view'
              AND content IS NOT NULL
            ORDER BY session_id, timestamp, id
            """
        ).fetchall()

    by_session: dict[str, list[tuple[float, str]]] = defaultdict(list)
    for _msg_id, session_id, content, timestamp in rows:
        name = _extract_skill_name(content)
        if name:
            by_session[str(session_id)].append((float(timestamp), name))

    groups: list[list[str]] = []
    for calls in by_session.values():
        calls.sort(key=lambda item: item[0])
        current: set[str] = set()
        last_ts: float | None = None
        for timestamp, name in calls:
            if last_ts is not None and timestamp - last_ts > COOC_WINDOW_SECONDS:
                if len(current) > 1:
                    groups.append(sorted(current))
                current = set()
            current.add(name)
            last_ts = timestamp
        if len(current) > 1:
            groups.append(sorted(current))

    return groups


def _load_cooc_pairs(cooc_db_path: str) -> list[tuple[str, str, int]]:
    if not os.path.exists(cooc_db_path):
        return []

    with sqlite3.connect(cooc_db_path) as conn:
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='cooc'"
        ).fetchone()
        if exists is None:
            return []
        rows = conn.execute("SELECT skill_a, skill_b, count FROM cooc").fetchall()

    pairs: list[tuple[str, str, int]] = []
    for a, b, count in rows:
        if a and b and int(count) > 0:
            pairs.append((str(a), str(b), int(count)))
    return pairs


def _build_w_raw_from_cooc(cooc_db_path: str, registry: NodeRegistry) -> np.ndarray:
    W = np.zeros((registry.size(), registry.size()), dtype=np.float64)
    for a, b, count in _load_cooc_pairs(cooc_db_path):
        i = _idx_for_skill(registry, a)
        j = _idx_for_skill(registry, b)
        if i is None or j is None or i == j:
            continue
        W[i, j] += float(count)
        W[j, i] += float(count)
    return W


def _idx_for_skill(registry: NodeRegistry, skill: str) -> int | None:
    idx = registry.get_idx(skill)
    if idx is not None:
        return idx
    return registry.get_idx(f"skill:{skill}")


def _known_unique_skills(registry: NodeRegistry, skills: list[str]) -> list[str]:
    seen = set()
    known = []
    for skill in skills:
        if skill in seen:
            continue
        if _idx_for_skill(registry, skill) is not None:
            seen.add(skill)
            known.append(skill)
    return known


def _top_skill_ids(
    engine: ResonanceEngine,
    scores: np.ndarray,
    k: int,
    exclude: set[str] | None = None,
) -> list[str]:
    exclude = exclude or set()
    ranked: list[tuple[float, str]] = []
    for idx, score in enumerate(scores):
        node = engine.registry.get_node(idx)
        if node is None or node.plane != PlaneType.SKILL:
            continue
        if node.node_id in exclude or node.label in exclude:
            continue
        ranked.append((float(score), node.node_id))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [node_id for _score, node_id in ranked[:k]]


def _empty_result(k: int) -> dict:
    return {
        "mean_precision": 0.0,
        "median_precision": 0.0,
        "per_case": [],
        "k": int(k),
        "n_cases": 0,
        "coverage": 0.0,
        "skill_breakdown": {},
    }


def _print_result(result: dict, n_nodes: int) -> None:
    print(f"\n{'=' * 60}")
    print("  RESONANCE EVALUATION")
    print(f"{'=' * 60}")
    print(f"  Precision@{result['k']}: {result['mean_precision']:.3f}")
    print(f"  Median:           {result['median_precision']:.3f}")
    print(f"  Coverage:         {result['coverage']:.1%}")
    print(f"  Test cases:       {result['n_cases']}")
    baseline = (result["k"] / n_nodes) if n_nodes else 0.0
    print(f"  Random baseline:  ~{baseline:.3f} (k/N)")
    print("\n  Per-skill breakdown (top 15):")
    for skill, precision in sorted(
        result["skill_breakdown"].items(), key=lambda item: -item[1]
    )[:15]:
        print(f"    {skill:40s} {precision:.3f}")


if __name__ == "__main__":
    main()
