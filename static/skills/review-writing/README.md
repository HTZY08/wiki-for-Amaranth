# 化学生物综述写作技能包

> 适用：化学/材料/生物领域综述（Critical Review / 大综述 / 技术百科型）
> 交付：纯 markdown 或 LaTeX 或 Word
> 工作流积累于 2026 年，经过 3 篇中文综述 + 1 篇英文 LaTeX 综述验证

---

## 技能总览

本包包含 4 个 Hermes Agent skill，覆盖综述写作全流程：

```
┌─────────────────────────────────────────────────────┐
│                    review-chem-bio-pipeline          │
│   Phase 1   Phase 2-4   Phase 5   Phase 6   Phase 7  │
│   ANALYZE → SEARCH → ORGANIZE → WRITE → FIGURES    │
│                      ↓                              │
│              precision-review-search                 │
│              (精搜索替代 PISMA 管道)                  │
└─────────────────────────────────────────────────────┘
         ↓                          ↓
  review-chem-bio-writing    paper-figure-mapper
  (写作规范 + 引用格式 +      (配图识别 + prompt 生成)
   去AI腔 + LaTeX翻译)
```

| Skill | 路径 | 文件数 | 功能 |
|-------|------|--------|------|
| `review-chem-bio-pipeline` | `review-chem-bio-pipeline/` | 18 | 全流程管道：定范围→搜索→去重→分类→写→图→核验 |
| `review-chem-bio-writing` | `review-chem-bio-writing/` | 14 | 核心写作规范：两种模式/三种架构/数据密度/引用格式/去AI腔/LaTeX翻译 |
| `precision-review-search` | `precision-review-search/` | 7 | 精搜索替代管线：当 PISMA 返回不足时，10-15 子主题直接搜 OpenAlex+PubMed |
| `paper-figure-mapper` | `paper-figure-mapper/` | 5 | 配图工作流：扫读章节→识别图位→产出 prompt→批量出图 |

---

## 快速开始

### 场景 A：写一篇 Critical Review（~50 篇引用，5-7 节）

```bash
1. review-chem-bio-pipeline Phase 1     → 定角 + 定范围 + 学术谱系
2. precision-review-search               → 10-15 子主题搜索 + 筛选
3. review-chem-bio-pipeline Phase 5-6   → 组织成节 + C-E-L-T 写作
4. review-chem-bio-writing               → 清洗 + 去AI腔 + 格式统一
5. paper-figure-mapper                   → 配图 prompt（选做）
```

### 场景 B：写一篇大综述（≥200 篇引用，8-12 节）

```bash
1. review-chem-bio-pipeline Phase 1     → 系统架构型/叙事型框架
2. precision-review-search               → 广泛搜索（600-1500 篇）
3. review-chem-bio-pipeline Phase 5-6   → 金风格写作（流动学术散文）
4. review-chem-bio-writing 金风格节     → 清洗 + 期刊缩写引用 + 无框架标签
5. paper-figure-mapper                   → 配图 prompt
```

### 场景 C：写技术百科型综述（可查阅，按条目分）

```bash
1. review-chem-bio-writing               → 直接看「技术百科型」节
2. 按功能链路分卷 + 每节三段式：科学史→近三年前沿→性能边界表
3. 每节标注真实发文密度
```

### 场景 D：中文综述 → 英文 LaTeX 翻译

```bash
1. review-chem-bio-writing               → 看 references/translation-to-latex-workflow.md
2. 多阶段流水线：DOI 提取 → CrossRef 元数据补充 → 分块翻译 → 组装
```

---

## 核心写作规范（review-chem-bio-writing）

### 两种写作模式

| 维度 | Critical Review | 金风格（大综述） |
|------|---------------|----------------|
| 目标期刊 | Biosens Bioelectron / TrAC / Anal Chem | Chem Rev / Chem Soc Rev / Nat Rev Bioeng |
| 参考文献 | ~50 篇精引 | ≥200 篇唯一 DOI |
| 段落结构 | C-E-L-T（显式标注 → 最后清洗掉） | 流动学术散文（无框架标签） |
| 引用格式 | (Author, Year, DOI:xxx) | (Author, Year, *Journal Abbrev*, DOI:xxx) |
| 交付格式 | 纯 markdown | 纯 markdown |

### 三种架构类型

| 类型 | 组织原则 | 适用场景 |
|------|---------|---------|
| 瓶颈驱动型 | 每章围绕一个瓶颈，多技术多路线回应 | 中篇焦点综述 |
| 系统架构型 | 按功能模块因果链组织 | 与论文体系平行的综述 |
| **技术百科型** | 按功能链路分卷 + 技术条目分节 + 三段式 | 可查阅的"工具书"型综述 |

### 数据密度规则（最重要）

- 每个论断必须跟一个具体数字
- 比较表填真实数字，不填"高/中/低"定性标签
- 给范围而非最优值
- 每节用"钉子开门"：用具体数据锚点开篇
- 密度标注：每个方向标注真实发文密度 + "真正有用的占比"

### 引用格式

内联格式：`(Author, Year, *Journal Abbrev*, DOI:10.xxxx/xxxxx)`

中文输出用"等人"：`(Tan等人, 2024, DOI:10.1002/jmv.29624)`

### 去AI腔工作流

写作完成后执行机械清洗：
1. 删除 C-E-L-T 行首标记
2. 删除 "需要指出的是""值得注意的是" 等 AI 填充词
3. 将 "这一结论表明" 类过渡句改为自然承接
4. 将孤立 C/L/T 字符清除
5. 删除框架标签

---

## 关键教训（2026-06-12 更新）

### LaTeX/Word 翻译流水线

不要单次 delegate_task 做全文翻译 —— 第一版 253KB 中文只产出了 83KB/91 条引用（原文 367 条丢了 75%）。

**正确做法（已验证，365KB/367引用/727处标注）：**

```
Step 1: 提取 DOI 映射 → Step 2: CrossRef API 补充元数据
Step 3: 按章节分块 → Step 4: 并行翻译（3 路并行）
Step 5: 组装 → Step 6: pandoc 转 docx → Step 7: python-docx 修上标引用
```

### 框架设计失败恢复

当用户连续说"不够"2 次以上：
1. 立即停止当前框架推进
2. 退回一级抽象判断层级错误
3. 一句话检验：框架能否用一句话说清？
4. 示出新框架再写，不猜

---

## 文件结构

```
review-writing-skill-pack/
├── README.md                     ← 本文件
├── review-chem-bio-pipeline/     ← 全流程管道（SKILL.md + 14 refs + 3 scripts）
├── review-chem-bio-writing/      ← 写作规范（SKILL.md + 10 refs + 2 templates + 1 script）
├── precision-review-search/      ← 精搜索（SKILL.md + 1 ref + 1 template + 4 scripts）
└── paper-figure-mapper/          ← 配图（SKILL.md + 4 refs）
```

---

## 依赖环境

- Hermes Agent（推荐）或其他 LLM Agent 框架
- Python 3.10+（运行搜索脚本需要 requests / biopython / habanero 等）
- LaTeX 环境（pandoc，用于 .tex → .docx 转换）
- 可选：OpenAlex API key、NCBI API key

---

## 版本历史

- 2026-06-12：新增 LaTeX/Word 翻译流水线参考文件 + 经验教训；完善 README
- 2026-06-09：三篇综述深刻教训后重构：技术百科型、密度标注、金风格、框架设计恢复流程
- 2026-06-03：首次打包，覆盖金纳米材料综述全流程
