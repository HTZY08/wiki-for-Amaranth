---
title: Evm
---

## 陷阱（Pitfalls）
- CoinGecko 免费版限制：约 10-30 次请求/分钟。可使用 `--no-prices` 加快钱包扫描。
- 公共 RPC 可能会限流。生产环境中请将 `EVM_RPC_URL` 设置为私有端点。
- `wallet` 和 `allowance` 仅检查已知的代币列表（每条链约 30 个代币）。如需完整的代币发现，请使用区块浏览器。
- `activity` 仅扫描最近的区块（最多 200 个）。如需完整历史记录，请使用 Etherscan API。
- `multichain` 运行 8 个并行线程——可能触发公共 RPC 的速率限制。
- ENS 解析依赖于单个公共端点（ensideas.com / ens.vitalik.ca），无备用端点。如果该端点不可用，`ens` 将失败——稍后重试或使用区块浏览器。
- 交易解码依赖于单个公共端点（4byte.directory），无备用端点。不在其数据库中的选择器会显示为 `unknown`。
- **L2 的 gas 估算仅包含 L2 执行部分。** 在 Base、Arbitrum、Optimism 和 zkSync 等 rollup 上，实际交易成本还包括 L1 数据提交费用，该费用取决于 calldata 大小和当前 L1 gas 价格。`gas` 命令不估算该 L1 部分。对于 Base，请参考该网络的 L1 费用预言机（合约 `0x420000000000000000000000000000000000000F`）。
- 地址 / 交易哈希输入会验证 0x 前缀 + 正确长度 + 十六进制，但 **不强制** EIP-55 校验和大小写（RPC 端点接受任意大小写的十六进制）。

---

--- body ---
## 验证（Verification）
```bash
# Should print current block, gas price, ETH price
python3 ~/.hermes/skills/blockchain/evm/scripts/evm_client.py stats

# Should resolve vitalik.eth to 0xd8dA...
python3 ~/.hermes/skills/blockchain/evm/scripts/evm_client.py ens vitalik.eth
```