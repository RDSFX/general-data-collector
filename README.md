# data-collector

轻量级数据采集工具，支持 API 请求和浏览器页面采集，适用于定时获取数据并保存为历史记录。

## 功能特性

- **API 采集**：支持普通 HTTP 请求和 OKX API 签名认证
- **浏览器采集**：支持浏览器内 JavaScript 执行和页面 XPath 提取
- **单次执行**：executor.py 执行单轮采集
- **定时调度**：timer.py 按固定间隔持续采集
- **历史记录**：JSONL 格式追加保存，按日期分文件
- **日志脱敏**：自动隐藏敏感信息（API 密钥、Token 等）
- **配置驱动**：TOML 配置文件，UTF-8 编码

## 快速开始

详见 [ENV.md](ENV.md) 了解完整的环境配置步骤。

### API 采集示例

创建配置文件 `config/tasks/my_api.toml`：

```toml
name = "my_api"
template = "api_request"

[timeouts]
http_seconds = 10

[request]
method = "GET"
base_url = "https://api.example.com"
path = "/data"

[request.headers]
Accept = "application/json"
```

**单次执行**：
```powershell
python executor.py config/tasks/my_api.toml
```

**定时调度**：
```powershell
python timer.py config/tasks/my_api.toml
```

需要在配置文件中添加 `[schedule]` 节：
```toml
[schedule]
interval_seconds = 60  # 每 60 秒采集一次
```

采集结果保存在 `data/my_api/<日期>.jsonl`。

### 浏览器采集示例

**启动浏览器**：
```powershell
.\start-browser.bat
```

创建配置文件 `config/tasks/my_browser.toml`：

```toml
name = "my_browser"
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

**单次执行**：
```powershell
python executor.py config/tasks/my_browser.toml
```

**定时调度**：
```powershell
python timer.py config/tasks/my_browser.toml
```

需要在配置文件中添加 `[schedule]` 节：
```toml
[schedule]
interval_seconds = 300  # 每 5 分钟采集一次
```

## 项目结构

```
data-collector/
├── config/
│   ├── browser.toml          # 浏览器启动配置
│   └── tasks/                # 任务配置目录
│       ├── example_api.toml
│       └── example_browser_page.toml
├── data/                     # 采集数据（按任务分目录）
│   └── <task_name>/
│       └── <YYYY-MM-DD>.jsonl
├── logs/                     # 日志文件（按任务分目录）
│   └── <task_name>/
│       └── <YYYY-MM-DD>.log
├── scripts/
│   ├── start_browser.py      # 浏览器启动脚本
│   ├── browser_init.js       # 浏览器初始化脚本
│   └── request.js            # 浏览器内请求封装
├── shared/
│   ├── config.py             # 配置加载与校验
│   ├── output.py             # 结果保存与日志
│   ├── http.py               # HTTP 请求模块
│   └── browser.py            # 浏览器生命周期管理
├── template/
│   ├── api_request.py        # 普通 API 请求模板
│   ├── okx_api.py            # OKX API 签名模板
│   ├── browser_api.py        # 浏览器内 API 请求模板
│   └── browser_page.py       # 浏览器页面采集模板
├── executor.py               # 单次执行入口
├── timer.py                  # 定时调度入口
├── start-browser.bat         # 浏览器启动入口（Windows）
├── requirements.txt          # Python 依赖
├── README.md                 # 使用说明（本文件）
└── ENV.md                    # 环境配置说明
```

## 支持的模板

### API 模板

#### 1. api_request - 普通 API 请求

支持常规 HTTP 请求（GET、POST 等），2xx 响应视为成功。

**配置示例**：
```toml
name = "example_api"
template = "api_request"

[timeouts]
http_seconds = 10

[request]
method = "POST"
base_url = "https://api.example.com"
path = "/endpoint"

[request.headers]
Authorization = "Bearer YOUR_TOKEN"
Content-Type = "application/json"

[request.json]
key = "value"
```

#### 2. okx_api - OKX API 签名认证

支持 HMAC-SHA256 签名认证，从环境变量读取凭据。

**环境变量**：
```powershell
$env:OKX_API_KEY="your_api_key"
$env:OKX_SECRET_KEY="your_secret_key"
$env:OKX_PASSPHRASE="your_passphrase"
```

**配置示例**：
```toml
name = "example_okx"
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

### 浏览器模板

#### 3. browser_api - 浏览器内 API 请求

执行用户提供的 JavaScript 脚本，返回 JSON 对象。

**JavaScript 脚本示例** (`scripts/my_request.js`)：
```javascript
(async () => {
  const result = await window.request('https://api.example.com/data', {
    method: 'GET',
    headers: { 'Accept': 'application/json' }
  });
  return result.data;
})();
```

