---
title: Line
---

## 故障排除

**Webhook 验证时出现 "invalid signature"。** `Channel secret` 复制错误，或者你的隧道重写了请求体。首先用 `curl -i https://<tunnel>/line/webhook/health` 验证——应该返回 `{"status":"ok","platform":"line"}`。

**机器人在群组中收不到消息。** 检查 `LINE_ALLOWED_GROUPS` 是否包含了 `C...` 群组 ID。要找到群组 ID，发送一条测试消息并在 `~/.hermes/logs/gateway.log` 中 grep `LINE: rejecting unauthorized source` —— 被拒绝的来源字典中包含这些 ID。

**`send_image` 失败，提示 "LINE_PUBLIC_URL must be set"。** LINE 的 Messaging API 不接受二进制上传——图片、音频和视频必须通过可访问的 HTTPS URL 提供。将 `LINE_PUBLIC_URL` 设置为隧道的公共主机名，适配器将自动从 `/line/media/<token>/<filename>` 提供文件服务。

**回传按钮从未出现。** 要么是 LLM 的响应速度比 `LINE_SLOW_RESPONSE_THRESHOLD` 更快，要么是另一个气泡（工具进度、流式输出）先消耗了回复令牌。请参见“慢速 LLM 响应”下的抑制块。

**"已被其他配置文件使用"。** 相同的频道访问令牌已绑定到另一个正在运行的 Hermes 配置文件。停止另一个网关或使用单独的频道。

---

--- body ---
## 限制

* **气泡和长度上限。** 每个 LINE 文本气泡的上限为 5000 个字符。较长的响应会被智能分块为大约 4500 字符，每次回复/推送调用最多 5 个气泡，尽可能在自然边界处分割。
* **无原生消息编辑。** LINE 没有编辑消息的 API——流式响应总是发送新气泡，从不编辑之前的气泡。
* **不支持 Markdown 渲染。** 粗体（`**`）、斜体（`*`）、代码块和标题会以字面字符形式呈现。适配器会在发送前移除它们；URL 会被保留（`[label](url)` 变成 `label (url)`）。
* **加载指示器仅限私聊。** LINE 拒绝群组和聊天室的 chat/loading API，因此打字指示器仅在 1 对 1 聊天中显示。