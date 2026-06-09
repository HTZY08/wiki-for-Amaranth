---
title: 全系统踩坑指南
description: Hermes Agent 及相关组件部署与使用中的常见问题与解决方案
---

本文汇总了 Hermes Agent 部署与日常使用中可能遇到的典型问题，以及经过验证的解决方案。

---

## 🤖 Hermes Agent

### Docker 部署顺序

**问题**：`docker compose up -d` 一次性启动所有容器时，mihomo 代理容器尚未完成配置。代理无可用节点，导致 API 请求超时。

**解决方案**：先完成 mihomo 的 `config.yaml` 配置后再启动全部容器。或分步启动——只启动不含 mihomo 的最小容器，代理就绪后再全量启动。

### 配置文件路径歧义

**问题**：部分文档中 `basic-config.md` 指示修改 `~/.hermes/config.yaml`，而 `docker-deploy.md` 指示修改项目目录下的 `config.yaml`。新手容易误以为是两个不同文件，实际在容器内映射到同一路径。

**解决方案**：统一以 `~/.hermes/config.yaml` 作为配置文件的描述路径，docker compose 的卷映射关系单独说明。

### CI Secret 名不一致

**问题**：GitHub Actions workflow 中引用的 Secret 名为 `CLOUDFARE`（非标准拼写），但文档中写的是 `CLOUDFLARE_API_TOKEN`。拼写不一致导致 CI 持续报错。

**解决方案**：确保 workflow 文件中引用的 Secret 名与 GitHub 仓库中实际设置的名称完全一致。文档可如实记录但加注释说明。

### Codex 认证方式

**问题**：早期文档声明「必须 ChatGPT Plus + OAuth」，实际上 OpenAI Codex 官方仍接受 API key 认证。信息不准确可能误导用户。

**解决方案**：文档应明确列出「ChatGPT Plus 或 API key 两种认证方式」。

---

## 🌐 网络与代理

### 代理启动顺序

**问题**：mihomo 容器启动时若订阅 URL 尚未拉取完成，容器虽然运行但无可用节点。Hermes 发出的代理请求→代理无节点→超时报错。

**解决方案**：启动后检查 mihomo 日志确认节点已加载：`docker compose logs mihomo | tail -20`

### 订阅链接过期

**问题**：代理订阅链接具有时效性，过期后所有海外 API 调用失败。排查时容易先怀疑代码或网络配置问题。

**解决方案**：订阅链接定期更新。验证命令：`curl -x http://mihomo:7890 -I https://api.openai.com`

### 订阅链接中的敏感信息

**问题**：订阅 URL 中通常直接包含 token 参数，截图或分享时容易泄露凭据。

**解决方案**：任何包含订阅链接的内容不应上线、截图或对外分享。

---

## 🎮 ComfyUI

### `--force-fp16` 参数必须开启

**问题**：SDXL 模型默认以 FP32 精度推理，在 12GB 显存环境下会直接 OOM。必须添加 `--force-fp16` 参数启动。

### 自定义节点版本冲突

**问题**：不同 ComfyUI 自定义节点的依赖版本要求不同，pip 安装时可能互相覆盖。修复一个节点可能导致另一个节点失效。

**解决方案**：尽量保持节点最小集。记录节点版本号，升级前备份工作流。

### WSL2 TDR 超时

**问题**：WSL2 环境下长时间 GPU 密集计算会触发 Windows 显卡驱动的 TDR（Timeout Detection and Recovery）保护机制，直接终止 CUDA 进程。

**解决方案**：WSL2 下无完美绕开方案。长训练任务建议拆短分批或迁移至云端 GPU 环境。

---

## 💾 Wiki / Starlight

### locale 配置导致 404

**问题**：Starlight 将 `locale` 设为 `zh-cn` 后，侧边栏链接会附带 `/zh-cn/` 前缀，与路由不匹配导致 404。

**解决方案**：中文单语言站需使用 `defaultLocale: 'root'`，配合 `locales: { root: { label: '简体中文', lang: 'zh-cn' } }`。

### 侧边栏 autogenerate 失效

**问题**：Starlight 的自动生成侧边栏功能在特定版本中会静默失效——不报错，仅不显示页面。

**解决方案**：不使用 autogenerate，侧边栏全部显式写出。

### 敏感信息审查

**原则**：所有推送到公开仓库的内容须经过敏感信息审查。硬件型号使用通用描述，路径使用示例路径，服务商不具名，个人身份信息不出现。

---

## 🎤 语音 / TTS

### edge-tts 与代理的兼容性

**问题**：edge-tts 需要访问微软 TTS 服务。容器内若通过 mihomo 代理转发，部分节点可能被微软边缘节点拒绝连接。

**解决方案**：TTS 请求不走代理（配置 `no_proxy` 环境变量），或选用不限地域的 TTS 服务。

---

## 🔧 本地 GPU 训练

GPU 训练相关问题的详细记录请参考：[GPU 训练踩坑全记录](/notes/gpu-training-pitfalls/)

常见问题摘要：

| 问题 | 现象 | 解决方案 |
|:----|:----|:---------|
| PyTorch 2.10+ `use_reentrant` bug | `prepare_model_for_kbit_training` 挂死 | 手动设置 `use_reentrant=False` 绕过 |
| pip 安装 torch 超时 | 下载中断或编译挂死 | 使用预编译 wheel 手动安装 |
| WSL2 CUDA driver error | 训练进程中段被杀 | 缩短 batch size 或切换至云端 GPU |

---

## 📊 搜索 / API

### Tavily API 限额耗尽

**问题**：Tavily 免费 API key 有月度额度限制。额度耗尽后搜索接口返回空结果而非错误提示，容易被误判为网络问题。

**解决方案**：准备多个 key 轮换使用。监控消耗量，额度耗尽自动切换。

### Codex 审阅超时

**问题**：Codex CLI 执行 Wiki 全站内容审阅时，默认 600s 超时不足以完成全部页面的分析，结果被截断。

**解决方案**：设置 `timeout=1200` 以上，后台运行并通知完成。

---

## 📄 OCR

### 超长图片处理

**问题**：超长图片直接送入 OCR 引擎会导致文字截断或内存溢出。

**解决方案**：按 2000px 高度切片，200px 重叠防止断句。GPU 模型仅加载一次，逐块处理。

---

> 本文档持续更新——每发现一个典型问题就记录一笔。
