---
title: AI 信息前沿
description: 重大 AI 事件、新模型发布、关键架构突破的持续记录与合并
---

本页持续记录 AI 领域的重要事件，按时间线排列。不是日报，是**里程碑索引**——值得长期记住的模型发布、架构突破、定价变化、产业拐点。

---

## 2026年6月

### 🏛️ 白宫 AI 行政令 — 促进先进 AI 创新与安全

**时间**：2026年6月2日  
**发布方**：美国白宫，特朗普总统  
**官方文本**：[EO 14409](https://www.whitehouse.gov/presidential-actions/2026/06/promoting-advanced-artificial-intelligence-innovation-and-security/)

**核心内容**：
- 要求联邦机构在 30 天内强化网络防御能力
- 建立 AI 网络安全信息交换所（clearinghouse）
- 指示司法部优先起诉利用 AI 非法访问计算机系统的行为
- 建立政府与领先 AI 开发商的网络安全评估协作机制

**定位**：特朗普第二任期首份专门针对 AI 安全的行政令，延续了拜登政府以来的 AI 治理思路但更侧重国家安全与执法。

**相关**：[Fact Sheet](https://www.whitehouse.gov/fact-sheets/2026/06/fact-sheet-president-donald-j-trump-promotes-advanced-artificial-intelligence-innovation-and-security/)

---

### 🧠 Anthropic 发布 Claude Fable 5 / Mythos 5 — 新世代旗舰

**时间**：2026年6月9日  
**发布方**：Anthropic  
**官方公告**：[Claude Fable 5 and Claude Mythos 5](https://www.anthropic.com/news/claude-fable-5-mythos-5)

**产品线**：
- **Claude Fable 5** — Mythos 级能力的安全版，向全量用户开放。已在 claude.com 定价页列为最高档模型
- **Claude Mythos 5** — 解除安全限制，通过 Project Glasswing 向美国政府/网络防御合作伙伴提供

**定价**：$10/百万输入 tokens，$50/百万输出 tokens（不到 Mythos Preview 的一半）

**离谱的实测案例**：

| 领域 | 表现 |
|------|------|
| **软件工程** | Stripe 一天内迁移 5000万行 Ruby 代码库（原估团队 >2个月）；CursorBench SOTA |
| **知识工作** | Hebbia Finance Benchmark 最高分 |
| **视觉** | 纯截图打穿 Pokémon FireRed（无地图/导航辅助）；从截图重建 Web App 源码 |
| **记忆** | Slay the Spire 中持久记忆比 Opus 4.8 好 3 倍 |
| **药物设计 (Mythos 5)** | 14个蛋白靶点中 9 个出强候选，加速 ~10× |
| **基因组学** | 自训练 ML 模型击败 *Science* 论文模型，体积小 100× |

**安全机制**：分类器兜底——<5% 会话降级到 Opus 4.8。外部赏金 >1000 小时无通用越狱。UK AISI 在初始窗口内取得部分进展。30 天数据留存策略。

**定位**：Fable 5 是 Anthropic 目前对全量用户开放的最强模型，定位在 Opus 4.8 之上。

**相关**：[官方公告](https://www.anthropic.com/news/claude-fable-5-mythos-5) | [Pricing](https://claude.com/pricing) | [System Card](https://anthropic.com/claude-fable-5-mythos-5-system-card)

---

### 🔬 Google DeepMind 发布 DiffusionGemma 26B-A4B — 文本扩散架构突破

**时间**：2026年6月9日（模型卡）/ 6月10日（正式公告）  
**发布方**：Google DeepMind  
**许可**：Apache 2.0（开源开放权重）  
**官方博客**：[DiffusionGemma: 4x faster text generation](https://blog.google/innovation-and-ai/technology/developers-tools/diffusion-gemma-faster-text-generation/)

**核心突破**：
- **首个开源文本扩散语言模型** — 摒弃传统的自回归逐 token 解码，改用扩散方法并行生成 256-token 块
- **推理速度**：在专用 GPU 上最高可加速 4×
- **架构**：26B 总参数 / 3.8B 激活参数（MoE），256K token 上下文窗口
- **多模态输入**：支持文本、图片、视频输入
- **功能**：可配置思维链推理模式、原生函数调用

**代价**：在标准评测基准上，DiffusionGemma 略逊于同尺寸的 Gemma 4。官方明确标注为"实验性"模型。

**意义**：文本扩散路线首次以可用形式开源，可能改变未来 LLM 推理的设计范式——不再强制逐 token 生成。

**相关**：[Hugging Face (NVidia FP4)](https://huggingface.co/nvidia/diffusiongemma-26B-A4B-it-NVFP4) | [Developer Guide](https://developers.googleblog.com/diffusiongemma-the-developer-guide/)

---

### 🏎️ 小米 MiMo-V2.5-Pro UltraSpeed — 1000 TPS

**时间**：2026年6月9日  
**发布方**：小米 MiMo 团队 + TileRT  
**核心指标**：万亿参数 MoE 模型，单台 8 卡通用 GPU 节点，文本生成速度 1000 TPS（峰值 1200 TPS）

**技术路线**（三管齐下）：
1. **FP4 量化** — 针对 MoE 架构仅对专家层做无损压缩，减少模型体积
2. **DFlash 推测解码** — 挂载轻量级 drafter 模型，一次草稿 8 个候选 token，大模型只出场一次验证整块。平均单轮确认 6-7 个 token，大模型出场次数直接除以 8
3. **TileRT 工程调度** — 算子间交接间隙压到微秒级：一次开线、持续运转

**代价**：价格是标准版的 **3 倍**。官方宣称"更快因此更便宜"的逻辑引发社区争议——按 token 计费下 3 倍价格如何得出更便宜的结论？

**社区评价**：「AI 界安兔兔跑分」「不明觉厉」「分给 50 个用户还能保持同样智力水平吗？」

**对比参照**：GPT 5.5 标准输出 ~50-60 tkps，高速模式 ~100 tkps。MiMo UltraSpeed 是 GPT 5.5 高速模式的 ~10 倍。

**相关**：[知乎讨论](https://www.zhihu.com/question/2047628080479524844)

---

### 📝 Moonshot AI 开源 Kimi K2.7 Code — 编程专注的开放权重模型

**时间**：2026年6月12日  
**发布方**：Moonshot AI（月之暗面）  
**许可**：开放权重（Apache 2.0 式许可）  
**官方**：[Kimi K2.7 Code](https://kimik2ai.com/k2.7/)

**核心参数**：
- 1 万亿参数 MoE 模型，256K 上下文窗口
- 专注于 agentic 代码生成和长周期软件工程任务
- 推理 token 消耗降低约 30%（相比 K2.6）
- 文本输入/文本输出

**基准提升**：
- Kimi Code Bench v2：+21.8%
- Program Bench：+11.0%
- MLS Bench Lite：+31.5%

**社区反应**：VentureBeat 报道指出"基准与现实有差距"——部分从业者认为 K2.7 Code 在标准化基准上表现亮眼，但实际 agentic 编码场景的提升未完全反映在分数中。

**定位**：延续 K2.6 的开源路线，进一步压低推理成本，目标是挑战 Claude Code 和 OpenAI Codex 在 agentic 编程领域的地位。

**相关**：[MarkTechPost](https://www.marktechpost.com/2026/06/12/moonshot-ai-releases-kimi-k2-7-code-a-coding-model-reporting-21-8-on-kimi-code-bench-v2-over-k2-6/) | [VentureBeat](https://venturebeat.com/technology/kimi-k2-7-code-cuts-thinking-tokens-30-practitioners-say-benchmarks-dont-check-out)

---

### 🏛️ Z.ai (智谱) 发布 GLM-5.2 — 国产开源模型的里程碑

**时间**：2026年6月13日  
**发布方**：Z.ai（原名智谱 AI / Zhipu AI）  
**许可**：开放权重（开源）  
**官方公告**：[GLM-5.2: Built for Long-Horizon Tasks](https://z.ai/blog/glm-5.2)

**核心参数**：
- **744B 总参数 / 40B 激活参数**（MoE 架构），与 GLM-5.1 同尺寸
- **1M token 上下文窗口** — 可一次装入完整代码库
- 在独立开放权重排行榜上位居榜首

**基准表现**：
- 在多项长周期编码基准上超过 GPT-5.5
- API 成本约为 GPT-5.5 的 **1/6**
- 在编码基准上同时超过 Google 的同尺寸开放模型

**定价**：未公开详细价格，但官方强调显著低于 GPT-5.5

**意义**：GLM-5.2 标志着中国开源模型首次在关键基准（长周期编码）上系统性超越 OpenAI 的对应产品线。1M 上下文 + 开放权重的组合使其在开发者生态中迅速获得关注。

**相关**：[VentureBeat](https://venturebeat.com/technology/z-ais-open-weights-glm-5-2-beats-gpt-5-5-on-multiple-long-horizon-coding-benchmarks-for-1-6th-the-cost) | [SCMP 报道](https://aiweekly.co/alerts/zhipu-ais-glm-52-outscores-gpt-55-on-coding-benchmarks) | [API 文档](https://docs.z.ai/release-notes/new-released)

---

### 🏢 字节跳动发布 Seed 2.1 Pro / Turbo — 豆包旗舰模型

**时间**：2026年6月23日（火山引擎）/ 6月24日（全球发布）  
**发布方**：字节跳动（ByteDance）— 火山引擎 / Doubao  
**官方**：[Seed 2.1 发布页](https://seed.bytedance.com/en/seed2_1)

**产品线**：
- **Seed 2.1 Pro** — 旗舰版，面向复杂推理、长周期 Agent 任务、代码生成。匹配 Claude Opus 4.6 级别能力
- **Seed 2.1 Turbo** — 轻量版，面向规模化生产部署

**核心变化**：
- 在四个维度达到"生产级质变点"：信息分析、方案设计、内容策划、结果整合
- 日 token 消耗量大幅增长，反映在企业级部署中的快速采用
- 集成了 agent 式工作流（前台开发、长周期任务编排）

**定价**：通过火山引擎 API 提供

**定位**：字节跳动在闭源大模型领域的最新旗舰，直接对标 Anthropic Claude Opus 和 OpenAI GPT-5.5。在中国 AI 厂商中，字节/豆包是日活和调用量最大的消费级 AI 产品之一。

**相关**：[LLM Stats](https://llm-stats.com/models/seed-2.1-pro) | [Dataconomy](https://dataconomy.com/2026/06/24/bytedance-launches-doubao-2-1-pro-language-model/) | [Fello AI 评测](https://felloai.com/seed-2-1-pro/)

---

### 🔧 OpenAI 发布首款自研推理芯片 Jalapeño — 联手 Broadcom

**时间**：2026年6月24日  
**发布方**：OpenAI + Broadcom  
**官方公告**：[OpenAI and Broadcom unveil LLM-optimized inference chip](https://openai.com/index/openai-broadcom-jalapeno-inference-chip/)

**核心细节**：
- **首款自研 AI 推理芯片** — 对标 NVIDIA Blackwell 的定制 ASIC
- **开发周期**：从设计到 tape-out 仅 9 个月，期间使用 OpenAI 自身模型加速芯片设计
- **尺寸**：reticle-sized ASIC（掩膜版极限尺寸）
- **合作伙伴**：Broadcom 提供硅设计和制造，Celestica 提供机架技术
- **部署时间表**：计划 2026 年底开始部署

**意义**：
- OpenAI 加入 Google（TPU）、Apple、SpaceX 等自研芯片阵营，减少对 NVIDIA 的依赖
- 9 个月 tape-out 速度（行业平均 18-24 个月）展示了 AI 辅助芯片设计的潜力
- 推理专用芯片可能大幅降低 API 成本

**相关**：[TechCrunch](https://techcrunch.com/2026/06/24/openai-unveils-its-first-custom-chip-built-by-broadcom/) | [Tom's Hardware](https://www.tomshardware.com/tech-industry/artificial-intelligence/broadcom-and-openai-unveil-custom-built-jalapeno-inference-processor-openais-first-chip-is-a-massive-reticle-sized-asic-built-in-an-ultra-fast-nine-month-development-cycle) | [Reuters](https://www.reuters.com/world/asia-pacific/openai-unveils-custom-chip-it-designed-with-broadcom-boost-its-ai-infrastructure-2026-06-24/)

---

### 🌞 OpenAI 预览 GPT-5.6 系列：Sol / Terra / Luna — 三梯队新旗舰

**时间**：2026年6月26日  
**发布方**：OpenAI  
**官方公告**：[Previewing GPT-5.6 Sol: a next-generation model](https://openai.com/index/previewing-gpt-5-6-sol/)  
**System Card**：[Deployment Safety Hub](https://deploymentsafety.openai.com/gpt-5-6-preview)

**产品线**：

| 模型 | 定位 | 输入价格 | 输出价格 |
|------|------|---------|---------|
| **GPT-5.6 Sol** | 旗舰，最强推理/编码/安全 | $5/M tokens | $30/M tokens |
| **GPT-5.6 Terra** | 平衡，日常工作的性价比选择 | $2.50/M tokens | $15/M tokens |
| **GPT-5.6 Luna** | 最快、最经济，高吞吐场景 | $1/M tokens | $6/M tokens |

**核心能力**：
- **Sol** 在编码、科学推理、网络安全领域达到 OpenAI 最高水平
- 新增 **"Max Reasoning"** 模式和 **Ultra Subagent** 模式，支持长时间深度推理链
- 全系列支持最高 1M token 上下文
- Agentic 能力大幅提升：coding、biology、cybersecurity 三领域均有突破

**安全与监管**：
- **仅限于约 20 个美国政府批准的合作伙伴** — 这是史上首次由美国政府直接审批谁可以使用前沿 AI 模型
- 白宫要求推迟公开部署，理由是国家安全考量（网络安全能力提升显著）
- OpenAI 公开表示这一限制"不可持续"（unsustainable），但配合政府要求

**社区影响**：
- Sol 的定价（$5/$30 每 M token）约为 Anthropic Fable 5 的一半，直接对标竞争
- 在多项内部评测中 Sol "可与 Claude Fable 5 匹敌"
- 三层产品结构（Sol/Terra/Luna）标志着 OpenAI 从"一个旗舰模型"策略转向"按需分层"——与 Anthropic 的 Opus/Sonnet/Haiku 路线趋同

**相关**：[CNBC](https://www.cnbc.com/2026/06/26/openai-limits-new-ai-models-to-trusted-partners-request-us-government.html) | [Reuters](https://www.reuters.com/legal/litigation/openai-defers-public-rollout-gpt56-us-seeks-early-access-frontier-ai-models-2026-06-26/) | [Simon Willison](https://simonwillison.net/2026/Jun/26/openai/) | [Axios](https://www.axios.com/2026/06/26/openai-gpt-sol-terra-luna-trump)

---

### 📡 DeepSeek V4 Flash — API 定价调整

**时间**：2026年6月  
**核心变化**：DeepSeek V4 Flash 作为高性价比 backbone 的定位进一步巩固。  
**价格参考**：输入 ¥0.5/M tokens，输出 ¥2/M tokens，缓存命中 ¥0.1/M tokens  
**特征**：原生不支持视觉输入（纯文本模型），但推理速度快、中文能力强

---

### 🤖 MiniMax M3 多模态模型 + Token Plan 更新

**时间**：2026年6月  
**核心变化**：MiniMax Token Plan 用户可用的多模态模型更新。  
**注意**：MiniMax M2.5 Pro 无多模态能力；M2.5 有。M3 为独立新模型。

---

## 2026年5月

### 🌙 Meta 发布 Muse Spark — 终结开源 Llama 时代

**时间**：2026年4月8日（发布）/ 5月起逐步部署至 Meta 全线产品  
**发布方**：Meta Superintelligence Labs  
**官方公告**：[Introducing Muse Spark](https://about.fb.com/news/2026/04/introducing-muse-spark-meta-superintelligence-labs/)

**核心变化**：
- **首个闭源 Meta 模型** — 彻底背离 Meta 自 Llama 1（2023年）以来的开源路线
- 原生多模态推理模型，内置工具调用、视觉思维链、多智能体编排
- 驱动 Meta AI 助手，部署在 WhatsApp、Instagram、Facebook、Messenger 及 Ray-Ban Meta 智能眼镜
- 同时支持消费级应用和企业级部署

**意义**：Meta 的路线转换是 2026 年最重要的产业信号之一。Llama 4 Behemoth 长期处于"预览"状态（近一年未正式发布），Muse Spark 的闭源策略意味着开源社区失去了最大的推手。多家分析指出，"开源 AI 的黄金时代可能已经结束"。

**后续**：2026年6月4日，Reuters 报道 Meta 一再推迟向开发者开放 Muse Spark API。

**相关**：[Meta AI Blog](https://ai.meta.com/blog/introducing-muse-spark-msl/) | [CNBC](https://www.cnbc.com/2026/04/09/metas-long-awaited-ai-model-is-finally-here-but-can-it-make-money.html) | [The New Stack](https://thenewstack.io/meta-abandons-llama-spark/) | [Reuters (API delays)](https://www.reuters.com/technology/meta-repeatedly-pushes-back-new-ai-model-release-developers-wsj-says-2026-06-04/)

---

### 🔵 OpenAI 发布 GPT-5.5 系列 — 第二代旗舰

**时间**：2026年4月23日（GPT-5.5）/ 5月5日（GPT-5.5 Instant）/ 5月28日（GPT-5.5 Instant 更新）  
**发布方**：OpenAI  
**官方**：[Introducing GPT-5.5](https://openai.com/index/introducing-gpt-5-5/) | [GPT-5.5 Instant](https://openai.com/index/gpt-5-5-instant/)

**产品线**：
- **GPT-5.5** — 旗舰模型，$5/百万输入 tokens，$30/百万输出 tokens。深度推理、代码生成、研究能力突出
- **GPT-5.5 Instant** — ChatGPT 默认模型，$2.50/百万输入 tokens，$12/百万输出 tokens。2026年5月28日更新后响应更简洁、减少幻觉、个性化增强

**API 变革**：随 GPT-5.5 发布，OpenAI 推出全新的 Responses API，逐步替代 Chat Completions API。

**基准表现**：Intelligence Index 评分 59-60，在通用聊天和知识工作场景排名靠前但非最高（Claude Opus 4.8 在复杂推理上略胜）。

**相关**：[TechCrunch](https://techcrunch.com/2026/05/05/openai-releases-gpt-5-5-instant-a-new-default-model-for-chatgpt/) | [Release Notes](https://help.openai.com/en/articles/9624314-model-release-notes) | [VentureBeat (5.28更新)](https://venturebeat.com/technology/openais-updated-gpt-5-5-instant-is-better-at-shopping-complex-constraints-and-understanding-user-intent-and-its-already-in-the-api)

---

### ⚡ Google 发布 Gemini 3.5 Flash — 小型模型的前沿能力

**时间**：2026年5月19日（GA）  
**发布方**：Google DeepMind  
**官方**：[Gemini 3.5 Flash Blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-5/)

**核心指标**：
- 在 APEX-Agents-AA 基准上排名第 1，超越同尺寸以上模型
- 比同类前沿模型推理速度快 4 倍
- 1M token 上下文窗口
- 定价：$1.50/百万输入 tokens，$9/百万输出 tokens

**定位**：Flash 系列首次在多个维度达到与旗舰模型竞争的智能水平。在 Google I/O 2026 上作为重点发布，随后集成到 Google Search 的 AI 功能中。

**后续**：Gemini 3.5 Pro 原定 6 月发布，后推迟至 7 月。

**相关**：[Google Blog](https://blog.google/products-and-platforms/products/search/search-io-2026/) | [Mashable](https://mashable.com/article/google-io-2026-gemini-35-flash) | [WaveSpeed 分析](https://wavespeed.ai/blog/posts/gemini-3-5-pro-flash/)

---

### 🏛️ OpenAI 重组为营利性公益公司

**时间**：2026年5月  
**核心变化**：OpenAI 正式从非营利+ capped-profit 结构转为 Delaware 公共利益公司（PBC）。  
**影响**：对投资者更友好，加速 IPO 进程。原非营利董事会权力被显著削弱。

---

### 🔓 Anthropic 发布 Claude Opus 4

**时间**：2026年5月  
**核心变化**：在复杂推理、代码生成、长上下文理解上超越 GPT-5。  
**定价**：$15/M input tokens, $75/M output tokens。  
**定位**：最贵的商用模型，仅在需要最高质量的推理任务时使用。

---

## 2026年4月

### 📐 Google Gemini 2.5 Pro — 1M 上下文

**时间**：2026年4月  
**核心变化**：1M token 上下文窗口（可申请 2M），原生多模态输入（文本/图片/音频/视频）。  
**定价**：$1.25-2.50/M input tokens（视缓存命中率），$10/M output tokens。  
**特征**：思维链推理（"thinking" mode），在数学/科学/编程基准上拔尖。

---

## 格式说明

- **条目结构**：时间线 → 事件标题 → 核心变化/技术细节 → 定价（如有）→ 影响/评价
- **来源标注**：关键数据附来源链接
- **更新频率**：每周末 cron 自动扫描采集，重要事件即时手动补充
- **去重原则**：同一事件不重复录入，新增信息追加到已有条目
