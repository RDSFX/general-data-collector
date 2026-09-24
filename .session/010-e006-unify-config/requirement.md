# 需求

**会话编号**：010  
**关联任务**：E-006（统一配置，移除 CLI 间隔参数）  
**日期**：2026-09-24

## 背景

当前 timer.py 同时从 CLI 参数和配置文件读取 `interval_seconds`，存在冗余和冲突：
- CLI：`python timer.py <config> <interval_seconds>`
- 配置：`[schedule] interval_seconds = 60`

用户反馈应该统一走配置文件，CLI 只接收配置文件路径。

## 本次范围

1. 修改 [timer.py](../../timer.py) CLI 参数解析：
   - 只接收一个参数：配置文件路径
   - 从配置的 `[schedule].interval_seconds` 读取间隔
   - 如果配置缺失 `interval_seconds`，提示用户并退出
2. 更新相关文档和使用示例
3. 更新 README.md 中的使用说明
