--- frontmatter ---
---

## 高级主题（Advanced Topics）

### 协同部署模式（Co-located Deployment）

在训练和推理之间共享 GPU 以减少内存占用：

```bash
python train.py \
    --colocate \
    --actor-num-gpus-per-node 8 \
    --sglang-mem-fraction-static 0.4 \
    ${MODEL_ARGS[@]}
```

### 自定义奖励模型（Custom Reward Model）

```python
# custom_rm.py
class CustomRewardModel:
    def __init__(self, model_path):
        self.model = load_model(model_path)

    def compute_reward(self, prompts, responses):
        inputs = self.tokenize(prompts, responses)
        scores = self.model(inputs)
        return scores.tolist()
```

```bash
--custom-rm-path custom_rm.py
```

### 评估多任务（Evaluating Multiple Tasks）

```bash
--eval-prompt-data aime /path/to/aime.jsonl \
--eval-prompt-data gsm8k /path/to/gsm8k.jsonl \
--n-samples-per-eval-prompt 16
```

---

--- body ---
--- body ---
--- body ---
--- body ---
## 资源（Resources）

- **文档（Documentation）**: https://thudm.github.io/slime/
- **GitHub**: https://github.com/THUDM/slime
- **博客（Blog）**: https://lmsys.org/blog/2025-07-09-slime/
- **示例（Examples）**: 参见 `examples/` 目录，包含 14 个以上的完整示例