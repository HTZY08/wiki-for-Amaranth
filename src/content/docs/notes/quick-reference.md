---
title: 常用命令速查
description: 不用理解原理，找到你要做的事，复制命令执行
---

> 即用即走的操作菜谱。

## 微信连不上了

```bash
ps aux | grep "hermes gateway run"                  # ① 进程活着吗？
cat /opt/data/gateway_state.json | python3 -m json.tool    # ② 连接状态？
tail -20 /opt/data/logs/agent.log                    # ③ 最新错误？

# 最常见的修复（代理冲突导致）：
pkill -f "hermes gateway run"
rm -f /opt/data/gateway.lock /opt/data/gateway_state.json
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
HERMES_ALLOW_ROOT_GATEWAY=1 /opt/hermes/.venv/bin/hermes gateway run --replace

# 等 1-2 分钟让限流计数器复位
```

## 电脑重启了，重新连微信

```bash
rm -f /opt/data/gateway.lock /opt/data/gateway_state.json
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
HERMES_ALLOW_ROOT_GATEWAY=1 /opt/hermes/.venv/bin/hermes gateway run --replace
```

## 想用微信发语音气泡（不是文件）

在回复中加入：

```
[[audio_as_voice]]
MEDIA:/path/to/audio.mp3
```

## 生一张图（SiliconFlow 便宜版）

```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
python3 << 'PYEOF'
import os, json, urllib.request

key = None
with open('/opt/data/.env') as f:
    for line in f:
        if line.startswith('SILICONFLOW_API_KEY'):
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
    headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
)
resp = json.loads(opener.open(req).read())
print(resp['data'][0]['url'])
PYEOF
```

## 本地跑一个临时 HTTP 服务器

```bash
python3 -m http.server 8080 --bind 0.0.0.0
```

## Docker 容器内查看 GPU 是否可用

```bash
docker exec hermes-agent nvidia-smi
```
