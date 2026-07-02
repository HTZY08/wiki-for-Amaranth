#!/usr/bin/env python3
"""Inject top cluster experience notes into SOUL.md.
Called after cluster-experience-rebuild (every 30 min).
Makes experience notes always visible in context.
"""
import json, os

SOUL = ".//SOUL.md"
NOTES = "./data/cluster-experience.json"

def build_experience_block() -> str:
    if not os.path.exists(NOTES):
        return "暂无经验数据（cron 未运行）\n"
    with open(NOTES) as f:
        notes = json.load(f)
    
    # Top 8 clusters by session count, only those with experience
    clusters = sorted(notes.items(), key=lambda x: -x[1].get("sessions", 0))
    lines = []
    for cid_str, info in clusters[:8]:
        exp = info.get("experience", [])
        if exp:
            s = info.get("sessions", 0)
            lines.append(f"  C{cid_str} ({s}次会话, {len(exp)}条):")
            for e in exp[:3]:
                lines.append(f"    • {e}")
    return "\n".join(lines) if lines else "暂无经验数据\n"

def main():
    exp_block = build_experience_block()
    
    new_section = f"""## 状态空间 — 经验笔记

每次对话开始时，根据你第一句话匹配活跃经验簇：

```
{exp_block}
```

### 注入规则
- 你说第一句话后 → 提取关键词 → 匹配簇 → 前缀注入 📁 CX 经验
- 没命中时正常回答，不提
- 对话结束时自动记录关键词，cron 每 30 分钟重建"""

    with open(SOUL) as f:
        content = f.read()

    # Find the old section boundaries
    start_marker = "## 状态空间 — 经验笔记"
    end_marker = "## 前置检查"

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    if start_idx >= 0 and end_idx > start_idx:
        # Replace between the section headers
        old_section = content[start_idx:end_idx]
        new_full = new_section + "\n\n"
        content = content.replace(old_section, new_full, 1)
        with open(SOUL, "w") as f:
            f.write(content)
        print(f"✅ 已更新 SOUL.md 经验笔记 ({len(exp_block)} chars)")
    else:
        print(f"⚠️ 未找到章节标记（start={start_idx}, end={end_idx}）")

if __name__ == "__main__":
    main()
