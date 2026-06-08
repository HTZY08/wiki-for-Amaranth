---
title: 基础配置
description: 配置 API Key、模型选择、基础参数
---

部署完成后，需要配置 AI 模型的 API Key 和基本参数。

---

## 配置文件位置

Hermes 的主配置文件位于容器内的 `/root/.hermes/config.yaml`，这个文件映射自宿主机的 `~/.hermes/config.yaml`。

```bash
# 在宿主机上编辑（推荐）
nano ~/.hermes/config.yaml

# 或在容器内编辑
docker exec -it hermes-agent vi /root/.hermes/config.yaml
```

> 如果文件不存在，可以复制示例配置：`cp config.example.yaml ~/.hermes/config.yaml`

## 配置 AI 模型

### 获取 API Key

1. 注册 AI 服务商账号（如 DeepSeek、OpenAI、Anthropic）
2. 进入控制台 → API Keys → 创建新 Key
3. 复制 Key 字符串（通常以 `sk-` 或类似前缀开头）

### 配置单个模型

最简单的配置——只用一个 AI 模型：

```yaml
providers:
  deepseek:
    api_key: "sk-your-api-key-here"
    models:
      - name: deepseek-chat
        type: chat
```

### 配置多个模型

不同任务用不同模型：

```yaml
providers:
  deepseek:
    api_key: "sk-your-deepseek-key"
    models:
      - name: deepseek-chat
        type: chat

  openai:
    api_key: "sk-your-openai-key"
    models:
      - name: gpt-4o
        type: chat

  anthropic:
    api_key: "sk-ant-your-claude-key"
    models:
      - name: claude-sonnet-4
        type: chat
```

### 使用环境变量（推荐）

把 API Key 写在配置文件里不安全（容易误提交到 Git）。推荐用环境变量：

```yaml
providers:
  deepseek:
    api_key: ${DEEPSEEK_API_KEY}
    models:
      - name: deepseek-chat
```

在 `.env` 文件中设置：

```bash
# ~/.hermes/.env
DEEPSEEK_API_KEY=sk-your-key-here
OPENAI_API_KEY=sk-your-key-here
```

## 配置基础参数

```yaml
# config.yaml 其他常用配置项
agent:
  name: "hermes"
  default_model: deepseek-chat
  max_tokens: 4096
  temperature: 0.7  # 0.0 = 精确，1.0 = 有创意

session:
  max_history: 50  # 保留最近 50 条对话

tools:
  enabled: true  # 启用工具调用（搜索、运行命令等）
```

## 验证配置

重启 Hermes 使配置生效：

```bash
docker compose restart hermes
```

然后进入 CLI 测试：

```bash
docker exec -it hermes-agent hermes
```

输入 `你好，能正常工作吗？`，如果正常回复说明配置正确。

## 常见问题

**问题：提示 "API key not configured"**
> 检查 `config.yaml` 中的 `api_key` 字段是否填写正确。
> 检查环境变量名是否拼写一致（`${变量名}` 要和 `.env` 中的一致）。

**问题：提示 "provider not found"**
> 检查 provider 名称是否拼写正确（DeepSeek/OpenAI/Anthropic 都是大小写敏感的）。
> 检查 `models` 下的 `name` 是否是该服务商支持的模型名。

**问题：所有请求都返回超时**
> 网络不通，检查[代理配置](/hermes/proxy-setup/)。
