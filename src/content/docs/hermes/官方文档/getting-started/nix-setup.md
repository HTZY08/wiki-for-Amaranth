--- frontmatter ---
---

## 更新

```bash
# 更新 flake 输入（在包含 flake.nix 的目录中运行）
cd /etc/nixos && nix flake update hermes-agent

# 重建
sudo nixos-rebuild switch
```

在容器模式下，`current-package` 符号链接会被更新，代理（Agent）在重启后会加载新的二进制文件。无需重建容器，也不会丢失已安装的软件包。

---

--- body ---
--- body ---
## 故障排除

:::tip Podman 用户
以下所有 `docker` 命令在 `podman` 中同样适用。如果你设置了 `container.backend = "podman"`，请相应替换。
:::

### 服务日志

```bash
# 两种模式使用相同的 systemd 单元
journalctl -u hermes-agent -f

# 容器模式：也可直接使用
docker logs -f hermes-agent
```

### 容器检查

```bash
systemctl status hermes-agent
docker ps -a --filter name=hermes-agent
docker inspect hermes-agent --format='{{.State.Status}}'
docker exec -it hermes-agent bash
docker exec hermes-agent readlink /data/current-package
docker exec hermes-agent cat /data/.container-identity
```

### 强制重建容器

如果需要重置可写层（全新的 Ubuntu）：

```bash
sudo systemctl stop hermes-agent
docker rm -f hermes-agent
sudo rm /var/lib/hermes/.container-identity
sudo systemctl start hermes-agent
```

### 验证密钥是否正确加载

如果代理（Agent）启动但无法与 LLM 提供商进行身份验证，请检查 `.env` 文件是否已正确合并：

```bash
# 原生模式
sudo -u hermes cat /var/lib/hermes/.hermes/.env

# 容器模式
docker exec hermes-agent cat /data/.hermes/.env
```

### GC 根检查

```bash
nix-store --query --roots $(docker exec hermes-agent readlink /data/current-package)
```

### 常见问题

| 症状 | 原因 | 解决方案 |
|---|---|---|
| `Cannot save configuration: managed by NixOS` | CLI 保护机制已激活 | 编辑 `configuration.nix` 并执行 `nixos-rebuild switch` |
| `No adapter available for discord`（或 telegram/slack） | 封闭的 Nix venv 中缺少消息传递依赖 | 安装 `#messaging` 变体：`nix profile install ...#messaging`。对于 NixOS 模块：`extraDependencyGroups = [ "messaging" ]`。检查 `journalctl -u hermes-agent` 中是否有 `FeatureUnavailable` 或 `requirements not met` 以获取底层错误信息。 |
| 容器被意外重建 | `extraVolumes`、`extraOptions` 或 `image` 发生更改 | 这是预期的行为——可写层会重置。重新安装软件包或使用自定义镜像 |
| `hermes version` 显示旧版本 | 容器未重启 | `systemctl restart hermes-agent` |
| 对 `/var/lib/hermes` 的权限被拒绝 | 状态目录的权限为 `0750 hermes:hermes` | 使用 `docker exec` 或 `sudo -u hermes` |
| `nix-collect-garbage` 移除了 hermes | GC 根丢失 | 重启服务（preStart 会重新创建 GC 根） |
| `no container with name or ID "hermes-agent"`（Podman） | 普通用户无法看到 Podman rootful 容器 | 为 podman 添加免密码 sudo（参见[容器模式](#容器模式)部分） |
| `unable to find user hermes` | 容器仍在启动中（entrypoint 尚未创建用户） | 等待几秒后重试——CLI 会自动重试 |
| 通过 `extraPackages` 添加的工具在终端中找不到 | 需要执行 `nixos-rebuild switch` 来更新用户级配置文件 | 重建并重启：`nixos-rebuild switch && systemctl restart hermes-agent` |