---
title: Pytorch Lightning
---

title: "PyTorch Lightning 框架"
sidebar_label: "PyTorch Lightning"
description: "高级 PyTorch 框架，包含 Trainer 类、自动分布式训练（DDP/FSDP/DeepSpeed）、回调系统，以及极少的样板代码。同一份代码可从笔记本扩展到超级计算机。当您希望使用内置最佳实践来编写简洁的训练循环时，请使用它。"
---

--- body ---
{/* 此页面由 skill 的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

# PyTorch Lightning 框架

高级 PyTorch 框架，包含 Trainer 类、自动分布式训练（DDP/FSDP/DeepSpeed）、回调系统，以及极少的样板代码。同一份代码可从笔记本扩展到超级计算机。当您希望使用内置最佳实践来编写简洁的训练循环时，请使用它。

## Skill 元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/pytorch-lightning` 安装 |
| 路径 | `optional-skills/mlops/pytorch-lightning` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可 | MIT |
| 依赖 | `lightning`, `torch`, `transformers` |
| 平台 | linux, macos, windows |
| 标签 | `PyTorch Lightning`, `训练框架`, `分布式训练`, `DDP`, `FSDP`, `DeepSpeed`, `高级 API`, `回调`, `最佳实践`, `可扩展` |

## 参考：完整 SKILL.md

:::info
以下是触发此 skill 时 Hermes 加载的完整技能定义。这是 agent 在 skill 激活时看到的指令。
:::

# PyTorch Lightning - 高级训练框架

## 快速开始

PyTorch Lightning 组织 PyTorch 代码以消除样板代码，同时保持灵活性。

**安装**：
```bash
pip install lightning
```

**将 PyTorch 转换为 Lightning**（三步）：

```python
import lightning as L
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

# 第 1 步：定义 LightningModule（组织您的 PyTorch 代码）
class LitModel(L.LightningModule):
    def __init__(self, hidden_size=128):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(28 * 28, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 10)
        )

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self.model(x)
        loss = nn.functional.cross_entropy(y_hat, y)
        self.log('train_loss', loss)  # 自动记录到 TensorBoard
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=1e-3)

# 第 2 步：创建数据
train_loader = DataLoader(train_dataset, batch_size=32)

# 第 3 步：使用 Trainer 训练（处理其他所有事情！）
trainer = L.Trainer(max_epochs=10, accelerator='gpu', devices=2)
model = LitModel()
trainer.fit(model, train_loader)
```

**就是这样！** Trainer 负责处理：
- GPU/TPU/CPU 切换
- 分布式训练（DDP, FSDP, DeepSpeed）
- 混合精度（FP16, BF16）
- 梯度累积
- 检查点保存
- 日志记录
- 进度条

## 常见工作流

### 工作流 1：从 PyTorch 到 Lightning

**原始 PyTorch 代码**：
```python
model = MyModel()
optimizer = torch.optim.Adam(model.parameters())
model.to('cuda')

for epoch in range(max_epochs):
    for batch in train_loader:
        batch = batch.to('cuda')
        optimizer.zero_grad()
        loss = model(batch)
        loss.backward()
        optimizer.step()
```

**Lightning 版本**：
```python
class LitModel(L.LightningModule):
    def __init__(self):
        super().__init__()
        self.model = MyModel()

    def training_step(self, batch, batch_idx):
        loss = self.model(batch)  # 不再需要 .to('cuda')！
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters())

# 训练
trainer = L.Trainer(max_epochs=10, accelerator='gpu')
trainer.fit(LitModel(), train_loader)
```

**好处**：40+ 行 → 15 行，无需设备管理，自动分布式

### 工作流 2：验证和测试

```python
class LitModel(L.LightningModule):
    def __init__(self):
        super().__init__()
        self.model = MyModel()

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self.model(x)
        loss = nn.functional.cross_entropy(y_hat, y)
        self.log('train_loss', loss)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self.model(x)
        val_loss = nn.functional.cross_entropy(y_hat, y)
        acc = (y_hat.argmax(dim=1) == y).float().mean()
        self.log('val_loss', val_loss)
        self.log('val_acc', acc)

    def test_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self.model(x)
        test_loss = nn.functional.cross_entropy(y_hat, y)
        self.log('test_loss', test_loss)

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=1e-3)

# 训练并验证
trainer = L.Trainer(max_epochs=10)
trainer.fit(model, train_loader, val_loader)

# 测试
trainer.test(model, test_loader)
```

**自动特性**：
- 默认每个 epoch 运行验证
- 指标记录到 TensorBoard
- 基于 val_loss 的最佳模型检查点保存

### 工作流 3：分布式训练（DDP）

```python
# 与单 GPU 相同的代码！
model = LitModel()

# 使用 DDP 的 8 GPU（自动！）
trainer = L.Trainer(
    accelerator='gpu',
    devices=8,
    strategy='ddp'  # 或 'fsdp', 'deepspeed'
)

trainer.fit(model, train_loader)
```

**启动**：
```bash
# 单个命令，Lightning 负责其余部分
python train.py
```

**无需更改**：
- 自动数据分发
- 梯度同步
- 多节点支持（只需设置 `num_nodes=2`）

### 工作流 4：用于监控的回调

```python
from lightning.pytorch.callbacks import ModelCheckpoint, EarlyStopping, LearningRateMonitor

# 创建回调
checkpoint = ModelCheckpoint(
    monitor='val_loss',
    mode='min',
    save_top_k=3,
    filename='model-{epoch:02d}-{val_loss:.2f}'
)

early_stop = EarlyStopping(
    monitor='val_loss',
    patience=5,
    mode='min'
)

lr_monitor = LearningRateMonitor(logging_interval='epoch')

# 添加到 Trainer
trainer = L.Trainer(
    max_epochs=100,
    callbacks=[checkpoint, early_stop, lr_monitor]
)

trainer.fit(model, train_loader, val_loader)
```

**结果**：
- 自动保存最佳的 3 个模型
- 若 5 个 epoch 无改进则提前停止
- 将学习率记录到 TensorBoard

### 工作流 5：学习率调度

```python
class LitModel(L.LightningModule):
    # ... (training_step, 等)

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=1e-3)

        # 余弦退火
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=100,
            eta_min=1e-5
        )

        return {
            'optimizer': optimizer,
            'lr_scheduler': {
                'scheduler': scheduler,
                'interval': 'epoch',  # 每 epoch 更新
                'frequency': 1
            }
        }

# 学习率自动记录！
trainer = L.Trainer(max_epochs=100)
trainer.fit(model, train_loader)
```

## 何时使用 vs 替代方案

**使用 PyTorch Lightning 当**：
- 希望代码整洁、组织有序
- 需要生产就绪的训练循环
- 在单 GPU、多 GPU、TPU 之间切换
- 希望有内置的回调和日志记录
- 团队协作（标准化结构）

**主要优势**：
- **组织化**：将研究代码与工程代码分离
- **自动化**：一行代码实现 DDP、FSDP、DeepSpeed
- **回调**：模块化的训练扩展
- **可重现**：更少的样板代码 = 更少的 bug
- **经过测试**：每月下载量超过 100 万，久经考验

**使用替代方案**：
- **Accelerate**：对现有代码改动最小，更灵活
- **Ray Train**：多节点编排，超参数调优
- **原生 PyTorch**：最大控制权，适合学习
- **Keras**：TensorFlow 生态系统

## 常见问题

**问题：损失不下降**

检查数据和模型设置：
```python
# 在 training_step 中添加
def training_step(self, batch, batch_idx):
    if batch_idx == 0:
        print(f"Batch shape: {batch[0].shape}")
        print(f"Labels: {batch[1]}")
    loss = ...
    return loss
```

**问题：内存不足**

减少批量大小或使用梯度累积：
```python
trainer = L.Trainer(
    accumulate_grad_batches=4,  # 有效批大小 = batch_size × 4
    precision='bf16'  # 或 'fp16'，内存减少 50%
)
```

**问题：验证未运行**

确保传入 val_loader：
```python
# 错误
trainer.fit(model, train_loader)

# 正确
trainer.fit(model, train_loader, val_loader)
```

**问题：DDP 意外产生多个进程**

Lightning 会自动检测 GPU。显式设置设备：
```python
# 先在 CPU 上测试
trainer = L.Trainer(accelerator='cpu', devices=1)

# 然后 GPU
trainer = L.Trainer(accelerator='gpu', devices=1)
```

## 高级主题

**回调**：参见 [references/callbacks.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/pytorch-lightning/references/callbacks.md) 了解 EarlyStopping、ModelCheckpoint、自定义回调和回调钩子。

**分布式策略**：参见 [references/distributed.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/pytorch-lightning/references/distributed.md) 了解 DDP、FSDP、DeepSpeed ZeRO 集成、多节点设置。

**超参数调优**：参见 [references/hyperparameter-tuning.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/pytorch-lightning/references/hyperparameter-tuning.md) 了解与 Optuna、Ray Tune 和 WandB 扫描的集成。

## 硬件需求

- **CPU**：可用（适合调试）
- **单 GPU**：可用
- **多 GPU**：DDP（默认）、FSDP 或 DeepSpeed
- **多节点**：DDP、FSDP、DeepSpeed
- **TPU**：支持（8 核心）
- **Apple MPS**：支持

**精度选项**：
- FP32（默认）
- FP16（V100、旧 GPU）
- BF16（A100/H100，推荐）
- FP8（H100）

## 资源

- 文档：https://lightning.ai/docs/pytorch/stable/
- GitHub：https://github.com/Lightning-AI/pytorch-lightning ⭐ 29,000+
- 版本：2.5.5+
- 示例：https://github.com/Lightning-AI/pytorch-lightning/tree/master/examples
- Discord：https://discord.gg/lightning-ai
- 使用者：Kaggle 获胜者、研究实验室、生产团队