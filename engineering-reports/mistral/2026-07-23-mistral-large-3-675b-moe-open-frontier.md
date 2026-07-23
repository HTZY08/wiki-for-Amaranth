---
title: Mistral Large 3 — 675B MoE 开源前沿的工程路线
date: 2025-12-02
source: https://mistral.ai/news/mistral-3/
---

# Mistral Large 3 — 675B MoE 开源前沿的工程路线

**发布日期：** 2025-12-02（模型与博文同时发布）
**来源：** https://mistral.ai/news/mistral-3/ | https://docs.mistral.ai/models/model-cards/mistral-large-3-25-12
**工程范式：** 以 41B/675B 的稀疏 MoE 实现开源模型的前沿性能，走"广度优先"路线——强调通用知识、多语言、多模态、agent 能力的均衡覆盖，而非极端推理深度的单点突破

## 设计哲学

Mistral Large 3 是 Mistral AI 自 Mixtral 系列以来首个 MoE 旗舰，也是其从纯文本小模型扩展为多模态大模型的转型之作。核心约束：**在 Apache 2.0 许可下，用可持续的硬件预算（3000 张 H200）训练一个可部署在单节点 8×GPU 上的前沿模型。**

三个关键权衡：

1. **激活参数优先于总参数：** 41B active / 675B total 意味着 1:16 的激活比——每 token 仅激活 6% 的参数。这与 DeepSeek-V3.2 的 MLA + MoE 设计思路一致（用稀疏性降低推理成本），但 Mistral 选择了更"粗粒度"的激活比（DS V3.2 未公开 exact activation ratio，但 V3 约 37B/671B ≈ 1:18）。
2. **通用知识 > 深度推理：** GPQA Diamond ~43.9% 反映了这一权衡——模型优先保证多语言、多轮对话、工具使用的通用能力，而非数学/推理的极限。放弃的是"在每项基准上争第一"的定位。
3. **开放生态优先：** Apache 2.0 + NVFP4 quantization + vLLM/SGLang/TensorRT-LLM 多框架支持。放弃的是封闭生态的专属优化收益。

## 关键架构决策

### MoE 设计

- **粒度的选择：** 官方描述为"granular Mixture-of-Experts"，具体专家数和路由策略未完全公开。已知总参数 675B，激活参数 41B（per token），激活比约 6%
- **视觉处理：** 独立的 2.5B 视觉编码器，支持文本+图像双模态输入
- **上下文长度：** 256K tokens，原生支持
- **训练基础设施：** 3000× NVIDIA H200 GPU（Hopper 架构），HBM3e 高带宽内存

### 注意力机制

- 具体注意力选型未在公开资料中详细披露。基于 Mistral 系列历史（Mistral 7B 使用 grouped-query attention 和 sliding window attention），Large 3 大概率延续了 GQA + SWA 的设计路线
- 256K 上下文的支持暗示了某种形式的 long-context 优化（可能是 sliding window + 全局注意力的混合）

### 多模态架构

- 2.5B 视觉编码器处理图像输入
- 编码器输出的视觉 token 通过投影层映射到 LLM 的 embedding 空间
- 不支持音频或视频输入（有别于 Gemini 等）

### 训练策略

- 训练数据来源：公开数据 + 授权数据 + 合成数据，具体规模未披露
- 多语言覆盖：40+ 语言原生支持
- 训练细节（optimizer / batch size / learning rate schedule）未公开

### Post-training

- Instruction tuning 面向 agent 场景优化：原生 function calling、JSON mode、tool use
- NVFP4 量化感知训练：与 NVIDIA 合作，llm-compressor 工具链支持，可在 Blackwell NVL72 和单节点 8×A100/H100 上运行
- 投机解码（speculative decoding）：NVIDIA 集成支持，降低长上下文吞吐场景的延迟

### 推理优化

- **NVFP4 量化**：与 NVIDIA 合作开发，A100/H100 上可用 4-bit 浮点推理
- **Blackwell 优化的 MoE/Attention 内核**：NVIDIA 提供针对 GB200 NVL72 及以上配置的底层优化
- **Prefill/Decode 分离**：支持长上下文场景的预填充和解码分离部署
- **GGUF 量化**：社区提供，可在 4×RTX 4090（Q4）上运行

