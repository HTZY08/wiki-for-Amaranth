---
title: AI 信息前沿
description: 重大 AI 事件、新模型发布、关键架构突破的持续记录与合并
---

本页持续记录 AI 领域的重要事件，按时间线排列。不是日报，是**里程碑索引**——值得长期记住的模型发布、架构突破、定价变化、产业拐点。

---

## 2026年6月

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
