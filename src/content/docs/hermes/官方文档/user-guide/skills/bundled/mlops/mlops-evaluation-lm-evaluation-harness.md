---
title: Evaluation Lm Evaluation Harness
---

title: "评估LLMs的Harness — lm-eval-harness：基准测试LLMs（MMLU、GSM8K等）"
sidebar_label: "评估LLMs的Harness"
description: "lm-eval-harness：基准测试LLMs（MMLU、GSM8K等）"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能（Skill）的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 评估LLMs的Harness

lm-eval-harness：基准测试大语言模型（LLMs）（MMLU、GSM8K等）。

## 技能（Skill）元数据

| | |
|---|---|
| 来源 | 捆绑（默认安装） |
| 路径 | `skills/mlops/evaluation/lm-evaluation-harness` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可协议 | MIT |
| 依赖 | `lm-eval`, `transformers`, `vllm` |
| 平台 | linux, macos |
| 标签 | `Evaluation`, `LM Evaluation Harness`, `Benchmarking`, `MMLU`, `HumanEval`, `GSM8K`, `EleutherAI`, `Model Quality`, `Academic Benchmarks`, `Industry Standard` |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，代理（Agent）会看到这些指令。
:::

# lm-evaluation-harness - LLM基准测试

## 内含内容

评估大语言模型（LLMs）在60多项学术基准（MMLU、HumanEval、GSM8K、TruthfulQA、HellaSwag）上的表现。用于基准测试模型质量、比较模型、报告学术结果或跟踪训练进度。这是EleutherAI、HuggingFace及主要实验室使用的行业标准。支持HuggingFace、vLLM、API。

## 快速开始

lm-evaluation-harness使用标准化提示（prompts）和指标评估大语言模型（LLMs）在60多项学术基准上的表现。

**安装**：
```bash
pip install lm-eval
```

**评估任意HuggingFace模型**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu,gsm8k,hellaswag \
  --device cuda:0 \
  --batch_size 8
```

**查看可用任务**：
```bash
lm_eval --tasks list
```

## 常见工作流程

### 工作流程1：标准基准评估

在核心基准（MMLU、GSM8K、HumanEval）上评估模型。

复制此检查清单：

```
基准评估：
- [ ] 步骤1：选择基准套件
- [ ] 步骤2：配置模型
- [ ] 步骤3：运行评估
- [ ] 步骤4：分析结果
```

**步骤1：选择基准套件**

**核心推理基准**：
- **MMLU**（大规模多任务语言理解）- 57个科目，多项选择
- **GSM8K** - 小学数学应用题
- **HellaSwag** - 常识推理
- **TruthfulQA** - 真实性与事实性
- **ARC**（AI2推理挑战）- 科学问题

**代码基准**：
- **HumanEval** - Python代码生成（164个问题）
- **MBPP**（主要基础Python问题）- Python编码

**标准套件**（推荐用于模型发布）：
```bash
--tasks mmlu,gsm8k,hellaswag,truthfulqa,arc_challenge
```

**步骤2：配置模型**

**HuggingFace模型**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf,dtype=bfloat16 \
  --tasks mmlu \
  --device cuda:0 \
  --batch_size auto  # 自动检测最佳批大小
```

**量化模型（4位/8位）**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf,load_in_4bit=True \
  --tasks mmlu \
  --device cuda:0
```

**自定义检查点**：
```bash
lm_eval --model hf \
  --model_args pretrained=/path/to/my-model,tokenizer=/path/to/tokenizer \
  --tasks mmlu \
  --device cuda:0
```

**步骤3：运行评估**

```bash
# 完整MMLU评估（57个科目）
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu \
  --num_fewshot 5 \  # 5-shot评估（标准）
  --batch_size 8 \
  --output_path results/ \
  --log_samples  # 保存单个预测

# 同时评估多个基准
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu,gsm8k,hellaswag,truthfulqa,arc_challenge \
  --num_fewshot 5 \
  --batch_size 8 \
  --output_path results/llama2-7b-eval.json
```

**步骤4：分析结果**

结果保存至 `results/llama2-7b-eval.json`：

```json
{
  "results": {
    "mmlu": {
      "acc": 0.459,
      "acc_stderr": 0.004
    },
    "gsm8k": {
      "exact_match": 0.142,
      "exact_match_stderr": 0.006
    },
    "hellaswag": {
      "acc_norm": 0.765,
      "acc_norm_stderr": 0.004
    }
  },
  "config": {
    "model": "hf",
    "model_args": "pretrained=meta-llama/Llama-2-7b-hf",
    "num_fewshot": 5
  }
}
```

### 工作流程2：跟踪训练进度

在训练期间评估检查点。

```
训练进度跟踪：
- [ ] 步骤1：设置定期评估
- [ ] 步骤2：选择快速基准
- [ ] 步骤3：自动化评估
- [ ] 步骤4：绘制学习曲线
```

**步骤1：设置定期评估**

每N个训练步评估一次：

```bash
#!/bin/bash
# eval_checkpoint.sh

