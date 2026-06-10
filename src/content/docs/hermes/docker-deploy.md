---
title: Docker 部署
description: 从零开始——构建并运行 Hermes Agent 容器
---

本文档教你如何用 Docker 部署 Hermes Agent。你不需要懂 Docker 原理，按步骤执行命令即可。

---

| **说明**
|------|
| 本文档假设你已准备好代理配置。如果代理（mihomo）尚未配置，首次 `docker compose up -d` 时只会启动 Hermes 主容器。代理配置完成后需要重新启动（详见[代理配置](/hermes/proxy-setup/)）。 |

## 前置条件

- ✅ Docker Desktop 已安装并正常运行
- ✅ WSL2 集成已开启
- ✅ 终端（Ubuntu）已打开

## 下载项目

```bash
# 克隆 Hermes Agent 仓库
git clone https://github.com/nousresearch/hermes-agent.git
cd hermes-agent
```

> 如果提示 `git: command not found`，先运行 `sudo apt install git -y`

## 配置文件

Hermes 使用 YAML 格式的配置文件。项目目录下有一个示例配置：

```bash
# 复制示例配置
cp config.example.yaml config.yaml
```

### 最小配置

编辑 `config.yaml`，至少需要配置一个 AI 模型：

```yaml
providers:
  deepseek:
    api_key: "你的 DeepSeek API Key"
    models:
      - name: deepseek-chat
        type: chat
```

> API Key 从 AI 服务商的官网获取，通常是充值后生成的一个密钥字符串。

## 构建镜像

```bash
docker compose build
```

第一次构建会下载基础镜像和依赖，耗时 5-15 分钟，取决于网络速度。

## 启动容器

```bash
docker compose up -d
```

`-d` 参数表示后台运行。启动后：

```bash
# 查看容器状态
docker compose ps

# 应该显示两个容器：hermes-agent 和 mihomo（代理）
```

## 进入 Hermes

```bash
docker exec -it hermes-agent hermes
```

看到命令提示符说明成功了。输入 `你好` 测试对话。

## 常用操作

### 查看日志

```bash
# 实时查看 Hermes 日志
docker compose logs -f hermes

# 查看代理日志
docker compose logs -f mihomo
```

`-f` 表示持续跟踪输出，按 `Ctrl+C` 退出。

### 重启服务

```bash
docker compose restart hermes
```

### 停止服务

```bash
docker compose down
```

停止后所有容器会被删除，但配置和数据会保留在磁盘上（因为挂了数据卷）。

### 更新版本

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker compose build
docker compose up -d
```

## 目录结构说明

容器运行后，会创建以下目录结构：

```
~/.hermes/                  ← Hermes 配置和数据目录
├── config.yaml             ← 主配置（API Key 等）
├── profiles/
│   └── default/
│       ├── config.yaml     ← profile 专属配置
│       ├── skills/         ← 技能包
│       ├── plugins/        ← 插件
│       ├── cron/           ← 定时任务
│       └── memories/       ← 持久记忆
└── scripts/                ← 自定义脚本
```

## 故障排查

### 容器启动后立即退出

```bash
# 查看日志找出原因
docker compose logs hermes
```

常见原因：配置文件语法错误、API Key 缺失。

### 端口被占用

错误信息：`port is already allocated`

```bash
# 查找占用端口的进程
sudo lsof -i :7890

# 或在 docker-compose.yml 中修改端口映射
```

### 容器内无法联网

```bash
# 测试网络
docker exec hermes-agent curl -I https://api.github.com
```

如果不通，检查代理配置（参见[代理配置](/hermes/proxy-setup/)）。

## 高级配置：GPU 透传

基础部署只能运行对话和搜索功能。如果你需要使用图片生成（AI 绘图）、语音识别（Whisper GPU 加速）、本地模型推理等能力，需要为容器配置 GPU 访问。

### 修改 docker-compose.yml

在 `docker-compose.yml` 的 `hermes` 服务下添加：

```yaml
services:
  hermes:
    # ... 已有配置 ...
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

### 验证 GPU 是否生效

```bash
docker compose up -d
docker exec hermes-agent nvidia-smi
```

应显示 GPU 型号和显存信息。

> 完整 GPU 配置步骤（含 NVIDIA Container Toolkit 安装、常见故障排查）参见 **[GPU 计算](/hermes/gpu-compute/)**。

---

## 下一步

容器正常运行后，去配置 **[网络代理](/hermes/proxy-setup/)**。
