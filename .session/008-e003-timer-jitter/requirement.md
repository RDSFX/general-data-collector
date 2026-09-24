# 需求

**会话编号**：008  
**关联任务**：E-003（定时调度随机抖动）  
**日期**：2026-09-24

## 任务范围

实施 [docs/future-enhancements.md](../../docs/future-enhancements.md#e-003--定时调度随机抖动) E-003：为 timer.py 添加随机抖动支持，避免整点流量尖峰。

**用户选择的方案**：
- 配置方式：方案 B（配置文件 `[schedule]` 新增 `jitter_percent`）
- 抖动分布：均匀分布 `[interval * (1-jitter), interval * (1+jitter)]`
- 默认行为：无抖动（向后兼容）

## 本次范围

1. 修改 [timer.py](../../timer.py)，支持从配置读取 `schedule.jitter_percent`（可选字段，0-100 百分比）
2. 抖动逻辑使用均匀分布
3. `jitter_percent` 缺失或 ≤ 0 时无抖动，保持向后兼容
4. 更新 [docs/future-enhancements.md](../../docs/future-enhancements.md) E-003 状态为已完成
5. 更新 [docs/task-progress.md](../../docs/task-progress.md) 和会话索引
