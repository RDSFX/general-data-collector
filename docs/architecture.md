---
status: frozen
finalized_on: "2026-09-23"
source_session: "001"
amended_on: "2026-09-24"
amended_by: "D-005"
---

# 架构设计

data-collector：通过 TOML 配置驱动的本地轻量采集工具。

设计基线已于 2026-09-23 冻结，来源会话 001。用户在逐项确认需求、默认值与接口后，针对任务计划及冻结请求明确回复：“确认，准许冻结当前设计”。本文件与 config-examples.md 共同定义实施基线；日常进度见 task-progress.md，范围、接口和验收变更须经用户确认。001 仅完成设计，业务代码尚未实现。

## 需求与范围

| ID | 已确认需求 |
|----|------------|
| R001 | Python 主体、JavaScript 浏览器脚本；模板放 template/、TOML 配置放 config/、计时器和执行器在根目录。 |
| R002 | 支持普通 API、OKX 签名 API、浏览器内 JS 请求 API、XPath 页面采集。 |
| R003 | 页面采集支持顺序执行刷新、点击、双击、滑动和等待；动作失败结束本轮。 |
| R004 | 一个配置参数启动一个任务进程；多个任务由用户另开终端，不自动扫描并启动全部配置。 |
| R005 | 本轮结束后等待固定间隔再执行，同一任务不重叠；不考虑重启恢复或停机补采。 |
| R006 | BAT 作为浏览器启动入口，启动参数存入独立配置文件便于修改；程序连接 CDP，每个浏览器任务新建专属 Tab，同 URL 也不共享 Tab。 |
| R007 | 任务期间持续复用自己的 Tab，正常结束或 Ctrl+C 时关闭该 Tab，保留浏览器。 |
| R008 | 任务 Tab 的初始化 JS 使 navigator.webdriver 读取为 undefined，刷新、跳转后继续生效。 |
| R009 | wait_for_login=true 时，打开 Tab 后等用户在终端按 Enter；只在启动时确认一次，不自动检测登录过期。 |
| R010 | 成功结果追加到 JSONL，按任务、日期分文件，记录任务名称、采集时间和结果数据。 |
| R011 | API 保存完整响应数据，JSON 为结构化数据，其他响应为文本；XPath 支持文本/属性、单值/多值。 |
| R012 | 本轮失败记日志，间隔后继续；启动配置错误、模板不存在、CDP 断开或任务 Tab 关闭时退出。 |

不包含统一多任务管理、跨进程锁、共享 Tab、自动登录、立即重试、热更新、数据库、管理页面、通用清洗/去重/字段计算、条件或循环动作语法。

## 技术方案与结构

已确认使用 Python、标准库 tomllib、requests 和 Playwright 同步 API；签名使用 hmac/hashlib/base64，调度、JSONL 和日志使用标准库。Python 最低版本为 3.11，与本地环境一致。单进程单任务，不需要线程池或异步调度框架。依赖选型于 2026-09-23 在 001 会话中获用户回复“可以，收尾吧”确认。环境见 [ENV.md](../ENV.md)。

以下为计划结构，业务文件尚未创建：

```text
data-collector/
  start-browser.bat
  timer.py
  executor.py
  requirements.txt
  template/
    api_request.py
    okx_api.py
    browser_api.py
    browser_page.py
  shared/
    config.py
    output.py
    http.py
    browser.py
  config/
    browser.toml
    tasks/*.toml
  scripts/
    start_browser.py
    browser_init.js
    example_request.js
  data/<task_name>/<YYYY-MM-DD>.jsonl
  logs/<task_name>/<YYYY-MM-DD>.log
  .runtime/browser-profile/
  tests/
  docs/
  .session/
```

现有 src/.gitkeep 保留占位，不要求把源码迁入 src/。

