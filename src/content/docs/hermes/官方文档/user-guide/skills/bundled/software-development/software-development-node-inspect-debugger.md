---
title: "Node Inspect 调试器 — 调试 Node"
sidebar_label: "Node Inspect 调试器"
description: "调试 Node"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而不是此页面。 */}

# Node Inspect 调试器

通过 --inspect + Chrome DevTools Protocol CLI 调试 Node.js。

## 技能元数据

| | |
|---|---|
| 源 | 捆绑（默认已安装） |
| 路径 | `skills/software-development/node-inspect-debugger` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `debugging`, `nodejs`, `node-inspect`, `cdp`, `breakpoints`, `ui-tui` |
| 相关技能 | [`systematic-debugging`](/docs/user-guide/skills/bundled/software-development/software-development-systematic-debugging), [`python-debugpy`](/docs/user-guide/skills/bundled/software-development/software-development-python-debugpy), `debugging-hermes-tui-commands` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时代理所看到的指令。
:::

# Node.js Inspect 调试器

## 概述

当 `console.log` 不够用时，可以通过终端以编程方式驱动 Node 内置的 V8 检查器。你可以获得真正的断点、步入/步过/步出、调用栈遍历、局部/闭包作用域转储，以及在暂停帧中任意表达式求值。

两种工具，任选其一：

- **`node inspect`** — 内置，无需安装，CLI REPL。最适合快速探查。
- **`ndb` / CDP via `chrome-remote-interface`** — 可通过 Node/Python 编写脚本；当你想要自动化许多断点、跨运行收集状态或从代理循环中以非交互方式调试时，效果最佳。

**首选 `node inspect`。** 它始终可用且 REPL 快速。

## 何时使用

- 某个 Node 测试失败，你需要查看中间状态
- ui-tui 崩溃或行为异常，你需要在渲染前检查 React/Ink 状态
- tui_gateway 子进程（`_SlashWorker`、PTY 桥接工作进程）行为异常
- 你需要检查闭包中的某个值，而不用修补代码就无法通过 `console.log` 访问
- 性能分析：附加到正在运行的进程以捕获 CPU 概要或堆快照

**不要用于：** `console.log` 在一分钟内就能解决的事情。基于断点的调试开销更大；只有在真正有价值时才使用。

## 快速参考：`node inspect` REPL

在第一行暂停启动：

```bash
node inspect path/to/script.js
# or with tsx
node --inspect-brk $(which tsx) path/to/script.ts
```

`debug>` 提示符接受以下命令：

| 命令 | 操作 |
|---|---|
| `c` or `cont` | 继续 |
| `n` or `next` | 步过 |
| `s` or `step` | 步入 |
| `o` or `out` | 步出 |
| `pause` | 暂停运行中的代码 |
| `sb('file.js', 42)` | 在 file.js 第 42 行设置断点 |
| `sb(42)` | 在当前文件的第 42 行设置断点 |
| `sb('functionName')` | 当函数被调用时中断 |
| `cb('file.js', 42)` | 清除断点 |
| `breakpoints` | 列出所有断点 |
| `bt` | 回溯（调用栈） |
| `list(5)` | 显示当前位置周围的 5 行源码 |
| `watch('expr')` | 每次暂停时计算表达式 |
| `watchers` | 显示监视表达式 |
| `repl` | 进入当前作用域的 REPL（Ctrl+C 退出 REPL） |
| `exec expr` | 计算一次表达式 |
| `restart` | 重新启动脚本 |
| `kill` | 终止脚本 |
| `.exit` | 退出调试器 |

**在 `repl` 子模式下：** 输入任意 JS 表达式，包括访问局部/闭包变量。`Ctrl+C` 返回 `debug>`。

## 附加到正在运行的进程

当进程已经在运行时（例如，一个长时间运行的开发服务器或 TUI 网关）：

```bash
# 1. Send SIGUSR1 to enable the inspector on an existing process
kill -SIGUSR1 <pid>
# Node prints: Debugger listening on ws://127.0.0.1:9229/<uuid>

# 2. Attach the debugger CLI
node inspect -p <pid>
# or by URL
node inspect ws://127.0.0.1:9229/<uuid>
```

从一开始就启动带有检查器的进程：

```bash
node --inspect script.js           # listen on 127.0.0.1:9229, keep running
node --inspect-brk script.js       # listen AND pause on first line
node --inspect=0.0.0.0:9230 script.js   # custom host:port
```