CHECKPOINT_DIR=$1
STEP=$2

lm_eval --model hf \
  --model_args pretrained=$CHECKPOINT_DIR/checkpoint-$STEP \
  --tasks gsm8k,hellaswag \
  --num_fewshot 0 \  # 0-shot以提速
  --batch_size 16 \
  --output_path results/step-$STEP.json
```

**步骤2：选择快速基准**

适合频繁评估的快速基准：
- **HellaSwag**：单GPU约10分钟
- **GSM8K**：约5分钟
- **PIQA**：约2分钟

避免用于频繁评估（太慢）：
- **MMLU**：约2小时（57个科目）
- **HumanEval**：需要执行代码

**步骤3：自动化评估**

集成到训练脚本中：

```python
# 训练循环中
if step % eval_interval == 0:
    model.save_pretrained(f"checkpoints/step-{step}")

    # 运行评估
    os.system(f"./eval_checkpoint.sh checkpoints step-{step}")
```

或者使用PyTorch Lightning回调：

```python
from pytorch_lightning import Callback

class EvalHarnessCallback(Callback):
    def on_validation_epoch_end(self, trainer, pl_module):
        step = trainer.global_step
        checkpoint_path = f"checkpoints/step-{step}"

        # 保存检查点
        trainer.save_checkpoint(checkpoint_path)

        # 运行lm-eval
        os.system(f"lm_eval --model hf --model_args pretrained={checkpoint_path} ...")
```

**步骤4：绘制学习曲线**

```python
import json
import matplotlib.pyplot as plt

# 加载所有结果
steps = []
mmlu_scores = []

for file in sorted(glob.glob("results/step-*.json")):
    with open(file) as f:
        data = json.load(f)
        step = int(file.split("-")[1].split(".")[0])
        steps.append(step)
        mmlu_scores.append(data["results"]["mmlu"]["acc"])

# 绘图
plt.plot(steps, mmlu_scores)
plt.xlabel("训练步数")
plt.ylabel("MMLU准确率")
plt.title("训练进度")
plt.savefig("training_curve.png")
```

### 工作流程3：比较多个模型

用于模型比较的基准套件。

```
模型比较：
- [ ] 步骤1：定义模型列表
- [ ] 步骤2：运行评估
- [ ] 步骤3：生成比较表格
```

**步骤1：定义模型列表**

```bash
# models.txt
meta-llama/Llama-2-7b-hf
meta-llama/Llama-2-13b-hf
mistralai/Mistral-7B-v0.1
microsoft/phi-2
```

**步骤2：运行评估**

```bash
#!/bin/bash
# eval_all_models.sh

TASKS="mmlu,gsm8k,hellaswag,truthfulqa"

while read model; do
    echo "正在评估 $model"

    # 提取模型名称用于输出文件
    model_name=$(echo $model | sed 's/\//-/g')

    lm_eval --model hf \
      --model_args pretrained=$model,dtype=bfloat16 \
      --tasks $TASKS \
      --num_fewshot 5 \
      --batch_size auto \
      --output_path results/$model_name.json

done < models.txt
```

**步骤3：生成比较表格**

```python
import json
import pandas as pd

models = [
    "meta-llama-Llama-2-7b-hf",
    "meta-llama-Llama-2-13b-hf",
    "mistralai-Mistral-7B-v0.1",
    "microsoft-phi-2"
]

tasks = ["mmlu", "gsm8k", "hellaswag", "truthfulqa"]

results = []
for model in models:
    with open(f"results/{model}.json") as f:
        data = json.load(f)
        row = {"模型": model.replace("-", "/")}
        for task in tasks:
            # 获取每个任务的主要指标
            metrics = data["results"][task]
            if "acc" in metrics:
                row[task.upper()] = f"{metrics['acc']:.3f}"
            elif "exact_match" in metrics:
                row[task.upper()] = f"{metrics['exact_match']:.3f}"
        results.append(row)

