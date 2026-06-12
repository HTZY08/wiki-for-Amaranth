---
name: review-chem-bio-pipeline
description: >-
  End-to-end pipeline for producing critical reviews in chemistry and biology
  (Chinese or English). Covers BOTH fundamental physical/inorganic chemistry
  (nanomaterial synthesis, growth mechanisms, optical/thermal/
  electrical/magnetic properties) AND applied bioanalytical chemistry
  (biosensing, POCT, DNA nanotechnology, biomaterials).
  NOT a general-purpose review writer — this is a structured workflow that:
  (1) queries real academic databases directly (PubMed, Semantic Scholar,
  OpenAlex, CrossRef, bioRxiv, PubChem),
  (2) deduplicates and classifies results by theme,
  (3) builds an intellectual genealogy tracing the field's growth,
  (4) writes with Claim-Evidence-Limitation paragraph structure,
  (5) generates publication-quality figures with enforced style consistency
  via SciencePlots + matplotlib/seaborn templates.
  Reference user-writing-style for output conventions. Default output language
  is Chinese unless the user specifies English.
---

# Review Pipeline: Chemistry & Biology

## Phase 0 ─ Thesis Chapter 1 to Review Decomposition

### When to Use This Phase

Trigger: The user says "把我论文第一章拆成几篇综述" or equivalent. Their thesis Chapter 1 is a comprehensive literature review spanning multiple sub-topics, and they want to extract 2-3 independent review papers from it.

### Decomposition Workflow

```
Step 1 ─ Map thesis sections to separable review topics
  Scan the Chapter 1 table of contents and paragraph-level coverage.
  Identify natural thematic clusters that could stand alone as reviews.
  Each cluster must have:
    - A distinct core question (not just "review of X")
    - A non-overlapping reference set (or minimal overlap)
    - A different target journal / reader community

Step 2 ─ Define each review's core angle
  For each candidate review, answer:
    - What unsolved problem does this review address?
    - What is the argument/thesis (not just a summary)?
    - What is NOT covered (exclusion boundary)?
  Ensure the three reviews do not compete on angle —
    each should serve a different reader and a different journal.

Step 3 ─ Allocate references
  Split the thesis Chapter 1's reference list among the reviews.
  References that span multiple themes become supplementary citations
  in the review where they're most relevant; cross-link titles suffice
  in the other reviews.

Step 4 ─ Map to target journals
  For each review, determine:
    - Primary journal (ideal fit, high impact)
    - Secondary journal (good fit, more accessible)
    - Backup journal (broader scope, lower barrier)
  Use references/journal-targeting-guide.md for domain-specific mappings.
  See Phase 0 Pitfalls below for critical constraints.

Step 5 ─ Assess existing work
  Check if any candidate review already has a draft or outline
  (e.g., an earlier session produced a partial draft).
  If so, incorporate that work rather than restarting from scratch.
```

### Typical Decomposition Patterns for Thesis Chapter 1

| Thesis Chapter Themes | Possible Reviews | Separation Logic |
|-----------------------|------------------|------------------|
| POCT + nucleic acid amplification + LFIA + AuNP + microfluidics | (1) POCT核酸检测, (2) 微流控POCT, (3) AuNP材料 | Different readership (biosensor vs. device engineering vs. materials chemistry), different journals, non-overlapping reference sets |
| Synthesis + characterization + application | (1) synthesis/mechanism, (2) biosensing application | Fundamental vs. applied framing — same papers can be cited from different angles |
| Multiple detection targets (nucleic acid + protein + small molecule) | One review per target class | Different molecular recognition mechanisms, different assay design constraints |

### Phase 0 Pitfalls

1. **Don't propose your own split first.** The user has their own mental model of how the chapter divides. Propose your split only AFTER the user states theirs — otherwise you waste rounds on correction (as happened here: first split rejected, second split accepted).
2. **Each review needs its own argument thesis.** A review that just "summarizes the literature" will be desk-rejected. Every extracted review must have a critical claim (e.g., "the bottleneck has shifted from X to Y").
3. **Journal constraints affect the split.** If two candidate reviews would both target Biosensors and Bioelectronics, they compete with each other. The split should aim for different journal communities.
4. **Goldilocks scope.** A review too broad (everything about POCT) has no focused argument. A review too narrow (one specific enzyme in one specific assay) has no readership. Each extracted review should cover a 3-5 year window with ~80-200 core references.
5. **Check for existing drafts.** The user may have started one review in a previous session. Check `/opt/data/reviews/` or vault for existing outlines/sections before proposing the full pipeline run.

## Phase 0 ─ Thesis Chapter 1 to Review Decomposition

### When to Use This Phase

Trigger: The user says "把我论文第一章拆成几篇综述" or equivalent. Their thesis Chapter 1 is a comprehensive literature review spanning multiple sub-topics, and they want to extract 2-3 independent review papers from it.

### Critical Rule: Propose Your Split Only After the User States Theirs

**Do NOT propose a split first.** The user has their own mental model of how their chapter divides. If you propose your split before they state theirs, you waste rounds on correction. Wait for the user to describe their desired split, then validate and refine.

Signal: if the user says "不不不，这么来分", your proposed split was wrong. Scrap it and adopt theirs.

### Decomposition Workflow

```
Step 1 ─ Map thesis sections to separable review topics
  Scan the Chapter 1 table of contents.
  Identify natural thematic clusters that could stand alone as reviews.
  Each cluster must have:
    - A distinct core question
    - A non-overlapping reference set
    - A different target journal / reader community

Step 2 ─ Wait for user's split preference
  Propose candidate splits tentatively. Let the user correct.
  Once the user says "这个是对的" for the split, proceed.

Step 3 ─ Define each review's core angle
  For each candidate review, YOUR angle must be DIFFERENT from the user's thesis angle.
  - Their thesis organizes by technology type → you organize by simplification cost
  - Their thesis argues for a specific technical solution → you ask a meta-level question
  - The user will reject any review that reads like a repackaged version of their chapter

Step 4 ─ Map to target journals
  Each review should target a DIFFERENT journal community.
  If two reviews would land in the same journal, the split is wrong — revise.

Step 5 ─ Check for existing drafts
  Look for existing outlines/sections in /opt/data/reviews/ before starting fresh.
```

### Typical Decomposition Patterns

| Thesis Chapter Themes | Possible Reviews | Target Journals |
|-----------------------|------------------|-----------------|
| POCT + nucleic acid amplification + LFIA + AuNP + microfluidics | (1) Nucleic acid detection for POCT, (2) Microfluidic POCT platforms, (3) Gold nanomaterials | Biosensors/Bioelectron vs Lab on a Chip vs Nanoscale/Chem Mater |
| Synthesis + characterization + application of one material | (1) Synthesis/mechanism, (2) Application in biosensing | Chem Mater / Nanoscale vs ACS Sensors / Anal Chem |

### Reference for Data Anchors

This skill ships with `references/poct-nucleic-acid-data-anchors.md` which contains verified quantitative benchmarks for POCT reviews: PCR inhibitor thresholds, amplification method performance ranges, commercial product LOD comparisons, and correction factors. Load it when starting Phase 1 on a POCT-adjacent topic.

### Phase 0 Pitfalls

1. **Don't propose your own split first.** Let the user state theirs. Correcting a wrong split takes multiple turns.
2. **Each review needs its own argument thesis that is NOT the user's thesis argument.** If your review says "layered gating solves false positives" and their thesis says the same thing, you haven't added value.
3. **Journal constraints affect the split.** If two reviews would target the same journal, revise the split.
4. **Check for existing drafts.** The user may have started one review in a previous session. Search `/opt/data/reviews/` before proposing the pipeline.
5. **Goldilocks scope.** Each extracted review should cover ~80-250 references. Anything under 40 is a short communication; anything over 400 is a book.

## Domain Scope Warning (READ FIRST)
> This skill covers BOTH fundamental physical/inorganic chemistry (synthesis, growth mechanisms, optical/thermal/electrical/magnetic properties of nanomaterials) AND applied bioanalytical chemistry (biosensing, POCT, DNA nanotechnology, drug delivery).
> 
> **Critical pitfall:** Never assume the user's sub-domain based on their academic background. The same person may work on fundamental AuNP synthesis one month and DNAzyme biosensors the next. Always confirm scope during Phase 1 before proceeding.
> 
> The skill defaults to NO applied/application framing unless the user explicitly confirms it. When in doubt, choose the fundamental track.

## Pipeline Overview

```
Phase 1 ─ ANALYZE         Analyze the topic, define scope, formulate argument thesis
Phase 2 ─ SEARCH          Query databases directly, collect raw records
Phase 3 ─ DEDUP           Cross-database deduplication + PRISMA tracking
Phase 4 ─ CLASSIFY        Categorize records into thematic buckets
Phase 5 ─ ORGANIZE        Build section outline from classified papers
Phase 6 ─ WRITE           Draft sections with C-E-L-T paragraph structure
Phase 7 ─ FIGURES         Generate consistent figures via SciencePlots
Phase 8 ─ VERIFY          Check citations, data consistency, language
```

Each phase produces a concrete deliverable that feeds the next. The pipeline is iterative — gaps found in Phase 6 may trigger a return to Phase 2.

---

## Phase 1 ─ ANALYZE (Overall Analysis)

### ⚠️ Critical Rule: Don't Assume the User's Angle — And Don't Rewrite Their Work

This skill was designed for chemistry/biology interface research. But within that, the user may be asking about ANY sub-direction — synthesis, mechanism, properties, applications, or theory.

When the user gives a topic (e.g., "金纳米材料"), do NOT default to their known research background (e.g., biosensing/POCT). Their stated topic is the authoritative scope — not what you infer from their past work.

**Rule: If the topic is ambiguous, ask before proceeding with academic genealogy.**

例外：如果用户明确说了方向或上下文明确指向某个子领域，则直接推进。

**Critical pitfall: Don't just reorganize the user's existing work.** If the user has a thesis chapter (or prior publication) on the same broad topic, the first instinct is to rearrange their material into a new outline. The user will recognize this and reject it (signal: "不要和我的研究内容一样", "如果你来写，你会怎么写").

How to detect and avoid:
- If the user says "如果你来写"/"你会这么写"/"重新写", they want YOUR analytical framework, not a paraphrased version of their chapter
- Distill your own organizing principle before looking at their material — write §2 (the framework) first
- Test: if you can imagine the user saying "this is my literature review with different words", you haven't gone far enough
- Change the organizing principle, the core question, or the through-line. If their chapter is organized by "technology type" (PCR→LAMP→RPA), organize yours by "what was given up" (simplification cost framework)

**Critical pitfall: Don't just reorganize the user's existing work.** If the user has a thesis chapter (or prior publication) on the same broad topic, the first instinct is to rearrange their material into a new outline. The user will recognize this and reject it (signal: "不要和我的研究内容一样", "如果你来写，你会怎么写"). 

How to detect and avoid:
- If the user says "如果你来写"/"你会这么写"/"重新写", they want YOUR analytical framework, not a paraphrased version of their chapter
- Distill your own organizing principle before looking at their material — write §2 (the framework) first
- Test: if you can imagine the user saying "this is my literature review with different words", you haven't gone far enough
- Change the organizing principle, the core question, or the through-line. If their chapter is organized by "technology type" (PCR→LAMP→RPA), organize yours by "what was given up" (simplification cost framework)

### 0.1 Review Type: Critical Review vs 大综述 (Comprehensive Review)

Before starting Phase 1, determine which review type the user wants. This decision shapes the entire pipeline.

