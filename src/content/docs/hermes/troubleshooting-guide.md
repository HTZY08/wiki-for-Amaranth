---
title: 完整排障索引
description: 按部署阶段排的完整踩坑实录——不只告诉你"怎么修"，还告诉你"为什么"
---

部署 Hermes 的过程中，很多问题不是步骤不对——是**步骤背后的原因你不知道**。本页整理了所有实际踩过的坑，按阶段排列，每条注明根因、修复和指向的文档页。

---

## 部署阶段

:::note[核心问题]
Docker + Hermes 第一次跑起来至少需要三样东西：Docker Desktop 正常运行、网络能出墙、配置正确。三样缺任何一样都会卡住，而且报错信息经常让人看不懂。
:::

### Docker Desktop 容器启动不了

**表现**：`docker compose up -d` 后 `docker compose ps` 显示容器状态为 `Exited`。

**根因排查**：
```bash
docker compose logs hermes
```

**常见原因**：

| 原因 | 报错特征 | 修复 |
|------|---------|------|
| WSL2 集成未开启 | `Cannot connect to the Docker daemon` | Docker Desktop → Settings → Resources → WSL Integration → 勾选你的发行版 |
| config.yaml 语法错误 | `yaml: unmarshal errors` | 用 `python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"` 检查 |
| API Key 缺失 | `provider "deepseek" requires api_key` | 检查 `~/.hermes/.env` 中 Key 是否存在 |

**为什么**：Docker Desktop 在 Windows 上通过 WSL2 后端运行。如果 WSL Integration 没开，Linux 子系统里的 docker 命令找不到 Docker 守护进程。

