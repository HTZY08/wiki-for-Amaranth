---
title: "Docker + WSL2 GPU 训练踩坑全记录"
description: "Blackwell RTX 5070 Ti 上跑 QLoRA CPT 的真实经历——从 torch 装不上到 use_reentrant 挂死"
---

# Docker + WSL2 GPU 训练踩坑全记录

在 Docker 容器内（Hermes Agent 运行环境）用消费级 GPU 跑模型训练，听起来简单，实际每一步都可能翻车。本文记录了从零开始在 RTX 5070 Ti（Blackwell sm_120）上跑通 QLoRA Continued Pre-Training 的全过程——包括所有踩过的坑和修复方法。

---

## 一、硬件环境

| 项目 | 配置 |
|------|------|
| GPU | NVIDIA RTX 5070 Ti (12GB, Blackwell sm_120) |
| 系统 | WSL2 + Docker Desktop |
| 容器 | Hermes Agent Docker（无 root，叠加文件系统） |
| Python | 3.13（系统）+ 3.10（训练 venv） |
| PyTorch | 2.10.0+cu128 |
| CUDA | 13.3 |

---

## 二、训练管线

### 2.1 完整流程

```
选择基座模型（Qwen3-8B）
  → 准备训练数据（纯原文，不仿写）
  → Python 3.10 venv 搭建
  → torch 手动安装（pip 会挂死）
  → CUDA 库复制（import torch 缺 lib）
  → 安装 transformers/peft/bitsandbytes
  → QLoRA 4bit 配置（手动绕过 use_reentrant bug）
  → 训练（~55s/step，100 步 ~2h）
  → 交叉对比 checkpoint 输出
```

### 2.2 关键参数

```python
# QLoRA 配置
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)

# LoRA 配置
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM",
)

# 训练参数
training_args = TrainingArguments(
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    num_train_epochs=20,
    bf16=True,
    logging_steps=1,
    logging_first_step=True,
    save_steps=20,
    save_total_limit=5,
)
```

---

## 三、踩坑记录（按严重程度）

### 🔴 坑 1：PyTorch 2.9+ 梯度检查点挂死

**症状：** 训练启动成功，GPU 利用率 99%，但第一行 loss 永远不出现。进程看起来在跑，其实挂死了。

**根因：** PyTorch 2.10+ 要求梯度检查点必须显式传入 `use_reentrant` 参数。但 `peft` 的 `prepare_model_for_kbit_training()` 内部调用 `gradient_checkpointing_enable()` 时不带这个参数，导致第一个训练步骤挂死。

**尝试过的无效修复：**
- `PYTORCH_NO_CHECKPOINT_REENTRANT=1` 环境变量 → ❌ 无效
- 环境变量 + 二次调用 `gradient_checkpointing_enable(kwargs={"use_reentrant": False})` → ❌ 仍然挂死

**唯一有效的修复：** 完全绕过 `prepare_model_for_kbit_training`，手动进行 kbit 准备。

```python
# ❌ 不要这样做
from peft import prepare_model_for_kbit_training  # ← 不要 import

# ✅ 手动 kbit 准备
for param in model.parameters():
    param.requires_grad = False
    if param.ndim == 1:
        param.data = param.data.to(torch.float32)
model.gradient_checkpointing_enable(
    gradient_checkpointing_kwargs={"use_reentrant": False}
)
model = get_peft_model(model, lora_config)
```

### 🟡 坑 2：pip install torch 挂死

**症状：** `pip install torch` 在 Docker 叠加文件系统上卡住——进度条不动，几十分钟无响应。

**根因：** torch 的 wheel 包 874MB，pip 在叠加 FS 上解压时 `_path_stat` 调用阻塞。

**修复：** 直接下载 wheel，手动解压到 site-packages。

```python
import zipfile
with zipfile.ZipFile("torch-2.10.0-cp310-cp310-linux_x86_64.whl") as zf:
    zf.extractall(site_packages)
```

### 🟡 坑 3：import torch 报 CUDA 库找不到

**症状：** import torch 成功，但 `torch.cuda.is_available()` 返回 False，或在运行时报 `libcublasLt.so.12` 找不到。

**根因：** 手动解压的 torch 没有配套的 nvidia CUDA 库。

