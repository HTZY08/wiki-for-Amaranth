---
title: Qwen3.5-Omni — 全模态统一架构，Thinker-Talker 双轨 MoE
date: 2026-07-16
source: https://arxiv.org/abs/2604.15804
---

# Qwen3.5-Omni Technical Report — 全模态统一架构与自然全双工交互

**发布日期：** 2026年4月（arXiv:2604.15804）
**来源：** https://arxiv.org/abs/2604.15804
**工程范式：** 端到端全模态原生统一 + Thinker-Talker 双轨 MoE 分布式生成

## 设计哲学

Qwen3.5-Omni 的核心约束是：**在一个模型中同时处理文本、图像、音频、视频四种模态的输入，并实时生成文本或语音输出，且不损害任一模态的单项性能。**

面对这一约束，Qwen 团队的选择是：
- **不采用外部编排（orchestration）**——不通过外部 Agent 框架调度多个单模态模型，而是端到端训练单一模型处理所有模态。这是「原生全模态」（native omni-modal）路线。
- **延续 Thinker-Talker 架构**——Thinker 负责多模态理解和文本生成，Talker 负责流式语音合成。二者共享多模态上下文但分工明确。
- **放弃「为所有模态共享同一组参数」的简单方案**——引入 Hybrid Attention MoE，让不同 expert  specialize 在不同模态和任务上，用稀疏激活换取容量。
- **放弃「音频和文本使用相同 tokenizer 速率」的假设**——引入 ARIA 动态对齐机制，解决文本 tokenizer 与音频 codec tokenizer 速率不匹配导致的生成不稳定性。

核心放弃：Qwen3.5-Omni **不追求单一模型在纯文本/纯图像 benchmark 上超越 Qwen3.5 同规模单模态模型**，而是接受轻微退化（约 1-3%），换取全模态能力。Table 4 显示 Plus 版本在 MMLU-Pro 上 85.9 vs 86.8，退化可接受。

## 关键架构决策

### 总体架构：Thinker-Talker 双轨

```
输入 (文本/图像/音频/视频)
  └─→ Vision Encoder (SigLIP2) ──┐
  └─→ Audio Encoder (AuT) ───────┤
                                  ├─→ Thinker (Hybrid MoE Transformer)
                                      └─→ 文本输出 + 高层表示传给 Talker
                                            └─→ Talker (Hybrid MoE Transformer)
                                                  └─→ MTP (Multi-Token Prediction)
                                                        └─→ Code2Wav ConvNet
                                                              └─→ 流式语音
```

### Thinker — 多模态理解与文本生成

- **文本 Tokenizer**：Qwen3.5 tokenizer，byte-level BPE，词表 250k（从 150k 扩展），跨语言编码/解码效率提升 10-60%
- **视觉编码器**：SigLIP2（从 Qwen3.5 继承），支持图像和视频
- **音频编码器**：AuT（Audio Transformer），从零训练，消耗 4000 万小时音频-文本配对数据
  - 输入：16kHz 波形 → 128 通道 mel-spectrogram（25ms 窗，10ms 步长）
  - 4 层 Conv2D 下采样 16 倍 → 自注意力层 → 6.25Hz token 率（每 token 对应 ~160ms 信号）
  - 多语言训练比例：中文:英文:其他 = 3.5:3.5:3
  - 动态注意力窗口训练机制，平衡实时 prefilling 与离线理解

### Hybrid Attention MoE

这是 Qwen3.5-Omni 最关键的架构创新。Thinker 和 Talker 都采用 Hybrid MoE：

- **Gated Delta Net (GDN)** 模块——这是加速长音视频序列建模的核心。GDN 减少 KV-cache I/O 开销，在高并发长上下文推理中显著提升吞吐量
- **混合专家路由**——不同 expert  specialize 在不同模态（文本/图像/音频）和任务类型上
- 具体参数规模：Plus 版本为「数百亿参数」（原文未披露精确数字），Flash 版本为较小变体

### 时间感知位置编码

- 核心思路：**用文本时间戳替代绝对位置ID**
- **TM-RoPE**基础 + 对每个视频帧或音视频帧插入格式化的文本时间戳（「3.2s」格式）
- 解决了绝对位置 ID 在长视频中稀疏化的问题
- 音频每 160ms 一个时间 ID，视频帧按实际时间戳动态调整
- 多模态间位置编号连续，避免冲突

