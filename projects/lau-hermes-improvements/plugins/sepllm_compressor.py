"""
SepLLM Compressor — 分隔符感知的上下文压缩器

基于: SepLLM (ICML 2025) "Accelerate LLMs by Compressing One Segment into One Separator"

核心思想:
  自然语言中的分隔符（句号、换行、分段符）天然是信息压缩点。
  段落信息可以被压缩到分隔符token中，无需有损摘要。

Hermes集成方式:
  作为 context_engine plugin，替换默认的 ContextCompressor。
  在LLM做有损摘要之前，先做SepLLM式规则驱动的段落压缩。

与原始论文的映射:
  SepLLM             → Hermes
  ─────────────────────────────────────────────
  分隔符token        → 对话中的主题切换点/任务边界
  段落压缩            → 已完成子任务的对话压缩为摘要
  稀疏注意力(Initial) → 系统提示 + 首轮对话永远保留
  稀疏注意力(Separator) → 保留所有工具调用/结果边界标记
  稀疏注意力(Neighbor) → 最近的N条消息保留完整
  流式缓存管理        → 四块缓存: Initial / Separator / Past / Local

安装:
  1. 复制到 /opt/hermes/plugins/context_engine/sepllm/
  2. config.yaml 中设置 context.engine: sepllm
"""

import re
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 分隔符模式 — 对话中的"自然分隔符"
# ---------------------------------------------------------------------------
SEPARATOR_PATTERNS = [
    # 工具调用边界
    r"<tool_call>",
    r"</tool_call>",
    r'{\s*"function":',
    # 明确的主题切换标记
    r"^#{2,3}\s+",         # Markdown 标题
    r"^---+\s*$",          # 水平分隔线
    r"^==+\s*$",
    # 对话中的元指令
    r"接下来",
    r"另外",
    r"其次",
    r"然后",
    r"Now let'?s",
    r"Next,",
    r"Finally,",
    r"SUMMARY:",
    r"RESULT:",
    r"CONCLUSION:",
    r"Active Task",
    r"Remaining Work",
    r"Resolved",
    # 自然语言段落分隔
    r"[.?!]\s+[A-Z\"'(（「『\u4e00-\u9fff]",
]

# 编译所有分隔符模式
_COMPILED_SEPARATORS = [re.compile(p, re.MULTILINE) for p in SEPARATOR_PATTERNS]


def _find_separator_positions(text: str) -> List[int]:
    """返回文本中所有分隔符位置的列表（按出现顺序）"""
    positions = set()
    for pattern in _COMPILED_SEPARATORS:
        for match in pattern.finditer(text):
            # 记录分隔符之后的第一个字符位置（作为段落起点）
            pos = match.end()
            if pos < len(text):
                positions.add(pos)
    return sorted(positions)


def _compress_code_block(full_block: str, lang: str) -> str:
    """压缩长代码块：保留语言标记 + 首尾各两行"""
    lines = full_block.split("\n")
    if len(lines) <= 8:
        return full_block
    compressed_lines = len(lines) - 4
    return (
        "\n".join(lines[:3])
        + f"\n  ... [{compressed_lines} lines compressed by SepLLM] ...\n"
        + "\n".join(lines[-2:])
    )


def _compress_tool_output(content: str, max_head: int = 300, max_tail: int = 100) -> str:
    """压缩工具输出：保留头部+尾部"""
    if len(content) <= max_head + max_tail + 50:
        return content
    return (
        content[:max_head]
        + f"\n[SepLLM: {len(content) - max_head - max_tail} chars compressed]\n"
        + content[-max_tail:]
    )


def _compress_list_items(list_text: str) -> str:
    """压缩长列表：保留前2项+后2项"""
    items = [
        line
        for line in list_text.split("\n")
        if line.strip().startswith(("- ", "* ", "1. "))
    ]
    if len(items) <= 4:
        return list_text
    return (
        "\n".join(items[:2])
        + f"\n[+ {len(items) - 4} more items — SepLLM compressed]\n"
        + "\n".join(items[-2:])
    )


