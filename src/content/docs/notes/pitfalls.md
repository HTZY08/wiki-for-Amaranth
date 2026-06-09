---
title: 全系统踩坑指南
description: 从 Hermes 部署到日常使用中真实踩过的坑——记录在此，不再重蹈覆辙
---

从零搭这套系统到现在，每个组件都出过问题。记录在此，忘了就回来翻。

---

## 🤖 Hermes Agent

### Docker 部署顺序

**坑**：`docker compose up -d` 先启动所有容器，但 mihomo 没有配置文件。容器裸奔，API 调不通。

**解决**：先配好 mihomo 的 config.yaml 再启动。或者只启动不含 mihomo 的最小容器，配好代理再全量启动。

### 配置文件路径双标

**坑**：`basic-config.md` 让改 `~/.hermes/config.yaml`，`docker-deploy.md` 让改项目目录的 `config.yaml`——新手会以为这是两个不同文件，其实容器内映射到同一个。

**解决**：统一用 `~/.hermes/config.yaml` 描述，docker compose 映射关系单独说明。

### Secret 名大小写

**坑**：GitHub Actions 里 Secret 名是 `CLOUDFARE`（拼写不规范），文档里写的却是 `CLOUDFLARE_API_TOKEN`，导致 CI 一直报错。

**解决**：让 Secret 名和 workflow 文件里引用的名字保持一致。文档如实写但加注释说明非标准拼写。

### Codex 认证

**坑**：文档说"必须 ChatGPT Plus + OAuth"，实际上 API key 也能认证。文档不准确会劝退用户。

**解决**：明确写出"ChatGPT Plus 或 API key 两种方式"。

---

## 🌐 网络与代理

### 代理启动顺序

**坑**：mihomo 容器启动时如果订阅 URL 还没拉下来，容器跑起来了但没节点可用。Hermes 发请求走代理→代理无节点→超时报错。

**解决**：启动后检查 mihomo 日志确认代理节点已加载。`docker compose logs mihomo | tail -20`

### 订阅链接失效

**坑**：代理订阅链接有时效性，过期后所有海外 API 调不通。排查时容易先怀疑代码问题。

**解决**：订阅链接定期更新，失效时换新链接。验证：`curl -x http://mihomo:7890 -I https://api.openai.com`

### 订阅链接含敏感信息

**坑**：订阅 URL 里直接带 token 参数，截图或分享时容易泄露。

**解决**：任何包含订阅链接的内容不要上线、不要截图、不要分享。

---

## 🎮 ComfyUI

### --force-fp16 必须开

**坑**：SDXL 模型默认 FP32 推理，12GB 显存直接 OOM。必须加 `--force-fp16` 参数启动。

### 自定义节点版本冲突

**坑**：不同节点的依赖版本要求不同，pip 安装时互相覆盖。装完 A 节点，B 节点挂；修好 B，A 又挂。

**解决**：尽量少装节点，用最简依赖。记录节点版本号，升级前备份。

### WSL2 TDR 超时

**坑**：WSL2 上跑 GPU 密集计算超过一定时间，Windows 显卡驱动会触发 TDR（Timeout Detection and Recovery）保护，直接杀死 CUDA 进程。

**解决**：无完美方案。长训练任务拆短分批，或换云端 GPU。最终因此放弃了本地 ComfyUI 训练。

---

## 💾 Wiki / Starlight

### locale 配置

**坑**：Starlight 默认 en 语言，设 `zh-cn` 后侧边栏链接带 `/zh-cn/` 前缀，导致 404。

**解决**：中文单语言站必须用 `defaultLocale: 'root'`，`locales: { root: { label: '简体中文', lang: 'zh-cn' } }`。

### 侧边栏 autogenerate

**坑**：Starlight 的 autogenerate 侧边栏在某些版本会静默失效——不报错，只是不显示页面。

**解决**：不用 autogenerate，所有侧边栏显式写出。

### 敏感信息上线的风险

**规则**：所有推送到 GitHub 的内容必须经过敏感信息审查。具体硬件型号→通用描述，真实路径→示例路径，中转商不点名，个人身份信息不出现。

---

## 🎤 语音 / TTS

### edge-tts 容器内网络

**坑**：edge-tts 需要访问微软的 TTS 服务。容器内如果走 mihomo 代理，某些节点可能被微软边缘节点拒绝。

**解决**：TTS 请求不走代理（`no_proxy` 环境变量），或换用不限地域的 TTS 服务。

---

## 🔧 本地训练

GPU 训练踩坑有独立文档：[GPU 训练踩坑全记录](/notes/gpu-training-pitfalls/)

关键点摘要：

| 坑 | 现象 | 解决 |
|---|------|------|
| PyTorch 2.10+ `use_reentrant` bug | `prepare_model_for_kbit_training` 挂死 | 手动绕过，设置 `use_reentrant=False` |
| pip 安装 torch 超时 | 下载中断或编译挂死 | 用预编译 wheel 手动安装 |
| WSL2 CUDA driver error | 训练到一半进程被杀 | 拆短 batch，或放弃 WSL2 训练 |

---

## 📊 搜索 / API

### Tavily API 限额

**坑**：Tavily 免费 key 有月度限额，耗尽后搜索返回空结果，不是报错。很容易误判为网络问题。

**解决**：准备多个 key，轮换使用。监控用量，额度耗尽自动切换。

### Codex 审阅超时

**坑**：Codex CLI 跑 Wiki 全站审阅（31+ 页面）默认 600s 不够用，读到一半被截断。

**解决**：设置 `timeout=1200` 以上，后台运行并通知完成。

---

## 📄 OCR

### 长图切片策略

**坑**：超长图片直接 OCR 会截断文字或内存溢出。

**解决**：按 2000px 高度切块，200px 重叠防止断句。GPU 只加载一次模型，逐块处理。

---

> 这个清单会持续更新——每踩一个新坑就记一笔，避免同一条河淹两次。
