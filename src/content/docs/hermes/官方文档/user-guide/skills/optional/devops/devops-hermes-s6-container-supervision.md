--- frontmatter ---
---
title: "Hermes S6 容器监督"
sidebar_label: "Hermes S6 容器监督"
description: "修改、调试或扩展 Hermes Agent Docker 镜像内部的 s6-overlay 监督树——添加新服务、调试按配置文件（profile）的网关（gateway）、理解架构 B 的主程序模式。"
---

--- body ---

{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而不是此页面。 */}

# Hermes S6 容器监督

修改、调试或扩展 Hermes Agent Docker 镜像内部的 s6-overlay 监督树——添加新服务、调试按配置文件的网关、理解架构 B 的主程序模式。

## 技能元数据

| | |
|---|---|
| 来源 | 可选——使用 `hermes skills install official/devops/hermes-s6-container-supervision` 安装 |
| 路径 | `optional-skills/devops/hermes-s6-container-supervision` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux |
| 标签 | `docker`, `s6`, `supervision`, `gateway`, `profiles` |
| 相关技能 | [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent), `hermes-agent-dev` |

## 参考：完整 SKILL.md

:::info
以下为该技能触发时 Hermes 加载的完整技能定义。当技能激活时，代理（Agent）会看到这些指令。
:::

# Hermes s6-overlay 容器监督

## 何时使用此技能

当您处理以下工作时加载此技能：
- 在 Hermes Docker 镜像中添加或移除静态服务（每次容器启动时都应被监督，例如仪表板）
- 诊断为什么某个按配置文件的网关未能启动、重新启动或无法在 `docker restart` 后存活
- 理解为什么容器的 CMD 是 `/opt/hermes/docker/main-wrapper.sh`，以及前导短横线参数如何到达用户程序
- 修改 `cont-init.d` 启动脚本（UID 重映射、卷播种、配置文件协调）
- 更改按配置文件网关的渲染运行脚本（阶段 4）

如果您只是运行 Hermes Agent 并想使用 Docker，请参阅 `website/docs/user-guide/docker.md`。

## 架构概览

<!-- ascii-guard-ignore -->
```
/init                                  ← PID 1（s6-overlay v3.2.3.0）
├── cont-init.d                        ← 一次性设置，以 root 身份运行
│   ├── 01-hermes-setup                ← docker/stage2-hook.sh
│   │   ├── UID/GID 重映射
│   │   ├── chown /opt/data
│   │   ├── chown /opt/data/profiles（每次启动）
│   │   ├── 播种 .env / config.yaml / SOUL.md
│   │   └── skills_sync.py
│   └── 02-reconcile-profiles          ← hermes_cli.container_boot
│       ├── chown /run/service（对 hermes 可写，用于运行时注册）
│       └── 遍历 $HERMES_HOME/profiles/<name>/gateway_state.json
│           → 重新创建 /run/service/gateway-<name>/
│           → 仅自动启动那些 prior_state == "running" 的服务
│
├── s6-rc.d（静态服务，位于 /etc/s6-overlay/s6-rc.d/）
│   ├── main-hermes/run                ← exec sleep infinity（无操作占位）
│   └── dashboard/run                  ← 如果 HERMES_DASHBOARD=1，运行 `hermes dashboard`
│
├── /run/service（s6-svscan 监视；tmpfs）
│   ├── gateway-coder/                 ← 运行时注册的按配置文件服务
│   │   ├── type        ("longrun")
│   │   ├── run         ("#!/command/with-contenv sh ... exec s6-setuidgid hermes hermes -p coder gateway run")
│   │   ├── down        （标记——存在表示“已注册但不要自动启动”）
│   │   └── log/run     （s6-log → $HERMES_HOME/logs/gateways/coder/current）
│   └── ...
│
└── CMD（"主程序"）              ← /opt/hermes/docker/main-wrapper.sh
    └── 路由用户参数：bare exec | hermes 子命令 | hermes（无参数）
        — 由 /init 执行，继承 stdin/stdout/stderr（TTY 用于 --tui）
```
<!-- ascii-guard-ignore-end -->

## 关键文件

