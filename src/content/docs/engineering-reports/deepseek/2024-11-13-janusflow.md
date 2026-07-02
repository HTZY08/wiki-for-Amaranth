---
title: JanusFlow — 自回归与 Rectified Flow 的统一融合
date: 2024-11-13
source: arXiv 2411.07975
---

# JanusFlow

**发布日期：** 2024-11-13
**来源：** arXiv 2411.07975
**工程范式：** 将 Rectified Flow 融入 LLM 框架，实现比 VQ 更优的视觉生成质量。

## 设计哲学

Janus 的 VQ tokenizer 方案存在固有局限：离散 tokenization 会丢失像素级细节，限制生成质量。JanusFlow 的突破是用 Rectified Flow（即连续扩散流）替代 VQ 生成，保留自回归框架处理理解任务，但将图像生成建模为连续空间中的最优传输问题。关键洞察是 Rectified Flow 可以在 LLM 框架内以最小架构改动实现——只需要一个生成编码器（ConvNeXt）+ 一个生成解码器，LLM 本身充当 denoiser。为弥合理解编码器（SigLIP 语义特征）和生成编码器（flow latent）之间的表示差异，引入表示对齐正则化损失。

## 关键架构决策

- **理解通路：** SigLIP-L → 线性投影 → LLM（标准自回归）
- **生成通路：** VAE 潜在空间 → ConvNeXt 编码器 + 时间嵌入 → LLM（作为 denoiser）→ 生成解码器 → Euler solver → VAE 解码器
- **Causal Attention：** 生成通路使用因果注意力，实验发现 mask 无性能提升
- **表示对齐：** 生成阶段的 LLM 中间层特征与冻结的 SigLIP 特征做余弦相似度正则化
- **Classifier-Free Guidance：** 10% 文本 dropout

## 关键结果

JanusFlow 1.3B 在 GenEval 上达 0.63，DPG-Bench 达 80.09%，均超越 Janus（0.61, 未报告）和 SDXL（0.55, 74.65%）。理解任务上 POPE 88.0、MME-P 1333.1，与 Janus 相当。在生成质量上接近专属扩散模型水平。

## 范式对比

与 Janus（VQ 离散生成）相比，JanusFlow 的连续生成路径在 GenEval 上提升 2pp，DPG-Bench 上大幅领先。与 Transfusion（同时训练 AR+扩散但共享编码器）相比，解耦+对齐方案避免了任务冲突。

## 可复用工程经验

1. Rectified Flow 可以无缝嵌入 LLM 框架，架构改动极小
2. 连续生成（Flow）优于离散生成（VQ），尤其在密集指令跟随场景
3. 表示对齐（representation alignment）是缓解多任务冲突的有效正则化手段
4. CFG 在 LLM 框架内同样有效，10% dropout 是最优配置
