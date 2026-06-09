"""
MoR Adaptive Depth — 自适应计算深度的 context engine

基于: MoR (NeurIPS 2025) "Mixture-of-Recursions: Learning Dynamic Recursive Depths
      for Adaptive Token-Level Computation"

核心思想:
  不同复杂度的任务需要不同的"思考深度"——简单问题快速回答，复杂问题深入推理。
  MoR让每个token动态决定走多深的递归路径。Hermes Agent中，这意味着动态
  调整工具调用轮次上限和上下文保留策略。

与原始论文的映射:
  MoR                        → Hermes
  ─────────────────────────────────────────────────
  递归参数共享                → 同一组工具/skill库可递归复用
  自适应递归深度              → 动态调整 max_turns (5/15/30)
  轻量路由器(Router)          → 输入特征复杂度评分
  Expert-Choice路由          → agent自动决定是否继续思考
  Early Exit                 → 满足条件时提前结束
  KV缓存优化                 → 压缩不活跃的上下文中段

安装:
  1. 复制到 /opt/hermes/plugins/context_engine/mor/
  2. config.yaml 中设置 context.engine: mor
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# MoR复杂度评分器 — 轻量路由器
# ---------------------------------------------------------------------------

class MoRRouter:
    """
    根据输入特征估计任务复杂度的轻量路由器。
    
    返回 1(浅)/2(中)/3(深) 三个等级。
    """

    # 关键词权重
    KEYWORD_WEIGHTS = {
        # 深度关键词 (+0.3)
        "analyze": 0.3,
        "compare": 0.3,
        "investigate": 0.3,
        "research": 0.3,
        "build": 0.3,
        "develop": 0.3,
        "refactor": 0.3,
        "debug": 0.3,
        "design": 0.3,
        "evaluate": 0.3,
        # 分析方法 (+0.4)
        "pros and cons": 0.4,
        "trade-off": 0.4,
        "root cause": 0.4,
        "architecture": 0.4,
        "performance": 0.4,
        # 任务分解 (+0.5)
        "investigate.*and": 0.5,
        "compare.*and": 0.5,
    }

    # 多部分请求检测
    MULTIPART_CONJUNCTIONS = [
        "and", "then", "also", "additionally",
        "meanwhile", "furthermore", "moreover",
    ]

    # 需要工具的领域
    TOOL_HEAVY_PATTERNS = [
        r"git\s+",
        r"docker\s+",
        r"kubectl\s+",
        r"npm\s+",
        r"pip\s+",
        r"def\s+|class\s+|function\s+",
        r"import\s+",
    ]

    # 浅层关键词（降低复杂度）
    SHALLOW_PATTERNS = [
        r"what\s+is\s+",
        r"who\s+is\s+",
        r"when\s+is\s+",
        r"weather",
        r"time\s+in\s+",
        r"define\s+",
        r"meaning\s+of\s+",
        r"synonym",
    ]

    @classmethod
    def estimate_complexity(cls, user_message: str) -> int:
        """
        返回 1(浅层)/2(中层)/3(深度)
        
        复杂度 = 加权关键词 + 多部分 + 工具信号 - 浅层信号
        """
        text = user_message.lower()
        score = 0.0

        # 1. 关键词匹配
        for keyword, weight in cls.KEYWORD_WEIGHTS.items():
            if re.search(keyword, text):
                score += weight

        # 2. 多部分请求检测
        conjunction_count = sum(
            1 for conj in cls.MULTIPART_CONJUNCTIONS if conj in text
        )
        score += conjunction_count * 0.2

        # 3. 工具优化领域检测
        tool_signals = sum(
            1 for p in cls.TOOL_HEAVY_PATTERNS if re.search(p, text)
        )
        score += tool_signals * 0.15

        # 4. 浅层信号降级
        shallow_signals = sum(
            1 for p in cls.SHALLOW_PATTERNS if re.search(p, text)
        )
        score -= shallow_signals * 0.3

        # 5. 输入长度信号
        if len(user_message) > 500:
            score += 0.5
        elif len(user_message) > 200:
            score += 0.2

        # 映射到深度等级
        if score <= 0.5:
            return 1  # 浅层: 快问快答
        elif score <= 2.0:
            return 2  # 中层: 标准推理
        else:
            return 3  # 深度: 多步骤推理

    @classmethod
    def max_turns_for_depth(cls, depth: int) -> int:
        """每个深度等级对应的最大工具调用轮次"""
        return {1: 5, 2: 15, 3: 30}.get(depth, 15)

    @classmethod
    def context_keep_ratio(cls, depth: int) -> float:
        """每个深度等级对应的压缩保留率"""
        return {1: 0.15, 2: 0.40, 3: 0.65}.get(depth, 0.40)


# ---------------------------------------------------------------------------
# 提前退出检测
# ---------------------------------------------------------------------------

def should_early_exit(
    turn_count: int,
    last_assistant_content: str,
    last_tool_results: List[str],
) -> Tuple[bool, str]:
    """
    判断是否应提前退出（MoR Early Exit）.

    条件:
      1. 已收集到确凿答案（assistant直接给出了答案）
      2. 工具结果确认了最终状态（"已完成"/"已成功"等）
      3. 工具结果包含明确错误（快速失败）

    返回 (是否退出, 原因)
    """
    if turn_count <= 1:
        return False, ""

    # 条件1: assistant直接回答
    content = last_assistant_content or ""
    if re.search(
        r"^(是的|好的|完成|Done|Finished|Here'?s the|根据|Answer:)", content
    ):
        # 检查是否有下一步行动的信号
        if not re.search(r"接下来|next|further|还有|继续", content):
            return True, "assistant直接给出了答案"

    # 条件2: 工具确认完成
    for result in last_tool_results[-2:]:
        if re.search(r"已完成|已成功|successfully|exit code:?\s*0", result):
            return True, "工具确认任务完成"

    # 条件3: 致命错误
    for result in last_tool_results[-1:]:
        if re.search(r"exit code:?\s+[1-9]|Error:|Traceback", result):
            # 重试不超过3次
            return turn_count > 3, "工具返回错误（重试超过3次）"

    return False, ""


# ===========================================================================
# Hermes context_engine plugin 接口
# ===========================================================================

class MoRContextEngine:
    """
    MoR自适应计算深度的Context Engine for Hermes Agent.

    使用方法:
      在 config.yaml 中设置:
        context:
          engine: mor
          mor:
            local_window: 20
            default_depth: 2

    效果:
      - 简单问题用5轮tool call，快速回答
      - 中等问题用15轮tool call，标准推理
      - 复杂问题用30轮tool call，深入调研
      - 每轮tool call后检查是否可以提前退出
    """

    name = "mor"

    def __init__(self, context_length: int = 200000, **kwargs):
        self.context_length = context_length
        self.threshold_tokens = int(context_length * 0.50)
        self._local_window = kwargs.get("local_window", 20)
        self._default_depth = kwargs.get("default_depth", 2)
        self._thinking_depth = self._default_depth
        self._compression_count = 0
        self._last_total_tokens = 0
        self._router_history: List[int] = []

    def estimate_complexity(self, user_message: str) -> int:
        """公开给run_agent.py调用的复杂度估计接口"""
        depth = MoRRouter.estimate_complexity(user_message)
        self._thinking_depth = depth
        self._router_history.append(depth)
        return depth

    def get_max_turns(self) -> int:
        """获取当前深度对应的最大工具轮次"""
        return MoRRouter.max_turns_for_depth(self._thinking_depth)

    def should_compress(self, prompt_tokens: Optional[int] = None) -> bool:
        """
        覆盖: 深度1和2无需压缩（保留完整上下文），深度3才需要压缩。
        """
        if self._thinking_depth <= 2:
            return False
        tokens = prompt_tokens or self._last_total_tokens
        return tokens >= self.threshold_tokens

    def compress(
        self,
        messages: List[Dict],
        current_tokens: Optional[int] = None,
        **kwargs,
    ) -> List[Dict]:
        """深度感知的压缩：深度越大保留越多上下文"""
        self._last_total_tokens = current_tokens or self._last_total_tokens
        keep_ratio = MoRRouter.context_keep_ratio(self._thinking_depth)

        system_msgs = [m for m in messages if m.get("role") == "system"]
        history = [m for m in messages if m.get("role") != "system"]

        keep_count = max(1, int(len(history) * keep_ratio))
        compressed = system_msgs + history[-keep_count:]
        self._compression_count += 1

        logger.info(
            "MoR depth=%d compression #%d: kept %d/%d messages (ratio=%.0f%%)",
            self._thinking_depth,
            self._compression_count,
            len(compressed),
            len(messages),
            keep_ratio * 100,
        )
        return compressed

    def update_from_response(self, usage: Dict) -> None:
        self._last_total_tokens = usage.get("total_tokens", 0)

    def on_session_start(self, session_id: str, **kwargs) -> None:
        """每轮会话开始时重置深度"""
        self._thinking_depth = self._default_depth
        self._router_history = []

    def get_status(self) -> Dict:
        return {
            "engine": "mor",
            "current_depth": self._thinking_depth,
            "max_turns": self.get_max_turns(),
            "compressions": self._compression_count,
            "router_history": self._router_history[-10:],
        }


# ===========================================================================
# Integration Note: 在 run_agent.py 中集成 MoR
#
# 在 AIAgent.run_conversation() 中:
#
# 1. 在进入工具循环前:
#    ```python
#    if hasattr(self.context_engine, 'estimate_complexity'):
#        depth = self.context_engine.estimate_complexity(user_input)
#        max_turns = self.context_engine.get_max_turns()
#    else:
#        max_turns = DEFAULT_MAX_TURNS  # 原来的默认值
#    ```
#
# 2. 每次tool call后:
#    ```python
#    if hasattr(self.context_engine, 'should_early_exit'):
#        should_exit, reason = self.context_engine.should_early_exit(
#            turn_count, last_content, last_results
#        )
#        if should_exit:
#            logger.info("MoR early exit: %s", reason)
#            break
#    ```
# ===========================================================================
