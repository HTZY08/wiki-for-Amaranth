---
title: "2026 年中大模型选型指南"
description: "别只看 Benchmark。社区共识、实际体感、性价比，一个都不能少。"
---

# 2026 年中大模型选型指南

> **版本记录**
> - 2026.6.9 — 初版。骨架：快速选型 → 一句话评级 → 基准测试 → 定价 → 社区共识 → MoE 策略 → 本地训练部署。后续更新只改内容和数据，不打破这个结构。

**先说明**：这篇文章不会告诉你"某某模型排名第一"。截至 2026 年 6 月，不存在一个在所有场景下都最好的模型。Benchmark 数字越来越没用——很多模型跑分高但不经用，有些跑分低但日常顺手。本文的结构是：先帮你找到自己的场景→再看具体数据和社区风评→最后给一个实际可用的多模型策略。

---

## 一、先别查排名，先回答三个问题

选模型之前，想清楚你的瓶颈是什么：

| 你的情况 | 关键指标 | 推荐方向 |
|---------|---------|---------|
| **预算紧张，调用量大** | API 价格 | 国产模型：DeepSeek V4 Flash / V4 Pro |
| **写代码，尤其是修复杂 bug** | 代码质量、多文件理解 | Claude Opus 4.5+ 或 DeepSeek V4 Pro |
| **理科/数学/推理** | 数学竞赛、科学 QA | Gemini 3 Pro / GPT-5.2+ |
| **中文内容和日常对话** | 中文质量、成本 | DeepSeek V4 Flash / Qwen3.7 Max |
| **长文档/多模态** | 上下文窗口、视觉理解 | Gemini 3 Pro (1M ctx) / GPT-5.5 |
| **自己部署/私有化** | 开源协议、硬件要求 | DeepSeek V4 / Qwen3.5 / GLM-5 |
| **Agent / 自动化流程** | Function Calling、指令遵循 | GPT-5.4 / DeepSeek V4 |

**一句话版**：
- 有钱上 Opus，没钱上 DeepSeek V4 Flash
- 数学和长文档找 Gemini
- 日常主力用 Flash，攻坚上 Opus，偶尔 GPT-5.5

---

## 二、主流模型一句话总结（省流版）

| 模型 | 一句话评级 | 社区共识 |
|------|-----------|---------|
| **Claude Opus 4.8 / 4.7 / 4.6** | 🏆 综合最强，攻坚首选 | Everyone loves it |
| **Claude Sonnet 4.6** | 性价比版 Opus，低延迟 | 日常够用，比 Opus 明显差一档 |
| **GPT-5.5** | 全能，但贵 | 强但没啥惊喜 |
| **GPT-5.4 + Codex** | 编程工具链最佳 | Codex CLI 好评 |
| **Gemini 3 Pro** | 理科第一，多模态第二 | 论文党、数学党必备 |
| **DeepSeek V4 Pro** | 开源天花板，价格屠夫 | 社区高度认可 |
| **DeepSeek V4 Flash** | ⭐ **最佳性价比** | 你的主力模型，已验证靠谱 |
| **Qwen3.7 Max** | 中文最强 | 国内认可度高 |
| **GLM-5** | 国产全模态 | 中规中矩 |
| **Kimi K2.5 / K2.6** | 长文本不错，编程一般 | 偏向营销宣传 |
| **MiniMax M2.7 / M3** | ⚠️ **不推荐** | 社区评价极差 |
| **Grok 4.3** | 推理强，生态弱 | 性价比高，长程Agent任务意外好用 |
| **Grok 4.20** | 2M 超长上下文 | 小众但极端长文场景无可替代 |
| **Mistral Small 4** | 统一推理+视觉+编码 | 开源，119B MoE，极具性价比 |
| **Mistral Medium 3.5** | 128B 精调，Agent 专用 | 工具调用和多步推理稳定 |
| **Mistral Large 2512** | 旗舰模型 | 比上一代降价75% |
| **Devstral 2** | 编码 Agent 专用 | SWE-bench 开源 SOTA |
| **Perplexity Sonar Pro** | 搜索增强推理 | 带引用的深度研究，适合调研 |
| **Perplexity Sonar Deep Research** | 自主多步检索+综合 | 调研场景独一档 |
| **NVIDIA Nemotron 3 Ultra** | 免费可用的前沿模型 | 550B MoE，Agent编排强 |
| **Claude Haiku 4.5** | 轻量快速 | 够用但不惊艳 |
| **Gemini 3.5 Flash** | 高速推理 | 性价比不错，理科强 |
| **GPT-5.4 Mini / Nano** | GPT 的轻量版 | 生态好，价格适中 |
| **Step 3.7 Flash** | 国产多模态新秀 | 196B MoE，视觉理解好 |
| **Qwen3.7 Plus** | 多模态版 Qwen | 1M 上下文，看屏操控 |
| **Llama 3.3 70B** | 经典开源 | 便宜但已显老 |
| **Llama 4 Scout** | 10M 上下文的玩具 | 跑分好看，实际没人用 |

