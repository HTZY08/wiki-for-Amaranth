---
title: GPU 计算
description: 本地 GPU 环境配置与加速服务
---

GPU 用于加速语音识别、图像生成、本地模型推理等任务。本文档覆盖从底层环境到上层应用的完整配置链。

---

## 硬件与部署环境

| 项目 | 说明 |
|------|------|
| GPU | NVIDIA 12GB VRAM |
| 宿主系统 | WSL2 (Ubuntu) + Docker Desktop |
| 驱动 | Windows 侧安装 NVIDIA 驱动，WSL2 自动继承 |
| CUDA 版本 | 由 NVIDIA 驱动决定（向下兼容） |

## 第一步：基础驱动与 CUDA

### 在 Windows 端安装驱动

Windows 中安装 NVIDIA Game Ready 或 Studio 驱动后，WSL2 会自动继承 GPU 访问能力。

```bash
# 在 WSL2 终端中验证
nvidia-smi
```

如看到 GPU 信息（型号、显存、驱动版本）即代表 WSL2 已获得 GPU 访问权。若提示 `command not found`，需在 Windows 安装 NVIDIA 驱动后重启。

### WSL2 内 CUDA 工具包（可选）

容器化部署时 CUDA 由镜像提供，不需要在 WSL2 侧安装。如需在 WSL2 原生环境运行 GPU 任务，可安装：

```bash
# CUDA 工具包由 NVIDIA 官方 deb 源提供
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install -y cuda-toolkit
```

### 验证 CUDA

```bash
nvcc --version
```

---

## 第二步：NVIDIA Container Toolkit（Docker GPU 透传）

Hermes 运行在 Docker 容器中，容器内访问 GPU 需要 NVIDIA Container Toolkit。

### 安装

```bash
# 添加 NVIDIA 软件源
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 安装
sudo apt update
sudo apt install -y nvidia-container-toolkit

# 配置 Docker 运行时
sudo nvidia-ctk runtime configure --runtime=docker

# 重启 Docker
sudo systemctl restart docker
```

### Docker Compose 配置

在 `docker-compose.yml` 中添加：

```yaml
services:
  hermes:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

WSL2 + Docker Desktop 环境下也可通过设备节点方式：

```yaml
services:
  hermes:
    devices:
      - /dev/dri:/dev/dri
```

### 验证 Docker GPU 透传

```bash
docker compose up -d
docker exec hermes-agent nvidia-smi
```

预期输出应显示 GPU 型号和 12GB 显存。

```bash
# 容器内 Python 验证 CUDA
docker exec hermes-agent python3 -c "import torch; print(torch.cuda.is_available())"
# 应输出：True
```

---

## 第三步：本地 GPU 服务部署

### 语音转文字（Whisper）

GPU 加速下 Whisper 处理速度提升 5-10 倍：

```bash
# 安装 faster-whisper（容器内或 WSL2 原生）
pip install faster-whisper

# 自动使用 GPU
from faster_whisper import WhisperModel
model = WhisperModel("base", device="cuda", compute_type="float16")
```

faster-whisper 显存占用约 1-2GB，适合常驻运行。

### ComfyUI 图像生成

详见 [ComfyUI 本地部署与训练](/projects/comfyui/) 项目页。

12GB 显存可运行 SDXL 级别模型，需 `--force-fp16` 参数防止 OOM。

### 本地 LLM 推理

| 工具 | 配置方式 | 显存占用 |
|------|---------|---------|
| llama.cpp | 原生 CUDA 后端，GGUF 量化模型 | 取决于模型大小 |
| LM Studio | Docker 容器外安装，API 对接 | 取决于模型大小 |

---

## 故障排查

### `nvidia-smi` 报错 "command not found"

WSL2 未继承 Windows 的 NVIDIA 驱动。在 Windows 端安装 NVIDIA 驱动后重启。

### "could not select device driver "nvidia""

NVIDIA Container Toolkit 未正确安装。重新执行安装步骤，确认 `sudo systemctl restart docker` 成功。

### Docker 容器内 `nvidia-smi` 不显示 GPU

```bash
# 先在 WSL2 终端中确认 GPU 可见
nvidia-smi

# 如 WSL2 可见但容器不可见
# 检查 Docker Desktop → Settings → Resources → WSL Integration
# 确认对应 WSL 发行版的 integration 已开启
```

### WSL2 GPU 训练 TDR 超时

长时间 GPU 密集计算可能触发 Windows 驱动超时保护（TDR），表现为 CUDA driver error 或进程被杀死。当前无稳定解决方案，建议：

- 短任务分批执行
- 切换至云端 GPU 进行训练
- 容器外原生运行（绕过 Docker 虚拟化层）

---

## 使用场景显存参考

| 服务 | 用途 | 显存占用 |
|------|------|---------|
| faster-whisper | 音频/语音转文字 | 低（~1-2GB） |
| ComfyUI (SDXL) | AI 图像生成 | 中高（~6-8GB） |
| llama.cpp (7B Q4) | 本地语言模型推理 | ~5-6GB |
| LM Studio (13B Q4) | 本地模型服务 | ~8-10GB |
