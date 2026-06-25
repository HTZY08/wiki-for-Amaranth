---
title: Github Pr Workflow
---

{/* 此页面由技能中的 SKILL.md 通过网站脚本 generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# GitHub PR 工作流 (Github Pr Workflow)

GitHub PR生命周期：分支（branch）、提交（commit）、打开（open）、持续集成（CI）、合并（merge）。

## 技能元数据 (Skill metadata)

|          |                                                        |
| -------- | ------------------------------------------------------ |
| 来源     | 内置（默认安装）                                        |
| 路径     | `skills/github/github-pr-workflow`                     |
| 版本     | `1.1.0`                                                |
| 作者     | Hermes Agent                                           |
| 许可证   | MIT                                                    |
| 平台     | linux, macos, windows                                  |
| 标签     | `GitHub`, `Pull-Requests`, `CI/CD`, `Git`, `Automation`, `Merge` |
| 相关技能 | [`github-auth`](/docs/user-guide/skills/bundled/github/github-github-auth), [`github-code-review`](/docs/user-guide/skills/bundled/github/github-github-code-review) |

## 参考：完整 SKILL.md (Reference: full SKILL.md)

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是代理在技能激活时看到的指令。
:::

# GitHub Pull Request 工作流 (GitHub Pull Request Workflow)

管理 PR 生命周期的完整指南。每个部分首先展示 `gh` 方式，然后展示在没有 `gh` 的机器上使用 `git` + `curl` 的备选方式。

## 前提条件 (Prerequisites)

- 已通过 GitHub 身份验证（参见 `github-auth` 技能）
- 位于具有 GitHub 远程仓库的 git 仓库内

### 快速身份验证检测 (Quick Auth Detection)

```bash
# Determine which method to use throughout this workflow
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  # Ensure we have a token for API calls
  if [ -z "$GITHUB_TOKEN" ]; then
    if _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"; [ -f "$_hermes_env" ] && grep -q "^GITHUB_TOKEN=" "$_hermes_env"; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$_hermes_env" | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi
echo "Using: $AUTH"
```

### 从 Git 远程仓库提取 Owner/Repo (Extracting Owner/Repo from the Git Remote)

许多 `curl` 命令需要 `owner/repo`。从 git 远程仓库中提取：

```bash
# Works for both HTTPS and SSH remote URLs
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
echo "Owner: $OWNER, Repo: $REPO"
```

---

--- body ---
## 1. 创建分支 (Branch Creation)

这部分是纯 `git` 操作——两种方式一致：

```bash
# Make sure you're up to date
git fetch origin
git checkout main && git pull origin main

# Create and switch to a new branch
git checkout -b feat/add-user-authentication
```

分支命名规范：
- `feat/description` — 新功能
- `fix/description` — 错误修复
- `refactor/description` — 代码重构
- `docs/description` — 文档
- `ci/description` — CI/CD 变更

## 2. 提交 (Making Commits)

使用代理的文件工具（`write_file`、`patch`）进行更改，然后提交：

```bash
# Stage specific files
git add src/auth.py src/models/user.py tests/test_auth.py

# Commit with a conventional commit message
git commit -m "feat: add JWT-based user authentication

- Add login/register endpoints
- Add User model with password hashing
- Add auth middleware for protected routes
- Add unit tests for auth flow"
```

提交消息格式（Conventional Commits）：
```
type(scope): short description

Longer explanation if needed. Wrap at 72 characters.
```

类型：`feat`、`fix`、`refactor`、`docs`、`test`、`ci`、`chore`、`perf`

## 3. 推送并创建 PR (Pushing and Creating a PR)

### 推送分支（方式一致）

```bash
git push -u origin HEAD
```

### 创建 PR

**使用 gh：**

```bash
gh pr create \
  --title "feat: add JWT-based user authentication" \
  --body "## Summary
- Adds login and register API endpoints
- JWT token generation and validation

## Test Plan
- [ ] Unit tests pass

Closes #42"
```

选项：`--draft`、`--reviewer user1,user2`、`--label "enhancement"`、`--base develop`

**使用 git + curl：**

```bash
BRANCH=$(git branch --show-current)

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{
    \"title\": \"feat: add JWT-based user authentication\",
    \"body\": \"## Summary\nAdds login and register API endpoints.\n\nCloses #42\",
    \"head\": \"$BRANCH\",
    \"base\": \"main\"
  }"
```

响应 JSON 包含 PR 的 `number`——保存以备后续命令使用。

要创建草稿，请在 JSON 体中添加 `"draft": true`。

## 4. 监控 CI 状态 (Monitoring CI Status)

### 检查 CI 状态

**使用 gh：**

```bash
# One-shot check
gh pr checks

# Watch until all checks finish (polls every 10s)
gh pr checks --watch
```

**使用 git + curl：**

```bash
# Get the latest commit SHA on the current branch
SHA=$(git rev-parse HEAD)

# Query the combined status
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Overall: {data['state']}\")
for s in data.get('statuses', []):
    print(f\"  {s['context']}: {s['state']} - {s.get('description', '')}\")"

# Also check GitHub Actions check runs (separate endpoint)
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/check-runs \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for cr in data.get('check_runs', []):
    print(f\"  {cr['name']}: {cr['status']} / {cr['conclusion'] or 'pending'}\")"
```

### 轮询直到完成（git + curl）

```bash
# Simple polling loop — check every 30 seconds, up to 10 minutes
SHA=$(git rev-parse HEAD)
for i in $(seq 1 20); do
  STATUS=$(curl -s \
    -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['state'])")
  echo "Check $i: $STATUS"
  if [ "$STATUS" = "success" ] || [ "$STATUS" = "failure" ] || [ "$STATUS" = "error" ]; then
    break
  fi
  sleep 30
done
```

## 5. 自动修复 CI 失败 (Auto-Fixing CI Failures)

当 CI 失败时，诊断并修复。此循环适用于两种身份验证方法。

### 步骤 1：获取失败详情

**使用 gh：**

```bash
# List recent workflow runs on this branch
gh run list --branch $(git branch --show-current) --limit 5

# View failed logs
gh run view <RUN_ID> --log-failed
```

**使用 git + curl：**

```bash
BRANCH=$(git branch --show-current)

# List workflow runs on this branch
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?branch=$BRANCH&per_page=5" \
  | python3 -c "
import sys, json
runs = json.load(sys.stdin)['workflow_runs']
for r in runs:
    print(f\"Run {r['id']}: {r['name']} - {r['conclusion'] or r['status']}\")"

# Get failed job logs (download as zip, extract, read)
RUN_ID=<run_id>
curl -s -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/logs \
  -o /tmp/ci-logs.zip
cd /tmp && unzip -o ci-logs.zip -d ci-logs && cat ci-logs/*.txt
```

### 步骤 2：修复并推送

识别问题后，使用文件工具（`patch`、`write_file`）进行修复：

```bash
git add <fixed_files>
git commit -m "fix: resolve CI failure in <check_name>"
git push
```

### 步骤 3：验证

使用第 4 节中的命令重新检查 CI 状态。

### 自动修复循环模式 (Auto-Fix Loop Pattern)

当要求自动修复 CI 时，遵循此循环：

1. 检查 CI 状态 → 识别失败
2. 读取失败日志 → 理解错误
3. 使用 `read_file` + `patch`/`write_file` → 修复代码
4. `git add . && git commit -m "fix: ..." && git push`
5. 等待 CI → 重新检查状态
6. 如果仍然失败则重复（最多尝试 3 次，然后询问用户）

## 6. 合并 (Merging)

**使用 gh：**

```bash
# Squash merge + delete branch (cleanest for feature branches)
gh pr merge --squash --delete-branch

# Enable auto-merge (merges when all checks pass)
gh pr merge --auto --squash --delete-branch
```

**使用 git + curl：**

```bash
PR_NUMBER=<number>

# Merge the PR via API (squash)
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/merge \
  -d "{
    \"merge_method\": \"squash\",
    \"commit_title\": \"feat: add user authentication (#$PR_NUMBER)\"
  }"

# Delete the remote branch after merge
BRANCH=$(git branch --show-current)
git push origin --delete $BRANCH

# Switch back to main locally
git checkout main && git pull origin main
git branch -d $BRANCH
```

合并方式：`"merge"`（合并提交）、`"squash"`、`"rebase"`

### 启用自动合并（curl）

```bash
# Auto-merge requires the repo to have it enabled in settings.
# This uses the GraphQL API since REST doesn't support auto-merge.
PR_NODE_ID=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['node_id'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/graphql \
  -d "{\"query\": \"mutation { enablePullRequestAutoMerge(input: {pullRequestId: \\\"$PR_NODE_ID\\\", mergeMethod: SQUASH}) { clientMutationId } }\"}"
```

## 7. 完整工作流示例 (Complete Workflow Example)

```bash
# 1. Start from clean main
git checkout main && git pull origin main

# 2. Branch
git checkout -b fix/login-redirect-bug

# 3. (Agent makes code changes with file tools)

# 4. Commit
git add src/auth/login.py tests/test_login.py
git commit -m "fix: correct redirect URL after login

Preserves the ?next= parameter instead of always redirecting to /dashboard."

# 5. Push
git push -u origin HEAD

# 6. Create PR (picks gh or curl based on what's available)
# ... (see Section 3)

# 7. Monitor CI (see Section 4)

# 8. Merge when green (see Section 6)
```

## 常用 PR 命令参考 (Useful PR Commands Reference)

| 操作 | gh | git + curl |
|--------|-----|-----------|
| 列出我的 PR | `gh pr list --author @me` | `curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$OWNER/$REPO/pulls?state=open"` |
| 查看 PR 差异 | `gh pr diff` | `git diff main...HEAD` (本地) 或 `curl -H "Accept: application/vnd.github.diff" ...` |
| 添加评论 | `gh pr comment N --body "..."` | `curl -X POST .../issues/N/comments -d '{"body":"..."}'` |
| 请求审阅 | `gh pr edit N --add-reviewer user` | `curl -X POST .../pulls/N/requested_reviewers -d '{"reviewers":["user"]}'` |
| 关闭 PR | `gh pr close N` | `curl -X PATCH .../pulls/N -d '{"state":"closed"}'` |
| 检出他人的 PR | `gh pr checkout N` | `git fetch origin pull/N/head:pr-N && git checkout pr-N` |