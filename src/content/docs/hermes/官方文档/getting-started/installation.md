---
## 非 Sudo / 系统服务用户安装

支持将 Hermes 作为专用非特权用户（例如 `hermes` systemd 服务账户，或任何没有 `sudo` 权限的用户）运行。在安装路径中，唯一真正需要 root 权限的是 Playwright 的 `--with-deps` 步骤，该步骤会通过 `apt` 安装 Chromium 所需的共享库（`libnss3`、`libxkbcommon` 等）。安装程序会检测 sudo 是否可用，并在不可用时优雅降级——它会在服务用户自己的 Playwright 缓存中安装 Chromium 二进制文件，并打印出管理员需要单独运行的确切命令。

**推荐的分步安装（Debian/Ubuntu）：**

1. **一次性，由拥有 sudo 权限的管理员用户**安装 Chromium 所需的系统库：
   ```bash
   sudo npx playwright install-deps chromium
   ```
   （可以从任何位置运行此命令 — `npx` 会即时获取 Playwright。）

2. **作为非特权服务用户**，运行常规安装程序。它会检测到缺少 sudo，跳过 `--with-deps`，并将 Chromium 安装到用户的本地 Playwright 缓存中：
   ```bash
   curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
   ```

   如果您想完全跳过 Playwright 步骤——例如因为您运行在无头模式下且不需要浏览器自动化——请传入 `--skip-browser`：
   ```bash
   curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-browser
   ```

3. **将 `hermes` 添加到服务用户的 shell 环境变量中**。安装程序会将启动器写入 `~/.local/bin/hermes`。系统服务账户通常具有最小的 PATH，不包含 `~/.local/bin`。可以将其添加到用户的环境中，或者将启动器符号链接到系统位置：
   ```bash
   # 选项 A — 添加到服务用户的 profile 中
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

   # 选项 B — 系统级符号链接（由管理员运行）
   sudo ln -s /home/hermes/.hermes/hermes-agent/venv/bin/hermes /usr/local/bin/hermes
   ```

4. **验证：** 此时运行 `hermes doctor` 应该会输出正常。如果出现 `ModuleNotFoundError: No module named 'dotenv'`，说明您是用系统 Python 调用了仓库源文件 `hermes`（`~/.hermes/hermes-agent/hermes`），而不是使用 venv 启动器（`~/.hermes/hermes-agent/venv/bin/hermes`）—— 请修正步骤 3。

同样的模式在 Arch 上也能使用（安装程序使用 pacman，并采用相同的 sudo 检测逻辑）、Fedora/RHEL 和 openSUSE 上也是如此——这些发行版根本不支持 `--with-deps`，因此管理员需要单独安装系统库。相应的 `dnf`/`zypper` 命令会由安装程序打印出来。

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