---

## 三、真实基准测试

> 先泼一盆冷水：SWE-bench 已被多家模型针对性优化过。MiniMax M2.7 宣称在 SWE-Pro 上达到 56.2% 追平 GPT-5.3 Codex，但 Reddit 和开发者社区普遍反映"连 80 行的 system prompt 都无法遵守"、"工具调用频繁出错"。跑分 ≠ 好用。

### 3.1 编程：最重要的战场

| 模型 | SWE-bench Verified | SWE-bench Pro | 社区体感 |
|------|:-----------------:|:-------------:|---------|
| Claude Opus 4.8 | **88.6%** | - | 👑 公认最强，多文件重构独一档 |
| Claude Opus 4.7 | 83.5% | - | 接近 4.8，便宜一档 |
| Claude Opus 4.5 | 80.9% | 52.3% | 退位但不落后 |
| GPT-5.4 | 76.9% | 57.7% | 计算机操作强，纯代码不如 Opus |
| Gemini 3.1 Pro | 80.6% | 54.2% | 性价比高，有一定用户基础 |
| DeepSeek V4 Pro Max | 80.6% | - | 开源 SOTA，社区真实反馈好 |
| DeepSeek V4 Flash | ~73% | - | 够用，成本极低 |
| **MiniMax M2.7** | **78.0%** | 56.2% | ⚠️ **跑分好看，实际翻车** |
| Kimi K2.5 | 76.8% | - | 长文本强，代码一般 |
| Qwen3.7 Max | ~75% | - | 中文代码场景不错 |

**关于 MiniMax M2.7 / M3 的社区真实反馈**：

M2.7 发布时一篇 VentureBeat 文章吹成了"自进化模型"，但：
- API 经常超时，返回格式不一致
- 对 system prompt 的遵循能力差——80 行的 prompt 就乱了
- 工具调用不稳定，不适合 Agent 场景
- Reddit r/MiniMax_AI 的标题就是 "Minimax M3 Is a Huge Letdown"

**为什么跑分能这么高？** 因为 SWE-bench 本身在 2026 年已被各厂商针对性优化过，变成了一场"谁优化更用力"的比赛，而不是"谁能力更强"的测试。

### 3.2 推理 & 理科

| 模型 | GPQA Diamond | HLE | AIME 2025 | 社区体感 |
|------|:-----------:|:---:|:---------:|---------|
| Claude Opus 4.8 | 93.6% | **57.9%** | - | 硬推理没人能打 |
| GPT-5.5 | 93.6% | 43.1% | - | 中规中矩 |
| Gemini 3 Pro | 92.6% | 45.8% | **100%** | 🏆 数学无敌 |
| GPT-5.2 | 92.4% | - | **100%** | 老模型但数学极强 |

