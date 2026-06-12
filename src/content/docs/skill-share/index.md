---
title: Skill 分享
description: 可分享的 Hermes Agent 技能包
---

这里是整理好的可分享 Skill 包，可直接用于 Hermes Agent 或其他 LLM Agent 框架。

## 综述写作技能包

化学生物领域综述的完整写作规范，覆盖全流程。

仓库路径：[`static/skills/review-writing/`](https://github.com/HTZY08/wiki-for-Amaranth/tree/main/static/skills/review-writing)

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
- LaTeX 翻译需多阶段流水线，禁止单次 delegate_task
- 框架设计被拒时，连续 2 次"不够"就切换层级

## 使用方式

Fork 本仓库后，将 `static/skills/review-writing/` 下的内容解压到 Hermes Agent 的 skills 目录：

```bash
# 克隆仓库
git clone https://github.com/HTZY08/wiki-for-Amaranth.git

# 将 skill 复制到 Hermes 目录
cp -r wiki-for-Amaranth/static/skills/review-writing/* ~/.hermes/skills/

# 在对话中加载使用
# /skill review-chem-bio-writing
```

或者直接下载 tar.gz 包：[`review-writing-skill-pack.tar.gz`](https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/review-writing/review-writing-skill-pack.tar.gz)

---

*更多技能包陆续整理中...*