对于通过 tsx 的 TypeScript：

```bash
node --inspect-brk --import tsx script.ts
# or older tsx
node --inspect-brk -r tsx/cjs script.ts
```

## 编程式 CDP（从终端编写脚本）

当你想要自动化时——设置多个断点、捕获作用域状态、编写复现脚本——使用 `chrome-remote-interface`：

```bash
npm i -g chrome-remote-interface        # or project-local
# Start your target:
node --inspect-brk=9229 target.js &
```

驱动程序脚本（保存为 `/tmp/cdp-debug.js`）：

```javascript
const CDP = require('chrome-remote-interface');

(async () => {
  const client = await CDP({ port: 9229 });
  const { Debugger, Runtime } = client;

  Debugger.paused(async ({ callFrames, reason }) => {
    const top = callFrames[0];
    console.log(`PAUSED: ${reason} @ ${top.url}:${top.location.lineNumber + 1}`);

    // Walk scopes for locals
    for (const scope of top.scopeChain) {
      if (scope.type === 'local' || scope.type === 'closure') {
        const { result } = await Runtime.getProperties({
          objectId: scope.object.objectId,
          ownProperties: true,
        });
        for (const p of result) {
          console.log(`  ${scope.type}.${p.name} =`, p.value?.value ?? p.value?.description);
        }
      }
    }

    // Evaluate an expression in the paused frame
    const { result } = await Debugger.evaluateOnCallFrame({
      callFrameId: top.callFrameId,
      expression: 'typeof state !== "undefined" ? JSON.stringify(state) : "n/a"',
    });
    console.log('state =', result.value ?? result.description);

    await Debugger.resume();
  });

  await Runtime.enable();
  await Debugger.enable();

  // Set a breakpoint by URL regex + line
  await Debugger.setBreakpointByUrl({
    urlRegex: '.*app\\.tsx$',
    lineNumber: 119,       // 0-indexed
    columnNumber: 0,
  });

  await Runtime.runIfWaitingForDebugger();
})();
```

运行它：

```bash
node /tmp/cdp-debug.js
```

特定于 Hermes 的说明：`chrome-remote-interface` 不在 `ui-tui/package.json` 中。如果你不想污染项目，可以将其安装到临时位置：

```bash
mkdir -p /tmp/cdp-tools && cd /tmp/cdp-tools && npm i chrome-remote-interface
NODE_PATH=/tmp/cdp-tools/node_modules node /tmp/cdp-debug.js
```

## 调试 Hermes ui-tui

TUI 由 Ink + tsx 构建。两种常见场景：

### 在开发模式下调试单个 Ink 组件

`ui-tui/package.json` 中有 `npm run dev` (tsx --watch)。通过直接运行 tsx 添加 `--inspect-brk`：

```bash
cd /home/bb/hermes-agent/ui-tui
npm run build    # produce dist/ once so transpile isn't needed on first load
node --inspect-brk dist/entry.js
# In another terminal:
node inspect -p <node pid>
```

然后在 `debug>` 内部：

```
sb('dist/app.js', 220)     # or wherever the suspect render is
cont
```

当它暂停时，`repl` → 检查 `props`、状态引用、`useInput` 处理程序值等。

### 调试正在运行的 `hermes --tui`

TUI 从 Python CLI 生成 Node 进程。最简单的路径：

```bash
# 1. Launch TUI
hermes --tui &
TUI_PID=$(pgrep -f 'ui-tui/dist/entry' | head -1)

# 2. Enable inspector on that Node PID
kill -SIGUSR1 "$TUI_PID"

# 3. Find the WS URL
curl -s http://127.0.0.1:9229/json/list | jq -r '.[0].webSocketDebuggerUrl'

# 4. Attach
node inspect ws://127.0.0.1:9229/<uuid>
```

与 TUI 交互（在其窗口中输入）将继续推进执行；你的调试器可以在任何 `sb(...)` 处将其暂停在断点上。

### 调试 `_SlashWorker` / PTY 子进程

这些是 Python 进程，而不是 Node 进程——请为它们使用 `python-debugpy` 技能。只有 Node 部分（Ink UI、tui_gateway 客户端、`ui-tui/` 下的 tsx-run 测试）使用此技能。

## 在调试器下运行 Vitest 测试

