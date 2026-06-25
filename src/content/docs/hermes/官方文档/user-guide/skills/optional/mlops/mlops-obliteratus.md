--- frontmatter ---


--- body ---
# Obliteratus

OBLITERATUS：清除LLM拒绝行为（均值差异法）

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/obliteratus` 安装 |
| 路径 | `optional-skills/mlops/obliteratus` |
| 版本 | `2.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 依赖项 | `obliteratus`、`torch`、`transformers`、`bitsandbytes`、`accelerate`、`safetensors` |
| 支持平台 | linux, macos |
| 标签 | `Abliteration`、`Uncensoring`、`Refusal-Removal`、`LLM`、`Weight-Projection`、`SVD`、`Mechanistic-Interpretability`、`HuggingFace`、`Model-Surgery` |
| 相关技能 | `vllm`、`gguf`、[`huggingface-tokenizers`](/docs/user-guide/skills/optional/mlops/mlops-huggingface-tokenizers) |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时代理看到的指令。
:::

# OBLITERATUS 技能

## 内部包含

9 个 CLI 方法，28 个分析模块，116 个模型预设（覆盖 5 个计算层级），锦标赛评估以及遥测驱动的推荐。

在不进行重新训练或微调的情况下，从开放权重的 LLM 中移除拒绝行为（护栏）。使用机制可解释性技术——包括均值差异法（diff-in-means）、SVD（奇异值分解）、白化 SVD、LEACE（闭式线性擦除）、SAE（稀疏自编码器）分解、贝叶斯核投影等——来识别并从模型权重中精确切除拒绝方向，同时保留推理能力。

**许可证警告：** OBLITERATUS 使用 AGPL-3.0 许可证。切勿将其作为 Python 库导入。始终通过 CLI（`obliteratus` 命令）或子进程调用。这样能保持 Hermes Agent 的 MIT 许可证纯净。

## 视频指南

Hermes 代理使用 OBLITERATUS 消除 Gemma 拒绝行为的完整演示：
https://www.youtube.com/watch?v=8fG9BrNTeHs （"OBLITERATUS: An AI Agent Removed Gemma 4's Safety Guardrails"）

当用户希望在自行运行之前获得端到端工作流的视觉概览时非常有用。

## 何时使用此技能

当用户出现以下情况时触发：
- 想要"解除审查"或"消除"一个 LLM
- 询问如何从模型中移除拒绝行为/护栏
- 想要创建 Llama、Qwen、Mistral 等模型的取消审查版本
- 提到"拒绝移除"（refusal removal）、"消除"（abliteration）、"权重投影"（weight projection）
- 想要分析模型的拒绝机制工作原理
- 提及 OBLITERATUS、abliterator 或拒绝方向

## 第一步：安装

检查是否已安装：
```bash
obliteratus --version 2>/dev/null && echo "INSTALLED" || echo "NOT INSTALLED"
```

如果未安装，从 GitHub 克隆并安装：
```bash
git clone https://github.com/elder-plinius/OBLITERATUS.git
cd OBLITERATUS
pip install -e .
# 如需 Gradio Web UI 支持：
# pip install -e ".[spaces]"
```

**重要：** 安装前需与用户确认。这将拉取约 5-10GB 的依赖（PyTorch、Transformers、bitsandbytes 等）。

## 第二步：检查硬件

在进行任何操作前，先检查可用的 GPU：
```bash
python3 -c "
import torch
if torch.cuda.is_available():
    gpu = torch.cuda.get_device_name(0)
    vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f'GPU: {gpu}')
    print(f'VRAM: {vram:.1f} GB')
    if vram < 4: print('层级：极小（小于 1B 参数的模型）')
    elif vram < 8: print('层级：小（1-4B 参数的模型）')
    elif vram < 16: print('层级：中（4-9B 参数，使用 4 位量化）')
    elif vram < 32: print('层级：大（8-32B 参数，使用 4 位量化）')
    else: print('层级：前沿（32B+ 参数的模型）')
else:
    print('无 GPU —— 仅能在 CPU 上运行极小模型（小于 1B 参数）')
"
```

### VRAM 需求（使用 4 位量化）