### ARIA（Adaptive Rate Interleave Alignment）

适配速率交叉对齐——解决流式语音合成中的核心痛点：

- **问题**：文本 tokenizer 与音频 codec tokenizer 的编码效率差异大（文本~4 chars/token，音频~160ms/token），导致固定交叉速率下出现跳词、发音错误、数字歧义
- **方案**：对生成序列的任意前缀，累积语音-文本 token 比率不超过对应条目的全局比率。单流交叉（从 Qwen3-Omni 的双通道变为单通道）
- **效果**：显著改善自然度和韵律，跨语言泛化良好，支持任意文本 token 前缀 + 连贯语音 token 续接

### Talker — 流式语音生成

- 基于 RVQ（残差向量量化）的语音表示
- 多码簿 codec 表示实现单帧即时合成
- MTP（Multi-Token Prediction）模块建模残差码簿
- Code2Wav：因果 ConvNet 实现逐帧波形重建
- 支持零样本语音克隆：通过专用 system prompt 指定目标音色特征

### 流式与并发设计

- **Chunked Prefilling**：音频和视频编码器按时间维度输出 chunk，显著降低 TTFT
- 首包延迟：音频输入 Plus 435ms / Flash 235ms；视频输入 Plus 651ms / Flash 426ms
- 4 并发下 Thinker TTFT 仅升至 86ms（音频）和 446ms（视频）
- Generation RTF（实时因子）= 0.178-0.334，满足流式语音生成余量

## 训练策略

### 预训练（三阶段）

| 阶段 | 序列长度 | 说明 |
|------|---------|------|
| S1: Encoder Alignment | — | 锁定 LLM 参数，单独训练视觉和音频编码器 + adapter |
| S2: General Stage | 32,768 | 全参数解锁，约 4 万亿 token：文本 0.92T + 音频 1.99T + 图像 0.95T + 视频 0.14T + 音视频 0.29T |
| S3: Long Context Stage | 262,144 | 扩展到 256k，增加长音频/长视频比例 |

音频训练数据：超过 4000 万小时。

### 思考器后训练（三阶段）

1. **Specialist Distillation**：先训练多个领域专家教师模型（纯文本agent/coding/reasoning + 视觉 + 音频），各自 SFT+RL 后蒸馏到统一模型
2. **On-Policy Distillation (OPD)**：将文本条件下的强响应能力蒸馏到音频输入条件，弥合模态间响应质量差距
3. **Interaction-Aligned RL**：构建多轮交互轨迹，设计用户体验目标（语言切换稳定性、人格一致性、长上下文指令跟随）的 reward 信号

### 语音生成训练（四阶段）

1. **General Stage**：2000 万+小时多语言语音数据 + 多模态上下文配对
2. **Long-Context Stage**：数据质量分层 + CPT，扩展到 64k token 上下文
3. **RL Stage**：DPO + 规则奖励 + GSPO
4. **Speaker Fine-tuning**：轻量级说话人微调

## 关键结果

### Text → Text（与 Qwen3.5-Plus-Instruct 对比）

| Benchmark | Qwen3.5-Plus | Qwen3.5-Omni-Plus | 退化 |
|-----------|-------------|-------------------|------|
| MMLU-Pro | 86.8 | **85.9** | -0.9 |
| MMLU-Redux | 94.3 | **94.2** | -0.1 |
| GPQA | 85.9 | **83.9** | -2.0 |
| LiveCodeBench v6 | 67.1 | **65.6** | -1.5 |
| IFEval | 89.7 | **89.7** | 持平 |
| TAU2Bench | 82.7 | **81.0** | -1.7 |

### Audio → Text（与 Gemini-3.1 Pro 对比）

| Benchmark | Gemini-3.1 Pro | Qwen3.5-Omni-Plus |
|-----------|---------------|-------------------|
| MMAU | 81.1 | **82.2** |
| VoiceBench | 88.9 | **93.1** |
| ASR Fleurs WER ↓ | 7.32 | **6.55** |
| ASR LibriSpeech clean WER ↓ | 3.36 | **1.11** |
| ASR LibriSpeech other WER ↓ | 4.41 | **2.23** |

Qwen3.5-Omni-Plus 在语音识别上显著超越 Gemini-3.1 Pro（LibriSpeech clean WER 1.11% vs 3.36%）。

