---
title: Fitness Nutrition
---

## 验证

运行练习搜索后：确认结果包含练习名称、肌肉群和器材。
运行营养查询后：确认每100克宏量营养素数据返回包含千卡、蛋白质、脂肪、碳水化合物。
运行计算器后：进行合理性检查输出（例如，对于大多数成年人，TDEE 应在 1500-3500 之间）。

---

--- body ---
## 快速参考

| 任务 | 来源 | 端点 |
|------|------|------|
| 按名称搜索练习 | wger | `GET /api/v2/exercise/search/?term=&language=english` |
| 练习详细信息 | wger | `GET /api/v2/exerciseinfo/{id}/` |
| 按肌肉筛选 | wger | `GET /api/v2/exercise/?muscles={id}&language=2&status=2` |
| 按器材筛选 | wger | `GET /api/v2/exercise/?equipment={id}&language=2&status=2` |
| 列出类别 | wger | `GET /api/v2/exercisecategory/` |
| 列出肌肉 | wger | `GET /api/v2/muscle/` |
| 搜索食物 | USDA | `GET /fdc/v1/foods/search?query=&dataType=Foundation,SR Legacy` |
| 食物详细信息 | USDA | `GET /fdc/v1/food/{fdcId}` |
| BMI / TDEE / 1RM / 宏量营养素 | 离线 | `python3 scripts/body_calc.py` |