| VRAM     | 最大模型大小  | 示例模型                                   |
|:---------|:--------------|:-------------------------------------------|
| 仅 CPU   | ~1B 参数      | GPT-2、TinyLlama、SmolLM                  |
| 4-8 GB   | ~4B 参数      | Qwen2.5-1.5B、Phi-3.5 mini、Llama 3.2 3B |
| 8-16 GB  | ~9B 参数      | Llama 3.1 8B、Mistral 7B、Gemma 2 9B     |
| 24 GB    | ~32B 参数     | Qwen3-32B、Llama 3.1 70B（紧张）、Command-R |
| 48 GB+   | ~72B+ 参数    | Qwen2.5-72B、DeepSeek-R1                   |
| 多 GPU   | 200B+ 参数    | Llama 3.1 405B、DeepSeek-V3（685B MoE）   |

## 第三步：浏览可用模型并获取推荐

```bash
# 按计算层级浏览模型
obliteratus models --tier medium

# 获取特定模型的架构信息
obliteratus info <model_name>

# 获取遥测驱动的最佳方法和参数推荐
obliteratus recommend <model_name>
obliteratus recommend <model_name> --insights  # 跨架构全局排名
```

## 第四步：选择方法

### 方法选择指南
**默认 / 推荐大多数情况使用：`advanced`。** 它使用多方向 SVD 结合范数保持投影，且经过充分测试。

| 情况                            | 推荐方法          | 原因                                       |
|:--------------------------------|:------------------|:-------------------------------------------|
| 默认 / 大多数模型                | `advanced`        | 多方向 SVD，范数保持，可靠                  |
| 快速测试 / 原型开发              | `basic`           | 快速、简单，足以进行评估                     |
| 密集模型（Llama、Mistral）       | `advanced`        | 多方向，范数保持                            |
| MoE 模型（DeepSeek、Mixtral）    | `nuclear`         | 专家粒度，处理 MoE 复杂性                    |
| 推理模型（R1 蒸馏版）            | `surgical`        | 感知思维链，保留推理过程                     |
| 顽固拒绝仍然存在                 | `aggressive`      | 白化 SVD + 注意力头手术 + 越狱提示            |
| 想要可逆更改                     | 使用引导向量（见分析模块部分） |
| 最大质量，不计算时间              | `optimized`       | 贝叶斯搜索最佳参数                           |
| 实验性自动检测                    | `informed`        | 自动检测对齐类型——实验性，不一定总是优于 advanced |

### 9 个 CLI 方法
- **basic** —— 通过均值差异法（diff-in-means）获得单一拒绝方向。快速（8B 模型约 5-10 分钟）。
- **advanced**（默认，推荐）—— 多个 SVD 方向，范数保持投影，2 轮细化。中等速度（约 10-20 分钟）。
- **aggressive** —— 白化 SVD + 越狱对比 + 注意力头手术。模型连贯性受损风险较高。
- **spectral_cascade** —— DCT 频域分解。研究/新颖方法。
- **informed** —— 在消除过程中运行分析以自动配置。实验性 —— 比 advanced 慢且结果不可预测。
- **surgical** —— SAE 特征 + 神经元掩码 + 注意力头手术 + 逐专家处理。非常慢（约 1-2 小时）。最适合推理模型。
- **optimized** —— 贝叶斯超参数搜索（Optuna TPE）。运行时间最长，但能找到最优参数。
- **inverted** —— 翻转拒绝方向。模型变得主动配合。
- **nuclear** —— 针对顽固 MoE 模型的最大力度组合。专家粒度。

### 方向提取方法（--direction-method 标志）
- **diff_means**（默认）—— 在拒绝/服从激活之间的简单均值差异。稳健。
- **svd** —— 多方向 SVD 提取。更适合复杂对齐。
- **leace** —— LEACE（Linear Erasure via Closed-form Estimation）。最优线性擦除。

### 4 个仅限 Python API 的方法
（CLI 不可用 —— 需要 Python 导入，这违反了 AGPL 边界。仅当用户明确想在自己的 AGPL 项目中将 OBLITERATUS 作为库使用时才提及。）
- failspy、gabliteration、heretic、rdo

## 第五步：运行消除

