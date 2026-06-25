--- frontmatter ---
---

## 陷阱（Pitfalls）

- 公共信息接口存在速率限制。大量历史查询可能返回截断窗口；请使用较晚的 `startTime` 值进行迭代。
- `fills --hours ...` 使用 `userFillsByTime`，该接口仅暴露最近一段滚动窗口，而非完整的历史归档。
- `historicalOrders` 仅返回最近的订单，并非完整导出。
- `review` 命令基于启发式规则。它无法仅从成交（fills）中重建意图、订单下达质量或真实滑点。
- `export` 命令输出标准化数据集，而非回测引擎。您仍需自行处理滑点/成交模型。
- 现货别名（如 `@107`）是有效的标识符，即使界面显示更友好的名称。
- `l2` 是时间点快照，而非时间序列。

---

--- body ---
## 验证（Verification）

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  markets --limit 5
```

应输出按24小时名义交易量排名靠前的 Hyperliquid 永续合约市场。