#!/usr/bin/env python3
"""Extended cron entry point for the resonance engine."""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import time
from collections import Counter

# Ensure user site-packages is in path (cron runs with minimal env)
_USER_SITE = os.path.expanduser("~/.local/lib/python3.13/site-packages")
if os.path.isdir(_USER_SITE) and _USER_SITE not in sys.path:
    sys.path.insert(0, _USER_SITE)

import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
for path in (SCRIPT_DIR, "/tmp/resonance2"):
    if path not in sys.path:
        sys.path.insert(0, path)

from skill_monitor import incremental_update, init_db as init_cooc_db, save_cooc

from resonance.anti_collapse import build_transition_matrix
from resonance.cold_start import bootstrap_W_raw, load_skill_manifest
from resonance.node_registry import NodeRegistry, PlaneType
from resonance.temporal import exponential_decay, momentum_update
from resonance.config import (
    STATE_DB, COOC_DB, RESONANCE_DB, MANIFEST_PATH, MATRIX_DIR,
    NUM_ITERATIONS, DAMPING_FACTOR,
)

RESONANCE_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS matrix_state (
    id INTEGER PRIMARY KEY,
    rebuilt_at REAL,
    n_nodes INTEGER,
    nnz_edges INTEGER,
    drift_magnitude REAL,
    beta_used REAL,
    precision_k REAL,
    time_ms REAL
);

CREATE TABLE IF NOT EXISTS node_frequencies (
    node_id TEXT PRIMARY KEY,
    frequency INTEGER DEFAULT 0,
    last_updated REAL
);

CREATE TABLE IF NOT EXISTS w_raw_snapshot (
    source_id TEXT,
    target_id TEXT,
    weight REAL,
    PRIMARY KEY (source_id, target_id)
);
"""


def init_resonance_db(db_path: str):
    """Create resonance.db schema if not exists and enable WAL mode."""

    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(RESONANCE_DB_SCHEMA)
    _ensure_column(conn, "matrix_state", "precision_k", "REAL")
    conn.commit()
    return conn


def _ensure_column(conn, table: str, column: str, definition: str) -> None:
    columns = {
        row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
    }
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def log_matrix_state(
    conn,
    n_nodes: int,
    nnz_edges: int,
    drift_magnitude: float,
    beta_used: float,
    precision_k: float,
    time_ms: float,
) -> None:
    """Insert a rebuild stats record."""

    conn.execute(
        """
        INSERT INTO matrix_state
            (rebuilt_at, n_nodes, nnz_edges, drift_magnitude, beta_used, precision_k, time_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            time.time(),
            n_nodes,
            nnz_edges,
            drift_magnitude,
            beta_used,
            precision_k,
            time_ms,
        ),
    )
    conn.commit()


def atomic_save_matrix(M, registry, matrix_path: str, registry_path: str) -> None:
    """Atomically save matrix and registry using temp files and os.replace."""

    from scipy.sparse import save_npz

    matrix_dir = os.path.dirname(matrix_path) or "."
    registry_dir = os.path.dirname(registry_path) or "."
    os.makedirs(matrix_dir, exist_ok=True)
    os.makedirs(registry_dir, exist_ok=True)

    matrix_tmp = f"{matrix_path}.tmp.npz"
    registry_tmp = f"{registry_path}.tmp.pkl"
    save_npz(matrix_tmp, M)
    registry.save(registry_tmp)
    os.replace(matrix_tmp, matrix_path)
    os.replace(registry_tmp, registry_path)


def run_monitor_incremental() -> tuple[Counter, Counter, int | None]:
    """Run the existing monitor incrementally and persist new cooc rows."""

    conn = init_cooc_db()
    cur = conn.cursor()
    cur.execute("SELECT MAX(last_id) FROM watch_position")
    last_id = cur.fetchone()[0]
    last_id = last_id or 0

    cooc_extra, skill_extra, new_last_id = incremental_update(last_id)
    if cooc_extra or new_last_id != last_id:
        save_cooc(conn, cooc_extra, new_last_id)
    conn.close()
    return cooc_extra, skill_extra, new_last_id


def run_resonance_rebuild(
    cooc_db_path: str = COOC_DB,
    resonance_db_path: str = RESONANCE_DB,
    matrix_dir: str = MATRIX_DIR,
    manifest_path: str = MANIFEST_PATH,
    skip_viz: bool = True,
) -> dict:
    """Full rebuild pipeline. Returns stats dict."""

    del skip_viz
    started = time.time()
    rebuilt_at = started
    os.makedirs(matrix_dir, exist_ok=True)

    manifest = load_skill_manifest(manifest_path)
    pairs = _load_cooc_pairs(cooc_db_path)
    skill_names = _collect_skill_names(manifest, pairs)

    registry = NodeRegistry()
    for name in sorted(skill_names):
        registry.add_node(name, PlaneType.SKILL, name)

    n = registry.size()
    conn = init_resonance_db(resonance_db_path)
    frequencies = _load_frequencies(conn, registry)

    old_W = _load_w_raw_snapshot(conn, registry)
    if old_W is None:
        old_W = bootstrap_W_raw(manifest, registry)

    last_rebuild = _last_rebuild_time(conn)
    delta_days = 0.0 if last_rebuild is None else (rebuilt_at - last_rebuild) / 86400.0
    decayed_W = exponential_decay(old_W, delta_days)
    delta_W = _pairs_to_matrix(pairs, registry)
    W_new, drift = momentum_update(decayed_W, delta_W)
    np.fill_diagonal(W_new, 0.0)

    _save_w_raw_snapshot(conn, registry, W_new)
    _save_frequencies(conn, registry, pairs)
    frequencies = _load_frequencies(conn, registry)

    M = build_transition_matrix(W_new, frequencies, registry)
    matrix_path = os.path.join(matrix_dir, "matrix.npz")
    registry_path = os.path.join(matrix_dir, "registry.pkl")
    atomic_save_matrix(M, registry, matrix_path, registry_path)

    nnz_edges = int(np.count_nonzero(W_new))
    beta_used = 0.5 if drift > 2.0 else 0.9
    elapsed_ms = (time.time() - started) * 1000.0
    precision_k = 0.0
    log_matrix_state(conn, n, nnz_edges, drift, beta_used, precision_k, elapsed_ms)
    conn.close()

    return {
        "rebuilt_at": rebuilt_at,
        "n_nodes": n,
        "nnz_edges": nnz_edges,
        "drift_magnitude": drift,
        "beta_used": beta_used,
        "time_ms": elapsed_ms,
        "matrix_path": matrix_path,
        "registry_path": registry_path,
    }


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
    return [(str(a), str(b), int(c)) for a, b, c in rows if a and b and int(c) > 0]


