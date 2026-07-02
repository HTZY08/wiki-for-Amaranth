---
title: Mistral Large — 旗舰级 API 推理模型
date: 2024-02-26
source: mistral.ai/news/mistral-large
---

# Mistral Large

**发布日期：** 2024-02-26  
**来源：** mistral.ai/news/mistral-large (blog)  
**工程范式：** 闭源旗舰——多语言推理、精确指令遵循、函数调用。

## 设计哲学

Mistral Large 是 Mistral AI 的旗舰 API 模型，定位为"仅次于 GPT-4 的全球第二可用的 API 模型"。

核心理念：**通过 API 提供前沿能力，开源与闭源双线并行**。开源模型（Mistral 7B、Mixtral）获取社区影响力和反馈，闭源模型（Mistral Large）支撑商业收入。

## 关键架构决策

### 旗舰模型
- Mistral AI 最新最强大的文本生成模型
- **32K token 上下文窗口**——精确的大文档信息召回
- **原生多语言**：英语、法语、西班牙语、德语、意大利语——精细的语法和文化理解
- 通过 **la Plateforme**（欧洲主机）和 **Azure** 提供

### 关键能力
1. **精确指令遵循**——用于 le Chat 的系统级内容审核
2. **原生函数调用**——可调用外部工具和 API
3. **JSON 格式模式**——强制输出合法 JSON
4. **约束输出模式**——用于结构化数据提取

### 并发模型：Mistral Small
- 同时发布，优化延迟和成本
- 超越 Mixtral 8x7B，延迟更低
- 同样支持 RAG 和函数调用

### 定价和部署
| 终端 | 类型 | 可用性 |
|------|------|--------|
| open-mistral-7B | 开源权重 | 免费 |
| open-mixtral-8x7B | 开源权重 | 免费 |
| mistral-small-2402 | 优化模型 | la Plateforme |
| mistral-large-2402 | 旗舰 | la Plateforme, Azure |
| mistral-medium | 维护中 | la Plateforme |

## 关键结果

### 基准性能
- MMLU、HellaSwag、WinoGrande、ARC、TriviaQA、TruthfulQA 上表现强劲
- 多语言版超越 LLaMA 2 70B（法语、德语、西班牙语、意大利语的 HellaSwag、ARC、MMLU）
- HumanEval (pass@1) 和 MBPP (pass@1) 顶尖
- GSM8K (maj@8) 和 MATH (maj@4) 强

## 范式对比
| 维度 | Mistral Large | GPT-4 | Claude 3 Opus |
|------|--------------|-------|--------------|
| 推理排名 | #2 (仅次于 GPT-4) | #1 | #3 |
| 多语言 | 5 种原生 | 多语言 | 多语言 |
| 函数调用 | 原生支持 | 支持 | 支持 |
| JSON 模式 | 原生 | 需 prompt | 需 prompt |
| 开源策略 | 有开源版本 | 不开源 | 不开源 |
| 部署 | la Plateforme + Azure | Azure + OpenAI | AWS + GCP |

## 可复用的工程经验

1. **开源/闭源双线策略**——开源驱动社区和影响力，闭源驱动商业收入。
2. **API 与开源模型共享技术栈**——Mistral Large 的架构与开源模型的连续性有利于技术演进。
3. **原生函数调用 + JSON 模式**是 API 产品的核心竞争力——降低开发者集成成本。
4. **Azure 作为首发云伙伴**——借助大平台分发是欧洲 AI 公司进入全球市场的有效策略。
5. **"世界第二"的定位**巧妙——承认 GPT-4 领先，但强调自己是开源友好、在欧洲托管的替代方案。
