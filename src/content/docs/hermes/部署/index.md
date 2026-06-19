---
title: Hermes 部署指南
description: 从零开始部署 Hermes Agent——环境、容器、网络、GPU
sidebar:
  order: 1
---

本文档覆盖 Hermes Agent 从零搭建的全流程：基础环境准备、Docker 部署、代理配置、GPU 透传、网络兜底等。

## 内容

- **[环境准备](env-prep)** — 系统依赖、Python、Hermes 安装
- **[Docker 部署](docker-deploy)** — Docker 环境搭建与容器管理
- **[代理配置](proxy-setup)** — mihomo 代理容器部署
- **[GPU 透传](gpu-compute)** — NVIDIA GPU 穿透到 Docker 容器
- **[验证运行](verify)** — 确认一切正常
- **[断网兜底](network-fallback)** — 本地模型自动 Fallback
- **[云端生图](cloud-image-gen)** — Cloudflare Worker 图片生成代理
- **[GPU 训练踩坑](gpu-training-pitfalls)** — WSL2 + Docker GPU 训练全记录
