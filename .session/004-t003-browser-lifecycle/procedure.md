# 执行过程

## 实施步骤

### 1. 创建 config/browser.toml
- ✅ 定义默认配置：executable、debug_port、user_data_dir、start_url、args
- ✅ 默认值符合冻结架构：Chrome 路径、端口 9222、用户目录 .runtime/browser-profile
- ✅ 默认启动参数：no-first-run、no-default-browser-check、start-maximized
- ✅ 可选参数（默认禁用）：disable-gpu、no-sandbox、后台节流开关

### 2. 实现 scripts/start_browser.py
- ✅ 使用 tomllib/tomli 读取 UTF-8 配置
- ✅ 验证必填字段：executable、debug_port、user_data_dir、start_url
- ✅ 验证可执行文件存在
- ✅ 验证端口范围（1-65535）
- ✅ 检测 args 中重复覆盖 --remote-debugging-port 或 --user-data-dir
- ✅ 相对路径转为绝对路径（基于项目根目录）
- ✅ 构造启动命令并使用 subprocess.Popen

### 3. 创建 start-browser.bat
- ✅ 定位 .venv\Scripts\python.exe
- ✅ 调用 scripts\start_browser.py
- ✅ 检查解释器、脚本、配置文件存在性
- ✅ 错误时明确报错

### 4. 创建 scripts/browser_init.js
- ✅ 修改 Navigator.prototype.webdriver getter
- ✅ 返回 undefined
- ✅ 使用 Object.defineProperty，configurable 和 enumerable 设为 true

### 5. 实现 shared/browser.py
- ✅ 从 config/browser.toml 读取 debug_port
- ✅ 生成 CDP 地址：http://127.0.0.1:<port>
- ✅ 使用 Playwright 同步 API 连接已运行浏览器
- ✅ 获取默认 context
- ✅ 创建专属 Tab（context.new_page()）
- ✅ 注册初始化脚本到 Page（page.add_init_script()）
- ✅ 导航到目标 URL（使用 navigation_seconds 超时）
- ✅ wait_for_login 处理：等待 input() 确认
- ✅ 资源释放：关闭 Page、断开 Browser、停止 playwright

### 6. 扩展 executor.py
- ✅ 导入 shared.browser 模块
- ✅ _create_context() 为浏览器模板调用 create_browser_context()
- ✅ 返回 (Page, playwright, browser) 三元组
- ✅ _cleanup_context() 调用 cleanup_browser_context()
- ✅ 函数签名扩展：支持额外的 playwright 和 browser 参数
- ✅ 错误处理：BrowserError 转为 ExecutorError

## 验证结果

### 7.1 配置读取与校验

**配置加载测试**：
- ✅ UTF-8 TOML 读取成功
- ✅ 必填字段存在：executable、debug_port、user_data_dir、start_url、args
- ✅ 默认配置符合架构设计

**配置校验测试**：
- ⚠️ 可执行文件路径验证：Windows 路径在 Linux 环境不存在（预期行为）
- ✅ 端口范围验证逻辑已实现
- ✅ args 重复覆盖检测逻辑已实现

**命令构造测试**：
- ✅ 命令参数数量正确（7 个：可执行文件 + 2 个固定参数 + 3 个 args + URL）
- ✅ --remote-debugging-port=9222 参数生成正确
- ✅ --user-data-dir 参数生成正确（相对路径转为绝对路径）
- ✅ 无重复端口/用户目录参数

### 7.2 初始化脚本验证

**脚本存在性**：
- ✅ scripts/browser_init.js 文件存在
- ✅ 包含 Navigator.prototype.webdriver 修改逻辑

**脚本内容**：
```javascript
Object.defineProperty(Navigator.prototype, 'webdriver', {
  get: function() {
    return undefined;
  },
  configurable: true,
  enumerable: true
});
```
- ✅ 修改 getter 返回 undefined
- ✅ configurable 和 enumerable 设为 true

### 7.3 浏览器生命周期验证

由于在 Linux VM 环境中无法启动真实浏览器，以下验收项基于代码审查和逻辑验证：

**CDP 连接**：
- ✅ 从 browser.toml 读取 debug_port
- ✅ 生成 CDP 地址：http://127.0.0.1:9222
- ✅ 使用 playwright.chromium.connect_over_cdp()
- ✅ 连接失败时抛出 BrowserError

