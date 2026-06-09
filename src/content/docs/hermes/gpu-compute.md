---
title: GPU 透传
description: 让 Hermes 使用 NVIDIA 显卡加速
---

配置 GPU 后，Hermes 可以使用显卡加速语音识别、本地模型推理等任务。

---

## 前置条件

- ✅ 宿主机已安装 NVIDIA 显卡驱动（`nvidia-smi` 能正常输出）
- ✅ WSL2（Windows 用户）
- ✅ Docker Desktop（Windows 用户）

## 安装 NVIDIA Container Toolkit

### Windows + WSL2 用户

在 WSL2（Ubuntu）终端中运行：

```bash
# 添加 NVIDIA 软件源
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 安装
sudo apt update
sudo apt install -y nvidia-container-toolkit

# 配置 Docker
sudo nvidia-ctk runtime configure --runtime=docker

# 重启 Docker
sudo systemctl restart docker
```

### Linux 原生用户

```bash
# 同样方法安装
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
# ⚠️ 以上仓库路径可能已更新，如果报 404 请参考 NVIDIA Container Toolkit 官方文档（https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html）
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker
```

## 配置 Docker Compose

在 `docker-compose.yml` 中添加 GPU 配置：

```yaml
services:
  hermes:
    # ... 其他配置 ...
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

## 验证 GPU 透传

重启容器后验证：

```bash
docker compose up -d
docker exec hermes-agent nvidia-smi
```

应该能看到：
```
+-----------------------------------------------------------------------+
| NVIDIA-SMI ...  Driver Version: ...  CUDA Version: ...                |
|-------------------------------+----------------------+----------------+
| GPU  Name            TCC/WDDN | Bus-Id        Disp.A | Volatile Uncorr.|
|===============================+======================+================|
|   0  NVIDIA GPU          ...  | ...                  |                |
+-------------------------------+----------------------+----------------+
```

## GPU 加速的应用

### 语音转文字（Whisper）

配置好 GPU 后，语音转文字会自动使用 GPU 加速，处理速度提升 5-10 倍。

```bash
# 在容器内检查 Whisper 是否使用 GPU
docker exec hermes-agent python3 -c "import torch; print(torch.cuda.is_available())"
# 应该输出：True
```

### 本地模型推理

可以用 ollama 或 llama.cpp 在容器内运行本地模型：

```bash
# 在 Hermes 对话中
你：能不能在本地跑一个翻译模型？
```

## 故障排查

### nvidia-smi 报错 "command not found"

驱动还没有安装或者 WSL2 没有继承驱动。在 Windows 下安装 NVIDIA 驱动后重启。

### "could not select device driver "nvidia""

NVIDIA Container Toolkit 没有正确安装。重新执行安装步骤，确认 `sudo systemctl restart docker` 成功。

### 容器能启动但 nvidia-smi 不显示 GPU

```bash
# 检查 WSL2 中是否能识别 GPU
nvidia-smi
```

如果在 WSL2 终端里能看到 GPU，但容器里看不到，检查 Docker Desktop 的 WSL Integration 设置是否开启。
