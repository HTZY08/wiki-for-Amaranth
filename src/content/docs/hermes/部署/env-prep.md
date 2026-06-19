---
title: 环境准备
description: 搭建 Hermes 前的准备工作——安装 Docker、配置 WSL2
---

在安装 Hermes Agent 之前，需要准备好运行环境。本指南以 **Windows + WSL2** 为例，Linux 和 macOS 用户可跳过 WSL2 相关步骤。

---

## 第一步：确认操作系统

打开"设置" → "系统" → "关于"，查看系统信息。

**你需要：**
- Windows 10 版本 2004 以上（build 19041 以上），或 Windows 11
- 或者直接使用 Linux（Ubuntu 22.04+ / Debian 12+）
- macOS（Intel 或 Apple Silicon）

---

## 第二步：安装 WSL2（仅 Windows）

WSL2 是 Windows 下的 Linux 子系统，Hermes 需要它作为运行环境。

### 一键安装

以**管理员身份**打开 PowerShell 或命令提示符（右键"开始"菜单 → Windows PowerShell(管理员)），运行：

```powershell
wsl --install
```

这个命令会自动安装 WSL2 和 Ubuntu。安装完成后重启电脑。

### 验证安装

重启后打开"开始"菜单 → 搜索"Ubuntu" → 打开。初次启动会提示设置 Linux 用户名和密码。

```bash
# 查看 WSL 版本
wsl --version

# 应该显示：WSL 版本 2.x.x.x
```

### 常见问题

**问题：`wsl --install` 报错**
> 原因：可能是虚拟化未开启。
> 解决：重启进 BIOS（开机时按 F2/Del），开启 Intel VT-x（Intel）或 AMD-V（AMD）。

**问题：安装后打开 Ubuntu 报错 "WSL 2 需要更新其内核组件"**
> 解决：下载安装 [WSL2 Linux 内核更新包](https://learn.microsoft.com/zh-cn/windows/wsl/install-manual#step-4---download-the-linux-kernel-update-package)

---

## 第三步：安装 Docker

Docker 用来运行 Hermes 及其配套服务。

### 下载安装

1. 访问 [Docker Desktop 官网](https://www.docker.com/products/docker-desktop/)
2. 下载 Windows 版本安装包
3. 双击安装，一路默认选项
4. 安装完成后重启电脑

### 配置 WSL2 集成

1. 打开 Docker Desktop
2. 点击右上角齿轮图标 → Settings → Resources → WSL Integration
3. 确保你的 Ubuntu 发行版开关是**打开**的
4. 点击 Apply & Restart

### 验证安装

打开 Ubuntu 终端，运行：

```bash
docker --version
# 输出类似：Docker version 26.x.x

docker ps
# 应该显示：CONTAINER ID  ... （列表可能是空的，但不报错就行）
```

---

## 第四步：GPU 驱动（可选，但有 GPU 建议装）

如果需要 GPU 加速（语音转文字、本地模型），需要安装 NVIDIA 驱动。

1. 下载 [NVIDIA Game Ready Driver](https://www.nvidia.com/download/index.aspx) 或 Studio Driver
2. 安装后重启
3. 在 Ubuntu 终端中验证：

```bash
nvidia-smi
```

如果能显示 GPU 信息（型号、显存）就说明驱动正常。

---

## 环境就绪检查清单

| 项目 | 验证命令 | 预期结果 |
|------|---------|---------|
| WSL2 | `wsl --version` | 显示版本号 |
| Ubuntu | 能打开终端输入命令 | 正常交互 |
| Docker | `docker --version` | 显示版本号 |
| Docker 运行 | `docker run hello-world` | 打印欢迎信息 |
| GPU（如有） | `nvidia-smi` | 显示 GPU 信息 |

全部通过？下一步进入 **[Docker 部署](/hermes/部署/docker-deploy/)**。
