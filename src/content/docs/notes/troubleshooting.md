---
title: 故障排除手册
description: 一个月踩过的坑和修复方法
---

> 所有故障按频率排序——最常见的排最前面。

---

## 🥇 微信网关篇

### 微信连不上 / 消息发不出去

**症状：** 消息发出去没回复，或者日志里出现 `Cannot connect to host ilinkai.weixin.qq.com`

**诊断排序（30 秒内定位）：**

```bash
# ① 进程活着吗？（2 秒）
ps aux | grep "hermes gateway run"

# ② 连接状态？（1 秒）
cat /opt/data/gateway_state.json | python3 -m json.tool

# ③ 最新错误？（3 秒）
tail -20 /opt/data/logs/agent.log
```

**#1 原因：代理冲突** — gateway 继承了代理环境变量

**修复：** 去掉代理重新启动

```bash
pkill -f "hermes gateway run"
rm -f /opt/data/gateway.lock /opt/data/gateway_state.json
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
HERMES_ALLOW_ROOT_GATEWAY=1 /opt/hermes/.venv/bin/hermes gateway run --replace
```

**#2 原因：限流**

**症状：** 日志出现 `rate limited`，消息能收到但发不出回复

**修复：** 重启 gateway 断开限流循环（同上），然后等 1-2 分钟让计数器复位

**#3 原因：s6 环境变量丢失**

**症状：** `.env` 里配好了但 gateway 读不到

**修复：** 修改 s6 run 脚本，在 `exec` 前显式注入变量。脚本路径：

```bash
find /run /opt/data -name "run" -path "*/gateway*/run"
```

---

## 🥈 Docker / 容器篇

### Docker 连不上（权限问题）

```bash
# 症状：docker: permission denied
# 修复：把用户加入 docker 组
sudo usermod -aG docker $USER
# 然后退出重新登录
```

### 容器内 GPU 不可用

```bash
# 症状：nvidia-smi 报错 "could not select device driver"
# 修复：安装 NVIDIA Container Toolkit
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### 容器映射目录不见了

```bash
# 症状：容器内 /opt/data 为空
# 修复：检查 Docker Desktop WSL 集成设置
# Docker Desktop → Settings → Resources → WSL Integration
# 确保 Ubuntu 开关是开的
```

---

## 🥉 SSH / Git 篇

### SSH 推送失败

```bash
# 症状：git push 报 Permission denied
# 诊断：确认密钥路径
ls -la ~/.ssh/id_*

# 常见原因：HOME 环境变量导致 SSH 找错路径
# 修复：在仓库内指定 SSH 命令
git config core.sshCommand "ssh -i /正确的/密钥路径"
```

### Actions 构建失败

```bash
# 症状：GitHub Actions 报 Node.js 版本不支持
# 修复：workflow 中指定 Node 版本 ≥ 22
# actions/setup-node@v4 → node-version: 22
```

### Secret 名不对

```bash
# 症状：Actions 部署步骤报 401/403
# 修复：确认 GitHub Secrets 名称与 workflow 中一致
# workflow 里写的是 ${{ secrets.CLOUDFLARE }}
# 就去 Settings → Secrets 检查名字是不是完全一样
```

---

## 🏅 网络 / 代理篇

### 国内 API 连不上

```bash
# 症状：curl 到 siliconflow.cn 超时
# 原因：走了代理（国内 API 不能走代理）
# 修复：去掉代理环境变量
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
```

### 海外 API 连不上

```bash
# 症状：curl 到 openai.com 超时
# 原因：代理挂了或者路由不对
# 诊断：
curl -x http://127.0.0.1:7890 -s -o /dev/null -w "%{http_code}" https://www.google.com/generate_204
# 如果不是 204，说明代理坏了
```

---

## 🎨 生图篇

### 图片太暗看不清

```bash
# 原因：Qwen-Image 默认出图偏暗
# 修复：在 prompt 里加 "画面明亮清晰，曝光正常"
```

### 人脸崩了（AI 假脸感）

```bash
# 原因：SiliconFlow 模型不擅长写实人像
# 修复：换 API Yi 的 chatgpt-image-latest（贵但脸不崩）
```

### 图片在微信里发不出去

```bash
# 原因：图片太大（微信限制 ~1MB）
# 修复：压缩
python3 -c "
from PIL import Image
img = Image.open('原图.png').convert('RGB')
img.thumbnail((1200, 1200))
img.save('压缩后.jpg', 'JPEG', quality=85)
"
```

---

## 📝 写作/论文篇

### 怎么调用古籍库

```bash
# 古籍在：/opt/data/references/Chinese-Classical-Texts/
# 15,694 篇，用 grep / find 搜索
grep -r "关键词" /opt/data/references/Chinese-Classical-Texts/ -l
```

### 查文献表征数据

```bash
# 通过 Amaranth 的 material-characterization-query skill
# 告诉她 "查 AuNP 的 TEM 数据" 即可
```

---

## 📋 通用诊断流程

任何问题先做这三步：

```bash
# 1. 看日志
tail -50 /opt/data/logs/errors.log

# 2. 看进程
ps aux | grep -E "hermes|mihomo|python" | grep -v grep

# 3. 看磁盘
df -h /opt/data
```