def _collect_skill_names(manifest: dict, pairs: list[tuple[str, str, int]]) -> set[str]:
    names = set()
    skills = manifest.get("skills", {}) if isinstance(manifest, dict) else {}
    names.update(str(name) for name in skills.keys())
    for metadata in skills.values():
        if isinstance(metadata, dict):
            names.update(str(name) for name in metadata.get("related_skills") or [])
    for a, b, _ in pairs:
        names.add(a)
        names.add(b)
    return names


def _pairs_to_matrix(
    pairs: list[tuple[str, str, int]], registry: NodeRegistry
) -> np.ndarray:
    W = np.zeros((registry.size(), registry.size()), dtype=np.float64)
    for a, b, count in pairs:
        idx_a = registry.get_idx(a)
        idx_b = registry.get_idx(b)
        if idx_a is None or idx_b is None or idx_a == idx_b:
            continue
        W[idx_a, idx_b] += float(count)
        W[idx_b, idx_a] += float(count)
    return W


def _load_w_raw_snapshot(conn, registry: NodeRegistry) -> np.ndarray | None:
    row = conn.execute("SELECT COUNT(*) FROM w_raw_snapshot").fetchone()
    if row is None or row[0] == 0:
        return None
    W = np.zeros((registry.size(), registry.size()), dtype=np.float64)
    rows = conn.execute(
        "SELECT source_id, target_id, weight FROM w_raw_snapshot"
    ).fetchall()
    for source_id, target_id, weight in rows:
        i = registry.get_idx(source_id)
        j = registry.get_idx(target_id)
        if i is not None and j is not None:
            W[i, j] = float(weight)
    return W


def _save_w_raw_snapshot(conn, registry: NodeRegistry, W: np.ndarray) -> None:
    conn.execute("DELETE FROM w_raw_snapshot")
    rows = []
    ids = registry.all_ids()
    for i, source_id in enumerate(ids):
        for j, target_id in enumerate(ids):
            weight = float(W[i, j])
            if weight > 0.0:
                rows.append((source_id, target_id, weight))
    conn.executemany(
        """
        INSERT INTO w_raw_snapshot (source_id, target_id, weight)
        VALUES (?, ?, ?)
        """,
        rows,
    )


def _save_frequencies(
    conn, registry: NodeRegistry, pairs: list[tuple[str, str, int]]
) -> None:
    counts = Counter()
    for a, b, count in pairs:
        counts[a] += int(count)
        counts[b] += int(count)
    now = time.time()
    for node_id in registry.all_ids():
        conn.execute(
            """
            INSERT INTO node_frequencies (node_id, frequency, last_updated)
            VALUES (?, ?, ?)
            ON CONFLICT(node_id) DO UPDATE SET
                frequency = excluded.frequency,
                last_updated = excluded.last_updated
            """,
            (node_id, counts.get(node_id, 0), now),
        )


def _load_frequencies(conn, registry: NodeRegistry) -> np.ndarray:
    freqs = np.zeros(registry.size(), dtype=np.float64)
    rows = conn.execute("SELECT node_id, frequency FROM node_frequencies").fetchall()
    for node_id, frequency in rows:
        idx = registry.get_idx(node_id)
        if idx is not None:
            freqs[idx] = float(frequency)
    return freqs


def _last_rebuild_time(conn) -> float | None:
    row = conn.execute("SELECT MAX(rebuilt_at) FROM matrix_state").fetchone()
    return None if row is None or row[0] is None else float(row[0])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-viz", action="store_true", default=True)
    parser.add_argument("--no-monitor", action="store_true")
    args = parser.parse_args()

    if not args.no_monitor:
        if os.path.exists(STATE_DB):
            cooc_extra, _, _ = run_monitor_incremental()
            print(f"[RESONANCE] monitor saved {len(cooc_extra)} new pairs")
        else:
            print(f"[RESONANCE] state db not found at {STATE_DB}; skipping monitor")

    stats = run_resonance_rebuild(skip_viz=args.skip_viz)
    print(
        f"[RESONANCE] rebuilt N={stats['n_nodes']}, nnz={stats['nnz_edges']}, "
        f"drift={stats['drift_magnitude']:.3f}, time={stats['time_ms']:.0f}ms"
    )


if __name__ == "__main__":
    main()
