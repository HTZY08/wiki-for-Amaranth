--- frontmatter ---
---

### 方法 E：手动安装（高级/不受支持的硬件）

适用于昇腾 NPU、寒武纪 MLU、Intel Arc 或其他不受支持的硬件。

**文档：** https://docs.comfy.org/installation/manual_install

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu130
pip install -r requirements.txt
python main.py
```

---

--- body ---
### 安装后：下载模型

```bash
# SDXL（通用，约 6.5 GB）
comfy model download \
  --url "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" \
  --relative-path models/checkpoints

# SD 1.5（较轻量，约 4 GB，适合 6 GB 显卡）
comfy model download \
  --url "https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" \
  --relative-path models/checkpoints

# Flux Dev fp8（较小变体，约 12 GB）
comfy model download \
  --url "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors" \
  --relative-path models/checkpoints

# CivitAI（请先设置令牌）：
comfy model download \
  --url "https://civitai.com/api/download/models/128713" \
  --relative-path models/checkpoints \
  --set-civitai-api-token "YOUR_TOKEN"
```

查看已安装模型：`comfy model list`。

### 安装后：安装自定义节点

```bash
comfy node install comfyui-impact-pack             # 常用工具包
comfy node install comfyui-animatediff-evolved     # 视频生成
comfy node install comfyui-controlnet-aux          # ControlNet 预处理
comfy node install comfyui-essentials              # 通用辅助
comfy node update all
comfy node install-deps --workflow=workflow.json   # 安装工作流所需的所有依赖
```

### 安装后：验证

```bash
python3 scripts/health_check.py
# → 检查 comfy_cli 是否在 PATH 中？服务器是否可达？检查点是否存在？冒烟测试？

python3 scripts/check_deps.py my_workflow.json
# → 该工作流所需的节点/模型/嵌入是否已安装？

python3 scripts/run_workflow.py \
  --workflow workflows/sd15_txt2img.json \
  --args '{"prompt": "test", "steps": 4}' \
  --output-dir ./test-outputs
```

## 图像上传（img2img / 修复）

最简单的方法是使用 `run_workflow.py` 配合 `--input-image`：

```bash
python3 scripts/run_workflow.py \
  --workflow workflows/sdxl_img2img.json \
  --input-image image=./photo.png \
  --args '{"prompt": "make it cyberpunk", "denoise": 0.6}'
```

该标志会上传 `photo.png`，然后将其服务器端文件名注入到名为 `image` 的模式参数中。对于修复，请同时传入两者：

```bash
python3 scripts/run_workflow.py \
  --workflow workflows/sdxl_inpaint.json \
  --input-image image=./photo.png \
  --input-image mask_image=./mask.png \
  --args '{"prompt": "fill with flowers"}'
```

通过 REST 手动上传：
```bash
curl -X POST "http://127.0.0.1:8188/upload/image" \
  -F "image=@photo.png" -F "type=input" -F "overwrite=true"
# 返回：{"name": "photo.png", "subfolder": "", "type": "input"}

# 云端等效：
curl -X POST "https://cloud.comfy.org/api/upload/image" \
  -H "X-API-Key: $COMFY_CLOUD_API_KEY" \
  -F "image=@photo.png" -F "type=input" -F "overwrite=true"
```

## 云端特性

- **基础 URL：** `https://cloud.comfy.org`
- **认证：** `X-API-Key` 头部（或 WebSocket 使用 `?token=KEY`）
- **API 密钥：** 设置 `$COMFY_CLOUD_API_KEY` 一次，脚本会自动使用它
- **输出下载：** `/api/view` 返回 302 重定向到签名 URL；脚本会跟随重定向，并在从存储后端获取前去除 `X-API-Key`（不要向 S3/CloudFront 泄露 API 密钥）。
- **与本地 ComfyUI 的端点差异：**
  - `/api/object_info`、`/api/queue`、`/api/userdata` — **免费套餐返回 403**；仅付费可用。
  - `/history` 在云端重命名为 `/history_v2`（脚本会自动路由）。
  - `/models/<folder>` 在云端重命名为 `/experiment/models/<folder>`（脚本会自动路由）。
  - WebSocket 中的 `clientId` 当前被忽略——用户的所有连接都会收到相同的广播。请在客户端按 `prompt_id` 过滤。
  - 上传时接受 `subfolder` 但忽略——云端采用扁平命名空间。
