---
title: Termux
---

## 故障排除

### 安装 `.[all]` 时出现“未找到解决方案”

请改用经过测试的 Termux 包：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

目前的阻塞问题在于 `voice` 附加组件：
- `voice` 拉取了 `faster-whisper`
- `faster-whisper` 依赖于 `ctranslate2`
- `ctranslate2` 未发布 Android 版本的 wheel 包

### `uv pip install` 在 Android 上失败

请改用 Termux 路径，配合 stdlib venv + `pip`：

```bash
python -m venv venv
source venv/bin/activate
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

### `jiter` / `maturin` 报错关于 `ANDROID_API_LEVEL`

请在安装前显式设置 API 级别：

```bash
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

### `hermes doctor` 提示缺少 ripgrep 或 Node

请通过 Termux 包安装：

```bash
pkg install ripgrep nodejs
```

### 安装 Python 包时编译失败

请确保已安装构建工具链：

```bash
pkg install clang rust make pkg-config libffi openssl
```

然后重试：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

---

--- body ---
--- body ---
## 手机上的已知限制

- Docker 后端不可用
- 在测试路径下，通过 `faster-whisper` 进行的本地语音转录不可用
- 安装程序已有意跳过浏览器自动化设置
- 某些可选附加组件可能可以工作，但目前仅 `.[termux]` 和 `.[termux-all]` 被记录为经过测试的 Android 包

如果遇到新的 Android 特定问题，请提交 GitHub issue，并附上以下信息：
- 你的 Android 版本
- `termux-info` 输出
- `python --version` 输出
- `hermes doctor` 输出
- 完整的安装命令及错误输出