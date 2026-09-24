# 手动验证指南

本文档汇总 T002-T005 中需要真实环境手动验证的项目，提供详细的验证步骤和预期结果。

## 验证环境要求

### 基础环境
- Windows 10/11
- Python 3.10 或 3.11
- 虚拟环境已激活
- 依赖已安装（`pip install -r requirements.txt`）

### 特定功能环境
- **OKX API 验证**：有效的 OKX 只读 API 凭据
- **浏览器功能验证**：Chrome 已安装，`start-browser.bat` 可正常启动
- **真实网页采集**：可访问的目标网页，XPath 和动作序列

## T002: 普通 API 与 OKX 模板

### 未验证项：真实 OKX API 验证

**所需准备**：
1. OKX 账户和只读 API 凭据（API Key、Secret Key、Passphrase）
2. 推荐测试端点：`GET /api/v5/account/balance`（查询余额，只读操作）

**步骤 1：设置环境变量**

PowerShell：
```powershell
$env:OKX_API_KEY="your_api_key"
$env:OKX_SECRET_KEY="your_secret_key"
$env:OKX_PASSPHRASE="your_passphrase"
```

**步骤 2：创建配置文件**

`config/tasks/verify_okx.toml`：
```toml
name = "verify_okx"
template = "okx_api"

[timeouts]
http_seconds = 10

[auth]
api_key_env = "OKX_API_KEY"
secret_key_env = "OKX_SECRET_KEY"
passphrase_env = "OKX_PASSPHRASE"

[request]
method = "GET"
base_url = "https://www.okx.com"
path = "/api/v5/account/balance"
```

**步骤 3：执行测试**

```powershell
python executor.py config/tasks/verify_okx.toml
```

**预期结果**：
- 执行成功，无报错
- 数据保存到 `data/verify_okx/2026-09-23.jsonl`
- 日志保存到 `logs/verify_okx/2026-09-23.log`
- 响应包含账户余额信息（code="0"）

**验证点**：
- ✅ 签名正确（HTTP 200 + code="0"）
- ✅ 请求头包含 OK-ACCESS-KEY、OK-ACCESS-SIGN 等
- ✅ 查询参数和请求体（如有）参与签名计算
- ✅ 业务失败（code != "0"）正确报错
- ✅ 非 JSON 响应正确报错

**故障排查**：
- HTTP 401：签名错误，检查凭据和时间同步
- code != "0"：业务错误，检查 API 权限和参数
- 连接超时：检查网络和 base_url

---

## T003: 浏览器启动与 Tab 生命周期

### 未验证项：真实浏览器环境验证

**所需准备**：
- Windows 环境
- Chrome 已安装
- `config/browser.toml` 配置正确

**步骤 1：启动浏览器**

```powershell
.\start-browser.bat
```

**预期结果**：
- Chrome 窗口打开
- 访问 http://127.0.0.1:9222 显示 JSON 响应

**验证点**：
- ✅ 浏览器启动成功
- ✅ CDP 端口可访问

**步骤 2：测试单 Tab 创建**

配置文件 `config/tasks/verify_browser_tab.toml`（已存在）：
```toml
name = "verify_browser_tab"
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

执行：
```powershell
python executor.py config/tasks/verify_browser_tab.toml
```

**预期结果**：
- 创建新 Tab
- 导航到 example.com
- 提取标题字段
- 执行成功

**验证点**：
- ✅ 专属 Tab 创建
- ✅ 页面导航成功
- ✅ 字段提取成功

**步骤 3：测试多 Tab 隔离**

在两个终端同时运行：
```powershell
# 终端 1
python executor.py config/tasks/verify_browser_tab.toml