| 路径 | 角色 |
|---|---|
| `Dockerfile` | s6-overlay 安装 + cont-init.d 连接 + `ENTRYPOINT ["/init", "/opt/hermes/docker/main-wrapper.sh"]` |
| `docker/stage2-hook.sh` | "旧入口点逻辑"——UID 重映射、chown、播种、技能同步。作为 cont-init.d/01-hermes-setup 运行。 |
| `docker/cont-init.d/02-reconcile-profiles` | 每次启动时调用 `hermes_cli.container_boot`，从持久卷恢复配置文件网关插槽。 |
| `docker/main-wrapper.sh` | 容器的 CMD。路由用户参数，通过 `s6-setuidgid` 切换到 hermes，执行所选程序。 |
| `docker/s6-rc.d/main-hermes/run` | 无操作 `sleep infinity`——该插槽仅用于使 s6-rc 用户包有效；主 hermes 以 CMD 运行，而不是作为一个被监督的服务。 |
| `docker/s6-rc.d/dashboard/run` | 条件服务——除非 `HERMES_DASHBOARD` 为真，否则执行 `exec sleep infinity`。 |
| `docker/entrypoint.sh` | 向后兼容的垫片，执行 stage2 钩子。硬编码了旧入口点路径的外部脚本仍然可用。 |
| `hermes_cli/service_manager.py` | `S6ServiceManager`：`register_profile_gateway`、`unregister_profile_gateway`、`start/stop/restart/is_running`、`list_profile_gateways`。 |
| `hermes_cli/container_boot.py` | `reconcile_profile_gateways()`——遍历持久化的配置文件，重新生成 s6 插槽，输出 `container-boot.log`。 |
| `hermes_cli/gateway.py::_dispatch_via_service_manager_if_s6` | 拦截 `hermes gateway start/stop/restart` 命令，并在容器中运行时将其路由到 s6。 |

## 为什么选择架构 B（CMD 作为主程序，而非 s6 监督）

最初计划（v1–v3）是将主 hermes 作为受监督的 s6-rc 服务运行。两个实际的 s6-overlay v3 机制阻止了这一点：

