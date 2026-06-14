"""Convert resonance activations into prompt context blocks."""

from __future__ import annotations

from dataclasses import dataclass

from resonance.matrix_engine import ResonanceConfig, ResonanceResult
from resonance.node_registry import NodeRegistry, PlaneType


@dataclass
class AssembledContext:
    """Context grouped by resonance plane plus a rendered prompt block."""

    skills: list[tuple[str, float]]
    memories: list[tuple[str, float]]
    soul_rules: list[tuple[str, float]]
    prompt_block: str


SKILL_TEMPLATE = "## Available Skills{}"
SKILL_ITEM = "- {name} (relevance: {score:.2f})"
MEMORY_TEMPLATE = "## Relevant Context{}"
SOUL_TEMPLATE = "## Active Constraints{}"


def assemble_context(
    result: ResonanceResult,
    registry: NodeRegistry,
    config: ResonanceConfig,
    soul_priority_map: dict[str, int] = None,
) -> AssembledContext:
    """Assemble activated resonance nodes into an LLM prompt block."""

    grouped: dict[PlaneType, list[tuple[str, float]]] = {
        PlaneType.SKILL: [],
        PlaneType.MEMORY: [],
        PlaneType.SOUL: [],
    }

    for node_id, plane_value, score in result.activated:
        node = registry.get_node_by_id(node_id)
        if node is not None:
            name = node.label or node.node_id
            plane = node.plane
        else:
            name = node_id
            try:
                plane = PlaneType(plane_value)
            except ValueError:
                continue
        if plane in grouped:
            grouped[plane].append((name, float(score)))

    skills = sorted(grouped[PlaneType.SKILL], key=lambda item: item[1], reverse=True)[
        : config.k_skills
    ]
    memories = sorted(grouped[PlaneType.MEMORY], key=lambda item: item[1], reverse=True)[
        : config.k_memories
    ]

    soul_rules = grouped[PlaneType.SOUL]
    if soul_priority_map:
        soul_rules = sorted(
            soul_rules,
            key=lambda item: (
                int(soul_priority_map.get(item[0], soul_priority_map.get(_node_id_for_label(registry, item[0]), 10_000))),
                -item[1],
            ),
        )
    else:
        soul_rules = sorted(soul_rules, key=lambda item: item[1], reverse=True)
    soul_rules = soul_rules[: config.k_soul]

    sections: list[str] = []
    if soul_rules:
        lines = [SOUL_TEMPLATE.format("")]
        lines.extend(f"- {name} (relevance: {score:.2f})" for name, score in soul_rules)
        lines.append("")
        lines.append("Rules listed first supersede subsequent rules in case of conflict.")
        sections.append("\n".join(lines))

    if memories:
        lines = [MEMORY_TEMPLATE.format("")]
        lines.extend(f"- {name} (relevance: {score:.2f})" for name, score in memories)
        sections.append("\n".join(lines))

    if skills:
        lines = [SKILL_TEMPLATE.format("")]
        lines.extend(SKILL_ITEM.format(name=name, score=score) for name, score in skills)
        sections.append("\n".join(lines))

    return AssembledContext(
        skills=skills,
        memories=memories,
        soul_rules=soul_rules,
        prompt_block="\n\n".join(sections),
    )


def _node_id_for_label(registry: NodeRegistry, label: str) -> str:
    for node_id in registry.all_ids():
        node = registry.get_node_by_id(node_id)
        if node is not None and node.label == label:
            return node.node_id
    return label
