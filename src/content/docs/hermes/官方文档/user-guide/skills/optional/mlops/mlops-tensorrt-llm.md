```markdown
---
title: "Tensorrt Llm — 使用 NVIDIA TensorRT 优化 LLM 推理，实现最大吞吐量和最低延迟"
sidebar_label: "Tensorrt Llm"
description: "使用 NVIDIA TensorRT 优化 LLM 推理，实现最大吞吐量和最低延迟"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

# Tensorrt Llm

使用 NVIDIA TensorRT 优化 LLM 推理，实现最大吞吐量和最低延迟。适用于在 NVIDIA GPU（A100/H100）上进行生产部署，当您需要比 PyTorch 快 10-100 倍的推理速度时，或用于通过量化（FP8/INT4）、飞行中批处理（in-flight batching）和多 GPU 扩展来服务模型。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/tensorrt-llm` 安装 |
| 路径 | `optional-skills/mlops/tensorrt-llm` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可协议 | MIT |
| 依赖项 | `tensorrt-llm`, `torch` |
| 平台 | linux, macos |
| 标签 | `Inference Serving`, `TensorRT-LLM`, `NVIDIA`, `Inference Optimization`, `High Throughput`, `Low Latency`, `Production`, `FP8`, `INT4`, `In-Flight Batching`, `Multi-GPU` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时代理看到的指令。
:::

# TensorRT-LLM

NVIDIA 的开源库，用于在 NVIDIA GPU 上以最先进的性能优化 LLM 推理。

## 何时使用 TensorRT-LLM

**在以下情况使用 TensorRT-LLM：**
- 在 NVIDIA GPU（A100, H100, GB200）上部署
- 需要最大吞吐量（Llama 3 上每秒超过 24,000 个 token）
- 对实时应用要求低延迟
- 处理量化模型（FP8, INT4, FP4）
- 跨多个 GPU 或节点扩展

**在以下情况改用 vLLM：**
- 需要更简单的设置和以 Python 为先的 API
- 需要 PagedAttention 但无需 TensorRT 编译
- 使用 AMD GPU 或非 NVIDIA 硬件

**在以下情况改用 llama.cpp：**
- 在 CPU 或 Apple Silicon 上部署
- 需要边缘部署且无 NVIDIA GPU
- 需要更简单的 GGUF 量化格式

## 快速开始

### 安装

```bash
# Docker（推荐）
docker pull nvidia/tensorrt_llm:latest

# pip 安装
pip install tensorrt_llm==1.2.0rc3

# 需要 CUDA 13.0.0, TensorRT 10.13.2, Python 3.10-3.12
```

### 基本推理

```python
from tensorrt_llm import LLM, SamplingParams

# 初始化模型
llm = LLM(model="meta-llama/Meta-Llama-3-8B")

# 配置采样参数
sampling_params = SamplingParams(
    max_tokens=100,
    temperature=0.7,
    top_p=0.9
)

# 生成
prompts = ["解释量子计算"]
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(output.text)
```

### 使用 trtllm-serve 服务

```bash
# 启动服务器（自动下载和编译模型）
trtllm-serve meta-llama/Meta-Llama-3-8B \
    --tp_size 4 \              # 张量并行（4 GPU）
    --max_batch_size 256 \
    --max_num_tokens 4096

# 客户端请求
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3-8B",
    "messages": [{"role": "user", "content": "你好！"}],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

## 关键特性

### 性能优化
- **飞行中批处理（In-flight batching）**：生成过程中动态批处理
- **分页 KV 缓存（Paged KV cache）**：高效内存管理
- **Flash Attention**：优化的注意力内核
- **量化**：FP8, INT4, FP4，实现 2-4 倍更快的推理
- **CUDA graphs**：减少内核启动开销

### 并行性
- **张量并行（Tensor parallelism, TP）**：跨 GPU 拆分模型
- **流水线并行（Pipeline parallelism, PP）**：按层分布
- **专家并行（Expert parallelism）**：用于混合专家模型
- **多节点（Multi-node）**：扩展至单机之外

### 高级特性
- **推测解码（Speculative decoding）**：使用草稿模型实现更快的生成
- **LoRA 服务（LoRA serving）**：高效的多适配器部署
- **分离式服务（Disaggregated serving）**：分离预填充和生成阶段

## 常见模式

### 量化模型（FP8）

```python
from tensorrt_llm import LLM

# 加载 FP8 量化模型（2 倍速度，50% 内存节省）
llm = LLM(
    model="meta-llama/Meta-Llama-3-70B",
    dtype="fp8",
    max_num_tokens=8192
)

# 推理方式同之前
outputs = llm.generate(["总结本文..."])
```

### 多 GPU 部署

```python
# 跨 8 个 GPU 的张量并行
llm = LLM(
    model="meta-llama/Meta-Llama-3-405B",
    tensor_parallel_size=8,
    dtype="fp8"
)
```

### 批量推理

```python
# 高效处理 100 个提示
prompts = [f"问题 {i}: ..." for i in range(100)]

outputs = llm.generate(
    prompts,
    sampling_params=SamplingParams(max_tokens=200)
)

# 自动飞行中批处理以获得最大吞吐量
```

## 性能基准

**Meta Llama 3-8B**（H100 GPU）：
- 吞吐量：24,000 tokens/秒
- 延迟：每 token 约 10ms
- 对比 PyTorch：**快 100 倍**

**Llama 3-70B**（8× A100 80GB）：
- FP8 量化：比 FP16 快 2 倍
- 内存：FP8 减少 50%

## 支持的模型

- **LLaMA 系列**：Llama 2, Llama 3, CodeLlama
- **GPT 系列**：GPT-2, GPT-J, GPT-NeoX
- **Qwen**：Qwen, Qwen2, QwQ
- **DeepSeek**：DeepSeek-V2, DeepSeek-V3
- **Mixtral**：Mixtral-8x7B, Mixtral-8x22B
- **视觉**：LLaVA, Phi-3-vision
- **HuggingFace 上 100+ 模型**

## 参考

- **[优化指南](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/tensorrt-llm/references/optimization.md)** — 量化、批处理、KV 缓存调优
- **[多 GPU 设置](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/tensorrt-llm/references/multi-gpu.md)** — 张量/流水线并行、多节点
- **[服务指南](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/tensorrt-llm/references/serving.md)** — 生产部署、监控、自动缩放

## 资源

- **文档**：https://nvidia.github.io/TensorRT-LLM/
- **GitHub**：https://github.com/NVIDIA/TensorRT-LLM
- **模型**：https://huggingface.co/models?library=tensorrt_llm
```