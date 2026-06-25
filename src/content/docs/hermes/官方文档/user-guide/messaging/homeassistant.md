--- frontmatter ---
---
title: Home Assistant
description: 通过 Home Assistant 集成，使用 Hermes Agent 控制您的智能家居。
sidebar_label: Home Assistant
sidebar_position: 5
---

--- body ---
# Home Assistant 集成

Hermes Agent 通过两种方式与 [Home Assistant](https://www.home-assistant.io/) 集成：

1. **网关平台（Gateway platform）** — 通过 WebSocket 订阅实时状态变化并响应事件
2. **智能家居工具（Smart home tools）** — 四个可供 LLM 调用的工具，通过 REST API 查询和控制设备

## 设置

### 1. 创建长效访问令牌

1. 打开您的 Home Assistant 实例
2. 进入您的 **个人资料**（点击侧边栏中的您的名字）
3. 滚动至 **长效访问令牌（Long-Lived Access Tokens）**
4. 点击 **创建令牌（Create Token）**，为其命名，例如 "Hermes Agent"
5. 复制该令牌

### 2. 配置环境变量

```bash
# 添加到 ~/.hermes/.env

# 必需：您的长效访问令牌
HASS_TOKEN=your-long-lived-access-token

# 可选：HA URL（默认：http://homeassistant.local:8123）
HASS_URL=http://192.168.1.100:8123
```

:::info
当设置了 `HASS_TOKEN` 时，`homeassistant` 工具集将自动启用。网关平台和设备控制工具均通过此单一令牌激活。
:::

### 3. 启动网关

```bash
hermes gateway
```

Home Assistant 将作为一个已连接的平台出现，与其他消息平台（Telegram、Discord 等）并列。

## 可用工具

Hermes Agent 注册了四个用于智能家居控制的工具：

### `ha_list_entities`

列出 Home Assistant 实体，可按域或区域进行筛选。

**参数：**
- `domain` *(可选)* — 按实体域筛选：`light`、`switch`、`climate`、`sensor`、`binary_sensor`、`cover`、`fan`、`media_player` 等
- `area` *(可选)* — 按区域/房间名称筛选（匹配友好名称）：`living room`、`kitchen`、`bedroom` 等

**示例：**
```
列出客厅中的所有灯
```

返回实体 ID、状态和友好名称。

### `ha_get_state`

获取单个实体的详细状态，包括所有属性（亮度、颜色、温度设定点、传感器读数等）。

**参数：**
- `entity_id` *(必需)* — 要查询的实体，例如 `light.living_room`、`climate.thermostat`、`sensor.temperature`

**示例：**
```
climate.thermostat 的当前状态是什么？
```

返回：状态、所有属性、最后更改/更新时间戳。

### `ha_list_services`

列出用于设备控制的可用服务（动作）。显示每种设备类型可执行的动作及其接受的参数。

**参数：**
- `domain` *(可选)* — 按域筛选，例如 `light`、`climate`、`switch`

**示例：**
```
气候设备有哪些可用服务？
```

### `ha_call_service`

调用 Home Assistant 服务以控制设备。

**参数：**
- `domain` *(必需)* — 服务域：`light`、`switch`、`climate`、`cover`、`media_player`、`fan`、`scene`、`script`
- `service` *(必需)* — 服务名称：`turn_on`、`turn_off`、`toggle`、`set_temperature`、`set_hvac_mode`、`open_cover`、`close_cover`、`set_volume_level`
- `entity_id` *(可选)* — 目标实体，例如 `light.living_room`
- `data` *(可选)* — 以 JSON 对象形式提供的附加参数

**示例：**

```
打开客厅灯
→ ha_call_service(domain="light", service="turn_on", entity_id="light.living_room")
```

```
将恒温器设置为制热模式 22 度
→ ha_call_service(domain="climate", service="set_temperature",
    entity_id="climate.thermostat", data={"temperature": 22, "hvac_mode": "heat"})
```

```
将客厅灯设置为蓝色，亮度 50%
→ ha_call_service(domain="light", service="turn_on",
    entity_id="light.living_room", data={"brightness": 128, "color_name": "blue"})
```

## 网关平台：实时事件

Home Assistant 网关适配器通过 WebSocket 连接并订阅 `state_changed` 事件。当设备状态发生变化并符合您的筛选条件时，该事件将以消息形式转发给代理（Agent）。

### 事件筛选

:::warning 必需配置
默认情况下，**不会转发任何事件**。您必须至少配置 `watch_domains`、`watch_entities` 或 `watch_all` 中的一个，才能接收事件。若无筛选条件，启动时会记录警告日志，所有状态变化将被静默丢弃。
:::

在 `~/.hermes/config.yaml` 的 Home Assistant 平台 `extra` 部分下，配置代理（Agent）能看到哪些事件：

```yaml
platforms:
  homeassistant:
    enabled: true
    extra:
      watch_domains:
        - climate
        - binary_sensor
        - alarm_control_panel
        - light
      watch_entities:
        - sensor.front_door_battery
      ignore_entities:
        - sensor.uptime
        - sensor.cpu_usage
        - sensor.memory_usage
      cooldown_seconds: 30
```

| 设置 | 默认值 | 描述 |
|---------|---------|-------------|
| `watch_domains` | *(无)* | 仅监视这些实体域（例如 `climate`、`light`、`binary_sensor`） |
| `watch_entities` | *(无)* | 仅监视这些特定实体 ID |
| `watch_all` | `false` | 设置为 `true` 以接收 **所有** 状态变化（大多数设置不建议使用） |
| `ignore_entities` | *(无)* | 始终忽略这些实体（在域/实体筛选之前应用） |
| `cooldown_seconds` | `30` | 同一实体的两次事件之间的最小秒数 |

:::tip
从一组集中的域开始——`climate`、`binary_sensor` 和 `alarm_control_panel` 涵盖了最有用的自动化。根据需要添加更多。使用 `ignore_entities` 来抑制像 CPU 温度或运行时间计数器这类嘈杂的传感器。
:::

### 事件格式化

状态变化根据域格式化为人类可读的消息：

| 域 | 格式 |
|--------|--------|
| `climate` | "HVAC 模式从 'off' 变为 'heat'（当前：21，目标：23）" |
| `sensor` | "从 21°C 变为 22°C" |
| `binary_sensor` | "触发" / "清除" |
| `light`、`switch`、`fan` | "开启" / "关闭" |
| `alarm_control_panel` | "警报状态从 'armed_away' 变为 'triggered'" |
| *(其他)* | "从 '旧值' 变为 '新值'" |

### 代理响应

来自代理（Agent）的出站消息将以 **Home Assistant 持久通知（persistent_notification）** 的形式传递（通过 `persistent_notification.create`）。这些通知将出现在 HA 通知面板中，标题为 "Hermes Agent"。

### 连接管理

- **WebSocket**，带 30 秒心跳，用于实时事件
- **自动重连**，带退避策略：5 秒 → 10 秒 → 30 秒 → 60 秒
- **REST API**，用于出站通知（独立会话，避免 WebSocket 冲突）
- **授权** — HA 事件始终是授权的（无需用户允许列表，因为 `HASS_TOKEN` 对连接进行了身份验证）

## 安全

Home Assistant 工具强制执行安全限制：

:::warning 被阻止的域
以下服务域**被阻止**，以防止在 HA 主机上执行任意代码：

- `shell_command` — 任意 shell 命令
- `command_line` — 执行命令的传感器/开关
- `python_script` — 脚本化 Python 执行
- `pyscript` — 更广泛的脚本集成
- `hassio` — 插件控制、主机关闭/重启
- `rest_command` — 来自 HA 服务器的 HTTP 请求（SSRF 向量）

尝试调用这些域中的服务将返回错误。
:::

实体 ID 根据模式 `^[a-z_][a-z0-9_]*\.[a-z0-9_]+$` 进行验证，以防止注入攻击。

## 示例自动化

### 早晨例行程序

```
用户：开始我的早晨例行程序

代理：
1. ha_call_service(domain="light", service="turn_on",
     entity_id="light.bedroom", data={"brightness": 128})
2. ha_call_service(domain="climate", service="set_temperature",
     entity_id="climate.thermostat", data={"temperature": 22})
3. ha_call_service(domain="media_player", service="turn_on",
     entity_id="media_player.kitchen_speaker")
```

### 安全检查

```
用户：房子安全吗？

代理：
1. ha_list_entities(domain="binary_sensor")
     → 检查门/窗传感器
2. ha_get_state(entity_id="alarm_control_panel.home")
     → 检查警报状态
3. ha_list_entities(domain="lock")
     → 检查锁的状态
4. 报告："所有门已关闭，警报处于 armed_away 模式，所有锁已锁好。"
```

### 响应式自动化（通过网关事件）

当作为网关平台连接时，代理（Agent）可以响应事件：

```
[Home Assistant] 前门：触发（之前为清除）

代理自动：
1. ha_get_state(entity_id="binary_sensor.front_door")
2. ha_call_service(domain="light", service="turn_on",
     entity_id="light.hallway")
3. 发送通知："前门已打开。走廊灯已开启。"
```

## 故障排除

**环境变量未被读取。**
适配器从 `~/.hermes/.env`（启动时自动合并）或从 `config.yaml` 读取凭据。
请仔细检查该文件是否位于活动的 Hermes 配置文件主目录下，并且 URL/令牌周围没有多余引号。
编辑后重启网关——环境变量的更改仅在进程启动时生效。

**REST 认证失败（`401 Unauthorized`）。**
令牌必须是您在 HA 用户个人资料页面创建的**长效访问令牌**（**Profile → Security → Long-lived access tokens**）。短暂的 UI 会话令牌将不起作用。还要验证基本 URL 包含协议和端口（例如 `http://homeassistant.local:8123`），并且可从运行 Hermes 的主机访问——`curl -H "Authorization: Bearer <token>" <url>/api/` 应返回 `{"message": "API running."}`。