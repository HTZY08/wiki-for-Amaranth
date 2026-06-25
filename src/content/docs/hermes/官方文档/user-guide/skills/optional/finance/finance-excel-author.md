---
title: Excel Author
---

title: "Excel 建模师"
sidebar_label: "Excel 建模师"
description: "使用 openpyxl 以无头模式构建可审计的 Excel 工作簿——遵循蓝/黑/绿单元格约定、公式优先于硬编码、命名区域、平衡检查、敏感性分析表。适用于金融模型、审计输出、对账。"
---

--- body ---
{/* 此页面由技能文件 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Excel 建模师（Excel Author）

使用 openpyxl 以无头模式构建可审计的 Excel 工作簿——遵循蓝/黑/绿单元格约定、公式优先于硬编码、命名区域、平衡检查、敏感性分析表。适用于金融模型、审计输出、对账。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源 | 可选——通过 `hermes skills install official/finance/excel-author` 安装 |
| 路径 | `optional-skills/finance/excel-author` |
| 版本 | `1.0.0` |
| 作者 | Anthropic（由 Nous Research 改编） |
| 许可证 | Apache-2.0 |
| 平台 | linux, macos, windows |
| 标签 | `excel`, `openpyxl`, `finance`, `spreadsheet`, `modeling` |
| 相关技能 | [`pptx-author`](/docs/user-guide/skills/optional/finance/finance-pptx-author), [`dcf-model`](/docs/user-guide/skills/optional/finance/finance-dcf-model), [`comps-analysis`](/docs/user-guide/skills/optional/finance/finance-comps-analysis), [`lbo-model`](/docs/user-guide/skills/optional/finance/finance-lbo-model), [`3-statement-model`](/docs/user-guide/skills/optional/finance/finance-3-statement-model) |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是代理（Agent）在技能激活时看到的指令。
:::

# excel-author

使用 `openpyxl` 在磁盘上生成一个 .xlsx 文件。请遵循以下银行级约定，以确保模型可审计、灵活且可由非构建者审查。

改编自 Anthropic 在 [anthropics/financial-services](https://github.com/anthropics/financial-services) 仓库中的 `xlsx-author` 和 `audit-xls` 技能。原技能中 MCP / Office-JS / Cowork 相关的分支已被移除——本技能假定为无头 Python 环境。

## 输出约定（Output contract）

- 写入 `./out/<名称>.xlsx`。如果 `./out/` 不存在则创建。
- 在最终消息中返回相对路径，以便下游工具拾取。
- 每个文件一个逻辑模型。除非明确要求，否则不要追加到现有工作簿。

## 设置（Setup）

```bash
pip install "openpyxl>=3.0"
```

## 核心约定（不可协商）

### 蓝/黑/绿单元格颜色
- **蓝色**（`Font(color="0000FF")`）——人类输入的硬编码值。收入驱动因素、WACC 输入、终值增长率、市场数据。
- **黑色**（默认）——公式。每个派生单元格都是实时 Excel 公式。
- **绿色**（`Font(color="006100")`）——指向其他工作表或外部文件的链接。

审查者可以扫描工作表，立即看出哪些是假设，哪些是计算结果。

### 公式优先于硬编码
每个计算单元格必须是公式字符串，绝不能是在 Python 中计算后粘贴为数值的数字。

```python
# 错误——潜藏的 bug
ws["D20"] = revenue_prior_year * (1 + growth)

# 正确——当用户更改假设时自动调整
ws["D20"] = "=D19*(1+$B$8)"
```

允许的硬编码数值只有：
1. 原始历史输入（实际收入、报告的 EBITDA 等）
2. 用户应调整的假设驱动因素（增长率、WACC 输入、终值增长率 g）
3. 当前市场数据（股价、债务余额）——需附带单元格注释，注明来源和日期

如果你发现自己用 Python 计算了一个值并写入结果，请停止。

### 跨工作表引用的命名区域
对引用自其他工作表、演示文稿或备忘录的任何数值，使用命名区域。

```python
from openpyxl.workbook.defined_name import DefinedName
wb.defined_names["WACC"] = DefinedName("WACC", attr_text="Inputs!$C$8")
# 然后在其他地方：
calc["D30"] = "=D29/WACC"
```

### 平衡检查标签页（Balance checks tab）
包含一个 `Checks` 工作表，用于核对所有内容并显示 TRUE/FALSE：
- 资产负债表平衡（资产 = 负债 + 权益）
- 现金流量与资产负债表的期间现金变动相符
- 分部加总与合并总数相符
- 计算区域内无意外硬编码

示例：
```python
checks = wb.create_sheet("Checks")
checks["A2"] = "BS 平衡"
checks["B2"] = "=IS!D20-IS!D21-IS!D22"
checks["C2"] = "=ABS(B2)<0.01"  # TRUE/FALSE
```

### 每个硬编码输入的单元格注释
在创建单元格时立即添加注释，而非事后。

```python
from openpyxl.comments import Comment
ws["C2"] = 1_250_000_000
ws["C2"].font = Font(color="0000FF")
ws["C2"].comment = Comment("来源：10-K FY2024, p.47，收入行", "分析师")
```

格式：`来源：[系统/文档]，[日期]，[引用]，[URL 如适用]`。

切勿推迟标注来源。切勿写 `TODO: 添加来源`。

## 骨架：典型金融模型

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter
from pathlib import Path

BLUE = Font(color="0000FF")
BLACK = Font(color="000000")
GREEN = Font(color="006100")
BOLD = Font(bold=True)
HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(color="FFFFFF", bold=True)

wb = Workbook()

# --- 输入标签页 ---
inp = wb.active
inp.title = "输入"
inp["A1"] = "市场数据与关键输入"
inp["A1"].font = HEADER_FONT
inp["A1"].fill = HEADER_FILL
inp.merge_cells("A1:C1")

inp["B3"] = "营收 FY2024"
inp["C3"] = 1_250_000_000
inp["C3"].font = BLUE
inp["C3"].comment = Comment("来源：10-K FY2024 p.47", "模型")

inp["B4"] = "增长率"
inp["C4"] = 0.12
inp["C4"].font = BLUE

# --- 计算标签页 ---
calc = wb.create_sheet("DCF")
calc["B2"] = "预计营收"
calc["C2"] = "=Inputs!C3*(1+Inputs!C4)"   # 公式，黑色

# --- 检查标签页 ---
chk = wb.create_sheet("检查")
chk["A2"] = "BS 平衡"
chk["B2"] = "=ABS(BS!D20-BS!D21-BS!D22)<0.01"

Path("./out").mkdir(exist_ok=True)
wb.save("./out/model.xlsx")
```

## 使用合并单元格的段落标题

openpyxl 注意事项：合并时，在左上角单元格设置值，并单独对整个范围设置样式。

```python
ws["A7"] = "现金流量预测"
ws["A7"].font = HEADER_FONT
ws.merge_cells("A7:H7")
for col in range(1, 9):  # A..H
    ws.cell(row=7, column=col).fill = HEADER_FILL
```

## 敏感性分析表（Sensitivity tables）

使用循环构建，而非逐单元格硬编码公式。规则：

- **行/列数为奇数**（5×5 或 7×7）——确保存在真正的中心单元格。
- **中心单元格 = 基准情形。** 中间行/列标题必须等于模型实际的 WACC 和终值增长率，以使中心输出等于基准情形下的隐含股价。这是合理性检查。
- **使用中蓝色填充（`"BDD7EE"`）和粗体突出显示中心单元格。**
- 每个单元格都填入完整重新计算公式——绝不使用近似值。

```python
# 5x5 WACC（行）x 终值增长率（列）敏感性
wacc_axis = [0.08, 0.085, 0.09, 0.095, 0.10]        # 中心行 = 基准 9.0%
term_axis = [0.02, 0.025, 0.03, 0.035, 0.04]        # 中心列 = 基准 3.0%

start_row = 40
ws.cell(row=start_row, column=1).value = "隐含股价 ($)"
ws.cell(row=start_row, column=1).font = BOLD

for j, g in enumerate(term_axis):
    ws.cell(row=start_row+1, column=2+j).value = g
    ws.cell(row=start_row+1, column=2+j).font = BLUE

for i, w in enumerate(wacc_axis):
    r = start_row + 2 + i
    ws.cell(row=r, column=1).value = w
    ws.cell(row=r, column=1).font = BLUE
    for j, g in enumerate(term_axis):
        c = 2 + j
        # 完整的 DCF 重新计算公式（为简化起见仅作示例）。
        # 在真实模型中，此公式引用完整的预测模块。
        ws.cell(row=r, column=c).value = (
            f"=SUMPRODUCT(FCF_range,1/(1+{w})^year_offset) + "
            f"FCF_terminal*(1+{g})/({w}-{g})/(1+{w})^terminal_year"
        )

# 突出显示中心单元格（基准情形）
center = ws.cell(row=start_row+2+len(wacc_axis)//2,
                 column=2+len(term_axis)//2)
center.fill = PatternFill("solid", fgColor="BDD7EE")
center.font = BOLD
```

## 交付前重新计算

openpyxl 写入公式字符串但不计算它们。Excel 会在打开时重新计算，但下游用户（自动检查脚本、CI）需要计算后的数值。

在交付前运行 LibreOffice 或专用重新计算步骤：

```bash
# LibreOffice 无头重新计算
libreoffice --headless --calc --convert-to xlsx ./out/model.xlsx --outdir ./out/
```

或使用 Python 重新计算辅助工具（参见此技能中的 `scripts/recalc.py`）。

## 模型布局规划

在编写任何公式之前：
1. 定义所有段落的行位置
2. 编写所有标题和标签
3. 编写所有段落分隔线和空白行
4. 然后使用锁定的行位置编写公式

这可以防止级联公式断裂模式——即在公式编写完成后插入标题行会导致所有下游引用偏移。

## 与用户逐步验证

对于大型模型（DCF、三表、LBO），在继续之前停下来向用户展示中间产物。在你构建下游敏感性分析表之前捕获一个错误的利润率假设，可以节省一小时。

检查点模式：
- 在输入模块之后 → 显示原始输入，确认后再进行预测
- 在营收预测之后 → 确认顶行和增长率
- 在自由现金流构建之后 → 确认完整日程表
- 在 WACC 之后 → 确认输入
- 在估值之后 → 确认权益桥接
- 然后构建敏感性分析表

## 何时不应使用此技能

- 当用户正在使用 Office MCP 进行实时 Excel 会话时——应直接操作其工作簿。
- 纯表格数据导出且不含公式时——`csv` 或 `pandas.to_excel` 更简单。
- 具有高度交互性的仪表板/图表——应使用真正的 BI 工具。

## 归属

约定（蓝/黑/绿、公式优先于硬编码、命名区域、敏感性规则）改编自 Anthropic 的 Claude for Financial Services 插件套件，基于 Apache-2.0 许可证。原始来源：https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/financial-analysis/skills/xlsx-author