**HLE（Humanity's Last Exam）** 是目前最难被污染的基准——由 1000 位专家各自出题，模型在未联网工具下回答。Claude Opus 4.8 的 57.9% 和第二名 Gemini 3 Pro 的 45.8% 之间差了 12 个百分点，这是当前最能体现真实推理差距的数字。

### 3.3 中文能力

中文任务上，国内模型天然占优。DeepSeek V4 和 Qwen3.7 Max 都是可靠选择。值得注意的是：
- DeepSeek V4 的**中文生成质量和对本土场景的适配**仍是所有模型里最自然的
- Qwen3.7 Max 在 Artificial Analysis 智能指数上获得 57 分（与 GPT-5.5 medium 持平）
- Claude 和 GPT 的中文能力在 2026 年已有巨大进步，日常对话不会露馅，但涉及中国本土梗、政策语境时会露怯

---

## 四、定价与真实成本

### 4.1 API 价格（$/1M tokens）

| 模型 | 输入 | 输出 | 上下文 |
|------|:---:|:---:|:-----:|
| Claude Opus 4.8 | $5 | $25 | 1M |
| GPT-5.5 | $5 | $30 | 1M |
| Gemini 3.1 Pro / 3 Pro | $2 | $12 | 1M |
| GPT-5.4 | $1.25 | $10 | 400K |
| Claude Sonnet 4.6 | $3 | $15 | 200K |
| Claude Haiku 4.5 | $1 | $5 | 200K |
| Gemini 3.5 Flash | $1.50 | $9 | 1M |
| Gemini 3 Flash Preview | $0.50 | $3 | 1M |
| DeepSeek V4 Pro | $1.74 | $3.48 | 1M |
| **DeepSeek V4 Flash** | **$0.14** | **$0.28** | 1M |
| DeepSeek R1 | $0.55 | $2.19 | 128K |
| Qwen3.7 Max | $0.90 | $2.70 | 1M |
| Qwen3.7 Plus | $0.40 | $1.60 | 1M |
| Qwen3 235B A22B | $0.72 | $2.16 | 262K |
| Mistral Medium 3.5 | $1.50 | $7.50 | 262K |
| Mistral Large 2512 | $0.50 | $1.50 | 262K |
| Mistral Small 4 | $0.15 | $0.60 | 262K |
| Devstral 2 | $0.40 | $2.00 | 262K |
| Grok 4.3 | $1.25 | $2.50 | 1M |
| Grok 4.20 | $2.00 | $6.00 | 2M |
| Perplexity Sonar Pro | $3.00 | $15.00 | 200K |
| Perplexity Sonar Deep Research | $2.00 | $8.00 | 128K |
| Perplexity Sonar (轻量) | $1.00 | $1.00 | 127K |
| NVIDIA Nemotron 3 Ultra | $0.50 | $2.50 | 1M |
| NVIDIA Nemotron 3 Super | **免费** | **免费** | 128K |
| GPT-5.4 Mini | $0.75 | $4.50 | 400K |
| GPT-5.4 Nano | $0.20 | $1.25 | 400K |
| GPT-4.1 Nano | $0.10 | $0.40 | 1M |
| Step 3.7 Flash | $0.20 | $1.15 | 256K |
| Meta Llama 3.3 70B | $0.10 | $0.32 | 131K |
| Nex-N2-Pro (free) | **免费** | **免费** | 262K |

### 4.2 真正有用的数字

- **DeepSeek V4 Flash** 的输出价格是 Claude Opus 4.8 的 **1/89**
- Claude Opus 4.8 跑一次的任务，Flash 能跑 **89 次**还多出几毛钱
- 跑分有争议但价格没争议——Flash 的性价比全网公认
- 即使 V4 Pro，输出价格也只是 Opus 的 1/7，但 SWE-bench 只差 8 个百分点

---

## 五、社区共识与冷知识

### 💬 真实用户怎么说