- **并发任务数：** 免费/标准：1，创作者：3，专业：5。额外任务自动排队。使用 `run_batch.py --parallel N` 来充分利用你的套餐。

## 队列与系统管理

```bash
# 本地
curl -s http://127.0.0.1:8188/queue | python3 -m json.tool
curl -X POST http://127.0.0.1:8188/queue -d '{"clear": true}'    # 取消待处理任务
curl -X POST http://127.0.0.1:8188/interrupt                      # 中断正在运行的任务
curl -X POST http://127.0.0.1:8188/free \
  -H "Content-Type: application/json" \
  -d '{"unload_models": true, "free_memory": true}'

# 云端——在 `/api/` 下路径相同，此外：
python3 scripts/fetch_logs.py --tail-queue --host https://cloud.comfy.org
```

## 常见陷阱

1. **需要 API 格式** — 每个脚本和 `/api/prompt` 端点都期望 API 格式的工作流 JSON。脚本会检测编辑器格式（顶层包含 `nodes` 和 `links` 数组）并提示你通过“工作流 → 导出（API）”（较新 UI）或“保存（API 格式）”（较旧 UI）重新导出。

2. **服务器必须运行** — 所有执行都需要一个运行中的服务器。`comfy launch --background` 会启动一个服务器。使用 `curl http://127.0.0.1:8188/system_stats` 验证。

3. **模型名称必须精确** — 区分大小写，包含文件扩展名。`check_deps.py` 会进行模糊匹配（带/不带扩展名和文件夹前缀），但工作流本身必须使用规范名称。使用 `comfy model list` 查看已安装的模型。

4. **缺少自定义节点** — 出现“class_type not found”表示所需的节点未安装。`check_deps.py` 会报告需要安装哪个包；`auto_fix_deps.py` 会为你执行安装。

5. **工作目录** — `comfy-cli` 会自动检测 ComfyUI 工作空间。如果命令失败并提示“未找到工作空间”，请使用 `comfy --workspace /path/to/ComfyUI <command>` 或 `comfy set-default /path/to/ComfyUI`。

6. **云端免费套餐 API 限制** — `/api/prompt`、`/api/view`、`/api/upload/*`、`/api/object_info` 在免费账户中均返回 403。`health_check.py` 和 `check_deps.py` 会优雅地处理并显示清晰消息。

7. **视频/音频工作流的超时** — 当输出节点是 `VHS_VideoCombine`、`SaveVideo` 等时自动检测；默认从 300 秒增加到 900 秒。可以通过 `--timeout 1800` 显式覆盖。

8. **输出文件名中的路径遍历** — 服务器提供的文件名会通过 `safe_path_join` 处理，拒绝任何试图逃逸 `--output-dir` 的路径。请保持此保护启用——带有自定义保存节点的工作流可能产生任意路径。

9. **工作流 JSON 是任意代码** — 自定义节点运行 Python，因此提交未知工作流具有与 `eval` 相同的信任风险。在运行来自不可信来源的工作流之前，请先检查。

10. **自动随机种子** — 在 `--args` 中传递 `seed: -1`（或使用 `--randomize-seed` 并省略种子）可为每次运行获得新种子。实际种子会记录到 stderr。

11. **`tracking` 提示** — 首次运行 `comfy` 时可能会提示分析。使用 `comfy --skip-prompt tracking disable` 以非交互方式跳过。`comfyui_setup.sh` 已为你执行此操作。

## 验证检查清单

使用 `python3 scripts/health_check.py` 一次性运行整个列表。手动检查：

- [ ] `hardware_check.py` 结果为 `ok` 或用户明确选择 Comfy Cloud
- [ ] `comfy --version` 正常（或 `uvx --from comfy-cli comfy --help`）
- [ ] `curl http://HOST:PORT/system_stats` 返回 JSON
- [ ] `comfy model list` 显示至少一个检查点（本地）或 `/api/experiment/models/checkpoints` 返回模型（云端）
- [ ] 工作流 JSON 为 API 格式
- [ ] `check_deps.py` 报告 `is_ready: true`（或云端免费套餐中仅 `node_check_skipped`）
- [ ] 使用小工作流进行测试运行完成；输出文件出现在 `--output-dir` 中