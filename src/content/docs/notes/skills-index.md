---
title: 技能索引
description: 即用即走的操作菜谱
---

> 不需要理解原理，找到你要做的事，复制命令，粘贴执行。

---

## 微信连不上了

```bash
# 三步排查
ps aux | grep "hermes gateway run"                  # ① 进程活着吗？
cat /opt/data/gateway_state.json | python3 -m json.tool    # ② 连接状态？
tail -20 /opt/data/logs/agent.log                    # ③ 最新的错误？

# 最常见的修复（代理冲突导致）：
pkill -f "hermes gateway run"
rm -f /opt/data/gateway.lock /opt/data/gateway_state.json
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
HERMES_ALLOW_ROOT_GATEWAY=1 /opt/hermes/.venv/bin/hermes gateway run --replace

# 等 1-2 分钟让限流计数器复位
```

## 想用微信发语音气泡（不是文件）

```bash
# 在回复中加入：
[[audio_as_voice]]
MEDIA:/path/to/audio.mp3
```

## 电脑重启了，重新连微信

```bash
rm -f /opt/data/gateway.lock /opt/data/gateway_state.json
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
HERMES_ALLOW_ROOT_GATEWAY=1 /opt/hermes/.venv/bin/hermes gateway run --replace
```

---

## 生一张图（便宜版 / SiliconFlow）

```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

python3 << 'PYEOF'
import os, json, urllib.request

# 读 API Key
key = None
with open('/opt/data/.env') as f:
    for line in f:
        if line.startswith('SILICONFLOW_API_KEY='):
            key = line.split('=', 1)[1].strip()
            break

proxy = urllib.request.ProxyHandler({})
opener = urllib.request.build_opener(proxy)

prompt = "你想要的画面描述，中文最好"
payload = json.dumps({
    "model": "Qwen/Qwen-Image",
    "prompt": prompt,
    "image_size": "928x1664",
}).encode()

req = urllib.request.Request(
    "https://api.siliconflow.cn/v1/images/generations",
    data=payload,
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
)

resp = opener.open(req, timeout=180)
data = json.loads(resp.read())
img_url = (data.get("images") or data.get("data") or [{}])[0].get("url", "")
urllib.request.urlretrieve(img_url, "/opt/data/output.png")
print(f"Saved: /opt/data/output.png")
PYEOF
```

成本 ~$0.03/张。要高质量（~$1/张）让 Amaranth 用 API Yi 跑。

## 微信发的图太大发不出去

```bash
python3 -c "
from PIL import Image
img = Image.open('原图.png').convert('RGB')
img.thumbnail((1200, 1200))
img.save('压缩后.jpg', 'JPEG', quality=85)
print('Done ~270KB')
"
```

---

## 把一段文字转语音

```bash
# 最简单的方式——让 Amaranth 直接发
# 说"把这段话念出来"就行

# 手动指定输出路径：
python3 -m edge_tts --text "要转成语音的文字" --voice zh-CN-XiaoxiaoNeural --write-media /opt/data/output.mp3
```

---

## 查之前聊过什么

```bash
# 直接问 Amaranth："上次我们讨论 XXX 的时候说了什么？"
# 她会自动搜索会话记录

# 或者自己搜 SQLite：
sqlite3 /opt/data/hindsight-lite/memory.db "SELECT content FROM memories WHERE content LIKE '%关键词%' ORDER BY id DESC LIMIT 5;"
```

---

## 日志太多不知道从哪看起

```bash
# 微信相关 → agent.log
tail -50 /opt/data/logs/agent.log

# 程序崩溃 → errors.log
tail -50 /opt/data/logs/errors.log

# Gateway 完整输出 → gateway.log
tail -50 /opt/data/logs/gateway.log
```

---

## 每天自动收日报

这个不需要手动操作。已经在跑了——每天 RSS 采集 → 汇总 → 发微信。

如果想改内容或频率，告诉 Amaranth 就行。

---

## 让 Hermes 定时执行某个任务

```bash
# 告诉 Amaranth：
# "每天早上9点检查我的 GitHub 仓库更新"
# "每30分钟查一次服务器负载"
# 她会帮你建好定时任务
```

---

## 技能怎么来的

每次遇到一个坑、修好了，顺手把修复步骤记成一个 skill。所以 120 多个 skill 里大部分是**故障记录**而不是"最佳实践"——哪个坑踩得最多，哪个 skill 就最长。

如果你发现某个步骤不对了，告诉 Amaranth，她会更新对应的 skill。
