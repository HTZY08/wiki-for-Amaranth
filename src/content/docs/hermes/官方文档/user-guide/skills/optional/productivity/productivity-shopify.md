--- frontmatter ---
---
title: "Shopify — 通过 curl 使用 Shopify Admin 与 Storefront GraphQL API"
sidebar_label: "Shopify"
description: "通过 curl 使用 Shopify Admin 与 Storefront GraphQL API"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */} 

# Shopify

通过 curl 使用 Shopify Admin 与 Storefront GraphQL API。产品、订单、客户、库存、元字段（metafields）。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源（Source） | 可选 —— 使用 `hermes skills install official/productivity/shopify` 安装 |
| 路径（Path） | `optional-skills/productivity/shopify` |
| 版本（Version） | `1.0.0` |
| 作者（Author） | community |
| 许可证（License） | MIT |
| 平台（Platforms） | linux, macos, windows |
| 标签（Tags） | `Shopify`, `E-commerce`, `Commerce`, `API`, `GraphQL` |
| 相关技能（Related skills） | [`airtable`](/docs/user-guide/skills/bundled/productivity/productivity-airtable), [`xurl`](/docs/user-guide/skills/bundled/social-media/social-media-xurl) |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是代理（agent）在技能激活时看到的指令。
:::

# Shopify — Admin 与 Storefront GraphQL API

直接通过 `curl` 操作 Shopify 商店：列出产品、管理库存、拉取订单、更新客户、读取元字段（metafields）。无需 SDK，无需应用框架——只需 GraphQL 端点和一个自定义应用访问令牌（access token）。

REST Admin API 自 2024-04 起已弃用，仅接收安全修复。**所有管理操作请使用 GraphQL Admin**。**使用 Storefront GraphQL** 进行面向客户的只读查询（产品、集合、购物车）。

## 先决条件（Prerequisites）

1. 在 Shopify 管理后台中：**设置 → 应用和销售渠道 → 开发应用 → 创建应用**。
2. 点击**配置 Admin API 作用域（scopes）**，选择你需要的内容（示例如下），保存。
3. **安装应用** → Admin API 访问令牌（Admin API access token）显示**一次**。立即复制——Shopify 不会再显示它。令牌以 `shpat_` 开头。
4. 保存至 `${HERMES_HOME:-~/.hermes}/.env`：
   ```
   SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxx
   SHOPIFY_STORE_DOMAIN=my-store.myshopify.com
   SHOPIFY_API_VERSION=2026-01
   ```

> **注意：** 自 2026 年 1 月 1 日起，在 Shopify 管理后台中创建的新的“旧版自定义应用（legacy custom apps）”已不可用。新设置应使用**开发者仪表板（Dev Dashboard）**（`shopify.dev/docs/apps/build/dev-dashboard`）。现有的管理后台创建的应用仍可继续使用。如果用户的商店没有现有的自定义应用且时间在 2026-01-01 之后，请引导他们使用 Dev Dashboard 而不是管理后台流程。

常见的作用域按任务划分：
- 产品 / 集合：`read_products`, `write_products`
- 库存：`read_inventory`, `write_inventory`, `read_locations`
- 订单：`read_orders`, `write_orders`（无 `read_all_orders` 时仅最近 30 条）
- 客户：`read_customers`, `write_customers`
- 草稿订单：`read_draft_orders`, `write_draft_orders`
- 履行：`read_fulfillments`, `write_fulfillments`
- 元字段（Metafields）/ 元对象（metaobjects）：由匹配的资源作用域覆盖

## API 基础（API Basics）

- **端点（Endpoint）：** `https://$SHOPIFY_STORE_DOMAIN/admin/api/$SHOPIFY_API_VERSION/graphql.json`
- **认证头（Auth header）：** `X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN`（**不是** `Authorization: Bearer`）
- **方法（Method）：** 始终为 `POST`，始终为 `Content-Type: application/json`，请求体为 `{"query": "...", "variables": {...}}`
- **HTTP 200 并不意味着成功。** GraphQL 在顶层 `errors` 数组和字段级 `userErrors` 中返回错误。请始终检查两者。
- **ID 是 GID 字符串：** `gid://shopify/Product/10079467700516`，`gid://shopify/Variant/...`，`gid://shopify/Order/...`。请原样传递——不要去掉前缀。
- **速率限制（Rate limit）：** 通过查询成本（漏桶算法）计算。每个响应包含 `extensions.cost`，其中有 `requestedQueryCost`、`actualQueryCost`、`throttleStatus.{currentlyAvailable, maximumAvailable, restoreRate}`。当 `currentlyAvailable` 低于下一个查询的成本时请退避。标准商店 = 100 点桶，50/s 恢复；Plus 商店 = 1000/100。