df = pd.DataFrame(results)
print(df.to_markdown(index=False))
```

输出：
```
| 模型                  | MMLU  | GSM8K | HELLASWAG | TRUTHFULQA |
|------------------------|-------|-------|-----------|------------|
| meta-llama/Llama-2-7b  | 0.459 | 0.142 | 0.765     | 0.391      |
| meta-llama/Llama-2-13b | 0.549 | 0.287 | 0.801     | 0.430      |
| mistralai/Mistral-7B   | 0.626 | 0.395 | 0.812     | 0.428      |
| microsoft/phi-2        | 0.560 | 0.613 | 0.682     | 0.447      |
```

### 工作流程4：使用vLLM评估（更快的推理）

使用vLLM后端进行5-10倍更快的评估。

```
vLLM评估：
- [ ] 步骤1：安装vLLM
- [ ] 步骤2：配置vLLM后端
- [ ] 步骤3：运行评估
```

**步骤1：安装vLLM**

```bash
pip install vllm
```

**步骤2：配置vLLM后端**

```bash
lm_eval --model vllm \
  --model_args pretrained=meta-llama/Llama-2-7b-hf,tensor_parallel_size=1,dtype=auto,gpu_memory_utilization=0.8 \
  --tasks mmlu \
  --batch_size auto
```

**步骤3：运行评估**

vLLM比标准HuggingFace快5-10倍：

```bash
# 标准HF：7B模型MMLU约2小时
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu \
  --batch_size 8

# vLLM：7B模型MMLU约15-20分钟
lm_eval --model vllm \
  --model_args pretrained=meta-llama/Llama-2-7b-hf,tensor_parallel_size=2 \
  --tasks mmlu \
  --batch_size auto
```

## 何时使用 vs 替代方案

**使用lm-evaluation-harness的情况：**
- 为学术论文基准测试模型
- 比较标准任务上的模型质量
- 跟踪训练进度
- 报告标准化指标（所有人使用相同提示）
- 需要可复现的评估

**使用替代方案的情况：**
- **HELM**（斯坦福）：更广泛的评估（公平性、效率、校准）
- **AlpacaEval**：使用LLM评判器进行指令遵循评估
- **MT-Bench**：对话式多轮评估
- **自定义脚本**：领域特定评估

## 常见问题

**问题：评估太慢**

使用vLLM后端：
```bash
lm_eval --model vllm \
  --model_args pretrained=model-name,tensor_parallel_size=2
```

或者减少fewshot示例：
```bash
--num_fewshot 0  # 代替5
```

或者评估MMLU子集：
```bash
--tasks mmlu_stem  # 仅STEM科目
```

**问题：内存不足**

减少批大小：
```bash
--batch_size 1  # 或 --batch_size auto
```

使用量化：
```bash
--model_args pretrained=model-name,load_in_8bit=True
```

启用CPU卸载：
```bash
--model_args pretrained=model-name,device_map=auto,offload_folder=offload
```

**问题：结果与报告不同**

检查fewshot计数：
```bash
--num_fewshot 5  # 大多数论文使用5-shot
```

检查确切任务名称：
```bash
--tasks mmlu  # 不是 mmlu_direct 或 mmlu_fewshot
```

验证模型和分词器匹配：
```bash
--model_args pretrained=model-name,tokenizer=same-model-name
```

**问题：HumanEval未执行代码**

安装执行依赖：
```bash
pip install human-eval
```

启用代码执行：
```bash
lm_eval --model hf \
  --model_args pretrained=model-name \
  --tasks humaneval \
  --allow_code_execution  # HumanEval必需
```

## 高级主题

**基准描述**：参见[references/benchmark-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/evaluation/lm-evaluation-harness/references/benchmark-guide.md)以获取所有60多个任务的详细描述、测量内容及解释。

**自定义任务**：参见[references/custom-tasks.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/evaluation/lm-evaluation-harness/references/custom-tasks.md)了解如何创建领域特定的评估任务。

**API评估**：参见[references/api-evaluation.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/evaluation/lm-evaluation-harness/references/api-evaluation.md)了解如何评估OpenAI、Anthropic及其他API模型。

**多GPU策略**：参见[references/distributed-eval.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/evaluation/lm-evaluation-harness/references/distributed-eval.md)了解数据并行和张量并行评估。

## 硬件要求

- **GPU**：NVIDIA（CUDA 11.8+），可在CPU上运行（非常慢）
- **显存**：
  - 7B模型：16GB（bf16）或8GB（8-bit）
  - 13B模型：28GB（bf16）或14GB（8-bit）
  - 70B模型：需要多GPU或量化
- **时间**（7B模型，单A100）：
  - HellaSwag：10分钟
  - GSM8K：5分钟
  - MMLU（完整）：2小时
  - HumanEval：20分钟

## 资源

- GitHub：https://github.com/EleutherAI/lm-evaluation-harness
- 文档：https://github.com/EleutherAI/lm-evaluation-harness/tree/main/docs
- 任务库：60多个任务，包括MMLU、GSM8K、HumanEval、TruthfulQA、HellaSwag、ARC、WinoGrande等
- 排行榜：https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard（使用此框架）