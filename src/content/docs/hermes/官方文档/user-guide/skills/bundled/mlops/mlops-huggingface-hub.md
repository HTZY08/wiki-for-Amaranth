--- frontmatter ---
---

## 专业化 Hub 交互

### 数据集（Datasets）与模型（Models）
*   **数据集（Datasets）：** `hf datasets list`、`info` 和 `parquet`（列出 parquet URL）。
*   **SQL 查询（SQL Queries）：** `hf datasets sql SQL` — 通过 DuckDB 对数据集 parquet URL 执行原始 SQL。
*   **模型（Models）：** `hf models list` 和 `info`。
*   **论文（Papers）：** `hf papers list` — 查看每日论文。

### 讨论（Discussions）与拉取请求（Pull Requests）（`hf discussions`）
*   管理 Hub 贡献的生命周期：`list`、`create`、`info`、`comment`、`close`、`reopen` 和 `rename`。
*   `diff`：查看 PR 中的变更。
*   `merge`：完成拉取请求。

### 基础设施与计算（Infrastructure & Compute）
*   **端点（Endpoints）：** 部署和管理推理端点（`deploy`、`pause`、`resume`、`scale-to-zero`、`catalog`）。
*   **任务（Jobs）：** 在 HF 基础设施上运行计算任务。包括用于运行带有内联依赖项的 Python 脚本的 `hf jobs uv`，以及用于资源监控的 `stats`。
*   **空间（Spaces）：** 管理交互式应用。包括无需完全重启即可用于 Python 文件的 `dev-mode` 和 `hot-reload`。

### 存储与自动化（Storage & Automation）
*   **存储桶（Buckets）：** 完整的 S3 风格存储桶管理（`create`、`cp`、`mv`、`rm`、`sync`）。
*   **缓存（Cache）：** 使用 `list`、`prune`（移除分离修订版本）和 `verify`（校验和检查）管理本地存储。
*   **Webhook（Webhooks）：** 通过管理 Hub Webhook 自动化工作流程（`create`、`watch`、`enable`/`disable`）。
*   **集合（Collections）：** 将 Hub 项目组织到集合中（`add-item`、`update`、`list`）。

---

---

## 高级用法与技巧

### 全局标志（Global Flags）
*   `--format json`：生成机器可读的输出，便于自动化。
*   `-q` / `--quiet`：仅输出 ID 以限制输出。

### 扩展（Extensions）与技能（Skills）
*   **扩展（Extensions）：** 通过 GitHub 仓库使用 `hf extensions install REPO_ID` 扩展 CLI 功能。
*   **技能（Skills）：** 使用 `hf skills add` 管理 AI 助手技能。