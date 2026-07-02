---
title: Strata — Agent 记忆地层引擎
description: 把混沌的对话历史变成可挖掘的地层结构
---

**Strata** 是一个轻量的 Agent 记忆分析框架。它把你的对话历史（session）自动聚类成簇，为每个簇积累经验笔记，追踪错误模式，监控注意力漂移——全部在本地运行，零 API 成本。

## 核心理念

对话历史不是噪声，是地层。每一次会话都是一次沉积，Strata 把它挖开、分层、标记，让你看到：

- 你在什么话题上花了最多时间（簇分布）
- 每个话题里你踩过什么坑（错误共振）
- 你的注意力在往哪漂移（月报）

## 架构

Strata 建立在三个轴和一个引擎上：

```
技能轴 (SKILL)        — 工具调用频率 + 共现模式 → 技能簇
记忆轴 (MEMORY)       — 关键词匹配 → 经验笔记定位
灵魂轴 (SOUL)         — 行为模式代理指标（建设中）

共振引擎               — 成功经验 + 错误记录 → 预检/推荐
```

### 簇结构

每个会话被映射到一个簇。簇内包含：

| 字段 | 说明 |
|------|------|
| `sessions` | 该簇命中的会话数 |
| `top_keywords` | 高频关键词 |
| `experience` | 阶段标记的经验笔记 |
| `last_session` | 最近一次会话摘要 |

### 阶段标记

每条经验笔记带一个阶段前缀：

| 前缀 | 含义 | 示例 |
|------|------|------|
| `[动手]` | 工具/方法选择 | `[动手] pip 装包用 uv + 清华镜像` |
| `[卡住]` | 失败根因 | `[卡住] 某 API 端点已返回 403` |
| `[解决]` | 修复策略 | `[解决] git clone 加 --depth 1` |

### 错误共振（第二层）

失败记录不单独存放，而是挂靠到对应的成功簇上。调用一个技能前，先查该簇的错误记录做预检。

## 快速开始

### 前置条件

- Python 3.10+
- 一个 Hermes Agent 实例（或任意可输出 JSONL 会话历史的 LLM 应用）

### 安装

```bash
# 1. 创建项目目录
mkdir -p strata && cd strata

# 2. 下载核心文件
# （从本仓库的 scripts/ 目录下载以下文件）
#   - cluster-engine.py     — 簇引擎
#   - live-logger.py        — 实时会话记录
#   - error-collector.py    — 错误收集
#   - drift-report.py       — 漂移月报

# 3. 准备会话历史
# 将你的会话历史放入 data/session-history.jsonl
# 格式: 每行一个 JSON 对象
# {"ts": "2026-01-01 12:00", "text": "会话摘要", "source": "cli", "msgs": 10}

# 4. 运行
python3 cluster-engine.py build    # 首次建立簇
python3 cluster-engine.py predict "你的问题"  # 匹配经验笔记
```

### 实时记录

```bash
# 每轮对话记录
python3 live-logger.py log "用户说" "我的回复摘要"

# 会话结束时归档
python3 live-logger.py finalize    # 自动合并 + 重建簇
```

### 错误收集

```bash
# 记录一次错误（挂靠到簇 18）
python3 error-collector.py log 18 "tool_name" "error_type" "解决方案"

# 查看已知错误
python3 error-collector.py summary
```

### 漂移月报

```bash
python3 drift-report.py
# 输出:
# C18:  199次 (49.5%) ████████████  工程经验
# C10:   51次 (12.7%) ██████         信息检索
# ...
```

## 输出说明

### 经验笔记（experience-notes.json）

```json
{
  "18": {
    "cluster": 18,
    "sessions": 199,
    "top_keywords": ["yaml", "api", "配置"],
    "experience": [
      "[动手] pip 装包用 uv + 清华镜像",
      "[卡住] config.yaml 用 key_env 而非 api_key_env",
      "[解决] git clone 加 --depth 1"
    ]
  }
}
```

### 错误索引（errors/INDEX.json）

```json
{
  "total_errors": 63,
  "clusters": {
    "18": {"count": 12, "last": "2026-07-02T16:00:00"},
    "10": {"count": 5, "last": "2026-07-01T12:00:00"}
  }
}
```

## 设计哲学

1. **零 API 成本** — 所有运算在本地完成，不调用外部模型
2. **关键词匹配优先** — 不用 embedding/向量数据库，零延迟
3. **越用越聪明** — 每轮对话都在喂养未来的自己
4. **错误即数据** — 失败和成功同等重要，挂靠到同一个簇
5. **注意力可观测** — 簇分布曲线比任何周报都诚实

## 与 Hermes Agent 集成

如果你使用 Hermes Agent，Strata 的经验笔记会自动注入 SOUL.md：

```
📁 C18 经验 (199次会话, 5条):
   • [动手] pip 装包用 uv + 清华镜像
   • [卡住] config.yaml key_env 不是 api_key_env
   • [解决] git clone 加 --depth 1
```

每次对话开始时，系统根据你的第一句话匹配活跃簇，将历史经验注入回答前缀。

## 代码仓库

所有核心代码在 `scripts/` 目录下，总计约 500 行 Python，零外部依赖（仅使用标准库）。

- `state-space/cluster-engine.py` — 簇引擎（训练 + 预测）
- `state-space/live-logger.py` — 实时会话记录器
- `state-space/error-collector.py` — 错误收集器
- `state-space/drift-report.py` — 注意力漂移月报
- `state-space/check-size.py` — 系统健康检查