基础 curl 模式（可复用）：

```bash
shop_gql() {
  local query="$1"
  local variables="${2:-{}}"
  curl -sS -X POST \
    "https://${SHOPIFY_STORE_DOMAIN}/admin/api/${SHOPIFY_API_VERSION:-2026-01}/graphql.json" \
    -H "Content-Type: application/json" \
    -H "X-Shopify-Access-Token: ${SHOPIFY_ACCESS_TOKEN}" \
    --data "$(jq -nc --arg q "$query" --argjson v "$variables" '{query: $q, variables: $v}')"
}
```

通过 `jq` 管道输出可读结果。`-sS` 保持错误可见但隐藏进度条。

## 发现（Discovery）

### 商店信息 + 当前 API 版本
```bash
shop_gql '{ shop { name myshopifyDomain primaryDomain { url } currencyCode plan { displayName } } }' | jq
```

### 列出所有支持的 API 版本
```bash
shop_gql '{ publicApiVersions { handle supported } }' | jq '.data.publicApiVersions[] | select(.supported)'
```

## 产品（Products）

### 搜索产品（前 20 条匹配查询）
```bash
shop_gql '
query($q: String!) {
  products(first: 20, query: $q) {
    edges { node { id title handle status totalInventory variants(first: 5) { edges { node { id sku price inventoryQuantity } } } } }
    pageInfo { hasNextPage endCursor }
  }
}' '{"q":"hoodie status:active"}' | jq
```

查询语法支持 `title:`、`sku:`、`vendor:`、`product_type:`、`status:active`、`tag:`、`created_at:>2025-01-01`。完整语法：https://shopify.dev/docs/api/usage/search-syntax

### 分页产品（游标）
```bash
shop_gql '
query($cursor: String) {
  products(first: 100, after: $cursor) {
    edges { cursor node { id handle } }
    pageInfo { hasNextPage endCursor }
  }
}' '{"cursor":null}'
# 后续调用：传入上一次的 endCursor
```

### 获取产品及其变体与元字段（metafields）
```bash
shop_gql '
query($id: ID!) {
  product(id: $id) {
    id title handle descriptionHtml tags status
    variants(first: 20) { edges { node { id sku price compareAtPrice inventoryQuantity selectedOptions { name value } } } }
    metafields(first: 20) { edges { node { namespace key type value } } }
  }
}' '{"id":"gid://shopify/Product/10079467700516"}' | jq
```

### 创建一个带一个变体的产品
```bash
shop_gql '
mutation($input: ProductCreateInput!) {
  productCreate(product: $input) {
    product { id handle }
    userErrors { field message }
  }
}' '{"input":{"title":"Test Hoodie","status":"DRAFT","vendor":"Hermes","productType":"Apparel","tags":["test"]}}'
```

在最近的版本中，变体现在有自己的变更操作（mutations）：

```bash
# 创建产品后添加变体
shop_gql '
mutation($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkCreate(productId: $productId, variants: $variants) {
    productVariants { id sku price }
    userErrors { field message }
  }
}' '{"productId":"gid://shopify/Product/...","variants":[{"optionValues":[{"optionName":"Size","name":"M"}],"price":"49.00","inventoryItem":{"sku":"HD-M","tracked":true}}]}'
```

### 更新价格 / SKU
```bash
shop_gql '
mutation($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $productId, variants: $variants) {
    productVariants { id sku price }
    userErrors { field message }
  }
}' '{"productId":"gid://shopify/Product/...","variants":[{"id":"gid://shopify/ProductVariant/...","price":"55.00"}]}'
```

## 订单（Orders）

### 列出最近订单（默认无 `read_all_orders` 时仅最近 30 条）
```bash
shop_gql '
{
  orders(first: 20, reverse: true, query: "financial_status:paid") {
    edges { node {
      id name createdAt displayFinancialStatus displayFulfillmentStatus
      totalPriceSet { shopMoney { amount currencyCode } }
      customer { id displayName email }
      lineItems(first: 10) { edges { node { title quantity sku } } }
    } }
  }
}' | jq
```

