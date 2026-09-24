# 实施计划

## 步骤

1. **修改 timer.py**
   - 导入 `random` 模块
   - 新增 `_calculate_wait_time(config, base_interval)` 函数，读取 `schedule.jitter_percent`，返回实际等待时间（浮点数）
   - 修改调度循环 `run_scheduler()` 的等待逻辑，使用 `_calculate_wait_time()` 计算实际等待
   - 修改等待循环支持浮点数时间（`elapsed` 改为 `float`）
   - 更新日志输出显示实际等待时间（保留 1 位小数）

2. **更新文档**
   - 在 docs/future-enhancements.md E-003 标记为已完成，记录实施方案和日期
   - 在 docs/task-progress.md 添加 E-003 完成记录
   - 同步会话索引

## 验收条件

- timer.py 支持 `schedule.jitter_percent` 配置项（可选）
- 默认行为（无抖动）保持向后兼容
- 抖动范围符合均匀分布 `[interval * (1-jitter), interval * (1+jitter)]`
- 代码无语法错误
- 文档同步完成
