---
sidebar_position: 12
title: "批处理"
description: "大规模生成代理轨迹——并行处理、检查点和工具集分布"
---

# 批处理

批处理（Batch Processing）让你能够并行运行 Hermes 智能体（Agent）处理成百上千个提示词，生成结构化的轨迹（trajectory）数据。这主要用于**训练数据生成**——生成包含工具使用统计的 ShareGPT 格式轨迹，可用于微调或评估。

## 概述

批处理运行器（`batch_runner.py`）处理一个 JSONL 格式的提示词数据集，通过一个完整的智能体会话（带工具访问权限）逐个运行每个提示词。每个提示词拥有独立的隔离环境。输出是结构化的轨迹数据，包含完整的对话历史、工具调用统计和推理覆盖度指标。

## 快速开始

```bash
# 基础批处理运行
python batch_runner.py \
    --dataset_file=data/prompts.jsonl \
    --batch_size=10 \
    --run_name=my_first_run \
    --model=anthropic/claude-sonnet-4.6 \
    --num_workers=4

# 恢复中断的运行
python batch_runner.py \
    --dataset_file=data/prompts.jsonl \
    --batch_size=10 \
    --run_name=my_first_run \
    --resume

# 列出可用的工具集分布
python batch_runner.py --list_distributions
```

:::tip 可预测的大规模成本
批处理运行会启动多个并发智能体会话，每个会话都会产生模型调用和工具调用。通过 [Nous Portal](/user-guide/features/tool-gateway) 订阅，可以将模型访问权限与网页搜索、图像生成、TTS 和云浏览器捆绑在同一账单下——当您希望每个轨迹的成本稳定，而无需在五个厂商账户间协调速率限制时，这非常有用。使用 `hermes setup --portal` 进行设置，然后通过 `--model` 指向一个 Nous 模型。
:::

## 数据集格式

输入数据集是一个 JSONL 文件（每行一个 JSON 对象）。每个条目必须包含一个 `prompt` 字段：

```jsonl
{"prompt": "Write a Python function that finds the longest palindromic substring"}
{"prompt": "Create a REST API endpoint for user authentication using Flask"}
{"prompt": "Debug this error: TypeError: cannot unpack non-iterable NoneType object"}
```

条目可以可选地包含：
- `image` 或 `docker_image`：用于该提示词沙盒的容器镜像（支持 Docker、Modal 和 Singularity 后端）
- `cwd`：任务终端会话的工作目录重写

## 配置选项

| 参数 | 默认值 | 描述 |
|-----------|---------|-------------|
| `--dataset_file` | (必填) | JSONL 数据集的路径 |
| `--batch_size` | (必填) | 每批的提示词数量 |
| `--run_name` | (必填) | 本次运行的名称（用于输出目录和检查点） |
| `--distribution` | `"default"` | 从中抽样的工具集分布 |
| `--model` | `claude-sonnet-4.6` | 使用的模型 |
| `--base_url` | `https://openrouter.ai/api/v1` | API 基础 URL |
| `--api_key` | (环境变量) | 模型的 API 密钥 |
| `--max_turns` | `10` | 每个提示词的最大工具调用迭代次数 |
| `--num_workers` | `4` | 并行工作进程数 |
| `--resume` | `false` | 从检查点恢复 |
| `--verbose` | `false` | 启用详细日志输出 |
| `--max_samples` | 全部 | 仅处理数据集中的前 N 个样本 |
| `--max_tokens` | 模型默认值 | 每个模型响应的最大令牌数 |

### 提供商路由（OpenRouter）

| 参数 | 描述 |
|-----------|-------------|
| `--providers_allowed` | 允许的提供商列表（逗号分隔），例如 `"anthropic,openai"` |
| `--providers_ignored` | 忽略的提供商列表（逗号分隔），例如 `"together,deepinfra"` |
| `--providers_order` | 首选提供商顺序列表（逗号分隔） |
| `--provider_sort` | 按 `"price"`、`"throughput"` 或 `"latency"` 排序 |

### 推理控制

| 参数 | 描述 |
|-----------|-------------|
| `--reasoning_effort` | 努力级别：`none`、`minimal`、`low`、`medium`、`high`、`xhigh` |
| `--reasoning_disabled` | 完全禁用推理/思考令牌 |

### 高级选项

| 参数 | 描述 |
|-----------|-------------|
| `--ephemeral_system_prompt` | 执行期间使用但**不**保存到轨迹中的系统提示词 |
| `--log_prefix_chars` | 日志预览中显示的字符数（默认：100） |
| `--prefill_messages_file` | 预填充消息 JSON 文件路径，用于少样本预热 |

## 工具集分布

每个提示词都会从一个**分布**中随机抽取一组工具集。这确保了训练数据涵盖多样的工具组合。使用 `--list_distributions` 查看所有可用的分布。

