---
title: DeepSeek-VL2 — MoE VLM 与动态平铺视觉编码
date: 2024-12-13
source: arXiv 2412.10302
---

# DeepSeek-VL2

**发布日期：** 2024-12-13
**来源：** arXiv 2412.10302
**工程范式：** MoE 架构 × MLA 注意力 × 动态平铺视觉编码的联合系统设计。

## 设计哲学

DeepSeek-VL2 是将 DeepSeek 在 LLM 层面的技术积累（MoE、MLA）系统性迁移到多模态领域的产物。核心设计原则是"每个 token 的激活参数尽量少，但总参数容量尽量大"。三个规模档位——Tiny（1.0B 激活/3B 总）、Small（2.8B/16B）、VL2（4.5B/27B）——覆盖不同部署场景。视觉方面引入动态平铺策略：候选分辨率集合 CR = {(m×384, n×384) | m,n ≥ 1, m×n ≤ 9}，自动选择最优切分，使一个 384x384 的 SigLIP 编码器能处理任意宽高比的高分辨率图像。

## 关键架构决策

- **视觉编码：** 单 SigLIP-SO400M-384 + 动态平铺（每 tile 27×27=729 tokens，pixel shuffle 压缩至 196）+ 全局缩略图
- **LLM：** DeepSeekMoE（64-72 routed experts + 2 shared experts, top-K=6）+ MLA（KV cache 压缩至 rank=512 latent）
- **训练数据：** 三阶段——对齐（仅 vision encoder+adaptor）、预训练（70% VL+30% text）、SFT。视觉 grounding 数据：标准化坐标格式和负样本。增量数据：YFCC、Docmatix、内部高质标注
- **特殊 token：** tile_newline、view_separator、grounding/ref/det 标记序列，支持细粒度视觉定位和 GUI 感知

## 关键结果

DeepSeek-VL2（4.5B 激活/27B 总参）在 MMBench 1.0/1.1 等多个基准上超越 InternVL2-8B、Qwen2-VL-7B 等稠密模型，在 OCRBench 上达 SOTA。动态平铺使高分辨率图像处理效率大幅提升——与固定全局分辨率方案相比，计算量减少 30%+。

## 范式对比

与 DeepSeek-VL（稠密 LLM）相比，VL2 的 MoE 架构用更少激活参数实现更强能力，验证了 MoE 在多模态领域的有效性。与 Qwen2-VL（动态平铺+稠密）相比，VL2 的 MLA 带来了更高效的推理。与 InternVL2（大规模稠密）相比，激活参数仅为其 1/3-1/2。

## 可复用工程经验

1. 动态平铺处理高分辨率图像比固定切分更灵活高效
2. MoE+MLA 组合在 VLM 场景下激活参数效率优势明显
3. 视觉 grounding 数据格式标准化后大幅降低标注成本
4. 三阶段训练 + 70/30 模态比从 DeepSeek-VL 延续改进
