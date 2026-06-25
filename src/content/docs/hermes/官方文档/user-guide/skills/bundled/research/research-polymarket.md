---
title: Polymarket
---

--- body ---
{/* 此页面由技能目录中的 SKILL.md 经由 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Polymarket

查询 Polymarket：市场、价格、订单簿、历史。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/research/polymarket` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent + Teknium |
| 平台 | linux, macos, windows |

## 参考：完整 SKILL.md

:::info
以下为 Hermes 在此技能被触发时加载的完整技能定义。这是技能激活后代理（Agent）所看到的指令。
:::

# Polymarket — 预测市场数据（Prediction Market Data）

通过 Polymarket 的公开 REST API 查询其预测市场数据。
所有接口均为只读，无需任何认证。

参见 `references/api-endpoints.md`，了解包含 curl 示例的完整接口参考。

## 何时使用

- 用户询问关于预测市场、投注赔率或事件概率的问题
- 用户想知道“某事件发生的概率是多少？”
- 用户专门询问 Polymarket
- 用户需要市场价格、订单簿数据或价格历史
- 用户要求监控或跟踪预测市场的动态

## 关键概念

- **事件（Events）** 包含一个或多个 **市场（Markets）**（一对多关系）
- **市场（Markets）** 是二元结果，Yes/No 的价格在 0.00 到 1.00 之间
- 价格即概率：价格 0.65 意味着市场认为可能性为 65%
- `outcomePrices` 字段：JSON 编码的数组，例如 `["0.80", "0.20"]`
- `clobTokenIds` 字段：JSON 编码的两个代币 ID 数组 [Yes, No]，用于价格/订单簿查询
- `conditionId` 字段：十六进制字符串，用于价格历史查询
- 交易量以 USDC（美元）计

## 三个公开 API（Three Public APIs）

1. **Gamma API**：`gamma-api.polymarket.com` — 发现、搜索、浏览
2. **CLOB API**：`clob.polymarket.com` — 实时价格、订单簿、历史
3. **数据 API（Data API）**：`data-api.polymarket.com` — 交易、未平仓合约

## 典型工作流程

当用户询问预测市场赔率时：

1. **搜索** — 使用 Gamma API 的 public-search 端点，根据用户查询进行搜索
2. **解析** — 解析响应，提取事件及其嵌套的市场
3. **展示结果** — 显示市场问题、当前价格（以百分比形式）及交易量
4. **深入分析** — 如果用户要求，使用 clobTokenIds 获取订单簿，使用 conditionId 获取历史数据

## 展示结果

将价格格式化为百分比以提升可读性：
- `outcomePrices` 为 `["0.652", "0.348"]` 时，显示为“Yes: 65.2%, No: 34.8%”
- 始终展示市场问题和概率
- 如有交易量数据，一并展示

示例：`"某事件会发生吗？" — 65.2% Yes（交易量 $1.2M）`

## 解析双重编码字段（Double-Encoded Fields）

Gamma API 返回的 `outcomePrices`、`outcomes` 和 `clobTokenIds` 是 JSON 响应中的 JSON 字符串（双重编码）。使用 Python 处理时，请通过 `json.loads(market['outcomePrices'])` 解析以获得实际的数组。

## 速率限制（Rate Limits）

限制较为宽松，正常使用通常不会触及：
- Gamma：每 10 秒 4,000 次请求（整体）
- CLOB：每 10 秒 9,000 次请求（整体）
- Data：每 10 秒 1,000 次请求（整体）

## 限制（Limitations）

- 本技能为只读 — 不支持下单交易
- 交易需要基于钱包的加密认证（EIP-712 签名）
- 部分新市场可能没有价格历史数据
- 交易存在地理限制，但只读数据全球可访问