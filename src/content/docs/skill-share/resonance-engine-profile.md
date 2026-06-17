---
title: Resonance Engine Profile
description: 基于共现矩阵的 skill/记忆/行为自组织发现引擎
---

# 🔮 共振引擎

不靠文本搜索、不靠 LLM 路由——一起用的 skill 在空间中靠近，下次自动出现。

## 一句话

从 session 日志中提取 skill 共现模式，构建稀疏转移矩阵，PageRank 风格迭代给出当前上下文最可能需要的 skill 列表。

## 解决的问题

Agent 技能超过 100 个后，扁平文本搜索开始失效——"计算化学"和"材料表征"的描述高度重叠但使用场景截然不同。共振引擎不读描述，读使用模式。

## 架构

```
Session 日志 → cooc.db（共现库） → Transition Matrix（hub-penalty + L1）
                                        ↓
                                 matrix.npz + registry.pkl
                                        ↓
                               ResonanceEngine.compute(v₀)
                               （<10ms，50次迭代）
                                        ↓
                               Context Assembler → Prompt
```

### 三平面

| 平面 | 节点来源 |
|------|----------|
| **Skill** | agent skill 注册表 |
| **Memory** | hindsight.db 记忆节点 |
| **Soul** | SOUL.md 行为规则 |

跨平面边以 γ=0.5 折扣处理，平面内路由优先。

## 核心算法

### 共振计算
```
v_{t+1} = α · M · v_t + (1-α) · v₀
```
- `M`：CSR 稀疏转移矩阵
- `v₀`：初始激活向量（任务嵌入或关键词匹配）
- `α`：阻尼因子（默认 0.85）
- 不收敛时回退到稀疏线性求解器

### 防坍缩
纯 Hebbian 会让通用 skill 拉拢所有簇。修复：
```
W'_ij = W_raw_ij / log(1 + f_j)
```
`f_j` = 目标节点 j 的全局调用频率。IDF 式抑制。

### 冷启动
使用数据积累前，从 `related_skills`（权重 1.0）和共享 `domain_tags`（每标签 0.2）预填充矩阵。

### v₀ 两条路径
1. **嵌入计算**：cosine 相似度（<2ms）
2. **关键词回退**：TF-IDF 风格匹配（<5ms）

## 性能实测

| 操作 | 目标 | 实测 |
|------|------|------|
| 矩阵构建 (N=500, 5%) | <100ms | ~36ms |
| 共振计算 | <10ms | ~1ms |
| Precision@5 | >0.35 | 0.912 |

## 文件结构

```
resonance-engine/
├── README.md
├── .gitignore
├── resonance_cron.py          # Cron 流水线：监控 + 重建
├── resonance_viz.py           # UMAP 可视化
└── resonance/
    ├── config.py               # 路径配置（环境变量）
    ├── node_registry.py        # 节点注册表
    ├── anti_collapse.py        # Hub-penalty + 归一化
    ├── matrix_engine.py        # CSR 矩阵 + 共振计算
    ├── embeddings.py           # 嵌入存储 + v₀ 初始化
    ├── cold_start.py           # 冷启动预填充
    ├── temporal.py             # 时间衰减 + 动量
    ├── context_assembler.py    # 阈值 → top-K → prompt
    ├── cross_plane.py          # 跨平面边（memory/soul）
    └── eval/
        ├── eval_resonance.py   # Precision@K 评估
        └── eval_clustering.py  # 聚类质量评估
```

## 使用

```bash
# 构建矩阵
python resonance_cron.py

# 查询
python3 -c "
from resonance import ResonanceEngine
engine = ResonanceEngine.load('matrix/matrix.npz', 'matrix/registry.pkl')
result = engine.compute(v0)
print(result.top_skills[:5])
"
```

## 依赖

- Python 3.10+
- numpy, scipy
- 可选：umap-learn, plotly（可视化）
- 可选：sentence-transformers（嵌入 v₀）

## License

CC BY-NC-SA 4.0
