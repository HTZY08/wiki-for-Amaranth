"""
FlyRoute — 隐式 Skill 路由插件

基于: FlyLoRA (NeurIPS 2025) 
"FlyLoRA: Boosting Task Decoupling and Parameter Efficiency via Implicit 
 Rank-Wise Mixture-of-Experts"

核心思想（果蝇嗅觉回路启发）:
  果蝇的嗅觉系统用随机投影 + 赢家通吃机制实现高效归类。
  FlyLoRA将这一机制用于LoRA的rank路由——冻结稀疏随机矩阵做投影，
  top-k选择激活，无需显式训练router参数。

Hermes映射:
  FlyLoRA                         → Hermes
  ─────────────────────────────────────────────
  冻结稀疏随机投影矩阵A           → 每个skill注册时固定一个随机签名
  top-k路由选择                   → 选最匹配的2-3个skill激活
  隐式路由（无显式router参数）    → 无需维护技能分类器/训练数据
  果蝇赢家通吃机制                → 每个请求只激活最相关的skill子集

效果:
  - 不再把所有skill描述注入prompt（O(n) token成本）
  - 改为预选top-3最相关的skill（O(1) token成本）
  - 大幅减少prompt token消耗

安装:
  1. 复制到 /opt/hermes/plugins/flyroute/
  2. config.yaml 中添加:
     tools:
       enabled_plugins: [flyroute]
     flyroute:
       top_k: 3
       projection_dim: 64
"""

import hashlib
import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# 稀疏随机投影的哈希种子（冻结，不可训练）
_FROZEN_SEED = 42