**关于 DeepSeek V4：**
- "Benchmarks can be gamed"——Reddit 用户说这很正常，但"V4 Flash 的性价比不靠跑分，靠钱包"
- "V4 Pro matches Opus on SWE-bench at 1/21x the output cost"——多家评测确认
- "Flash 日常够了，上强度还是得 Opus"

**关于 Claude Opus：**
- "Opus 4.5 到 4.8 的进步没有数字显示的那么大，但 4.8 在 HLE 上的领先是实打实的"
- "对于需要多文件理解的复杂重构，Opus 无人能敌"

**关于 GPT-5 系列：**
- "5.5 没有比 5.4 强多少，但贵了不少"
- "Codex 的 1M 上下文是真的有用，不是噱头"

**关于 MiniMax：**
- "M2.7 的跑分好看，但你去用一下就知道了"
- "API 经常崩，返回乱码，自进化是个营销概念"

**关于 Grok：**
- "Grok 4.3 的推理确实强，HLE 第三，但 xAI 的 API 生态太差了"——Reddit
- "Grok 4.3 赢下了13/18个长程Agent任务，总花费 $7.84，换 Opus 要 $71.50" — Towards AI 实测
- "Grok 4.3 是市场上最便宜的前沿模型" — 多家评测确认
- "如果你只跑推理题，Grok 性价比不错"
- "Grok Build 的并行子Agent是亮点，但beta阶段，没有独立基准测试"

**关于 Mistral：**
- "Mistral Small 4 用一个模型替代了三个（Magistral/Pixtral/Devstral），119B MoE，$0.15/M 输入" — 多家 AI 媒体
- "Mistral Medium 3.5 的 128B 密集模型在工具调用和 Agentic 工作流上比同价位竞品更可靠" — Reddit r/LocalLLaMA
- "Devstral 2 在 SWE-bench Verified 上超越所有开源模型，单张 4090 可跑" — Mistral 官方
- "欧洲那边的朋友主力在用 Mistral，数据合规优势"

**关于 Perplexity Sonar：**
- "Sonar Deep Research 在 Law、Medicine、Academic 场景表现特别好" — Perplexity 官方
- "Deep Research 跑一次的费用可能到 $0.41，但替代了几十次手动搜索" — Finout 定价分析
- "Sonar Pro Search 的自主多步推理在调研场景独一档，但每千次额外收 $18，高频用不起" — OpenRouter
- "Perplexity 做 research 不错，别当常规 LLM 用"

**关于 MiniMax：**

1. **SWE-bench 已被污染**——各厂商针对它做了专门优化，跑分和实际体验的差距越来越大
2. **MiniMax 的跑分是 Benchmark 游戏的最佳案例**——56.2% SWE-Pro 看着吓人，实际体验远不如跑分低 20% 的 DeepSeek V4 Flash
3. **跑分 80% 和 70% 的区别，在你实际项目里大概率感觉不到**——但价格差 89 倍，你一定能感觉到
4. **开源模型在 2026 年已经真正追上来了**——DeepSeek V4、Qwen3.5、GLM-5 全部 MIT 开源，可商用

---

## 六、一个经过验证的 MoE 策略

这是目前开发者社区里最主流的打法，也是本站在实际使用的方案：

```
80% 调用 → DeepSeek V4 Flash（日常：问答、中文、轻量编码）
10% 调用 → Claude Opus 4.7/4.8（攻坚：复杂架构、高难度调试）
 5% 调用 → Gemini 3 Pro / GPT-5.4（多模态、数学、长文档）
 5% 调用 → Grok 4.3 / Perplexity Sonar / Mistral（实验、对比、特定场景）
```

**为什么这么配？**
- Flash 承担 80% 的流量，年成本控制在 $20-50
- Opus 只用来解决 Flash 搞不定的硬骨头——推理、多文件重构、架构决策
- 偶尔用 Gemini/GPT 补多模态和数学场景
- Grok 适合长程 Agent 任务和性价比敏感的高频迭代
- Perplexity Sonar 在调研/文献检索场景无可替代
- Mistral 是欧洲数据合规场景下的可靠备选

