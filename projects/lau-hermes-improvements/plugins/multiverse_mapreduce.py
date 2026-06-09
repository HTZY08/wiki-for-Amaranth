"""
Multiverse MapReduce — 任务分解与并行归并工具

基于: Multiverse (NeurIPS 2025) 
"Your Language Models Secretly Decide How to Parallelize and Merge Generation"

核心思想:
  Multiverse将LLM推理从顺序自回归改造为MapReduce范式——先将任务分解为
  可并行计算的子任务（Map），独立执行（Process），再合并结果（Reduce）。

  Hermes Agent中，这个模式直接对应delegate_task的增强——当前delegate_task
  已支持tasks数组做并行，但缺少"自动分解"和"结果归并"两个阶段。

功能:
  1. analyze_task() — 分析用户请求，识别可并行子任务
  2. map_reduce() — 执行完整的Map→Process→Reduce流程
  3. merge_results() — 将多个子结果合并为统一输出

安装:
  1. 复制到 /opt/hermes/plugins/multiverse/
  2. 在 config.yaml 中添加:
     tools:
       enabled_plugins: [multiverse]
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# 最大并行子任务数
MAX_PARALLEL_TASKS = 5


def analyze_task(goal: str, context: str = "") -> List[Dict]:
    """
    分析任务，识别可并行执行的子任务。

    这是一个规则驱动的分解器，识别以下模式：
      1. "A和B" / "A与B" — 并列关系
      2. "对比X和Y" / "比较" — 对比关系
      3. "同时分析" / "多角度" — 多视角
      4. "遍历" / "所有文件" — 批量处理

    返回子任务列表，每个包含 goal/context/toolsets。
    """
    text = (goal + " " + context).lower()
    sub_tasks = []

    # 模式1: "分析X和Y" / "比较X与Y"
    compare_match = _extract_compare_items(text)
    if compare_match:
        items = compare_match
        for item in items:
            sub_tasks.append({
                "goal": f"分析: {item.strip()}",
                "context": f"主任务: {goal}\n分析对象: {item.strip()}",
                "toolsets": ["web", "search"],
            })

    # 模式2: "同时" / "多角度"
    if "同时" in text or "多角度" in text or "multi" in text:
        angles = _extract_angles(text)
        for angle in angles:
            sub_tasks.append({
                "goal": f"从{angle}角度分析: {goal}",
                "context": f"主任务: {goal}\n角度: {angle}",
                "toolsets": ["web", "search"],
            })

    # 模式3: 文件遍历
    if any(kw in text for kw in ["遍历", "所有文件", "each file", "all files"]):
        sub_tasks.append({
            "goal": f"遍历分析: {goal}",
            "context": f"主任务: {goal}\n逐个文件分析",
            "toolsets": ["terminal", "file"],
        })

    # 如果没有识别出子任务，返回空列表（由agent自行决定）
    return sub_tasks[:MAX_PARALLEL_TASKS]


def _extract_compare_items(text: str) -> List[str]:
    """提取对比/并列关系中的项目"""
    items = []

    # "X和Y的对比"
    patterns = [
        r"(?:比较|对比|分析|研究)(.+?)(?:和|与|and|vs\.?|versus)(.+?)(?:的|$)",
        r"(.+?)(?:和|与|and)(.+?)(?:有什么|的区别|的异同)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            for g in match.groups():
                if g and len(g) < 50:
                    items.append(g.strip())
            break

    # 枚举列表 "A、B、C"
    enum_match = re.findall(r"([\u4e00-\u9fff\w]+)[、,，]\s*", text)
    if len(enum_match) >= 2:
        items = enum_match

    if len(items) >= 2:
        # 去重
        seen = set()
        deduped = []
        for item in items:
            if item not in seen:
                seen.add(item)
                deduped.append(item)
        return deduped[:MAX_PARALLEL_TASKS]

    return []


def _extract_angles(text: str) -> List[str]:
    """提取多角度关键词"""
    angle_keywords = [
        "性能", "安全", "成本", "可用性", "可维护性",
        "performance", "security", "cost", "usability",
        "技术", "业务", "架构", "算法",
        "正面", "负面", "机遇", "风险",
    ]
    found = []
    for kw in angle_keywords:
        if kw in text:
            found.append(kw)
    return found[:MAX_PARALLEL_TASKS]


def merge_results(
    original_goal: str,
    sub_results: List[Tuple[str, str]],
) -> str:
    """
    将多个并行子任务结果合并为统一回答。

    参数:
      original_goal: 原始任务目标
      sub_results: [(子任务goal, 子任务结果), ...]

    返回:
      合并后的最终回答
    """
    if not sub_results:
        return "未收集到子任务结果。"

    if len(sub_results) == 1:
        return sub_results[0][1]

    # 结构化合并
    parts = [f"# {original_goal}\n"]

    for i, (sub_goal, result) in enumerate(sub_results, 1):
        parts.append(f"## {i}. {sub_goal}")
        parts.append("")
        # 截断过长的结果
        if len(result) > 5000:
            parts.append(result[:5000])
            parts.append(f"\n... [{len(result) - 5000} chars 省略]")
        else:
            parts.append(result)
        parts.append("")

    # 综合总结
    parts.append("---")
    parts.append(f"**以上 {len(sub_results)} 个子任务已完成并行分析。**")
    parts.append(f"来源: Multiverse MapReduce (NeurIPS'25)")

    return "\n".join(parts)


def map_reduce(
    goal: str,
    context: str = "",
    toolsets: Optional[List[str]] = None,
    max_parallel: int = 3,
) -> Dict:
    """
    完整的MapReduce执行流程。

    返回:
      {
        "status": "completed" | "no_subtasks" | "error",
        "sub_tasks": [...],
        "merged_result": "...",
        "parallel_count": N
      }

    调用方式（在Hermes中）:
      result = map_reduce(goal="研究A、B、C三个框架")
      # 内部会自动:
      #   1. analyze_task() → 识别子任务
      #   2. 对每个子任务调用 delegate_task()
      #   3. merge_results() → 合并输出
    """
    sub_tasks = analyze_task(goal, context)

    if not sub_tasks:
        return {
            "status": "no_subtasks",
            "sub_tasks": [],
            "merged_result": goal,
            "parallel_count": 0,
            "message": "未检测到可并行子任务，按常规方式执行。"
        }

    # 限制并发数
    sub_tasks = sub_tasks[:min(max_parallel, MAX_PARALLEL_TASKS)]

    # 构建delegate_task可接受的tasks参数
    tasks_param = []
    for st in sub_tasks:
        task = {
            "goal": st["goal"],
            "context": st.get("context", context),
        }
        if st.get("toolsets"):
            task["toolsets"] = st["toolsets"]
        tasks_param.append(task)

    # 注意: 实际的delegate_task调用由Hermes引擎执行
    # 这里返回tasks参数供Hermes调用
    return {
        "status": "ready",
        "sub_tasks": sub_tasks,
        "delegate_payload": tasks_param,
        "parallel_count": len(sub_tasks),
        "message": f"已分解为 {len(sub_tasks)} 个可并行子任务。"
    }


# ===========================================================================
# Hermes plugin 接口
# ===========================================================================

def register(ctx):
    """向Hermes注册Multiverse工具"""
    ctx.register_tool("multiverse_analyze", {
        "name": "multiverse_analyze",
        "description": "分析任务的可并行性，识别独立子任务",
        "parameters": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "任务目标"},
                "context": {"type": "string", "description": "上下文信息"},
            },
            "required": ["goal"],
        },
        "handler": lambda goal, context="": analyze_task(goal, context),
    })

    ctx.register_tool("multiverse_merge", {
        "name": "multiverse_merge",
        "description": "合并多个并行子任务的结果",
        "parameters": {
            "type": "object",
            "properties": {
                "goal": {"type": "string"},
                "sub_results": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": [{"type": "string"}, {"type": "string"}],
                    },
                },
            },
            "required": ["goal", "sub_results"],
        },
        "handler": lambda goal, sub_results: merge_results(goal, sub_results),
    })

    ctx.register_tool("multiverse_map_reduce", {
        "name": "multiverse_map_reduce",
        "description": "MapReduce全流程：分解→准备并行→合并模板",
        "parameters": {
            "type": "object",
            "properties": {
                "goal": {"type": "string"},
                "context": {"type": "string"},
            },
            "required": ["goal"],
        },
        "handler": lambda goal, context="": map_reduce(goal, context),
    })


# 需要re模块
import re