**配置示例**：
```toml
name = "example_browser_api"
template = "browser_api"

[timeouts]
navigation_seconds = 10
operation_seconds = 30

[browser]
url = "https://example.com"
wait_for_login = false
script = "scripts/my_request.js"
```

#### 4. browser_page - 浏览器页面采集

执行动作序列并通过 XPath 提取字段。

**配置示例**：
```toml
name = "example_browser_page"
template = "browser_page"

[timeouts]
navigation_seconds = 10
operation_seconds = 10

[browser]
url = "https://example.com"
wait_for_login = false

# 动作序列（可选）
[[actions]]
type = "waitForSelector"
selector = "#content"

[[actions]]
type = "click"
selector = "button.load-more"

[[actions]]
type = "wait"
duration = 1000

# 字段提取
[[fields]]
name = "title"
xpath = "//h1"
read = "text"
multiple = false
type = "string"

[[fields]]
name = "links"
xpath = "//a[@class='item']"
read = "attribute:href"
multiple = true
type = "string"

[[fields]]
name = "count"
xpath = "//span[@class='count']"
read = "text"
multiple = false
type = "number"
```

**支持的动作类型**：
- `refresh`：刷新当前页面
- `click`：点击元素（CSS 选择器）
- `wait`：等待固定时间（毫秒）
- `fill`：填写表单字段
- `select`：选择下拉选项
- `waitForSelector`：等待元素出现

**支持的提取类型**：
- `text`：文本内容
- `html`：HTML 内容
- `attribute:<name>`：属性值（如 `attribute:href`）

**支持的值类型**：
- `string`：字符串（默认）
- `number`：数值（整数或浮点数）
- `boolean`：布尔值（true/false/1/0/yes/no）

## 配置文件格式

所有配置文件使用 TOML 格式，UTF-8 编码。

### 通用字段

```toml
name = "task_name"          # 任务名称（字母、数字、下划线、连字符）
template = "api_request"    # 模板名称

[timeouts]
http_seconds = 10           # HTTP 请求超时（API 模板）
navigation_seconds = 10     # 页面导航超时（浏览器模板）
operation_seconds = 10      # 操作超时（浏览器模板）
```

### API 模板字段

```toml
[request]
method = "GET"              # HTTP 方法
base_url = "https://..."    # 基础 URL
path = "/api/endpoint"      # 路径

[request.params]            # 查询参数（可选）
key = "value"

[request.headers]           # 请求头（可选）
Authorization = "Bearer ..."

[request.json]              # JSON 请求体（可选，与 body 互斥）
key = "value"

[request.body]              # 文本请求体（可选，与 json 互斥）
# body = "raw text"
```

### 浏览器模板字段

```toml
[browser]
url = "https://..."         # 目标 URL
wait_for_login = false      # 是否等待人工登录确认
script = "path/to/script.js" # JavaScript 脚本路径（browser_api）

[[actions]]                 # 动作序列（browser_page，可选）
type = "click"
selector = "button.submit"

[[fields]]                  # 字段提取（browser_page）
name = "field_name"
xpath = "//div[@id='content']"
read = "text"
multiple = false
type = "string"
```

## 常见问题

### 1. 浏览器相关

**Q: 启动浏览器失败？**

A: 检查 `config/browser.toml` 中的 `executable` 路径是否正确。默认为：
```toml
executable = "C:/Program Files/Google/Chrome/Application/chrome.exe"
```

**Q: CDP 连接失败？**

A: 确保浏览器已启动且端口可访问：
```powershell
.\start-browser.bat
```

访问 http://127.0.0.1:9222 确认端口开放。

**Q: navigator.webdriver 检测？**

A: 初始化脚本已自动隐藏 `navigator.webdriver` 属性，但不承诺规避所有自动化检测。

### 2. 采集任务相关

**Q: 单轮失败后如何恢复？**

A: 使用 `timer.py` 定时调度，单轮失败不影响下一轮：
```powershell
python timer.py config/tasks/my_task.toml
```

配置文件需包含：
```toml
[schedule]
interval_seconds = 60
```

**Q: 如何优雅停止定时任务？**

A: 按 `Ctrl+C`，调度器会在当前轮完成后退出。

**Q: 日志在哪里？**

A: 日志保存在 `logs/<task_name>/<日期>.log`，自动按日期分文件。

### 3. 配置相关

**Q: 路径使用相对路径还是绝对路径？**

A: 支持两种方式。相对路径基于项目根目录解析。

**Q: 如何保护敏感信息？**

A: 使用环境变量存储凭据（如 OKX API 密钥），不要写在配置文件中。日志系统会自动脱敏关键字段。

## 许可证

本项目仅供个人学习和研究使用。

## 贡献

欢迎提交 Issue 和 Pull Request。

## 更多信息

- [环境配置说明](ENV.md)
- [任务计划](docs/task-plan.md)
- [架构设计](docs/architecture.md)