有用的订单查询筛选条件：`financial_status:paid|pending|refunded`、`fulfillment_status:unfulfilled|fulfilled`、`created_at:>2025-01-01`、`tag:gift`、`email:foo@example.com`。

### 获取单个订单及其收货地址
```bash
shop_gql '
query($id: ID!) {
  order(id: $id) {
    id name email
    shippingAddress { name address1 address2 city province country zip phone }
    lineItems(first: 50) { edges { node { title quantity variant { sku } originalUnitPriceSet { shopMoney { amount currencyCode } } } } }
    transactions { id kind status amountSet { shopMoney { amount currencyCode } } }
  }
}' '{"id":"gid://shopify/Order/...."}' | jq
```

## 客户（Customers）

```bash
# 搜索
shop_gql '
{
  customers(first: 10, query: "email:*@example.com") {
    edges { node { id email displayName numberOfOrders amountSpent { amount currencyCode } } }
  }
}'

# 创建
shop_gql '
mutation($input: CustomerInput!) {
  customerCreate(input: $input) {
    customer { id email }
    userErrors { field message }
  }
}' '{"input":{"email":"test@example.com","firstName":"Test","lastName":"User","tags":["api-created"]}}'
```

## 库存（Inventory）

库存存在于与变体关联的**库存项（inventory items）**上，数量按**位置（location）**追踪。

```bash
# 获取变体在所有位置的库存
shop_gql '
query($id: ID!) {
  productVariant(id: $id) {
    id sku
    inventoryItem {
      id tracked
      inventoryLevels(first: 10) {
        edges { node { location { id name } quantities(names: ["available","on_hand","committed"]) { name quantity } } }
      }
    }
  }
}' '{"id":"gid://shopify/ProductVariant/..."}'
```

调整库存（增量）——使用 `inventoryAdjustQuantities`：

```bash
shop_gql '
mutation($input: InventoryAdjustQuantitiesInput!) {
  inventoryAdjustQuantities(input: $input) {
    inventoryAdjustmentGroup { reason changes { name delta } }
    userErrors { field message }
  }
}' '{
  "input": {
    "reason": "correction",
    "name": "available",
    "changes": [{"delta": 5, "inventoryItemId": "gid://shopify/InventoryItem/...", "locationId": "gid://shopify/Location/..."}]
  }
}'
```

设置绝对库存（非增量）——`inventorySetQuantities`：

```bash
shop_gql '
mutation($input: InventorySetQuantitiesInput!) {
  inventorySetQuantities(input: $input) {
    inventoryAdjustmentGroup { id }
    userErrors { field message }
  }
}' '{"input":{"reason":"correction","name":"available","ignoreCompareQuantity":true,"quantities":[{"inventoryItemId":"gid://shopify/InventoryItem/...","locationId":"gid://shopify/Location/...","quantity":100}]}}'
```

## 元字段（Metafields）与元对象（Metaobjects）

元字段（Metafields）将自定义数据附加到资源上（产品、客户、订单、商店）。

```bash
# 读取
shop_gql '
query($id: ID!) {
  product(id: $id) {
    metafields(first: 10, namespace: "custom") {
      edges { node { key type value } }
    }
  }
}' '{"id":"gid://shopify/Product/..."}'

# 写入（适用于任何拥有者类型）
shop_gql '
mutation($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields { id key namespace }
    userErrors { field message code }
  }
}' '{"metafields":[{"ownerId":"gid://shopify/Product/...","namespace":"custom","key":"care_instructions","type":"multi_line_text_field","value":"Wash cold. Tumble dry low."}]}'
```

## Storefront API（公共只读）

不同的端点，不同的令牌，用于面向客户的应用/hydrogen 风格的无头设置。标头不同：

- **端点（Endpoint）：** `https://$SHOPIFY_STORE_DOMAIN/api/$SHOPIFY_API_VERSION/graphql.json`
- **认证头（公共）：** `X-Shopify-Storefront-Access-Token: <公共令牌>` —— 可嵌入浏览器
- **认证头（私有）：** `Shopify-Storefront-Private-Token: <私有令牌>` —— 仅服务端

