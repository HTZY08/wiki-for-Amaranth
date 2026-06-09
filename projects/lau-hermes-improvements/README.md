# Lau博士云组会 → Hermes Agent 实现方案

从Lau博士15篇论文中筛选出的**8个可落地实现**（3×P0 + 3×P2 + 2×P3），
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
│   ├── attnres_memory.py         # P1: AttnRes记忆检索 (Kimi'26)
│   ├── mudd_orchestrator.py      # P2: MUDDFormer多路编排 (ICML'25)
│   └── lori_selector.py          # P3: LoRI稀疏工具选择 (COLM'25)
├── skills/
│   ├── multiverse-mapreduce/SKILL.md
│   └── fractal-recursive/SKILL.md
└── patches/
    ├── 01-sepllm-integration.md
    ├── 02-mor-integration.md
    ├── 03-multiverse-integration.md
    ├── 04-flyroute-integration.md
    ├── 05-attnres-integration.md
    ├── 06-mudd-integration.md
    ├── 07-fractal-integration.md
    └── 08-lori-integration.md
```

## 全部8项实现

| 优先级 | 论文 | 会议 | 文件 | 核心创新 |
|--------|------|------|------|---------|
| **P0** | SepLLM | ICML'25 | `sepllm_compressor.py` | 分隔符感知压缩，零LLM调用 |
| **P0** | MoR | NeurIPS'25 | `mor_context_engine.py` | 自适应深度5/15/30轮 |
| **P0** | Multiverse | NeurIPS'25 | `multiverse_mapreduce.py` + skill | MapReduce并行分解归并 |
| **P1** | FlyLoRA | NeurIPS'25 | `flyroute_router.py` | 冻结随机投影隐式路由 |
| **P1** | AttnRes | Kimi'26 | `attnres_memory.py` | 注意力加权块级记忆检索 |
| **P2** | MUDDFormer | ICML'25 | `mudd_orchestrator.py` | 四路动态任务编排 |
| **P3** | 分形生成 | TMLR'25 | `fractal-recursive/SKILL.md` | 递归原子模块组合 |
| **P3** | LoRI | COLM'25 | `lori_selector.py` | 稀疏工具选择(90%省) |

## 全部15篇论文对照

### 可落地（8篇）
- ✅ P0: SepLLM, MoR, Multiverse
- ✅ P1: FlyLoRA, AttnRes
- ✅ P2-P3: MUDDFormer, 分形生成, LoRI

### 不可落地（7篇）
- CTM, OverLoCK, vHeat, RAEv2, NoProp, DiC, MeanFlow
→ 模型架构/训练/视觉方向，Agent框架层无法触及。