**修复：** 从系统 Python 3.13 的已安装 nvidia 包复制到训练 venv。

```bash
SYS_NVIDIA="/opt/data/home/.local/lib/python3.13/site-packages/nvidia"
VENV_NVIDIA="/opt/data/py310-qwen/lib/python3.10/site-packages/nvidia"
for d in $(ls -d $SYS_NVIDIA/*/); do
    name=$(basename $d)
    [ -d "$VENV_NVIDIA/$name" ] || cp -r "$d" "$VENV_NVIDIA/"
done
```

需要复制的包：cublas、cuda_nvrtc、cuda_runtime、cudnn、cufft、curand、cusparse、cusparselt、nccl、nvjitlink、nvshmem

### 🟢 坑 4：叠加文件系统导致 import 慢

**症状：** `python -c "import transformers"` 挂起几十秒。

**根因：** 叠加 FS 对大量小文件的 `_path_stat` 调用性能极差。

**修复：** 用文件模式运行脚本，不要用 `python -c`。训练脚本作为 `.py` 文件执行。

### 🟢 坑 5：后台进程的输出缓冲

**症状：** `terminal(background=true)` 启动的训练只显示开头几行日志，后续进度看不到。

**根因：** Python 的 stdout 在管道环境默认全缓冲。

**修复：**
```bash
python -u train_script.py           # -u 关闭缓冲
```
并在脚本中设置 `buffering=1`（行缓冲）写入日志文件。

### 🟢 坑 6：Docker C 盘膨胀

**症状：** 训练一次，C 盘 Docker ext4.vhdx 膨胀 13-50GB。删了容器内文件也不回收。

**根因：** WSL2 虚拟磁盘只增不减。

**修复（Windows）：**
```
# PowerShell 管理员
wsl --shutdown
diskpart
  select vdisk file="C:\Users\<user>\AppData\Local\Docker\wsl\data\ext4.vhdx"
  attach vdisk readonly
  compact vdisk
  detach vdisk
exit
```

### 🟢 坑 7：Blackwell GPU 训练兼容性

**症状：** `RuntimeError: CUDA driver error: device not ready` —— 注意力/前馈层首次前向传播崩溃。

**根因：** PyTorch 2.10 对 Blackwell (sm_120) 的训练支持不完整。推理正常，训练可能有兼容问题。

**状态：** 本次训练全程跑通（100 步无此错误），但没有在其他 workload（SDXL LoRA 等）上验证。

---

## 四、训练结果

| 检查点 | Epoch | Eval Loss | 语言质量 | 选择理由 |
|--------|-------|-----------|---------|---------|
| checkpoint-20 | 4 | ~2.2 | 尚可 | 起始点 |
| **checkpoint-40** | **8** | **2.179（最低）** | **语言最自然** | ✅ **最终选择** |
| checkpoint-60 | 12 | ~2.3 | 开始过拟合 | |
| checkpoint-100 (final) | 20 | ~0.1 | 语言僵硬、数据密度高但啰嗦 | ❌ 过拟合 |

**关键发现：** 最低 eval loss 的 checkpoint（#40）产生了最好的生成质量。继续训练虽然 loss 更低，但语言变得僵硬。

选择标准：**语言质量 > 数据密度**。

---

## 五、推理速度

| 部署方式 | 加载时间 | 推理速度 |
|---------|---------|---------|
| 4bit torch（transformers） | ~2.5 分钟 | ~15-20 t/s |
| 合并后 Q4 GGUF（llama.cpp） | ~10 秒 | ~30-50 t/s |

如果需要频繁使用，建议合并 LoRA → 转 GGUF → llama.cpp 部署。

---

## 六、训练数据铁律

```
续训只用原文，不用 LLM 生成的平行语料。
风格迁移靠学习原文特征，不是靠"仿冒"。
```

这句不是建议，是这条管线的基础假设。

---

## 七、参考

- 训练脚本：`/opt/data/scripts/continued_pretrain_qwen3.py`
- 推理脚本：`/opt/data/scripts/infer_qwen3.py`
- LoRA 适配器：`/opt/data/output/qwen3-cpt-output/final-cp40/`
- 环境搭建技能：`consumer-gpu-tuning`
