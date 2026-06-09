---
title: ComfyUI 本地部署与训练
description: WSL2 环境下 ComfyUI 的部署、模型加载、LoRA 训练与出图管线
---

记录在 WSL2（RTX 5070 Ti 12GB）环境下的 ComfyUI 完整工作流程。当前环境已清理，此页为操作留档。

---

## 环境概览

| 项目 | 规格 |
|------|------|
| 操作系统 | WSL2 (Ubuntu) + Docker Desktop |
| GPU | NVIDIA RTX 5070 Ti (12GB VRAM) |
| 驱动 | Windows 侧安装 NVIDIA 驱动，WSL2 自动继承 |
| 部署路径 | `/opt/data/ComfyUI/` |
| 虚拟环境 | `.venv/` 下独立 Python venv |

## ComfyUI 部署

### 1. 克隆与安装

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git /opt/data/ComfyUI
cd /opt/data/ComfyUI

# 创建虚拟环境并安装依赖
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 下载模型

ComfyUI 默认模型目录结构：

```
ComfyUI/
├── models/
│   ├── checkpoints/         # SD 大模型 (.safetensors)
│   ├── loras/               # LoRA 权重
│   ├── vae/                 # VAE 模型
│   ├── controlnet/          # ControlNet 模型
│   ├── ipadapter/           # IP-Adapter 模型
│   └── ultralytics/         # Ultralytics（如 bbox/pose 检测）
├── custom_nodes/            # 自定义节点
├── input/                   # 输入图片
├── output/                  # 输出目录
└── main.py                  # 启动入口
```

加载的模型示例：

- **大模型**：`juggernautXL_ragnarokBy.safetensors`（SDXL 系写实风格）
- **LoRA/ControlNet**：根据管线需求下载对应节点

### 3. 启动方式

```bash
# 手动启动
cd /opt/data/ComfyUI && source .venv/bin/activate && python main.py --force-fp16

# 或用启动脚本
bash /opt/data/scripts/start_comfy.sh
```

`--force-fp16` 强制半精度推理，12GB 显存下至关重要——不开启 FP16 会导致 SDXL 模型 OOM。

启动脚本内容（`start_comfy.sh`）：

```bash
#!/bin/bash
cd /opt/data/ComfyUI
exec /opt/data/ComfyUI/.venv/bin/python3 main.py --force-fp16 --listen > /tmp/comfyui.log 2>&1
```

`--listen` 将 WebUI 绑定到 `0.0.0.0:8188`，方便本地浏览器访问。

### 4. 验证

```bash
# 检查进程
ps aux | grep main.py | grep -v grep

# 检查 API 是否响应
curl -s http://127.0.0.1:8188/system_stats | head -20
```

---

## LoRA 训练准备

### 训练素材目录结构

```
lora_training/
├── lian_face_class/         # 面部特写数据集
├── primary_face_ref.jpg     # 主面部参考图
├── 01_front_body.jpg        # 正面全身参考
├── velvet_front.jpg         # 服装/风格参考
└── ...
```

素材经裁剪、去重后整理，用于训练角色 LoRA。

### 训练框架选择

| 框架 | 说明 |
|------|------|
| Kohya's GUI | 功能全面，适合 SDXL LoRA 训练 |
| SD-Scripts | 命令行版，适合脚本化批量训练 |

### WSL2 下训练的已知限制

WSL2 上的 GPU 密集计算存在 **TDR（Timeout Detection and Recovery）超时** 问题。长时间高负载训练（30 分钟以上）容易触发 Windows 显卡驱动超时保护，导致：

- CUDA driver error 崩溃
- 训练进程被杀死
- 需要重启 WSL2 会话恢复

实践中未能完成端到端 LoRA 全量训练，最终放弃本地训练方案。

---

## 贴吧风格出图管线

### 管线结构

Codex 辅助设计的 ComfyUI 工作流，用于生成角色一致性出图：

```
SDXL Base (juggernautXL)
    │
    ├── OpenPose (0.65)           # 姿态骨架控制
    ├── InstantID (0.75)          # 面部身份保持
    └── IP-Adapter (0.45)         # 风格参考迁移
```

三个控制层并联接入，权重通过实验调优：

| 组件 | 权重 | 作用 |
|------|------|------|
| OpenPose | 0.65 | 保持姿态骨架，防止肢体扭曲 |
| InstantID | 0.75 | 锁定面部特征，确保角色身份一致 |
| IP-Adapter | 0.45 | 迁移参考图的风格/色调 |

### 输入素材

- `primary_face_ref.jpg` — 角色正脸参考
- `01_front_body.jpg` — 正面全身照
- `velvet_front.jpg` — 质感/服装风格参考

### 产出测试图

管线调通后产出首张测试图 `Lian_codex_v1_00001_.png`（约 1MB），验证了：

- 面部一致性 ✅
- 姿态控制 ✅
- 风格迁移 ✅

---

## 最终状态

因以下原因，ComfyUI 全套环境已于 2026 年 6 月 7 日清理：

| 原因 | 说明 |
|------|------|
| WSL2 GPU 驱动不兼容 | TDR 超时阻止持续密集训练 |
| 角色图源充足 | 用户已获得 94 张 ChatGPT 高质量出图 |
| 维护成本高 | ComfyUI 自定义节点版本冲突，频繁调试 |

### 已删除内容

```bash
# 完整目录删除
rm -rf /opt/data/ComfyUI/          # ComfyUI 主程序 + 模型
rm -rf /opt/data/lora_training/    # 训练素材
rm -f /opt/data/scripts/start_comfy.sh  # 启动脚本
```

当前系统无 ComfyUI / 训练框架，角色生图依赖云端 API 方案。
