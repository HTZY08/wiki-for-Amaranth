--- frontmatter ---


--- body ---
## 在没有 `gh` 的情况下使用 GitHub API

当 `gh` 不可用时，你仍然可以使用带有个人访问令牌（personal access token）的 `curl` 来访问完整的 GitHub API。这是其他 GitHub 技能（Skill）实现其回退（fallback）的方式。

### 为 API 调用设置令牌

```bash
# 选项 1：导出为环境变量（推荐——避免在命令中显式出现）
export GITHUB_TOKEN="<token>"

# 然后在 curl 调用中使用：
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

### 从 Git 凭据中提取令牌

如果 Git 凭据已经配置（通过 credential.helper store），可以提取令牌：

```bash
# 从 git 凭据存储中读取
grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|'
```

### 辅助：检测认证方式

在任何 GitHub 工作流的开头使用以下模式：

```bash
# 首先尝试 gh，如果失败则回退到 git + curl
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  echo "AUTH_METHOD=gh"
elif [ -n "$GITHUB_TOKEN" ]; then
  echo "AUTH_METHOD=curl"
elif _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"; [ -f "$_hermes_env" ] && grep -q "^GITHUB_TOKEN=" "$_hermes_env"; then
  export GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$_hermes_env" | head -1 | cut -d= -f2 | tr -d '\n\r')
  echo "AUTH_METHOD=curl"
elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
  export GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
  echo "AUTH_METHOD=curl"
else
  echo "AUTH_METHOD=none"
  echo "需要先设置认证方式"
fi
```

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `git push` 询问密码 | GitHub 已禁用密码认证。使用个人访问令牌（personal access token）作为密码，或切换到 SSH |
| `remote: Permission to X denied` | 令牌可能缺少 `repo` 范围（scope）——使用正确的范围重新生成 |
| `fatal: Authentication failed` | 缓存的凭据可能已过期——运行 `git credential reject`，然后重新认证 |
| `ssh: connect to host github.com port 22: Connection refused` | 尝试通过 HTTPS 端口使用 SSH：在 `~/.ssh/config` 中添加 `Host github.com`，并设置 `Port 443` 和 `Hostname ssh.github.com` |
| 凭据不持久保存 | 检查 `git config --global credential.helper`——必须是 `store` 或 `cache` |
| 多个 GitHub 账户 | 在 `~/.ssh/config` 中为每个主机别名使用不同的 SSH 密钥，或为每个仓库使用不同的凭据 URL |
| `gh: command not found` + 无 sudo 权限 | 使用上面的仅 Git 方法 1 ——无需安装 |