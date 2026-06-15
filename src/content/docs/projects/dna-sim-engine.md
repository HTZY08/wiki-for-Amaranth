---
title: "DNA Sim Engine — 架构说明"
description: "2026-06-15 重构后架构, 含全流程CLI、多链平衡求解器、587篇文献验证"
---

# DNA Sim Engine 架构

## 快速入口

```bash
cd /opt/data/dna-sim-engine
.venv/bin/python bin/dna-designer <command> [args]
```

## 核心命令

| 命令 | 功能 |
|------|------|
| `analyze <SEQ>` | 序列特征分析: GC/Tm/发卡/PAM/方法推荐 |
| `complex --demo` | 多链平衡分析 (NUPACK complex模式) |
| `design <SEQ>` | 体系感知的方案设计 (引物/crRNA/探针) |
| `simulate [--system DETECTR]` | 动力学模拟 |
| `full <SEQ>` | 全流程一键出报告 |
| `primers` | 引物设计 (进化算法) |
| `optimize` | 参数优化 (NSGA-II) |

## 10 体系

DETECTR / SHERLOCK / LAMP-only / LAMP-Cas12a / RT-LAMP / RT-LAMP-Cas12a / RCA-Cas12a / Cas12a-only / Cas12b-DETECTR / DNAzyme

## 工程状态

| 模块 | 行数 | 状态 |
|------|------|------|
| CLI (src/cli/) | ~500 | ✅ |
| 模型 (src/models/) | ~976 | ✅ 已校准 |
| 引擎 (src/engine/) | ~1200 | ✅ |
| 设计 (src/design/) | ~2000 | 🟡 |
| 分析 (src/analysis/) | ~2000 | ✅ |
| 报告 (src/reporting/) | ~200 | ✅ |
| 文献 | 587篇 | ✅ 超标 |
| 验证矩阵 | 5体系 | 🟡 持续迭代 |

## 关键文件

- `src/models/modular_system.py` — 核心 (976行, 10体系+4校正层)
- `src/analysis/complex_analysis.py` — 多链平衡求解器 (替代NUPACK)
- `src/analysis/sequence_analyzer.py` — 序列分析+推荐引擎
- `src/design/protocol_generator.py` — 体系感知方案生成
- `data/literature/_all_papers.json` — 587篇PubMed文献
- `data/validation_matrix.json` — 验证矩阵

## 校准状态

- DETECTR: ✅ 偏差0.7x
- SHERLOCK: ⚠️ 偏差0.2x (需T7耦合修复)
- LAMP-Cas12a: ❌ (55°C Bst活性25%)
- RCA-Cas12a: ⚠️ (产物可及性0.02)
- DNAzyme: ❌ (需别构激活模型)
