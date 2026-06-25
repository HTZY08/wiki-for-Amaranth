---
title: "Pokemon Player"
---

--- body ---

# 宝可梦玩家（Pokemon Player）

通过无头模拟器结合 RAM 读取来游玩宝可梦游戏。

## 技能元数据（Skill Metadata）

|          |                                                                   |
|----------|-------------------------------------------------------------------|
| 来源（Source）     | 可选 — 通过 `hermes skills install official/gaming/pokemon-player` 安装 |
| 路径（Path）     | `optional-skills/gaming/pokemon-player`                           |
| 平台（Platform）     | linux, macos, windows                                             |

## 参考：完整 SKILL.md（Reference: Full SKILL.md）

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这就是技能激活时代理所看到的指令。
:::

# 宝可梦玩家（Pokemon Player）

通过使用 `pokemon-agent` 包的无头模拟来游玩宝可梦游戏。

## 使用时机（When to use）
- 用户说“玩宝可梦”、“开始宝可梦”、“宝可梦游戏”
- 用户询问关于宝可梦红、蓝、黄、火红等版本
- 用户想观看 AI 玩宝可梦
- 用户引用 ROM 文件（.gb, .gbc, .gba）

## 启动流程（Launch Flow）

### 1. 首次设置（First-time setup：克隆、虚拟环境、安装）
仓库是 GitHub 上的 NousResearch/pokemon-agent。克隆它，然后
设置一个 Python 3.10+ 的虚拟环境。使用 uv（首选，速度快）
来创建虚拟环境并以可编辑模式安装包，附带
pyboy 附加组件。如果 uv 不可用，则回退到 python3 -m venv + pip。

在这台机器上，它已经设置在 /home/teknium/pokemon-agent
并带有一个准备好的虚拟环境 — 只需 cd 到那里并 source .venv/bin/activate。

你还需要一个 ROM 文件。向用户索要他们的。在这台机器上
该目录下存在一个 ROM 文件 roms/pokemon_red.gb。
永远不要下载或提供 ROM 文件 — 始终询问用户。

### 2. 启动游戏服务器（Start the game server）
在 pokemon-agent 目录内，激活虚拟环境后，运行
pokemon-agent serve，使用 --rom 指向 ROM 文件，并使用 --port 9876。
在后台运行，加上 &。
要恢复已保存的游戏，请添加 --load-state 并指定存档名称。
等待 4 秒启动时间，然后通过 GET /health 验证。

### 3. 为用户设置实时仪表盘（Set up live dashboard for the user）
通过 localhost.run 使用 SSH 反向隧道，以便用户可以在
浏览器中查看仪表盘。使用 ssh 连接，将本地端口 9876 转发到
远程端口 80，到 nokey@localhost.run。将输出重定向
到日志文件，等待 10 秒，然后 grep 日志以查找 .lhr.life
URL。向用户提供附加了 /dashboard/ 的 URL。
隧道 URL 每次都会更改 — 如果重新启动，请给用户新的 URL。

## 保存与加载（Saving & Loading）

### 何时保存（When to save）
- 每 15-20 步游戏操作
- 在道馆战、劲敌遭遇或危险战斗之前**务必**保存
- 进入新城镇或迷宫之前
- 在任何你不确定的行动之前

### 如何保存（How to save）
POST /save，并提供一个描述性名称。好的示例：
before_brock, route1_start, mt_moon_entrance, got_cut

### 如何加载（How to load）
POST /load，并指定存档名称。

### 列出可用存档（List available saves）
GET /saves 返回所有已保存的状态。

### 服务器启动时加载（Load on server start）
启动服务器时使用 --load-state 标志自动加载存档。
这比启动后通过 API 加载更快。

## 游戏循环（Game Loop）

### 步骤 1：观察（Observe） — 同时检查状态并截图
GET /state 获取位置、HP、战斗、对话信息。
GET /screenshot 并保存到 /tmp/pokemon.png，然后使用 vision_analyze。
始终两者都做 — RAM 状态提供数字，视觉提供空间感知。

### 步骤 2：定位（Orient）
- 屏幕上有对话/文本 → 推进它
- 战斗中 → 战斗或逃跑
- 队伍受伤 → 前往宝可梦中心
- 接近目标 → 小心导航

### 步骤 3：决策（Decide）
优先级：对话 > 战斗 > 治疗 > 故事目标 > 训练 > 探索

### 步骤 4：行动（Act） — 每次最多移动 2-4 步，然后重新检查
POST /action，包含一个简短的动作列表（2-4 个动作，不是 10-15 个）。

### 步骤 5：验证（Verify） — 每次移动序列后截图
截取屏幕截图并使用 vision_analyze 确认你移动到了
预期的位置。这是**最重要的**步骤。没有视觉，你**肯定会**迷路。

### 步骤 6：将进度记录到记忆，前缀为 PKM:

### 步骤 7：定期保存（Save periodically）

## 动作参考（Action Reference）
- press_a — 确认、对话、选择
- press_b — 取消、关闭菜单
- press_start — 打开游戏菜单
- walk_up/down/left/right — 移动一格
- hold_b_N — 按住 B N 帧（用于快速跳过文本）
- wait_60 — 等待约 1 秒（60 帧）
- a_until_dialog_end — 重复按 A 直到对话清除

## 来自经验的关键提示（Key Tips from Experience）

### 持续使用视觉（Use vision constantly）
- 每 2-4 个移动步骤截取一次屏幕截图
- RAM 状态告诉你位置和 HP，但**不是**你周围有什么
- 悬崖、围栏、标志、建筑物门、NPC — 只有通过截图才能看到
- 向视觉模型提出具体问题：“我北边一格是什么？”
- 当卡住时，在尝试随机方向之前始终截图

