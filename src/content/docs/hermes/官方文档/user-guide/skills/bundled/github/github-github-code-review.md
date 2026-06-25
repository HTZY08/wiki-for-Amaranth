---
title: Github Code Review
---

--- body ---
*由 Hermes 代理审查*
EOF
)"
```

### 第 9 步：清理

```bash
git checkout main
git branch -D pr-$PR_NUMBER
```

### 决策：批准 vs 要求修改 vs 评论

- **批准（Approve）** —— 没有严重或警告级别的问题，只有微小的建议或一切正常
- **要求修改（Request Changes）** —— 存在任何应在合并前修复的严重或警告级别的问题
- **评论（Comment）** —— 观察和建议，但没有阻塞性问题（当你不确定或 PR 是草稿时使用）