| 文件 / 模块 | 职责 | 输入 / 输出 |
|-------------|------|-------------|
| start-browser.bat / scripts/start_browser.py | BAT 定位解释器与配置；Python 标准库解析 TOML 并启动浏览器 | config/browser.toml / 浏览器进程或启动错误 |
| timer.py | 单任务生命周期、每轮完成后等待间隔 | 单配置路径 / 日志、退出状态 |
| executor.py | 一次执行 CLI、供 timer 调用的函数、模板选择、错误处理、统一落盘 | 配置与上下文 / 成功记录或分类错误 |
| template/*.py | 请求或页面采集 | 配置与上下文 / 可 JSON 序列化结果 |
| shared/config.py | UTF-8 TOML 读取、字段/路径/模板名称校验 | 配置文件 / 已校验配置 |
| shared/output.py | JSONL 追加、日志配置 | 任务名、时间和数据 / 文件 |
| shared/http.py | 最终请求构造、超时、HTTP 状态、JSON/文本解码 | 请求参数 / 响应数据 |
| shared/browser.py | CDP 连接、专属 Tab、文档初始化、人工登录和释放 | 浏览器配置 / 任务 Page |
| scripts/*.js | 文档环境初始化或网站专用请求 | 页面环境和请求参数 / 环境设置或响应 |

依赖方向：timer -> executor -> template -> shared。模板返回数据，由执行器统一保存历史。模板之间不互相导入；不引入插件发现框架。

## 启动与浏览器生命周期

计划 CLI（尚不可执行）：

```powershell
python timer.py config/tasks/example.toml
python executor.py config/tasks/example.toml
```

恰好一个位置参数；前者持续采集，后者执行一次。配置启动时读取。已确认任务校验与所需初始化完成后立即执行首轮，不先等待采集间隔；需要人工登录时，在用户按 Enter 后执行首轮。后续每轮结束后用单调时钟等待间隔，失败轮次亦适用。

用户要求将 BAT 启动参数移到配置文件。设计采用现有 config/browser.toml 统一保存启动设置，BAT 仅作为启动入口，不内嵌浏览器参数。BAT 本身无 TOML 解析器，因此调用 scripts/start_browser.py，使用标准库 tomllib 读取 UTF-8 文本并解析，使用 subprocess 的参数列表启动浏览器，不新增第三方依赖或通过 shell 拼接配置字符串。

BAT 使用自身所在目录定位 .venv/Scripts/python.exe、启动脚本与 config/browser.toml；解释器或配置缺失时明确报错。浏览器路径、端口、用户数据目录、初始页面和附加参数均在 browser.toml 修改。配置中的相对路径遵循已确认的项目根目录规则；带空格或中文的路径作为单个参数传递。

用户已确认以下启动默认配置；disable-gpu、no-sandbox 和后台节流参数默认不启用，可按需在 args 中开启：

```toml
executable = "C:/Program Files/Google/Chrome/Application/chrome.exe"
debug_port = 9222
user_data_dir = ".runtime/browser-profile"
start_url = "about:blank"

args = [
  "--no-first-run",
  "--no-default-browser-check",
  "--start-maximized",
  # "--disable-gpu",
  # "--no-sandbox",
  # "--disable-background-timer-throttling",
  # "--disable-renderer-backgrounding",
  # "--disable-backgrounding-occluded-windows",
]
```

启动脚本从 debug_port 和 user_data_dir 生成 remote-debugging-port 与 user-data-dir 参数，args 中不得重复覆盖这两个参数，避免设置冲突。采集端由同一 debug_port 生成 http://127.0.0.1:<port>，不再另存 cdp_url。配置修改后需关闭使用该用户目录的浏览器再重新启动；正在运行的任务不热加载。采集进程只连接，不自动启动浏览器。

每个任务在默认浏览器上下文创建空白 Tab，先注册初始化脚本，再导航到目标 URL。不同 Tab 可能共享 Cookie 等登录数据，但不共享页面操作、Page 对象或请求函数。不按 URL 接管其他任务 Tab。

初始化使用目标 Page.add_init_script，修改 Navigator.prototype.webdriver 的 getter；不向整个 context 注册，避免影响其他任务。初始化覆盖本任务后续导航、刷新和子 frame 文档。该设置不承诺规避其他自动化检测。

已确认 wait_for_login 默认 false，省略时不等待人工登录；需要人工登录确认的浏览器任务显式设为 true。true 时导航后等待终端 Enter，人工等待不受网络超时限制，Ctrl+C 可退出。运行中不自动检测或恢复登录。第一版不自动管理弹出窗口。

正常结束、异常清理或 Ctrl+C 仅关闭本任务 Tab，再断开客户端；不得关闭共享浏览器或默认 context。强制终止进程时不保证清理遗留 Tab。

## 配置与接口

四种任务的完整配置形状见 [配置样例](config-examples.md)。用户已确认该配置结构、固定输出目录与下述模板/JS 接口；示例为设计文档，具体业务文件尚未创建。

统一入口为 run(config, context) -> JSON 可序列化数据。context 持有任务生命周期内复用的 HTTP 会话或专属 Page，浏览器创建与人工登录不重复执行。

已确认路径规则：命令行配置路径相对终端当前目录解析，也支持绝对路径；配置内部的相对文件路径统一以项目根目录为基准，与配置文件所在层级和启动目录无关。例如 scripts/example_request.js 始终指向项目根目录下的该文件。

已确认任务名称约定：TOML 顶层 name 必须显式填写非空名称，仅使用英文字母、数字、下划线和连字符。不同任务使用不同名称，Windows 上不能仅靠大小写区分；数据和日志目录分别为 data/<name>/ 与 logs/<name>/。不同时重复启动同一任务，第一版不增加跨进程锁。名称校验也需拒绝 Windows 保留设备名等无法作为目录的名称；全局不重名由用户维护。

```toml
name = "example"
template = "api_request"

[timeouts]
http_seconds = 10
navigation_seconds = 10
operation_seconds = 10

[schedule]
interval_seconds = 60

[request]
method = "GET"
base_url = "https://example.com"
path = "/api/data"

[request.params]
limit = 10

[request.headers]
Accept = "application/json"
```

显式指定配置启动，因此不再需要 enabled。timer 要求正数 interval_seconds；executor 不要求 schedule。

已确认按 HTTP 请求、页面导航、页面操作分别设置超时，三类默认均为 10 秒，任务可分别覆盖；取消统一 timeout_seconds。配置采用 [timeouts] 下的 http_seconds、navigation_seconds、operation_seconds。

范围映射：HTTP 请求包含普通 API、OKX API 和 Tab 内 JS 请求；页面导航包含打开目标 URL、刷新及明确等待跳转完成；页面操作包含点击、双击、滚动、元素等待和字段读取。点击引发导航时，操作与后续导航等待分别应用对应设置。超时按单次请求或操作计，不是整轮采集总时限；页面自行加载的资源不逐个套用采集 HTTP 超时。人工登录等待不受这三类超时限制，固定 wait 动作按自身 seconds 执行。

请求字段包括 method、base_url、path、params、headers 和互斥的 json/body；body 为 UTF-8 文本。结果默认只保存完整响应体，响应头/状态用于判断；不输出认证头、密钥或完整配置。

OKX 在 [auth] 中使用 api_key_env、secret_key_env、passphrase_env 引用环境变量。先形成最终请求路径（含查询串）及请求体，再生成时间戳和 HMAC-SHA256/Base64 签名；签名与发送使用相同内容。签名请求的非预期重定向作为失败处理。实施时核对官方规则。

config/browser.toml 同时供启动脚本与采集进程读取，保存 executable、debug_port、user_data_dir、start_url 和 args；CDP 地址由 debug_port 派生，已确认默认端口 9222。任务 [browser] 包含 url、wait_for_login，browser_api 另含 script 文件路径。CDP 面向本机；用户目录和密钥不纳入版本管理。

请求脚本安装 window.__collectorRequest(request)，返回 Promise<{status, data}>；data 为 JSON 值或文本。每轮检查函数，不存在则读取 UTF-8 脚本并注入；请求必须具有可结束的超时，不能被悬挂的 Promise 无限阻塞。网站特定 token/请求逻辑由脚本处理，仍受跨域与 Cookie 策略限制。

页面 [[actions]] 顺序执行，支持 refresh、click、fill、select、wait、waitForSelector。click/fill/select/waitForSelector 使用 CSS selector（Playwright 语法）定位；fill 额外提供 value 文本，select 额外提供 value 选项值；wait 用 duration 毫秒；refresh 刷新当前页面，无参数。失败后不继续后续动作或提取。

> 2026-09-24 变更：T004 实施改用 Playwright CSS selector 体系（不再是 xpath/x-y/delta），动作集合改为 click、wait、fill、select、waitForSelector，并新增 refresh；详见 [D-005](decisions.md#d-005)。

页面 [[fields]] 包含 name、xpath、read、multiple、type；read 为 text、html 或 attribute:<attribute名称>（如 attribute:href）；type 为 string、number 或 boolean，用于结果值转换。单值取首个匹配，多值返回所有匹配。

已确认的字段规则：单值无匹配时本轮失败；多值无匹配时正常保存空数组 []；元素缺少指定属性时本轮失败；元素文本或已存在的属性值为空字符串时正常保存 ""。动态内容通过前置 wait_for 动作等待；任一字段失败均不保存本轮部分结果，记录日志后在下一周期采集。

## 输出与错误

记录格式：{"task":"任务名","collected_at":"含时区的 ISO 8601 时间","data":结果}，UTF-8 每行追加一条。已确认 collected_at 为本轮成功采集完成时间，使用本机时区并包含偏移；文件名取该时间对应日期。采集跨过午夜时写入完成日期的文件，记录时间与文件日期使用同一次取时。保留重复数据，不清理历史；不同任务名隔离各进程输出和日志。

已确认 API 成功规则：普通 API 和浏览器内 API 以最终 HTTP 状态为准，仅 2xx 成功，其余状态失败；不额外解释 success/code 等业务字段，2xx 响应中的业务错误内容也原样保存。OKX 额外要求响应为 JSON 对象且 code 为字符串 "0"；code 缺失、非 "0" 或无法读取时均失败。请求异常、超时及页面动作/提取失败视为本轮失败，记录日志且不写成功结果。普通 API 和浏览器内 API 的响应不能解析为 JSON 时保存文本，OKX 须先通过上述业务成功检查。

持续模式可恢复错误记日志后等待下一轮；单次模式失败返回非零状态。配置无效、密钥缺失、模板不存在、CDP 不可连接/断开、Tab 关闭作为终止错误。失败不写成功 JSONL；日志屏蔽认证信息，不默认输出完整响应。

已确认结果写入失败处理：磁盘已满、无写入权限、文件占用等导致保存失败时，立即停止任务并在终端报错，不继续后续采集周期。浏览器任务仍清理自身 Tab，保留浏览器和其他 Tab；日志文件也无法写入时，错误至少输出到终端。文件系统写入失败可能留下未完整写入的行，不将其视为成功记录。

## 验证与风险

本地 HTTP 服务/页面验证响应、签名输入一致性、动作顺序、JS 重新注入、超时、历史追加和退出清理。真实 OKX 只读接口和登录站点验证需要用户提供配置、凭据及人工登录；未实测不能标记相关验收完成。

坐标受窗口布局影响；共享浏览器登录数据不等于账号隔离；任意 Tab 不一定有权跨域请求目标 API。后台 Tab 行为以实际验证为准，启动参数保持少量。

## 确认清单

- [x] 主要需求已逐项确认，ENV.md 已记录环境。
- [x] 依赖选型已确认：requests、Playwright 同步 API，其余所列能力使用标准库。
- [x] 配置结构、模板/JS 接口、固定输出目录和默认行为已确认。
- [x] 用户已确认任务拆分与验收方法。
- [x] 已记录日期与确认来源，冻结架构和任务计划并初始化 T001-T006 为 todo。
- [x] 2026-09-24：T004 页面动作/字段接口变更（selector 体系、新增 refresh）已记录为新基线，见 [D-005](decisions.md#d-005)。
