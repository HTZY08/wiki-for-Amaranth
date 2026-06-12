# 学术写作双重验证框架

2026-06-08 从对比 Claude/Codex 学术插件（Imbad0202/academic-research-skills）和本系统的工作流中提炼。

## 核心洞察

学术 AI 工具的"防假/验真"机制存在两个完全不同的深度层级，不应混为一谈：

| 维度 | 第一层：引用验证 | 第二层：数据自洽性验证 |
|------|----------------|---------------------|
| **验证对象** | 参考文献是否存在、DOI 是否解析 | 论文中的数据本身是否物理/化学自洽 |
| **典型问题** | "这篇论文不存在/作者不对/年份错了" | "XRD 峰位对不上空间群/Raman 位移和键能矛盾/LOD 低于理论极限" |
| **检测方法** | 查 DOI → CrossRef/PubMed/Semantic Scholar 确认存在 | 物理公式 → 量纲分析 → 交叉数据关系核验 |
| **覆盖范围** | 所有论文（通用） | 材料/化学/生物表征数据（领域特异） |
| **实现成本** | 低：API 查询即可 | 高：需要嵌入领域公式和物理约束 |
| **代表工具** | Semantic Scholar + OpenAlex + Crossref 三重交叉验证 | `data-consistency-validator` skill |

## 设计选择

**不要用"引用验证"的强度来评价"数据验证"的质量，反之亦然。** 它们是正交维度：

- 一篇文章可能引用全真、DOI 全可解析，但数据内部矛盾
- 一篇文章也可能某条引用有瑕疵，但表征数据自洽

## 对本 skill (review-chem-bio-pipeline) 的意义

Phase 8 VERIFY 包含两个独立子阶段：

```
Phase 8 ─ VERIFY
  ├─ 8.1 引用层验证 (citation verification)
  │   [通用] 查 DOI 存在性、年份匹配、作者匹配
  │   工具: research-verification skill
  │
  └─ 8.2 数据层验证 (data consistency verification)
      [领域特异] 查 XRD 峰位 ⇄ 空间群、Raman ⇄ 键能、LOD ⇄ 灵敏度
      工具: data-consistency-validator skill
```

两者不可互相替代。只做引用验证不保证数据可信，只做数据验证不保证引用真实。

## 参考

- WeChat 文章: Claude/Codex 学术插件 (Imbad0202/academic-research-skills) — 代表了引用层验证的工程化高度（三重 API + 掠夺性期刊检测 + 可信度分级）
- `data-consistency-validator` skill — 本系统的数据层验证
- `research-verification` skill — 本系统的引用层验证