## 关键结果

| 基准 | Mistral Large 3 | 同级开源模型* |
|------|:---:|:---:|
| MMLU (8-language, 5-shot) | ~85.5% | 未披露 |
| HumanEval (pass@1) | ~92% | 未披露 |
| GPQA Diamond | ~43.9% | 未披露 |
| LMArena OSS 排名 | #2 (非推理类) | #6 (包含推理类) |
| 上下文长度 | 256K | - |
| API 价格（输入） | $0.5/M tok | - |
| API 价格（输出） | $1.5/M tok | - |

*官方未提供与其他开源模型的直接并排对比表，以上数据来自独立测试和第三方编译。

**LMArena 表现：** Mistral Large 3 在开源非推理模型类别排名第二，在所有开源模型中排名第六。这一排名反映了其在通用对话、多语言、多模态任务上的综合竞争力。

## 范式对比

**vs DeepSeek-V3.2 (671B/37B MoE)：** 两者在总参数量和激活参数比上非常接近。关键差异：
- DeepSeek 在 reasoning 上更激进（12.5% 的 HLE 精度 vs 未知），Mistral 更强调多语言和工具使用
- DeepSeek 有完整的 arXiv 技术报告（含 DSA、RL scaling 等创新），Mistral Large 3 依赖博文 + 模型卡，缺少系统性公开
- Mistral 的 Apache 2.0 许可证比 DeepSeek 的社区许可证更开放

**vs Ministral 3（已在 wiki 中）：** 两者是不同定位的产品。Ministral 3（3B/8B/14B Dense）面向边缘/本地部署，Large 3 面向数据中心部署。Ministral 3 有独立的 arXiv 技术报告，Large 3 没有。

**vs Mixtral 8x22B（Mistral 上一代 MoE）：** 从 141B/39B MoE（8×22B）扩展到 675B/41B MoE，总参数增长 4.8 倍，激活参数增长仅 5%。表明 Mistral 的策略是保持激活参数大致恒定、通过增加总参数来扩展知识容量。

**vs Gemma 4 (31B Dense)：** Gemma 4 走相反路线——纯 Dense + 参数效率（31B 全激活），Mistral 用 41B 激活的 MoE 比 Gemma 4 的 31B Dense 拥有更大的总知识容量但推理开销更高。两种路线各有适用场景。

**核心差异：** Mistral Large 3 是唯一一个在 Apache 2.0 下提供 >600B 参数 MoE 的模型。Meta 的 Llama 4（402B/17B）使用自定义社区许可证，DeepSeek 使用自定许可证。Mistral 的开源姿态最激进。

## 社区评价

- 开源社区对 Mistral Large 3 的 NVFP4 量化和 8×A100 部署能力给予高度评价，认为它"真正让前沿模型可自托管"
- NVIDIA 的深度合作（Blackwell 内核、TensorRT-LLM 集成）被视为"硬件-模型联合设计的典范"
- 部分社区成员认为缺少详细技术报告（arXiv 论文）是遗憾，使得架构细节难以复现和评估
- API 定价（$0.5/$1.5 per M token）被认为在"开源模型价格和闭源模型质量之间找到了平衡点"

## 可复用的工程经验

1. **NVFP4 量化 + 量化感知训练**：与 NVIDIA 合作开发的 4-bit 浮点量化路线可以在 H100/A100 上运行 675B 模型。这比传统 INT4 量化更适合 MoE 架构（保留浮点动态范围对 expert routing 至关重要）
2. **开源策略与开发者体验一体设计**：同时支持 vLLM、SGLang、TensorRT-LLM、Ollama 四个推理框架，配合 NVIDIA + Red Hat 的联合优化，确保模型发布即可用
3. **Pre-fill/Decode 分离的 MoE 服务架构**：对长上下文（256K）MoE 推理而言，预填充和解码分离部署可以让两个阶段的资源利用率最优化
4. **MoE 的 "2B active 就够了" 设计思路**：从 Mixtral 8x22B（39B active）到 Large 3（41B active），激活参数几乎不变——说明 Mistral 认为 40B 左右的激活参数在 2025 年底是一个"甜点区"，更大的模型收益来自增加总参数而非激活参数
