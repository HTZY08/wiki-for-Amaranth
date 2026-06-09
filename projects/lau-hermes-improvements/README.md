# Lau博士云组会 → Hermes Agent 实现方案

从Lau博士15篇论文中筛选出的5个可落地实现（3×P0 + 2×P1），
全部可直接集成到Hermes Agent中。

## 项目结构

```
lau-hermes-improvements/
├── README.md
├── SPEC.md
├── plugins/
│   ├── sepllm_compressor.py      # P0: SepLLM压缩器 (ICML'25)
│   ├── mor_context_engine.py     # P0: MoR自适应深度 (NeurIPS'25)
│   ├── multiverse_mapreduce.py   # P0: Multiverse MapReduce (NeurIPS'25)
│   ├── flyroute_router.py        # P1: FlyLoRA隐式skill路由 (NeurIPS'25)
│   └── attnres_memory.py         # P1: AttnRes记忆检索 (Kimi'26)
├── skills/
│   └── multiverse-mapreduce/
│       └── SKILL.md
└── patches/
    ├── 01-sepllm-integration.md
    ├── 02-mor-integration.md
    ├── 03-multiverse-integration.md
    ├── 04-flyroute-integration.md
    └── 05-attnres-integration.md
```

## 五项实现速览

| # | 论文 | 会议 | 实现 | 核心创新 | 预期收益 |
|---|------|------|------|---------|---------|
| P0 | **SepLLM** | ICML'25 | `sepllm_compressor.py` | 分隔符感知段落压缩，零LLM调用 | 15-30% token节省 |
| P0 | **MoR** | NeurIPS'25 | `mor_context_engine.py` | 自适应计算深度5/15/30轮 | 40%+工具调用减少 |
| P0 | **Multiverse** | NeurIPS'25 | `multiverse_mapreduce.py` | MapReduce并行分解→归并 | 复杂任务2x加速 |
| P1 | **FlyLoRA** | NeurIPS'25 | `flyroute_router.py` | 冻结随机投影隐式skill路由 | skill选择O(1) |
| P1 | **AttnRes** | Kimi'26 | `attnres_memory.py` | 注意力加权记忆检索 | 更精准的上下文保留 |

## 论文对照表

### P0 — 可直接落地

| 论文 | 落地形态 | 工作量 | 状态 |
|------|---------|--------|------|
| SepLLM (ICML'25) | context_engine plugin | 中 | ✅ |
| MoR (NeurIPS'25) | context_engine plugin + run_agent.py补丁 | 中 | ✅ |
| Multiverse (NeurIPS'25) | skill + plugin | 中 | ✅ |

### P1 — 可直接落地

| 论文 | 落地形态 | 工作量 | 状态 |
|------|---------|--------|------|
| FlyLoRA (NeurIPS'25) | skill路由plugin | 低 | ✅ |
| AttnRes (Kimi) | context_engine plugin | 中 | ✅ |

### P2-P3 — 待续

| 论文 | 落地形态 | 优先级 | 状态 |
|------|---------|--------|------|
| MUDDFormer (ICML'25) | 多路workflow编排 | P2 | 📋 |
| 分形生成 (TMLR'25) | 递归skill组合 | P3 | 📋 |
| LoRI (COLM'25) | 稀疏工具选择 | P3 | 📋 |
| OverLoCK (CVPR'25) | Kanban多级调度 | P3 | 📋 |

### 不可落地（7篇）

CTM / vHeat / RAEv2 / NoProp / DiC / MeanFlow
→ 模型架构/训练/视觉方向，Agent框架层无法触及。

## 完整知识库

详见 `/opt/data/vault/研究/Lau博士云组会/` 下的15篇论文结构化笔记。