| Dimension | Critical Review | 大综述 (Comprehensive Review) |
|-----------|----------------|-------------------------------|
| **Core structure** | Argument-driven: one thesis, every section serves it | Framework-driven: an analytical lens, sections explore different facets |
| **Typical target** | Biosensors Bioelectron, TrAC, Anal Chem | Chemical Reviews, Chem Soc Rev, Advanced Materials |
| **Reference count** | ~50-100 | ~150-250+ |
| **Section count** | 5-7 | 10-12 |
| **Organizing principle** | "I argue that X" | "Here is a framework for understanding the field" |
| **Outcome** | A provable claim | A map with decision rules |
| **Phase 6 writing** | C-E-L-T paragraphs throughout | C-E-L-T for sub-sections, but sections may use different structures (comparison tables, decision trees, commercialization gap analysis) |

**Critical pitfall for the agent: When the user already has deep domain knowledge (e.g., their thesis covers the topic), do NOT simply reorganize their existing material into a review. The user wants YOUR analytical framework — a genuinely new perspective, not a paraphrase. If you produce text that reads like a rephrased version of their thesis chapter, they will reject it. The signal is "不要和我的研究内容一样" or "你会这么写". When this lands, scrap the outline and rebuild from a different analytical angle.**

**How to detect and avoid this pitfall:**
- If the user asks "如果你来写，你会怎么写" or equivalent, they want your framework, not theirs
- Ask yourself: "If this user had never written a thesis on this topic, would this outline still make sense?" If the answer is no, you're too close to their material
- The opening hook, the organizing principle, and the conclusion must all be yours, not a summary of their chapter
- "Framework-first" — establish the analytical lens (e.g., "simplify-and-pay trade-off", "the cost of each simplification") in §2 before diving into any technology categories

### 1.1 Deliverable
A structured scope document answering five questions, PLUS a genealogy tracing the field's intellectual lineage.

### 1.2 Intellectual Genealogy — "顺藤摸瓜"

**核心原则：综述的第一个大段不做分类罗列，要做学术谱系。**

这不是"把最早几篇论文列出来"，而是画出这个领域的**发生学结构**——谁种下了第一颗种子，在什么土壤里，哪几个节点让这个领域分了叉，哪几篇论文建立了范式、让后来者只能在其框架内工作。

#### 1.2.1 五根藤

溯源时沿五条线摸：

| 线 | 问什么 |
|----|--------|
| **概念源头** | 这个概念/现象最早是谁在什么语境下提出的？当时的名字和现在一样吗？（例如：DNAzyme 最早不叫 DNAzyme，叫 "catalytic DNA" / "deoxyribozyme"，命名变化本身就是信息） |
| **方法突破** | 哪篇论文让这个领域"突然能做之前不能做的事"？（例如：SELEX 技术让核酸适配体筛选成为可能；Santoro & Joyce 1997 的 10-23 DNAzyme 让催化活性达到实用阈值） |
| **跨界嫁接** | 哪篇论文把 A 领域的概念接到了 B 领域，产生了新方向？（例如：Willner 组把 DNAzyme 接到金纳米颗粒上，催生了"DNAzyme-AuNP 比色传感"这个子领域） |
| **范式定型** | 哪篇论文确立了该领域"默认怎么做实验/怎么报数据/怎么评价性能"的标准？（例如：Lu 组建立的水凝胶-比色法 DNAzyme 传感器范式） |
| **瓶颈显现** | 哪篇论文（或哪几年的集体沉默）标志着这个领域意识到原来的路走不通了？（例如：大量 DNAzyme 传感器止步于缓冲液测试，2018 年后开始系统性讨论"基质效应"问题） |

这五根藤的交织点就是你的**关键节点脉络**。

#### 1.2.2 关键节点类型

| 类型 | 特征 | 在综述中的功能 |
|------|------|---------------|
| **奠基之作**（Foundational） | 首次提出概念/现象 | 定义学科的起点，不可绕过 |
| **分水岭**（Watershed） | 让领域增速/转向的单一论文 | 划分"前X时代"和"后X时代" |
| **范式建立**（Paradigm-setting） | 确立了怎么做实验、报数据、评性能的默认标准 | 后人引用它不是在引用一个结果，是在引用一种方法 |
| **跨界融合**（Cross-pollination） | 把A领域工具用于B领域问题 | 产生了新子领域的节点 |
| **反思/瓶颈**（Bottleneck） | 明确指出了领域困境 | 论证"为什么我们需要这篇综述"的支点 |
| **综述综述**（Meta-review） | 该领域此前的重要综述 | 知道前人覆盖到哪里，你的增量在哪里 |

#### 1.2.3 执行流程

```
Step 1 ─ 初始种子
  从 Phase 2 搜索结果中，找到被引量最高、发表最早的 10-20 篇论文。
  用 Semantic Scholar 的 "highly influential" 标记过滤。

Step 2 ─ 反向追踪
  对每篇种子论文，查它的参考文献。
  找到这些参考文献中被引量最高的 3-5 篇。
  重复：查这些论文的参考文献。
  直到遇到"这篇论文的参考文献里已经没有什么论文被大量引用了"——你找到了概念源头。

Step 3 ─ 正向追踪
  对每篇奠基性论文，查 "citing papers"（谁引用了它）。
  按年份排序，标记出引用曲线突变点。
  突变点就是分水岭论文的候选。

Step 4 ─ 建立时间轴
  把所有关键节点按年份排列。
  标注每个节点连接了哪篇论文和哪篇论文。
  形成一张有向图（A → B 表示 B 引用了 A，即 A 影响了 B）。

Step 5 ─ 写成叙述
  把有向图翻译成"科学史叙事"。
  不是 "论文A发表于1994年，论文B发表于1997年"。
  而是 "1994年，Breaker和Joyce在筛了10^14个DNA序列后，找到了第一个催化DNA。
           这个发现来自一个基本问题：既然RNA能做酶，DNA为什么不行？
           但当时没有人能回答这有什么用——
           直到1997年，同一个Joyce组筛出了10-23和8-17，活性到了实用阈值。
           技术扩散开始了。"
```

#### 1.2.4 时间轴图生成

在 Phase 7 中，这个时间轴应该可视化为一张 **科学史发展脉络图**：

```
1994 ── Breaker & Joyce ── 首次发现 ──────┐
         │                                  │
         │                                  │
1997 ── Santoro & Joyce ── 10-23/8-17 ────┤ 活性达到实用阈值
         │                                  │
         │          ┌───────────────────────┤
         │          │                       │
2000s ── Lu Group ── 特异性传感 ──┬─── AuNP比色法
         │                       │
         ├── Willner Group ──── DNAzyme-AuNP杂化 ── 信号放大
         │
2010s ── Fan Group ── DNA纳米结构 ── 信号放大
         │
         ├── CRISPR 阵营崛起 ── 竞争/交叉
         │
2020s ── 瓶颈期 ── 基质效应、监管、产业转化
```

这个图可以用 matplotlib 的 annotate + arrow 生成，保持与全文一致的 SciencePlots 风格（Phase 7 约束）。

#### 1.2.5 这个部分的写作位置

放在 Introduction 之后，作为 **第2节（或第1节的第二部分）**：

```
§1 Introduction
  [Hook → Gap → What this review does differently]

§2 学术谱系：从发现到分流（2,000-4,000字）
  §2.1 概念源头与奠基
  §2.2 技术扩散与范式建立
  §2.3 分水岭与瓶颈
  §2.4 当前格局：未完成的闭环

§3 主题正文章节...
```

**与传统综述的区别：**

| 传统综述 | 本 skill 的做法 |
|---------|---------------|
| "DNAzyme 由 Breaker 和 Joyce 于 1994 年发现，随后 Santoro 和 Joyce 于 1997 年报道了 10-23 DNAzyme…" — 线性罗列，谁也没得罪 | "1994 年的发现回答了一个基本问题（DNA 能否做酶），但留下了一个工程问题（活性太低）。1997 年的论文不是简单的'改进'——它把 DNAzyme 从 curiosum 变成了 tool。这两个节点之间隔了三年，而这三年里该领域发表的论文不到 10 篇——这才是关键信息。" |
| 按技术分类逐个综述 | 按"这棵知识树是怎么长出来的"来组织 |
| 每个子领域独立介绍 | 展示子领域之间的分叉点和融合点 |
| 结尾总结"未来方向" | 揭示当前格局中的结构性问题——哪些分支长成了、哪些分叉被废弃了、哪些交叉口还没修通 |

| Question | Field | Example (DNAzyme biosensors) |
|----------|-------|-----------------------------|
| **Macro domain** | The broad field | Nucleic acid nanotechnology / bioanalytical chemistry |
| **Specific problem** | What unsolved question? | Why no DNAzyme sensor has achieved FDA clearance despite 30 years of research |
| **Review type** | Comprehensive / Critical / Mini | Critical Review (argue that bottleneck shifted from activity to matrix tolerance & regulation) |
| **Time window** | Foundational: no limit. Recent developments: last 5 years. |
| **Exclusion boundary** | What is NOT covered | RNA-based systems, in vivo imaging, purely therapeutic DNAzymes |

### 1.2 Argument Map (Mandatory, Human-Written)
Write **one paragraph** that the entire review will argue. Example:

> "DNAzyme-based biosensors have been studied for 30 years... This review argues that the bottleneck has shifted from catalytic activity to three interdependent constraints:..."

This is the **thesis** of the review. Every section serves it. The AI can help refine, but the core insight must come from the human author.

### 1.3 Pre-Search Concept Table

| Concept | Synonyms | MeSH Terms | Database-specific Keywords |
|---------|----------|-----------|---------------------------|
| DNAzyme | deoxyribozyme, catalytic DNA, DNA enzyme | "DNA, Catalytic"[Mesh] | DNAzyme OR deoxyribozyme |
| Signal amplification | signal enhancement, amplification strategy | "Nucleic Acid Amplification Techniques"[Mesh] | signal amplification OR signal enhancement |
| Point-of-care | POCT, bedside testing, decentralized | "Point-of-Care Systems"[Mesh] | point-of-care OR POCT OR POC |

Build this table before searching — it is the shared vocabulary across all databases.

---

## Phase 2 ─ SEARCH + Phase 3 ─ DEDUP + Phase 4 ─ CLASSIFY

**Decision: PISMA or Direct API Search?**

Before running any search, decide which approach fits the topic:

| Signal | Use PISMA | Use Direct API Sub-Topic Search |
|--------|-----------|----------------------------------|
| Topic width | Broad (>500 papers expected) | Narrow/niche sub-field |
| False-positive rate | Low — well-defined keywords | High — generic keywords drown in noise |
| Year range needed | Configurable, default ~5yr | Full 1850-2026 (foundational papers) |
| Foundational classics | Missed (year range too narrow) | Added manually |
| Search query style | Single flat query per source | 10-15 decomposed sub-topic queries |
| Typical yield | 50-200 papers | 600-1500 papers |
| Citation expansion | Built-in snowballing | Manual from top ~20 papers |
| ML deps available? | Needed for topic prefilter | Not needed (heuristic-only) |

**Verified benchmark (gold nanomaterials, 2026-06-03):**

| Metric | PISMA (3 sources) | Direct API sub-topic search |
|--------|-------------------|-----------------------------|
| Raw papers | 106 | 1,479 |
| True relevant after screening | ~5 | ~500+ |
| Foundational classics (Faraday, Turkevich, Brust) | 0 | 9 manually added |
| Run time | ~3 min (S2 disabled) | ~3 min (11 queries) |

**Rule of thumb:** If your first PISMA run returns top-cited papers that are mostly off-topic (drug delivery, biosensors, catalysis, etc.), switch to the direct API approach immediately — PISMA's single-flat-query strategy cannot filter out the application noise, and lowering the `relevance_threshold` lets in as much noise as signal.