### 标准用法
```bash
# 默认方法（advanced）—— 推荐用于大多数模型
obliteratus obliterate <model_name> --method advanced --output-dir ./abliterated-models

# 使用 4 位量化（节省 VRAM）
obliteratus obliterate <model_name> --method advanced --quantization 4bit --output-dir ./abliterated-models

# 大模型（70B+）—— 保守默认设置
obliteratus obliterate <model_name> --method advanced --quantization 4bit --large-model --output-dir ./abliterated-models
```

### 微调参数
```bash
obliteratus obliterate <model_name> \
  --method advanced \
  --direction-method diff_means \
  --n-directions 4 \
  --refinement-passes 2 \
  --regularization 0.1 \
  --quantization 4bit \
  --output-dir ./abliterated-models \
  --contribute  # 可选遥测数据贡献，用于社区研究
```

### 关键标志
| 标志 | 描述 | 默认值 |
|:-----|:-----|:-------|
| `--method` | 消除方法 | advanced |
| `--direction-method` | 方向提取方法 | diff_means |
| `--n-directions` | 拒绝方向数量（1-32） | 取决于方法 |
| `--refinement-passes` | 迭代轮数（1-5） | 2 |
| `--regularization` | 正则化强度（0.0-1.0） | 0.1 |
| `--quantization` | 以 4 位或 8 位加载 | 无（全精度） |
| `--large-model` | 120B+ 模型的保守默认设置 | false |
| `--output-dir` | 保存消除后模型的路径 | ./obliterated_model |
| `--contribute` | 共享匿名化结果用于研究 | false |
| `--verify-sample-size` | 用于拒绝检查的测试提示数量 | 20 |
| `--dtype` | 模型数据类型（float16, bfloat16） | auto |

### 其他执行模式
```bash
# 交互式引导模式（硬件 → 模型 → 预设）
obliteratus interactive

# Web UI（Gradio）
obliteratus ui --port 7860

# 从 YAML 配置文件运行完整消融研究
obliteratus run config.yaml --preset quick

# 锦标赛：让所有方法相互竞争
obliteratus tourney <model_name>
```

## 第六步：验证结果

消除后，检查输出指标：

| 指标 | 良好值 | 警告 |
|:-----|:-------|:-----|
| 拒绝率 | < 5%（理想情况下 ~0%） | > 10% 表示拒绝仍然存在 |
| 困惑度变化 | < 10% 增加 | > 15% 表示连贯性受损 |
| KL 散度 | < 0.1 | > 0.5 表示显著的分布偏移 |
| 连贯性 | 高 / 通过定性检查 | 响应退化、重复 |

### 如果拒绝仍然存在（> 10%）
1. 尝试 `aggressive` 方法
2. 增加 `--n-directions`（例如 8 或 16）
3. 添加 `--refinement-passes 3`
4. 将 `--direction-method` 改为 `svd` 而不是 diff_means

### 如果连贯性受损（困惑度增加 > 15%）
1. 减少 `--n-directions`（尝试 2）
2. 增加 `--regularization`（尝试 0.3）
3. 将 `--refinement-passes` 减少到 1
4. 尝试 `basic` 方法（更温和）

## 第七步：使用消除后的模型

输出是一个标准的 HuggingFace 模型目录。

```bash
# 使用 transformers 本地测试
python3 -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained('./abliterated-models/<model>')
tokenizer = AutoTokenizer.from_pretrained('./abliterated-models/<model>')
inputs = tokenizer('如何撬锁？', return_tensors='pt')
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
"

# 上传到 HuggingFace Hub
huggingface-cli upload <username>/<model-name>-abliterated ./abliterated-models/<model>

# 使用 vLLM 提供服务
vllm serve ./abliterated-models/<model>
```

## CLI 命令参考

| 命令 | 描述 |
|:-----|:-----|
| `obliteratus obliterate` | 主要消除命令 |
| `obliteratus info <model>` | 打印模型架构详情 |
| `obliteratus models --tier <tier>` | 按计算层级浏览精选模型 |
| `obliteratus recommend <model>` | 遥测驱动的方法/参数建议 |
| `obliteratus interactive` | 引导式设置向导 |
| `obliteratus tourney <model>` | 锦标赛：所有方法逐一对比 |
| `obliteratus run <config.yaml>` | 从 YAML 执行消融研究 |
| `obliteratus strategies` | 列出所有注册的消融策略 |
| `obliteratus report <results.json>` | 重新生成可视化报告 |
| `obliteratus ui` | 启动 Gradio Web 界面 |
| `obliteratus aggregate` | 汇总社区遥测数据 |