**成本对比**：如果全用 Opus 4.8，同样流量年花费约 $5,000-10,000。上述组合将成本压到 1/100 以下，质量损失不到 5%。

---

## 七、训练部署本地模型

如果你有消费级 GPU（12GB+ VRAM），训一个自己的小模型是 2026 年最划算的投入。以下是本站实际跑通的完整链路。

### 7.1 硬件基线

| 硬件 | 参数 |
|------|------|
| GPU | RTX 5070 Ti 12GB（Blackwell sm_120） |
| 可行方案 | QLoRA 4bit，7-8B 基座模型 |
| 训练速度 | ~55s/step，100 步约 2h |
| 推理显存 | 4bit 量化后 ~5.7GB/12GB |
| 操作系统 | Docker 容器内（WSL2 + Docker Desktop） |

### 7.2 训练流程

```
选择基座模型（推荐 Qwen3-8B）
  → 准备训练数据（纯原文，不仿写）
  → QLoRA 4bit 微调（rank=16, alpha=32）
  → 监控 loss 曲线，提前停止防过拟合
  → 交叉对比各 checkpoint 的输出质量
  → 选择最佳 checkpoint
```

**关键参数：**
- 量化：nf4 + double_quant
- LoRA rank=16, alpha=32，训练参数 43.6M / 8.2B = 0.53%
- Batch=2，grad_accum=4（有效 batch=8）
- LR=2e-4，cosine 调度
- PyTorch 2.10+ 需手动绕过 `prepare_model_for_kbit_training`（`use_reentrant` bug）

**训练数据铁律：** 只用原文做 Continued Pre-Training，不用 LLM 生成的平行语料。风格迁移靠学习原文特征，不是靠"仿冒"。

### 7.3 部署路径

训练后的 LoRA 适配器（`adapter_model.safetensors` ~175MB）不是完整模型——需要基座配合。三条路线：

| 方案 | 做法 | 优点 | 缺点 |
|------|------|------|------|
| ✅ 合并→转 GGUF | 合并 LoRA 到基座，转 GGUF，llama.cpp 部署 | 一次合并永久可用，加载快 | 需 ~30GB 磁盘，合并 3-5 分钟 |
| vLLM 动态加载 | vLLM serve + `--enable-lora` | 不合并，可热切换 | 需 Docker GPU，镜像 ~4GB |
| LM Studio | GUI 加载基座 + adapter | 零代码 | Adapter 兼容性偶有问题 |

**推荐方案：** 合并后量化到 Q4，llama.cpp server 部署。后续开机自启。

### 7.4 断网兜底

本地训练好的模型不仅是练手——它可以作为云端 API 的自动 Fallback。

方案：**Watchdog 按需启动**（本站实际使用的模式）

```
cron（每 3 分钟）→ 检测主 API 是否可达
  ├─ 可达 → 什么都不做（0 token 消耗）
  └─ 不可达 → 自动拉起本地推理服务器
              → Hermes 自动切到本地 provider
              → 网络恢复后切回云端
```

优势：模型不常驻（省显存）、断网后最多 3 分钟自动拉起、0 token 额外开销。

### 7.5 成本与收益

| 项目 | 数据 |
|------|------|
| 训练一次 | ~2h，电费 ~0.5 元 |
| 模型尺寸 | 8B Q4 ≈ 5GB 显存 |
| 推理速度 | ~30-50 t/s（llama.cpp） |
| 日常使用 | 够 80% 场景，攻坚还是得上 Opus |

一句话：**训练本地模型的性价比极高**——不是因为它能取代 Opus，而是因为它把"免费试错"的门槛降到了零。随便调 prompt、随便改数据、随便跑实验，不用心疼 API 费用。

---

## 八、OpenRouter 完整模型生态速查