The standard path uses PISMA (detailed below). When the signals above trigger, use the **Alternative Phase 2-4: Direct API Sub-Topic Search** section instead of this one. The scripts and workflow are documented there.

### Standard Path: PISMA

**PISMA** is an open-source systematic review pipeline that handles multi-source search, dedup, and screening.

### Why PISMA

| Our need | PISMA provides |
|----------|---------------|
| Multi-source search | PubMed, S2, OpenAlex, CrossRef, arXiv, CORE, Europe PMC, Springer — more than our original list |
| Deduplication | fuzzywuzzy cross-source |
| Citation expansion | Forward + backward snowballing |
| AI screening | Local sentence-transformers, or LLM (OpenAI/Gemini/Ollama/HuggingFace) |
| Rate limiting | Adaptive backoff, Retry-After parsing, S2-specific params |
| HTTP caching | Persistent on-disk cache with TTL |
| Partial rerun | Resume from screening/reporting without re-searching |
| Desktop GUI | Tkinter UI for manual inspection |
| CLI mode | Headless for automation |
| PRISMA reporting | Structured output with screening audit trail |

### Installation

```bash
git clone https://github.com/CarinaSchoppe/PISMA-Literature-Review-Pipeline-Automation-Tool.git
cd PISMA-Literature-Review-Pipeline-Automation-Tool
pip install -r requirements.txt
```

### Integration Flow

```
Phase 1 ─ ANALYZE  (our skill)
  → 五问定范围 + 五根藤溯源 + Argument Map
  → 输出：scope.json, concept_table.csv, anchor_papers.txt

PISMA (run from config)
  → discovery:   search all databases, collect records
  → dedup:       remove cross-database duplicates
  → screening:   AI relevance filter (topic prefilter + heuristic scoring)
  → citation:    expand from anchor papers
  → reporting:   structured results with PRISMA count

Phase 5 ─ ORGANIZE (our skill)
  → Import PISMA output → map buckets to sections
  → Build section outline

Phase 6-8 ─ WRITE / FIGURES / VERIFY (our skill)
```

### ⚠️ PISMA Critical Config Tips

These were learned through hard experience. Read `references/pisma-operational-notes.md` for full detail, but the essentials:

**1. uv --active flag required**
```bash
cd /opt/data/pisma
uv run --active python main.py --config gold_review_config.json
```
Without `--active`, uv creates a fresh venv and re-installs all deps. The Hermes venv already has `transformers`, `torch`, and all dependencies.

**2. relevance_threshold defaults to 70 (too high)**
Even papers with "gold nanoparticle" in the title score 50-60 on the composite heuristic. Set lower:
```json
{"relevance_threshold": 50}
```

**3. ai_evaluation_enabled must be true**
If false → `collect` mode, no screening runs. All papers pass through unclassified.

**4. S2 is disabled by default (2026)**
Without an API key, S2 returns 429 on every request. The registration process is broken. See `references/s2-operational-notes.md`.

### Configuration Template

Create a PISMA config file tailored to the review:

```yaml
# pisma_config.yaml — auto-generated from Phase 1 output
discovery:
  sources:
    - pubmed
    - semantic_scholar
    - openalex
    - crossref
    - arxiv
  queries:
    - "gold nanoparticle synthesis Turkevich citrate"
    - "anisotropic gold nanoparticle growth mechanism"
    - "gold nanorod seed-mediated El-Sayed"
  max_results_per_query: 500

dedup:
  method: fuzzy
  threshold: 85

screening:
  provider: local_heuristic
  topic_filter:
    keywords:
      - "gold nanoparticle|1.5|60"
      - "plasmon|1.2|50"
      - "anisotropic growth|1.8|70"

citation_expansion:
  enabled: true
  anchor_papers: /path/to/anchor_papers.txt  # From Phase 1
  depth: 2

output:
  format: json
  path: /opt/data/review-output/
```

### ⚠️ CRITICAL PITFALL — PISMA's Search Is Insufficient for Niche Topics

**Verified 2026-06-03 on gold nanomaterials review:**

| Metric | PISMA (3 sources) | Direct API sub-topic search |
|--------|-------------------|-----------------------------|
| Papers found | 106 | **1,479** |
| True relevant after screening | ~5 | **~500+** |
| Foundational classics included | 0 (year range too narrow) | **9 manually added** |

**Root cause:** PISMA concatenates `research_topic + search_keywords + boolean_operators` into a single flat query per source. This produces broad, unfocused queries that return papers which *mention* gold nanoparticles but are actually about drug delivery, SERS, biosensing, toxicity, etc. The topic prefilter then can't distinguish well because the underlying dataset is dominated by noise. The search keywords that should narrow the scope instead get combined into the query string reducing precision.

**Signals to use the alternative approach (below):**

- Your topic is a specific sub-field, not a broad domain
- PISMA returns <200 papers after dedup
- Top-cited papers are mostly irrelevant applications
- You need foundational papers from before PISMA's year range
- User explicitly validates that niche fields need precision search

**Verified benchmark (gold nanomaterials, 2026-06-03):**
PISMA returned 106 raw papers, of which only ~5 were truly relevant after screening (top papers were SERS, drug delivery, biosensing, catalysis — anything but synthesis). The same topic searched via Direct API sub-topic queries returned 1,479 papers, of which 731 passed a two-pass heuristic screen and 855 reached the final corpus after merging 9 manually added classic papers. The difference is not incremental — it is the difference between a review that cannot be written and one that can.

### Alternative Phase 2-4: Direct API Sub-Topic Search Pipeline

For niche or precision-focused reviews, bypass PISMA entirely and use targeted sub-topic queries directly against OpenAlex + PubMed APIs, then apply custom heuristic screening.

#### Workflow

```
Step 1 — Decompose topic into 8-12 sub-topic queries
  Each targets a specific sub-topic, not the whole field.
  Examples: "Turkevich method AND gold", "seed-mediated growth AND gold nanorod",
  "nucleation kinetics AND gold nanoparticle", "in situ TEM AND gold nanoparticle growth"

Step 2 — Search OpenAlex + PubMed per sub-topic
  OpenAlex: title_and_abstract.search with year range 1850-2026
  PubMed: E-utilities with same keywords

Step 3 — Deduplicate by DOI + normalized title

Step 4 — Heuristic screening (two-pass)
  a) Title-based hard exclusion: remove drug delivery, SERS, biosensor, cancer, etc.
  b) Score remaining: title signals + abstract signals + citation count + recency

Step 5 — Merge with manually added foundational classics
  Add papers too old for API search (Faraday 1857, Turkevich 1951, Brust 1994, etc.)

Step 6 — Optional citation expansion from top ~20 papers
  Fetch references/citations via OpenAlex cited_by_api_url
```

#### Available Scripts

These are saved under `scripts/` in this skill directory:

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/search_papers.py` | Search OpenAlex + PubMed across 11 sub-topic queries, deduplicate, save to JSON | `python3 scripts/search_papers.py` → `all_papers.json` |
| `scripts/screen_papers.py` | Two-pass heuristic screening: hard exclusion (title/abstract) + composite scoring. Outputs included/maybe/excluded lists. | `python3 scripts/screen_papers.py` → `{included,maybes,excluded}_papers.json` |
| `scripts/compile_corpus.py` | Merge auto-included + top maybes + manually added classics into final corpus. Handles DOI dedup across sets. | Edit `CLASSICS` list, then `python3 scripts/compile_corpus.py` → `final_corpus.json` |

#### Heuristic Scoring Formula

Scores are 0-200+:
- **Title signals** (0-100+): Inclusion keywords (synthesis, seed-mediated, Turkevich, growth mechanism...) vs hard exclusions (-100)
- **Abstract signals** (0-40): Synthesis terms + gold-specific language - application penalties (-20 each)
- **Citation bonus** (0-10): `min(10, log10(citation_count + 1) * 3)`
- **Recency bonus** (0-5): newer papers get small bonus

**Threshold guidelines (calibrated on gold nanomaterials):**
| Label | Score | Action |
|-------|-------|--------|
| Include | ≥40 | Directly relevant |
| Maybe | 10-39 | Review manually |
| Exclude | <10 | Discard |

#### When to Use Which

| Scenario | Use PISMA | Use Direct API |
|----------|-----------|----------------|
| Broad topic (>500 papers) | ✅ Fast screening | Overkill |
| Niche sub-field | ❌ Too many false positives | ✅ Precision |
| Citation graph/expansion needed | ✅ Built-in | Manual |
| Foundational papers needed | ❌ Year range too narrow | ✅ Open year range |
| ML deps unavailable | ✅ Heuristic-only fallback | ✅ Also heuristic |

### What PISMA Does NOT Replace (These Stay in Our Skill)

| Phase | Content | Why |
|-------|---------|-----|
| Phase 1 | Scope definition, intellectual genealogy, argument map | Conceptual framework — requires domain expertise |
| Phase 5 | Bucket→section mapping | Domain-specific chemical/biological knowledge |
| Phase 6 | C-E-L-T paragraph writing, chemistry nomenclature | Writing methodology |
| Phase 7 | SciencePlots consistent figures | Visual style enforcement |
| Phase 8 | data-consistency-validator, citation cross-check | Domain-specific verification |

### PISMA Output → Our Input

PISMA writes results to `results/` inside the PISMA directory. Key files:

| File | Contents |
|------|----------|
| `results/papers.csv` | All discovered papers with metadata |
| `results/included_papers.csv` | Papers passing topic prefilter |
| `results/top_papers.json` | Ranked shortlist |
| `results/citation_graph.json` | Citation relationships |
| `results/prisma_flow.md` | PRISMA flow diagram with counts |
| `results/review_summary.md` | Human-readable summary |

Import hook:

```python
import json, glob

def import_pisma_results(output_dir):
    """Load PISMA output into our Phase 5 organizer."""
    papers = []
    for f in glob.glob(f"{output_dir}/**/*.json", recursive=True):
        with open(f) as fh:
            data = json.load(fh)
            papers.extend(data.get("papers", []))
    
    # Group by PISMA's classification
    buckets = {}
    for p in papers:
        topic = p.get("topic_assignment", "unclassified")
        buckets.setdefault(topic, []).append(p)
    
    return buckets  # Feeds directly into Phase 5 ORGANIZE
