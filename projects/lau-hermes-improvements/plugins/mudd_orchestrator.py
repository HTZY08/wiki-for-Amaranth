"""
MUDD Workflow — 多路动态workflow编排

基于: MUDDFormer (ICML 2025)
"Breaking Residual Bottlenecks in Transformers via Multiway Dynamic Dense Connections"

核心思想:
  传统Transformer中残差连接让Q/K/V/R四路共享同一通道。MUDD为每一路
  独立地从所有前层动态聚合信息——根据当前token隐状态，动态生成通向
  所有前层的权重向量，而不是简单的"加1倍"。

Hermes映射:
  MUDDFormer                → Hermes
  ────────────────────────────────────
  Q路径                      → 需要"查询/搜索"的任务路径
  K路径                      → 需要"知识/记忆"的任务路径  
  V路径                      → 需要"执行/操作"的任务路径
  R(残差)路径                 → 需要"对话/交互"的任务路径
  动态权重                    → 根据输入自动路由到不同agent工作流

安装:
  plugins/mudd_orchestrator.py
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MUDDOrchestrator:
    """
    多路动态workflow编排器。
    
    根据输入内容特征，动态分配到不同的处理路径。
    对应MUDDFormer的Q/K/V/R四路独立连接。
    """

    # 四路处理路径定义
    ROUTES = {
        "query": {   # Q: 搜索/调研路径
            "name": "查询路径",
            "description": "需要搜索信息、查资料的任务",
            "toolsets": ["web", "search"],
            "max_turns": 10,
        },
        "knowledge": {  # K: 知识路径
            "name": "知识路径",
            "description": "需要推理、分析、解释的任务",
            "toolsets": ["session_search", "memory"],
            "max_turns": 8,
        },
        "execute": {  # V: 操作路径
            "name": "执行路径",
            "description": "需要修改文件、运行命令的任务",
            "toolsets": ["terminal", "file", "patch"],
            "max_turns": 15,
        },
        "interact": {  # R: 交互路径
            "name": "交互路径",
            "description": "需要写作、沟通、规划的任务",
            "toolsets": ["file", "todo"],
            "max_turns": 6,
        },
    }

    # MUDD风格: 每条路径有独立的"连接权重"（触发关键词）
    _QUERY_TRIGGERS = [
        r"research|调查|研究|搜索|查|find|search|look.?up",
        r"what.?is|who.?is|when.?did|where.?is",
        r"compare|对比|区别|difference",
    ]
    _KNOWLEDGE_TRIGGERS = [
        r"analyze|分析|解释|explain|why|how.?does|原理",
        r"reason|推理|逻辑|logic|deduce",
        r"evaluate|评估|评价|judge",
    ]
    _EXECUTE_TRIGGERS = [
        r"create|build|make|写|创建|实现|implement",
        r"fix|修复|debug|修改|change|update|add",
        r"run|执行|deploy|部署|install|安装",
        r"refactor|重构|optimize|优化",
    ]
    _INTERACT_TRIGGERS = [
        r"write|写|draft|起草|document|文档",
        r"plan|规划|plan|organize|组织|安排",
        r"chat|talk|discuss|讨论|think|想",
    ]

    @classmethod
    def route(cls, user_input: str) -> Dict:
        """
        根据输入内容动态路由到最匹配的路径。
        
        返回: {route_name, toolsets, max_turns}
        """
        text = user_input.lower()

        # 计算每条路径的MUDD"连接权重"（关键词匹配度）
        scores = {}
        for trigger, route_name in [
            (cls._QUERY_TRIGGERS, "query"),
            (cls._KNOWLEDGE_TRIGGERS, "knowledge"),
            (cls._EXECUTE_TRIGGERS, "execute"),
            (cls._INTERACT_TRIGGERS, "interact"),
        ]:
            score = sum(2 if re.search(p, text) else 0 for p in trigger)
            if score > 0:
                scores[route_name] = score

        if not scores:
            # 默认走interact路径（MUDD的残差路径）
            return {
                "route": "interact",
                **cls.ROUTES["interact"],
            }

        # 选最高分路径
        best = max(scores, key=scores.get)
        return {
            "route": best,
            **cls.ROUTES[best],
        }

    @classmethod
    def route_multi(cls, user_input: str) -> List[Dict]:
        """
        返回所有激活路径（对应MUDD的多路密集连接）。
        
        当输入包含多类型信号时，可能同时激活多条路径。
        """
        text = user_input.lower()
        active = []

        check = [
            (cls._QUERY_TRIGGERS, "query"),
            (cls._KNOWLEDGE_TRIGGERS, "knowledge"),
            (cls._EXECUTE_TRIGGERS, "execute"),
            (cls._INTERACT_TRIGGERS, "interact"),
        ]

        for triggers, route_name in check:
            if any(re.search(p, text) for p in triggers):
                active.append({
                    "route": route_name,
                    **cls.ROUTES[route_name],
                    "weight": sum(1 for p in triggers if re.search(p, text)),
                })

        if not active:
            active.append({
                "route": "interact",
                **cls.ROUTES["interact"],
                "weight": 1,
            })

        return sorted(active, key=lambda x: -x["weight"])


# Hermes plugin接口
def register(ctx):
    ctx.register_tool("mudd_orchestrate", {
        "name": "mudd_orchestrate",
        "description": "MUDD多路编排——根据输入自动分配到最佳处理路径",
        "parameters": {
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "用户输入/任务描述"},
            },
            "required": ["input"],
        },
        "handler": lambda input: MUDDOrchestrator.route(input),
    })
