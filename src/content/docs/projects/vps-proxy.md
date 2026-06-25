---
title: "用 VPS 代替机场：Tailscale + 自建代理"
description: "一台 $20.99/年的廉价 VPS，替代所有机场订阅"
---

## 动机

机场（付费代理订阅）的问题：
- 月付 ¥20-50，一年下来比 VPS 还贵
- 节点不稳定，随时跑路
- 隐私堪忧——所有流量过别人的服务器

**自建方案：** 一台廉价 VPS + xray + Tailscale，一次性投入不到 ¥150/年，所有设备共用。

## 架构

```
                    ┌──────────┐
                    │   VPS    │
                    │  xray    │
                    │  :8888   │
                    └────┬─────┘
                         │ Tailscale 内网
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     ┌────────┐    ┌────────┐    ┌────────┐
     │ 笔记本  │    │ 腾讯云  │    │ 腾讯云  │
     │ (WSL)  │    │ (北京)  │    │ (上海)  │
     └────────┘    └────────┘    └────────┘
```

**关键点：xray 只监听 Tailscale 内网 IP，不暴露公网。** 所有设备通过 Tailscale 加入同一个虚拟网络，通过内网 IP 访问代理，安全且不需要额外加密。

## 选型

| 需求 | 推荐 |
|------|------|
| 预算最低 | RackNerd $18/年（1C1G，线路普通） |
| 性价比 | **HostDare ASSD0 $20.99/年**（1C1G，Cogent 普线） |
| 中国直连 | HostDare CN2 GIA CSSD $35/年（三网直连，不依赖 Tailscale） |
| 配置 | Debian/Ubuntu 20.04+ |

> **注意：** 国内云服务器（腾讯云/阿里云）对 Trojan 等协议有 DPI 检测，代理流量会被掐断。必须用海外 VPS。

## 部署

### 1. 安装 Tailscale（所有设备）

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# → 打开浏览器认证，登录同一账号
```

每台设备认证后获得一个 `100.x.x.x` 的内网 IP，互相 ping 通即成功。

### 2. VPS 上安装 xray

```bash
# 一键安装
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

# 获取 VPS 的 Tailscale IP
TAILSCALE_IP=$(tailscale ip -4)

# 配置 xray（只监听 Tailscale 内网）
cat > /usr/local/etc/xray/config.json << EOF
{
  "inbounds": [
    {
      "port": 8888,
      "listen": "$TAILSCALE_IP",
      "protocol": "socks",
      "settings": {
        "udp": true
      }
    },
    {
      "port": 8888,
      "listen": "$TAILSCALE_IP",
      "protocol": "http",
      "settings": {}
    }
  ],
  "outbounds": [
    {"protocol": "freedom", "tag": "direct"}
  ]
}
EOF

systemctl restart xray
systemctl enable xray
```

### 3. 客户端配置

#### Linux / WSL

```bash
export http_proxy=http://100.x.x.x:8888
export https_proxy=http://100.x.x.x:8888
export no_proxy=localhost,127.0.0.1,.local,.cn,100.x.x.x
```

#### Docker 容器

```yaml
environment:
  - HTTP_PROXY=http://100.x.x.x:8888
  - HTTPS_PROXY=http://100.x.x.x:8888
  - NO_PROXY=localhost,127.0.0.1,.local,.cn,100.x.x.x
```

#### Windows

设置 → 网络 → 代理 → 手动设置 SOCKS5 `100.x.x.x:8888`

### 4. 国内 API 走直连

在 `.env` 中配置：

```bash
export NO_PROXY=localhost,127.0.0.1,.local,.sock,.cn,100.x.x.x,\
api.siliconflow.cn,api.deepseek.com,api.minimax.com
```

国内 API（DeepSeek、SiliconFlow 等）不走代理，避免绕路增加延迟。

## 对比

| | 机场 ¥30/月 | 自建 VPS ¥21/年 |
|:----|:----:|:----:|
| 年费 | ¥360 | ¥21（合租可更低） |
| 节点数 | 几十个 | 1 个（够用） |
| 速度 | 看运气 | 稳定（线路固定） |
| 隐私 | ❌ 流量过别人服务器 | ✅ 全在自己手里 |
| 维护 | 零 | 偶尔重启 |
| 可用性 | 随时跑路 | 跑不了（VPS 是你的） |

## 踩坑记录

**1. 腾讯云 DPI 阻断**
国内云服务器（腾讯云/阿里云）会对 Trojan 等协议做深度包检测，代理流量被掐断。**不要在境内 VPS 上搭代理。**

**2. 廉价 VPS 线路问题**
HostDare ASSD0（Cogent 普线）从中国直连速度一般，但通过 Tailscale 隧道中转后反而稳定——因为 Tailscale 走 UDP 打洞，不受 TCP 干扰。

**3. SOCKS5 vs HTTP**
xray 同时监听 SOCKS5 和 HTTP 两个端口，但有些程序只支持 HTTP 代理。统一用 `http://100.x.x.x:8888` 兼容性最好。

**4. Tailscale 被封**
Tailscale 官网（login.tailscale.com）在中国被墙。已登录的设备不受影响，但新设备认证需要已有设备协助或提前打开网页。

---

**📂 源代码：** [GitHub](https://github.com/HTZY08/wiki-for-Amaranth/blob/main/src/content/docs/projects/vps-proxy.md)