```

### AI Search ─ Supplementary Layer

Beyond PISMA, use general AI search for specific supplementary roles:

| Role | Which Tool | Notes |
|------|-----------|-------|
| Latest pulse check (last 6mo) | Exa (neural semantic) or AnySearch | Catches preprints and blog posts not yet indexed |
| Regulatory / policy context | Tavily or Serper | FDA clearances, CE marks — not in academic DBs |
| Commercial landscape | AnySearch or You.com | Funding, licensing, patent disputes |
| Writing Future Perspectives | Exa + AnySearch | "What's happening RIGHT NOW" |
| Cross-field gap analysis | Exa (semantic similarity) | Papers in adjacent fields missed by keyword search |

**Available tools with rate limits:**

| Tool | Keys | Limit | Status |
|------|------|-------|--------|
| Tavily | 3 keys (2 active) | 10 req/min per key | 🔄 rotating |
| AnySearch | 2 keys | 30 req/min per key | default router |
| Exa | 1 key | 1,000 free/month | neural search |
| Serper (Google) | 1 key | 2,500 free/month | structured |
| DuckDuckGo | none needed | unlimited (slow) | last resort |
| TinyFish | 1 key | 5 req/min | Chinese web only |

**Pitfall — AI search produces confident-sounding but sometimes hallucinated citations. Never trust an AI search result as a definitive paper reference. Always verify via DOI → academic DB cross-check before citing.**

### Database Tier System (Reference)

For reference, the databases PISMA queries and their characteristics:

#### Tier 1 ─ Primary (free, always available)

| Database | API | Python Access | Query Tips | Rate Limit |
|----------|-----|---------------|------------|------------|
| **PubMed** | E-utilities (ESearch + EFetch) | `Bio.Entrez` or direct `requests` | Use MeSH terms for precision; `ESearch` returns PMIDs, `EFetch` gets abstracts | 3/s (no key) / 10/s (with key) |
| **Semantic Scholar** | Graph API v1 | Direct REST (API key for high volume) | 200M papers, citation graph, TLDR summaries; search by title, DOI, author, venue | 100/5min (unauth), higher with key |
| **OpenAlex** | REST API (usage-based, $1/day free) | Direct REST or `pyalex` | Open catalog; search by concept, author, institution, topic | $1/day (~100K calls) |
| **CrossRef** | REST API (free, no key needed) | Direct REST or `habanero` | **Cited-by counts, DOI resolution, reference lists, funding data.** Polite use expected (1 req/s). No API key needed for basic queries. | "Polite" — 1 req/s recommended; no formal cap but handle Retry-After |
| **bioRxiv / medRxiv** | Content API (free) | Direct REST | Date-range queries, 100 results/page; chemistry content via bioRxiv | 3 req/s |
| **PubMed Central (PMC)** | OAI-PMH / FTP / BioC | Direct REST | Full-text XML for Open Access subset | Same as PubMed E-utilities |

#### Tier 2 ─ Supplementary (free, narrow scope)

| Database | Access | Use Case |
|----------|--------|----------|
| **ChemRxiv** | Via CrossRef API | Chemistry preprints |
| **PubChem** | PUG REST API (free) | Compound bioactivity, toxicity, assay data |
| **Unpaywall** | Simple REST (100k/month free) | Locate OA PDFs of paywalled papers |
| **CORE** | REST API (free tier) | 250M+ OA papers, full text available |

#### Tier 3 ─ Subscription (requires institutional access)

| Database | Access | Notes |
|----------|--------|-------|
| **Web of Science** | WoS API Expanded (Clarivate) | Best citation data; requires WoS subscription + developer key |
| **Scopus** | Elsevier Search API | Academic non-commercial free, but institution subscription for full |
| **ScienceDirect** | Elsevier API | Full text access; academic free but restricted |
| **ACS / RSC / Wiley** | No public metadata API | TDM licensing for commercial use only |

**For the user's context** (Tiangong University, materials chemistry/POCT focus): Tier 1 is fully available and sufficient for most review work. Tier 3 requires checking your institution's access.

### 2.5 Custom Query Code

All API calls use the `safe_request` pattern below. Do not call `requests.get()` directly on a database URL.

For ad-hoc single-paper lookups or small batches, use the Python snippet directly. For full review-scale discovery (Phases 2-4), use PISMA (see §2.2-2.4) — the old standalone scripts were removed in Version 8 of this skill because PISMA handles everything they did, plus dedup and citation expansion.

Legacy script → PISMA mapping:
| Legacy script | PISMA replacement |
|---------------|-------------------|
| `scripts/search_pubmed.py` | Source: `pubmed_client.py` (built-in) |
| `scripts/search_s2.py` | Source: `semantic_scholar_client.py` (built-in) |
| `scripts/search_crossref.py` | Source: `crossref_client.py` (built-in) |

```python
# === SAFE REQUEST WRAPPER (must be used for every API call) ===
import requests, time

API_KEY = ""  # Set via NCBI_API_KEY env var or ~/.ncbi_key

def safe_request(url, params, max_retries=3):
    """Rate-limited request with exponential backoff. Use for ALL database calls."""
    if API_KEY:
        params["api_key"] = API_KEY
    delay = 0.10 if API_KEY else 0.34  # 10 req/s or 3 req/s

    for attempt in range(max_retries):
        try:
            r = requests.get(url, params=params, timeout=30)
        except (requests.Timeout, requests.ConnectionError):
            time.sleep(60 * (2**attempt))
            continue
        if r.status_code == 429:
            retry = int(r.headers.get("Retry-After", 60))
            if attempt < max_retries - 1:
                time.sleep(min(retry, 300))
                continue
            raise RuntimeError("BLOCKED: 429 after 3 retries. Wait 24h.")
        if r.status_code == 403:
            raise RuntimeError("BLOCKED: 403 Forbidden. IP may be blacklisted.")
        r.raise_for_status()
        time.sleep(delay)
        return r
    raise RuntimeError(f"Failed after {max_retries} retries.")

