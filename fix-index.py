#!/usr/bin/env python3
"""修复 ai-daily 索引层：index.md / sidebar / 月度页"""
import re, os

WIKI = "/home/ubuntu/.hermes/starlight-wiki"
TODAY = "2026-08-02"

# 1. index.md — 今日最新滚动到 TODAY
idx = f"{WIKI}/src/content/docs/ai-daily/index.md"
with open(idx) as f:
    content = f.read()
content = re.sub(
    r'\[(\d{4}-\d{2}-\d{2})\]\((\d{4}-\d{2}-\d{2})\) — 最近一期日报',
    f'[{TODAY}]({TODAY}) — 最近一期日报',
    content,
)
# 确保 8 月归档链接存在
if "08月-2026" not in content:
    content = content.replace(
        "- [2026年7月](./07月-2026)",
        "- [2026年8月](./08月-2026)\n- [2026年7月](./07月-2026)"
    )
with open(idx, "w") as f:
    f.write(content)
print(f"✅ index.md: 今日最新 → {TODAY}")

# 2. astro.config.mjs — sidebar 滚动 + 加 8 月
cfg = f"{WIKI}/astro.config.mjs"
with open(cfg) as f:
    content = f.read()
content = re.sub(
    r"\{ label: '今日最新', link: 'ai-daily/[\d-]+' \}",
    f"{{ label: '今日最新', link: 'ai-daily/{TODAY}' }}",
    content,
)
if "2026年8月" not in content:
    content = content.replace(
        "{ label: '2026年7月', link: 'ai-daily/07月-2026' }",
        "{ label: '2026年8月', link: 'ai-daily/08月-2026' },\n          { label: '2026年7月', link: 'ai-daily/07月-2026' }"
    )
with open(cfg, "w") as f:
    f.write(content)
print(f"✅ astro.config.mjs: 今日最新 → {TODAY}，加入 8 月")

# 3. 检查 08月-2026.md，不存在则从 8/1、8/2 日报生成
aug = f"{WIKI}/src/content/docs/ai-daily/08月-2026.md"
if not os.path.exists(aug):
    def first_head(path):
        with open(path) as f:
            lines = f.readlines()
        for line in lines[5:]:  # 跳过 frontmatter
            if line.startswith("#") and not line.startswith("##"):
                return line.strip("#").strip()
        return path.split("/")[-1]

    d01 = f"{WIKI}/src/content/docs/ai-daily/2026-08-01.md"
    d02 = f"{WIKI}/src/content/docs/ai-daily/2026-08-02.md"
    h01 = first_head(d01) if os.path.exists(d01) else "2026-08-01"
    h02 = first_head(d02) if os.path.exists(d02) else "2026-08-02"

    # 提取每天的前 2 个话题（用于月度页简介）
    def topics(path, n=3):
        out = []
        with open(path) as f:
            for line in f:
                if line.startswith("###") and len(out) < n:
                    t = line.strip("#").strip()
                    if t and not t.startswith(("🔥", "💡", "📰")):
                        out.append(t)
        return out

    t01 = topics(d01) if os.path.exists(d01) else []
    t02 = topics(d02) if os.path.exists(d02) else []

    with open(aug, "w") as f:
        f.write(f"""---
title: 2026年8月 AI云组会
description: 2026年8月 — AI云组会日报
---

# 2026年8月 AI云组会

## 8月1日：{h01}

{chr(10).join(f'- {t}' for t in t01) if t01 else ''}

详见当日简报：[2026-08-01](./2026-08-01)

---

## 8月2日：{h02}

{chr(10).join(f'- {t}' for t in t02) if t02 else ''}

详见当日简报：[2026-08-02](./2026-08-02)
""")
    print(f"✅ 08月-2026.md 已创建")

# 4. 07月-2026.md — 追加 7/27~7/31 条目（指向每日页）
jul = f"{WIKI}/src/content/docs/ai-daily/07月-2026.md"
with open(jul) as f:
    content = f.read()
if "7月27日" not in content:
    # 检查 7/27~7/31 文件是否存在
    missing = [d for d in ["2026-07-27","2026-07-28","2026-07-29","2026-07-30","2026-07-31"]
               if not os.path.exists(f"{WIKI}/src/content/docs/ai-daily/{d}.md")]
    print(f"⚠️ 7月缺失文件: {missing if missing else '无，全部存在'}")
    with open(jul, "a") as f:
        f.write(f"""

---

## 7月27日~31日：补充条目

- [2026-07-27](./2026-07-27)
- [2026-07-28](./2026-07-28)
- [2026-07-29](./2026-07-29)
- [2026-07-30](./2026-07-30)
- [2026-07-31](./2026-07-31)
""")
    print("✅ 07月-2026.md 追加 7/27~7/31 链接")

print("=== 完成 ===")
