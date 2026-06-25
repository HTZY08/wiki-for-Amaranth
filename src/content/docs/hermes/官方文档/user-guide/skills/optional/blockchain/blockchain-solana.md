--- frontmatter ---
---

## 陷阱

- **CoinGecko 速率限制（rate-limits）** — 免费层约允许每分钟 10-30 次请求。
  价格查询每次代币消耗 1 个请求。持有多种代币的钱包可能无法获取所有代币的价格。可使用 `--no-prices` 提高速度。
- **公共 RPC 速率限制** — Solana 主网公共 RPC 会限制请求次数。
  生产环境下，请设置 `SOLANA_RPC_URL` 为私有端点（Helius、QuickNode、Triton）。
- **NFT 检测为启发式（heuristic）** — 需满足 `amount=1` 且 `decimals=0`。压缩 NFT（cNFTs）和 Token-2022 NFT 不会被检测到。
- **鲸鱼检测器仅扫描最新区块** — 不扫描历史区块。查询结果因查询时间而异。
- **交易历史** — 公共 RPC 保留约 2 天的数据。较早的交易可能无法获取。
- **代币名称** — 约 25 种知名代券有名称标签。其他代币显示为简化的铸币地址。使用 `token` 命令查看完整信息。
- **429 错误重试** — RPC 和 CoinGecko 调用均会在速率限制错误时最多重试 2 次，并使用指数退避（exponential backoff）策略。

---

--- body ---
## 验证

```bash
# 应输出当前 Solana slot、TPS 和 SOL 价格
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py stats
```