---
title: 自定义技能集
description: 自建的 Hermes Skill 生态——从微信机器人到论文编辑器，5 个开箱即用的自动化能力
---

都是平时干活攒的，每个都有完整的 SKILL.md 和可执行的触发流程。

---

## 🤖 微信接入机器人

将 Hermes 接进个人微信。基于腾讯 iLink Bot API，无需注册开发者账号，扫码即用。

**开箱步骤：**

```bash
# 安装依赖
source /opt/hermes/.venv/bin/activate
uv pip install aiohttp cryptography

# 交互式向导（推荐）
hermes gateway setup
# 选 "Weixin / WeChat" → 扫码 → 配置DM策略

# 或 API 直拿二维码
python3 << 'PY'
import urllib.request, json
resp = urllib.request.urlopen(
    "https://ilinkai.weixin.qq.com/ilink/bot/get_bot_qrcode?bot_type=3", timeout=10)
data = json.loads(resp.read())
print("QR:", data.get("qrcode_img_content"))
PY
```

扫码后自动写入 `~/.hermes/.env`，重启 Hermes 即生效：
```ini
WEIXIN_ACCOUNT_ID=<自动获取>
WEIXIN_TOKEN=<自动获取>
```

**故障速查：**
- 网关报 `NO_PLATFORMS` → 检查 `.env` 中 `WEIXIN_ACCOUNT_ID` / `WEIXIN_TOKEN` 是否写入
- 扫码后无反应 → 代理冲突，确认 mihomo 未拦截 `ilinkai.weixin.qq.com`
- 消息延迟大 → iLink Bot 有 5 秒/条的限流，群消息需开白名单

**文件位置：** `~/.hermes/skills/.archive/hermes-wechat-setup/SKILL.md`

---

## 🌐 网页自动化 (Playwright)

Hermes 的 `browser_navigate` 等工具不能执行 JS、无反检测、CAPTCHA 过不去。Playwright 补上。

**开箱步骤：**

```bash
source /opt/hermes/.venv/bin/activate
uv pip install playwright

# 下载 Chromium（去掉代理防 CAPTCHA 反爬）
http_proxy="" https_proxy="" python3 -m playwright install chromium
```

**核心脚架：**

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
    )
    page = await browser.new_page()
    # 覆盖 webdriver 检测
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
    """)
    await page.goto("目标URL")
    content = await page.content()
```

**适用场景：**
- 抖音/微博等需要 JS 执行的数据采集
- 政务平台自动填表（验证码用 `page.screenshot` 截取后走 OCR）
- 需要绕过遮罩层点击拦截的页面

**文件位置：** `~/.hermes/skills/.archive/playwright-web-automation/SKILL.md`

---

## ✍️ 中文论文语言编辑器

对工学/理学/医学硕士论文做终稿语言净化。**只改语言，不改内容**——不收束套话、不拔高观点、不造概念标签。

**开箱用法（对话中直接告诉 AI）：**

> "帮我润色这段论文正文"
> "去一下 AI 味"
> "压一压翻译腔"

AI 会执行四个层面处理：

| 层面 | 做什么 | 典型操作 |
|------|--------|----------|
| 句式润色 | 按中文科技论文语序重排 | 长句拆短、条件→行为→结果 |
| 用词净化 | 清除 AI 词和空泛评价 | "赋能""重塑""显著地"→删 |
| 文体控制 | 保持全文语气一致 | 不出现前修后拼的断裂 |
| 机械净化 | 修排版垃圾 | 括号不配对、中英标点混、概念双引号 |

**核心原则：** 每段只承担一个功能（背景/方法/结果/讨论），段落末尾不写"具有重要意义"这种废话。

**文件位置：** `~/.hermes/skills/.archive/chinese-academic-editing/SKILL.md`

---

## 🧠 用户写作风格采集

持续收集语言风格数据，目标是训练一个能复刻你说话/写作方式的模型。每次对话后自动追加观察，不用你提醒。

**自动采集的维度：**

| 维度 | 看什么 |
|------|--------|
| 句法特征 | 句长、指令结构、否定式、语气词 |
| 修辞特征 | 类比模式、直白/缓冲比例 |
| 交互特征 | 纠偏方式、推进信号 |
| 写作特征 | 开头方式、段落推进 |
| 词汇偏好 | 高频词、避用词 |

**数据文件位置：** `/opt/data/docs/user-style-data-v0.1.md`

**与 AI 配合方式：**
- 对话中自然表达即可，AI 会在收尾时扫描本轮对话，提取新的语言模式追加到数据文件
- 如果你纠正了 AI 对你风格的理解，那是一次重要的采样

**文件位置：** `~/.hermes/skills/.archive/user-style-corpus/SKILL.md`

---

## 🗣️ 用户风格语料库

上者的兄弟技能，一个偏"识别和存储"，这个偏"系统化积累"。核心区别：

- `user-style-collection` → 跨会话持续追加已有维度
- `user-style-corpus` → 发现新维度时开新节，保证覆盖完整

**触发条件：** 每次对话自然结束时自动执行。不需要你喊"记得收集"。

**当前数据量：** 每次对话后增量更新，版本号自动递增 (`v0.1 → v0.2 → ...`)

**文件位置：** `~/.hermes/skills/.archive/user-style-collection/SKILL.md`

---

> 所有 skill 都在 `~/.hermes/skills/.archive/` 下。想激活某个 skill 直接用 `skill_manage` 创建或 `skill_view` 加载即可。
