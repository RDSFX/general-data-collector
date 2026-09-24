# 实施计划

## 步骤

1. **修改 timer.py**
   - 修改 `run_scheduler()` 函数签名，从 config 读取 `schedule.max_rounds`
   - 将 `while True` 改为条件循环：当 `max_rounds > 0` 时检查 `round_num <= max_rounds`
   - 达到限制时输出日志并退出
   - 日志格式："已完成 N 轮采集，达到配置限制，停止调度"

2. **更新文档**
   - docs/config-examples.md 同步 `[schedule]` 节增加 `max_rounds` 说明和示例
   - docs/future-enhancements.md E-004 标记为已完成
   - docs/task-progress.md 增加 E-004 记录
   - 同步会话索引

## 验收条件

- timer.py 支持 `schedule.max_rounds` 配置项（可选）
- 默认行为（无限循环）保持向后兼容
- 所有轮次（包括失败）都计入次数
- 达到限制时输出清晰日志并正常退出
- 代码无语法错误
- 文档同步完成