```bash
curl -sS -X POST \
  "https://${SHOPIFY_STORE_DOMAIN}/api/${SHOPIFY_API_VERSION:-2026-01}/graphql.json" \
  -H "Content-Type: application/json" \
  -H "X-Shopify-Storefront-Access-Token: ${SHOPIFY_STOREFRONT_TOKEN}" \
  -d '{"query":"{ shop { name } products(first: 5) { edges { node { id title handle } } } }"}' | jq
```

## 批量操作（Bulk Operations）

用于超出速率限制的数据转储（完整产品目录、一年的所有订单）：

```bash
# 1. 启动批量查询
shop_gql '
mutation {
  bulkOperationRunQuery(query: """
    { products { edges { node { id title handle variants { edges { node { sku price } } } } } } }
  """) {
    bulkOperation { id status }
    userErrors { field message }
  }
}'

# 2. 轮询状态
shop_gql '{ currentBulkOperation { id status errorCode objectCount fileSize url partialDataUrl } }'

# 3. 当状态为 COMPLETED 时，下载 JSONL 文件
curl -sS "$URL" > products.jsonl
```

每个 JSONL 行是一个节点，嵌套的连接作为单独的行发出，带有 `__parentId`。如果需要，可在客户端重新组装。

## Webhook

订阅事件以便无需轮询：

```bash
shop_gql '
mutation($topic: WebhookSubscriptionTopic!, $sub: WebhookSubscriptionInput!) {
  webhookSubscriptionCreate(topic: $topic, webhookSubscription: $sub) {
    webhookSubscription { id topic endpoint { __typename ... on WebhookHttpEndpoint { callbackUrl } } }
    userErrors { field message }
  }
}' '{"topic":"ORDERS_CREATE","sub":{"callbackUrl":"https://example.com/webhook","format":"JSON"}}'
```

使用应用的客户端密钥（client secret，非访问令牌）验证传入的 webhook HMAC：

```bash
echo -n "$REQUEST_BODY" | openssl dgst -sha256 -hmac "$APP_SECRET" -binary | base64
# 与 X-Shopify-Hmac-Sha256 标头比较
```

## 陷阱（Pitfalls）

- **REST 端点仍然存在但已冻结。** 不要针对 `/admin/api/.../products.json` 编写新的集成。请使用 GraphQL。
- **令牌格式检查。** Admin 令牌以 `shpat_` 开头。Storefront 公共令牌以 `shpua_` 开头。如果你有一个令牌但使用了错误的标头，每次请求都会返回 401，且没有有用的错误信息。
- **有效令牌但返回 403 = 缺少作用域。** Shopify 返回 `{"errors":[{"message":"Access denied for ..."}]}`。重新配置应用的 Admin API 作用域，然后重新安装以重新生成令牌。
- **`userErrors` 为空 ≠ 成功。** 还要检查 `data.<mutation>.<resource>` 是否为非空。某些失败不会填充任何一个——请检查整个响应。
- **GID 与数字 ID。** 旧的 REST 返回数字 ID；GraphQL 需要完整的 GID 字符串。转换方法：`gid://shopify/Product/<数字>`。
- **速率限制意外。** 单个 `products(first: 250)` 并深度嵌套可能消耗 1000+ 点，并在标准计划商店上立即触发限制。从窄范围开始，读取 `extensions.cost`，然后调整。
- **分页顺序。** `products(first: N, reverse: true)` 按 `id DESC` 排序，而非 `created_at`。如需“最新优先”，请使用 `sortKey: CREATED_AT, reverse: true`。
- **历史数据需要 `read_all_orders`。** 没有它，`orders(...)` 会静默限制在 60 天窗口内。你不会收到错误，只会比预期结果少。对于订单很多的 Shopify Plus 商户，请通过应用的保护数据设置请求此作用域。
- **货币是字符串。** 金额返回为 `"49.00"` 而不是 `49.0`。如果你关心零填充，请不要盲目使用 `jq tonumber`。
- **多货币 Money 字段**包含 `shopMoney`（商店的货币）和 `presentmentMoney`（客户的货币）。请保持一致使用其中一个。

## 安全性（Safety）

Shopify 中的变更操作（Mutations）是真实的——它们会创建产品、收取退款、取消订单、发货履行。在运行 `productDelete`、`orderCancel`、`refundCreate` 或任何批量变更之前：明确说明该更改是什么、在哪个商店上执行，并与用户确认。除非用户拥有单独的开发商店，否则不存在生产数据的暂存副本。