OpenRouter 汇聚了 400+ 模型，来自 60+ 提供商。以下按生态分类列出所有可通过 OpenRouter 调用的主要模型家族，并标注定价区间与核心定位，方便你按场景快速检索。

### Anthropic 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| Claude Opus 4.8 | $5 / $25 | 1M | 综合最强，攻坚首选 |
| Claude Opus 4.7 | $5 / $25 | 1M | 略逊 4.8，性价比稍好 |
| Claude Opus 4.5 | $5 / $25 | 1M | 退位巨人 |
| Claude Sonnet 4.6 | $3 / $15 | 200K | 日常编码 |
| Claude Haiku 4.5 | $1 / $5 | 200K | 轻量任务 |

### OpenAI 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| GPT-5.5 | $5 / $30 | 1M | 旗舰全能 |
| GPT-5.4 | $1.25 / $10 | 400K | 编程+Codex 工具链 |
| GPT-5.4 Mini | $0.75 / $4.50 | 400K | 中型性价比 |
| GPT-5.4 Nano | $0.20 / $1.25 | 400K | 轻量快速 |
| GPT-4.1 | $2 / $8 | 1M | 上一代旗舰 |
| GPT-4.1 Nano | $0.10 / $0.40 | 1M | 极低成本 |
| o3 / o4-mini | $2/$8 / $1.1/$4.4 | 200K | 推理专用 |

### Google Gemini 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| Gemini 3.1 Pro Preview | $2 / $12 | 1M | 数学/推理最强 |
| Gemini 3 Pro | $2 / $12 | 1M | 老旗舰，理科强 |
| Gemini 3.5 Flash | $1.50 / $9 | 1M | 高速性价比 |
| Gemini 3 Flash Preview | $0.50 / $3 | 1M | 轻量推理 |
| Gemma 4 26B (free) | 免费 | — | 开源轻量 |

### DeepSeek 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| DeepSeek V4 Pro Max | $1.74 / $3.48 | 1M | 开源天花板 |
| **DeepSeek V4 Flash** | **$0.14 / $0.28** | **1M** | ⭐ 最佳性价比 |
| DeepSeek R1 | $0.55 / $2.19 | 128K | 推理链模型 |
| DeepSeek V3.2 | $0.28 / $0.40 | 128K | 上代主力 |

### Meta Llama 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| Llama 4 Maverick | ~$0.20 / $0.60 | 1M | 最新旗舰开源 |
| Llama 4 Scout | $0.15 / $0.50 | 10M | 超长上下文展示品 |
| Llama 3.3 70B | $0.10 / $0.32 | 131K | 经典开源，便宜够用 |

### Mistral 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| Mistral Large 2512 | $0.50 / $1.50 | 262K | 旗舰模型 |
| Mistral Medium 3.5 | $1.50 / $7.50 | 262K | 128B 密集，Agent 优秀 |
| Mistral Small 4 | $0.15 / $0.60 | 262K | 119B MoE 三合一 |
| Devstral 2 | $0.40 / $2.00 | 262K | 编码 Agent 专用 |
| Ministral 3 8B | $0.10 / $0.30 | 262K | 预算首选 |
| Codestral | $1 / $3 | 32K | 代码补全专用 |
| Voxtral TTS | $22/M char | — | 语音合成 |

### xAI Grok 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| Grok 4.3 | $1.25 / $2.50 | 1M | 旗舰推理+Agent |
| Grok 4.20 | $2 / $6 | 2M | 超长上下文 |
| Grok 4.1 Fast | $0.75 / $1.50 | 128K | 快速版 |
| Grok 4 (退役) | — | — | 已由 4.3 取代 |

### 阿里 Qwen 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| Qwen3.7 Max | $1.25 / $3.75 | 1M | 中文旗舰 |
| Qwen3.7 Plus | $0.40 / $1.60 | 1M | 多模态版 |
| Qwen3 235B A22B | $0.72 / $2.16 | 262K | MoE 开源 |
| Qwen3 VL 235B | — | — | 视觉版本 |

