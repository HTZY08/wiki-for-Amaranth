---
title: BigSet 部署指南
description: 一句话构建结构化数据集，AI 自动推断 schema + 多 agent 并行填表 + 定时刷新
---

> 开源项目 · AGPL-3.0 · [GitHub](https://github.com/tinyfish-io/bigset) · 1.2k Stars

**BigSet** 是 tinyfish 出品的工具：你输入一句自然语言描述，AI 自动推断表结构 → 编排 agent 搜网页 → 子 agent 并行填数据 → 定时自动刷新 → 导出 CSV/XLSX。

## 原理

```
一句话需求（"GPU 价格表"）
       ↓
AI 推断 schema（列名/类型/主键）
       ↓
编排 agent 搜索候选实体（NVIDIA、AMD、Intel…）
       ↓
子 agent 并行调研每个实体 → 真实数据校验 → 填行
       ↓
结构化表格（可浏览/导出/定时刷新）
```

## 环境要求

- **Docker**（已装：v26.1.5）
- **Make**（WSL 未装，需 `apt install make` 或手动执行）
- 三个 API Key（见下）

## 三个必备 API Key

| 服务 | 用途 | 费用 |
|------|------|------|
| **TinyFish** | 网页搜索 + 页面抓取 | Search 5次/分, Fetch 25次/分 免费 |
| **OpenRouter** | LLM 推理（Claude Sonnet + Qwen） | 按量付费，$5-10 起步 |
| **Clerk** | 用户登录认证 | 免费 |

## 一键部署

```bash
git clone https://github.com/tinyfish-io/bigset.git
cd bigset
cp .env.example .env
# 填三个 Key
make dev
```

打开 `http://localhost:3500` → 注册 → 新建 Dataset → 输入需求 → 开始。

> ⚠️ **WSL 关键坑**：项目**不能放在 /mnt/d/ 等 Windows 挂载目录**，否则 frontend 容器启动不了。务必放到 `~/projects/` 或 `/opt/data/` 下。

## 定价

- 免费层：每月 2,500 行操作（每月 1 日 UTC 重置）
- 预设数据集不占额度
- OpenRouter 消耗约几美元/数据集
