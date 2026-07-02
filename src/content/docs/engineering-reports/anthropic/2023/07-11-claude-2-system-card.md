---
title: Claude 2 System Card — RLHF + Constitutional AI 的开端
date: 2026-07-03
source: anthropic.com/system-cards
---

# Claude 2 System Card

**发布日期：** 2023-07-11  
**来源：** Model Card and Evaluations for Claude Models, Anthropic  
**工程范式：** RLHF → Constitutional AI 过渡期

## 设计哲学

Claude 2 是 Anthropic 从 RLHF 基础模型向 Constitutional AI（CAI）体系过渡的关键里程碑。其设计哲学可以概括为"连续演化而非革命"——Anthropic 明确表示 Claude 2 并非 transformative change，而是两年多来在 RLHF、偏好建模、红队测试、诚实性、道德自我修正和 Constitutional AI 等方向研究成果的集成。

**核心矛盾**：Anthropic 同时追求三个目标——helpfulness（有用）、honesty（诚实）、harmlessness（无害），三者之间存在根本张力。Claude 2 的设计哲学是对这个三角约束的工程化妥协。

关键放弃：Claude 2 明确不适用于高 stakes 场景。"They should not be used on their own in high stakes situations where an incorrect answer would cause harm." 这一放弃声明成为后续所有 System Card 的标准模板。

## 关键架构决策

- **训练管线**：无监督预训练 → RLHF → Constitutional AI（监督阶段 + RL 阶段）。CAI 的引入使模型能够根据一套书面的"Constitution"（伦理和行为原则）自我修正。
- **训练数据**：专有混合数据（公开互联网、授权第三方数据、用户共享数据、众包工人数据）。约 10% 非英语数据。截止日期 2023 年初。
- **架构**：标准 Transformer，无特殊架构创新公开。
- **评估方法论**：Elo 评分系统（人类比较两个 Claude 输出的偏好）、BBQ 偏差基准、外部红队测试。
- **不允许默认联网搜索**（可通过工具接入）。
- **宪法设计**：基于联合国《世界人权宣言》的一套书面伦理原则。

## 关键结果

### 对齐评估

| 维度 | Claude 2 vs Claude 1.3 | 备注 |
|------|----------------------|------|
| Helpfulness | 显著提升 | 更详细的指令遵循 |
| Honesty | 显著提升 | 更准确/事实性 |
| Harmlessness | 与 1.3 相当 | Helpful-Only 模型对比凸显对齐效果 |

### BBQ 偏差基准
- Claude 模型相比 Helpful-Only 模型**显著减少刻板印象偏差**。
- Claude 2 和 Claude Instant 1.1 比 1.3 偏差略低。
- 改进来自 debiasing algorithm：生成无偏差样本 → CAI 的 RL 阶段前微调。

### 红队测试结果
- 外部红队测试覆盖：虚假信息、仇恨/歧视、儿童安全。
- 与 ARC（Alignment Research Center）合作验证：Claude 2 不具备危险的自主复制能力。
- 与国家政策制定者合作评估国家安全风险结论：**没有部署的 Claude 模型构成显著的国安风险**。

## 范式对比

| 对比维度 | Claude 2 | GPT-4（同期） |
|---------|----------|-------------|
| 对齐方法 | RLHF + Constitutional AI | RLHF + 规则-based 安全 |
| Constitution | 公开的书面伦理原则 | 不公开的 moderation 系统 |
| 安全评估 | 相对透明（System Card） | 较少公开细节 |
| 架构细节 | 不公开 | 不公开 |

与未来 Claude 模型相比，Claude 2 缺乏系统化的安全分级框架（RSP 尚未建立），评估范围也较窄——没有专门的 agentic safety、reward hacking、model welfare 评估。这是 RSP 1.0 时代之前的产物。

## 可复用工程经验

1. **Constitutional AI 作为 RLHF 的补充**：CAI 在减少偏见的同时保持了帮助性，说明基于原则的自我修正可以作为人类反馈的高效扩展。
2. **Elo 评分 + 多维评估**：同时在 helpfulness/honesty/harmlessness 三个维度做对比评估，而非单一指标——防止 Goodhart 效应。
3. **外部红队独立验证**：ARC 和外部众包平台的双重验证机制，是早期"红队文化"的工程化落地。
4. **明确放弃声明**：在 System Card 中明确模型不应使用的场景，是负责任的发布 engineering practice。
5. **宪法中的人权框架**：以联合国《世界人权宣言》作为对齐目标，提供了跨文化可解释的伦理基础。

## 局限性

Claude 2 的 System Card 本身明确承认"这不是一篇科学论文"——不具备可复现性。评估方法（众包工人对话、主观判断）的统计严谨性有限。对非英语能力的覆盖不足（仅 10% 训练数据为非英语）。缺乏对 agentic 能力的系统评估——在当时 agent 还不是主流关注点。
