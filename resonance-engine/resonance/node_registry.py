"""Node and plane index management for the resonance engine."""

from __future__ import annotations

import pickle
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PlaneType(Enum):
    """Supported resonance planes."""

    SKILL = "skill"
    MEMORY = "memory"
    SOUL = "soul"


@dataclass
class Node:
    """A node in the global resonance matrix."""

    node_id: str
    plane: PlaneType
    label: str
    idx: int


class NodeRegistry:
    """Registry mapping node ids and matrix indices to node metadata."""

    def __init__(self) -> None:
        """Initialize an empty node registry."""

        self._nodes: list[Node] = []
        self._by_id: dict[str, Node] = {}
        self._plane_ranges: dict[PlaneType, tuple[int, int]] = {}

    def add_node(self, node_id: str, plane: PlaneType, label: str = "") -> int:
        """Add a node and return its index, or return the existing index."""

        existing = self._by_id.get(node_id)
        if existing is not None:
            return existing.idx

        idx = len(self._nodes)
        node = Node(node_id=node_id, plane=plane, label=label, idx=idx)
        self._nodes.append(node)
        self._by_id[node_id] = node
        self.rebuild_ranges()
        return idx

    def get_idx(self, node_id: str) -> Optional[int]:
        """Return the matrix index for a node id, if present."""

        node = self._by_id.get(node_id)
        return node.idx if node is not None else None

    def get_node(self, idx: int) -> Optional[Node]:
        """Return the node at a matrix index, if present."""

        if 0 <= idx < len(self._nodes):
            return self._nodes[idx]
        return None

    def get_node_by_id(self, node_id: str) -> Optional[Node]:
        """Return a node by id, if present."""

        return self._by_id.get(node_id)

    def get_plane_range(self, plane: PlaneType) -> Optional[tuple[int, int]]:
        """Return the half-open index range for a plane, if any nodes exist."""

        return self._plane_ranges.get(plane)

    def size(self) -> int:
        """Return the number of registered nodes."""

        return len(self._nodes)

    def all_ids(self) -> list[str]:
        """Return all node ids in matrix-index order."""

        return [node.node_id for node in self._nodes]

    def rebuild_ranges(self) -> None:
        """Recalculate plane ranges from current nodes."""

        ranges: dict[PlaneType, list[int]] = {}
        for node in self._nodes:
            if node.plane not in ranges:
                ranges[node.plane] = [node.idx, node.idx + 1]
            else:
                ranges[node.plane][0] = min(ranges[node.plane][0], node.idx)
                ranges[node.plane][1] = max(ranges[node.plane][1], node.idx + 1)

        self._plane_ranges = {
            plane: (bounds[0], bounds[1]) for plane, bounds in ranges.items()
        }

    def save(self, path: str) -> None:
        """Serialize the registry to a pickle file."""

        with open(path, "wb") as handle:
            pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, path: str) -> "NodeRegistry":
        """Load a registry from a pickle file."""

        with open(path, "rb") as handle:
            registry = pickle.load(handle)
        if not isinstance(registry, cls):
            raise TypeError(f"Expected NodeRegistry pickle, got {type(registry)!r}")
        registry.rebuild_ranges()
        return registry
