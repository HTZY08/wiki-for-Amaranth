---
title: Github Auth
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