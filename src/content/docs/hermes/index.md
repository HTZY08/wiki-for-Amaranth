---
title: 概述
description: Hermes Agent 本地化部署的整体架构
---

Hermes Agent 是一个自托管 AI 代理系统，可在本地 Docker 环境中运行，通过多模型路由调用不同的 LLM 后端完成各种自动化任务。

## 架构总览

```
┌─────────────────────────────────────┐
│          WSL2 (Ubuntu)              │
│  ┌───────────────────────────────┐  │
│  │      Docker Container         │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │   Hermes Agent          │  │  │
│  │  │   ├── CLI/TUI           │  │  │
│  │  │   ├── Gateway (微信等)  │  │  │
│  │  │   ├── Cron 调度         │  │  │
│  │  │   └── Skills 系统       │  │  │
│  │  └─────────────────────────┘  │  │
│  │         ▲                     │  │
│  │         │ HTTP/WS             │  │
│  │  ┌──────┴──────────┐          │  │
│  │  │  mihomo 代理    │          │  │
│  │  │  (Clash Meta)   │          │  │
│  │  └──────┬──────────┘          │  │
│  └─────────┼─────────────────────┘  │
│            │                        │
│       ┌────┴────┐                  │
│       │ NVIDIA  │                  │
│       │ 5070 Ti │ GPU 透传         │
│       └─────────┘                  │
└─────────────────────────────────────┘
            │
    ┌───────┴────────┐
    │   互联网出口    │
    │ (US 出口锁定)   │
    └────────────────┘
```

## 关键组件

| 组件 | 角色 |
|------|------|
| **Hermes Agent** | 核心代理系统，CLI/TUI 交互 |
| **Docker Desktop** | 容器运行时，管理 Hermes 容器生命周期 |
| **mihomo (Clash Meta)** | HTTP/HTTPS 代理，代理出口锁定美国 |
| **NVIDIA RTX 5070 Ti** | GPU 计算（Whisper 转录、本地 LLM 推理） |
| **多模型路由** | DeepSeek(主力) / GPT / Claude / Gemini 按任务分发 |

## 目录结构

```
~/.hermes/                    # Hermes 主配置目录
├── config.yaml               # 全局配置
├── .env                      # 环境变量（API Key 等）
├── profiles/
│   └── default/              # 默认 profile
│       ├── config.yaml
│       ├── skills/           # Skill 定义
│       ├── plugins/          # 插件
│       ├── cron/             # 定时任务
│       └── memories/         # 持久记忆
├── scripts/                  # 自定义脚本
└── audio_cache/              # TTS 缓存
```

## 内容索引

- [Docker 部署](/hermes/docker-deploy/) — 容器构建与运行
- [代理配置](/hermes/proxy-setup/) — mihomo 代理与网络出口
- [GPU 透传](/hermes/gpu-compute/) — NVIDIA 显卡容器直通
- [多模型路由](/hermes/model-routing/) — MoE 式模型调度架构
- [技能系统](/hermes/skills-system/) — Skill 体系与自定义
- [微信 Gateway](/hermes/gateway-wechat/) — 微信消息接入
- [定时任务](/hermes/cron-background/) — 自动化后台调度
