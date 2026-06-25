---
title: Blender Mcp
---

title: "Blender Mcp — 通过 socket 连接 blender-mcp 插件，从 Hermes 直接控制 Blender"
sidebar_label: "Blender Mcp"
description: "通过 socket 连接 blender-mcp 插件，从 Hermes 直接控制 Blender"
---

--- body ---
{/* 此页面由脚本 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Blender Mcp

通过 socket 连接 blender-mcp 插件，从 Hermes 直接控制 Blender。创建 3D 对象、材质、动画，并运行任意 Blender Python (bpy) 代码。在用户想要在 Blender 中创建或修改任何内容时使用。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/creative/blender-mcp` 安装 |
| 路径 | `optional-skills/creative/blender-mcp` |
| 版本 | `1.0.0` |
| 作者 | alireza78a |
| 平台 | linux, macos, windows |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发该技能时加载的完整技能定义。这是技能激活时代理（agent）看到的指令。
:::

# Blender MCP

通过 TCP 端口 9876 上的 socket 从 Hermes 控制正在运行的 Blender 实例。

## 设置（一次性操作）

### 1. 安装 Blender 插件（addon）

    curl -sL https://raw.githubusercontent.com/ahujasid/blender-mcp/main/addon.py -o ~/Desktop/blender_mcp_addon.py

在 Blender 中：
    编辑（Edit）> 偏好设置（Preferences）> 插件（Add-ons）> 安装（Install）> 选择 blender_mcp_addon.py
    启用 "Interface: Blender MCP"

### 2. 在 Blender 中启动 socket 服务器

在 Blender 视口（viewport）中按 N 键打开侧边栏。
找到 "BlenderMCP" 标签并点击 "Start Server"。

### 3. 验证连接

    nc -z -w2 localhost 9876 && echo "OPEN" || echo "CLOSED"

## 协议（Protocol）

通过 TCP 传输纯 UTF-8 JSON，无长度前缀。

发送：    &#123;"type": "&lt;command>", "params": &#123;&lt;kwargs>&#125;&#125;
接收：    &#123;"status": "success", "result": &lt;value>&#125;
          &#123;"status": "error",   "message": "&lt;reason>"&#125;

## 可用命令（Available Commands）

| type                    | params            | description                     |
|-------------------------|-------------------|---------------------------------|
| execute_code            | code (str)        | 运行任意 bpy Python 代码        |
| get_scene_info          | (无)              | 列出场景中所有对象              |
| get_object_info         | object_name (str) | 特定对象的详细信息              |
| get_viewport_screenshot | (无)              | 当前视口的屏幕截图              |

## Python 帮助器（Python Helper）

可在 execute_code 工具调用中使用此代码：

    import socket, json

    def blender_exec(code: str, host="localhost", port=9876, timeout=15):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.settimeout(timeout)
        payload = json.dumps(&#123;"type": "execute_code", "params": &#123;"code": code&#125;&#125;)
        s.sendall(payload.encode("utf-8"))
        buf = b""
        while True:
            try:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buf += chunk
                try:
                    json.loads(buf.decode("utf-8"))
                    break
                except json.JSONDecodeError:
                    continue
            except socket.timeout:
                break
        s.close()
        return json.loads(buf.decode("utf-8"))

## 常见 bpy 模式（Common bpy Patterns）

### 清空场景
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

### 添加网格对象
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
    bpy.ops.mesh.primitive_cube_add(size=2, location=(3, 0, 0))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2, location=(-3, 0, 0))

### 创建并分配材质
    mat = bpy.data.materials.new(name="MyMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (R, G, B, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.3
    bsdf.inputs["Metallic"].default_value = 0.0
    obj.data.materials.append(mat)

### 关键帧动画
    obj.location = (0, 0, 0)
    obj.keyframe_insert(data_path="location", frame=1)
    obj.location = (0, 0, 3)
    obj.keyframe_insert(data_path="location", frame=60)

### 渲染到文件
    bpy.context.scene.render.filepath = "/tmp/render.png"
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.ops.render.render(write_still=True)

## 陷阱（Pitfalls）

- 必须在运行前检查 socket 是否打开（nc -z localhost 9876）
- 每次会话都需在 Blender 中启动插件服务器（N-panel > BlenderMCP > Connect）
- 将复杂场景拆分为多个较小的 execute_code 调用以避免超时
- 渲染输出路径必须为绝对路径（/tmp/...）而非相对路径
- shade_smooth() 要求对象被选中且处于对象模式（object mode）