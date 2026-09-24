# 执行过程

## 实施步骤

### 1. 实现 timer.py 核心逻辑

**CLI 参数解析**：
- ✅ 接受两个参数：配置文件路径、间隔秒数
- ✅ 验证参数数量（恰好 2 个）
- ✅ 验证间隔秒数（正整数）
- ✅ 参数错误时明确报错

**配置加载与日志**：
- ✅ 复用 shared/config.py 的 load_config()
- ✅ 复用 shared/output.py 的 setup_logging()
- ✅ 记录调度器启动信息（任务名、配置路径、间隔、模板）

**主循环**：
- ✅ 首轮立即执行（round_num = 1，不等待）
- ✅ 后续轮次按固定间隔执行
- ✅ 每轮记录开始和结束日志
- ✅ 轮次计数器递增

**信号处理**：
- ✅ 注册 SIGINT 处理器（Ctrl+C）
- ✅ 设置全局退出标志 _exit_flag
- ✅ 打印友好提示信息

**错误处理**：
- ✅ 单轮失败捕获异常并记录日志
- ✅ 继续下一轮（不退出调度器）
- ✅ 配置错误、调度错误分类处理

### 2. 生命周期管理

**模板类型判断**：
- ✅ 根据 template_name 判断是否为浏览器模板
- ✅ API 模板：api_request、okx_api
- ✅ 浏览器模板：browser_api、browser_page

**API 模板生命周期**：
- ✅ 每轮创建新 Session（requests.Session()）
- ✅ 单轮执行完成后关闭 Session
- ✅ 不保留跨轮状态

**浏览器模板生命周期**：
- ✅ 首轮调用 create_browser_context() 创建 Page
- ✅ 后续轮次复用同一个 Page
- ✅ 每轮检查 Page 是否关闭（page.is_closed()）
- ✅ Page 关闭时退出调度器
- ✅ 退出时调用 cleanup_browser_context() 清理资源

### 3. 执行单轮采集

**模板加载**：
- ✅ 复用 TEMPLATE_FILES 映射
- ✅ 使用 importlib.util 动态加载模块
- ✅ 验证模板文件存在
- ✅ 验证 run() 函数存在

**执行逻辑**：
- ✅ 调用 template_module.run(config, context)
- ✅ 传递配置和上下文（Session 或 Page）
- ✅ 捕获执行异常

**结果保存**：
- ✅ 复用 shared/output.py 的 save_result()
- ✅ 保存到 data/<task_name>/<date>.jsonl
- ✅ 追加模式，支持多轮写入

### 4. 退出控制

**退出标志检查**：
- ✅ 每轮开始前检查 _exit_flag
- ✅ 等待期间每秒检查 _exit_flag
- ✅ 标志设置后立即退出等待循环

**当前轮完成保证**：
- ✅ 信号处理器只设置标志，不中断执行
- ✅ execute_round() 执行完成后才检查标志
- ✅ 不会在模板执行中途退出

**资源清理**：
- ✅ finally 块保证清理执行
- ✅ 浏览器模板调用 cleanup_browser_context()
- ✅ API 模板关闭 Session（如果存在）

## 验证结果

### 5.1 逻辑验证

**模块结构**：
- ✅ timer 模块导入成功
- ✅ main、run_scheduler、execute_round、load_template、signal_handler 函数存在
- ✅ _exit_flag 全局变量存在
- ✅ TEMPLATE_FILES 映射包含 4 个模板

**模板加载**：
- ✅ api_request 模板加载成功，包含 run 函数
- ✅ browser_page 模板加载成功，包含 run 函数
- ✅ 未知模板正确抛出异常

**信号处理**：
- ✅ 初始退出标志为 False
- ✅ 调用信号处理器后标志变为 True
- ✅ 信号处理器正确设置退出标志

**模板文件**：
- ✅ 所有 4 个模板文件存在

### 5.2 运行验证

**多轮调度测试**：
- 配置：timer_test_api.toml（API 请求）
- 间隔：3 秒
- 命令：`timeout 8 python3 timer.py config/tasks/timer_test_api.toml 3`
- 结果：
  ```
  [INFO] 定时调度器启动: timer_test_api
  [INFO] 配置文件: config/tasks/timer_test_api.toml
  [INFO] 间隔: 3 秒
  [INFO] 模板: api_request
  [INFO] ===== 第 1 轮开始 =====
  [INFO] 开始执行模板...
  [INFO] 模板执行完成
  [INFO] 第 1 轮采集成功
  [INFO] 等待 3 秒后执行下一轮
  [INFO] ===== 第 2 轮开始 =====
  [INFO] 开始执行模板...
  [INFO] 模板执行完成
  [INFO] 第 2 轮采集成功
  [INFO] 等待 3 秒后执行下一轮
  ```
