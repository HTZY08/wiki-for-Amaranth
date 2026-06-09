"""
AttnRes Memory — 注意力加权记忆检索

基于: Attention Residuals (Kimi/Moonshot AI, 2026)
arXiv: https://arxiv.org/abs/2603.15031
代码: https://github.com/MoonshotAI/Attention-Residuals

核心思想:
  残差连接用固定权重(1.0)累加所有前层，导致深层信号被稀释（PreNorm稀释）。
  AttnRes将固定加法替换为跨层注意力——每层有一个可学习的伪查询向量，
  通过softmax从所有前层加权聚合。

  在Hermes中，这映射为：
    不是简单拼接所有记忆片段（残差式），
    而是对记忆池计算注意力权重，仅选择最相关的片段。

与原始论文的映射:
  AttnRes                      → Hermes
  ─────────────────────────────────────────────
  伪查询向量(pseudo-query)     → 当前用户查询的embedding
  前层输出(key/value)          → 历史记忆片段
  softmax注意力权重            → TF-IDF/关键词重叠权重
  Block AttnRes（块级）        → 按时间分块，块内加权摘要
  预训练时query初始化=0        → 默认保留最近N条（behavior cloning）

安装:
  1. 复制到 /opt/hermes/plugins/context_engine/attnres/
  2. config.yaml 中设置 context.engine: attnres
"""

import logging
import math
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class AttentiveMemoryRetriever:
    """
    注意力加权记忆检索器。
    
    不是简单拼接所有历史消息，而是：
    1. 将消息序列按时间分块（Block AttnRes）
    2. 计算当前查询与每个块的注意力权重
    3. 仅选择权重最高的块
    4. 块内用权重再分配token预算
    """

    def __init__(
        self,
        block_size: int = 8,
        temperature: float = 0.5,
        top_k_blocks: int = 3,
    ):
        """
        参数:
          block_size: 每个块包含的消息数（AttnRes的"块"）
          temperature: softmax温度（越低越尖锐，越高越平滑）
          top_k_blocks: 保留的top-k个块
        """
        self.block_size = block_size
        self.temperature = temperature
        self.top_k_blocks = top_k_blocks

    def compute_attention(
        self,
        query: str,
        candidates: List[Tuple[str, Any]],
    ) -> List[Tuple[int, float]]:
        """
        计算查询与候选记忆之间的注意力权重。
        
        返回: [(index, attention_score), ...]
        """
        if not candidates:
            return []

        query_terms = self._tokenize(query)
        query_counter = Counter(query_terms)

        scores = []
        for i, (text, _) in enumerate(candidates):
            terms = self._tokenize(text)
            counter = Counter(terms)
            # TF-IDF风格的注意力权重
            overlap = sum(
                min(query_counter.get(t, 0) * 2, counter.get(t, 0))
                for t in set(query_terms)
            )
            # 长度归一化
            denom = math.log(len(terms) + 1) + 1
            score = overlap / denom
            scores.append((i, score))

        if not scores:
            return scores

        # Softmax归一化
        max_score = max(s for _, s in scores)
        if max_score <= 0:
            return [(i, 1.0 / len(scores)) for i, _ in scores]

        exp_scores = [
            (i, math.exp((s - max_score) / self.temperature))
            for i, s in scores
        ]
        total = sum(s for _, s in exp_scores)
        if total > 0:
            exp_scores = [(i, s / total) for i, s in exp_scores]

        return exp_scores

    def retrieve_weighted(
        self,
        messages: List[Dict],
        query: Optional[str] = None,
        *,
        system_count: int = 2,
        tail_count: int = 5,
    ) -> List[Dict]:
        """
        加权检索：保留系统提示 + 注意力选中的块 + 尾部。

        参数:
          messages: 完整消息列表
          query: 当前用户查询（用于注意力权重计算）
          system_count: 开头保留的系统消息数
          tail_count: 末尾保留的最新消息数

        返回:
          压缩后的消息列表
        """
        if not messages:
            return messages

        # 分离系统消息、中间部分和尾部
        system_msgs = messages[:system_count]
        tail_msgs = messages[-tail_count:] if len(messages) > system_count + tail_count else []
        middle = messages[system_count:-tail_count] if tail_msgs else messages[system_count:]

        if not middle or len(middle) <= self.block_size:
            return messages

        # 将中间部分按时间分块（Block AttnRes）
        blocks = [
            middle[i:i + self.block_size]
            for i in range(0, len(middle), self.block_size)
        ]

        # 为每个块计算注意力分数
        query_text = query or (messages[-1].get("content", "") if messages else "")
        block_reprs = [
            (" ".join(m.get("content", "") or "" for m in block)[:500], block)
            for block in blocks
        ]
        attention = self.compute_attention(query_text, block_reprs)

        # 选择top-k块
        block_indices = [i for i, _ in sorted(attention, key=lambda x: -x[1])]
        selected_indices = set(block_indices[:self.top_k_blocks])

        # 构建结果：系统 + 选中块 + 尾部
        compressed = list(system_msgs)
        for i, block in enumerate(blocks):
            if i in selected_indices:
                compressed.extend(block)

        compressed.extend(tail_msgs)

        logger.info(
            "AttnRes: %d blocks → selected %d (attention-top), kept %d/%d messages",
            len(blocks),
            len(selected_indices),
            len(compressed),
            len(messages),
        )
        return compressed

    def _tokenize(self, text: str) -> List[str]:
        """分词（支持中英文混排）"""
        # 中文词（2-4字）
        chinese = re.findall(r"[\u4e00-\u9fff]{2,4}", text)
        # 英文词（3+字母）
        english = re.findall(r"[a-zA-Z]{3,}", text.lower())
        # 数字
        numbers = re.findall(r"\d+", text)
        return chinese + english + numbers

    @staticmethod
    def format_weighted_results(
        results: List[Tuple[str, float]],
        max_total_chars: int = 8000,
    ) -> str:
        """将加权结果格式化为带权重的文本"""
        if not results:
            return ""

        parts = []
        budget = max_total_chars
        for text, weight in results:
            # 根据权重分配字符预算
            alloc = int(budget * weight)
            alloc = max(alloc, 200)  # 每个片段至少200字
            alloc = min(alloc, len(text))
            if alloc < len(text):
                text = text[:alloc] + f"\n[... +{len(text) - alloc} chars]"
            parts.append(f"[relevance: {weight:.2f}]\n{text}")
            budget -= alloc

        return "\n\n".join(parts)


