--- frontmatter ---
---

## 获取更多帮助

如果你已经按照本指南操作，但问题仍然存在：

1. 使用 `hermes cron run <任务ID>` 运行任务（将在下一次网关周期触发），并在聊天输出中查看错误
2. 检查 `~/.hermes/logs/agent.log` 中的调度程序消息，以及 `~/.hermes/logs/errors.log` 中的警告信息
3. 在 [github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) 提交问题，并附上：
   - 任务ID（job ID）和调度计划（schedule）
   - 交付目标（delivery target）
   - 你期望的结果与实际发生的情况
   - 日志中相关的错误消息

---

--- body ---
*有关完整的 cron 参考，请参阅 [使用 Cron 自动化一切](/guides/automate-with-cron) 和 [计划任务 (Cron)](/user-guide/features/cron)。*