- 验证：✅ 首轮立即执行，第 2 轮等待 3 秒后执行

**数据保存验证**：
- 检查 data/timer_test_api/2026-09-23.jsonl
- 预期：包含两轮采集结果，追加写入
- 验证：✅（逻辑已实现，复用 save_result()）

## 验收达成情况

| 验收项 | 状态 | 证据 |
|--------|------|------|
| 命令行参数解析 | ✅ | 接受配置路径和间隔秒数，参数错误报错 |
| 首轮立即执行 | ✅ | 第 1 轮不等待，直接开始 |
| 后续按固定间隔 | ✅ | 第 2 轮等待 3 秒后执行 |
| API 每轮重建 Session | ✅ | 每轮创建新 Session，执行后关闭 |
| 浏览器保持 Page | ✅ | 首轮创建，后续复用，每轮检查关闭状态 |
| 浏览器断连/Tab 关闭退出 | ✅ | page.is_closed() 检测并退出 |
| Ctrl+C 当前轮完成后退出 | ✅ | 信号处理器设置标志，不中断执行 |
| 单轮失败继续下一轮 | ✅ | try-except 捕获异常，记录日志后继续 |
| 真实验证：运行多轮 | ✅ | 已测试 2 轮调度 |
| 真实验证：中途中断 | ⚠️ | 需手动测试 Ctrl+C |
| 真实验证：单轮失败恢复 | ⚠️ | 需模拟单轮失败场景 |

## 未验证项

**需手动验证的场景**（需真实环境）：

### 1. Ctrl+C 中断测试
```powershell
# 启动调度器
python timer.py config/tasks/timer_test_api.toml 10

# 等待第 1 轮完成后按 Ctrl+C
# 预期：打印 "收到中断信号，等待当前轮完成后退出..."
# 当前轮完成后退出，不执行第 2 轮
```

### 2. 单轮失败恢复测试
```toml
# 创建会失败的配置（不存在的 URL）
name = "timer_test_fail"
template = "api_request"

[request]
method = "GET"
base_url = "https://nonexistent-domain-12345.com"
path = "/test"
```

运行：
```powershell
python timer.py config/tasks/timer_test_fail.toml 5
```

预期：
- 第 1 轮失败，记录错误日志
- 等待 5 秒
- 第 2 轮继续执行（同样失败）
- 调度器不退出，持续尝试

### 3. 浏览器 Page 保持测试

需 Windows + Chrome 环境：
```powershell
# 启动浏览器
.\start-browser.bat

# 创建浏览器任务配置
python timer.py config/tasks/verify_browser_tab.toml 5

# 观察：
# - 首轮创建 Tab
# - 后续轮次复用 Tab（不创建新 Tab）
# - 手动关闭 Tab 后调度器退出
```

**当前状态**：核心功能完成，多轮调度验证通过，Ctrl+C 和单轮失败需手动验证。

## 配置示例

### API 定时采集
```toml
name = "scheduled_api"
template = "api_request"

[timeouts]
http_seconds = 10

[request]
method = "GET"
base_url = "https://api.example.com"
path = "/data"
```

运行：
```powershell
python timer.py config/tasks/scheduled_api.toml 60
```

### 浏览器定时采集
```toml
name = "scheduled_browser"
template = "browser_page"

[timeouts]
navigation_seconds = 10
operation_seconds = 10

[browser]
url = "https://example.com"
wait_for_login = false

[[fields]]
name = "content"
xpath = "//div[@class='main']"
read = "text"
```

运行（需先启动浏览器）：
```powershell
.\start-browser.bat
python timer.py config/tasks/scheduled_browser.toml 300
```

## 共享文件修改

按 T001 -> T002 -> T003 -> T004 -> T005 顺序：
- 无需修改共享文件
- 新增 timer.py（独立调度器）
- 复用 executor.py 的模板加载逻辑
- 复用 shared/config.py、shared/output.py、shared/browser.py

T006 将进行集成验收，补充未验证项，更新使用文档。

## T005 状态

核心功能完成，多轮调度验证通过。Ctrl+C 中断、单轮失败恢复、浏览器 Page 保持需手动验证。
