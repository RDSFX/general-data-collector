# 功能增强待办

记录 T001-T006 完成后的潜在改进项，待明确需求细节后实施。

## 待明确需求

### E-001 · CDP 检测规避方案

**背景**：通过 `--remote-debugging-port` 启动的浏览器会暴露特征（navigator.webdriver 已隐藏，但 CDP 本身、window.chrome 等仍可检测），部分网站（如 Cloudflare）会拒绝。

**当前状态**：
- `scripts/browser_init.js` 隐藏 `navigator.webdriver`
- 百度等常见站点可用，严格检测站点会失败
- 架构文档已声明"不承诺规避所有自动化检测"

**待确认**：
1. 是否接受这个限制，仅在文档强调适用场景
2. 还是需要更换启动方式（例如用 Playwright 管理浏览器生命周期而非手动启动）
3. 或提供可选的反检测配置（更多初始化脚本、User-Agent 等）

**影响范围**：T003 浏览器启动方式、browser.toml 配置、使用说明

---

### E-002 · 任务独立 profile 隔离

**背景**：当前所有任务共享 `.runtime/browser-profile`，可以共享登录态，但不隔离 Cookie/LocalStorage/IndexedDB。

**当前状态**：
- `config/browser.toml` 的 `user_data_dir = ".runtime/browser-profile"` 全局配置
- 不同任务可能相互影响（Cookie 冲突、登录态覆盖）

**待确认**：
1. profile 隔离粒度：
   - 方案 A：`browser.toml` 支持变量替换 `{task_name}`，例如 `user_data_dir = ".runtime/profiles/{task_name}"`
   - 方案 B：任务配置 `[browser]` 新增可选 `profile_dir`，不填则用公共目录
   - 方案 C：始终按任务名隔离，不提供共享选项
2. 已有公共 profile 的迁移策略
3. 磁盘空间占用考虑（每个任务独立 profile 会增加存储）

**影响范围**：shared/config.py、shared/browser.py、config/browser.toml 结构

---

### E-003 · 定时调度随机抖动

**状态**：✓ 已完成（2026-09-24 / [008](../.session/008-e003-timer-jitter/summary.md)）

**背景**：当前 `timer.py` 是固定间隔采集，容易被识别为自动化模式；真实用户行为通常有时间波动。

**实施方案**：
- 配置方式：`[schedule]` 新增可选字段 `jitter_percent`（0-100 百分比）
- 抖动分布：均匀分布 `random.uniform(min_wait, max_wait)`，其中 `min_wait = interval * (1-jitter/100)`，`max_wait = interval * (1+jitter/100)`
- 默认行为：`jitter_percent` 缺失或 ≤ 0 时无抖动（向后兼容）

**使用示例**：
```toml
[schedule]
jitter_percent = 20  # 基准间隔 ±20% 随机抖动
```

**修改文件**：[timer.py](../timer.py) — 导入 `random`，新增 `_calculate_wait_time()` 函数，修改等待逻辑支持浮点数时间

---

### E-004 · 总采集次数限制

**状态**：✓ 已完成（2026-09-24 / [009](../.session/009-e004-max-rounds/summary.md)）

**背景**：当前 `timer.py` 无限循环直到 Ctrl+C，无法实现"采集 N 次后自动停止"。

**实施方案**：
- 配置方式：`[schedule]` 新增可选字段 `max_rounds`（正整数）
- 默认行为：`max_rounds` 缺失或 ≤ 0 时无限循环（向后兼容）
- 计数语义：所有轮次（包括失败）都计入次数
- 达到限制时输出日志并退出："已完成 N 轮采集，达到配置限制，停止调度"

**使用示例**：
```toml
[schedule]
interval_seconds = 60
max_rounds = 10  # 采集 10 轮后自动停止
```

**修改文件**：[timer.py](../timer.py) — 在 `run_scheduler()` 中读取 `max_rounds` 配置，每轮开始前检查轮次限制

---

### E-006 · 统一配置（移除 CLI 间隔参数）

**状态**：✓ 已完成（2026-09-24 / [010](../.session/010-e006-unify-config/summary.md)）

**背景**：timer.py 同时从 CLI 参数和配置文件读取 `interval_seconds`，存在冗余和潜在冲突。

**实施方案**：
- 移除 CLI 的第二个参数（间隔秒数）
- 统一从配置文件的 `[schedule].interval_seconds` 读取
- 缺失配置时输出清晰错误提示

**新的使用方式**：
```bash
# 旧用法（已废弃）
python timer.py config.toml 60

# 新用法
python timer.py config.toml
```

配置文件必须包含：
```toml
[schedule]
interval_seconds = 60
```

**修改文件**：[timer.py](../timer.py) — CLI 参数解析、配置读取；[README.md](../README.md)、配置示例、验证文档

**注意**：向后不兼容变更，所有使用 timer.py 的命令需要更新。

---

## 实施优先级

待用户逐项明确需求后，按影响范围和依赖关系确定实施顺序。E-001 涉及架构调整，需优先决策；E-002/E-003/E-004 相对独立，可并行或按需实施。

---

**记录日期**：2026-09-24
**来源会话**：复核与真实验证会话
**状态**：待明确需求细节
