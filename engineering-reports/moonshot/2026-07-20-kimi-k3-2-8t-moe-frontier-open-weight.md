---
title: Kimi K3 — 2.8T MoE + Stable LatentMoE + Kimi Delta Attention，全球最大开源权重模型
date: 2026-07-20
source: https://arxiv.org/abs/2603.20633
---

# Kimi K3

**发布日期：** 2026-07-18（低调发布，WAIC 演示）；2026-07-27（计划开源权重）
**来源：** [BBC](https://www.bbc.com/news/articles/cy9w4q8pgp0o) | [AP News](https://apnews.com/article/kimi-k3-china-ai-0d8a5e268deb11a673f4d444fc597cc5) | [Delante 深度分析](https://delante.co/kimi-k3/)
**工程范式：** 2.8T 总参数/896 专家/16 活跃的极致细粒度 MoE，通过 Stable LatentMoE 框架和 Kimi Delta Attention 在 1M 上下文窗口上实现开源最大规模模型

## 设计哲学

Kimi K3 来自中国 AI 创业公司 Moonshot AI（月之暗面），是开源 AI 模型的里程碑：**全球首个 3 万亿参数级别的开源权重模型**，且性能在多个维度上超越 GPT-5.5、匹敌 Anthropic Claude Fable 5。

核心约束：在 US GPU 出口限制下，用可获取的算力实现世界级前沿模型。

关键设计选择：
- **极细粒度 MoE（896 专家 × 16 活跃）：** 不是常规的 8/16/64 专家，而是 896 个专家的极高粒度——更细的知识专业化但路由复杂度更高
- **Stable LatentMoE 框架：** 私有路由框架，与标准 top-k routing 不同，能更稳定地在分布式训练中收敛
- **Kimi Delta Attention（KDA）：** Moonshot 自研注意力机制变体，优化深层模型的信息流动稳定性
- **Attention Residuals（AttnRes）：** 受残差连接启发的注意力层改进
- **始终在线推理模式：** 不是可选 toggle，而是通过 `reasoning_effort="max"` 参数默认启用的深度思考
- **原生 1M token 上下文窗口**

**放弃的路线：**
- 不追求纯 Dense 扩展（Scaling Law 在纯 Dense 上已到边际收益递减点）
- 不追求闭源 API 封闭生态——开源策略直接对标 DeepSeek 的开放路线
- 不采用事后多模态——视觉和文本推理在同一框架内处理

## 关键架构决策

### 模型规格

| 特性 | Kimi K3 |
|------|---------|
| 总参数 | **2.8 万亿（2.8T）** |
| 活跃参数 | 未披露（16/896 专家活跃，估计 ~50-100B） |
| 架构 | 稀疏 MoE + Stable LatentMoE |
| 专家数 | **896** |
| 激活专家 | **16**（top-16 routing）|
| 注意力机制 | Kimi Delta Attention (KDA) + Attention Residuals (AttnRes) |
| 上下文窗口 | 原生 1M tokens |
| 推理模式 | 始终开启 deep thinking（`reasoning_effort="max"`）|
| 训练效率 | 约为 K2 的 2.5 倍扩展效率 |
| 发布日期 | 2026-07-18（API + 网页 playground）|
| 开源日期 | 2026-07-27（计划）|
| 开源许可 | 开放权重（Open-weight）|

**参数量对比（全球最大开源模型）：**

```
Kimi K3           ████████████████████████████████ 2.8T ★ 全球最大
DeepSeek V4 Pro   █████████████████               1.6T
Llama 4 Maverick  █████                            402B
```

### Stable LatentMoE

Moonshot 未公开 Stable LatentMoE 的完整技术细节，但从公开信息可推断关键创新点：

- **隐空间路由（Latent Routing）：** 不同于标准 MoE 在 token embedding 空间做 top-k routing，Stable LatentMoE 将 token 投影到低维隐空间后再路由，降低了路由器的维度爆炸压力
- **稳定性保障：** 标准 MoE 在 896 专家规模下路由收敛困难（专家坍缩、负载不平衡），Stable LatentMoE 通过隐空间约束 + 额外的辅助损失函数保障训练的稳定性
- **2.5 倍扩展效率：** 相对 K2，K3 的扩展效率提升了约 2.5 倍——这意味着同样算力投入下 K3 比 K2 学到更多

### Kimi Delta Attention (KDA)

KDA 是针对极深层 Transformer 的注意力机制改进：

- **增量注意力更新：** 标准注意力每层从零计算 QKV 乘积，KDA 引入层间的注意力增量更新——当前层的注意力是前一层注意力的 delta 修正，而非全新计算
- **减少注意力方差：** 在 80+ 层 Transformer 中，深层注意力分布趋向均匀（attention sink），KDA 通过残差式的注意力更新维持深层注意力的聚焦能力

### Attention Residuals (AttnRes)

与 KDA 配套的架构创新：
- 将注意力输出也加入残差路径（不仅是标准的 pre-norm 残差连接）
- 将前一层 attention map 的局部信息通过跳跃连接传递到深层
- 论文 "Attention Residuals" (arXiv:2603.15031) 由 Moonshot AI 发表

### 定价策略

| 指标 | Kimi K3 | Claude Opus 4.8 |
|------|---------|-----------------|
| 输入价格 | **$3/M tokens** | ~$15/M tokens |
| 输出价格 | **$15/M tokens** | ~$75/M tokens |
| 性价比 | 约 50% 每任务成本 | 基线 |

## 关键结果

### 独立评估

**Artificial Analysis Elo：1,547**
- 超过 GPT-5.5（未披露具体 Elo）
- 仅次于 Claude Fable 5（最高分）
- 排名第一的 Web 界面工程基准（blind human-preference test 中超过 Fable）

**Arena.ai 排名：**
- 匹敌 OpenAI GPT 和 Anthropic Claude 系列
- 在盲测中展现具有竞争力的 top-line 性能

**第三方评估关键发现：**
- 长程编码任务：K3 在需要持续数小时的无监督工程任务中表现出色（少引导、自校验、持续执行）
- 多模态视觉推理：通过屏幕截图和实时视觉反馈优化工作流（前端开发、CAD 设计、视频游戏开发）

## 范式对比

**vs DeepSeek V4 Pro（1.6T MoE）：** K3 的 2.8T 总参数几乎是 V4 的两倍，且 K3 的 896 专家远比 V4 细粒度。但 V4 Pro 的激活参数（49B）可能高于 K3 的活跃参数（未公开）。两者的核心差异在于：DeepSeek 在 MLA（Multi-Head Latent Attention）上更激进地压缩 KV cache，而 K3 在注意力机制上选择 KDA + AttnRes。

**vs Llama 4（402B/17B MoE）：** K3 总参数是 Llama 4 Maverick 的 7 倍。Llama 4 Scout 的 10M 上下文远超 K3 的 1M，但 K3 的 2.8T 总参数代表截然不同的设计方向——用极致参数规模换取更高的知识容量。

**vs Anthropic Claude Fable 5（闭源）：** K3 在 Elo 上仅次于 Fable 5，但 K3 开源而 Fable 5 闭源。这一对比被业界解读为"开源模型首次在性能上逼近闭源前沿"的转折点。

**vs Kimi K2.5（2602.02276）：** K2.5 是视觉/agentic 方向的产品，强调 GUI 理解和多模态 agent。K3 是通用旗舰，强调参数规模和纯推理/编码能力。两条路线互补而非替代。

## 社区评价

2026-07-22 当前，Kimi K3 是 AI 社区最热议的话题：

1. **"单月最大发布"评价：** AP News 引用业界评论称"这可能是今年最大的一次 AI 模型发布"

2. **市场冲击：** Zhipu 股价暴跌 27%，MiniMax 暴跌 16%。HK 市场的反应说明了 K3 的"鲶鱼效应"

3. **Geo-political 影响：** BBC 报道强调 K3 表明"尽管美国出口管制持续，中国已成功确保在前沿 LLM 发展中的前沿地位"

4. **订阅暂停：** K3 发布后因流量暴增暂停新用户注册——这是"需求冲击"而非技术故障

5. **开源争议：** 部分开发者质疑 Moonshot 能否在 7 月 27 日准时开源 2.8T 模型（分发和托管挑战巨大）

## 可复用的工程经验

1. **隐空间路由（Latent Routing）的稳定性收益：** 在高专家数（896）场景下，在隐空间中做路由比在原始 token embedding 中更稳定。这一思路可以移植到其他大规模 MoE 系统中。

2. **注意力残差（AttnRes）：** 将注意力输出加入残差路径是一个简单但有效的改进，特别对 80+ 层的极深 Transformer。实现成本低（几乎没有额外参数），收益主要在训练稳定性上。

3. **极细粒度 MoE 的 trade-off：** 896 专家 × 16 活跃意味着路由器的选择空间更大（C(896,16) 的决策空间），但通信和存储开销也相应增加。K3 的实践证明即使在受限计算条件下，细粒度 MoE 仍是可行的扩展方向。

4. **定价作为竞争武器：** K3 以 GPT-5.5 和 Claude 约 20-50% 的价格提供可比性能——开源 + 低价定价的组合具有巨大的市场破坏力。对于 API 服务商而言，这意味着用边际定价而非绝对性能来竞争。
