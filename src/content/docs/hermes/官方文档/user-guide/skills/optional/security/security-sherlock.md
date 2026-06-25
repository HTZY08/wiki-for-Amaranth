---
title: "Sherlock"
---

{/* 本页面由技能目录下的 SKILL.md 文件通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

# Sherlock

跨 400+ 社交网络的开源网络情报（OSINT）用户名搜索。根据用户名追踪社交媒体账户。

## 技能（Skill）元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/security/sherlock` 安装 |
| 路径 | `optional-skills/security/sherlock` |
| 版本 | `1.0.0` |
| 作者 | unmodeled-tyler |
| 许可证 | MIT |
| 支持平台 | linux, macos, windows |
| 标签 | `osint`, `security`, `username`, `social-media`, `reconnaissance` |

## 参考：完整 SKILL.md

:::info
以下为触发该技能时 Hermes 加载的完整技能定义。这是技能激活时代理所看到的指令。
:::

# Sherlock OSINT 用户名搜索

利用 [Sherlock 项目（Sherlock Project）](https://github.com/sherlock-project/sherlock) 跨 400+ 社交网络根据用户名追踪社交媒体账户。

## 使用时机

- 用户要求查找与某用户名相关联的账户
- 用户想检查用户名在各平台的可用性
- 用户正在进行 OSINT 或侦察研究
- 用户询问“这个用户名注册在哪里？”或类似问题

## 前置条件

- 已安装 Sherlock CLI：`pipx install sherlock-project` 或 `pip install sherlock-project`
- 备选方案：可使用 Docker（`docker run -it --rm sherlock/sherlock`）
- 具备访问社交平台的网络能力

## 操作流程

### 1. 检查 Sherlock 是否已安装

**在执行任何其他操作之前**，先确认 sherlock 可用：

```bash
sherlock --version
```

如果命令执行失败：
- 提供安装方式：`pipx install sherlock-project`（推荐）或 `pip install sherlock-project`
- **不要**尝试多种安装方法——选定一种并继续
- 如果安装失败，告知用户并停止

### 2. 提取用户名

**如果用户消息中明确提到了用户名，直接提取出来。**

以下示例中**不应**使用澄清（clarify）：
- “查找 nasa 的账户”→ 用户名为 `nasa`
- “搜索 johndoe123”→ 用户名为 `johndoe123`
- “检查 alice 是否存在于社交媒体”→ 用户名为 `alice`
- “在社交网络上查找用户 bob”→ 用户名为 `bob`

**仅在以下情况使用澄清：**
- 提到了多个可能的用户名（“搜索 alice 或 bob”）
- 表述模糊（“搜索我的用户名”但未具体说明）
- 完全没有提到用户名（“进行一次 OSINT 搜索”）

提取时，**完整保留**用户所说的用户名——包括大小写、数字、下划线等。

### 3. 构建命令

**默认命令**（除非用户特别要求，否则使用此命令）：
```bash
sherlock --print-found --no-color "<username>" --timeout 90
```

**可选标志**（仅在用户明确要求时添加）：
- `--nsfw` — 包含 NSFW 站点（仅当用户要求时）
- `--tor` — 通过 Tor 路由（仅当用户要求匿名时）

**不要通过澄清询问选项**——直接运行默认搜索。用户如需要特定选项可自行提出。

### 4. 执行搜索

通过 `terminal` 工具运行。该命令通常耗时 30-120 秒，取决于网络状况和检查的站点数量。

**终端调用示例：**
```json
{
  "command": "sherlock --print-found --no-color \"target_username\"",
  "timeout": 180
}
```

### 5. 解析并呈现结果

Sherlock 以简单格式输出已找到的账户。解析输出并呈现：

1. **摘要行：**“为用户名 'Y' 找到 X 个账户”
2. **分类链接：**如方便，可按平台类型分组（社交、职业、论坛等）
3. **输出文件位置：**默认情况下 Sherlock 将结果保存到 `<username>.txt`

**输出解析示例：**
```
[+] Instagram: https://instagram.com/username
[+] Twitter: https://twitter.com/username
[+] GitHub: https://github.com/username
```

尽可能以可点击链接的形式呈现发现结果。

## 常见陷阱（Pitfalls）

### 未找到结果
如果 Sherlock 未找到任何账户，这通常是正确的——该用户名可能未在已检查的平台上注册。建议：
- 检查拼写/变体
- 尝试使用 `?` 通配符查找相似用户名：`sherlock "user?name"`
- 用户可能设置了隐私设置或已删除账户

### 超时问题
部分站点响应缓慢或阻止自动请求。可使用 `--timeout 120` 增加等待时间，或使用 `--site` 限制搜索范围。

### Tor 配置
`--tor` 需要 Tor 守护进程正在运行。如果用户需要匿名但 Tor 不可用，建议：
- 安装 Tor 服务
- 使用 `--proxy` 配合替代代理

### 误报（False Positives）
某些站点因其响应结构始终返回“已找到”。对意外结果应结合手动检查进行交叉验证。

### 速率限制（Rate Limiting）
激进的搜索可能触发速率限制。对于批量用户名搜索，请在调用之间添加延迟，或使用 `--local` 配合缓存数据。

## 安装

### pipx（推荐）
```bash
pipx install sherlock-project
```

### pip
```bash
pip install sherlock-project
```

### Docker
```bash
docker pull sherlock/sherlock
docker run -it --rm sherlock/sherlock <username>
```

### Linux 软件包
在 Debian 13+、Ubuntu 22.10+、Homebrew、Kali、BlackArch 中可用。

## 伦理使用（Ethical Use）

本工具仅用于合法的 OSINT 和研究目的。提醒用户：
- 仅搜索本人拥有或有权调查的用户名
- 尊重各平台的服务条款
- 不得用于骚扰、跟踪或非法活动
- 在分享结果前考虑隐私影响

## 验证（Verification）

运行 sherlock 后，验证：
1. 输出列出了带有 URL 的发现站点
2. 如果使用文件输出，会创建 `<username>.txt` 文件（默认输出）
3. 如果使用了 `--print-found`，输出应仅包含匹配项的 `[+]` 行

## 交互示例

**用户：**“你能检查一下用户名 'johndoe123' 是否存在于社交媒体上吗？”

**代理（Agent）操作流程：**
1. 检查 `sherlock --version`（确认已安装）
2. 用户名已提供——直接继续
3. 运行：`sherlock --print-found --no-color "johndoe123" --timeout 90`
4. 解析输出并呈现链接

**响应格式：**
> 为用户名 'johndoe123' 找到 12 个账户：
>
> • https://twitter.com/johndoe123
> • https://github.com/johndoe123
> • https://instagram.com/johndoe123
> • [... 更多链接]
>
> 结果已保存至：johndoe123.txt

---

--- body ---
--- body ---
**用户：**“搜索用户名 'alice'，包含 NSFW 站点”

**代理（Agent）操作流程：**
1. 检查 sherlock 是否已安装
2. 用户名和 NSFW 标志均已提供
3. 运行：`sherlock --print-found --no-color --nsfw "alice" --timeout 90`
4. 呈现结果