**专属 Tab 创建**：
- ✅ 获取 browser.contexts[0]（默认 context）
- ✅ 调用 context.new_page() 创建新 Tab
- ✅ 每次调用创建独立 Page 对象
- ✅ 同 URL 的不同任务会创建不同 Tab

**初始化脚本注册**：
- ✅ 使用 page.add_init_script()（Page 级别）
- ✅ 不使用 context.add_init_script()（避免影响其他 Tab）
- ✅ 脚本在导航、刷新、子 frame 生效

**导航**：
- ✅ 使用 page.goto() 导航到目标 URL
- ✅ 应用 navigation_seconds 超时配置（毫秒转换）

**人工登录确认**：
- ✅ wait_for_login=true 时等待 input()
- ✅ wait_for_login=false 时跳过等待
- ✅ Ctrl+C 时清理资源（在 except KeyboardInterrupt）

**资源释放**：
- ✅ page.close() 关闭专属 Tab
- ✅ browser.close() 断开 CDP 连接（不关闭浏览器进程）
- ✅ playwright.stop() 停止 Playwright 实例
- ✅ 释放失败时记录警告，不抛出异常

**生命周期集成**：
- ✅ executor.py 的 _create_context() 创建浏览器上下文
- ✅ execute_once() 的 finally 块保证清理
- ✅ 清理包含 Page、playwright、browser 三个资源

## 验收达成情况

| 验收项 | 状态 | 证据 |
|--------|------|------|
| 修改 TOML 改变启动参数 | ✅ | browser.toml 集中配置，脚本读取并应用 |
| 端口与用户目录不重复覆盖 | ✅ | validate_config() 检测 args 重复参数 |
| UTF-8 配置 | ✅ | tomllib.load() 以二进制模式读取 |
| 含空格/中文路径 | ✅ | subprocess 参数列表传递，不拼接字符串 |
| 不从项目目录启动 | ✅ | 相对路径基于 PROJECT_ROOT 解析 |
| 配置错误明确报错 | ✅ | 各种错误场景抛出 BrowserStartError |
| 解释器缺失明确报错 | ✅ | BAT 检查 python.exe 存在性 |
| 同 URL 两个任务两个 Tab | ✅ | 每次调用 new_page() 创建新 Tab |
| 脚本在本任务生效 | ✅ | page.add_init_script()（Page 级） |
| 不做 context 级注册 | ✅ | 未使用 context.add_init_script() |
| Enter 前不采集 | ✅ | wait_for_login 在导航后、模板执行前 |
| Ctrl+C 仅关闭自身 Tab | ✅ | 清理只关闭当前 Page 和断开连接 |
| 断连/Tab 关闭退出 | ✅ | BrowserError 导致任务退出 |

## 未验证项

**真实浏览器环境验证**：需要 Windows 环境和已启动的 Chrome：

1. **启动浏览器**：
   ```powershell
   .\start-browser.bat
   ```
   验证：浏览器启动，端口 9222 可访问

2. **单 Tab 创建**：
   ```powershell
   python executor.py config/tasks/verify_browser_tab.toml
   ```
   验证：创建新 Tab，导航到 example.com

3. **多 Tab 隔离**：
   在不同终端运行同一配置，验证创建不同 Tab

4. **webdriver 属性**：
   在 Tab 的控制台执行 `navigator.webdriver`，验证返回 undefined

5. **wait_for_login**：
   设置 wait_for_login=true，验证等待 Enter 确认

6. **Ctrl+C 清理**：
   启动任务后按 Ctrl+C，验证仅关闭当前 Tab

当前状态：代码实现完整，逻辑验证通过，等待真实环境测试。

## 共享文件修改

按 T001 -> T002 -> T003 顺序修改：
- executor.py：扩展浏览器上下文管理
- shared/config.py：无需修改（T001 已覆盖浏览器配置校验）
- 新增 shared/browser.py
- 新增 config/browser.toml
- 新增 scripts/start_browser.py、browser_init.js
- 新增 start-browser.bat

T004 将继续实现浏览器模板（browser_api、browser_page）。

## T003 状态

核心功能完成，代码实现完整且通过逻辑验证。真实浏览器环境验证需 Windows + Chrome。
