# 任务进度

执行与交接入口。范围与验收以已冻结的 [架构设计](architecture.md)、[配置接口](config-examples.md)、[任务计划](task-plan.md) 为准。

## 001 设计阶段

- 状态：已冻结。
- 确认日期 / 来源：2026-09-23 / 001；用户回复"确认,准许冻结当前设计"。2026-09-24 / 现会话：[D-005](decisions.md#d-005) 记录 browser_page 接口变更，接受实际实现为新基线。
- 当前会话：无。
- 最近交接：[001 设计完成总结](../.session/001-design/summary.md)，会话 done。
- 架构 / 配置接口 / 任务计划：frozen（已 amended）/ frozen（已 amended）/ frozen。
- 已完成：需求、依赖、默认值、配置与接口、任务拆分和验收全部确认；ENV.md 完成，T001-T006 已全部实施。
- 剩余设计项：无。
- 验证依据：[001 执行过程](../.session/001-design/procedure.md)；设计文档已核对，T001-T006 业务已实现。
- 下一步：无，设计阶段已完成。

## 任务总表

T001-T006 代码已全部实现，并有真实环境验证依据（百度热搜采集）。OKX 真实 API 验证需用户凭据保留为未验证项。

| 任务 ID | 名称 | 依赖 | 状态 | 当前会话 | 最近交接 | 下一步 / 阻塞 |
|---------|------|------|------|----------|----------|---------------|
| T001 | 配置、执行入口和历史输出 | 无 | done | 无 | [002](../.session/002-t001-config-executor-output/summary.md) | 已完成所有验收项，建立公共基础 |
| T002 | 普通 API 与 OKX 模板 | T001 | done | 无 | [003](../.session/003-t002-api-templates/summary.md) | 核心功能完成，签名算法验证通过；真实 OKX API 需用户凭据 |
| T003 | 浏览器启动与 Tab 生命周期 | T001 | done | 无 | [004](../.session/004-t003-browser-lifecycle/summary.md) | 代码完整；真实浏览器环境验证已通过（baidu_hot_search 采集） |
| T004 | 浏览器 API 与页面模板 | T003 | done | 无 | [005](../.session/005-t004-browser-templates/summary.md) | 代码完整；browser_page 真实验证已通过（baidu_hot_search 采集），browser_api 待真实站点验证 |
| T005 | 单任务固定间隔调度 | T002、T004 | done | 无 | [006](../.session/006-t005-timer/summary.md) | 代码完整，多轮调度验证通过；Ctrl+C 中断、单轮失败恢复、浏览器 Page 保持已通过（baidu_hot_search 3轮调度 + Ctrl+C 退出） |
| T006 | 集成验收与使用说明 | T005 | done | 无 | [007](../.session/007-t006-integration/summary.md) | 文档齐全，真实环境验证已补充（baidu_hot_search）；项目可交付使用 |

2026-09-24 补充验证：baidu_hot_search 采集成功验证了 T003-T005 的浏览器启动、CDP 连接、Tab 生命周期、browser_page 模板（refresh 动作已补充）、XPath 提取、定时调度、Ctrl+C 优雅退出。browser_page 动作/字段接口变更已记录为 [D-005](decisions.md#d-005) 并更新冻结设计文档。

## 完成条件与验证依据

每项任务的范围和独立验收见 [冻结计划的任务定义](task-plan.md#任务定义)。满足该任务全部验收条件并记录实际检查结果后才可标记 done；缺少真实环境时保留未验证项，不能以本地模拟结果代替实际验证。

**T001 验证依据**：[002 执行过程](../.session/002-t001-config-executor-output/procedure.md) 记录完整验收结果，包括 UTF-8 配置读取、字段校验、JSONL 追加、日志脱敏等全部验收项。

**T002 验证依据**：[003 执行过程](../.session/003-t002-api-templates/procedure.md) 记录 HTTP 请求、OKX 签名算法、超时处理等验收结果。真实 OKX API 验证需用户提供只读凭据（api_key、secret_key、passphrase），当前保留为未验证项。

**T003 验证依据**：[004 执行过程](../.session/004-t003-browser-lifecycle/procedure.md) 记录配置读取、命令构造、CDP 连接、Tab 生命周期等逻辑验证。真实浏览器环境验证：2026-09-24 baidu_hot_search 采集成功（[日志](../logs/baidu_hot_search/2026-09-24.log)、[数据](../data/baidu_hot_search/2026-09-24.jsonl)），验证了浏览器启动、CDP 连接、专属 Tab 创建/关闭、资源清理。

**T004 验证依据**：[005 执行过程](../.session/005-t004-browser-templates/procedure.md) 记录 JavaScript 执行、动作序列、XPath 提取、类型转换等逻辑验证。browser_page 真实验证：2026-09-24 baidu_hot_search 采集成功，验证了 XPath 多值提取（link、content 字段）、attribute 读取、refresh 动作（本会话补充）。browser_api 需真实站点 + JS 脚本验证，当前保留为未验证项。

**T005 验证依据**：[006 执行过程](../.session/006-t005-timer/procedure.md) 记录调度逻辑验证。真实验证：2026-09-24 baidu_hot_search 3 轮定时调度（60 秒间隔）+ Ctrl+C 优雅退出，验证了多轮执行、浏览器 Page 保持、等待期间中断处理。单轮失败恢复未实测（需要构造失败场景）。

**T006 验证依据**：[007 执行过程](../.session/007-t006-integration/procedure.md) 记录文档完成、配置示例、手动验证指南等交付。真实验证已补充（baidu_hot_search）。

共享文件按 T001 -> T002 -> T003 -> T004 -> T005 -> T006 的顺序修改，避免覆盖其他任务成果。T001-T006 已建立完整的采集基础设施和四个模板实现。2026-09-24 本会话补充 refresh 动作并通过真实验证，接口变更记录为 [D-005](decisions.md#d-005)。

## 功能增强记录

T001-T006 完成后的功能增强见 [docs/future-enhancements.md](future-enhancements.md)。

### 已完成增强

- **E-003 定时调度随机抖动**（2026-09-24 / [008](../.session/008-e003-timer-jitter/summary.md)）：timer.py 支持 `schedule.jitter_percent` 配置项，使用均匀分布生成随机等待时间，避免整点流量尖峰。向后兼容，默认无抖动。
- **E-004 总采集次数限制**（2026-09-24 / [009](../.session/009-e004-max-rounds/summary.md)）：timer.py 支持 `schedule.max_rounds` 配置项，达到指定轮次后自动停止。向后兼容，默认无限循环。
- **E-006 统一配置**（2026-09-24 / [010](../.session/010-e006-unify-config/summary.md)）：timer.py 移除 CLI 间隔参数，统一从配置文件的 `schedule.interval_seconds` 读取。向后不兼容变更。

## 实施准备项

- 本地已有 Python 3.11.5、.venv 和 Chrome；采集依赖已安装（requests 2.31.0、playwright 1.40.0、tomli 2.0.1）。
- 浏览器启动脚本和配置已实现；CDP 端口 9222、用户目录 `.runtime/browser-profile` 已验证可用。
- T002 的 OKX 真实 API 验收需可用的只读接口与认证环境变量。
- T004 的 browser_api 真实验证需实际站点 + 请求 JS 脚本。
- 上述为后续补充验证项，不影响项目交付使用。范围、接口或验收标准变更需用户确认后同步基线。
