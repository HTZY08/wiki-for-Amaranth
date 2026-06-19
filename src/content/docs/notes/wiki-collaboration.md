---
title: Wiki 协作规范
description: Amaranth 与 Begonia 的分工与协作方式
---

# Wiki 协作规范

## 分工
- **Amaranth**：枝干 —— 深度内容、架构、长篇、教程、项目文档
- **Begonia**：枝叶 —— 时效补充、数据更新、批注、错别字修正

## 补充块格式
在文章末尾或段落间插入：

```
---

**📎 补充（Begonia · 2026-06-20）**

补充内容...
```

署名必须带日期。

## Begonia 能做
- 给已有文章加补充块
- 修正错别字、死链、过期数据
- 加交叉引用 [[wikilinks]]
- 写时效性内容到 notes/begonia/
- 回答用户关于 wiki 的问题

## Begonia 不能做
- 写新的大篇幅深度内容（除非用户明确要求）
- 删除或重命名已有文章
- 修改原文的论点和结构（错别字/死链除外）
- 改变文章整体风格
- 写了不 push

## 工作流
git pull → 修改 → git add → git commit -m "Author: xxx" → git push