class SepLLMCompressor:
    """
    规则驱动的对话压缩器，无需LLM调用。

    四类缓存（对应SepLLM的稀疏注意力掩码）:
      1. Initial — 系统提示 + 首轮对话（永远保留）
      2. Separator — 所有主题/任务边界标记（保留）
      3. Past Window — 历史滑动窗口（可压缩）
      4. Local Window — 最近的N条消息（保留完整）
    """

    def __init__(self, local_window: int = 20, min_segment_len: int = 100):
        self.local_window = local_window
        self.min_segment_len = min_segment_len
        self._stats = {
            "compressed_segments": 0,
            "original_chars": 0,
            "saved_chars": 0,
        }

    def compress_content(self, text: str) -> str:
        """对单条消息内容做SepLLM式压缩"""
        if len(text) < self.min_segment_len:
            return text

        original_len = len(text)
        text = self._apply_sepllm(text)
        saved = original_len - len(text)
        self._stats["compressed_segments"] += 1
        self._stats["original_chars"] += original_len
        self._stats["saved_chars"] += saved
        return text

    def _apply_sepllm(self, text: str) -> str:
        """应用SepLLM压缩策略"""
        # 1. 压缩长代码块
        text = re.sub(
            r"```(\w*)\n[\s\S]*?\n```",
            lambda m: _compress_code_block(m.group(0), m.group(1)),
            text,
        )
        # 2. 压缩JSON工具输出
        text = re.sub(
            r'(\{\s*\n)([\s\S]{1000,}?)(\n\s*\})',
            lambda m: m.group(1)
            + _compress_tool_output(m.group(2))
            + m.group(3),
            text,
        )
        # 3. 压缩长列表
        text = re.sub(
            r"((?:^|\n)(?:[-*]\s.*(?:\n|$)){8,})",
            lambda m: _compress_list_items(m.group(0)),
            text,
        )
        return text

    def segment_messages(self, messages: List[Dict]) -> List[List[Dict]]:
        """根据分隔符将消息序列分段"""
        segments: List[List[Dict]] = []
        current: List[Dict] = []

        for msg in messages:
            content = str(msg.get("content", "") or "")
            is_separator = any(p.search(content) for p in _COMPILED_SEPARATORS)
            if is_separator and current:
                segments.append(current)
                current = [msg]
            else:
                current.append(msg)

        if current:
            segments.append(current)
        return segments

    def compress_messages(
        self,
        messages: List[Dict],
        *,
        initial_count: int = 3,
        local_window: Optional[int] = None,
    ) -> List[Dict]:
        """
        压缩消息列表。

        参数:
          messages: 原始消息列表
          initial_count: 开头保留的条数（系统提示+首轮）
          local_window: 末尾保留的条数（最近的对话）
        """
        window = local_window or self.local_window

        if len(messages) <= initial_count + window:
            # 消息太少，不需要压缩
            return messages

        # 分解为三部分
        initial = messages[:initial_count]
        middle = messages[initial_count:-window]
        tail = messages[-window:]

        # 将middle按分隔符分段
        segments = self.segment_messages(middle)

        compressed_middle = []
        for seg in segments:
            if len(seg) <= 2:
                # 短段保留
                for m in seg:
                    # 但压缩单条消息内容
                    if isinstance(m, dict) and "content" in m:
                        mc = dict(m)
                        mc["content"] = self.compress_content(
                            str(mc.get("content", "") or "")
                        )
                        compressed_middle.append(mc)
                    else:
                        compressed_middle.append(m)
            else:
                # 长段 → 替换为摘要标记
                seg_summary = self._summarize_segment(seg)
                compressed_middle.append({
                    "role": "assistant",
                    "content": f"[SepLLM压缩段] {seg_summary}",
                })

        return initial + compressed_middle + tail

    def _summarize_segment(self, segment: List[Dict]) -> str:
        """为一段对话生成简短摘要（规则驱动）"""
        tools_used = set()
        topics = set()
        for msg in segment:
            role = msg.get("role", "")
            content = str(msg.get("content", "") or "")
            if role == "assistant" and "tool_calls" in msg:
                for tc in msg.get("tool_calls", []):
                    fn = tc.get("function", {})
                    tools_used.add(fn.get("name", "unknown"))
            # 提取关键名词作为主题
            nouns = re.findall(r"[A-Z]\w+|[a-z]{4,}", content[:200])
            topics.update(nouns[:5])
        tools_str = ", ".join(sorted(tools_used)[:5]) if tools_used else "对话"
        topic_str = ", ".join(list(topics)[:3]) if topics else ""
        return f"[{len(segment)}条消息 | 工具: {tools_str} | 主题: {topic_str}]"

    def get_stats(self) -> Dict:
        return dict(self._stats)

    def reset_stats(self) -> None:
        self._stats = {
            "compressed_segments": 0,
            "original_chars": 0,
            "saved_chars": 0,
        }


# ===========================================================================
# Hermes context_engine plugin 接口
# ===========================================================================

class SepLLMContextEngine:
    """
    SepLLM Context Engine for Hermes Agent.

    使用方法:
      在 config.yaml 中设置:
        context:
          engine: sepllm
          sepllm:
            local_window: 20
            min_segment_len: 100
    """

    name = "sepllm"

    def __init__(self, context_length: int = 200000, **kwargs):
        self.context_length = context_length
        self.threshold_tokens = int(context_length * 0.50)
        self.compressor = SepLLMCompressor(
            local_window=kwargs.get("local_window", 20),
            min_segment_len=kwargs.get("min_segment_len", 100),
        )
        self._last_total_tokens = 0
        self._compression_count = 0

    def should_compress(self, prompt_tokens: Optional[int] = None) -> bool:
        tokens = prompt_tokens or self._last_total_tokens
        return tokens >= self.threshold_tokens

    def compress(
        self,
        messages: List[Dict],
        current_tokens: Optional[int] = None,
        **kwargs,
    ) -> List[Dict]:
        self._last_total_tokens = current_tokens or self._last_total_tokens
        result = self.compressor.compress_messages(messages)
        self._compression_count += 1
        logger.info(
            "SepLLM compression #%d: saved %d chars, %d segments compressed",
            self._compression_count,
            self.compressor.get_stats().get("saved_chars", 0),
            self.compressor.get_stats().get("compressed_segments", 0),
        )
        return result

    def update_from_response(self, usage: Dict) -> None:
        self._last_total_tokens = usage.get("total_tokens", 0)

    def get_status(self) -> Dict:
        return {
            "engine": "sepllm",
            "compressions": self._compression_count,
            "stats": self.compressor.get_stats(),
        }


# ===========================================================================
# Integration Note: Patch for agent/context_compressor.py
#
# To use SepLLM BEFORE the LLM summarization in the existing compressor,
# add these ~10 lines to ContextCompressor.compress() method:
#
#   # === SepLLM pre-compression (before LLM summarization) ===
#   from plugins.sepllm_compressor import SepLLMCompressor
#   _sepllm = getattr(self, '_sepllm_compressor', None)
#   if _sepllm is None:
#       _sepllm = SepLLMCompressor()
#       self._sepllm_compressor = _sepllm
#   messages = _sepllm.compress_messages(messages)
#   # === End SepLLM ===
# ===========================================================================
