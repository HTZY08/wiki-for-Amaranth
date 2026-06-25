---
title: "Stocks — 股票报价、历史、搜索、比较、加密货币（通过 Yahoo）"
sidebar_label: "Stocks"
description: "通过 Yahoo 获取股票报价、历史、搜索、比较、加密货币数据"
---

{/* 此页面由 skill 的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Stocks（股票）

通过 Yahoo 获取股票报价、历史、搜索、比较、加密货币数据。

## 技能元数据

| 属性 | 值 |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/finance/stocks` 安装 |
| 路径 | `optional-skills/finance/stocks` |
| 版本 | `0.1.0` |
| 作者 | Mibay（Mibayy），Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Stocks`（股票）、`Finance`（金融）、`Market`（市场）、`Crypto`（加密货币）、`Investing`（投资） |
| 相关技能 | [`dcf-model`](/docs/user-guide/skills/optional/finance/finance-dcf-model)、[`comps-analysis`](/docs/user-guide/skills/optional/finance/finance-comps-analysis)、[`lbo-model`](/docs/user-guide/skills/optional/finance/finance-lbo-model) |

## 参考：完整版 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时代理所看到的指令。
:::

# Stocks Skill（股票技能）

通过 Yahoo Finance 获取的只读市场数据。包含五个命令：`quote`（报价）、`search`（搜索）、`history`（历史）、`compare`（比较）、`crypto`（加密货币）。仅使用 Python 标准库 — 无需 API 密钥，无需 pip 安装。Yahoo 的接口是非官方的，可能会限制速率或发生变更。

## 使用时机

- 用户询问当前股价（AAPL、TSLA、MSFT 等）
- 用户想通过公司名称查找股票代码（ticker）
- 用户想要获取特定日期范围内的 OHLCV 历史数据或表现
- 用户想要并排比较多个股票代码
- 用户询问加密货币价格（BTC、ETH、SOL 等）

## 前置条件

仅需 Python 3.8+ 标准库。可选：设置 `ALPHA_VANTAGE_KEY`，以在 Yahoo 的 crumb 保护字段返回空值时补充 `market_cap`（市值）、`pe_ratio`（市盈率）和 52 周高低点数据。免费密钥获取地址：https://www.alphavantage.co/support/#api-key

## 运行方式

通过 `terminal` 工具调用。安装后：

```
SCRIPT=~/.hermes/skills/finance/stocks/scripts/stocks_client.py
python3 $SCRIPT quote AAPL
```

所有输出均为 stdout 上的 JSON 格式 — 如需切片处理，可管道传递给 `jq`。

## 快速参考

```
python3 $SCRIPT quote AAPL
python3 $SCRIPT quote AAPL MSFT GOOGL TSLA
python3 $SCRIPT search "Tesla"
python3 $SCRIPT history NVDA --range 6mo
python3 $SCRIPT compare AAPL MSFT GOOGL
python3 $SCRIPT crypto BTC ETH SOL
```

## 命令

### `quote SYMBOL [SYMBOL2 ...]`

当前价格、涨跌幅、涨跌幅百分比、成交量、52 周最高/最低价。

### `search QUERY`

通过公司名称查找股票代码。返回前 5 个结果：股票代码（symbol）、名称、交易所、类型（type）。

### `history SYMBOL [--range RANGE]`

每日 OHLCV 数据及统计数据（最低值、最高值、平均值、总收益率 %）。可选范围：`1mo`、`3mo`、`6mo`、`1y`、`5y`。默认值：`1mo`。

### `compare SYMBOL1 SYMBOL2 [...]`

并排比较：价格、涨跌幅百分比、52 周表现。

### `crypto SYMBOL [SYMBOL2 ...]`

加密货币价格。传入 `BTC`（脚本会自动附加 `-USD`）。

## 注意事项

- Yahoo Finance 的 API 是非官方的。接口可能在没有通知的情况下变更或限制速率 — 如果请求开始失败，这便是原因。
- 当 Yahoo 的 crumb 会话未建立时，`quote` 命令中的 `market_cap`（市值）和 `pe_ratio`（市盈率）可能返回空值。可设置 `ALPHA_VANTAGE_KEY` 进行回填。
- 在批量请求之间添加短暂延迟，以避免触发速率限制。
- 本技能为只读 — 不支持下单或账户集成。

## 验证

```
python3 ~/.hermes/skills/finance/stocks/scripts/stocks_client.py quote AAPL
```

返回一个包含 `symbol: "AAPL"` 和数字类型 `price` 字段的 JSON 对象。