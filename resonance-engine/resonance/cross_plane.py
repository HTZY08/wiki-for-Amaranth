"""Cross-plane edge builder for the resonance engine."""

from __future__ import annotations

import json
import os
import re
import sqlite3

from resonance.node_registry import NodeRegistry
from resonance.config import STATE_DB, SOUL_PATHS


MEMORY_DB_PATH = ""
STATE_DB_PATH = STATE_DB


def extract_memory_nodes(
    hindsight_db_path: str = MEMORY_DB_PATH,
    min_importance: float = 0.3,
) -> list[tuple[str, str]]:
    """
    Extract memory nodes from hindsight.db.

    Returns [(node_id, content_preview), ...].
    """

    if not hindsight_db_path or not os.path.exists(hindsight_db_path):
        return []

    memories: list[tuple[str, str]] = []
    with sqlite3.connect(hindsight_db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        tables = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {row[0] for row in tables}

        if "memories" in table_names:
            rows = cur.execute(
                """
                SELECT id, content
                FROM memories
                WHERE importance >= ?
                ORDER BY importance DESC
                LIMIT 200
                """,
                (min_importance,),
            ).fetchall()
            for row in rows:
                mem_id = row["id"]
                content = row["content"][:80] if row["content"] else ""
                memories.append((f"mem:{mem_id}", content))

    return memories


def extract_soul_nodes(
    soul_file_paths: list[str] | None = None,
) -> list[tuple[str, str]]:
    """
    Extract soul/behavioral nodes from SOUL.md and similar files.

    Returns [(node_id, rule_text), ...].
    """

    if soul_file_paths is None:
        soul_file_paths = SOUL_PATHS

    nodes: list[tuple[str, str]] = []
    for filepath in soul_file_paths:
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r", encoding="utf-8") as handle:
            content = handle.read()

        sections = re.findall(r"^#{2,3}\s+(.+)$", content, re.MULTILINE)
        for section in sections[:10]:
            rule_id = f"soul:{os.path.basename(filepath)}:{section[:30]}"
            nodes.append((rule_id, section[:80]))

    return nodes


def build_cross_plane_edges(
    registry: NodeRegistry,
    state_db_path: str = STATE_DB_PATH,
    session_window_minutes: int = 60,
) -> list[tuple[int, int, float]]:
    """
    Build cross-plane edges from co-activations in session logs.

    Returns [(source_idx, target_idx, weight), ...].
    """

    if not os.path.exists(state_db_path):
        return []

    edges: list[tuple[int, int, float]] = []
    with sqlite3.connect(state_db_path) as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT m1.session_id, m1.tool_name as tool1, m2.tool_name as tool2,
                       m1.content as c1, m2.content as c2
                FROM messages m1
                JOIN messages m2 ON m1.session_id = m2.session_id
                WHERE m1.tool_name = 'skill_view'
                  AND m2.tool_name IN ('memory', 'session_search')
                  AND m1.id != m2.id
                  AND abs(m1.timestamp - m2.timestamp) < ?
                """,
                (session_window_minutes * 60,),
            )
            pairs = cur.fetchall()
        except sqlite3.Error:
            return []

    for _session_id, _tool1, _tool2, c1, _c2 in pairs:
        try:
            skill_data = json.loads(c1)
        except (json.JSONDecodeError, TypeError):
            continue

        skill_name = skill_data.get("name", "")
        skill_idx = registry.get_idx(skill_name)
        if skill_idx is None:
            continue

        # Memory/soul nodes are populated in a later phase; keep this as a stable stub.
        continue

    return edges