```bash
cd /home/bb/hermes-agent/ui-tui
# Run a single test file paused on entry
node --inspect-brk ./node_modules/vitest/vitest.mjs run --no-file-parallelism src/app/foo.test.tsx
```

在另一个终端中：`node inspect -p <pid>`，然后 `sb('src/app/foo.tsx', 42)`，`cont`。

使用 `--no-file-parallelism` (vitest) 或 `--runInBand` (jest) 以便只有一个工作进程存在——调试池是痛苦的。

## 堆快照和 CPU 概要（非交互式）

从上面的 CDP 驱动程序中，将 Debugger 替换为 `HeapProfiler` / `Profiler`：

```javascript
// CPU profile for 5 seconds
await client.Profiler.enable();
await client.Profiler.start();
await new Promise(r => setTimeout(r, 5000));
const { profile } = await client.Profiler.stop();
require('fs').writeFileSync('/tmp/cpu.cpuprofile', JSON.stringify(profile));
// Open /tmp/cpu.cpuprofile in Chrome DevTools → Performance tab
```

```javascript
// Heap snapshot
await client.HeapProfiler.enable();
const chunks = [];
client.HeapProfiler.addHeapSnapshotChunk(({ chunk }) => chunks.push(chunk));
await client.HeapProfiler.takeHeapSnapshot({ reportProgress: false });
require('fs').writeFileSync('/tmp/heap.heapsnapshot', chunks.join(''));
```

## 常见陷阱

1. **TS 源码中的错误行号。** 断点命中生成的 JS，而不是 `.ts`。要么 (a) 在构建后的 `dist/*.js` 中设置断点，要么 (b) 启用源映射（`node --enable-source-maps`）并使用 `sb('src/app.tsx', N)`——但仅适用于遵循源映射的 CDP 客户端。`node inspect` CLI 不遵循。

2. **`--inspect` vs `--inspect-brk`。** `--inspect` 启动检查器但不暂停；如果你的脚本附加太晚，它会在第一个断点之前运行完毕。当需要在任何代码运行之前设置断点时，请使用 `--inspect-brk`。

3. **端口冲突。** 默认为 `9229`。如果有多个 Node 进程在进行检查，传递 `--inspect=0`（随机端口）并从 `/json/list` 读取实际 URL：
   ```bash
   curl -s http://127.0.0.1:9229/json/list   # lists all inspectable targets on the host
   ```

4. **子进程。** 父进程上的 `--inspect` 不会检查其子进程。使用 `NODE_OPTIONS='--inspect-brk' node parent.js` 可以传播给每个子进程；请注意它们都需要唯一的端口（当继承了 `NODE_OPTIONS='--inspect'` 时，Node 会自动递增）。

5. **后台终止。** 如果在目标暂停时按 `Ctrl+C` 退出 `node inspect`，目标将保持暂停状态。要么先 `cont`，要么显式 `kill` 目标。

6. **通过代理终端运行 `node inspect`。** 这是一个 PTY 友好的 REPL。在 Hermes 中，使用 `terminal(pty=true)` 或 `background=true` + `process(action='submit', data='...')` 启动它。非 PTY 前台模式适用于一次性命令，但不适用于交互式步进。

7. **安全性。** `--inspect=0.0.0.0:9229` 暴露了任意代码执行。始终绑定到 `127.0.0.1`（默认），除非你有隔离网络。

## 验证检查表

设置调试会话后，验证：

- [ ] `curl -s http://127.0.0.1:9229/json/list` 返回你期望的目标
- [ ] 第一个断点实际命中了（如果没有，你可能忘记了 `--inspect-brk` 或附加时间晚于执行完成）
- [ ] 暂停时的源码列表显示正确的文件（不匹配 = 源映射问题，参见陷阱 1）
- [ ] `repl` 中的 `exec process.pid` 返回你打算附加的 PID

## 一次性配方

**“为什么这个变量在第 X 行是未定义的？”**
```bash
node --inspect-brk script.js &
node inspect -p $!
# debug>
sb('script.js', X)
cont
# paused. Now:
repl
> myVariable
> Object.keys(this)
```

**“进入这个函数的调用路径是什么？”**
```
debug> sb('suspectFn')
debug> cont
# paused on entry
debug> bt
```

**“这个异步链挂起了——在哪里？”**
```
# Start with --inspect (no -brk), let it run to the hang, then:
debug> pause
debug> bt
# Now you see the stuck frame
```