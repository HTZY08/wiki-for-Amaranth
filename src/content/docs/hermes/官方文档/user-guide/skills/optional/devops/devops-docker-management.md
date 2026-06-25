--- frontmatter ---
--- frontmatter ---
---
title: "Docker 管理"
sidebar_label: "Docker 管理"
description: "管理 Docker 容器、镜像、卷、网络和 Compose 堆栈 — 生命周期操作、调试、清理以及 Dockerfile 优化"
---

--- body ---
--- body ---
{/* 此页面由 skill 的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Docker 管理

管理 Docker 容器（Container）、镜像（Image）、卷（Volume）、网络（Network）和 Compose 堆栈（Stack） — 生命周期操作、调试、清理以及 Dockerfile 优化。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/devops/docker-management` 安装 |
| 路径 | `optional-skills/devops/docker-management` |
| 版本 | `1.0.0` |
| 作者 | sprmn24 |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `docker`，`容器`，`devops`，`基础设施`，`compose`，`镜像`，`卷`，`网络`，`调试` |

## 参考：完整 SKILL.md

:::info
以下是在技能被触发时 Hermes 加载的完整技能定义。当技能激活时，这就是 agent 看到的指令。
:::

# Docker 管理

使用标准 Docker CLI 命令管理 Docker 容器、镜像、卷、网络和 Compose 堆栈。除 Docker 本身外无需额外依赖。

## 何时使用

- 运行、停止、重启、删除或检查容器
- 构建、拉取、推送、标记或清理 Docker 镜像
- 使用 Docker Compose（多服务堆栈）
- 管理卷或网络
- 调试崩溃的容器或分析日志
- 检查 Docker 磁盘使用情况或释放空间
- 审阅或优化 Dockerfile

## 前提条件

- Docker 引擎已安装并运行
- 用户已添加到 `docker` 组（或使用 `sudo`）
- Docker Compose v2（现代 Docker 安装自带）

快速检查：

```bash
docker --version && docker compose version
```

## 快速参考

| 任务 | 命令 |
|------|---------|
| 运行容器（后台） | `docker run -d --name NAME IMAGE` |
| 停止 + 删除 | `docker stop NAME && docker rm NAME` |
| 查看日志（实时跟踪） | `docker logs --tail 50 -f NAME` |
| 进入容器 Shell | `docker exec -it NAME /bin/sh` |
| 列出所有容器 | `docker ps -a` |
| 构建镜像 | `docker build -t TAG .` |
| Compose 启动 | `docker compose up -d` |
| Compose 停止并清理 | `docker compose down` |
| 磁盘使用情况 | `docker system df` |
| 清理悬空资源 | `docker image prune && docker container prune` |

## 操作流程

### 1. 确定领域

判断请求属于哪个领域：

- **容器生命周期** → 运行、停止、启动、重启、删除、暂停/恢复
- **容器交互** → exec、cp、logs、inspect、stats
- **镜像管理** → 构建、拉取、推送、标记、删除、保存/加载
- **Docker Compose** → 启动、停止、查看状态、查看日志、执行命令、构建、验证配置
- **卷和网络** → 创建、检查、删除、清理、连接
- **故障排查** → 日志分析、退出代码、资源问题

### 2. 容器操作

**运行新容器：**

```bash
# 后台服务并映射端口
docker run -d --name web -p 8080:80 nginx

# 带环境变量
docker run -d -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=mydb --name db postgres:16

# 带持久化数据（命名卷）
docker run -d -v pgdata:/var/lib/postgresql/data --name db postgres:16

# 开发用（绑定挂载源码）
docker run -d -v $(pwd)/src:/app/src -p 3000:3000 --name dev my-app

# 交互式调试（退出时自动删除）
docker run -it --rm ubuntu:22.04 /bin/bash

# 设置资源限制和重启策略
docker run -d --memory=512m --cpus=1.5 --restart=unless-stopped --name app my-app
```

关键标志：`-d` 后台运行，`-it` 交互式 + 终端，`--rm` 自动删除，`-p` 端口映射（主机:容器），`-e` 环境变量，`-v` 卷，`--name` 名称，`--restart` 重启策略。

**管理运行中的容器：**

```bash
docker ps                        # 运行中的容器
docker ps -a                     # 所有容器（包括已停止的）
docker stop NAME                 # 优雅停止
docker start NAME                # 启动已停止的容器
docker restart NAME              # 停止 + 启动
docker rm NAME                   # 删除已停止的容器
docker rm -f NAME                # 强制删除运行中的容器
docker container prune           # 删除所有已停止的容器
```

**与容器交互：**

```bash
docker exec -it NAME /bin/sh          # 进入 Shell（如果可用则用 /bin/bash）
docker exec NAME env                   # 查看环境变量
docker exec -u root NAME apt update    # 以特定用户身份执行
docker logs --tail 100 -f NAME         # 实时跟踪最近 100 行日志
docker logs --since 2h NAME            # 最近 2 小时的日志
docker cp NAME:/path/file ./local      # 从容器复制文件到本地
docker cp ./file NAME:/path/           # 从本地复制文件到容器
docker inspect NAME                    # 容器详细信息（JSON）
docker stats --no-stream               # 资源使用快照
docker top NAME                        # 运行中的进程
```

### 3. 镜像管理

```bash
# 构建
docker build -t my-app:latest .
docker build -t my-app:prod -f Dockerfile.prod .
docker build --no-cache -t my-app .              # 清缓存重建
DOCKER_BUILDKIT=1 docker build -t my-app .       # 使用 BuildKit 加速

# 拉取和推送
docker pull node:20-alpine
docker login ghcr.io
docker tag my-app:latest registry/my-app:v1.0
docker push registry/my-app:v1.0

# 检查
docker images                          # 列出本地镜像
docker history IMAGE                   # 查看层
docker inspect IMAGE                   # 详细信息

# 清理
docker image prune                     # 删除悬空（无标签）镜像
docker image prune -a                  # 删除所有未使用的镜像（谨慎！）
docker image prune -a --filter "until=168h"   # 删除超过 7 天的未使用镜像
```

### 4. Docker Compose

```bash
# 启动/停止
docker compose up -d                   # 后台启动所有服务
docker compose up -d --build           # 启动前重新构建镜像
docker compose down                    # 停止并删除容器
docker compose down -v                 # 同时删除卷（数据会丢失）

# 监控
docker compose ps                      # 列出服务
docker compose logs -f api             # 实时查看特定服务日志
docker compose logs --tail 50          # 查看所有服务最近 50 行日志

# 交互
docker compose exec api /bin/sh        # 进入运行中的服务 Shell
docker compose run --rm api npm test   # 一次性命令（新容器）
docker compose restart api             # 重启特定服务

# 验证
docker compose config                  # 验证并查看解析后的配置
```

**最小化 compose.yml 示例：**

```yaml
services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

### 5. 卷和网络

```bash
# 卷
docker volume ls                       # 列出卷
docker volume create mydata            # 创建命名卷
docker volume inspect mydata           # 详细信息（挂载点等）
docker volume rm mydata                # 删除（如果正在使用则失败）
docker volume prune                    # 删除未使用的卷

# 网络
docker network ls                      # 列出网络
docker network create mynet            # 创建桥接网络
docker network inspect mynet           # 详细信息（连接的容器）
docker network connect mynet NAME      # 将容器连接到网络
docker network disconnect mynet NAME   # 断开容器与网络的连接
docker network rm mynet                # 删除网络
docker network prune                   # 删除未使用的网络
```

### 6. 磁盘使用与清理

始终先诊断再清理：

```bash
# 检查空间使用情况
docker system df                       # 摘要
docker system df -v                    # 详细分解

# 针对性清理（安全）
docker container prune                 # 已停止的容器
docker image prune                     # 悬空镜像
docker volume prune                    # 未使用的卷
docker network prune                   # 未使用的网络

# 激进清理（请先与用户确认！）
docker system prune                    # 容器 + 镜像 + 网络
docker system prune -a                 # 还包括未使用的镜像
docker system prune -a --volumes       # 所有内容 — 包括命名卷
```

**警告：** 除非得到用户确认，否则切勿运行 `docker system prune -a --volumes`。这会删除可能包含重要数据的命名卷。

## 常见问题

| 问题 | 原因 | 解决方法 |
|---------|-------|-----|
| 容器立即退出 | 主进程完成或崩溃 | 检查 `docker logs NAME`，尝试 `docker run -it --entrypoint /bin/sh IMAGE` |
| "port is already allocated" | 其他进程正在使用该端口 | 使用 `docker ps` 或 `lsof -i :PORT` 查找 |
| "no space left on device" | Docker 磁盘满 | 运行 `docker system df` 然后针对性清理 |
| 无法连接到容器 | 应用在容器内绑定到 127.0.0.1 | 应用必须绑定到 `0.0.0.0`，检查 `-p` 映射 |
| 卷权限拒绝 | 主机与容器的 UID/GID 不匹配 | 使用 `--user $(id -u):$(id -g)` 或修复权限 |
| Compose 服务无法互相访问 | 错误的网络或服务名称 | 服务使用服务名作为主机名，检查 `docker compose config` |
| 构建缓存不生效 | Dockerfile 中层的顺序错误 | 将变化少的层放在前面（依赖项放在源码前） |
| 镜像过大 | 未使用多阶段构建，无 .dockerignore | 使用多阶段构建，添加 `.dockerignore` |

## 验证

执行任何 Docker 操作后，验证结果：

- **容器已启动？** → `docker ps`（检查状态为 "Up"）
- **日志无错误？** → `docker logs --tail 20 NAME`（无错误）
- **端口可访问？** → `curl -s http://localhost:PORT` 或 `docker port NAME`
- **镜像已构建？** → `docker images | grep TAG`
- **Compose 堆栈健康？** → `docker compose ps`（所有服务状态为 "running" 或 "healthy"）
- **磁盘空间释放？** → `docker system df`（对比前后）

## Dockerfile 优化提示

在审查或创建 Dockerfile 时，建议进行以下改进：

1. **多阶段构建** — 将构建环境与运行环境分离，减小最终镜像体积
2. **层顺序** — 将依赖项放在源代码之前，这样代码变更不会使缓存层失效
3. **合并 RUN 命令** — 减少层数，镜像更小
4. **使用 .dockerignore** — 排除 `node_modules`、`.git`、`__pycache__` 等
5. **固定基础镜像版本** — 使用 `node:20-alpine` 而非 `node:latest`
6. **以非 root 用户运行** — 添加 `USER` 指令增强安全性
7. **使用 slim/alpine 基础镜像** — 使用 `python:3.12-slim` 而非 `python:3.12`