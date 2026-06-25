--- frontmatter ---
---
{/* 此页面由网站脚本 scripts/generate-skill-docs.py 基于技能目录中的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 域名情报（Domain Intel）

使用 Python 标准库进行被动式域名侦察。支持子域名发现、SSL 证书检查、WHOIS 查询、DNS 记录、域名可用性检查以及批量多域名分析。无需 API 密钥。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/research/domain-intel` 安装 |
| 路径 | `optional-skills/research/domain-intel` |
| 平台 | linux, macos, windows |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在该技能被触发时加载的完整技能定义。即技能激活时智能体所看到的指令。
:::

# 域名情报 — 被动式 OSINT

仅使用 Python 标准库进行被动式域名侦察。
**零依赖。零 API 密钥。适用于 Linux、macOS 和 Windows。**

## 辅助脚本

本技能包含 `scripts/domain_intel.py` —— 一个用于所有域名情报操作的完整 CLI 工具。

```bash
# 通过证书透明度日志进行子域名发现
python3 SKILL_DIR/scripts/domain_intel.py subdomains example.com

# SSL 证书检查（过期时间、加密套件、SANs、颁发者）
python3 SKILL_DIR/scripts/domain_intel.py ssl example.com

# WHOIS 查询（注册商、日期、名称服务器 — 100+ 顶级域）
python3 SKILL_DIR/scripts/domain_intel.py whois example.com

# DNS 记录（A、AAAA、MX、NS、TXT、CNAME）
python3 SKILL_DIR/scripts/domain_intel.py dns example.com

# 域名可用性检查（被动式：DNS + WHOIS + SSL 信号）
python3 SKILL_DIR/scripts/domain_intel.py available coolstartup.io

# 批量分析 — 同时对多个域名执行多项检查
python3 SKILL_DIR/scripts/domain_intel.py bulk example.com github.com google.com
python3 SKILL_DIR/scripts/domain_intel.py bulk example.com github.com --checks ssl,dns
```

`SKILL_DIR` 是包含此 SKILL.md 文件的目录。所有输出均为结构化的 JSON。

## 可用命令

| 命令 | 功能 | 数据源 |
|---------|-------------|-------------|
| `subdomains` | 从证书日志中查找子域名 | crt.sh (HTTPS) |
| `ssl` | 检查 TLS 证书详情 | 直接 TCP:443 连接到目标 |
| `whois` | 注册信息、注册商、日期 | WHOIS 服务器 (TCP:43) |
| `dns` | A、AAAA、MX、NS、TXT、CNAME 记录 | 系统 DNS + Google DoH |
| `available` | 检查域名是否已注册 | DNS + WHOIS + SSL 信号 |
| `bulk` | 对多个域名运行多项检查 | 上述所有数据源 |

## 何时使用此技能 vs 内置工具

- **使用此技能** 解决基础设施相关问题：子域名、SSL 证书、WHOIS、DNS 记录、可用性
- **使用 `web_search`** 进行关于域名/公司一般信息的研究
- **使用 `web_extract`** 获取网页的实际内容
- **使用带 `curl -I` 的 `terminal`** 进行简单的“此 URL 是否可达”检查

| 任务 | 更合适的工具 | 原因 |
|------|-------------|-----|
| “example.com 是做什么的？” | `web_extract` | 获取页面内容，而非 DNS/WHOIS 数据 |
| “查找某公司的信息” | `web_search` | 一般研究，不局限于域名 |
| “这个网站安全吗？” | `web_search` | 信誉检查需要网络上下文 |
| “检查 URL 是否可达” | 带 `curl -I` 的 `terminal` | 简单的 HTTP 检查 |
| “查找 X 的子域名” | **此技能** | 唯一的被动式数据源 |
| “SSL 证书何时过期？” | **此技能** | 内置工具无法检查 TLS |
| “谁注册了这个域名？” | **此技能** | WHOIS 数据不在网络搜索中 |
| “coolstartup.io 是否可用？” | **此技能** | 通过 DNS+WHOIS+SSL 进行被动式可用性检查 |

## 平台兼容性

纯 Python 标准库（`socket`, `ssl`, `urllib`, `json`, `concurrent.futures`）。
无需任何依赖，在 Linux、macOS 和 Windows 上运行一致。

- **crt.sh 查询** 使用 HTTPS（端口 443）—— 在大多数防火墙下可用
- **WHOIS 查询** 使用 TCP 端口 43 —— 在受限网络环境中可能被阻止
- **DNS 查询** 对 MX/NS/TXT 使用 Google DoH（HTTPS）—— 对防火墙友好
- **SSL 检查** 连接到目标服务器的端口 443 —— 唯一的“主动”操作

## 数据源

所有查询均为 **被动式** —— 无端口扫描，无漏洞测试：

- **crt.sh** —— 证书透明度日志（子域名发现，仅 HTTPS）
- **WHOIS 服务器** —— 直接 TCP 连接到 100+ 个权威顶级域注册商
- **Google DNS-over-HTTPS** —— MX、NS、TXT、CNAME 解析（对防火墙友好）
- **系统 DNS** —— A/AAAA 记录解析
- **SSL 检查** 是唯一的“主动”操作（TCP 连接到目标:443）

## 备注

- WHOIS 查询使用 TCP 端口 43 —— 在受限网络环境中可能被阻止
- 部分 WHOIS 服务器会隐去注册者信息（GDPR 合规）—— 请向用户说明这一点
- 对于非常流行的域名，crt.sh 可能较慢（数千张证书）—— 请设定合理预期
- 可用性检查基于启发式（3 种被动信号）—— 不如注册商 API 那样权威

---

--- body ---
*贡献者：[@FurkanL0](https://github.com/FurkanL0)*