# 决策与实施知识

记录影响后续工作的决策、可复用结论及原因，避免重复会话日志。

## 记录方式

- 实际条目从 `D-001` 开始递增，最新在上。
- 注明日期、关联任务和来源会话；专题内容较多时另建文档并链接。
- 涉及基线变更时，记录用户确认依据并同步架构、计划及进度。

## 条目模板

```markdown
## D-NNN · YYYY-MM-DD · 标题

- 关联任务：
- 结论与原因：
- 影响范围：
- 来源：会话链接；基线变更附用户确认依据。
```

## 记录

## D-005 · 2026-09-24 · browser_page 动作/字段接口改为 selector 体系并接受为新基线

- 关联任务：T004、T006；影响 architecture.md、config-examples.md 冻结内容。
- 结论与原因：T004 实施时（[005 会话](../.session/005-t004-browser-templates/summary.md)）未采用冻结设计中的 xpath/x-y/delta 动作方案，而是实现为 Playwright CSS selector 体系：动作类型为 click、wait、fill、select、waitForSelector（新增 fill/select，未实现 double_click/scroll/wait_for）；字段 read 支持 text/html/attribute:<name>（原设计为 text/attribute + 独立 attribute 字段），并新增 type（string/number/boolean）转换。2026-09-24 复核会话中确认接受该实现为新基线，不改代码贴合原冻结设计；同时在 template/browser_page.py 补充 refresh 动作（刷新当前页面），补齐原设计要求、实现原本缺失的能力。
- 影响范围：architecture.md、config-examples.md 已同步动作/字段接口描述并标注 amended_on/amended_by；两份文档标题仍为 frozen，本条变更记录作为基线修正依据。后续涉及页面动作/字段的任务以本条为准，不再对照 001 会话最初的 xpath/x-y/delta 方案。
- 来源：2026-09-24 复核会话；用户对"如何处理接口偏离"回复选择"接受现状为新基线"，对 refresh 动作回复选择"补充为新动作类型"。

## D-004 · 2026-09-23 · 设计基线冻结

- 关联任务：设计、T001-T006。
- 结论与原因：用户逐项确认需求、配置、接口及默认值后，最终确认任务拆分和验收方法，准许冻结当前设计。
- 影响范围：architecture.md、config-examples.md、task-plan.md 设为 frozen，日期 2026-09-23、来源 001；T001-T006 初始化为 todo，001 为 done。后续范围/接口/验收变更需用户确认；日常进度仅维护 task-progress.md。
- 来源：[001 设计完成记录](../.session/001-design/requirement.md)；用户原话“确认，准许冻结当前设计”。冻结不授权本会话开始业务开发。

## D-003 · 2026-09-23 · 依赖选型保持精简

- 关联任务：设计、T001-T006（草案）。
- 结论与原因：用户确认 requests 负责 HTTP、Playwright 同步 API 负责 CDP 与页面操作；TOML、签名、调度、JSONL、日志使用 Python 标准库，适配单进程单任务。
- 影响范围：依赖版本待实施时确定，当前未安装；选型确认不代表补充接口、默认值与任务计划整体冻结。
- 来源：[001 需求与收尾记录](../.session/001-design/requirement.md)；用户回复“可以，收尾吧”。

## D-002 · 2026-09-23 · 浏览器任务独占 Tab

- 关联任务：设计、T003-T005（草案）。
- 结论与原因：每个任务新建并持续复用自己的 Tab，同 URL 也不共享；退出关闭自身 Tab，保留浏览器。避免跨任务页面操作协调。
- 影响范围：任务可共享浏览器 Cookie 等登录数据，不能据此声称账号隔离；初始化脚本应限制在任务 Page，不做 context 级全局注入。
- 来源：[001 会话](../.session/001-design/requirement.md)；用户明确要求“不搞共享 Tab”，随后确认生命周期规则。

## D-001 · 2026-09-23 · 单配置单进程

- 关联任务：设计、T001、T005（草案）。
- 结论与原因：每次启动只接收一个 TOML 任务配置；用户另开终端运行其他任务，不需要统一并发调度或跨进程锁。每轮结束后等待间隔，不设计重启恢复。
- 影响范围：计时器和执行器仅接受单个任务配置，后续不恢复多配置同进程或扫描全部配置的旧建议。
- 来源：[001 会话](../.session/001-design/requirement.md)；用户明确要求“不支持一次性传入多个任务配置”。
