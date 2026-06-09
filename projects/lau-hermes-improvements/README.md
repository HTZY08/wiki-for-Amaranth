# Lau博士云组会 → Hermes Agent 实现方案

从Lau博士15篇论文中筛选的3个P0级落地项，全部可直接集成到Hermes Agent中。

## 项目结构

```
lau-hermes-improvements/
├── README.md                          # 本文件
├── SPEC.md                            # 详细Spec（集成指南+代码补丁）
├── plugins/
│   ├── sepllm_compressor.py           # SepLLM压缩器(ICML'25)
│   ├── mor_context_engine.py          # MoR自适应深度(NeurIPS'25)
│   └── multiverse_mapreduce.py        # Multiverse MapReduce(NeurIPS'25)
├── skills/
│   └── multiverse-mapreduce/
│       └── SKILL.md                   # MapReduce skill描述
└── patches/
    ├── 01-sepllm-integration.md       # SepLLM集成补丁说明
    ├── 02-mor-integration.md          # MoR集成补丁说明
    └── 03-multiverse-integration.md   # Multiverse集成补丁说明
```

## 三项实现速览

| # | 论文 | 会议 | 实现 | 核心创新 | 预期收益 |
|---|------|------|------|---------|---------|
| 1 | **SepLLM** | ICML'25 | `plugins/sepllm_compressor.py` | 分隔符感知的段落压缩，无需LLM调用 | 15-30% token节省 |
| 2 | **MoR** | NeurIPS'25 | `plugins/mor_context_engine.py` | 自适应计算深度(5/15/30轮)，减少40%+工具调用 |
| 3 | **Multiverse** | NeurIPS'25 | `plugins/...` + `skills/...` | MapReduce并行分解→归并 | 复杂任务2x加速 |

## 实现思路

### 1. SepLLM 压缩器

**核心思想**: 自然语言中的分隔符（句号、换行、分段符）天然是信息压缩点。
论文发现LLM对分隔符token的注意力分数异常高——分隔符在充当段落摘要。

**落地方式**: context_engine plugin，非侵入式替换。
- 规则驱动（无LLM调用，零token成本）
- 四类缓存: Initial/Separator/Past/Local
- 长段替换为摘要标记（含工具名和主题词）

### 2. MoR 自适应深度

**核心思想**: 不同复杂度的任务需要不同的"思考深度"。

**落地方式**: context_engine plugin + run_agent.py补丁
- 复杂度路由器：基于输入特征（关键词、长度、工具信号）评分
- 三级深度: 浅层(5轮)/中层(15轮)/深度(30轮)
- 提前退出：收集到确凿答案即终止

### 3. Multiverse MapReduce

**核心思想**: MapReduce三阶段范式——分解→并行执行→合并。

**落地方式**: plugin + skill
- 自动分解：识别并列/对比/多角度/遍历模式
- 并行子任务：复用delegate_task的tasks参数
- 归并合成：结构化合并多个子结果

## 论文对照表

### 可落地（3篇P0 + 4篇参考）

| 论文 | 落地优先级 | 文件 | 状态 |
|------|-----------|------|------|
| SepLLM (ICML'25) | P0 | `plugins/sepllm_compressor.py` | ✅ 完成 |
| MoR (NeurIPS'25) | P0 | `plugins/mor_context_engine.py` | ✅ 完成 |
| Multiverse (NeurIPS'25) | P0 | `plugins/...` + `skills/...` | ✅ 完成 |
| FlyLoRA (NeurIPS'25) | P1 | 待开发 | 📋 规划 |
| AttnRes (Kimi) | P2 | 待开发 | 📋 规划 |
| MUDDFormer (ICML'25) | P2 | 待开发 | 📋 规划 |
| 分形生成 (TMLR'25) | P3 | 待开发 | 📋 规划 |
| LoRI (COLM'25) | P3 | 待开发 | 📋 规划 |

### 不可落地（7篇）

CTM / OverLoCK / vHeat / RAEv2 / NoProp / DiC / MeanFlow
→ 模型架构/训练/视觉方向，Agent框架层无法触及。

## 完整知识库

详见 `/opt/data/vault/研究/Lau博士云组会/` 下的15篇论文结构化笔记。
