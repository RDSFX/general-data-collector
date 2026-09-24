---
status: frozen
finalized_on: "2026-09-23"
source_session: "001"
amended_on: "2026-09-24"
amended_by: "D-005, E-003, E-004"
---

# 配置样例与接口

来源：001。用户已确认本文所列配置结构、固定输出目录和模板/JS 接口，并于 2026-09-23 明确“确认，准许冻结当前设计”。本文随 [架构设计](architecture.md) 一并冻结；后续接口或范围变更按基线变更规则处理。以下示例尚未创建为实际配置文件，不代表功能已经实现。

## 公共约定

- 每个 TOML 对应一个任务，顶层 name、template 必填，模板名为四个固定名称之一。
- timer 需要 [schedule].interval_seconds，executor 单次执行可省略整个 schedule。
- [schedule] 可选字段：
  - jitter_percent（0-100 整数）用于随机抖动，避免整点流量尖峰；缺省为 0（无抖动）
  - max_rounds（正整数）用于限制总采集次数，达到后自动停止；缺省为 0（无限循环）
- [timeouts] 可省略或只覆盖部分项，http_seconds、navigation_seconds、operation_seconds 缺省均为 10 秒；配置值必须为正数。
- [request] 用于三种 API 模板；params 为查询参数、headers 为请求头，json 与 body 互斥。复杂嵌套 JSON 可用 TOML 子表表达，body 为原始 UTF-8 文本。不引入通用字符串插值或配置表达式。
- [browser] 只用于浏览器模板，url 为任务 Tab 的初始页面；请求 API 的地址由 request 单独定义。浏览器启动与 CDP 端口来自公共 config/browser.toml。
- data/<name>/ 和 logs/<name>/ 自动生成，第一版不增加独立输出路径设置。
- 示例 URL 为占位地址；真实使用需替换。所有文件使用 UTF-8。

## 普通 API

建议文件：config/tasks/example_api.toml。

```toml
name = "example_api"
template = "api_request"

[schedule]
interval_seconds = 60
# jitter_percent = 20  # 可选：基准间隔 ±20% 随机抖动
# max_rounds = 10      # 可选：采集 10 轮后自动停止

[timeouts]
http_seconds = 10

[request]
method = "GET"
base_url = "https://example.com"
path = "/api/items"

[request.params]
limit = 10

[request.headers]
Accept = "application/json"
```

## OKX API

建议文件：config/tasks/okx_balance.toml。三个环境变量必须事先配置，TOML 中不保存实际密钥。

```toml
name = "okx_balance"
template = "okx_api"

[schedule]
interval_seconds = 60

[request]
method = "GET"
base_url = "https://www.okx.com"
path = "/api/v5/account/balance"

[request.params]
ccy = "USDT"

[auth]
api_key_env = "OKX_API_KEY"
secret_key_env = "OKX_SECRET_KEY"
passphrase_env = "OKX_PASSPHRASE"
```

示例为只读查询。真实请求需适配用户账号对应的可用服务地址，签名头由模板生成。

## 浏览器内 API

建议文件：config/tasks/browser_api.toml。

```toml
name = "browser_api"
template = "browser_api"

[schedule]
interval_seconds = 60

[timeouts]
http_seconds = 10
navigation_seconds = 10
operation_seconds = 10

[browser]
url = "https://example.com/account"
wait_for_login = true
script = "scripts/example_request.js"

[request]
method = "GET"
base_url = "https://example.com"
path = "/api/items"

[request.params]
limit = 10

[request.headers]
Accept = "application/json"
```

## XPath 页面采集

建议文件：config/tasks/browser_page.toml。无前置动作时省略所有 actions。

> 2026-09-24 变更：以下动作/字段接口为 T004 实施后的实际基线（selector 体系 + refresh），取代本文档最初冻结版本中的 xpath/x-y/delta 动作设计；变更记录见 [D-005](decisions.md#d-005)。

```toml
name = "browser_page"
template = "browser_page"

[schedule]
interval_seconds = 60

[browser]
url = "https://example.com/market"
wait_for_login = false

[[actions]]
type = "refresh"

[[actions]]
type = "waitForSelector"
selector = "h1"

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
```

页面动作字段如下：

| type | 参数 | 超时类别 |
|------|------|----------|
| refresh | 无 | navigation_seconds |
| click | selector（CSS，Playwright 语法） | operation_seconds |
| fill | selector、value（文本） | operation_seconds |
| select | selector、value（选项值） | operation_seconds |
| waitForSelector | selector，等待元素出现 | operation_seconds |
| wait | duration，毫秒，非负等待时长 | 按自身时长执行 |

字段提取使用 xpath 定位，read 为 text、html 或 attribute:<attribute名称>；type 为 string、number 或 boolean，用于结果值转换。单值字段取第一个匹配；多值保留匹配顺序。字段 name 在任务内不重复。缺失与空值行为遵循已确认规则。

## 两个接口

Python 模板统一入口为 run(config, context)，返回可 JSON 序列化的结果。config 为已校验任务配置；context 提供已初始化且供任务持续复用的资源，例如 requests 会话或任务 Page。模板完成请求、检查成功状态和提取数据；执行器统一追加任务名/采集时间并落盘。采集异常交由执行器按已确认规则处理。

浏览器请求脚本安装 window.__collectorRequest(request)，返回 Promise，结果为 {status, data}。传入对象含请求 method、base_url、path、params、headers 及可选 json/body，并携带从 timeouts.http_seconds 派生的 timeout_ms。脚本负责发起请求、读取完整响应体、必要的网站 token 和超时取消；结果以实际 HTTP 状态与已解析 JSON/文本返回。模板依据 status 判断成功，只将 data 交给执行器保存。

Python 侧也需有有界的请求等待，不因自定义 JS 未处理超时而永久挂起；超时后处理未结束的请求，避免下一轮与旧请求重叠。具体实现方式在实施时验证，不新增第四类超时配置。

请求函数在每轮执行前检查，刷新后缺失时重新注入；browser_init.js 则由 Page 初始化机制在新文档中自动执行。
