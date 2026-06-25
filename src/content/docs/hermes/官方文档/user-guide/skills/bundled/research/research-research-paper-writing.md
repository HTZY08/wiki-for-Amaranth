---
title: Research Paper Writing
---

## 常见问题及解决方案

| 问题 | 解决方案 |
|------|----------|
| 摘要过于泛化 | 删除第一句（如果它可以加在任何机器学习论文前面）。直接从你的具体贡献开始。 |
| 引言超过1.5页 | 将背景部分拆分为相关工作。将贡献点列表提前。 |
| 实验缺乏明确断言 | 在每个实验前添加：“本实验旨在检验[具体断言]……”。 |
| 审稿人认为论文难以理解 | 增加路径指示标识（signposting），使用一致的术语，使图注自包含。 |
| 缺少统计显著性 | 添加误差条、运行次数、统计检验、置信区间。 |
| 实验范围蔓延 | 每个实验必须对应一个具体断言。删除不对应的实验。 |
| 论文被拒，需要重新提交 | 参见阶段7中的会议重新提交。回应审稿人关切，但不引用审稿意见。 |
| 缺少更广泛影响声明 | 参见步骤5.10。大多数会议要求该声明。声称“无负面影响”几乎不可信。 |
| 人工评估被批评为薄弱 | 参见步骤2.5和[references/human-evaluation.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/human-evaluation.md)。报告一致性指标、标注者详情、报酬。 |
| 审稿人质疑可复现性 | 发布代码（步骤7.9），记录所有超参数，包含随机种子和计算细节。 |
| 理论论文缺乏直觉 | 在正式证明前添加带有平实语言解释的证明草图。参见[references/paper-types.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/paper-types.md)。 |
| 结果为阴性/无效 | 参见阶段4.3关于处理阴性结果的内容。考虑研讨会、TMLR，或将其重新框架为分析性工作。 |

---

## 参考文献

| 文档 | 内容 |
|------|------|
| [references/writing-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/writing-guide.md) | Gopen & Swan 7项原则、Perez微技巧、Lipton用词选择、Steinhardt精确性、图形设计 |
| [references/citation-workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/citation-workflow.md) | 引用API、Python代码、CitationManager类、BibTeX管理 |
| [references/checklists.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/checklists.md) | NeurIPS 16项、ICML、ICLR、ACL要求、通用投稿前检查清单 |
| [references/reviewer-guidelines.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/reviewer-guidelines.md) | 评估标准、评分、常见关切、回复模板 |
| [references/sources.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/sources.md) | 所有写作指南、会议指南、API的完整参考文献 |
| [references/experiment-patterns.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/experiment-patterns.md) | 实验设计模式、评估协议、监控、错误恢复 |
| [references/autoreason-methodology.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/autoreason-methodology.md) | Autoreason循环、策略选择、模型指南、提示、范围约束、Borda评分 |
| [references/human-evaluation.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/human-evaluation.md) | 人工评估设计、标注指南、一致性指标、众包质量控制、IRB指导 |
| [references/paper-types.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/paper-types.md) | 理论论文（证明写作、定理结构）、综述论文、基准论文、立场论文 |

### LaTeX 模板

`templates/` 中的模板适用于：**NeurIPS 2025**、**ICML 2026**、**ICLR 2026**、**ACL**、**AAAI 2026**、**COLM 2025**。

编译说明请参见 [templates/README.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/templates/README.md)。

### 关键外部资源

**写作理念：**
- [Neel Nanda: 如何撰写机器学习论文](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers)
- [Sebastian Farquhar: 如何撰写机器学习论文](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/)
- [Gopen & Swan: 科学写作的科学](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf)
- [Lipton: 科学写作启发式法则](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/)
- [Perez: 轻松论文写作技巧](https://ethanperez.net/easy-paper-writing-tips/)

**API：** [Semantic Scholar](https://api.semanticscholar.org/api-docs/) | [CrossRef](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | [arXiv](https://info.arxiv.org/help/api/basics.html)

**会议：** [NeurIPS](https://neurips.cc/Conferences/2025/PaperInformation/StyleFiles) | [ICML](https://icml.cc/Conferences/2025/AuthorInstructions) | [ICLR](https://iclr.cc/Conferences/2026/AuthorGuide) | [ACL](https://github.com/acl-org/acl-style-files)