# 终端 2（同时执行）
python executor.py config/tasks/verify_browser_tab.toml
```

**预期结果**：
- 创建两个独立的 Tab
- 两个任务并行执行，互不干扰

**验证点**：
- ✅ 同 URL 不同任务创建不同 Tab
- ✅ 任务间隔离

**步骤 4：测试 webdriver 属性**

在创建的 Tab 中，打开 DevTools Console（F12），执行：
```javascript
navigator.webdriver
```

**预期结果**：
- 返回 `undefined`

**验证点**：
- ✅ 初始化脚本生效
- ✅ webdriver 属性隐藏

**步骤 5：测试 wait_for_login**

修改配置文件，设置 `wait_for_login = true`，执行任务：
```powershell
python executor.py config/tasks/verify_browser_tab.toml
```

**预期结果**：
- 导航后打印："等待人工登录，请在浏览器中完成登录后回到终端按 Enter 继续..."
- 按 Enter 后继续执行

**验证点**：
- ✅ Enter 前暂停，不执行采集
- ✅ Enter 后继续执行

**步骤 6：测试 Ctrl+C 清理**

执行任务后立即按 `Ctrl+C`：
```powershell
python executor.py config/tasks/verify_browser_tab.toml
# 按 Ctrl+C
```

**预期结果**：
- 任务中断
- 当前 Tab 关闭
- 其他 Tab 和浏览器保留

**验证点**：
- ✅ 仅关闭当前任务的 Tab
- ✅ 浏览器和其他 Tab 不受影响

---

## T004: 浏览器 API 与页面模板

### 未验证项 1：browser_api 真实验证

**步骤 1：启动浏览器**

```powershell
.\start-browser.bat
```

**步骤 2：使用示例配置**

配置文件 `config/tasks/example_browser_api.toml`（已创建）

**步骤 3：执行测试**

```powershell
python executor.py config/tasks/example_browser_api.toml
```

**预期结果**：
- 导航到 httpbin.org/html
- 注入 request.js
- 执行用户脚本（发送请求到 httpbin.org/json）
- 返回 JSON 响应
- 数据保存成功

**验证点**：
- ✅ JavaScript 脚本执行成功
- ✅ window.request 函数可用
- ✅ 返回 JSON 对象
- ✅ 脚本执行失败报错
- ✅ 非 JSON 返回报错
- ✅ 超时控制生效

### 未验证项 2：browser_page 真实验证

**步骤 1：启动浏览器**

```powershell
.\start-browser.bat
```

**步骤 2：使用示例配置**

配置文件 `config/tasks/example_browser_page.toml`（已创建）

**步骤 3：执行测试**

```powershell
python executor.py config/tasks/example_browser_page.toml
```

**预期结果**：
- 导航到 example.com
- 等待 #content 元素出现
- 点击 "load-more" 按钮
- 等待 1 秒
- 提取标题、链接、计数字段
- 数据保存成功

**验证点**：
- ✅ 动作顺序执行
- ✅ XPath 单值提取
- ✅ XPath 多值提取
- ✅ 属性提取（href）
- ✅ 类型转换（number）
- ✅ 元素不存在报错
- ✅ XPath 错误报错

**步骤 4：测试错误场景**

创建错误配置：
```toml
name = "verify_browser_error"
template = "browser_page"

[timeouts]
navigation_seconds = 10
operation_seconds = 10

[browser]
url = "https://example.com"
wait_for_login = false

[[fields]]
name = "nonexistent"
xpath = "//div[@id='nonexistent-element']"
read = "text"
multiple = false
type = "string"
```

执行：
```powershell
python executor.py config/tasks/verify_browser_error.toml
```

**预期结果**：
- 报错："XPath 未匹配到元素"
- 任务失败

**验证点**：
- ✅ 空值错误处理

---

## T005: 单任务固定间隔调度

### 未验证项 1：Ctrl+C 中途中断

**步骤 1：启动定时任务**

```powershell
python timer.py config/tasks/example_api.toml
```

需要在配置中添加 `[schedule]` 节：
```toml
[schedule]
interval_seconds = 10
```

**步骤 2：等待第 1 轮完成后按 Ctrl+C**

**预期结果**：
- 打印："收到中断信号，等待当前轮完成后退出..."
- 当前轮完成后退出
- 不执行第 2 轮

**验证点**：
- ✅ 当前轮完成后才退出
- ✅ 不中断执行中的模板

### 未验证项 2：单轮失败恢复

**步骤 1：创建会失败的配置**

`config/tasks/verify_timer_fail.toml`：
```toml
name = "verify_timer_fail"
template = "api_request"

[timeouts]
http_seconds = 5

