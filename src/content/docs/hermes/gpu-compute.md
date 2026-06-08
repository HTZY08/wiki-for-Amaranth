---
title: GPU 透传
description: NVIDIA 显卡直通 Docker 容器
---

Hermes 容器内的 GPU 加速服务（如 Whisper 音频转录、本地 LLM 推理）需要将宿主机 NVIDIA 显卡透传入容器。

## 环境

- **GPU**: NVIDIA RTX 5070 Ti (12GB VRAM)
- **宿主**: WSL2 (Ubuntu) + Docker Desktop
- **驱动**: NVIDIA Driver 通过 Windows 侧安装，WSL2 自动继承

## 前提条件

WSL2 中安装 NVIDIA Container Toolkit：

```bash
# 添加 NVIDIA 容器工具源
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update && sudo apt install -y nvidia-container-toolkit

# 配置 Docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

## Docker Compose 配置

```yaml
services:
  hermes:
    image: hermes-agent
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

在 Windows + WSL2 + Docker Desktop 环境下，也可以通过 `devices` 方式直通：

```yaml
services:
  hermes:
    devices:
      - /dev/dri:/dev/dri  # WSL2 GPU 设备节点
```

## 验证

```bash
# 容器内检查 GPU 是否可见
docker exec hermes-agent nvidia-smi

# 预期输出应显示 RTX 5070 Ti 及其 12GB 显存
```

## 使用场景

| 服务 | 用途 | GPU 负载 |
|------|------|----------|
| faster-whisper | 音频/语音转文字 | 低（~1-2GB） |
| ComfyUI | AI 图像生成 | 中高（~6-8GB） |
| 本地 LLM (llama.cpp) | 本地语言模型推理 | 取决于模型大小 |
| LM Studio | 本地模型服务 | 取决于模型大小 |
