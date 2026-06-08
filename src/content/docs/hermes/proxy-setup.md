---
title: 代理配置
description: mihomo (Clash Meta) 代理容器配置
---

Hermes Agent 需要稳定的国际网络出口以调用海外 AI API。使用 mihomo（Clash Meta 内核）作为 Docker 容器内的代理服务。

## 架构

```
Hermes 容器 → HTTP_PROXY → mihomo 容器:7890 → 宿主机 → 海外出口(US)
```

代理出口**锁定美国**，确保 AI API 调用不被地域限制阻断。

## 配置要点

### mihomo 容器

mihomo 以 sidecar 容器运行，通过 `depends_on` 确保 Hermes 容器在代理就绪后启动。

### 环境变量注入

Hermes 容器中设置：

```bash
http_proxy=http://mihomo:7890
https_proxy=http://mihomo:7890
```

Docker Compose 的 DNS 解析会通过容器名 `mihomo` 自动解析到代理容器 IP。

### 订阅与配置

代理节点通过订阅 URL 更新。配置目录映射到宿主机，持久化保存：

```yaml
volumes:
  - ./config/mihomo:/root/.config/mihomo
```

## 调试

```bash
# 检查代理连通性
docker exec hermes-agent curl -x http://mihomo:7890 -I https://api.openai.com

# 查看 mihomo 日志
docker compose logs mihomo

# 查看代理节点状态
curl http://localhost:9090/proxies
```
