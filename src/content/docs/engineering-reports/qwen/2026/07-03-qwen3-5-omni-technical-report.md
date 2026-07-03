---
title: Qwen3.5-Omni — Thinker–Talker 双 MoE 全模态架构，Audio-Visual Vibe Coding 涌现
date: 2026-07-03
source: https://arxiv.org/abs/2604.15804
---

# Qwen3.5-Omni Technical Report

**发布日期：** 2026-04（arXiv 提交日期）
**来源：** arXiv 2604.15804
**工程范式：** 全模态统一路线——Thinker–Talker 双 MoE 架构，用一个模型覆盖文本、图像、音频、视频的全模态理解和流式语音生成。

## 设计哲学

Qwen3.5-Omni 是 Qwen-Omni 系列的最新演进，核心设计理念是"一个模型做所有模态的事"——不仅是理解和生成，还要在实时交互中完成 agentic 行为。与 Qwen3-Coder-Next（专注 Coding Agent）不同，Omni 路线追求广度。

核心约束是跨模态的信息对齐和流式交互的低延迟。Qwen 团队选择不拆分任务（不用独立的 ASR/TTS 管道），而是用 Thinker–Talker 双模块架构统一处理。代价是训练和推理复杂度高（两个 MoE），收益是模态间信息无损传递和端到端优化。

## 关键架构决策

### Thinker–Talker 架构
- **Thinker**：接收多模态输入（文本/图像/音频/视频），生成文本响应
- **Talker**：基于 Thinker 的 high-level 表征，生成流式语音 token
- 两者均采用 **Hybrid-Attention MoE** 架构（相比 Qwen3-Omni 的改进）

### 音频 Transformer (AuT)
- 从头训练的 Transformer 音频编码器，在 **4000 万小时** 音频-文本数据上训练（由 Qwen3-ASR 生成）
- 音频下采样到 **6.25 Hz token 率**（一帧 ≈ 160ms）
- 支持动态注意力窗口，兼顾流式实时和离线处理

### 输入处理
- **文本：** Qwen3.5 tokenizer，BPE 250k 词汇表（从 150k 扩展），编码效率提升 10-60%
- **音频：** 16kHz → 128 通道 mel 频谱（25ms 窗口，10ms 步长）
- **视觉：** SigLIP2 编码器，视频动态帧率采样
- **时间戳：** 显式文本时间戳（秒级）预置到每个 patch，替代 TM-RoPE，在长上下文中时序对齐更好

### 流式语音生成
- RVQ（残差向量量化）token，多码本编解码器
- MTP（Multi-Token Prediction）模块建模残差码本
- 因果 ConvNet 编解码器，低延迟波形重建
- **ARIA**（Adaptive Rate Interleave Alignment）：自适应率约束，流式解码时动态对齐文本和语音单元

### 推理优化
- **Chunked Prefilling**：减少 TTFT（首包延迟）
- **GDN (Gated Delta Net)**：加速长序列建模，减少 KV-cache I/O
- 延迟数据：音频输入首包延迟 **235ms（Flash）/ 435ms（Plus）**

### 训练数据规模
- 超过 **1 亿小时** 音频-视觉内容
- 三阶段训练：
  1. 编码器对齐（S1）：LLM 冻结，训练视觉/音频编码器
  2. 通用阶段（S2）：全部参数解冻，~4T tokens
  3. 长上下文阶段（S3）：最大序列长度 262,144

### 后训练
- Thinker 三阶段：Specialist Distillation → On-Policy Distillation → Interaction-Aligned RL
- Talker 四阶段：General Stage → Long-Context Stage → RL (DPO) → GAN-based 微调

## 关键结果

- **215 项** 音频和音视频理解/推理/交互子任务和基准上达到 SOTA
- 关键音频任务上 **超越 Gemini-3.1 Pro**，综合音视频理解上持平
- 256k 上下文，支持 **10+ 小时音频**、**400 秒 720P 视频**（1 FPS）
- 语音识别覆盖 **113 种语言和方言**，语音合成覆盖 **36 种语言**
- 涌现能力：**Audio-Visual Vibe Coding**——直接基于音视频指令编程

| 延迟指标 | Flash (1并发) | Plus (1并发) |
|---------|-------------|-------------|
| Thinker TTFT (A/V) | 80/255 ms | 162/377 ms |
| Talker TTFC | 56/61 ms | 54/56 ms |
| 整体延迟 | 235/426 ms | 435/651 ms |
| 生成 RTF | 0.178 | 0.187 |

## 范式对比

与 Gemini 的能力密度路线不同，Qwen3.5-Omni 追求的是**模态覆盖度**。Google 在 Gemini 3.5 Flash 上走的是"把能力做小做快"路线，Qwen 走的是"把所有模态统一到一个模型"路线。

与 Qwen3-Coder-Next（同一公司的 Coding Agent 模型）相比，Omni 在编码能力上不专精，但获得了跨模态交互能力，包括 Audio-Visual Vibe Coding 这一涌现能力。

## 社区评价

缺乏 Reddit/HN 上的深度讨论。中文社区（知乎、CSDN）有初步介绍，但尚未有深入的 benchmark 验证报告。

## 可复用的工程经验

1. **显式时间戳优于位置编码**：用格式化时间戳字符串预置到视频 patch 和音频序列，比 TM-RoPE 在长序列上时序对齐更好，且实现简单。
2. **ARIA 解决了流式 TTS 的关键矛盾**：文本 tokenizer 和语音 tokenizer 的编码效率差异会导致流式合成不稳定，ARIA 的自适应率约束优雅地解决了这个问题。
3. **On-Policy Distillation 对齐模态质量**：用文本条件响应作为高质量目标来对齐音频条件响应，减少模态间的质量差距。
4. **Specialist Distillation 比统一 SFT 更优**：先训练多个领域专家模型，再蒸馏合并到统一模型，比直接在统一模型上做多领域 SFT 效果更好。
