---
title: Installation
---

## 故障排除

| 问题 | 解决方法 |
|------|----------|
| `hermes: command not found` | 重新加载 shell（`source ~/.bashrc`）或检查 PATH |
| `API key not set` | 运行 `hermes model` 配置您的提供商，或运行 `hermes config set OPENROUTER_API_KEY your_key` |
| 更新后配置缺失 | 先运行 `hermes config check`，然后运行 `hermes config migrate` |

如需更多诊断信息，请运行 `hermes doctor` —— 它会准确告知您缺少什么以及如何修复。

## 安装方法自动检测

Hermes 会自动检测是通过 `pip`、git 安装器、Homebrew 还是 NixOS 安装的，并且 `hermes update` 会打印出对应路径的更新命令。无需设置环境变量——检测基于安装布局（Python site-packages、`~/.hermes/hermes-agent/`、Homebrew 前缀或 Nix 存储路径）。`hermes doctor` 也会在其环境摘要中显示检测到的方法。