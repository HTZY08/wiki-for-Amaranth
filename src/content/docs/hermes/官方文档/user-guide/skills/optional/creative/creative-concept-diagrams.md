---
title: Concept Diagrams
---

## 示例参考（Examples Reference）

`examples/` 目录包含 15 个完整、经过测试的图表。在编写同类型新图表之前，可先浏览这些示例以了解工作模式：

| 文件（File） | 类型（Type） | 说明（Demonstrates） |
|------|------|--------------|
| `hospital-emergency-department-flow.md` | Flowchart | 使用语义颜色进行优先级路由 |
| `feature-film-production-pipeline.md` | Flowchart | 分阶段工作流，水平子流程 |
| `automated-password-reset-flow.md` | Flowchart | 含错误分支的认证流程 |
| `autonomous-llm-research-agent-flow.md` | Flowchart | 循环箭头、决策分支 |
| `place-order-uml-sequence.md` | Sequence | UML 时序图样式 |
| `commercial-aircraft-structure.md` | Physical | 使用路径、多边形、椭圆绘制逼真形状 |
| `wind-turbine-structure.md` | Physical cross-section | 地下/地上分离，颜色编码 |
| `smartphone-layer-anatomy.md` | Exploded view | 交替左右标签，分层组件 |
| `apartment-floor-plan-conversion.md` | Floor plan | 墙、门、红色虚线表示的改造建议 |
| `banana-journey-tree-to-smoothie.md` | Narrative journey | 蜿蜒路径，渐进状态变化 |
| `cpu-ooo-microarchitecture.md` | Hardware pipeline | 扇出（fan-out），侧边栏显示内存层次结构 |
| `sn2-reaction-mechanism.md` | Chemistry | 分子、曲线箭头、能量曲线 |
| `smart-city-infrastructure.md` | Hub-spoke | 每个系统的语义线型 |
| `electricity-grid-flow.md` | Multi-stage flow | 电压层次，流向标记 |
| `ml-benchmark-grouped-bar-chart.md` | Chart | 分组柱状图，双轴 |

使用以下方式加载任意示例：
```
skill_view(name="concept-diagrams", file_path="examples/<filename>")
```

---

--- body ---
--- body ---
## 快速参考：何时使用何种图表

| 用户说（User says） | 图表类型（Diagram type） | 建议颜色（Suggested colors） |
|-----------|--------------|------------------|
| "展示流水线" | Flowchart | 灰色起点/终点，紫色步骤，红色错误，青色部署 |
| "绘制数据流" | Data pipeline (左右流向) | 灰色数据源，紫色处理，青色数据终点 |
| "可视化系统" | Structural (包含关系) | 紫色容器，青色服务，珊瑚色数据 |
| "映射端点" | API tree | 紫色根节点，每个资源组一个分支 |
| "展示服务" | Microservice topology | 灰色入口，青色服务，紫色总线，珊瑚色工作者 |
| "绘制飞机/交通工具" | Physical | 使用路径、多边形、椭圆绘制逼真形状 |
| "智慧城市 / IoT" | Hub-spoke integration | 每个子系统使用语义线型 |
| "展示仪表盘" | UI mockup | 深色屏幕，图表颜色：青色、紫色，警报用珊瑚色 |
| "电网 / 电力" | Multi-stage flow | 电压层次 (HV/MV/LV 线宽) |
| "风力涡轮机 / 涡轮" | Physical cross-section | 基础 + 塔筒剖视 + 机舱颜色编码 |
| "X 的旅程 / 生命周期" | Narrative journey | 蜿蜒路径，渐进状态变化 |
| "X 的层级 / 分解图" | Exploded layer view | 垂直堆叠，交替标签 |
| "CPU / 流水线" | Hardware pipeline | 垂直阶段，扇出到执行端口 |
| "平面图 / 公寓" | Floor plan | 墙、门、红色虚线表示的改造建议 |
| "反应机理" | Chemistry | 原子、化学键、曲线箭头、过渡态、能量曲线 |