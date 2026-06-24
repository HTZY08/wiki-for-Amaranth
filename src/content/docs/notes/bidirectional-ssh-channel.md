---
title: 双向 SSH 互修通道搭建
description: 通过 Tailscale + SSH 打通云端与本地笔记本之间的双向修复通道
---

本文记录如何在一台本地笔记本（WSL2 + Docker）与一台腾讯云服务器之间建立双向免密 SSH 通道，实现云端能远程修复本地容器、本地也能管理云端。

## 背景

本地运行 Hermes Agent 的 Docker 容器（Amaranth）部署在笔记本 WSL2 上。云端有另一台 Hermes 实例（Begonia）跑在腾讯云服务器上，24h 在线。

问题是单向的——本地能 SSH 到云端修复，但云端访问不了本地（笔记本在内网，无公网 IP）。

## 架构

```
Begonia (腾讯云) ──Tailscale──→ Windows (Tailscale IP)
                                       │ 端口转发 2222→WSL:22
                                       ▼
                                  WSL (Ubuntu, Tailscale 节点)
                                       │ SSH 密钥认证
                                       ▼
                               Docker 容器 (Amaranth)
```

## 步骤

### 1. 确保 Windows 上有 Tailscale

Windows 安装 [Tailscale](https://tailscale.com/download) 并登录，确认获得 Tailscale IP。

### 2. WSL 内安装 Tailscale

```powershell
# PowerShell（管理员）
wsl -u root -d Ubuntu bash -c "curl -fsSL https://tailscale.com/install.sh | sh"
wsl -u root -d Ubuntu tailscale up
```

浏览器弹窗认证后，WSL 会获得一个独立的 Tailscale IP。

### 3. 启动 WSL SSH 服务

WSL SSH 默认不启用，需手动启动：

```powershell
wsl -u root -d Ubuntu service ssh start
```

也可设置开机自启，但 WSL 每次启动需手动触发 systemd。

### 4. 设置 Windows 端口转发

将 Windows 端口 2222 转发到 WSL 的 SSH 端口 22：

```powershell
wsl -u root -d Ubuntu hostname -I | % {
    $wsl_ip = $_.Trim()
    netsh interface portproxy delete v4tov4 listenport=2222 2>$null
    netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=2222 `
      connectaddress=$wsl_ip connectport=22
    Write-Host "转发: 0.0.0.0:2222 → ${wsl_ip}:22"
}
```

### 5. 部署 SSH 密钥

从 Docker 容器生成密钥对，公钥写入 WSL 的 `authorized_keys`：

```powershell
# 先查看公钥内容
cat ~/.ssh/id_ed25519.pub

# 将输出的公钥写入 WSL
wsl -u duhaotian -d Ubuntu bash -c "
  mkdir -p ~/.ssh &&
  echo 'ssh-ed25519 <你的公钥内容>' > ~/.ssh/authorized_keys &&
  chmod 600 ~/.ssh/authorized_keys
"
```

### 6. 修复容器内 SSH 的 IdentityFile 路径

Docker 容器内可能因 `$HOME` 环境变量与系统级 home 目录不一致，导致 SSH 找不到密钥。症状：SSH 报告 `no such identity`，路径指向错误目录。

**修复**：创建 `.ssh` 目录的软链接：

```bash
# 在容器内执行
rm -rf /opt/data/.ssh 2>/dev/null
ln -s /opt/data/home/.ssh /opt/data/.ssh
```

或修改 SSH 配置文件，使用绝对路径指定 IdentityFile。

### 7. 验证

```powershell
# 从 Docker 容器向 WSL SSH
ssh -o StrictHostKeyChecking=no duhaotian@<WSL_IP> "echo 通道通了"
```

## 全链路验证（从云端修本地）

1. 云端 Begonia SSH 到 Windows Tailscale IP（端口 2222）
2. Windows 端口转发到 WSL 22
3. WSL 内 `docker exec -it <容器名> bash` 进入容器

## 注意事项

- **WSL2 IP 会变化**：WSL 重启后内部 IP 可能改变，需重新设置端口转发
- **Tailscale IP 固定**：`100.x.x.x` 段不会变，适合作为稳定的连接入口
- **WSL SSH 服务不持久**：WSL 退出后 SSH 服务停止，需重新 `service ssh start`
- **Docker Desktop 状态**：若 Docker Desktop 崩溃，WSL 内的 Docker CLI 可能不可用，需重启 Docker Desktop
- **Windows 防火墙**：确保 Windows 防火墙放行 2222 端口的入站连接
- **防止密钥被覆盖**：`>` 覆盖写入会擦除已有公钥，如需保留应使用 `>>` 追加

## 参考

- [Tailscale 官方文档](https://tailscale.com/kb/)
- [WSL 网络配置](https://learn.microsoft.com/zh-cn/windows/wsl/networking)
