---
title: Local Llm On Mac
---

## 连接 Hermes（Hermes）

当你的本地服务器运行后：

```bash
hermes model
```

选择 **自定义端点（Custom endpoint）** 并按提示操作。它会要求你输入基础 URL 和模型名称——使用你在上方设置的后端对应的值。

---

--- body ---
--- body ---
## 超时（Timeouts）

Hermes 会自动检测本地端点（localhost、LAN IP）并放宽其流式超时时间。大多数场景下无需配置。

如果你仍然遇到超时错误（例如在缓慢的硬件上处理非常大的上下文），你可以覆盖流式读取超时时间：

```bash
# 在你的 .env 文件中——从默认的 120 秒提升到 30 分钟
HERMES_STREAM_READ_TIMEOUT=1800
```

| 超时类型 | 默认值 | 本地自动调整 | 环境变量覆盖 |
|---------|---------|----------------------|------------------|
| 流式读取（套接字层） | 120s | 提升至 1800s | `HERMES_STREAM_READ_TIMEOUT` |
| 停滞流检测 | 180s | 完全禁用 | `HERMES_STREAM_STALE_TIMEOUT` |
| API 调用（非流式） | 1800s | 无需更改 | `HERMES_API_TIMEOUT` |

流式读取超时是最可能导致问题的——它是接收下一个数据块的套接字层截止时间。在大型上下文的预填充（prefill）过程中，本地模型在处理提示时可能数分钟没有输出。自动检测会透明地处理这一情况。