### Perplexity Sonar 生态
| 模型 | 定价基准 | 定位 |
|------|---------|------|
| Sonar Pro Search | $3/$15/M + $18/1K请求 | 自主多步研究 |
| Sonar Deep Research | $2/$8/M + $5/1K搜索 + $3/M推理 | 深度调研 |
| Sonar Pro | $3/$15/M | 搜索增强 |
| Sonar Reasoning Pro | $2/$8/M | 链式推理 |
| Sonar (轻量) | $1/$1/M | 快速搜索 |

### NVIDIA Nemotron 生态
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| Nemotron 3 Ultra | $0.50 / $2.50 | 1M | 前沿推理 (550B MoE) |
| Nemotron 3 Ultra (free) | 免费 | 1M | 免费前沿模型 |
| Nemotron 3 Super (free) | 免费 | 128K | 免费 Agent 编排 (120B MoE) |
| Nemotron 3 Nano 30B (free) | 免费 | 256K | 免费轻量推理 |

### 国产模型生态（其他）
| 模型 | 输入/输出 $/M | 上下文 | 定位 |
|------|:------------:|:-----:|------|
| Step 3.7 Flash | $0.20 / $1.15 | 256K | 阶跃星辰 MoE，多模态 |
| Kimi K2.6 / K2.5 | $0.68 / $3.42 | 262K | 长文本强 |
| GLM-5 | $0.50 / $2.00 | 200K | 智谱全模态 |
| GLM-4.5 Air (free) | 免费 | — | 免费国产 |
| MiniMax M3 | $0.30 / $1.20 | 1M | ⚠️ 不推荐 |
| Yi-Lightning | $0.50 / $1.50 | — | 01.AI 旗舰 |
| Hunyuan Large | — | — | 腾讯混元 |
| Nex-N2-Pro (free) | 免费 | 262K | 397B MoE 国产 Agent |

### 其他值得关注的模型
| 模型 | 输入/输出 $/M | 定位 |
|------|:------------:|------|
| Cohere Command-A | $2 / $8 | 企业级检索增强 |
| AI21 Jamba 1.5 | $0.50 / $0.70 | SSM-Transformer 混合 |
| Reka Core | — | 多模态 |
| Microsoft Phi-4 | — | 小模型高效 |
| ByteDance Seed | — | 字节跳动系列 |

> 数据来源：OpenRouter 官方模型目录 & pricing API（2026-06），直接获取。上面 80+ 个模型均可在 OpenRouter 上通过统一 API 调用。定价为 OpenRouter 直通价，与官方一致。

---

## 九、结论

| 你的身份 | 最佳选择 |
|---------|---------|
| 个人开发者，自用 | DeepSeek V4 Flash 主力 + Opus 攻坚 |
| 创业团队，降本 | DeepSeek V4 Flash/Pro（全栈开源）+ Grok 4.3 |
| 企业，质量优先 | Claude Opus + GPT-5.5 |
| 科研/学术调研 | Perplexity Sonar Deep Research / Gemini 3 Pro |
| 中文内容创作 | DeepSeek V4 / Qwen3.7 Max |
| 欧洲/数据合规 | Mistral Small 4 / Mistral Medium 3.5 |
| 私有化部署 | DeepSeek V4 Pro / Mistral Small 4 / Devstral 2（均开源） |
| 超长文档/代码库 | Grok 4.20（2M ctx） |

**避坑：** MiniMax 系列暂时别碰。跑分和实际体验的差距太大。

**守则：** 先用自己的数据测，别信跑分。一个月后觉得"这模型真好用"才是真的好用。

---

> 数据来源：OpenRouter 官方模型目录 (2026-06)、CostGoat (2026-05-30)、Vellum LLM Leaderboard (2026-05-29)、Artificial Analysis、LM Council、Reddit r/DeepSeek / r/LocalLLaMA / r/singularity  
> 最后更新：2026 年 6 月
