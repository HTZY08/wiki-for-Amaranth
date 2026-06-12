# 出图平台对比

2026 年可用的文生图平台对比，适用于科学综述/论文配图场景。

## 对比表

| 维度 | **MeiGen** (meigen.ai) | **APIYi** (api.apiyi.com) | **OpenAI 直连** |
|:-----|:-----------------------|:--------------------------|:----------------|
| **接入方式** | MCP Server（`mcp_meigen_generate_image`） | OpenAI SDK，改 base_url | OpenAI SDK |
| **GPT Image 2 价格** | 2K 标准 = 5 积分（积分:USD 不公开） | $0.03/张（gpt-image-2-all 统一价） | $0.006-$0.211（按尺寸/画质） |
| **其他模型** | Nanobanana/Seedream/Midjourney/Flux 等 | 主要是 OpenAI 系 | 仅 OpenAI |
| **国内支付** | ❌ 需境外卡 | ✅ 支付宝/微信 | ❌ 需境外卡 |
| **速度** | GPT Image 2 ~45s | ~30s（gpt-image-2-all） | ~120s（4K high） |
| **特性** | 社区图库、Figma 插件 | 充值活动最高 8 折 | 官方直连，最稳定 |

## 选择建议

- **有国内支付 + 要便宜** → APIYi `gpt-image-2-all`（$0.03/张，30s，支付宝）
- **已有 MeiGen 积分** → 继续用 `mcp_meigen_generate_image`
- **有 Codex/OpenAI 订阅** → 直接在 Codex CLI 里调 OpenAI SDK（包在订阅里，不算额外费用）