### 传送过渡需要额外等待时间（Teleport transitions need extra waits）
当走过一扇门或楼梯时，地图切换时屏幕会变黑。你**必须**等待它完成。在任何门/楼梯传送之后添加 2-3 个 wait_60 动作。如果不等待，位置读数会过时，你会认为你还在旧地图中。

### 建筑物出口陷阱（Building exit trap）
当你从建筑物出来时，你直接出现在门**前面**。
如果你向北走，你会直接回到建筑物里。**始终**先侧身走，
向左或向右走 2 格，然后继续你打算的方向。

### 对话处理（Dialog handling）
第一代文本逐个字母地缓慢滚动。要快速通过对话，
按住 B 120 帧然后按 A。根据需要重复。按住 B 可使
文本以最快速度显示。然后按 A 前进到下一行。
a_until_dialog_end 动作会检查 RAM 对话标志，但该标志
不会捕获**所有**文本状态。如果对话似乎卡住，请使用手动的
hold_b + press_a 模式，并通过截图验证。

### 悬崖是单向的（Cliffs are one-way）
悬崖（小悬崖边缘）只能向下跳（向南），永远不能向上爬
（向北）。如果向北被悬崖挡住，你必须向左或向右走
找到绕过它的缺口。使用视觉来确定哪个方向有
缺口。明确询问视觉模型。

### 导航策略（Navigation strategy）
- 一次移动 2-4 步，然后截图检查位置
- 进入新区域时，立即截图以定位
- 向视觉模型提问“去[目的地]往哪个方向？”
- 如果 3 次以上尝试后仍卡住，截图并完全重新评估
- 不要连续发送 10-15 次移动 — 你会走过头或卡住

### 从野生战斗中逃跑（Running from wild battles）
在战斗菜单中，逃跑在右下角。要从默认光标位置
（战斗，左上角）到达它：先按下再按右将光标移到
逃跑，然后按 A。结合 hold_b 来加快文本/动画速度。

### 战斗（攻击）（Battling (attack)）
在战斗菜单中，攻击在左上角（默认光标位置）。
按 A 进入招式选择，再按 A 使用第一个招式。
然后按住 B 来加快攻击动画和文本速度。

## 战斗策略（Battle Strategy）

### 决策树（Decision tree）
1. 想捕捉？ → 削弱后投掷宝可梦球
2. 不需要的野生？ → 逃跑
3. 有属性优势？ → 使用效果拔群的招式
4. 没有优势？ → 使用最强的本系加成招式
5. HP 低？ → 切换或使用伤药

### 第一代属性相克表（Key matchups in Gen 1）
- 水克制火、地面、岩石
- 火克制草、虫、冰
- 草克制水、地面、岩石
- 电克制水、飞行
- 地面克制火、电、岩石、毒
- 超能力克制格斗、毒（在第一代中占主导地位！）

### 第一代特殊机制（Gen 1 special mechanics）
- 特殊属性 = 特殊招式的**攻击和防御**（双倍作用）
- 超能力类型过于强大（幽灵招式有 bug）
- 会心一击基于速度属性
- 缠绕/绑紧阻止对手行动
- 聚焦能量 bug：**降低**会心率而不是提高

## 记忆约定（Memory Conventions）
| 前缀            | 用途             | 示例                                         |
|-----------------|------------------|----------------------------------------------|
| PKM:OBJECTIVE   | 当前目标         | 从真新镇宝可梦中心获得包裹                    |
| PKM:MAP         | 导航知识         | 常青市：宝可梦中心在东北                      |
| PKM:STRATEGY    | 战斗/队伍计划     | 需要在小霞之前获得草属性                      |
| PKM:PROGRESS    | 里程碑跟踪       | 击败劲敌，前往常青市                        |
| PKM:STUCK       | 卡住情况         | 在 y=28 的悬崖处向右绕过                     |
| PKM:TEAM        | 队伍笔记         | 杰尼龟 Lv6，撞击 + 摇尾巴                   |

## 进度里程碑（Progress Milestones）
- 选择初始宝可梦
- 从真新镇宝可梦中心递送包裹，获得图鉴
- 灰色徽章 — 小刚（岩石）→ 使用水/草
- 蓝色徽章 — 小霞（水）→ 使用草/电
- 黄色徽章 — 马志士（电）→ 使用地面
- 彩虹徽章 — 莉佳（草）→ 使用火/冰/飞行
- 灵魂徽章 — 阿桔（毒）→ 使用地面/超能力
- 沼泽徽章 — 娜姿（超能力）→ 最难的道馆
- 火山徽章 — 夏伯（火）→ 使用水/地面
- 大地徽章 — 坂木（地面）→ 使用水/草/冰
- 四大天王 → 冠军！

## 停止游戏（Stopping the game）
1. 通过 POST /save 使用描述性名称保存游戏
2. 使用 PKM:PROGRESS 更新记忆
3. 告诉用户：“游戏已保存为 [名称]！说‘玩宝可梦’即可继续。”
4. 终止服务器和隧道的后台进程

## 陷阱（Pitfalls）
- 永远不要下载或提供 ROM 文件
- 不要在未经视觉检查的情况下发送超过 4-5 个动作
- 从建筑物出来后，在向北走之前始终侧身
- 在门/楼梯传送后始终添加 wait_60 x2-3
- 通过 RAM 检测对话不可靠 — 使用截图验证
- 在危险遭遇之前**务必**保存
- 隧道 URL 每次重新启动都会更改