### 音视频 → Text

| Benchmark | Gemini-3.1 Pro | Qwen3.5-Omni-Plus |
|-----------|---------------|-------------------|
| DailyOmni | 82.7 | **84.6** |
| Qualcomm IVD | 66.2 | **68.5** |
| Omni-Cloze (Caption) | 57.2 | **64.8** |

### Zero-Shot 语音生成（SEED-TTS 测试集 WER ↓）

| 模型 | 中文 | 英文 |
|------|------|------|
| Qwen3.5-Omni-Plus | **0.99** | **1.26** |
| CosyVoice 3 | 0.71 | 1.45 |
| MiniMax-Speech | 0.83 | 1.65 |
| Qwen3-Omni-30B | 1.07 | 1.39 |

### 自定义语音多语言生成（WER ↓，29 语言）

Qwen3.5-Omni-Plus 在 29 个评估语言中的 22 个上取得最低 WER，显著优于 ElevenLabs、Gemini-2.5 Pro TTS、GPT-Audio 和 MiniMax-Speech。

## 范式对比

### vs Gemini-3.1 Pro（Google DeepMind）

| 维度 | Qwen3.5-Omni | Gemini-3.1 Pro |
|------|-------------|----------------|
| 架构 | Thinker-Talker 双轨 MoE | 原生多模态 Transformer |
| 语音生成 | 内置端到端（Talker + MTP + Code2Wav） | 外挂 TTS |
| 音频理解 | 独立 AuT 编码器（4000 万小时训练） | 统一编码 |
| 交互模式 | 全双工流式 + ARIA 动态对齐 | 半双工 |
| 开放程度 | API 可访问 | API 可访问 |
| 多语言 | 113 语言/方言识别，36 语音合成，201 文本 | 未披露 |

Qwen3.5-Omni 在音频理解/ASR 上全面领先 Gemini-3.1 Pro，且内置了端到端语音生成能力。

### vs GPT-5.6 Sol（OpenAI）

OpenAI 的 GPT-5.6 系列和 GPT-Live 也支持语音对话，但 GPT-Live 通过「委派」（delegation）方式将复杂工作交给 GPT-5.6 模型，而非端到端统一架构。Qwen3.5-Omni 走的是纯端到端路线，减少了系统复杂度和延迟，但在极端复杂推理任务上可能不如委派方案灵活。

### vs Qwen3-Coder-Next（自家产品线）

Qwen3-Coder-Next（80B total, 3B active）是纯文本代码 Agent 专用模型，而 Qwen3.5-Omni 是全模态通用模型。二者定位完全不同——前者追求编码 Agent 性价比，后者追求全模态交互的自然度。

## 可复用的工程经验

1. **Hybrid MoE + GDN 是大规模多模态的首选架构**。GDN 在长序列下显著降低 KV-cache I/O，对音频/视频这类高 token 量输入至关重要。

2. **音频编码器的训练数据规模是质量的关键**。AuT 消耗 4000 万小时数据，6.25Hz token 率（~160ms/token）平衡了计算效率和语义保真度。动态注意力窗口训练是兼顾实时 prefilling 和离线理解的关键。

3. **文本时间戳替代绝对位置 ID** 是一个简单但有效的工程技巧。解决了 TM-RoPE 在长视频输入下的稀疏化问题，且无需复杂的帧率适配数据采样。

4. **ARIA 将双通道生成转为单通道**。这是解决文本-语音 tokenizer 速率不匹配的优雅方案——用简单约束（累积比率 ≤ 全局比率）替代了复杂的对齐模型（MFA）。

5. **On-Policy Distillation 弥合模态间差距**。音频输入条件的响应质量天然低于文本输入条件，用文本条件下的输出作为蒸馏目标来训练音频条件分支，比直接 RL 更稳定高效。

6. **专精蒸馏 → 统一蒸馏的分阶段训法**。先训单模态专家 → 蒸馏到统一模型 → OPD 弥合模态差距 → Interaction-Aligned RL 优化交互体验。这种「先分裂再融合」的路径比从零开始训练全模态模型更可控。

7. **Token Saver 关键信息**：Qwen3.5-Omni 的 250k 词表相对 Qwen3.5 的 150k 词表，跨语言编码效率提升 10-60%，对多语言推理延迟有明显改善。