1. **cont-init.d 脚本不接收 CMD 参数**——因此 stage2 钩子无法解析 `docker run <image> chat -q "hi"` 来设置供服务 `run` 脚本使用的 `HERMES_ARGS`。
2. **`/run/s6/basedir/bin/halt` 不会传播**写入到 `/run/s6-linux-init-container-results/exitcode` 的退出码。无论何种情况，容器始终以 143（SIGTERM）退出。这一论断在 skarnet（s6 作者）的 [issue #477](https://github.com/just-containers/s6-overlay/issues/477) 中得到确认：_"如果希望容器关闭，你需要要么让 CMD 退出，要么在没有 CMD 的情况下，写入你想要的容器退出码然后调用 halt"_。

因此我们使用 s6-overlay 原生的 CMD 模式：`ENTRYPOINT ["/init", "/opt/hermes/docker/main-wrapper.sh"]`。/init 会自动将包装器附加到用户参数之前——所以 `docker run <image> --version` 变成 `/init main-wrapper.sh --version`，而 `--version` 不会被 /init 的 POSIX shell 截获。包装器通过 `s6-setuidgid` 切换到 hermes，然后执行所选程序。程序的退出码成为容器的退出码，完全匹配之前使用 tini 的契约。

权衡：主 hermes 在 s6 下不受监督。这恰好匹配了其在 tini（即 s6 之前的镜像）下的行为。仪表板监督是唯一**新增**的保证——而 `/run/service/` 下的按配置文件网关则获得了完整的监督。

## 快速操作指南

### 在运行中的容器内验证 s6 是否为 PID 1

```sh
docker exec <c> sh -c 'cat /proc/1/comm; readlink /proc/1/exe'
# 期望输出：s6-svscan 或 init / /package/admin/s6/.../s6-svscan
```

### 检查某个配置文件网关服务

```sh
# /command/ 不在 docker-exec 的 PATH 中——请使用绝对路径
docker exec <c> /command/s6-svstat /run/service/gateway-<name>
# "up (pid …) … seconds"            → 运行中
# "down (exitcode N) … seconds, normally up, want up, …" → s6 希望它启动但进程不断退出（崩溃循环）
# "down … normally up, ready …"     → 用户停止了它
```

### 手动启动/停止服务

```sh
docker exec <c> /command/s6-svc -u /run/service/gateway-<name>   # 启动
docker exec <c> /command/s6-svc -d /run/service/gateway-<name>   # 停止
docker exec <c> /command/s6-svc -t /run/service/gateway-<name>   # SIGTERM（重启）
```

### 查看 cont-init 协调器日志

```sh
docker exec <c> tail -n 50 /opt/data/logs/container-boot.log
# 2026-05-21T06:18:05+0000 profile=coder prior_state=running action=started
# 2026-05-21T06:18:05+0000 profile=writer prior_state=stopped action=registered
```

### 添加一个新静态服务

1. 创建 `docker/s6-rc.d/<name>/type` 文件，内容为 `longrun\n`；创建 `docker/s6-rc.d/<name>/run`（使用 `#!/command/with-contenv sh` + `# shellcheck shell=sh`）。
2. 在 run 脚本顶部通过 `s6-setuidgid hermes` 切换到 hermes（除非明确需要 root 权限）。
3. 创建空文件 `docker/s6-rc.d/<name>/dependencies.d/base`，以便它等待基础包。
4. 创建空文件 `docker/s6-rc.d/<name>/contents.d/<name>`，以便它加入用户包。
5. Dockerfile 中的 `COPY docker/s6-rc.d/` 会自动将其纳入——无需其他更改。

### 更改按配置文件网关的运行命令

编辑 `hermes_cli/service_manager.py` 中的 `S6ServiceManager._render_run_script`。该函数也会在启动协调期间被 `hermes_cli/container_boot.py::_register_service` 调用，因此它是唯一的事实来源。相应地更新 `tests/hermes_cli/test_service_manager.py::test_s6_register_creates_service_dir_and_triggers_scan` 中的断言。

### 运行 Docker 测试工具集

```sh
docker build -t hermes-agent-harness:latest .
HERMES_TEST_IMAGE=hermes-agent-harness:latest scripts/run_tests.sh tests/docker/ -v
# 期望结果：19 passed，0 xfailed，针对 s6 镜像
```

测试工具集位于 `tests/docker/` 目录，当 Docker 不可用时自动跳过。每个测试的超时时间已提高至 180 秒（参见 `tests/docker/conftest.py`）。

## 常见陷阱

### 通过 `docker exec` 出现 "command not found"

`/command/`（s6-overlay 放置其二进制文件的位置）仅在由监督树产生的进程（服务、cont-init.d、main-wrapper.sh）的 PATH 中。`docker exec <c> s6-svstat …` 将失败并显示 "command not found"；始终使用绝对路径 `/command/s6-svstat`。`hermes` 二进制文件可以工作，因为 Dockerfile 将 `/opt/hermes/.venv/bin` 添加到了运行时的 `ENV PATH` 中。

### 配置文件目录所有权

cont-init 协调器以 hermes 用户身份运行（`02-reconcile-profiles` 中的 `s6-setuidgid hermes`）。如果某个配置文件目录最终属于 root（例如，因为 `docker exec <c> hermes profile create …` 默认以 root 身份运行），协调器将无法读取 SOUL.md 并失败并显示 `PermissionError`。缓解措施：`stage2-hook.sh` 在**每次**启动时幂等地将 `$HERMES_HOME/profiles` 的所有权更改为 hermes。不要删除该块。

### 由 `docker exec` 写入的文件归 root 所有

`docker exec` 默认以 root 身份运行。要么传入 `--user hermes`，要么依赖下一次重启时的 stage2 chown 扫描。不要手动以 root 身份在 `$HERMES_HOME/profiles/<name>/` 下写入文件——下一次协调过程会扫描它们，但正在进行的操作可能会遇到权限错误。

### 服务插槽存在但 s6-svstat 显示 "s6-supervise not running"

服务目录位于 tmpfs 上，在容器重启时已被清除。要么 cont-init 协调器尚未运行（`docker restart` 后稍等片刻），要么它失败了。检查 `docker logs <c> | grep '02-reconcile'`。

### 网关启动后立即退出（svstat 显示 `down (exitcode 1)`）

最可能的原因是配置文件没有配置模型或认证。服务插槽是正确的——网关本身未配置。先运行 `hermes -p <profile> setup`。s6 监督器会不断重启它；这是期望的行为（当你修复配置后，下一次尝试将成功并保持运行）。

### 协调器跳过了某个配置文件

协调器以 **`SOUL.md` 的存在**作为“真实配置文件”的标记。`hermes profile create` 总是播种该文件。如果某个配置文件目录缺少 SOUL.md（孤立目录、部分恢复、备份进行中），协调器会故意跳过它。添加一个 `SOUL.md`（即使为空）以重新加入协调。

### "救命，容器以 143 退出！"

检查是否有东西调用了 `s6-svscanctl -t` 或 `/run/s6/basedir/bin/halt`——两者都会导致 /init 开始阶段 3 关闭，但返回 143（SIGTERM）而不是期望的退出码。这是从架构 A 转向架构 B 的阶段 2 设计转折点。对于需要真实退出码的容器关闭，你必须让 CMD（main-wrapper.sh）正常退出；**不要**试图从 finish 脚本控制退出。

## 相关技能

- `hermes-agent-dev`：一般的 hermes-agent 代码库导航
- `hermes-tool-quirks`：特定的 Hermes 工具变通方法（sed/grep 等）——在调试 s6 栈与 hermes 内置工具的交互时加载。