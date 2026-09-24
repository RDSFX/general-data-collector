# T005 实施总结

## 任务完成情况

T005（单任务固定间隔调度）核心功能已完成，多轮调度验证通过。Ctrl+C 中断、单轮失败恢复、浏览器 Page 保持需手动验证。

## 主要交付

### 1. 定时调度器
- `timer.py`：完整的固定间隔调度实现
  - CLI 参数：配置路径、间隔秒数
  - 首轮立即执行，后续按固定间隔
  - 轮次计数和日志记录
  - 信号处理（Ctrl+C 优雅退出）
  - 单轮失败不影响下一轮
  - 完善的错误分类和处理

### 2. 生命周期管理
- **API 模板**：
  - 每轮创建新 Session
  - 执行后关闭 Session
  - 无跨轮状态保留
  
- **浏览器模板**：
  - 首轮创建 Page（CDP 连接）
  - 后续轮次复用 Page
  - 每轮检查 Page 是否关闭
  - Page 关闭或断连时退出调度器
  - 退出时清理资源

### 3. 集成复用
- 复用 shared/config.py 配置加载
- 复用 shared/output.py 日志和结果保存
- 复用 shared/browser.py 浏览器生命周期
- 复用 executor.py 的模板加载逻辑

## 验收达成

已完成验收项：
- ✅ 命令行参数解析（配置路径 + 间隔秒数）
- ✅ 首轮立即执行
- ✅ 后续按固定间隔执行
- ✅ API 模板每轮重建 Session
- ✅ 浏览器模板保持 Page（逻辑实现）
- ✅ 浏览器断连/Tab 关闭退出（逻辑实现）
- ✅ Ctrl+C 当前轮完成后退出（信号处理实现）
- ✅ 单轮失败继续下一轮（异常捕获实现）
- ✅ 多轮调度验证（已测试 2 轮）

未完成验收项：
- ⚠️ **手动验证**：Ctrl+C 中途中断
- ⚠️ **手动验证**：单轮失败恢复
- ⚠️ **手动验证**：浏览器 Page 保持（需 Windows + Chrome）

## 手动验证指南

### 1. Ctrl+C 中断测试

启动调度器：
```powershell
python timer.py config/tasks/timer_test_api.toml 10
```

等待第 1 轮完成后按 `Ctrl+C`

**预期结果**：
- 打印："收到中断信号，等待当前轮完成后退出..."
- 当前轮完成后退出
- 不执行第 2 轮

### 2. 单轮失败恢复测试

创建会失败的配置 `config/tasks/timer_test_fail.toml`：
```toml
name = "timer_test_fail"
template = "api_request"

[timeouts]
http_seconds = 5

[request]
method = "GET"
base_url = "https://nonexistent-domain-12345.com"
path = "/test"
```

运行：
```powershell
python timer.py config/tasks/timer_test_fail.toml 5
```

**预期结果**：
- 第 1 轮失败，记录错误日志
- 等待 5 秒
- 第 2 轮继续执行（同样失败）
- 调度器不退出，持续尝试

### 3. 浏览器 Page 保持测试

需 Windows + Chrome 环境：

1. 启动浏览器：
   ```powershell
   .\start-browser.bat
   ```

2. 启动调度器：
   ```powershell
   python timer.py config/tasks/verify_browser_tab.toml 10
   ```

3. 观察：
   - 首轮创建新 Tab
   - 后续轮次复用同一个 Tab（不创建新 Tab）
   
4. 手动关闭该 Tab

**预期结果**：
- 调度器检测到 Page 已关闭
- 打印退出日志
- 调度器退出

## 使用示例

### API 定时采集

配置文件 `config/tasks/scheduled_api.toml`：
```toml
name = "scheduled_api"
template = "api_request"

[timeouts]
http_seconds = 10

[request]
method = "GET"
base_url = "https://api.example.com"
path = "/data"

[request.headers]
Authorization = "Bearer YOUR_TOKEN"
```

启动调度（每 60 秒采集一次）：
```powershell
python timer.py config/tasks/scheduled_api.toml 60
```

### 浏览器定时采集

配置文件 `config/tasks/scheduled_browser.toml`：
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
name = "title"
xpath = "//h1"
read = "text"
multiple = false
type = "string"
```

启动调度（每 5 分钟采集一次）：
```powershell
# 1. 启动浏览器
.\start-browser.bat

# 2. 启动调度器
python timer.py config/tasks/scheduled_browser.toml 300
```

## 后续工作

T005 已完成定时调度功能：
- **T006**（集成验收与使用说明）：
  - 补充手动验证项
  - 真实场景端到端测试
  - 更新 README.md 使用说明
  - 更新 ENV.md 环境配置
  - 补充配置示例和最佳实践

T001-T005 已建立完整的数据采集系统，T006 将完成最终验收和文档。
