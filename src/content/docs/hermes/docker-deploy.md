---
title: Docker 部署
description: Hermes Agent 的 Docker 容器构建与运行
---

Hermes Agent 官方通过 pip 分发，但在 Docker 中运行可以隔离环境依赖，方便 GPU 透传和网络配置。

## 构建镜像

项目仓库包含 `Dockerfile` 和 `docker-compose.yml`，建议直接基于官方镜像或从源码构建。

```dockerfile
# 简化版 Dockerfile 结构
FROM python:3.13-slim
# 使用 uv 安装依赖
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# ... 安装 Hermes Agent 及依赖
```

## Docker Compose 配置

```yaml
version: '3.8'
services:
  hermes:
    build: .
    container_name: hermes-agent
    volumes:
      - ~/.hermes:/root/.hermes
      - /opt/data:/opt/data
    environment:
      - HERMES_HOME=/root/.hermes
      - http_proxy=http://mihomo:7890
      - https_proxy=http://mihomo:7890
    devices:
      - /dev/dri:/dev/dri  # GPU 透传
    depends_on:
      - mihomo
    stdin_open: true
    tty: true

  mihomo:
    image: ghcr.io/metacubex/mihomo:latest
    container_name: mihomo
    volumes:
      - ./mihomo-config.yaml:/root/.config/mihomo/config.yaml
    ports:
      - "7890:7890"
      - "9090:9090"
    cap_add:
      - NET_ADMIN
```

## 启动与停止

```bash
# 启动所有服务
docker compose up -d

# 进入 Hermes 容器 CLI
docker exec -it hermes-agent hermes

# 查看日志
docker compose logs -f hermes

# 停止
docker compose down
```

## 关键路径映射

| 主机路径 | 容器路径 | 用途 |
|----------|----------|------|
| `~/.hermes/` | `/root/.hermes/` | 配置、Skill、记忆 |
| `/opt/data/` | `/opt/data/` | 工作目录、项目文件 |
| `D:\\传递文件\\` | `/opt/data/传递文件/` | 与 Windows 互传文件 |

## 常见问题

### 容器重启后环境恢复

使用 `hermes-env-recovery` skill 可一键恢复 TTS 补丁、Gateway、视觉模型、GPU 服务等配置。

### 端口冲突

默认端口为 TUI/CLI 交互，Gateway 服务需额外映射端口（如微信服务端口）。