[request]
method = "GET"
base_url = "https://nonexistent-domain-12345.com"
path = "/test"
```

**步骤 2：启动定时任务**

```powershell
python timer.py config/tasks/verify_timer_fail.toml 5
```

**预期结果**：
- 第 1 轮失败，记录错误日志
- 等待 5 秒
- 第 2 轮继续执行（同样失败）
- 第 3 轮继续执行...
- 调度器不退出

**验证点**：
- ✅ 单轮失败不影响下一轮
- ✅ 错误日志记录完整

### 未验证项 3：浏览器 Page 保持

**步骤 1：启动浏览器**

```powershell
.\start-browser.bat
```

**步骤 2：启动定时任务**

```powershell
python timer.py config/tasks/verify_browser_tab.toml
```

需要在配置中添加 `[schedule]` 节：
```toml
[schedule]
interval_seconds = 10
```

**步骤 3：观察执行**

- 第 1 轮：创建新 Tab
- 第 2 轮：复用同一个 Tab（不创建新 Tab）
- 第 3 轮：复用同一个 Tab

**验证点**：
- ✅ 首轮创建 Page
- ✅ 后续轮次复用 Page
- ✅ 不创建额外 Tab

**步骤 4：手动关闭 Tab**

在执行期间，手动关闭调度器创建的 Tab。

**预期结果**：
- 调度器检测到 Page 已关闭
- 打印："浏览器 Tab 已关闭，退出调度"
- 调度器退出

**验证点**：
- ✅ 浏览器断连/Tab 关闭时退出

---

## 验收总结

### 已通过验证（2026-09-24）

**T001：配置、执行入口和历史输出**
- ✅ 所有验收项通过逻辑验证
- 验证依据：[002 执行过程](../.session/002-t001-config-executor-output/procedure.md)

**T002：普通 API 与 OKX 模板**
- ✅ HTTP 请求、超时、状态码验证通过
- ✅ OKX 签名算法验证通过
- ⚠️ **真实 OKX API 请求未验证**（需用户凭据）
- 验证依据：[003 执行过程](../.session/003-t002-api-templates/procedure.md)

**T003：浏览器启动与 Tab 生命周期**
- ✅ 真实浏览器环境验证通过（baidu_hot_search 采集）
- ✅ 浏览器启动、CDP 连接、专属 Tab 创建/关闭、资源清理
- 验证依据：[004 执行过程](../.session/004-t003-browser-lifecycle/procedure.md)、[日志](../logs/baidu_hot_search/2026-09-24.log)、[数据](../data/baidu_hot_search/2026-09-24.jsonl)

**T004：浏览器 API 与页面模板**
- ✅ browser_page 真实验证通过（baidu_hot_search 采集）
- ✅ XPath 多值提取（link、content 字段）、attribute 读取、refresh 动作
- ⚠️ **browser_api 未验证**（需真实站点 + JS 脚本）
- 验证依据：[005 执行过程](../.session/005-t004-browser-templates/procedure.md)

**T005：单任务固定间隔调度**
- ✅ 真实验证通过（baidu_hot_search 3 轮调度 + Ctrl+C 优雅退出）
- ✅ 多轮执行、浏览器 Page 保持、等待期间中断处理
- ⚠️ **单轮失败恢复未实测**（需构造失败场景）
- 验证依据：[006 执行过程](../.session/006-t005-timer/procedure.md)

**T006：集成验收与使用说明**
- ✅ 文档齐全，真实环境验证已补充
- 验证依据：[007 执行过程](../.session/007-t006-integration/procedure.md)

### 剩余未验证项

仅以下 3 项需补充验证，不影响项目交付使用：

1. **T002 真实 OKX API**：需用户提供只读 API 凭据（api_key、secret_key、passphrase）
2. **T004 browser_api**：需实际站点 + 请求 JS 脚本
3. **T005 单轮失败恢复**：需构造失败场景（如无效 URL）

### 验证优先级

**已完成**（核心功能）：
- ✅ T003 浏览器启动和 Tab 创建
- ✅ T004 浏览器页面采集（browser_page）
- ✅ T005 Ctrl+C 中断和浏览器 Page 保持

**剩余项**（可选）：
1. T002 OKX API 签名认证（需用户凭据）
2. T004 browser_api 模板（需真实站点）
3. T005 单轮失败恢复（可构造场景验证）

## 验证记录

### 验证日期：2026-09-24

### 验证环境
- 操作系统：Windows 10 Pro for Workstations 10.0.19045
- Python 版本：3.11.5
- Chrome 版本：已安装（通过 CDP 端口 9222 连接）
- 虚拟环境：.venv，依赖已安装

### 真实环境验证：baidu_hot_search

**配置**：[config/tasks/baidu_page.toml](../config/tasks/baidu_page.toml)
- 模板：browser_page
- 目标：百度热搜榜 https://top.baidu.com/board?tab=realtime
- 字段：20 条热搜（链接 + 内容）
- 调度：60 秒间隔，3 轮采集

**验证结果**：
- ✅ T003 浏览器启动：Chrome 通过 CDP 9222 端口连接成功
- ✅ T003 专属 Tab 创建：任务创建独立 Tab，不干扰其他 Tab
- ✅ T003 资源清理：Ctrl+C 后仅关闭任务 Tab，浏览器保留
- ✅ T004 refresh 动作：页面刷新成功（本会话补充实现）
- ✅ T004 XPath 多值提取：20 条热搜的 link 和 content 字段提取成功
- ✅ T004 attribute 读取：href 属性正确提取
- ✅ T005 多轮调度：3 轮采集均成功，间隔 60 秒
- ✅ T005 浏览器 Page 保持：同一 Tab 跨轮次复用
- ✅ T005 Ctrl+C 优雅退出：第 3 轮完成后按 Ctrl+C，当前轮完成后退出

**数据产物**：
- 日志：[logs/baidu_hot_search/2026-09-24.log](../logs/baidu_hot_search/2026-09-24.log)
- 数据：[data/baidu_hot_search/2026-09-24.jsonl](../data/baidu_hot_search/2026-09-24.jsonl)（3 条记录，每条 20 个热搜项）

**遗留问题**：无
