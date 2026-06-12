---
title: Review Writing Skills
description: 化学生物综述写作 Hermes Agent 技能包
---

# Review Writing Skills

> 一套完整的化学生物领域综述写作 Hermes Agent 技能包。覆盖从定题搜索到英文 LaTeX 排版的全流程。

**GitHub 仓库：** [`HTZY08/wiki-for-Amaranth` → `static/skills/review-writing/`](https://github.com/HTZY08/wiki-for-Amaranth/tree/main/static/skills/review-writing)

**直接下载：** [`review-writing-skill-pack.tar.gz`](https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/review-writing/review-writing-skill-pack.tar.gz)（126KB，44 文件）

**License：** CC BY-NC-SA 4.0

---

## 背景

写化学生物综述时，最常见的问题不是"不知道怎么搜文献"，而是：

- 搜了 1000 篇但筛不出真正相关的
- 框架永远被导师说"眼界不够高"
- 数据密度不够，被批"信息密度低"
- 中文写完了转英文 LaTeX 排版又花一周

这套技能包就是针对这些问题积累的方法论，经过 3 篇中文综述 + 1 篇英文 LaTeX 综述（253KB 中文 → 365KB LaTeX，367 条引用完整保留）的实际验证。

---

## 包含的 Skill

### 1. review-chem-bio-pipeline

全流程管道，8 个 Phase：

```
Phase 1  ANALYZE   定角度、画学术谱系、写 Argument Map
Phase 2  SEARCH    多数据库搜索（PubMed / OpenAlex / CrossRef）
Phase 3  DEDUP     跨库去重
Phase 4  CLASSIFY  按主题分类
Phase 5  ORGANIZE  映射为章节
Phase 6  WRITE     C-E-L-T 或金风格写作
Phase 7  FIGURES   SciencePlots 统一风格出图
Phase 8  VERIFY    引用核验 + 数据一致性检查
```

### 2. review-chem-bio-writing

核心写作规范，含两种模式、三种架构类型：

**两种写作模式：**

| 模式 | 目标期刊 | 引用数 | 风格 |
|------|---------|--------|------|
| Critical Review | Biosens Bioelectron / TrAC | ~50 篇精引 | C-E-L-T 段落推进 |
| 金风格（大综述） | Chem Rev / Chem Soc Rev | ≥200 篇唯一 DOI | 流动学术散文，无框架标签 |

**三种架构类型：**

- **瓶颈驱动型** — 每章围绕一个瓶颈问题，多技术从多路线回应
- **系统架构型** — 按功能模块的因果链组织
- **技术百科型** — 按功能链路分卷 + 技术条目分节 + 三段式（科学史→近三年前沿→性能边界表）

**关键规范：**
- 数据密度规则：每个论断必须跟一个具体数字
- 密度标注：每个方向标注真实发文密度 + 真正有用的占比
- 引用格式：内联 `(Author, Year, *Journal Abbrev*, DOI:10.xxxx)`
- 去 AI 腔清洗流程
- 框架设计失败恢复机制（"前倨后恭"陷阱规避）

### 3. precision-review-search

当 PISMA 管道搜索不足时使用的替代方案。

- 将主题分解为 10-15 个精确子主题
- 直接搜索 OpenAlex + PubMed
- 两轮启发式筛选（硬排除 + 复合评分）
- 手动补充经典奠基论文
- 已验证：单次运行产出 1,479 篇原始论文 → 855 篇最终语料库

### 4. paper-figure-mapper

配图工作流，不生成图片，产出与 meiGen / Codex CLI / ComfyUI 兼容的 prompt。

- 扫读章节 → 识别 8 类配图信号
- 排序优先级（P0/P1/P2）
- 先产 1 张测试图 → 用户审核 → 确认风格 → 批量产出
- 5 种 Prompt 模板（时间线 / 对比 / 信息图 / 流程图 / 框架图）

---

## 快速开始

```bash
# 方式一：下载压缩包
wget https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/review-writing/review-writing-skill-pack.tar.gz
tar xzf review-writing-skill-pack.tar.gz -C ~/.hermes/skills/

# 方式二：Fork 整个仓库
# https://github.com/HTZY08/wiki-for-Amaranth/fork

# 在 Hermes 中加载
# /skill review-chem-bio-writing
```

## 场景路线

| 场景 | 用到哪些 Skill | 预估工作量 |
|------|---------------|-----------|
| 写 1 篇 Critical Review（~50 篇引用） | pipeline Phase 1 → precision-search → pipeline Phase 5-6 → writing 清洗 | 1-2 天 |
| 写 1 篇大综述（≥200 篇引用） | pipeline Phase 1 → precision-search → pipeline Phase 5-6 → 金风格写作 → figure-mapper | 3-5 天 |
| 中文综述转英文 LaTeX/Word | writing 翻译参考文件（多阶段流水线） | 1 天（~250KB 中文） |

## 依赖

- Hermes Agent 或其他 LLM Agent 框架
- Python 3.10+
- 可选：OpenAlex API Key、NCBI API Key（免费）
- LaTeX → Word 转换需 pandoc

## 链接

| 资源 | 链接 |
|------|------|
| GitHub 仓库 | [github.com/HTZY08/wiki-for-Amaranth](https://github.com/HTZY08/wiki-for-Amaranth) |
| Skill 文件目录 | [static/skills/review-writing/](https://github.com/HTZY08/wiki-for-Amaranth/tree/main/static/skills/review-writing) |
| 直接下载 tar.gz | [review-writing-skill-pack.tar.gz](https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/review-writing/review-writing-skill-pack.tar.gz) |
| License | CC BY-NC-SA 4.0 |
