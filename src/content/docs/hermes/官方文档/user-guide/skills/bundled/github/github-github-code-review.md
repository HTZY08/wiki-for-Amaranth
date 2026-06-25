--- frontmatter ---


--- body ---
## 5. PR 审查工作流（端到端）

当用户要求你“审查 PR #N”、“看看这个 PR”或给你一个 PR URL 时，请按以下步骤操作：

### 第 1 步：设置环境

```bash
source "${HERMES_HOME:-$HOME/.hermes}/skills/github/github-auth/scripts/gh-env.sh"
# 或者运行本技能顶部的内联设置代码块
```

### 第 2 步：收集 PR 上下文

在深入代码之前，获取 PR 的元数据、描述以及变更文件列表，以了解范围。

**使用 gh：**
```bash
gh pr view 123
gh pr diff 123 --name-only
gh pr checks 123
```

**使用 curl：**
```bash
PR_NUMBER=123

# PR 详情（标题、作者、描述、分支）
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER

# 变更文件及行数
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER/files
```

### 第 3 步：在本地检出 PR

这将使你能够完全访问 `read_file`、`search_files` 以及运行测试的功能。

```bash
git fetch origin pull/$PR_NUMBER/head:pr-$PR_NUMBER
git checkout pr-$PR_NUMBER
```

### 第 4 步：阅读差异并理解变更

```bash
# 相对于基础分支的完整差异
git diff main...HEAD

# 或者针对大型 PR 逐个文件查看
git diff main...HEAD --name-only
# 然后针对每个文件：
git diff main...HEAD -- path/to/file.py
```

对于每个变更文件，使用 `read_file` 查看变更周围的完整上下文——仅靠差异可能会遗漏只有在周围代码中才能发现的问题。

### 第 5 步：在本地运行自动化检查（如适用）

```bash
# 如果有测试套件，运行测试
python -m pytest 2>&1 | tail -20
# 或：npm test, cargo test, go test ./..., 等等

# 如果配置了 linter，则运行
ruff check . 2>&1 | head -30
# 或：eslint, clippy, 等等
```

### 第 6 步：应用审查清单（第 3 节）

逐一检查每个类别：正确性（Correctness）、安全性（Security）、代码质量（Code Quality）、测试（Testing）、性能（Performance）、文档（Documentation）。

### 第 7 步：将审查发布到 GitHub

整理你的发现，并通过内联评论（inline comments）将其作为正式审查提交。

**使用 gh：**
```bash
# 如果没有问题——批准
gh pr review $PR_NUMBER --approve --body "由 Hermes 代理审查。代码看起来干净——测试覆盖良好，无安全问题。"

# 如果发现问题——要求修改并附带内联评论
gh pr review $PR_NUMBER --request-changes --body "发现一些问题——请参见内联评论。"
```

**使用 curl —— 带多个内联评论的原子化审查：**
```bash
HEAD_SHA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

# 构建审查 JSON —— event 可选 APPROVE、REQUEST_CHANGES 或 COMMENT
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER/reviews \
  -d "{
    \"commit_id\": \"$HEAD_SHA\",
    \"event\": \"REQUEST_CHANGES\",
    \"body\": \"## Hermes 代理审查\n\n发现 2 个问题，1 个建议。请参见内联评论。\",
    \"comments\": [
      {\"path\": \"src/auth.py\", \"line\": 45, \"body\": \"🔴 **严重：** 用户输入直接传递给 SQL 查询——请使用参数化查询。\"},
      {\"path\": \"src/models.py\", \"line\": 23, \"body\": \"⚠️ **警告：** 密码未经哈希存储。\"},
      {\"path\": \"src/utils.py\", \"line\": 8, \"body\": \"💡 **建议：** 这与 core/utils.py:34 中的逻辑重复。\"}
    ]
  }"
```

### 第 8 步：同时发布一个总结性评论

除了内联评论外，再留一个顶层总结，以便 PR 作者一目了然地了解全貌。使用 `references/review-output-template.md` 中的审查输出格式。

**使用 gh：**
```bash
gh pr comment $PR_NUMBER --body "$(cat <<'EOF'
## 代码审查总结

**判定：要求修改**（2 个问题，1 个建议）

### 🔴 严重
- **src/auth.py:45** —— SQL 注入漏洞

### ⚠️ 警告
- **src/models.py:23** —— 明文密码存储

### 💡 建议
- **src/utils.py:8** —— 重复逻辑，考虑合并

### ✅ 看起来不错
- 干净的 API 设计
- 中间件层良好的错误处理

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