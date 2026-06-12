---
title: Review Writing Skills
description: 化学生物综述写作 Hermes Agent 技能包 — 开源可 Fork
---

# Review Writing Skills

> 一套完整的化学生物领域综述写作 Hermes Agent 技能包。覆盖从定题搜索到英文 LaTeX 排版的全流程。

**GitHub 仓库：** [`HTZY08/wiki-for-Amaranth` → `static/skills/review-writing/`](https://github.com/HTZY08/wiki-for-Amaranth/tree/main/static/skills/review-writing)

**直接下载：** [`review-writing-skill-pack.tar.gz`](https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/review-writing/review-writing-skill-pack.tar.gz)（126KB，44 文件）

**License：** MIT — 可自由 Fork、修改、商用

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

---

## 依赖

- Hermes Agent 或其他 LLM Agent 框架
- Python 3.10+
- 可选：OpenAlex API Key、NCBI API Key（免费）
- LaTeX → Word 转换需 pandoc

---

## 链接

| 资源 | 链接 |
|------|------|
| GitHub 仓库（Fork 入口） | [github.com/HTZY08/wiki-for-Amaranth](https://github.com/HTZY08/wiki-for-Amaranth) |
| Skill 文件目录 | [static/skills/review-writing/](https://github.com/HTZY08/wiki-for-Amaranth/tree/main/static/skills/review-writing) |
| 直接下载 tar.gz | [review-writing-skill-pack.tar.gz](https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/review-writing/review-writing-skill-pack.tar.gz) |
| Wiki 首页 | [wiki-for-amaranth.pages.dev](https://wiki-for-amaranth.pages.dev) |
| License | MIT |

---

## 异步任务委派系统（Async Delegate）

> 基于 Hermes Kanban 的多 Profile 异步任务处理架构。大任务拆解后交给后台 Worker 执行，前台保持响应。解决 `delegate_task()` 同步阻塞的问题。

**GitHub 仓库：** [`HTZY08/wiki-for-Amaranth` → `static/skills/async-delegate/`](https://github.com/HTZY08/wiki-for-Amaranth/tree/main/static/skills/async-delegate)

**直接下载：** [`hermes-async-delegate.tar.gz`](https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/async-delegate/hermes-async-delegate.tar.gz)（3.4KB）

**License：** MIT — 可自由 Fork、修改、商用

---

### 背景

Hermes Agent 内置的 `delegate_task()` 提供子 agent 能力，但问题是同步阻塞的——主 agent 派发子任务后必须等待所有子任务完成才能继续响应。社区对此的诉求体现在 GitHub issues 中，但尚未进入主分支。

Kanban 是 Hermes 内建的异步任务队列，支持多 profile 协作、依赖链、自动派发。这套 skill 封装了"前后台分离"的最佳实践。

### 包含的文件

| 文件 | 功能 |
|------|------|
| **delegate/SKILL.md** | 核心 Skill：架构说明、配置参数、行为规则、Profile 模板 |
| **delegate/references/worker-SOUL.md** | Worker Profile 的 SOUL.md 模板，含失败处理、路径限制、完成验证 |

### 快速开始

```bash
# 下载并解压
wget https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/async-delegate/hermes-async-delegate.tar.gz
tar xzf hermes-async-delegate.tar.gz -C ~/.hermes/skills/

# 初始化 Kanban
hermes kanban init

# 创建 Worker Profile
hermes profile create worker --clone

# 使用参考 worker-SOUL.md 更新 worker 的行为定义
```

### 核心参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| dispatch_interval | 5s | Dispatcher 轮询间隔 |
| stale_timeout | 600s（10min） | Worker 崩溃后自动回收 |
| failure_limit | 3 | 失败重试次数 |
| max_concurrent | 3 | 每 Profile 并发任务数 |

### Profile 模板

| Profile | 主模型 | 副模型 | 专精 |
|---------|-------|-------|------|
| worker | 通用 | — | 不明确分类的任务 |
| compute | 执行模型 | 分析模型 | 计算化学 |
| code | 执行模型 | 架构模型 | 编码/Debug |
| writer | 写作模型 | 执行模型 | 文档/翻译 |
| researcher | 分析模型 | 执行模型 | 文献/深度研究 |

### 关键经验

- **前后台分离铁律**：先创建卡片再回复用户，禁止在回复前做调研
- **最小权限**：Worker .env 只保留必要的 API Key，移除所有第三方服务 Key
- **路径白名单**：限制 Worker 只能写入指定输出目录，防止覆盖系统配置
- **Stale Timeout**：Worker 崩溃后 10 分钟自动回收，避免任务永久卡死
- **分层模型**：执行用快速模型，复杂分析调高端模型（Gemini Pro / Claude）

### 链接

| 资源 | 链接 |
|------|------|
| GitHub 仓库 | [github.com/HTZY08/wiki-for-Amaranth](https://github.com/HTZY08/wiki-for-Amaranth) |
| Skill 文件目录 | [static/skills/async-delegate/](https://github.com/HTZY08/wiki-for-Amaranth/tree/main/static/skills/async-delegate) |
| 直接下载 tar.gz | [hermes-async-delegate.tar.gz](https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/async-delegate/hermes-async-delegate.tar.gz) |
| Wiki 说明页 | [notes/async-delegate/](https://wiki-for-amaranth.pages.dev/notes/async-delegate/) |
| License | MIT |
