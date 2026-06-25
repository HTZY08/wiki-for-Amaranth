--- frontmatter ---
---
title: "Minecraft 模组包服务器 — 托管修改版 Minecraft 服务器（CurseForge、Modrinth）"
sidebar_label: "Minecraft Modpack Server"
description: "托管修改版 Minecraft 服务器（CurseForge、Modrinth）"
---

--- body ---
{/* 此页面由网站/脚本/generate-skill-docs.py 根据技能 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Minecraft 模组包服务器

托管修改版 Minecraft 服务器（CurseForge、Modrinth）。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/gaming/minecraft-modpack-server` 安装 |
| 路径 | `optional-skills/gaming/minecraft-modpack-server` |
| 平台 | linux, macos |

## 参考：完整 SKILL.md

:::info
以下为 Hermes 在触发该技能时加载的完整技能定义。即技能激活后代理（Agent）看到作为指令的内容。
:::

# Minecraft 模组包服务器搭建

## 何时使用
- 用户希望通过服务器包 zip 搭建一个模组版 Minecraft 服务器
- 用户需要 NeoForge/Forge 服务器配置帮助
- 用户询问关于 Minecraft 服务器性能调优或备份的问题

## 先收集用户偏好
开始搭建前，向用户询问以下信息：
- **服务器名称 / MOTD** — 服务器列表中应显示什么？
- **种子** — 指定种子还是随机？
- **难度** — 和平 / 简单 / 普通 / 困难？
- **游戏模式** — 生存 / 创造 / 冒险？
- **在线模式** — 开启（Mojang 认证，正版账号）或关闭（局域网/离线友好）？
- **玩家数量** — 预计有多少玩家？（影响内存与视距调优）
- **内存分配** — 或让代理根据模组数量与可用内存决定？
- **视距 / 模拟距离** — 或让代理根据玩家数量与硬件选择？
- **PvP** — 开启还是关闭？
- **白名单** — 开放服务器还是仅白名单？
- **备份** — 需要自动备份吗？频率如何？

如果用户不在意，使用合理的默认值，但生成配置前务必询问。

## 步骤

### 1. 下载并检查模组包
```bash
mkdir -p ~/minecraft-server
cd ~/minecraft-server
wget -O serverpack.zip "<URL>"
unzip -o serverpack.zip -d server
ls server/
```
查找以下文件：`startserver.sh`、安装程序 jar（neoforge/forge）、`user_jvm_args.txt`、`mods/` 文件夹。
检查脚本以确定：模组加载器类型、版本以及所需的 Java 版本。

### 2. 安装 Java
- Minecraft 1.21+ → Java 21：`sudo apt install openjdk-21-jre-headless`
- Minecraft 1.18-1.20 → Java 17：`sudo apt install openjdk-17-jre-headless`
- Minecraft 1.16 及以下 → Java 8：`sudo apt install openjdk-8-jre-headless`
- 验证：`java -version`

### 3. 安装模组加载器
大多数服务器包包含安装脚本。使用 `INSTALL_ONLY` 环境变量安装而不启动：
```bash
cd ~/minecraft-server/server
ATM10_INSTALL_ONLY=true bash startserver.sh
# 对于通用 Forge 包：
# java -jar forge-*-installer.jar --installServer
```
此过程会下载库文件、修补服务器 jar 等。

### 4. 接受 EULA
```bash
echo "eula=true" > ~/minecraft-server/server/eula.txt
```

### 5. 配置 server.properties
针对模组版/局域网的关键设置：
```properties
motd=\u00a7b\u00a7l服务器名称 \u00a7r\u00a78| \u00a7a模组包名
server-port=25565
online-mode=true          # 局域网无需 Mojang 认证时设为 false
enforce-secure-profile=true  # 与 online-mode 保持一致
difficulty=hard            # 多数模组包围绕困难模式平衡
allow-flight=true          # 模组版必须（飞行坐骑/物品）
spawn-protection=0         # 允许所有人在出生点建造
max-tick-time=180000       # 模组版需要更长的 tick 超时时间
enable-command-block=true
```

性能设置（根据硬件调整）：
```properties
# 2 名玩家，强力机器：
view-distance=16
simulation-distance=10

# 4-6 名玩家，中等机器：
view-distance=10
simulation-distance=6

# 8+ 名玩家或较弱硬件：
view-distance=8
simulation-distance=4
```

### 6. 调优 JVM 参数（user_jvm_args.txt）
根据玩家数量和模组数量调整内存。模组版经验法则：
- 100-200 个模组：6-12GB
- 200-350+ 个模组：12-24GB
- 至少为操作系统/其他任务保留 8GB 空闲内存

```
-Xms12G
-Xmx24G
-XX:+UseG1GC
-XX:+ParallelRefProcEnabled
-XX:MaxGCPauseMillis=200
-XX:+UnlockExperimentalVMOptions
-XX:+DisableExplicitGC
-XX:+AlwaysPreTouch
-XX:G1NewSizePercent=30
-XX:G1MaxNewSizePercent=40
-XX:G1HeapRegionSize=8M
-XX:G1ReservePercent=20
-XX:G1HeapWastePercent=5
-XX:G1MixedGCCountTarget=4
-XX:InitiatingHeapOccupancyPercent=15
-XX:G1MixedGCLiveThresholdPercent=90
-XX:G1RSetUpdatingPauseTimePercent=5
-XX:SurvivorRatio=32
-XX:+PerfDisableSharedMem
-XX:MaxTenuringThreshold=1
```

### 7. 开放防火墙
```bash
sudo ufw allow 25565/tcp comment "Minecraft 服务器"
```
验证：`sudo ufw status | grep 25565`

### 8. 创建启动脚本
```bash
cat > ~/start-minecraft.sh << 'EOF'
#!/bin/bash
cd ~/minecraft-server/server
java @user_jvm_args.txt @libraries/net/neoforged/neoforge/<VERSION>/unix_args.txt nogui
EOF
chmod +x ~/start-minecraft.sh
```
注意：对于 Forge（非 NeoForge），参数文件路径不同。请查看 `startserver.sh` 以获取准确路径。

### 9. 设置自动备份
创建备份脚本：
```bash
cat > ~/minecraft-server/backup.sh << 'SCRIPT'
#!/bin/bash
SERVER_DIR="$HOME/minecraft-server/server"
BACKUP_DIR="$HOME/minecraft-server/backups"
WORLD_DIR="$SERVER_DIR/world"
MAX_BACKUPS=24
mkdir -p "$BACKUP_DIR"
[ ! -d "$WORLD_DIR" ] && echo "[备份] 无世界文件夹" && exit 0
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="$BACKUP_DIR/world_${TIMESTAMP}.tar.gz"
echo "[备份] 开始于 $(date)"
tar -czf "$BACKUP_FILE" -C "$SERVER_DIR" world
SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "[备份] 已保存：$BACKUP_FILE ($SIZE)"
BACKUP_COUNT=$(ls -1t "$BACKUP_DIR"/world_*.tar.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
    REMOVE=$((BACKUP_COUNT - MAX_BACKUPS))
    ls -1t "$BACKUP_DIR"/world_*.tar.gz | tail -n "$REMOVE" | xargs rm -f
    echo "[备份] 已清理 $REMOVE 个旧备份"
fi
echo "[备份] 完成于 $(date)"
SCRIPT
chmod +x ~/minecraft-server/backup.sh
```

添加每小时定时任务：
```bash
(crontab -l 2>/dev/null | grep -v "minecraft/backup.sh"; echo "0 * * * * $HOME/minecraft-server/backup.sh >> $HOME/minecraft-server/backups/backup.log 2>&1") | crontab -
```

## 易错点
- 模组版**务必**设置 `allow-flight=true` — 否则带有喷气背包/飞行能力的模组会导致玩家被踢
- 设置 `max-tick-time=180000` 或更高 — 模组服务器在生成世界时常常有较长的 tick
- 首次启动**非常慢**（大型模组包需数分钟）— 不必惊慌
- 首次启动时出现“Can't keep up!”警告是正常的，初始化区块生成后会稳定
- 如果 `online-mode=false`，同时设置 `enforce-secure-profile=false`，否则客户端会被拒绝
- 模组包的 startserver.sh 通常带有自动重启循环 — 请编写一个不含此循环的干净启动脚本
- 删除 world/ 文件夹以使用新种子重新生成
- 某些模组包有控制行为的环境变量（例如 ATM10 使用 ATM10_JAVA、ATM10_RESTART、ATM10_INSTALL_ONLY）

## 验证
- 使用 `pgrep -fa neoforge` 或 `pgrep -fa minecraft` 检查是否在运行
- 查看日志：`tail -f ~/minecraft-server/server/logs/latest.log`
- 日志中出现“Done (Xs)!”表示服务器已就绪
- 测试连接：玩家在多人游戏中添加服务器 IP