在当前实现中，分布为**每个单独的工具集**分配一个概率。采样器独立地翻转每个工具集，然后保证至少有一个工具集被启用。这与手工编写的预构建组合表不同。

## 输出格式

所有输出都放到 `data/<run_name>/` 目录下：

```text
data/my_run/
├── trajectories.jsonl    # 合并后的最终输出（所有批次合并）
├── batch_0.jsonl         # 单个批次结果
├── batch_1.jsonl
├── ...
├── checkpoint.json       # 恢复检查点
└── statistics.json       # 聚合的工具使用统计
```

### 轨迹格式

`trajectories.jsonl` 中的每一行都是一个 JSON 对象：

```json
{
  "prompt_index": 42,
  "conversations": [
    {"from": "human", "value": "Write a function..."},
    {"from": "gpt", "value": "I'll create that function...",
     "tool_calls": [...]},
    {"from": "tool", "value": "..."},
    {"from": "gpt", "value": "Here's the completed function..."}
  ],
  "metadata": {
    "batch_num": 2,
    "timestamp": "2026-01-15T10:30:00",
    "model": "anthropic/claude-sonnet-4.6"
  },
  "completed": true,
  "partial": false,
  "api_calls": 3,
  "toolsets_used": ["terminal", "file"],
  "tool_stats": {
    "terminal": {"count": 2, "success": 2, "failure": 0},
    "read_file": {"count": 1, "success": 1, "failure": 0}
  },
  "tool_error_counts": {
    "terminal": 0,
    "read_file": 0
  }
}
```

`conversations` 字段使用类似 ShareGPT 的格式，包含 `from` 和 `value` 字段。工具统计数据已归一化，包括所有可能的工具并以零作为默认值，确保跨条目的一致性架构，以兼容 HuggingFace 数据集。

## 检查点

批处理运行器具有强大的检查点功能，可实现容错：

- **检查点文件**：每批完成后保存，跟踪哪些提示词索引已完成
- **基于内容的恢复**：使用 `--resume` 时，运行器会扫描现有的批次文件，并根据实际文本内容（不仅仅是索引）匹配已完成的提示词，即使数据集顺序发生变化也能恢复
- **失败提示词**：仅成功完成的提示词被标记为完成——失败提示词将在恢复时重试
- **批次合并**：完成后，所有批次文件（包括之前运行中的）被合并到一个 `trajectories.jsonl` 中

### 恢复如何工作

1. 扫描所有 `batch_*.jsonl` 文件中已完成的提示词（通过内容匹配）
2. 过滤数据集，排除已完成的提示词
3. 对剩余的提示词重新分批
4. 仅处理剩余的提示词
5. 将所有批次文件（旧 + 新）合并为最终输出

## 质量过滤

批处理运行器会自动应用质量过滤：

- **无推理过滤**：丢弃那些零个助手（assistant）轮次包含推理的样本（没有 `<REASONING_SCRATCHPAD>` 或原生思考令牌）
- **损坏条目过滤**：在最终合并时，过滤掉包含幻觉工具名称（不在有效工具列表中）的条目
- **推理统计**：跟踪整个运行中带有/不带推理的轮次百分比

## 统计数据

运行完成后，运行器会打印全面的统计信息：

- **工具使用**：每个工具的调用次数、成功/失败率
- **推理覆盖度**：包含推理的助手轮次百分比
- **丢弃的样本数**：因缺乏推理而被过滤的样本计数
- **持续时间**：总处理时间

统计数据也会保存到 `statistics.json`，供程序化分析使用。

## 用例

### 训练数据生成

为微调生成多样化的工具使用轨迹：

```bash
python batch_runner.py \
    --dataset_file=data/coding_prompts.jsonl \
    --batch_size=20 \
    --run_name=coding_v1 \
    --model=anthropic/claude-sonnet-4.6 \
    --num_workers=8 \
    --distribution=default \
    --max_turns=15
```

### 模型评估

评估模型在标准化提示词上的工具使用能力：

```bash
python batch_runner.py \
    --dataset_file=data/eval_suite.jsonl \
    --batch_size=10 \
    --run_name=eval_gpt4 \
    --model=openai/gpt-4o \
    --num_workers=4 \
    --max_turns=10
```

### 每个提示词指定容器镜像

对于需要特定环境的基准测试，每个提示词可以指定自己的容器镜像：

```jsonl
{"prompt": "Install numpy and compute eigenvalues of a 3x3 matrix", "image": "python:3.11-slim"}
{"prompt": "Compile this Rust program and run it", "image": "rust:1.75"}
{"prompt": "Set up a Node.js Express server", "image": "node:20-alpine", "cwd": "/app"}
```

批处理运行器会在运行每个提示词之前验证 Docker 镜像是否可访问。