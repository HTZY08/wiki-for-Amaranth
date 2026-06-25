---
sidebar_position: 3
title: "托管作用域（Managed Scope）"
description: "通过系统级托管目录实现管理员锁定、用户不可变配置与密钥"
---

# 托管作用域（Managed Scope）

**托管作用域（Managed scope）** 允许管理员推送一份基线配置和密钥，普通（非 root）用户**无法覆盖**。它适用于需要在每台机器上锁定模型提供商、共享 API 基础 URL 或 `security.redact_secrets: true` 等设置的团队/组织部署。

当存在托管作用域时，它指定的值将胜过用户的 `~/.hermes/config.yaml`、`~/.hermes/.env`，甚至 shell 环境——但仅限于其锁定的键。其他所有配置仍完全由用户控制。

:::note 与包管理器锁定安装的区别
包管理器管理的安装（declarative-distro / formula）会阻止*所有*配置变更，并提示您使用包管理器。托管作用域是另一种机制：它按每个键注入*特定的不可变值*，而不是锁定整个配置。两者独立，可以共存。
:::

## 存放位置

托管作用域从系统级目录读取，默认为 `/etc/hermes`：

```text
/etc/hermes/
├── config.yaml     # 托管配置层（胜过 ~/.hermes/config.yaml）
└── .env            # 托管环境变量层（胜过 ~/.hermes/.env + shell）
```

该目录和文件由 `root` 拥有（目录模式 `0755`，文件 `0644`）：所有人可读，仅管理员可写。**该文件系统权限就是强制机制**——普通用户可以读取托管文件，但无法编辑它们。

任一文件都是可选的。缺少托管目录或文件仅表示“无托管作用域”，配置解析方式与没有此功能时完全相同。

### 更改目录位置

可通过环境变量 `HERMES_MANAGED_DIR` 更改位置（适用于容器或非 `/etc` 部署）。这是一个部署/引导路径旋钮——类似于 `HERMES_HOME`——由拥有托管文件的同一管理员设置。Hermes **绝不会**将其持久化到任何 `.env` 中。

```bash
# 将托管作用域指向自定义目录（由IT/部署设置，而非用户）
export HERMES_MANAGED_DIR=/opt/org/hermes-policy
```

:::warning
能够设置 `HERMES_MANAGED_DIR` 的用户可以将托管作用域重定向到其控制的目录，从而绕过它。在实际部署中，此变量应由管理员固定（例如，内置于服务单元/容器映像中），而不应由用户设置。`hermes doctor` 会报告*解析后的*托管目录，因此重定向是可见的。
:::

## 优先级

对于托管层指定的键，顺序如下（最高优先级获胜）：

| 层级 | config.yaml | .env |
|---|---|---|
| 1 | `/etc/hermes/config.yaml`（托管） | `/etc/hermes/.env`（托管） |
| 2 | `~/.hermes/config.yaml`（用户） | `~/.hermes/.env`（用户） |
| 3 | 内置默认值 | 预先存在的 shell 环境 |

合并是**叶子级别**的：锁定 `model.default` 并不会冻结 `model.*` 的其余部分。一个托管的 `config.yaml` 如下：

```yaml
model:
  default: org/standard-model
```

会强制每个用户的 `model.default` 为固定值，而 `model.fallback`（以及其他所有键）仍由用户控制。

:::note 优先级说明
对于其锁定的键，托管作用域特意胜过 shell 环境——否则就不能称为“托管”。这是唯一一个逆反通常的“环境变量覆盖 config.yaml”规则的地方，且仅适用于托管层指定的具体键。
:::

## 查看哪些内容被托管

```bash
hermes config        # 显示头部信息，指明托管来源 + 被锁定的键
hermes doctor        # 报告解析后的托管目录 + 被锁定的键数量
```

如果试图更改托管的值，Hermes 会拒绝并指明来源：

```bash
$ hermes config set model.default my/model
Cannot set 'model.default': it is managed by your administrator
(/etc/hermes/config.yaml) and cannot be changed.
```

对于托管的密钥（secrets）同样适用——`hermes config set` / setup 不会为托管 `.env` 锁定的环境变量键写入用户值。

## 设置托管作用域（管理员）

```bash
sudo mkdir -p /etc/hermes

# 为此机器上的每个用户锁定一些配置值
sudo tee /etc/hermes/config.yaml >/dev/null <<'YAML'
model:
  provider: nous
security:
  redact_secrets: true
YAML

# 可选：锁定一个共享的非敏感环境变量值
sudo tee /etc/hermes/.env >/dev/null <<'ENV'
OPENAI_API_BASE=https://inference.example.com/v1
ENV

sudo chmod 0755 /etc/hermes
sudo chmod 0644 /etc/hermes/config.yaml /etc/hermes/.env
```

更改在 Hermes 下次启动时生效（格式错误的托管文件会被强烈记录并忽略——它绝不会阻止启动，但管理员应检查 `hermes doctor` 以确认策略正在应用）。

## 安全模型与局限性（v1）

- **强制机制仅基于文件系统权限。** 如果用户对托管目录具有写权限（或以 `root` 身份运行 Hermes），则托管作用域仅为建议性。
- **托管的 `.env` 是全局可读的**（`0644`），因此任何本地用户都可以读取通过它推送的密钥。请将其用于共享的非敏感值（组织 API 基础 URL、功能默认值），而不是高敏感度的密钥。
- **代理自身的工具不会硬阻止托管的*环境变量*值。** 托管环境变量在启动时应用，但没有什么能阻止代理在其自身子进程 shell 内设置不同的值。v1 是针对普通用户的便捷管理边界，而非无法逃脱的沙箱。

以下内容在 **v1 中明确不在范围内**，可能会在后续版本中加入：

- 代理本身无法逃脱的硬边界。
- macOS 和 Windows 上的原生托管位置（v1 优先支持 Linux/POSIX）。
- 用于分层策略的 drop-in 片段目录（`managed.d/`）。
- 已签名/完整性检查的托管文件。
- 远程/设备管理（MDM）交付。
- 针对托管密钥的更严格（组作用域）权限。