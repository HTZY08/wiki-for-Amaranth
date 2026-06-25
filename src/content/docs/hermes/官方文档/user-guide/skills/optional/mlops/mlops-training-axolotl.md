--- frontmatter ---
---
title: "Axolotl — Axolotl：YAML LLM 微调（LoRA, DPO, GRPO）"
sidebar_label: "Axolotl"
description: "Axolotl：YAML LLM 微调（LoRA, DPO, GRPO）"
---

--- body ---
{/* 本页面由网站脚本 generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

# Axolotl

Axolotl：YAML LLM 微调（LoRA, DPO, GRPO）。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源（Source） | 可选（Optional）—— 通过 `hermes skills install official/mlops/axolotl` 安装 |
| 路径（Path） | `optional-skills/mlops/training/axolotl` |
| 版本（Version） | `1.0.0` |
| 作者（Author） | Orchestra Research |
| 许可证（License） | MIT |
| 依赖（Dependencies） | `axolotl`, `torch`, `transformers`, `datasets`, `peft`, `accelerate`, `deepspeed` |
| 平台（Platforms） | linux, macos |
| 标签（Tags） | `Fine-Tuning`、`Axolotl`、`LLM`、`LoRA`、`QLoRA`、`DPO`、`KTO`、`ORPO`、`GRPO`、`YAML`、`HuggingFace`、`DeepSpeed`、`多模态（Multimodal）` |

## 参考资料：完整 SKILL.md

:::info
以下为 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，代理（Agent）将其视为指令。
:::

# Axolotl 技能

## 包含内容

使用 Axolotl 进行 LLM 微调的专业指导——YAML 配置、100+ 模型、LoRA/QLoRA、DPO/KTO/ORPO/GRPO、多模态支持。

基于官方文档生成的 Axolotl 开发全面帮助。

## 何时使用此技能

在以下情况下应触发此技能：
- 使用 axolotl 时
- 询问 axolotl 功能或 API 时
- 实现 axolotl 解决方案时
- 调试 axolotl 代码时
- 学习 axolotl 最佳实践时

## 快速参考

### 常见模式

**模式 1：** 为了验证训练任务是否存在可接受的数据传输速度，运行 NCCL 测试有助于定位瓶颈，例如：

```
./build/all_reduce_perf -b 8 -e 128M -f 2 -g 3
```

**模式 2：** 在 Axolotl yaml 中配置模型使用 FSDP。例如：

```
fsdp_version: 2
fsdp_config:
  offload_params: true
  state_dict_type: FULL_STATE_DICT
  auto_wrap_policy: TRANSFORMER_BASED_WRAP
  transformer_layer_cls_to_wrap: LlamaDecoderLayer
  reshard_after_forward: true
```

**模式 3：** `context_parallel_size` 应为 GPU 总数的除数。例如：

```
context_parallel_size
```

**模式 4：** 例如：
- 使用 8 个 GPU 且无序列并行：每步处理 8 个不同的批次
- 使用 8 个 GPU 且 context_parallel_size=4：每步仅处理 2 个不同的批次（每个批次分布在 4 个 GPU 上）
- 如果每个 GPU 的 micro_batch_size 为 2，则全局 batch size 从 16 减少到 4

```
context_parallel_size=4
```

**模式 5：** 在配置中设置 `save_compressed: true` 可启用压缩格式保存模型，这将：
- 减少约 40% 的磁盘空间占用
- 保持与 vLLM 的兼容性以加速推理
- 保持与 llmcompressor 的兼容性以便进一步优化（例如量化）

```
save_compressed: true
```

**模式 6：** 注意：不必将集成放在 integrations 文件夹中。它可以放在任何位置，只要安装在 Python 环境的包中即可。示例请参见此仓库：https://github.com/axolotl-ai-cloud/diff-transformer

```
integrations
```

**模式 7：** 处理单样本和批量数据。
- 单样本：sample['input_ids'] 为 list[int]
- 批量数据：sample['input_ids'] 为 list[list[int]]

```
utils.trainer.drop_long_seq(sample, sequence_len=2048, min_sequence_len=2)
```

### 示例代码模式

**示例 1**（python）：
```python
cli.cloud.modal_.ModalCloud(config, app=None)
```

**示例 2**（python）：
```python
cli.cloud.modal_.run_cmd(cmd, run_folder, volumes=None)
```

**示例 3**（python）：
```python
core.trainers.base.AxolotlTrainer(
    *_args,
    bench_data_collator=None,
    eval_data_collator=None,
    dataset_tags=None,
    **kwargs,
)
```

**示例 4**（python）：
```python
core.trainers.base.AxolotlTrainer.log(logs, start_time=None)
```

**示例 5**（python）：
```python
prompt_strategies.input_output.RawInputOutputPrompter()
```

## 参考文件

此技能包含 `references/` 目录下的全面文档：

- **api.md** - API 文档
- **dataset-formats.md** - 数据集格式（Dataset-Formats）文档
- **other.md** - 其他文档

需要详细信息时，请使用 `view` 读取特定的参考文件。

## 使用此技能

### 对于初学者
从入门指南（getting_started）或教程参考文件开始，了解基础概念。

### 对于特定功能
使用相应类别的参考文件（api、guides 等）获取详细信息。

### 对于代码示例
上述快速参考部分包含了从官方文档中提取的常见模式。

## 资源

### references/
从官方来源提取的整理文档。这些文件包含：
- 详细说明
- 带语言标注的代码示例
- 原始文档链接
- 快速导航目录

### scripts/
在此添加辅助脚本，用于常见自动化任务。

### assets/
在此添加模板、样板文件或示例项目。

## 备注

- 此技能从官方文档自动生成
- 参考文件保留了源文档的结构和示例
- 代码示例包含语言检测以便更好地语法高亮
- 快速参考模式从文档中的常见用法示例中提取

## 更新

要用更新后的文档刷新此技能：
1. 使用相同配置重新运行抓取器
2. 技能将使用最新信息重建