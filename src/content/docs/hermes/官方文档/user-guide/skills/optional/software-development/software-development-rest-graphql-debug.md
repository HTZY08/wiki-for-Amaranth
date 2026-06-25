--- frontmatter ---
---
title: "Rest Graphql Debug — 调试 REST/GraphQL API：状态码、认证、模式、复现"
sidebar_label: "Rest Graphql Debug"
description: "调试 REST/GraphQL API：状态码、认证、模式、复现"
---

--- body ---

{/* 本页由 skill 的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。如要编辑，请修改源文件 SKILL.md，而非本页。 */}

# Rest Graphql Debug

调试 REST/GraphQL API：状态码、认证、模式、复现。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源（Source） | 可选——通过 `hermes skills install official/software-development/rest-graphql-debug` 安装 |
| 路径（Path） | `optional-skills/software-development/rest-graphql-debug` |
| 版本（Version） | `1.2.0` |
| 作者（Author） | eren-karakus0 |
| 许可证（License） | MIT |
| 标签（Tags） | `api`, `rest`, `graphql`, `http`, `debugging`, `testing`, `curl`, `integration` |
| 相关技能（Related skills） | [`systematic-debugging`](/docs/user-guide/skills/bundled/software-development/software-development-systematic-debugging), [`test-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-test-driven-development) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发该技能时加载的完整技能定义。这是技能激活时代理所看到的指令。
:::

# API 测试与调试

通过 Hermes 工具驱动 REST 和 GraphQL 诊断——使用 `terminal` 执行 `curl`，使用 `execute_code` 执行 Python `requests`，使用 `web_extract` 获取供应商文档。在猜测修复方案之前，先隔离出故障层。

## 何时使用

- API 返回意外的状态或响应体
- 认证失败（401/403，令牌刷新后、OAuth、API 密钥）
- 在 Postman 中正常工作但在代码中失败
- Webhook / 回调集成调试
- 构建或审查 API 集成测试
- 速率限制或分页问题

跳过 UI 渲染、数据库查询调优或 DNS/防火墙基础设施（升级处理）。

## 核心原则

**先隔离层，再修复。** 200 OK 可能掩盖错误的数据。500 可能隐藏一个字符的认证拼写错误。按顺序逐层检查，不要跳过任何步骤。

```
1. 连通性（Connectivity）     → 我们能否访问到主机？
1.5 超时（Timeouts）        → 连接慢还是读取慢？
2. TLS/SSL        → 证书有效且受信任？
3. 认证（Auth）           → 凭据正确且未过期？
4. 请求格式（Request format） → 请求体形状是否符合服务器期望？
5. 响应解析（Response parse） → 我们的代码能否接受返回的内容？
6. 语义（Semantics）       → 数据是否如我们假设的那样有意义？
```

## 5 分钟快速入门

### 通过终端调试 REST

```python
# 详细的请求/响应交互
terminal('curl -v https://api.example.com/users/1')

# 带 JSON 的 POST 请求
terminal("""curl -X POST https://api.example.com/users \\
  -H 'Content-Type: application/json' \\
  -H "Authorization: Bearer $TOKEN" \\
  -d '{"name":"test","email":"test@example.com"}'""")

# 仅获取响应头
terminal('curl -sI https://api.example.com/health')

# 格式化输出 JSON
terminal('curl -s https://api.example.com/users | python3 -m json.tool')
```

### 通过终端调试 GraphQL

```python
terminal("""curl -X POST https://api.example.com/graphql \\
  -H 'Content-Type: application/json' \\
  -H "Authorization: Bearer $TOKEN" \\
  -d '{"query":"{ user(id: 1) { name email } }"}'""")
```

**GraphQL 误区：**即使查询失败，服务器也经常返回 HTTP 200。始终检查 `errors` 字段，而不论状态码如何：

```python
execute_code('''
import os, requests
resp = requests.post(
    "https://api.example.com/graphql",
    json={"query": "{ user(id: 1) { name email } }"},
    headers={"Authorization": f"Bearer {os.environ['TOKEN']}"},
    timeout=10,
)
data = resp.json()
if data.get("errors"):
    for err in data["errors"]:
        print(f"GraphQL error: {err['message']} (path: {err.get('path')})")
print(data.get("data"))
''')
```

### 通过 execute_code 使用 Python（requests）

```python
execute_code('''
import requests
resp = requests.get(
    "https://api.example.com/users/1",
    headers={"Authorization": "Bearer <TOKEN>"},
    timeout=(3.05, 30),  # (连接超时, 读取超时)
)
print(resp.status_code, dict(resp.headers))
print(resp.text[:500])
''')
```

## 分层调试流程

### 第 1 步——连通性（Connectivity）

```python
terminal('nslookup api.example.com')
terminal('curl -v --connect-timeout 5 https://api.example.com/health')
```

失败原因：DNS 未解析、防火墙、需要 VPN、代理缺失。

### 第 1.5 步——超时（Timeouts）

区分*无法到达*与*能到达但缓慢*：

```python
terminal('''curl -w "dns:%{time_namelookup}s connect:%{time_connect}s tls:%{time_appconnect}s ttfb:%{time_starttransfer}s total:%{time_total}s\\n" \\
  -o /dev/null -s https://api.example.com/endpoint''')
```

在 Python 中，始终传递元组类型的超时参数——`requests` 没有默认超时，会永远挂起：

```python
execute_code('''
import requests
from requests.exceptions import ConnectTimeout, ReadTimeout
try:
    requests.get(url, timeout=(3.05, 30))
except ConnectTimeout:
    print("无法到达主机——DNS、防火墙、VPN")
except ReadTimeout:
    print("已连接但服务器响应慢")
''')
```

诊断：`time_connect` 高表示网络/防火墙问题；`time_connect` 低但 `time_starttransfer` 高表示服务器响应慢。

### 第 2 步——TLS/SSL

```python
terminal('curl -vI https://api.example.com 2>&1 | grep -E "SSL|subject|expire|issuer"')
```

失败原因：证书过期、自签名证书、主机名不匹配、缺少 CA 证书包。仅可临时调试使用 `-k`，绝不要在代码中使用。

### 第 3 步——认证（Authentication）

```python
# 令牌有效性检查
terminal('curl -s -o /dev/null -w "%{http_code}\\n" -H "Authorization: Bearer $TOKEN" https://api.example.com/me')

# 解码 JWT 的 exp 声明——正确处理 base64url 填充
execute_code('''
import json, base64, os
tok = os.environ["TOKEN"]
payload = tok.split(".")[1]
payload += "=" * (-len(payload) % 4)
print(json.dumps(json.loads(base64.urlsafe_b64decode(payload)), indent=2))
''')
```

检查清单：
- 令牌过期了吗？（JWT 中的 `exp` 声明）
- 认证方案正确吗？Bearer 还是 Basic 还是 Token 还是 `X-Api-Key`
- 环境正确吗？在产品环境使用测试密钥是常见错误
- API 密钥是放在请求头还是查询参数（`?api_key=…`）？

### 第 4 步——请求格式（Request Format）

```python
terminal("""curl -v -X POST https://api.example.com/endpoint \\
  -H 'Content-Type: application/json' \\
  -d '{"key":"value"}' 2>&1""")
```

**Content-Type 与请求体不匹配——静默的 415/400 错误：**

```python
# 错误——data= 发送 form-encoded 数据，但请求头声明为 JSON
requests.post(url, data='{"k":"v"}', headers={"Content-Type": "application/json"})

# 正确——json= 会自动设置请求头并序列化
requests.post(url, json={"k": "v"})

# 错误——Accept 声明为 XML，代码却调用 .json()
requests.get(url, headers={"Accept": "text/xml"})

# 正确——让 requests 自动构建 multipart 并生成边界
requests.post(url, files={"file": open("doc.pdf", "rb")})
```

常见问题：form-encoded 与 JSON 混淆、缺少必填字段、HTTP 方法错误、查询参数未编码。

### 第 5 步——响应解析（Response Parsing）

在调用 `.json()` 之前始终检查 content-type：

```python
execute_code('''
import requests
resp = requests.post(url, json=payload, timeout=10)
print(f"status={resp.status_code}")
print(f"headers={dict(resp.headers)}")
ct = resp.headers.get("Content-Type", "")
if "application/json" in ct:
    print(resp.json())
else:
    print(f"unexpected content-type {ct!r}, body={resp.text[:500]!r}")
''')
```

失败原因：预期 JSON 却收到 HTML 错误页面、空响应体、字符集错误。

### 第 6 步——语义验证（Semantic Validation）

解析正常——但数据*正确*吗？

- `"status": "active"` 是否与你的代码理解一致？
- 响应中的 ID 是否与请求的一致？
- 时间戳是否在预期的时区？
- 分页是否返回了所有结果，还是只返回了第一页？

## HTTP 状态码速查手册

### 401 未授权（Unauthorized）——缺少或无效的凭据

1. `Authorization` 请求头是否真的存在？（用 `curl -v` 确认）
2. 令牌是否正确且未过期？
3. 认证方案是否正确？（`Bearer` vs `Basic` vs `Token`）
4. 某些 API 使用查询参数（`?api_key=…`）代替请求头。

### 403 禁止（Forbidden）——已认证但未授权

1. 令牌具有所需的权限范围（scopes/permissions）吗？
2. 资源是否属于其他账户？
3. IP 白名单是否阻止了你？
4. 浏览器中的 CORS 问题？（检查 `Access-Control-Allow-Origin`）

### 404 未找到（Not Found）——资源不存在或 URL 错误

1. 路径是否正确？（尾部斜杠、拼写错误、版本前缀）
2. 资源 ID 是否存在？
3. API 版本是否正确（`/v1/` vs `/v2/`）？
4. 基础 URL 是否正确（测试环境 vs 产品环境）？

### 409 冲突（Conflict）——状态冲突

1. 资源已存在（重复创建）？
2. 过期的 `ETag` / `If-Match`？
3. 另一个进程并发修改？

### 422 不可处理的实体（Unprocessable Entity）——JSON 有效但数据无效

错误体通常会指明有问题的字段。检查：
- 字段类型（字符串 vs 整数，日期格式）
- 必填 vs 可选
- 枚举值是否在允许的集合内

### 429 请求过多（Too Many Requests）——被限流

检查 `Retry-After` 和 `X-RateLimit-*` 请求头。使用指数退避：

```python
execute_code('''
import time, requests

def with_backoff(method, url, **kwargs):
    for attempt in range(5):
        resp = requests.request(method, url, **kwargs)
        if resp.status_code != 429:
            return resp
        wait = int(resp.headers.get("Retry-After", 2 ** attempt))
        time.sleep(wait)
    return resp
''')
```

### 5xx——服务器端错误，通常不是你造成的

- **500**——服务器 bug。捕获关联 ID（correlation ID），向服务商提交。
- **502**——上游服务宕机。退避 + 重试。
- **503**——过载 / 维护中。检查服务状态页面。
- **504**——上游超时。减少请求体或增加超时时间。

针对所有 5xx：使用带抖动的退避策略，持续告警。

## 分页与幂等性

**分页。** 确认你获取了*所有*结果。查找 `next_cursor`、`next_page`、`total_count` 字段。两种模式：
- 偏移量（Offset）（`?limit=100&offset=200`）——简单，但数据变化时可能跳过条目。
- 游标（Cursor）（`?cursor=abc123`）——推荐用于实时或大型数据集。

**幂等性。** 对于非幂等操作（POST），发送 `Idempotency-Key: <uuid>`，以便重试不会重复计费/创建。支付和订单场景必须使用。

## 契约验证

在 schema 漂移进入产品环境之前捕获它：

```python
execute_code('''
import requests

def validate_user(data: dict) -> list[str]:
    errors = []
    required = {"id": int, "email": str, "created_at": str}
    for field, expected in required.items():
        if field not in data:
            errors.append(f"missing field: {field}")
        elif not isinstance(data[field], expected):
            errors.append(f"{field}: want {expected.__name__}, got {type(data[field]).__name__}")
    return errors

resp = requests.get(f"{BASE}/users/1", headers=HEADERS, timeout=10)
issues = validate_user(resp.json())
if issues:
    print(f"contract violations: {issues}")
''')
```

在 API 升级后、集成新第三方时，或 CI 冒烟测试中运行。

## 关联 ID（Correlation IDs）

始终捕获服务商提供的请求 ID——这是联系供应商支持的最快路径：

```python
execute_code('''
import requests
resp = requests.post(url, json=payload, headers=headers, timeout=10)
request_id = (
    resp.headers.get("X-Request-Id")
    or resp.headers.get("X-Trace-Id")
    or resp.headers.get("CF-Ray")  # Cloudflare
)
if resp.status_code >= 400:
    print(f"failed status={resp.status_code} req_id={request_id} ts={resp.headers.get('Date')}")
''')
```

**供应商 bug 报告模板：**

```
Endpoint:    POST /api/v1/orders
Request ID:  req_abc123xyz
Timestamp:   2026-03-17T14:30:00Z
Status:      500
Expected:    201 with order object
Actual:      500 {"error":"internal server error"}
Repro:       curl -X POST … (auth: <REDACTED>)
```

## 回归测试模板

将该模板放入 `tests/` 目录，并通过 `terminal('pytest tests/test_api_smoke.py -v')` 运行：

```python
import os, requests, pytest

BASE_URL = os.environ.get("API_BASE_URL", "https://api.example.com")
TOKEN    = os.environ.get("API_TOKEN", "")
HEADERS  = {"Authorization": f"Bearer {TOKEN}"}

class TestAPISmoke:
    def test_health(self):
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        assert resp.status_code == 200

    def test_list_users_returns_array(self):
        resp = requests.get(f"{BASE_URL}/users", headers=HEADERS, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data.get("data", data), list)

    def test_get_user_required_fields(self):
        resp = requests.get(f"{BASE_URL}/users/1", headers=HEADERS, timeout=10)
        assert resp.status_code in (200, 404)
        if resp.status_code == 200:
            user = resp.json()
            assert "id" in user and "email" in user

    def test_invalid_auth_returns_401(self):
        resp = requests.get(
            f"{BASE_URL}/users",
            headers={"Authorization": "Bearer invalid-token"},
            timeout=10,
        )
        assert resp.status_code == 401
```

## 安全

### 令牌处理
- 切勿记录完整的令牌。脱敏处理：`Bearer <REDACTED>`。
- 切勿在脚本中硬编码令牌。从环境变量（`os.environ["API_TOKEN"]`）或 `${HERMES_HOME:-~/.hermes}/.env` 中读取。
- 如果令牌出现在日志、错误消息或 git 历史中，立即轮换。

### 安全日志记录

```python
def redact_auth(headers: dict) -> dict:
    sensitive = {"authorization", "x-api-key", "cookie", "set-cookie"}
    return {k: ("<REDACTED>" if k.lower() in sensitive else v) for k, v in headers.items()}
```

### 泄露检查清单

- [ ] **URL 中的凭据。** 查询字符串中的 API 密钥会出现在服务器日志、浏览器历史、referrer 请求头中——应使用请求头。
- [ ] **错误响应中的 PII。** `404 on /users/123` 不应泄露用户是否存在（枚举）。
- [ ] **产品环境中的堆栈跟踪。** 500 错误不应泄露文件路径、框架版本。
- [ ] **内部主机名/IP。** `10.x.x.x`、`internal-api.corp.local` 出现在错误体中。
- [ ] **令牌被回显。** 某些 API 会在错误详情中包含认证令牌。确认它们不会。
- [ ] **详细的 `Server` / `X-Powered-By`。** 堆栈信息泄露。需安全审查注意。

## Hermes 工具模式

### terminal——用于 curl、dig、openssl

```python
terminal('curl -sI https://api.example.com')
terminal('openssl s_client -connect api.example.com:443 -servername api.example.com </dev/null 2>/dev/null | openssl x509 -noout -dates')
```

### execute_code——用于多步骤 Python 流程

当调试流程涉及认证 → 获取 → 分页 → 验证时，使用 `execute_code`。变量在脚本中持久化，结果输出到 stdout，不会在你的上下文中产生令牌垃圾：

```python
execute_code('''
import os, requests

token = os.environ["API_TOKEN"]
base  = "https://api.example.com"
H     = {"Authorization": f"Bearer {token}"}

# 1. 认证
me = requests.get(f"{base}/me", headers=H, timeout=10)
print(f"auth {me.status_code}")

# 2. 分页
all_users, cursor = [], None
while True:
    params = {"cursor": cursor} if cursor else {}
    r = requests.get(f"{base}/users", headers=H, params=params, timeout=10)
    body = r.json()
    all_users.extend(body["data"])
    cursor = body.get("next_cursor")
    if not cursor:
        break
print(f"users={len(all_users)}")
''')
```

### web_extract——用于供应商 API 文档

拉取正在调试的端点的规范，而不是猜测：

```python
web_extract(urls=["https://docs.example.com/api/v1/users"])
```

### delegate_task——用于完整的 CRUD 测试扫描

```python
delegate_task(
    goal="Test all CRUD endpoints for /api/v1/users",
    context="""
Follow the rest-graphql-debug skill (optional-skills/software-development/rest-graphql-debug).
Base URL: https://api.example.com
Auth: Bearer token from API_TOKEN env var.

For each verb (POST, GET, PATCH, DELETE):
  - happy path: assert status + response schema
  - error cases: 400, 404, 422
  - log a repro curl for any failure (redact tokens)

Output: pass/fail per endpoint + correlation IDs for failures.
""",
    toolsets=["terminal", "file"],
)
```

## 输出格式

报告发现时：

```
## Finding
Endpoint: POST /api/v1/users
Status:   422 Unprocessable Entity
Req ID:   req_abc123xyz

## Repro
curl -X POST https://api.example.com/api/v1/users \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <REDACTED>' \
  -d '{"name":"test"}'

## Root Cause
Missing required field `email`. Server validation rejects before processing.

## Fix
-d '{"name":"test","email":"test@example.com"}'
```

## 相关技能

- `systematic-debugging`——一旦隔离出故障的 API 层，进一步排查代码根因
- `test-driven-development`——在部署修复之前编写回归测试