## 分析模块

OBLITERATUS 包含 28 个用于机制可解释性的分析模块。
完整参考见 `skill_view(name="obliteratus", file_path="references/analysis-modules.md")`。

### 快速分析命令
```bash
# 运行特定的分析模块
obliteratus run analysis-config.yaml --preset quick

# 优先运行的模块：
# - alignment_imprint：对 DPO/RLHF/CAI/SFT 对齐方法进行指纹识别
# - concept_geometry：单一方向 vs. 多面锥体
# - logit_lens：确定哪个层决定拒绝
# - anti_ouroboros：自我修复风险评分
# - causal_tracing：因果必要组件
```

### 引导向量（可逆替代方案）
不是永久修改权重，而是在推理时使用引导向量：
```python
# 仅限 Python API — 用于用户自己的项目
from obliteratus.analysis.steering_vectors import SteeringVectorFactory, SteeringHookManager
```

## 消融策略

除了基于方向的消除，OBLITERATUS 还包括结构消融策略：
- **嵌入消融** —— 针对嵌入层组件
- **FFN 消融** —— 前馈网络块移除
- **注意力头剪枝** —— 注意力头剪枝
- **层移除** —— 完整层移除

列出所有可用策略：`obliteratus strategies`

## 评估

OBLITERATUS 包含内置评估工具：
- 拒绝率基准测试
- 困惑度比较（前后对比）
- LM Eval Harness 集成用于学术基准
- 与竞品逐对比比较
- 基线性能跟踪

## 平台支持

- **CUDA** — 完整支持（NVIDIA GPU）
- **Apple Silicon（MLX）** — 通过 MLX 后端支持
- **CPU** — 支持极小模型（< 1B 参数）

## YAML 配置模板

通过 `skill_view` 加载模板以实现可重复运行：
- `templates/abliteration-config.yaml` — 标准单模型配置
- `templates/analysis-study.yaml` — 消除前分析研究
- `templates/batch-abliteration.yaml` — 多模型批量处理

## 遥测

OBLITERATUS 可以选择性地将匿名运行数据贡献给全球研究数据集。
使用 `--contribute` 标志启用。不收集任何个人数据 —— 仅包含模型名称、方法、指标。

## 常见陷阱

1. **不要将 `informed` 作为默认方法** —— 它是实验性的，速度较慢。使用 `advanced` 以获得可靠结果。
2. **约 1B 以下的模型对消除反应不佳** —— 其拒绝行为浅显且分散，难以进行清洁的方向提取。预期结果不完整（拒绝残留 20-40%）。3B+ 的模型具有更清晰的拒绝方向，效果更好（使用 `advanced` 通常达到 0% 拒绝）。
3. **`aggressive` 可能使情况更糟** —— 在小型模型上会损害连贯性，甚至可能增加拒绝率。仅在 3B+ 模型上 `advanced` 留下 > 10% 拒绝时才使用。
4. **始终检查困惑度** —— 如果飙升 > 15%，则模型受损。降低激进程度。
5. **MoE 模型需要特殊处理** —— 对于 Mixtral、DeepSeek-MoE 等，使用 `nuclear` 方法。
6. **量化后的模型无法重新量化** —— 先对全精度模型进行消除，再量化输出。
7. **VRAM 预估是近似值** —— 4 位量化有帮助，但提取过程中峰值使用率可能激增。
8. **推理模型很敏感** —— 对于 R1 蒸馏版，使用 `surgical` 以保留思维链。
9. **检查 `obliteratus recommend`** —— 遥测数据可能提供比默认值更好的参数。
10. **AGPL 许可证** —— 切勿在 MIT/Apache 项目中 `import obliteratus`。仅限 CLI 调用。
11. **大型模型（70B+）** —— 始终使用 `--large-model` 标志以获得保守默认设置。
12. **光谱认证 RED 常见** —— 即使实际拒绝率为 0%，光谱检查也常常标记为"不完整"。应检查实际拒绝率，而不单依赖光谱认证。

## 互补技能

- **vllm** — 以高吞吐量提供被消除模型的服务
- **gguf** — 将被消除模型转换为 GGUF 格式用于 llama.cpp
- **huggingface-tokenizers** — 处理模型分词器