# === PubMed via E-utilities ===
def search_pubmed(query, max_results=200):
    params = {"db": "pubmed", "term": query, "retmax": min(max_results, 500),
              "retmode": "json", "sort": "relevance"}
    r = safe_request("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params)
    return r.json().get("esearchresult", {}).get("idlist", [])

def fetch_abstracts(pmids):
    """Batch at 100 per call, each with safe_request."""
    all_articles = []
    for i in range(0, len(pmids), 100):
        batch = pmids[i:i+100]
        params = {"db": "pubmed", "id": ",".join(batch), "retmode": "xml", "rettype": "abstract"}
        r = safe_request("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params)
        # Parse XML with ElementTree...
        all_articles.extend(parse_articles(r.text))
    return all_articles

# === Semantic Scholar ===
def search_s2(query, limit=100):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": query, "limit": min(limit, 100),
              "fields": "title,abstract,year,authors,externalIds,citationCount,venue"}
    r = safe_request(url, params)
    return r.json().get("data", [])

# === OpenAlex ===
def search_openalex(query, per_page=50):
    url = "https://api.openalex.org/works"
    params = {"search": query, "per_page": per_page}
    r = safe_request(url, params)
    return r.json().get("results", [])
```

**⚠️ Rate limit enforcement in all scripts:**
- Every API call must go through `safe_request()` or equivalent
- Never call `requests.get()` directly on a database URL
- See `scripts/search_pubmed.py` for the full implementation

---

### 前沿文献补充(2026-06-09新增步骤)

在Phase 2搜索之后，增加一个独立的前沿文献补充步骤：

1. 使用 `mcp_perplexity_perplexity_search` 搜索"latest advances TOPIC 2024 2025 2026 specific papers"
2. 对返回结果中的每篇论文提取作者、年份、期刊、DOI
3. 将前沿论文按主题分类并入对应节
4. 每个技术主题至少补充3-5篇2023-2026的论文
5. 前沿论文在正文中标明作者名和定量数据(不要只引综述)

前沿论文占整篇综述引用的比例应在30-50%之间，以确保综述不显得"陈旧"。

**Getting IP-banned from these databases will break your research access for days to weeks. Respect the limits.**

### Rate Limit Table

| Database | No API Key | With API Key | Ban Risk | Notes |
|----------|-----------|--------------|----------|-------|
| **PubMed (E-utilities)** | **3 req/sec** per IP | **10 req/sec** | HIGH — IP ban if sustained >10 req/s | HTTP 429 → back off immediately. Get a free API key from NCBI |
| **Semantic Scholar** | **Unusable without key (2026)** — shared pool exhausted globally. Even 0.33 req/s triggers 429 on the 2nd request. PISMA's client works without a key but will waste pipeline time on retries. | 1+ req/s (but registration process is broken — GitHub #104 confirms 5+ day no-response) | HIGH — IP throttled, repeated abuse → block | **Recommendation:** Disable S2 in PISMA config unless you have a working API key. Use OpenAlex/PubMed/CrossRef as primary sources instead. See `references/s2-operational-notes.md` for full details. | |
| **OpenAlex** | **$1/day free** (≈100K calls) | Usage-based pricing above $1/day | MODERATE — just runs out of credits | No ban risk, just stops working |
| **bioRxiv / medRxiv** | **3 req/sec** | Same | MODERATE | 100 results/page; use pagination, not multiple parallel queries |
| **CrossRef** | No formal limit | Same | LOW — but "polite" use expected | Handle 429/Retry-After if it comes |
| **Unpaywall** | **100K/month** | Paid beyond that | LOW | Resets monthly |
| **PubChem (PUG)** | **5 req/sec** | 10 req/sec with key | MODERATE | Similar to E-utilities |

### Enforcement Rules (must be implemented in every search script)

```
Rule 1 ─ Throttle: Insert time.sleep() between every single API call.
  PubMed (no key):    time.sleep(0.34)   →  ~3 req/s
  PubMed (with key):  time.sleep(0.1)    →  ~10 req/s
  Semantic Scholar:   time.sleep(3.1)    →  ~1 req/3s
  bioRxiv:            time.sleep(0.34)
  OpenAlex:           time.sleep(0.1)    →  budget will exhaust before rate limit

Rule 2 ─ Backoff: If you get HTTP 429 (Too Many Requests):
  Wait 60 seconds, retry once.
  If 429 again, wait 300 seconds (5 min), retry.
  If 429 again → STOP, report to user, do not retry same day.

Rule 3 ─ No parallel queries to the same database.
  You may query PubMed AND Semantic Scholar simultaneously (different hosts).
  You may NOT run 2 parallel PubMed queries — they share the same IP rate limit.

Rule 4 ─ Never query >500 results per search in a single run.
  Split large searches into multiple smaller queries (by year, by sub-topic).
  Many databases have practical limits (S2: max 100/query; PMC: max 500/query).

Rule 5 ─ API key checklist before any batch run:
  [ ] PubMed: ncbi_key obtained from https://ncbi.nlm.nih.gov/account/
  [ ] Semantic Scholar: key via partner application
  [ ] OpenAlex: key via free registration
  If any key is missing, use the no-key rate limit for that database.
```

### What to do if you get blocked

| Symptom | Likely Cause | Recovery |
|---------|-------------|----------|
| HTTP 429 (Too Many Requests) | Exceeded rate limit | Back off (Rule 2). Reduce rate by 50%. |
| HTTP 403 (Forbidden) | IP blacklisted | Stop all queries immediately. Wait 24h. Email database support. |
| HTTP 503 (Service Unavailable) | Server overload / your queries | Wait 1h, reduce rate. |
| Sudden "no results" for valid queries | Shadow-banned | Check with web interface. Switch to different database. |

### Database Contact / Appeal

- **NCBI / PubMed**: E-utilities help: info@ncbi.nlm.nih.gov
- **Semantic Scholar**: API support via GitHub issues
- **OpenAlex**: support@openalex.org

### 2.7 Search Fallback Strategy (Critical)

**Academic database APIs are reliable but not always available.** Common failure modes and their fallbacks:

| Failure | Cause | Fallback |
|---------|-------|----------|
| S2 returns HTTP 429 immediately | Rate limit exhausted — unauthenticated S2 is unusable in 2026 (global pool saturated). | Disable S2 source. Use OpenAlex + PubMed + CrossRef. For citation graph data, use OpenAlex's `cited_by_api_url` and `related_works`. |
| S2 returns HTTP 403 | IP blacklisted | Stop S2 completely. Use web_search for the session. Switch proxy endpoint. |
| PubMed E-utilities time out | Proxy/mihomo not running | Start mihomo via `/opt/data/bin/mihomo -d /opt/data/mihomo-config` or use web_search as temporary fallback |
| OpenAlex returns zero credits | Daily $1 budget exhausted | Use web_search or switch to S2 + PubMed only |
| Connection refused to all databases | Proxy is down | Start proxy first. Check with `curl -x http://127.0.0.1:7890 https://httpbin.org/ip` |
| AI search (web_search) returns hallucinated citations | Search engine confabulation | Cross-check EVERY citation via DOI → PubMed/S2 before including. Never cite an AI search result without verification. |

**Fallback decision tree:**
```
Database API available?
  ├─ Yes → Use it with safe_request + rate limiting (preferred)
  └─ No  → Use web_search (Hermes tool) for initial sweep.
            Tag all AI-found citations as [UNVERIFIED].
            When DB API recovers (next session or 1h later),
            run DOI/PMID cross-check on all [UNVERIFIED] refs.
```

### 2.8 Semantic Scholar Optimization Strategy

S2 is the most powerful but also the most rate-limited database in the stack. These optimizations are critical.

#### 2.8.1 S2 API Key — Reality Check

**The S2 API key registration process is effectively broken.** The "Request an API Key" button on the API page is a same-page anchor link that scrolls to a non-functional section. Multiple GitHub issues (e.g., SakanaAI/AI-Scientist #104) confirm: users applied and received no response for 5+ days or indefinitely.

**Critical finding: PISMA's S2 client works WITHOUT an API key.** The code (semantic_scholar_client.py lines 37-39) checks `if config.api_settings.semantic_scholar_api_key:` before adding the header — if no key is set, it simply sends requests without authentication. The API still returns results; you just get a lower rate limit.

Without key: **100 requests per 5 minutes** (~1 req/3s). With key: substantially higher (varies, but rarely obtainable).

If you somehow do get a key:
```
Store in: S2_API_KEY env var
```
Key affects:
- Rate limit (10-100x improvement)
- Access to bulk endpoints
- Higher offset limits for pagination

**Config adjustment when running PISMA without an S2 key:**
Lower the default rate limits in the PISMA config (or via CLI args) to match the unauthenticated cap:
```json
{
  "api_settings": {
    "semantic_scholar_calls_per_second": 0.3,
    "semantic_scholar_max_requests_per_minute": 20,
    "semantic_scholar_request_delay_seconds": 3.0,
    "semantic_scholar_retry_attempts": 4,
    "semantic_scholar_retry_backoff_strategy": "exponential",
    "semantic_scholar_retry_backoff_base_seconds": 5.0
  }
}
```
Or via PISMA CLI:
```bash
python main.py run --config gold_review_config.json \
  --semantic-scholar-calls-per-second 0.3 \
  --semantic-scholar-max-requests-per-minute 20
```

**Without these adjustments, the default 3 req/s will trigger 429s within seconds when no API key is present.**

#### 2.8.2 Use Bulk Endpoints (Critical Optimization)

| Endpoint | Regular | Bulk | Efficiency Gain |
|----------|---------|------|-----------------|
| **Paper search** | `/graph/v1/paper/search` (100 results/call) | `/graph/v1/paper/search/bulk` (1,000 results/call) | **10x** — 1 request instead of 10 |
| **Paper lookup** | GET `/paper/{id}` (1 paper) | POST `/paper` (up to 1,000 papers by DOI/ID) | **1000x** — 1 request instead of 1000 |

**Always use the bulk search for initial sweeps.** Example:

```python
# BAD: 10 requests for 1,000 papers
for i in range(10):
    r = requests.get(url, params={"query": q, "offset": i*100, "limit": 100})
    time.sleep(3.1)

# GOOD: 1 request for 1,000 papers
r = requests.get(f"{S2}/paper/search/bulk", params={"query": q, "limit": 1000})
# Note: bulk endpoint may not return abstracts or TLDR. Use for discovery only,
# then fetch details via POST /paper for selected papers.
```

#### 2.8.3 Citation Traversal Strategy

When doing forward/backward citation traversal from anchor papers, the dedicated endpoints are more efficient:

```python
# Optimal citation traversal
s2_paper_id = "CorpusId:123456"  # Get this from initial search

# One call gets 1,000 citing papers (use offset for more)
# This is MUCH cheaper than individual paper lookups
r_citing = requests.get(f"{S2}/paper/{s2_paper_id}/citations",
    params={"limit": 1000, "fields": "title,year,citationCount"})
# 1 request = up to 1,000 citing papers

r_cited = requests.get(f"{S2}/paper/{s2_paper_id}/references",
    params={"limit": 1000, "fields": "title,year,citationCount"})
# 1 request = up to 1,000 references
```

#### 2.8.4 Batch Paper Lookup by DOI

After initial discovery, fetch full details for selected papers in batches:

```python
import requests, json

def batch_paper_lookup(doi_list, api_key=""):
    """Look up up to 1,000 papers by DOI in a single POST request."""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key
    payload = {"ids": doi_list}
    r = requests.post(
        "https://api.semanticscholar.org/graph/v1/paper/batch",
        json=payload, headers=headers, timeout=30
    )
    return r.json()

# Usage: 50 DOIs = 1 request
papers = batch_paper_lookup([
    "DOI:10.1039/df9511100055",    # Turkevich
    "DOI:10.1038/physci241020a0",   # Frens
    "DOI:10.1039/c39940000801",    # Brust
    "DOI:10.1021/cm020732l",       # El-Sayed
])
```

#### 2.8.5 Local Caching

Every S2 result should be cached locally to avoid repeated queries:

```python
import os, json, hashlib

S2_CACHE_DIR = "/opt/data/cache/s2/"

def s2_cached_query(query, max_age_days=7):
    """Query S2 with local caching. Returns cached result if fresh."""
    cache_key = hashlib.md5(query.encode()).hexdigest()
    cache_path = f"{S2_CACHE_DIR}/{cache_key}.json"
    
    # Check cache
    if os.path.exists(cache_path):
        age = time.time() - os.path.getmtime(cache_path)
        if age < max_age_days * 86400:
            with open(cache_path) as f:
                return json.load(f)
    
    # Query S2
    result = actual_s2_query(query)
    
    # Save to cache
    os.makedirs(S2_CACHE_DIR, exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(result, f)
    
    return result
```

#### 2.8.6 S2 Rate Limit Budget Calculator

Plan your runs with this mental model:

```
Budget per 5-minute window (no key): 100 requests

Cost of each operation:
  Bulk search (/paper/search/bulk):            1 request → 1,000 papers
  Citation lookup (citations + references):    2 requests → 2,000 papers
  Batch paper detail (POST /paper/batch):      1 request → 1,000 papers
  Regular search (/paper/search):              1 request → 100 papers
  Single paper detail (GET /paper/{id}):       1 request → 1 paper

Optimal strategy for a full review pipeline:
  1. Bulk search for each concept:      3-5 concepts × 1 req =  3-5 req
  2. Batch detail for selected papers:  1 req                       1 req
  3. Citation traversal for anchors:    3-5 anchors × 2 req =    6-10 req
  4. Total:                                                      10-16 req
  → One budget window is enough for an entire review.
```

#### 2.8.7 When S2 Is Down (Fallback Chain)

| S2 Status | Fallback | What You Lose |
|-----------|----------|---------------|
| 429 rate limited | Wait 5 min → retry (usually fails again). **Recommendation:** disable S2 entirely and use OpenAlex for concept tags, CrossRef for cited-by counts. S2 without a key is not viable in 2026. | Citation graph, TLDR, forward/backward traversal — but these can be replaced by OpenAlex's citation data |
| 403 blocked | Same proxy IP may be blacklisted. Switch proxy node or bypass proxy for S2 (direct connection may work). | All S2 data |
| Empty results for valid queries | Try rephrasing query with specific keywords. Use web_search as temporary fallback. Mark results [UNVERIFIED]. | S2's AI-ranked completeness |

### 2.9 Recommended Search Cascade (2026 Update)

```markdown
0. CrossRef (always first):  Resolve key paper DOIs → get cited-by counts to prioritize.
1. PubMed:              Broad MeSH-based query → collect PMIDs + abstracts
2. OpenAlex:            Same query → collect concept-tagged results for classification
                        (use `cited_by_api_url` for citation graph data as S2 substitute)
3. CrossRef:            For every paper in the final set → confirm DOI, get cited-by count
4. Preprint Check:      bioRxiv + ChemRxiv for papers too new for peer review
5. Gap Check:           Cross with last 2-3 existing reviews on the same topic

⚠️ Semantic Scholar is omitted from the cascade. As of 2026, the unauthenticated API
   is rate-limited to effectively 0 requests (shared global pool exhausted) and the
   API key registration process is broken. See references/s2-operational-notes.md.

   If you have a working S2 API key, insert S2 between PubMed and OpenAlex above.
```

### 2.10 Time Window Rules (from user correction)

```
Foundational papers:     NO TIME LIMIT. Go back to Faraday 1857, Mie 1908,
                         Turkevich 1951, or earlier if needed.
Recent developments:     LAST 5 YEARS (2021-2026 at time of writing).
                         Updates to the review must shift this window.
```

---

## Phase 3 ─ DEDUP (Cross-Database Deduplication)

### 3.1 Problem
PubMed, Semantic Scholar, OpenAlex, and bioRxiv overlap significantly. Searching all four without deduplication inflates your paper count by 30-50%.

### 3.2 Deduplication Strategy

| Method | Precision | Recall | Implementation |
|--------|-----------|--------|---------------|
| **DOI matching** | 100% | ~70% | `doi.lower().strip()` → set comparison |
| **Title normalization** | ~95% | ~85% | Lowercase, remove punctuation, fuzzy match (Levenshtein ratio >0.85) |
| **PMID matching** | 100% | ~50% | Direct PMID lookup |
| **Combined** | ~98% | ~95% | Run all three sequentially |

### 3.3 PRISMA Flow Tracking

Maintain a record:

| Step | Count |
|------|-------|
| Records identified from PubMed | XXX |
| Records identified from Semantic Scholar | XXX |
| Records identified from OpenAlex / bioRxiv / other | XXX |
| **Total before dedup** | XXX |
| Duplicates removed | XXX |
| **Total after dedup** | XXX |
| Records excluded by title/abstract screen | XXX |
| Reports sought for retrieval | XXX |
| Reports assessed for eligibility | XXX |
| Reports excluded (with reasons) | XXX |
| **Studies included in review** | XXX |

---

## Phase 4 ─ CLASSIFY (Thematic Categorization)

### 4.1 Goal
Assign each deduped paper to a thematic bucket. Buckets should map to planned review sections.

### 4.2 Classification Strategies

| Method | When to Use | Implementation |
|--------|-------------|---------------|
| **Keyword-based** | Well-defined categories | Regex on title + abstract; fast, interpretable |
| **LLM-based** | Ambiguous boundaries | Ask the LLM to classify each abstract into one of N buckets |
| **Citation clustering** | Exploratory topics | Use citation graph (S2 API) to detect paper clusters |

### 4.3 Classification Log Format

```json
{
  "bucket": "Signal amplification - Enzyme-free",
  "papers": [
    {"pmid": "12345", "title": "CHA-based DNAzyme sensor", "year": 2024, "citationCount": 45},
    {"pmid": "67890", "title": "HCR signal enhancement", "year": 2025, "citationCount": 12}
  ],
  "bucket_question": "What is the gain-to-complexity ratio of enzyme-free methods?",
  "key_findings": "CHA achieves ~10³-fold amplif. in 30 min; HCR offers multiplexing at slower kinetics"
}
```

### 4.4 Classification Script

When using the `precision-review-search` alternative for Phases 2-4 (instead of PISMA),
use `scripts/classify_papers.py` from that skill to classify the final corpus
into section-level buckets. The script:

1. Reads `final_corpus.json` (from `compile_corpus.py`)
2. Scores each paper against N section-matched buckets
3. Outputs `classification.json` with each paper's primary bucket + score
4. Summary lists paper counts per bucket — feeds directly into Phase 5 ORGANIZE

See `precision-review-search` skill for the full script and usage instructions.

---

## Phase 5 ─ ORGANIZE (Structure Building)

### 5.1 From Buckets to Sections

| Bucket | Becomes | Section Role |
|--------|---------|-------------|
| Fundamentals | Section 2: Basics | Essential background |
| Enzyme-free amplif. | Section 3.1 | First thematic pillar |
| Enzyme-assisted amplif. | Section 3.2 | Second thematic pillar |
| Nanomaterial amplif. | Section 3.3 | Third thematic pillar |
| Clinical translation | Section 4: Reality check | Critical analysis |
| Comparison | Section 5: Comparison table | Synthesis |
### 5.2 Section Outline Template

#### Critical Review

```

1. Introduction (1,000-2,000 words)
   [Hook -> History -> Gap -> Roadmap]

2. Fundamentals (1,000-3,000 words)
   2.1 [Mechanism 1]
   2.2 [Mechanism 2]

3. [Thematic Area A] (2,000-5,000 words)
   3.1 [Sub-topic A1] -- C-E-L-T paragraphs
   3.2 [Sub-topic A2]

4. [Thematic Area B] (2,000-5,000 words)
   4.1 [Sub-topic B1]

5. Comparative Analysis (1,000-2,000 words)
   [Unified comparison table] [Decision framework]

6. Conclusions and Future Perspectives (1,000-2,000 words)
   [Summary -> Unresolved questions -> Concrete next steps]
```

#### Comprehensive / 大综述 (for Chem Rev / Chem Soc Rev, ~150-250 references)

Use the framework-first structure — the organizing principle is an analytical lens, not an argument:

```

1. Introduction — Open with a specific tension point or anomalous fact, not general framing
2. Analytical framework — The organizing principle (e.g. six-dimension comparison, simplification-cost exchange, complexity placement)
3. Sample preparation — The first bottleneck (often missing in other reviews)
4. Technology tree — Organized by structural logic (e.g. "what was sacrificed"), not by chronology or discovery order
5. Paradigm-shifting method — e.g. CRISPR-Dx as a separate paradigm, not a sub-topic of amplification
6. Signal readout — The cost of each simplification in the detection chain
7. Integration — How components are combined (fluid control logic, microfluidic platforms)
8. Commercialization gap — Academic LOD vs product LOD (typically 2-5 orders of magnitude difference)
9. Outlook — AI, synthetic biology, wearables, or other frontier directions
10. Conclusion — Scenario-method decision tree, not a summary

```

Key differences from critical review: (a) Section 2 establishes a framework not an argument; (b) sample prep and commercialization are non-negotiable sections; (c) comparison tables are filled with real numbers not qualitative labels; (d) conclusion provides a decision rule not a restatement.

#### Fast-Track: Thesis Chapter 1 to Review

When the user has an existing thesis Chapter 1 and wants to extract a review quickly:

1. Skip Phase 2-4 (search/dedup/classify) — the thesis already contains curated references
2. Decompose Chapter 1 into thematic clusters (Phase 0)
3. Build a DIFFERENT analytical framework (not the thesis's organizing logic)
4. Supplement the thesis references with the latest 1-2 years of literature
5. Use the thesis references to support YOUR framework, not to reproduce their narrative

#### Comprehensive / 大综述 (for Chem Rev / Chem Soc Rev)

For reviews that span competing technology platforms (e.g. PCR vs LAMP vs RPA vs CRISPR), use the framework-first structure:

```
1.  Introduction -- Open with a specific tension point, not WHO ASSURED
2.  Analytical framework -- The organizing principle (e.g. six-dimension comparison)
3.  Sample preparation -- The first bottleneck (often missing from other reviews)
4.  Technology tree -- Organized by "what was sacrificed", not by chronology
5.  Paradigm-shifting method -- e.g. CRISPR-Dx as a separate paradigm, not a sub-topic
6.  Signal readout -- The cost of each simplification in the optical chain
7.  Integration -- Fluid control logic categories
8.  Commercialization gap -- Academic LOD vs real product LOD (2-5 orders of magnitude)
9.  Outlook -- AI, synthetic biology, wearables
10. Conclusion -- Scenario-method decision tree
```

Key differences from critical review: (a) Section 2 establishes a framework not an argument; (b) sample prep and commercialization are non-negotiable sections; (c) comparison tables are filled with real numbers not qualitative labels; (d) conclusion provides a decision rule not a summary.

---

## Phase 6 ─ WRITE (Drafting)

### 6.1 Paragraph Structure: C-E-L-T (Internal) or Gold Style (External)

There are two writing modes for Phase 6 output. Choose based on user preference:

**Mode A: C-E-L-T (for Critical Reviews)** — Expose the structure:
- Use C-E-L-T as both thinking tool and deliverable format
- Each paragraph explicitly carries Claim, Evidence, Limitation, Transition
- Recommended for Biosensors Bioelectron / TrAC / Anal Chem level reviews
- See the table below for the C-E-L-T format

**Mode B: Gold Style (for 大综述 / Comprehensive Reviews)** — Hide the structure:
- C-E-L-T remains the thinking structure during drafting but MUST be stripped before delivery
- The final output is flowing academic prose with no exposed structural markers
- Citation format includes journal abbreviations: (Author, Year, *Journal Abbrev*, DOI:xxx)
- Use the "钉子开门" technique: every section opens with a specific data point
- See `references/gold-style-writing.md` for the full convention set
- Recommended for Chemical Reviews / Chem Soc Rev level reviews

**Choosing between modes:** Default to C-E-L-T Mode A. Switch to Gold Style Mode B when the user says "像第三个那样写", "改成金纳米那种风格", or explicitly asks for journal-name citations and flowing prose. The signal is usually explicit — don't guess.

Every thematic paragraph follows (Mode A format):

| Component | Function | Length |
|-----------|----------|--------|
| **Claim** | The paragraph's single argument | 1 sentence |
| **Evidence** | 1-3 papers supporting the claim | 2-5 sentences |
| **Limitation** | What the evidence does NOT address | 1-2 sentences |
| **Transition** | Link to next paragraph/topic | 1 sentence |

### 6.2 Writing Constraints

- **No annotated bibliographies.** Every paragraph must have a claim
- **Active voice.** "We summarize", not "It is summarized"
- **No hedging intensifiers.** Delete "novel", "very", "highly", "importantly"
- **No "It is worth noting that"** — if it's important, say it plainly
- **Chemical nomenclature:** Full name + abbreviation at first mention
- **Biological terms:** Species italicized; EC numbers for enzymes
- **Numbers:** ACS Style Guide (space between number and unit)

### 6.3 Critical Pitfall: Do Not Reorganize, Redesign

When writing a review on a topic the user has already written about (their thesis, a prior paper, etc.), the first instinct is to reorganize their existing work into a new structure. **This is wrong and the user will reject it.**

The learning from this session (2026-06-09, user 杜昊天, thesis on gated nucleic acid detection):

1. The agent wrote a first version organized around the user's thesis argument (layered gating for false positive control). The user rejected it: "不要和我的研究内容一样".
2. The second version was organized around a completely different analytical framework (simplify-and-pay trade-off). The user confirmed: "这个是对的".

**How to avoid this:**
- If the user says "如果你来写"/"你会这么写"/"重新写", they want YOUR framework, not theirs
- Distill your own organizing principle before looking at their material
- Write §2 (the framework) before writing anything else — if §2 reads like their thesis §1, pivot
- The user's references should support YOUR argument, not be the skeleton of it

### 6.4 Information Density Requirements

This is the single most important quality signal for this user. A review that passes the framework test but fails the density test will be rejected as "信息密度不够".

#### The 钉子开门 Technique for Section Openings

Every section should open with a specific quantitative fact, not a general statement about the field. Two styles compared:

| Weak opening (general) | Strong opening (data-dense) |
|------------------------|-----------------------------|
| "核酸提取是POCT中的重要步骤，存在诸多挑战。" | "Cepheid Xpert（超声+磁珠提取）的临床LOD约250 copies/mL；Abbott ID NOW（直接裂解+滤膜）的真实世界LOD为500-20,000 copies/mL。两者差了1-2个数量级，差距来源不是扩增效率而是前处理。" |
| "CRISPR/Cas12a具有很高的附带切割活性。" | "Cas12a附带切割周转率约1250 s-1——单分子识别事件在1分钟内可切割约75,000个报告探针(Chen 2018, Science, DOI:10.1126/science.aar6245)。" |
| "等温扩增技术各有优缺点。" | "LAMP的NTC假阳性率5-30%(Kim 2023, DOI:10.1016/j.aca.2023.341693)；RPA在37°C下NTC假阳性率>40%(Ullah 2024, DOI:10.3390/antibiotics13100984)；PCR在同等对照中<1%。这一差距是温度降低后ΔG歧视度丧失的热力学结果。" |

**Rules for data-dense writing (apply to every paragraph in Phase 6):**

1. **No claim without a number.** Every performance claim (LOD, speed, specificity, cost) must cite a specific numerical value from a specific paper. Not "high sensitivity" but "25 copies/reaction (Tan 2024, DOI:...)".
2. **Comparison tables must be filled with real numbers.** Replace "high / medium / low" with actual LOD ranges (copies/reaction), actual time (minutes), actual costs (currency). Use "—" for unavailable data rather than guessing.
3. **Cite the specific paper for each number.** A number without a citation is an opinion, not evidence. Exception: well-established constants that any textbook covers.
4. **Prefer comparative over single numbers.** "X achieves Y vs Z achieves 10Y under same conditions" reveals the trade-off. Single-point numbers do not.
5. **Admit the range, not just the best case.** Report best-case AND typical-range. "LAMP LOD: 22-1000 copies/reaction" is honest; "LAMP LOD: 22 copies/reaction" is selective reporting.

### 6.5 Citation Format: Inline (Author, Year, DOI)

Use inline format: `(Author, Year, DOI:10.xxxx/xxxxx)` — **not** markdown link `([Author Year](https://doi.org/xxx))`. The user may need to copy-paste individual citations into reference managers, and plain-text DOI strings are more portable than embedded links.

Multiple authors: use "等人" for Chinese-language output: `(Tan等人, 2024, DOI:10.1002/jmv.29624)`

### 6.6 Output Format: Markdown Preferred

Deliver the review as **plain markdown (.md)** unless the user explicitly asks for PDF. Chinese academic users often want to review/edit the prose directly before formatting. Do not automatically compile to PDF — it wastes time and the user may reject the format.

When the user says "以后以md给出", stop producing any non-markdown output (HTML, PDF) until explicitly asked. Keep the markdown clean enough to paste directly into a research note or manuscript.

### 6.7 Final Polish: Strip the Scaffolding

After Phase 6 (WRITE) and before delivery:

1. Strip all C-E-L-T markers from the final text — they are working notes, not prose
2. Remove thinking residues: isolated "C："/"L："/"T：" at paragraph starts, "关键数据锚点", "关键观察", "数据来源："
3. Remove rhetorical staging questions: "这一退化在真实场景中如何呈现？"
4. Run the `humanizer` skill to strip AI patterns (em dash overuse, filler phrases, generic transitions)
5. Verify every paragraph reads naturally when said aloud, without the underlying structure showing

When the user asks you to write a review about a topic they have published/pending work on (thesis chapter, previous paper, draft), **do NOT write a reorganized version of their content** — even if you rephrase everything. The user will immediately recognize it as their own structure repackaged.

**Instead:** Bring a genuinely different analytical framework. Change the organizing principle, the core question, or the through-line. Examples:
- If their thesis is organized by "technology type" (PCR→LAMP→RPA→CRISPR), organize yours by "what was given up" (simplification cost framework)
- If their thesis argues for a specific technical solution (layered gating), yours should ask a meta-level question (which costs are acceptable in which scenarios)
- Your value is in the different perspective, not in better cataloging of the same papers

**Verification test:** If a user could say "this is just my literature review with different words", you haven't gone far enough.

### 6.4 Information Density Requirements for 大综述

A "大综述" targeting Chemical Reviews / Chem Soc Rev (150-250 references, 15,000-30,000 words) requires substantially higher density than a critical review:

| Aspect | Critical Review | 大综述 (this) |
|--------|----------------|--------------|
| References | 40-80 | 150-250 |
| Unique claims per section | 3-5 | 8-15 |
| Quantitative comparisons | Qualitative | Tables with specific numbers |
| Data per claim | 1-2 papers | 3-5 papers per claim |
| Sample prep discussion | Often skipped | Required as a major section |
| Commercial landscape | Optional | Required section |

**Every claim needs a number attached.** Not "灵敏度退化" but "灵敏度退化约14×(Sidstedt 2018, DOI:10.1007/s00216-018-0931-z)".

**Every comparison needs a table** with actual numerical ranges, not qualitative high/medium/low evaluations.

### 6.5 Citation Format: Inline (Author, Year, DOI)

Use inline format: `(Author, Year, DOI:10.xxxx/xxxxx)` — **not** markdown link `([Author Year](https://doi.org/xxx))`. The user may need to copy-paste individual citations into reference managers, and plain-text DOI strings are more portable than embedded links.

Multiple authors: use "等人" for Chinese-language output: `(Tan等人, 2024, DOI:10.1002/jmv.29624)`

### 6.6 Output Format: Markdown Preferred

Deliver the review as **plain markdown (.md)** unless the user explicitly asks for PDF. Chinese academic users often want to review/edit the prose directly before formatting. Do not automatically compile to PDF via weasyprint — it wastes time and the user may reject the format.

### 6.7 Final Polish: Run Through Humanizer

After Phase 6 (WRITE) and before delivery:

1. Strip all C-E-L-T markers from the final text — they are working notes, not prose
2. Remove thinking residues: isolated "C："/"L："/"T：" at paragraph starts, "关键数据锚点", "关键观察", "数据来源："
3. Remove rhetorical staging questions: "这一退化在真实场景中如何呈现？"
4. Run the `humanizer` skill to strip AI patterns (em dash overuse, filler phrases, generic transitions)
5. Verify every paragraph reads naturally when said aloud, without the underlying structure showing

### 6.8 Data Anchor Reference File

The `references/poct-nucleic-acid-data-anchors.md` file contains verified quantitative benchmarks for POCT nucleic acid detection reviews — inhibitor thresholds, amplification method performance ranges, correction factors, and "钉子开门" (nail-opening) data points. Load it for quick access when starting Phase 1 on a POCT-adjacent review topic.

### 6.2b Critical Pitfall: Do Not Reorganize, Redesign

When writing a review on a topic the user has already written about (their thesis, a prior paper, etc.), the first instinct is to reorganize their existing work into a new structure. **This is wrong and the user will reject it.**

The learning from this session (2026-06-09, user 杜昊天, thesis on gated nucleic acid detection):

1. The agent wrote a first version organized around the user's thesis argument (layered gating for false positive control). The user rejected it: "不要和我的研究内容一样".
2. The second version was organized around a completely different analytical framework (simplify-and-pay trade-off). The user confirmed: "这个是对的".

**How to avoid this:**
- If the user says "如果你来写"/"你会这么写"/"重新写", they want YOUR framework, not theirs
- Distill your own organizing principle before looking at their material
- Write §2 (the framework) before writing anything else — if §2 reads like their thesis §1, pivot
- The user's references should support YOUR argument, not be the skeleton of it

### 6.3 Language Selection (2026-06-03)

**Default: Chinese.** Most users of this skill are Chinese-speaking materials chemists.
Write in Chinese unless the user explicitly says "English" or the target journal
requires English.

Chinese writing rules:
- Key terms keep the original English parenthetically at first mention:
  "局域表面等离激元共振（LSPR）"
- All DOI references inline: `([Author Year](https://doi.org/10.xxxx/xxxx))`
  — not as a separate reference list section. This allows users to copy-paste
  individual citations into their reference manager.
- C-E-L-T structure in Chinese: Claim → Evidence → Limitation → Transition.
  Label each section explicitly with **C:**, **E:**, **L:**, **T:** markers.
- Use Chinese scientific prose conventions (active voice, short paragraphs,
  one claim per paragraph). Avoid English sentence structures translated directly.

### 6.4 Citation Format: Inline Plain Text (Author, Year, DOI:xxx)

Use plain-text inline format **only**: `(Author, Year, DOI:10.xxxx/xxxxx)`. Do NOT use markdown hyperlinks.

| Correct ✅ | Wrong ❌ |
|------------|---------|
| `(Sidstedt, 2018, DOI:10.1007/s00216-018-0931-z)` | `([Sidstedt 2018](https://doi.org/10.1007/s00216-018-0931-z))` |

Rationale: the user copies citations into reference managers. Plain-text DOI strings are more portable than embedded hyperlinks. Chinese output: use `(Tan等人, 2024, DOI:10.1002/jmv.29624)` for Chinese-language text.

### 6.6 Reference Count Requirements (2026-06-09)

The user requires each review to have at least 200 unique DOIs. Build a reference list section at the end of the document with 200+ numbered entries, each with full citation details: Author(s), Year, Title, Journal Abbreviation, DOI.

### 6.7 Two-Version Output (2026-06-09)

This user wants two versions of each review:
1. Essay version (no suffix): flowing prose, narrative openings, conversational tone. For internal discussion.
2. Academic version (-v3-academic): formal tone, no narrative openings, no rhetorical questions. For journal submission.

Conversion rules: replace cinematic openings with direct factual statements, replace informal assertions with measured phrasing, remove rhetorical questions, remove we as narrative voice, keep all data and citations identical between versions.

### 6.8 Section Heading Convention

Use plain numbering: # 1 Introduction, ## 2.1 Method. Do NOT use section markers such as the paragraph symbol.

### 6.9 Post-Writing: Two-Version Output (Academic vs Essay)

The user requires two versions of every written deliverable (learned 2026-06-09):

1. **Default version (no suffix in filename):** Flowing/essay style with narrative openings, conversational tone, used for internal discussion and blog posting
2. **Academic version (filename ends `-academic`):** Formal tone, no narrative openings, no rhetorical questions, no "我们" as narrative voice, for journal submission

Conversion checklist when producing the academic version from the essay version:
- [ ] Cinematic/narrative openings → direct factual statements
- [ ] "不是A——是B" dramatic contrasts → measured comparative statements
- [ ] Rhetorical questions → factual statements
- [ ] "我们" as narrative voice → third person or passive voice
- [ ] Section marker references in text → "第N节"
- [ ] All data and citations identical between both versions

### 6.10 Output Format: Markdown Preferred, Not PDF (2026-06-09)

Deliver the final review as **plain markdown (.md)** unless the user explicitly asks for PDF. Do not auto-compile to PDF via weasyprint — the user may reject the format ("以后以md给出"). Chinese academic users want to review/edit the prose directly before formatting.

When the user says "以后以md给出", stop producing any non-markdown output (HTML, PDF) until explicitly asked. Keep the markdown clean enough to paste directly into a research note or manuscript.

Signal: if you just spent time converting to PDF and the user complains about format, that time was wasted. Default to .md for all drafts and final deliverables.

C-E-L-T markers (C:, E:, L:, T:) are a THINKING structure only. They MUST NOT appear in the deliverable text. The final markdown should contain only:
- Section headers (#, ##, ###)
- Plain paragraphs without bold/italic structural labels
- Tables with real data
- Citations in (Author, Year, DOI:xxx) format
- No "关键观察：", "注意：" or other thinking artifacts

### 6.6 写作模式选择：Critical Review 与 金风格/大综述（2026-06-09）

根据目标期刊规模和用户期望选择写作模式：

| 特征 | Critical Review | 金风格/大综述 |
|------|---------------|-------------|
| 目标期刊 | Biosens Bioelectron / TrAC / Anal Chem | Chem Rev / Chem Soc Rev / Nat Rev Bioeng |
| 参考文献 | 约47篇精引 | **≥200篇唯一DOI** |
| 框架标签 | C-E-L-T每段标注(**C: **/etc) | 框架在引言说完，正文不露标签 |
| 段落结构 | 短段(80-150字)，每段一个论断 | 长段(150-300字)，覆盖一个概念单元 |
| 数据密度 | 每段1-2个具体数字 | 每段2-3个具体数字+对应引用 |
| 引用格式 | (Author, Year, DOI) | (Author, Year, *Journal Abbr*, DOI:10.xxxx) |
| 前沿覆盖 | 可少可多 | **必须**覆盖最近3年(2023-2026)具体进展 |
| 交付格式 | md或PDF | **纯md** |

**选择规则：** 用户说"大综述"或目标期刊为高影响因子时，选择金风格。从第一版开始就按金风格写，不要从Critical Review改版——改版成本高于重写。

**关键陷阱：** 金风格不是"文章更长"而是"信息更密"。每段必须有2-3个独立数据点支持。空泛的一般性陈述在大综述中比在Critical Review中更难容忍。

有关金风格的具体写作规范——段落结构、去除框架标签、引用格式——参见 `review-chem-bio-writing` skill 的"金风格(Gold Style)写作模式"节。

Load `user-writing-style` and adapt to English:
- "钉子开门" → "open with a concrete observation/object/experiment"
- "追问代价" → "trace the trade-off: what performance was sacrificed for what gain?"
- "数据密度优先" → "every claim needs a supporting citation or data point"

### 6.6 Data Density Requirements

This is the single most important quality signal for this user. A review that passes the framework test but fails the density test will be rejected as "信息密度不够".

#### The 钉子开门 Technique for Section Openings

Every section should open with a specific quantitative fact, not a general statement about the field. Two styles compared:

| Weak opening (general) | Strong opening (data-dense) |
|------------------------|-----------------------------|
| "核酸提取是POCT中的重要步骤，存在诸多挑战。" | "Cepheid Xpert（超声+磁珠提取）的临床LOD约250 copies/mL；Abbott ID NOW（直接裂解+滤膜）的真实世界LOD为500-20,000 copies/mL。两者差了1-2个数量级，差距来源不是扩增效率而是前处理。" |
| "CRISPR/Cas12a具有很高的附带切割活性。" | "Cas12a附带切割周转率约1250 s-1——单分子识别事件在1分钟内可切割约75,000个报告探针(Chen 2018, Science)。" |
| "等温扩增技术各有优缺点。" | "LAMP的NTC假阳性率5-30%(Kim 2023)；RPA在37C下NTC假阳性率>40%(Ullah 2024)；PCR在同等对照中<1%。这一差距是温度降低后DeltaG歧视度丧失的热力学结果。" |

**Rules for data-dense writing (apply to every paragraph in Phase 6):**

1. No claim without a number. Every performance claim (LOD, speed, specificity, cost) must cite a specific numerical value from a specific paper. Not "high sensitivity" but "25 copies/reaction (Tan 2024)".
2. Comparison tables must be filled with real numbers. Replace "high / medium / low" with actual LOD ranges (copies/reaction), actual time (minutes), actual costs (currency). Use "—" for unavailable data rather than guessing.
3. Cite the specific paper for each number. A number without a citation is an opinion, not evidence. Exception: well-established constants.
4. Prefer comparative over single numbers. "X achieves Y vs Z achieves 10Y under same conditions" reveals the trade-off. Single-point numbers do not.
5. Admit the range, not just the best case. Report best-case AND typical-range. "LAMP LOD: 22-1000 copies/reaction" is honest; "LAMP LOD: 22 copies/reaction" is selective reporting.

#### Phase 6 Deliverable Format

User preference: deliver draft sections as raw markdown (.md) files. Only compile to HTML/PDF as a final verification step and only when the user explicitly requests it. The signal "以后以md给出" means stop producing compiled outputs until told otherwise. The markdown should be clean enough to paste directly into a research note or manuscript.

---

## Phase 7 ─ FIGURES (Consistent Style Generation)

### 7.1 Principle
> All figures in a single review must share a unified style — identical font, line width, color palette, axis formatting, and resolution. This is not aesthetic preference; it is a publication requirement.

### 7.2 Toolchain
```
SciencePlots (matplotlib style sheets) + seaborn (statistical plots) + matplotlib
```

### 7.3 Style Enforcement

EVERY figure-generating code block must start with:

```python
import matplotlib.pyplot as plt
import scienceplots
import seaborn as sns

# ENFORCE UNIFIED STYLE — pick ONE and use everywhere
plt.style.use(['science', 'nature'])   # Nature style
# plt.style.use(['science', 'acs'])    # ACS style
sns.set_context('paper')
```

### 7.4 Color Palettes

```python
# Colorblind-safe (Wong, Nature Methods 2011)
CB_PALETTE = {
    'blue': '#0072B2', 'orange': '#E69F00', 'green': '#009E73',
    'pink': '#CC79A7', 'yellow': '#F0E442', 'skyblue': '#56B4E9',
    'vermilion': '#D55E00', 'black': '#000000'
}
sns.set_palette(list(CB_PALETTE.values()))
```

### 7.5 Figure Type Templates

| Type | When | Code |
|------|------|------|
| **Bar chart** | Comparing metrics | `sns.barplot()` with error bars |
| **Line chart** | Time trends | `sns.lineplot()` with CI |
| **Scatter** | Correlation | `sns.scatterplot()` with regression |
| **Heatmap** | Comparison matrix | `sns.heatmap()` with annotation |
| **PRISMA flow** | Literature selection | matplotlib or draw.io |

### 7.6 Figure Checklist

- [ ] Uses `scienceplots` (not raw matplotlib defaults)
- [ ] Font consistent across all figures
- [ ] Color palette colorblind-safe and identical
- [ ] Resolution ≥ 300 dpi
- [ ] Axis labels with units
- [ ] No 3D effects, drop shadows, or bevels
- [ ] Export: TIFF or EPS for submission

---

## Phase 8 ─ VERIFY (Quality Control)

### 8.1 Citation Verification
- Cross-check ≥10% of citations: does the cited paper support the claim?
- Self-citation ratio < 10%
- All DOIs resolve
- All abbreviations defined

### 8.2 Data Consistency
- Load `data-consistency-validator` for LOD values, nanoparticle sizes, kinetics constants
- 引用验证 ≠ 数据验证，两者是正交维度。详见 `references/dual-verification-framework.md`

### 8.3 Language
- Delete all "importantly", "notably", "it is worth noting"
- Every paragraph has a claim sentence
- Active voice throughout

### 8.4 Figures
- All figures use the SAME `scienceplots` style
- Font sizes consistent across all panels
- Color palette identical

### 8.5 Format Compliance
- Word count within journal limits
- Reference format matches target journal
- All required sections present
- AI disclosure included

---

## Appendix A ─ Domain-Specific Templates

### Template A: Nano-Bio Interface (Biosensing / POCT / DNA Nanotechnology)

For reviews at the intersection of nucleic acids, gold nanoparticles, and point-of-care diagnostics:

```
§1 Introduction → WHO ASSURED, why nucleic acid sensing, scope
§2 Signal Amplification
  → 2.1 Enzyme-free (DNAzyme, CHA, HCR)
  → 2.2 Enzyme-assisted (RPA, LAMP, CRISPR)
  → 2.3 Nanomaterial-enhanced (AuNP, QD, MOF)
  → 2.4 Comparative table
§3 Signal Transduction → Colorimetric, fluorescent, electrochemical, SERS, LF
§4 Microfluidic Integration → Centrifugal, paper-based (µPAD), digital, wearable
§5 Real-World Performance → Matrix effects, reproducibility, shelf life, regulatory
§6 Cross-Platform Comparison → DNAzyme vs CRISPR vs antibody vs aptamer
§7 Conclusions → Three real bottlenecks, hybrid systems, AI-assisted design
```

**Key Literature Anchors** (start here for citation traversal):
- Breaker & Joyce (1994) — first DNAzyme
- Santoro & Joyce (1997) — 10-23 and 8-17
- Lu, Willner, Liu, Fan, Li groups — foundational work

### Template B: Gold Nanomaterials — Fundamental Physical Chemistry

For reviews covering synthesis, growth mechanisms, and intrinsic optical/thermal/electrical/magnetic properties — NOT applications:

```
§1 Introduction
  → Why gold? The history from Faraday (1857) to nanoscale.
  → Scope: this review examines structure-property relationships
    at the level of the nanocrystal itself, not its applications.
  → The central tension: synthetic control has outpaced mechanistic
    understanding by at least a decade.

§2 Synthesis Methods (organized by growth logic, not chronology)
  2.1 Spherical particles: Turkevich-Frens, Brust-Schiffrin —
      thermodynamic vs. kinetic control
  2.2 Anisotropic growth: seed-mediated (Murphy/El-Sayed), AuNR,
      nanostars, nanoshells, nanocages — where does shape selectivity
      come from?
  2.3 High-index facets: overgrowth, templating, galvanic replacement
  2.4 Scalability and monodispersity: the engineering gap

§3 Growth Mechanisms
  3.1 Nucleation: classical vs. non-classical, two-step, cluster aggregation
  3.2 Capping agents: CTAB, citrate, PVP — what do they actually do
      at the growing facet? Not just "stabilize."
  3.3 Twin vs. single-crystal growth paths: what decides the outcome?
  3.4 In situ characterization breakthroughs: liquid-phase TEM,
      in situ XAS, SAXS — what they've revealed and what they can't see

§4 Optical Properties (Localized Surface Plasmon Resonance)
  4.1 Mie theory → Gans theory → numerical methods (DDA, FDTD):
      what each level of theory captures and misses
  4.2 Size, shape, dielectric environment — which parameter drives what
  4.3 Beyond dipolar LSPR: quadrupole modes, Fano resonances,
      plasmon coupling in dimers and assemblies
  4.4 The gap between ensemble measurements and single-particle
      optical properties

§5 Thermal and Electronic Properties
  5.1 Photothermal conversion: mechanism, measurement standards,
      the persistent debate over conversion efficiency numbers
  5.2 Hot electron dynamics: pump-probe studies, relaxation pathways
  5.3 Conductivity, catalysis at the surface — electrons that don't
      stay hot
  5.4 Magnetic properties of Au nanostructures (diamagnetic bulk →
      size-dependent effects)

§6 Structure-Property Mapping: Towards a Unified Picture
  6.1 What correlates (size ↔ SPR peak, aspect ratio ↔ LSPR tuning)
  6.2 What does NOT correlate (batch-to-batch optical reproducibility
      despite same TEM statistics)
  6.3 The missing layer: surface ligand structure at molecular resolution
  6.4 Is a "gold nanomaterial phase diagram" achievable?

§7 Conclusions and Outlook
  → Three real bottlenecks (not a wish list)
  → What in situ characterization must solve next
  → AI-guided synthesis prediction vs. first-principles growth models
```

**Key Literature Anchors** (fundamental AuNP):
- Faraday (1857) — first colloidal gold report (Phil Trans R Soc Lond)
- Turkevich (1951) — citrate reduction method (Discuss Faraday Soc)
- Brust & Schiffrin (1994) — two-phase synthesis, thiol stabilization (JCS Chem Comm)
- Mie (1908) — light scattering by spherical particles (Ann Phys)
- El-Sayed group — shape-dependent SPR of AuNRs (JPCB 1999, etc.)
- Murphy group — seed-mediated growth protocol (JPCB 2001, etc.)
- Liz-Marzán group — nanoshells, nanostars, colloidal chemistry
- Xia group — nanocages, galvanic replacement

---

## Appendix B ─ Required Python Packages

| Package | Purpose | Install |
|---------|---------|---------|
| `requests` | HTTP for all API calls | (included) |
| `biopython` | PubMed E-utilities wrapper | `pip install biopython` |
| `habanero` | CrossRef API wrapper | `pip install habanero` |
| `pyalex` | OpenAlex API wrapper | `pip install pyalex` |
| `matplotlib` | All plotting | `pip install matplotlib` |
| `seaborn` | Stats plots, themes | `pip install seaborn` |
| `scienceplots` | Journal-ready style sheets | `pip install SciencePlots` |
| `pandas` | Data management, tables | `pip install pandas` |

---

## Appendix C ─ Related Skills and References

### Related Skills

- `user-writing-style` — Output conventions (adapt to English)
- `precision-review-search` — Focused precision search pipeline for niche/broad topics (alternative to PISMA for Phases 2-4 when broad search returns too much noise)
- `data-consistency-validator` — Physical/chemical consistency check
- `thesis-computation` — Nucleic acid thermodynamics, nanoparticle synthesis
- `chinese-thesis-language-editor` — Language quality reference
- `research-verification` — Citation fact-checking

#### Project Organization Convention

Keep skill and project files strictly separate:

```
/opt/data/
  ├── skills/research/review-chem-bio-pipeline/   ← Methodology (reusable)
  └── reviews/<project-name>/                      ← Project files (one-time)
      ├── scripts/          ← Copied or adapted from skill
      ├── data/             ← Raw search results, final corpora
      ├── screening/        ← Included/maybe/excluded splits
      ├── sections/         ← Drafted section files
      └── cache/            ← API response cache
```

The skill directory stays clean as a reusable template. One project never contaminates another's data. See `scripts/search_papers.py`, `screen_papers.py`, and `compile_corpus.py` for the implementation template.

### Skill References

- `references/CHANGELOG.md` — Full edit history across 8 versions
- `references/design-rationale.md` — Design philosophy vs existing open-source tools
- `references/pisma-operational-notes.md` — PISMA installation, config, performance, and known issues from field testing
- `references/journal-targeting-guide.md` — Journal recommendations for POCT/nucleic acid/microfluidics/gold nanomaterial reviews, with impact factors, submission policies, and tiered recommendations
- `references/thesis-fast-track-workflow.md` — Fast-track pipeline (skip Phase 2-4) when writing a review from an existing thesis Chapter 1 with curated references
- `references/comprehensive-review-framework.md` — The "simplify-and-pay trade-off" framework template for 大综述 (comprehensive reviews targeting Chem Rev / Chem Soc Rev), with the six-dimensional comparison framework, section structure template, and scenario-decision-tree method
- `references/poct-nucleic-acid-data-anchors.md` — Concrete quantitative data points for POCT nucleic acid detection reviews: PCR inhibitor thresholds, amplification method performance ranges, commercial product LOD comparison, and market data
- `references/gold-style-writing.md` — "Gold style" writing conventions (dense academic prose, journal-abbreviated citations, 钉子开门 technique). Activate when the user asks to write reviews in the style of the gold nanomaterials review.

*Skill was rebuilt on 2026-06-03 after survey of open-source alternatives: K-Dense/scientific-agent-skills (141 skills), brycewang-stanford/Awesome-Journal-Skills (1600 skills), Master-cai/Research-Paper-Writing-Skills (Peng Sida methodology), InternScience/Awesome-Scientific-Skills.*
