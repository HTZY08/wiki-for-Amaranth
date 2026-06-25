---
title: Requesting Code Review
---

[INSERT GIT DIFF]
---

--- body ---
--- body ---
精确修复每个问题。描述你更改了什么以及原因。”””，
    context="仅修复报告的问题。不更改任何其他内容。”，
    toolsets=["terminal", "file"]
)

修复代理（Agent）完成后，重新运行步骤1-6（完整验证循环）。
- 通过：进入步骤8
- 失败且尝试次数 < 2：重复步骤7
- 失败且尝试次数 >= 2：将剩余问题上报给用户，并建议使用 `git stash` 或 `git reset` 撤销更改

## 步骤8 — 提交

如果验证通过：

```bash
git add -A && git commit -m "[verified] <description>"
```

`[verified]` 前缀表示该更改已通过独立审查者的批准。

## 参考：需标记的常见模式

### Python
```python
# 错误：SQL 注入
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
# 正确：参数化
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# 错误：Shell 注入
os.system(f"ls {user_input}")
# 正确：安全的子进程
subprocess.run(["ls", user_input], check=True)
```

### JavaScript
```javascript
// 错误：XSS
element.innerHTML = userInput;
// 正确：安全
element.textContent = userInput;
```

## 与其他技能（Skill）的集成

**子代理驱动开发（subagent-driven-development）：** 在每项任务之后运行此流程，作为质量关卡。两阶段审查（规范合规性 + 代码质量）使用此管道。

**测试驱动开发（test-driven-development）：** 此管道验证是否遵循了 TDD 原则——测试存在、测试通过、无回归。

**计划（plan）：** 验证实现是否符合计划要求。

## 陷阱

- **空补丁（Empty diff）** —— 检查 `git status`，告知用户无需验证
- **非 Git 仓库** —— 跳过并告知用户
- **大补丁（Large diff，>15k 字符）** —— 按文件分割，分别审查每个文件
- **delegate_task 返回非 JSON** —— 使用更严格的提示重试一次，然后视为 FAIL
- **误报（False positives）** —— 如果审查者标记了某些有意为之的内容，请在修复提示中注明
- **未找到测试框架** —— 跳过回归检查，审查者判决仍会运行
- **未安装 Lint 工具** —— 静默跳过该检查，不要导致失败
- **自动修复引入新问题** —— 算作一次新的失败，循环继续