# ===========================================================================
# Hermes context_engine plugin 接口
# ===========================================================================

class AttnResContextEngine:
    """
    AttnRes注意力加权记忆Context Engine for Hermes Agent.

    使用方法:
      在 config.yaml 中设置:
        context:
          engine: attnres
          attnres:
            block_size: 8
            temperature: 0.5
            top_k_blocks: 3
    """

    name = "attnres"

    def __init__(self, context_length: int = 200000, **kwargs):
        self.context_length = context_length
        self.threshold_tokens = int(context_length * 0.50)
        self._last_total_tokens = 0
        self._compression_count = 0
        self._last_query = ""
        self.retriever = AttentiveMemoryRetriever(
            block_size=kwargs.get("block_size", 8),
            temperature=kwargs.get("temperature", 0.5),
            top_k_blocks=kwargs.get("top_k_blocks", 3),
        )

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
        result = self.retriever.retrieve_weighted(
            messages,
            query=self._last_query,
        )
        self._compression_count += 1
        return result

    def update_from_response(self, usage: Dict) -> None:
        self._last_total_tokens = usage.get("total_tokens", 0)
        # 记录最新用户查询
        self._last_query = usage.get("last_user_message", self._last_query)

    def get_status(self) -> Dict:
        return {
            "engine": "attnres",
            "compressions": self._compression_count,
            "block_size": self.retriever.block_size,
            "temperature": self.retriever.temperature,
            "top_k_blocks": self.retriever.top_k_blocks,
        }
