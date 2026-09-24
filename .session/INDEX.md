# 会话索引

001 已完成，设计于 2026-09-23 经用户确认冻结，T001-T006 已初始化。002 起按任务计划实施，下一项为 T001。

## 登记步骤

1. 续接当前会话时复用目录；设计未完成时继续 `001`。
2. 新建时取索引和实际目录中的最大编号加一，忽略 `_template/`，使用 `NNN-short-slug`。
3. 同步本表与 `requirement.md` 的编号、状态等信息；`001` 的关联任务写“设计”，实施会话填写任务 ID。
4. 收尾时更新 [任务进度](../docs/task-progress.md) 和交接记录，再同步会话状态。

会话状态：`open` 进行中、`done` 已验收、`archived` 已交接但有剩余工作、`abandoned` 已取消。恢复时改为 `open`；会话归档不代表任务完成。

| 编号 | 主题 | 关联任务 | 状态 | 日期 |
|------|------|----------|------|------|
| [001](001-design/requirement.md) | 轻量数据采集工具设计 | 设计 | done | 2026-09-23 |
| [002](002-t001-config-executor-output/requirement.md) | 配置、执行入口和历史输出 | T001 | done | 2026-09-23 |
| [003](003-t002-api-templates/requirement.md) | 普通 API 与 OKX 模板 | T002 | done | 2026-09-23 |
| [004](004-t003-browser-lifecycle/requirement.md) | 浏览器启动与 Tab 生命周期 | T003 | done | 2026-09-23 |
| [005](005-t004-browser-templates/requirement.md) | 浏览器 API 与页面模板 | T004 | done | 2026-09-23 |
| [006](006-t005-timer/requirement.md) | 单任务固定间隔调度 | T005 | done | 2026-09-23 |
| [007](007-t006-integration/requirement.md) | 集成验收与使用说明 | T006 | done | 2026-09-23 |
| [008](008-e003-timer-jitter/requirement.md) | 定时调度随机抖动 | E-003 | done | 2026-09-24 |
| [009](009-e004-max-rounds/requirement.md) | 总采集次数限制 | E-004 | done | 2026-09-24 |
| [010](010-e006-unify-config/requirement.md) | 统一配置，移除 CLI 间隔参数 | E-006 | done | 2026-09-24 |

设计完成交接：[001 总结](001-design/summary.md)。
T001 完成交接：[002 总结](002-t001-config-executor-output/summary.md)。
T002 完成交接：[003 总结](003-t002-api-templates/summary.md)。
T003 完成交接：[004 总结](004-t003-browser-lifecycle/summary.md)。
T004 完成交接：[005 总结](005-t004-browser-templates/summary.md)。
T005 完成交接：[006 总结](006-t005-timer/summary.md)。
T006 完成交接：[007 总结](007-t006-integration/summary.md)。
E-003 完成交接：[008 总结](008-e003-timer-jitter/summary.md)。
E-004 完成交接：[009 总结](009-e004-max-rounds/summary.md)。
E-006 完成交接：[010 总结](010-e006-unify-config/summary.md)。
