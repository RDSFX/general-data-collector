# 执行过程

## 实施步骤

### 1. 创建 scripts/request.js
- ✅ 封装 fetch API
- ✅ 接受参数：url、method、headers、body
- ✅ 返回格式：{status, data}
- ✅ 自动 JSON 序列化请求体
- ✅ 自动 JSON/文本解析响应
- ✅ 超时控制（AbortController）
- ✅ 异常处理（连接错误、超时）
- ✅ 挂载到 window.request

### 2. 实现 template/browser_api.py
- ✅ 读取用户提供的 JS 脚本文件（支持相对路径）
- ✅ 检测脚本是否使用 request() 函数
- ✅ 按需注入 request.js
- ✅ 使用 page.evaluate() 执行脚本
- ✅ 应用 operation_seconds 超时配置（秒转毫秒）
- ✅ 验证返回值为 JSON 对象（dict）
- ✅ 脚本不存在、执行失败、超时、非 JSON 返回明确报错

### 3. 实现 template/browser_page.py

**动作执行**：
- ✅ 顺序执行 actions 数组
- ✅ 支持动作类型：
  - click：点击元素（CSS 选择器）
  - wait：等待固定时间（毫秒）
  - fill：填写表单字段
  - select：选择下拉选项
  - waitForSelector：等待元素出现
- ✅ 每个动作应用 operation_seconds 超时
- ✅ 动作缺少必填字段时报错
- ✅ 不支持的动作类型报错
- ✅ 动作执行失败或超时明确报错

**字段提取**：
- ✅ 读取 fields 数组
- ✅ XPath 定位元素（page.locator(f"xpath={xpath}")）
- ✅ 支持提取类型：
  - text：inner_text()
  - html：inner_html()
  - attribute:<name>：get_attribute()
- ✅ 支持单值模式（取第一个元素）
- ✅ 支持多值模式（multiple=true，返回数组）
- ✅ 值类型转换：
  - string：原样返回
  - number：int 或 float
  - boolean：true/false/1/0/yes/no/空字符串
- ✅ XPath 无匹配元素时报错
- ✅ 属性不存在时报错
- ✅ 类型转换失败时报错

### 4. 逻辑验证

**request.js 验证**：
- ✅ 脚本文件存在
- ✅ 包含 async function request 和 fetch 调用
- ✅ 挂载到 window.request

**browser_api 模板验证**：
- ✅ 模块导入成功
- ✅ run 函数存在
- ✅ _inject_request_helper 函数存在

**browser_page 模板验证**：
- ✅ 模块导入成功
- ✅ run 函数存在
- ✅ execute_actions 函数存在
- ✅ extract_fields 函数存在
- ✅ _extract_element_value 函数存在
- ✅ _convert_type 函数存在

**类型转换验证**：
- ✅ 字符串转换："hello" → "hello"
- ✅ 整数转换："123" → 123
- ✅ 浮点数转换："123.45" → 123.45
- ✅ 布尔值转换：
  - "true"/"1"/"yes" → True
  - "false"/"0"/"no"/"" → False

## 验收达成情况

### browser_api 模板

| 验收项 | 状态 | 证据 |
|--------|------|------|
| 读取并执行用户 JS | ✅ | 代码实现，读取文件并 page.evaluate() |
| 返回 JSON 对象 | ✅ | isinstance(result, dict) 验证 |
| 脚本执行失败报错 | ✅ | except Exception: raise Exception() |
| 非 JSON 响应报错 | ✅ | 类型检查并抛出异常 |
| 超时控制 | ✅ | page.evaluate(timeout=timeout_ms) |
| 真实验证 | ⚠️ | 需用户提供实际 URL 和请求脚本 |

### browser_page 模板

| 验收项 | 状态 | 证据 |
|--------|------|------|
| 顺序执行 actions | ✅ | for 循环顺序执行，带序号错误提示 |
| 支持 5 种动作类型 | ✅ | click/wait/fill/select/waitForSelector |
| XPath 单值提取 | ✅ | elements[0]，返回转换后的值 |
| XPath 多值提取 | ✅ | multiple=true，返回数组 |
| 文本/属性/HTML 提取 | ✅ | text/attribute:<name>/html |
| 类型转换 | ✅ | string/number/boolean，测试通过 |
| 空值报错 | ✅ | XPath 无匹配元素时抛出异常 |
| XPath 错误报错 | ✅ | Playwright 异常捕获并重新抛出 |
| 真实验证 | ⚠️ | 需用户提供实际 URL、XPath、动作 |

## 未验证项

**真实浏览器环境验证**：需要 Windows + Chrome + CDP + 真实网页

### browser_api 真实验证

**所需准备**：
1. 启动浏览器：`.\start-browser.bat`
2. 准备测试脚本（例如 scripts/test_api.js）：
   ```javascript
   // 使用 window.request 发送请求
   (async () => {
     const result = await window.request('https://httpbin.org/json');
     return result;
   })();
   ```
3. 创建配置文件：
   ```toml
   name = "test_browser_api"
   template = "browser_api"
   
   [timeouts]
   navigation_seconds = 10
   operation_seconds = 10
   
   [browser]
   url = "about:blank"
   script = "scripts/test_api.js"
   ```
4. 运行：`python executor.py config/tasks/test_browser_api.toml`

**预期结果**：
- 注入 request.js
- 执行用户脚本
- 返回 httpbin.org 的 JSON 响应
- 数据保存到 data/test_browser_api/

### browser_page 真实验证

**所需准备**：
1. 启动浏览器：`.\start-browser.bat`
2. 创建测试 HTML 文件或使用真实网页
3. 创建配置文件，包含：
   - actions：点击、填写、等待等操作
   - fields：XPath 提取字段
4. 运行：`python executor.py config/tasks/test_browser_page.toml`

**测试场景**：
- 单值文本提取
- 多值提取（列表）
- 属性提取（href、src 等）
- 类型转换（数值、布尔）
- 动作序列执行
- 元素不存在错误处理

**当前状态**：代码实现完整，逻辑验证通过，等待真实环境测试。

## 配置示例

### browser_api 配置示例

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

### browser_page 配置示例

```toml
name = "example_browser_page"
template = "browser_page"

[timeouts]
navigation_seconds = 10
operation_seconds = 10

[browser]
url = "https://example.com"
wait_for_login = false

[[actions]]
type = "waitForSelector"
selector = "#content"

[[actions]]
type = "click"
selector = "button.load-more"

[[actions]]
type = "wait"
duration = 1000

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

## 共享文件修改

按 T001 -> T002 -> T003 -> T004 顺序：
- 无需修改共享文件
- 新增 template/browser_api.py（替换桩）
- 新增 template/browser_page.py（替换桩）
- 新增 scripts/request.js

T005 将实现 timer.py 调度器，集成所有模板。

## T004 状态

核心功能完成，代码实现完整且通过逻辑验证。真实浏览器环境验证需 Windows + Chrome + 真实网页。
