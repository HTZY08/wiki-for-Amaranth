---
title: CodeGeeX — 多语言代码生成模型与 HumanEval-X 基准
date: 2023-03-30
source: arXiv 2303.17568 (KDD 2023)
---

# CodeGeeX

**发布日期：** 2023-03-30  
**来源：** arXiv 2303.17568 (KDD 2023)  
**工程范式：** 多语言代码生成——从数据集、模型到 IDE 插件的全栈工程。

## 设计哲学

CodeGeeX 是智谱 AI 与清华大学联合推出的多语言代码生成模型。核心贡献不仅是 13B 参数模型本身，还包含：

1. **HumanEval-X 基准**：将 HumanEval（仅 Python）扩展到 C++、Java、JavaScript、Go，共 820 个手工编写问题
2. **全栈产品**：VS Code、JetBrains、Cloud Studio 插件
3. **国产硬件适配**：在 1,536 个 Ascend 910 AI 处理器上训练

核心理念：**代码模型不只是模型，而是完整的开发者工具链**。

## 关键架构决策

### 模型规格
- **13B 参数**，基于 GLM 架构
- 训练数据：23 种编程语言，**850B tokens**（截至 2022 年 6 月）
- 训练集群：1,536 个 Ascend 910 AI 处理器

### HumanEval-X 基准
- 5 种语言（Python、C++、Java、JavaScript、Go）
- 820 个手工编写编程问题
- 每个问题附带测试用例和标准解答
- 支持代码生成和代码翻译两种评测

### IDE 插件
- VS Code 插件
- JetBrains 插件
- Cloud Studio 插件
- 每周为数万活跃用户生成 **47 亿 tokens**

## 关键结果

### 代码生成（HumanEval-X Pass@1）
| 语言 | CodeGeeX | 同规模模型 |
|------|---------|-----------|
| Python | 领先 | 可比 |
| C++ | 领先 | - |
| Java | 领先 | - |
| JavaScript | 领先 | - |
| Go | 领先 | - |

### 代码翻译
在 HumanEval-X 翻译任务上，CodeGeeX 也优于同规模多语言代码模型。

### 用户研究
- **83.4%** 的用户反馈 CodeGeeX 提升了编码效率

### 后续版本
基于 ChatGLM2-6B 的 **CodeGeeX2-6B** 额外训练 600B 代码 tokens：
- HumanEval-X Pass@1 提升：Python +57%，C++ +71%，Java +54%，JavaScript +83%，Go +56%

## 范式对比
| 维度 | CodeGeeX 13B | Codex (OpenAI) | CodeLlama 7B |
|------|-------------|---------------|-------------|
| 开源 | ✅ 完全开源 | ❌ | ✅ |
| 多语言 | 23 种 | 部分 | 部分 |
| 中文支持 | ✅ | ❌ | ❌ |
| IDE 插件 | VS Code, JetBrains, Cloud | GitHub Copilot | 无官方插件 |
| 国产硬件 | Ascend 910 | NVIDIA only | NVIDIA only |

## 可复用的工程经验

1. **HumanEval-X 是重要的基础设施贡献**——填补了多语言代码评测的空白，被后续多个模型引用。
2. **全栈产品（模型 + 数据 + IDE 插件）**比纯模型发布更有产品价值。
3. **国产硬件生态**——在 Ascend 910 上训练 13B 模型证明了国产 AI 芯片在大模型训练中的可行性。
4. **代码翻译是代码生成的"兄弟任务"**——CodeGeeX 同时支持两者，扩大了适用范围。
5. **从 CodeGeeX 13B 到 CodeGeeX2-6B 的迭代展示了"基座升级"策略**——用更强的基座模型+代码续训，比从零训练更高效。
