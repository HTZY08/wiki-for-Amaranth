---
title: Skill 分享
description: 可分享的 Hermes Agent 技能包
---

这里是整理好的可分享 Skill 包，打包了从综述写作到日常工具链的完整方法论。

## 综述写作技能包

化学生物领域综述的完整写作规范，覆盖全流程。

📦 `D:\传递文件\review-writing-skill-pack.tar.gz`（126KB）

包含 4 个 Hermes Agent Skill：

| Skill | 功能 |
|-------|------|
| **review-chem-bio-pipeline** | 全流程管道：定范围 → 搜索 → 去重 → 分类 → 写作 → 配图 → 核验 |
| **review-chem-bio-writing** | 核心写作规范：两种模式（Critical Review / 金风格），三种架构（瓶颈驱动/系统架构/技术百科），数据密度规则，去 AI 腔清洗 |
| **precision-review-search** | 精搜索管线：当数据库搜索噪声过大时，分解 10-15 子主题直搜 OpenAlex+PubMed |
| **paper-figure-mapper** | 配图工作流：扫读章节 → 识别图位 → 产出 prompt → 批量出图 |

**适用场景：**
- 写 Critical Review（~50 篇引用，5-7 节）→ 管道 Phase 1 → 精搜索 → Phase 5-6
- 写大综述（≥200 篇引用）→ 金风格写作 + 技术百科型框架
- 中文综述 → 英文 LaTeX → Word 翻译

**关键经验：**
- 每个论断必须跟一个具体数字，不用定性标签
- 每节标注真实发文密度，禁止"装繁荣"
- LaTeX 翻译需多阶段流水线，禁止单次 delegate_task — 已验证 253KB 中文完整翻为 365KB LaTeX/367 条引用/727 处上标标注
- 框架设计被拒时，连续 2 次"不够"就切换层级，不要在同类型框架迭代

## 使用方式

将 tar.gz 解压到 Hermes Agent 的 skills 目录：
```bash
tar xzf review-writing-skill-pack.tar.gz -C ~/.hermes/skills/
```

然后在对话中加载对应 skill 即可使用：
```
/skill review-chem-bio-writing
```

---

*更多技能包陆续整理中...*