**相关文档**：[Docker 部署 → 故障排查](/hermes/docker-deploy/#故障排查)

---

### 容器内无法联网

**表现**：容器能启动，但 Hermes 回复说"网络错误"或搜索返回空。

**根因**：代理没配或配错了。

**修复**：
```bash
# 检查容器内网络
docker exec hermes-agent curl -I https://api.github.com

# 如果不通，检查 mihomo 代理是否正在运行
docker compose ps
```

**为什么**：Hermes 的简单配置下（`hermes.chat` 等）用的是你家宽带的 DNS 和 IP，出不了墙——必须跑一个代理容器。但反过来，**微信网关不能走代理**（见下文）。

**相关文档**：[代理配置](/hermes/proxy-setup/)

---

### Docker socket 没挂载 → Python 代码执行失败

**表现**：Agent 尝试执行 Python 代码时返回 `'docker version' failed` 或类似错误。

**根因**：`docker-compose.yml` 中没有挂载 Docker socket。Hermes 的代码执行工具（terminal/execute_code）依赖 Docker 守护进程来运行沙箱。

**修复**：在 `docker-compose.yml` 的 `hermes` 服务下添加：
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

**为什么**：Hermes 容器内的 Python 代码并不是在 Hermes 容器本身运行的——它向宿主机的 Docker 守护进程请求一个隔离的执行沙箱。没挂 socket 就发不了这个请求。

---

### Node.js 版本不足

**表现**：构建 Wiki 或其他 Astro 项目时报错，提及 Node.js 版本要求。

**根因**：Astro 6+ 需要 Node.js ≥ 22.12.0。

**修复**：
```bash
node --version
# 如果低于 22.12.0，升级
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
```

---

## 配置阶段

:::note[核心问题]
第一次配置时，你面对的是一个空白的 `config.yaml` 和一堆环境变量——每个 Key 的格式、每段配置的含义、哪些能走代理、哪些不能，都是试出来的。
:::

### API Key 被截断

**表现**：配置后请求始终返回认证错误。

**根因**：`.env` 文件中的 Key 包含特殊字符（`@`、`:`、`#`），用 `export $(cat .env | xargs)` 加载时被 shell 截断了。**WEIXIN_TOKEN 最常中招**（格式为 `xxx@im.bot:长hex字符串`）。

**修复**：用 Python 加载 `.env`，或在 shell 中显式导出每个变量：
```bash
# 不要这样
export $(cat .env | xargs)

# 要这样
set -a; source .env; set +a
```

**为什么**：`xargs` 把 `@` 和 `:` 当成分隔符处理了。

**相关文档**：[微信接入 → Token 验证失败](/hermes/gateway-wechat/#token-验证失败)

---

### DeepSeek 直连 vs 走代理

**常见问题**：DeepSeek 到底需不需要代理？

**答案**：**DeepSeek 可以直接连（国内可访问）**，不需要走代理。但其他模型（OpenAI、Claude、Gemini 等）必须走代理。

**最佳实践**：
```yaml
providers:
  deepseek:
    # 直连，无需代理
    base_url: https://api.deepseek.com
  openai:
    # 需要代理（通过 mihomo）
    base_url: https://api.openai.com
```

**为什么**：DeepSeek 服务器在国内或对国内 IP 开放，而 OpenAI/Anthropic 等被墙。不需要所有流量都走代理。

---

### `.env` 文件不同步

**表现**：改了 `.env` 后重启 Hermes 不生效。

**根因**：Hermes 有两个 `.env` 文件：`~/.hermes/.env`（Hermes 原生加载）和 `/opt/data/.env`（有些脚本或配置会引用这个）。只改一个另一个没同步。

**修复**：统一只用一套。推荐用 `~/.hermes/.env`，然后用 `hermes config set` 命令配置：
```bash
hermes config set model.vision "provider=... , api_key=$API_KEY"
```

**为什么**：WSL 环境里不同的启动方式（手动 vs s6 vs systemd）加载的是不同的 `.env` 文件。

---

## 微信接入阶段

:::note[核心问题]
微信网关（WeChat Gateway）是踩坑最密集的部分。文本消息通常能用，但**图片发不出去、重启后挂掉、被限流**这三个问题几乎每个人都会遇到。核心矛盾是：微信 iLink 服务器在国内（不能走代理），而 Hermes 代理出口在美国。
:::

### 代理冲突（poll error）

**表现**：gateway 日志每 30 秒报 `Cannot connect to host ilinkai.weixin.qq.com:443`。

**根因**：Gateway 走了代理，但微信 iLink 是国内服务器，美国出口连不上。

**修复**：启动 gateway 前取消代理环境变量：
```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
```
然后在 s6 run 脚本的 `exec` 前也插入同样的 `unset`。

**诊断**：
```bash
# 直连测试
curl -s --noproxy '*' https://ilinkai.weixin.qq.com/ilink/bot/get_bot_qrcode?bot_type=3

# 走代理测试
curl -s --proxy http://127.0.0.1:7890 https://ilinkai.weixin.qq.com/ilink/bot/get_bot_qrcode?bot_type=3
```

**为什么**：Hermes 容器内默认设置了 http_proxy 环境变量指向 mihomo（127.0.0.1:7890，美国出口）。微信 iLink 是国内 CDN，美国 IP 连不上甚至被主动丢弃。必须让 gateway 进程**直连**。

**相关文档**：[微信接入 → 连不上 iLink 服务器](/hermes/gateway-wechat/#连不上-ilink-服务器)

---

### 图片消息发不出去（"请稍后再试"）

**表现**：Agent 回复中包含图片，微信侧只显示"请稍后再试"，文本消息正常。

**根因**：gateway 重启后，`context_token` 是旧会话的过期 token。上传媒体时 iLink 返回 session timeout 错误。且 Hermes v0.16.0 没有重试机制——失败直接失败。

**修复**：
```bash
# 清除 stale 状态
rm -f /opt/data/gateway.lock /opt/data/gateway_state.json

# 去掉代理后重启 gateway
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
HERMES_ALLOW_ROOT_GATEWAY=1 hermes gateway run --replace

# 等待 1-2 分钟让微信侧会话重建
```

**预防**：
- gateway 重启后，先发一条文本消息确认会话已建立，再发图
- 避免连续发送多张图片（> 3-5 张/分钟触发独立限流）

**为什么**：每次 gateway 重启，它与 iLink 服务器的会话会获得一个新的 `context_token`。但如果重启太快，新进程拿到的还是上一个会话的 token。微信 CDN 收到这个 token 时发现会话已过期 → 拒收图片 → 无重试 → 用户看到"请稍后再试"。

**相关文档**：[微信接入 → 图片消息发不出去](/hermes/gateway-wechat/#图片消息发不出去请稍后再试)

---

### gateway.lock 被 root 抢占

**表现**：gateway 进程不断被 s6 重启（PID 持续变化），gateway.log 无新条目。

**根因**：s6 首次以 root 身份启动了 gateway，创建了 `/opt/data/gateway.lock`。之后 s6 切换到 `hermes` 用户运行，普通用户写不了 root 属主的锁文件 → `PermissionError` → 进程退出 → s6 尝试重启 → 死循环。

**修复**：
```bash
rm -f /opt/data/gateway.lock /opt/data/gateway_state.json
# 重启 gateway
```

**为什么**：s6 先以 root 启动进程完成初始化（创建锁文件），然后切换为低权限用户继续运行。但锁文件创建时的属主是 root，切换后写不了。这是一个 s6 服务配置问题，根源在 `docker-entrypoint.sh` 的启动顺序。

---

### 限流（rate limited）

**表现**：消息发不出去，gateway 日志出现 `rate limited`。

**根因**：微信 iLink 对消息发送有频率限制。消息和图片有两条独立计数器。

**修复**：
```bash
pkill -f "hermes gateway run"
rm -f /opt/data/gateway.lock /opt/data/gateway_state.json
HERMES_ALLOW_ROOT_GATEWAY=1 hermes gateway run --replace
```

等待 1-2 分钟让计数器复位。

> ⚠️ **不要闷头操作**：限流时用户再发消息会加剧限流。先告诉用户在修，再操作。

**为什么**：限流不是永久封禁，是短时间高频请求后的临时阻断。重启 gateway 相当于断开旧的限流计数器，新建一个会话重新开始计数。

**相关文档**：[微信接入 → 限流](/hermes/gateway-wechat/#限流)

---

### gateway 重启后立即发图 → 必挂

**表现**：刚配好或刚重启 gateway，发图立刻失败。

**原因**：见上方"图片消息发不出去"——这是 stale token 场景的高发操作。Wiki 里修复限流的步骤（`pkill → rm lock → 重启`）恰恰又制造了一次 stale token。

**正确顺序**：重启 → 等 1-2 分钟 → 发一条文本确认会话建立 → 再发图。

---

## 生图与语音阶段

:::note[核心问题]
很多人以为部署完就能直接生图——实际上需要 GPU 透传或云端 API 配置。Wiki 之前默认不提这件事，新人发现"聊天可以、画图不行"，反馈的就是 `'docker version' failed`。
:::

### 图片生成用不了（没 GPU）

**表现**：让 Agent 画图，返回"很抱歉，目前无法生成图片"或 Docker 相关错误。

**根因**：默认部署的容器没有 GPU 访问权限。生图依赖 GPU 或云端 API。

**解决（二选一）**：

- **有独立显卡** → [配置 GPU 透传](/hermes/docker-deploy/#高级配置gpu-透传)
- **没有显卡** → [配置云端 API 生图](/hermes/cloud-image-gen/)，无需 GPU，注册即用

**为什么**：Hermes 本身不内置图像生成模型。生图要么调用本地 ComfyUI（需要 GPU），要么调云端 API。两者都没配就会掉到 Python 代码执行路径——那条路需要 Docker socket，没挂 socket 就报错。

**相关文档**：[云端生图配置](/hermes/cloud-image-gen/) | [GPU 计算](/hermes/gpu-compute/)

---

### GPU 透传后容器内 nvidia-smi 不显示

**表现**：WSL2 侧 `nvidia-smi` 正常，但容器内 `nvidia-smi` 报错。

**根因**：NVIDIA Container Toolkit 未安装，或 Docker 运行时未配置。

**修复**：
```bash
# 安装 NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

**相关文档**：[GPU 计算 → NVIDIA Container Toolkit](/hermes/gpu-compute/#第二步nvidia-container-toolkitdocker-gpu-透传)

---

### 语音识别 / TTS 用不了

**表现**：发语音消息没反应，或 TTS 返回错误。

**常见原因**：

| 问题 | 表现 | 修复 |
|------|------|------|
| Whisper 模型未下载 | 首次调用失败 | `docker exec hermes-agent python3 -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cuda')"` 让它自动下载 |
| GPU 没配 | 语音转文字极慢 | 配 GPU 透传（见上方） |
| TTS edge-tts 缺依赖 | 联网问题 | 检查容器内网络 |

---

## 更新与维护

### 更新 Hermes 后配置失效

**表现**：`git pull && docker compose build` 后，之前能用的配置报错。

**根因**：新版 Hermes 改动了配置格式，或插件不兼容。

**修复**：
1. 备份当前配置：`cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak`
2. 查看新版示例配置：`cp config.example.yaml ~/.hermes/config.yaml`
3. 逐一恢复你的配置项
4. 检查 release notes 中的 breaking changes

---

## 技巧与习惯

以下不是故障，但能让你少走弯路：

### 改完配置先验证再重启

```bash
# 验证 config.yaml 语法
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"

# 测试 API 连通性
curl -s https://api.deepseek.com/models | head -c 100
```

### 每次修完一个 Bug 记下来

我们自己也吃了这个亏——**跑成了就忘了为什么失败了**。如果你遇到了这里没覆盖的问题，修完后顺手加上一页，下一个人就不用再趟一遍。

---

## 还没遇到的问题？

如果这里没覆盖你的情况，先去对应功能页面查看详细文档：

- [Docker 部署](/hermes/docker-deploy/)
- [代理配置](/hermes/proxy-setup/)
- [基础配置](/hermes/basic-config/)
- [GPU 透传](/hermes/gpu-compute/)
- [微信接入](/hermes/gateway-wechat/)
- [云端生图](/hermes/cloud-image-gen/)
- [多模型路由](/hermes/model-routing/)