class FlyRouter:
    """
    隐式Skill路由器。
    
    每个skill注册时被分配一个固定的随机投影向量（基于skill名字的hash）。
    查询时，用户输入被投影到同一空间，通过余弦相似度选top-k。
    
    全部操作是确定性的（冻结随机种子），不需要训练数据。
    """

    def __init__(self, projection_dim: int = 64, sparsity: float = 0.1):
        """
        参数:
          projection_dim: 投影空间的维度（越大区分度越高）
          sparsity: 随机投影的稀疏度（0.1=10%非零）
        """
        self.projection_dim = projection_dim
        self.sparsity = sparsity
        self.skill_index: Dict[str, Dict] = {}
        self._frozen_projections: Dict[str, list] = {}

    def register_skill(
        self,
        name: str,
        description: str,
        tags: Optional[List[str]] = None,
        examples: Optional[List[str]] = None,
    ) -> None:
        """
        注册一个skill到路由索引。
        
        每个skill获得一个冻结的随机投影向量（基于名字hash），
        加上来自标签和示例的文本特征。
        """
        tags = tags or []
        examples = examples or []

        # 1. 冻结随机投影（果蝇式随机签名）
        seed = hash(name + "flylora_frozen") & 0xFFFFFFFF
        rng = __import__("random").Random(seed)
        proj = [0.0] * self.projection_dim
        for i in range(self.projection_dim):
            if rng.random() < self.sparsity:
                proj[i] = rng.gauss(0, 1.0 / self.sparsity ** 0.5)
        self._frozen_projections[name] = proj

        # 2. 文本特征向量（基于描述+标签+示例的词袋hash）
        text_sig = self._text_to_signature(
            f"{description} {' '.join(tags)} {' '.join(examples[:3])}"
        )

        # 3. 合并：随机投影 + 文本特征
        combined = [
            proj[i] + text_sig[i] * 0.3
            for i in range(self.projection_dim)
        ]

        self.skill_index[name] = {
            "name": name,
            "description": description[:120],
            "tags": tags,
            "signature": combined,
        }

    def _text_to_signature(self, text: str) -> List[float]:
        """将文本转换为固定维度的签名向量（hash技巧）"""
        sig = [0.0] * self.projection_dim
        words = re.findall(r"\w{3,}", text.lower())
        for word in set(words):
            h = hashlib.sha256(word.encode()).digest()
            idx = int.from_bytes(h[:2], "big") % self.projection_dim
            val = int.from_bytes(h[2:4], "big") / 65535.0
            sig[idx] += val
        # L2归一化
        norm = sum(v * v for v in sig) ** 0.5
        if norm > 0:
            sig = [v / norm for v in sig]
        return sig

    def route(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        将用户查询路由到最相关的top-k个skill。
        
        返回: [{name, description, score, tags}, ...]
        """
        if not self.skill_index:
            logger.warning("FlyRouter: 没有注册任何skill")
            return []

        query_sig = self._text_to_signature(query)

        # 计算查询与每个skill的余弦相似度
        scores = []
        for name, info in self.skill_index.items():
            sig = info["signature"]
            dot = sum(q * s for q, s in zip(query_sig, sig))
            q_norm = sum(v * v for v in query_sig) ** 0.5 or 1
            s_norm = sum(v * v for v in sig) ** 0.5 or 1
            similarity = dot / (q_norm * s_norm)
            # 加上冻结随机投影的隐式匹配（FlyLoRA核心机制）
            frozen_proj = self._frozen_projections.get(name, [0.0] * self.projection_dim)
            implicit = sum(
                q * f * (0.5 if f != 0 else 0)
                for q, f in zip(query_sig, frozen_proj)
            )
            scores.append({
                "name": name,
                "description": info["description"],
                "tags": info.get("tags", []),
                "score": similarity,
                "implicit_match": implicit,
            })

        # FlyLoRA的top-k选择
        scores.sort(key=lambda x: -(x["score"] + x["implicit_match"]))
        top = scores[:top_k]

        logger.info(
            "FlyRoute: '%s' → top-%d: %s",
            query[:60],
            top_k,
            [t["name"] for t in top],
        )
        return top

    def get_status(self) -> Dict:
        return {
            "registered_skills": len(self.skill_index),
            "projection_dim": self.projection_dim,
            "sparsity": self.sparsity,
        }


# ===========================================================================
# 预置skill注册（Hermes默认skills映射）
# ===========================================================================

_DEFAULT_SKILLS = [
    ("code-review", "代码审查与质量检查", ["code", "review", "quality"]),
    ("debugging", "问题排查与调试", ["debug", "error", "fix"]),
    ("writing", "文档与文本写作", ["write", "doc", "readme"]),
    ("research", "网络调研与信息收集", ["research", "search", "find"]),
    ("data-analysis", "数据分析与可视化", ["data", "analysis", "chart"]),
    ("devops", "部署与运维操作", ["deploy", "docker", "ci"]),
    ("planning", "任务规划与分解", ["plan", "organize", "breakdown"]),
    ("architecture", "系统架构设计", ["architecture", "design", "structure"]),
]

def create_default_router() -> FlyRouter:
    """创建并初始化带默认skills的router"""
    router = FlyRouter()
    for name, desc, tags in _DEFAULT_SKILLS:
        router.register_skill(name, desc, tags)
    return router


# ===========================================================================
# Hermes plugin 接口
# ===========================================================================

_router: Optional[FlyRouter] = None


def register(ctx):
    """向Hermes注册FlyRoute工具"""
    global _router
    _router = create_default_router()

    ctx.register_tool("flyroute_select", {
        "name": "flyroute_select",
        "description": "隐式skill路由选择——根据用户输入自动匹配最相关的skill。"
                       "基于FlyLoRA(NeurIPS'25)的果蝇嗅觉回路启发路由机制",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "用户查询或任务描述"},
                "top_k": {"type": "integer", "description": "返回前N个最匹配的skill", "default": 3},
            },
            "required": ["query"],
        },
        "handler": lambda query, top_k=3: _router.route(query, top_k),
    })


def get_router() -> FlyRouter:
    global _router
    if _router is None:
        _router = create_default_router()
    return _router
