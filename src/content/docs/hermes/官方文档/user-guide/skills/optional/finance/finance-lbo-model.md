---
title: Lbo Model
---

## 与用户协作——按章节的检查点

* **如果模板结构不清晰**，请先询问再继续
* **如果用户的需求与模板冲突**，确认其偏好
* **在完成每个主要部分后**，停止并与用户验证，再继续：
  - **完成资金来源与用途（Sources & Uses）后** → 展示平衡表格，确认填补项（plug）正确，在构建运营模型前获得签字确认
  - **完成运营模型/预测（Operating Model / Projections）后** → 展示预测损益表（P&L），确认增长率与利润率合理，在构建债务日程表（Debt Schedule）前获得签字确认
  - **完成债务日程表（Debt Schedule）后** → 展示期初/期末余额及利息，确认瀑布逻辑（waterfall logic），在计算回报前获得签字确认
  - **完成回报（IRR/MOIC）后** → 展示现金流序列及输出结果，确认符号和范围合理，在建立敏感性分析表前获得签字确认
  - **完成敏感性分析表（Sensitivity Tables）后** → 展示每个单元格的变化，确认基础案例（base case）落在预期位置
* **如果在验证过程中发现错误**，请先修复再进入下一部分
* **展示你的工作**——在有益时解释关键公式或假设
* **绝不要在未在每个部分确认的情况下呈现完整的模型**——在源头发现错误的单元格引用比从错误的IRR逆向追踪更快

--- body ---
**本技能通过使用正确的公式、适当的格式和经过验证的计算填充模板，生成投资银行级别的杠杆收购（LBO）模型。该技能适应任何模板结构，同时确保财务准确性和专业呈现标准。**

## 数据来源——优先使用MCP，网页作为后备

以下许多段落提到“使用标普肯肖MCP（S&P Kensho MCP）/ Daloopa MCP / FactSet MCP”。这些是源自原始Cowork插件环境的商业金融数据MCP。在Hermes中：

- **如果你配置了任何结构化金融数据MCP**（Hermes支持MCP——参见`native-mcp`技能），优先使用它获取时点可比公司（comps）、先例交易（precedent transactions）和备案文件（filings）。
- **否则**，退而使用：
  - `web_search` / `web_extract` 针对SEC EDGAR（`https://www.sec.gov/cgi-bin/browse-edgar`）获取美国备案文件
  - 公司投资者关系页面，获取新闻稿、财报演示文稿
  - `browser_navigate` 用于交互式数据门户
  - 用户提供的数据（若上下文中没有，明确询问）
- **绝不捏造**。如果倍数（multiple）、先例或备案编号无法获得，将单元格标记为`[UNSOURCED]`并告知用户。

## 归属（Attribution）

本技能改编自Anthropic的金融服务插件套件中的Claude（Apache-2.0许可证）。已移除Office-JS / Cowork实时Excel路径；本版本通过`excel-author`技能的约定，针对无头openpyxl。原始来源：https://github.com/anthropics/financial-services