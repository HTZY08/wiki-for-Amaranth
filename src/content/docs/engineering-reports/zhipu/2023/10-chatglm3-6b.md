---
title: ChatGLM3-6B — 第三代全能对话模型
date: 2023-10-27
source: GitHub (THUDM/ChatGLM3-6B)
---

# ChatGLM3-6B

**发布日期：** 2023-10-27  
**来源：** GitHub THUDM/ChatGLM3-6B  
**工程范式：** 第三代全能小模型——在 6B 规模上实现工具调用、代码解释和智能体能力。

## 设计哲学

ChatGLM3-6B 是第三代的里程碑。如果说第一代解决了"能不能对话"，第二代解决了"怎么更快"，第三代解决了"能不能做更多"——引入 Function Call、Code Interpreter、Agent 任务支持。

核心哲学：**在固定参数量下，从"对话模型"进化到"全能助手"**，为后续 GLM-4 All Tools 奠定技术基础。

## 关键架构决策

### Function Call 原生支持
- 模型可以自主决定调用外部工具
- prompt 设计和训练数据中加入工具调用格式

### Code Interpreter 支持
- 模型可以编写和执行 Python 代码
- 在训练中引入代码执行结果反馈

### Agent 任务能力
- 支持多步推理 + 工具调用
- 在 AgentBench 等评测中取得好成绩

### 全面领先
- 在 42 个中文和英文 benchmark 上取得最佳成绩（同尺寸）

## 关键结果

- 在 **42 个 benchmark** 上全面领先（6B 级别）
- 支持 Function Call、Code Interpreter、Agent
- 上下文窗口维持 **32K**（继承自 ChatGLM2）
- 基准测试全面超越 Llama 2 7B/13B

## 范式对比

| 维度 | ChatGLM2-6B | ChatGLM3-6B | LLaMA 2 7B |
|------|-------------|-------------|------------|
| 上下文 | 32K | 32K | 4K |
| Function Call | ❌ | ✅ | ❌ |
| Code Interpreter | ❌ | ✅ | ❌ |
| Agent 任务 | ❌ | ✅ | ❌ |
| Benchmark 领先 | 部分 | 42 个全面领先 | - |

## 可复用的工程经验

1. **小模型的工具调用能力是产品化关键**——ChatGLM3 证明 6B 模型也能做 Function Call 和 Agent。
2. **"全能"比"单项最强"对产品更重要**——覆盖更多场景比在单一维度做到极致更有产品价值。
3. **在 6B 规模上"堆能力"是可行的**——参数量不是限制，训练数据和对齐策略才是。
4. **从 ChatGLM3 到 GLM-4 All Tools 的技术路径已经明确**——先在小模型上验证工具调用，再推广到大模型。
