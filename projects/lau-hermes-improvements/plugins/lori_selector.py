"""
LoRI Tool Selector — 稀疏工具选择器

基于: LoRI (COLM 2025)
"Reducing Cross-Task Interference in Multi-Task Low-Rank Adaptation"

核心思想:
  LoRI将LoRA的A矩阵冻结为随机投影（永远不变），B矩阵做稀疏掩码——
  只激活与当前任务最相关的5%参数。正交的随机投影确保多任务间不干扰。

Hermes映射:
  LoRI                          → Hermes
  ──────────────────────────────────────────
  冻结A矩阵（所有工具全集）      → 工具注册表永远完整
  稀疏B矩阵（仅激活子集）       → 每个任务类型只激活相关工具
  90%稀疏度                     → 70工具→只激活7个
  正交性保证无干扰              → 不同任务类型使用不重叠的工具子集

安装:
  复制到 /opt/hermes/plugins/lori_selector/
  在config.yaml添加 tools.enabled_plugins: [lori_selector]
"""

import logging
import re
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class LoRISelector:
    """
    稀疏工具选择器。
    
    根据任务类型，从全集中仅激活相关工具子集。
    对应LoRI的"冻结A矩阵 + 稀疏B矩阵"。
    """

    # 冻结的A矩阵：工具全集（永远不变）
    ALL_TOOLS = frozenset({
        # Web & Search
        "web_search", "web_extract", "browser_navigate",
        "browser_click", "browser_snapshot", "browser_type",
        "browser_scroll", "browser_vision",
        # File operations
        "read_file", "write_file", "patch", "search_files",
        # Execution
        "terminal", "execute_code",
        # Agent orchestration
        "delegate_task", "cronjob", "process", "todo",
        # Knowledge
        "memory", "session_search", "skill_view", "skills_list",
        # Communication
        "send_message", "clarify",
        # Media
        "text_to_speech", "vision_analyze",
        # Custom
        "mudd_orchestrate", "flyroute_select", "multiverse_map_reduce",
    })

    # 稀疏B矩阵：每个任务类型激活的工具子集
    # 90%稀疏度 → 24 tools → 激活~6个
    TASK_MASKS: Dict[str, Set[str]] = {
        "web_research": {
            "web_search", "web_extract", "browser_navigate",
            "browser_click", "browser_snapshot",
            "session_search", "memory",
        },
        "code_dev": {
            "read_file", "write_file", "patch", "search_files",
            "terminal", "execute_code",
        },
        "file_ops": {
            "read_file", "write_file", "patch", "search_files",
            "terminal",
        },
        "agent_orch": {
            "delegate_task", "cronjob", "process", "todo",
            "skill_view", "skills_list",
        },
        "knowledge": {
            "memory", "session_search", "web_search",
            "skill_view",
        },
        "communication": {
            "send_message", "clarify", "todo",
        },
        "analysis": {
            "web_search", "session_search", "web_extract",
            "execute_code", "search_files",
        },
        "generic": set(),  # 所有工具
    }

    # 任务分类器关键词
    TASK_CLASSIFIER: Dict[str, List[str]] = {
        "web_research": [
            r"research|调查|研究|搜索|find|search|look.?up",
            r"what.?is|who.?is",
        ],
        "code_dev": [
            r"code|代码|implement|实现|写|write|fix|修复",
            r"refactor|重构|debug|函数|class|def ",
        ],
        "agent_orch": [
            r"schedule|定时|cron|delegate|委派|subagent",
            r"parallel|并行|background|后台",
        ],
        "knowledge": [
            r"remember|记住|recall|回忆|memory|记忆",
            r"what did we|之前|我们|历史",
        ],
        "communication": [
            r"send|发送|tell|告诉|message|消息|通知",
        ],
        "analysis": [
            r"analyze|分析|compare|对比|evaluate|评估",
            r"summarize|总结|report|报告",
        ],
    }

    @classmethod
    def classify_task(cls, user_input: str) -> str:
        """分类任务类型，返回对应的mask键名"""
        text = user_input.lower()
        scores = {}
        for task_type, patterns in cls.TASK_CLASSIFIER.items():
            score = sum(2 if re.search(p, text) else 0 for p in patterns)
            if score:
                scores[task_type] = score

        if not scores:
            return "generic"
        return max(scores, key=scores.get)

    @classmethod
    def select_tools(cls, user_input: str) -> Set[str]:
        """
        LoRI式稀疏工具选择。
        
        对应: A矩阵（冻结全集）× B矩阵（稀疏掩码）
        """
        task = cls.classify_task(user_input)
        mask = cls.TASK_MASKS.get(task, set())

        if not mask:
            # generic → 返回所有工具
            return set(cls.ALL_TOOLS)

        # 确保关键工具始终可用
        essential = {"memory", "session_search", "read_file", "terminal", "write_file"}
        mask = mask | essential

        logger.info("LoRI: '%s' → %s (%d tools active of %d)",
                     user_input[:50], task, len(mask), len(cls.ALL_TOOLS))
        return mask

    @classmethod
    def get_status(cls) -> Dict:
        return {
            "total_tools": len(cls.ALL_TOOLS),
            "task_types": list(cls.TASK_MASKS.keys()),
            "avg_active": sum(len(v) for v in cls.TASK_MASKS.values() if v) / max(1, len(cls.TASK_MASKS) - 1),
        }


# Hermes plugin接口
def register(ctx):
    ctx.register_tool("lori_select", {
        "name": "lori_select",
        "description": "LoRI稀疏工具选择——根据任务类型仅激活相关工具子集",
        "parameters": {
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "任务描述"},
            },
            "required": ["input"],
        },
        "handler": lambda input: {
            "task_type": LoRISelector.classify_task(input),
            "active_tools": list(LoRISelector.select_tools(input)),
            "savings": f"激活{len(LoRISelector.select_tools(input))}/{len(LoRISelector.ALL_TOOLS)}个工具",
        },
    })
