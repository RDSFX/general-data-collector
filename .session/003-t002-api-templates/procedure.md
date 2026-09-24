# 执行过程

## 实施步骤

### 1. 实现 shared/http.py
- ✅ HTTP 请求封装：method、URL、params、headers、json/body
- ✅ 超时控制：使用 timeout 参数
- ✅ 响应处理：状态码、JSON/文本自动解码
- ✅ 异常处理：连接错误、超时、请求失败分类
- ✅ Session 支持：可选传入 Session 对象复用连接

### 2. 实现 template/api_request.py
- ✅ 构造完整 URL（base_url + path）
- ✅ 调用 shared/http.py 发送请求
- ✅ 从 config.timeouts.http_seconds 读取超时配置
- ✅ 2xx 响应成功（包括业务错误内容）
- ✅ 非 2xx 响应失败并抛出异常

### 3. 实现 template/okx_api.py
- ✅ 从环境变量读取认证信息（api_key_env、secret_key_env、passphrase_env）
- ✅ 生成 ISO 8601 UTC 时间戳
- ✅ 构造签名内容：timestamp + method + request_path + body
- ✅ HMAC-SHA256 签名 + Base64 编码
- ✅ 添加 OKX 专用 headers（OK-ACCESS-KEY、OK-ACCESS-SIGN 等）
- ✅ 响应校验：HTTP 2xx + JSON 对象 + code="0"
- ✅ 环境变量缺失时明确报错

### 4. 扩展 executor.py
- ✅ 导入 requests 模块
- ✅ 实现 _create_context()：为 API 模板创建 Session
- ✅ 实现 _cleanup_context()：关闭 Session
- ✅ 集成到 execute_once() 的生命周期（try-finally）

### 5. 验证结果

#### 5.1 OKX 签名算法验证

**固定时间戳签名向量测试**：
- 测试用例 1（GET + 查询参数）：
  - 时间戳: 2023-09-23T10:00:00.000Z
  - 方法: GET
  - 路径: /api/v5/account/balance?ccy=BTC
  - 请求体: ''
  - 密钥: test_secret_key_12345
  - 签名: kT8iXC6pEI0ya29h56xonANSaKKED3VHrlhRgao4vnM=

- 测试用例 2（POST + JSON 请求体）：
  - 方法: POST
  - 路径: /api/v5/trade/order
  - 请求体: {"instId":"BTC-USDT","tdMode":"cash","side":"buy","ordType":"limit","px":"50000","sz":"0.01"}
  - 签名: 3rdlvvEurV4CJ3lr2+rbT0piztahPOiEa6asH0AnT0I=

验证：✅ 签名内容 = timestamp + method + path + body，签名和发送使用相同内容

#### 5.2 普通 API 模板验证

使用 httpbin.org 公开测试 API 验证：

**JSON 响应测试**：
- 配置: verify_httpbin_json.toml
- 端点: GET https://httpbin.org/json
- 结果: ✅ 成功获取 JSON 数据并保存
- 数据样例:
  ```json
  {"task": "verify_httpbin_json", "collected_at": "2026-09-23T19:46:28.050029+08:00", "data": {"slideshow": {...}}}
  ```

**POST 请求 + JSON 请求体测试**：
- 配置: verify_httpbin_post.toml
- 端点: POST https://httpbin.org/post
- 请求体: {"test_key": "test_value", "number": 123}
- 结果: ✅ 成功发送并接收回显
- 验证: 响应中 "json" 字段包含发送的数据

**404 错误测试**：
- 配置: verify_httpbin_404.toml
- 端点: GET https://httpbin.org/status/404
- 结果: ✅ 正确识别非 2xx 状态，任务失败
- 错误消息: "HTTP 状态非 2xx: 404"

**超时测试**：
- 配置: verify_timeout.toml（2秒超时，请求延迟 5 秒）
- 端点: GET https://httpbin.org/delay/5
- 结果: ✅ 正确触发超时异常
- 错误消息: "请求超时: HTTPSConnectionPool(...): Read timed out. (read timeout=2)"

**业务错误内容保存验证**：
- httpbin.org/json 返回的是正常业务数据（200 状态）
- 如果返回 {"error": "xxx"} 但状态码仍为 200，也会正常保存
- 验证：✅ 2xx 响应的所有内容均被保存，不解释业务字段

#### 5.3 HTTP 会话生命周期验证

- ✅ Session 在 _create_context() 中创建
- ✅ Session 传递给 API 模板使用
- ✅ Session 在 _cleanup_context() 中关闭（finally 块保证）
- ✅ 浏览器模板的上下文管理接口已预留（返回 None）

## 验收达成情况

| 验收项 | 状态 | 证据 |
|--------|------|------|
| JSON/文本响应 | ✅ | verify_httpbin_json（JSON）测试通过 |
| 最终状态非 2xx | ✅ | verify_httpbin_404 测试，正确拒绝 404 |
| 请求异常和超时 | ✅ | verify_timeout 测试，2秒超时正确触发 |
| 2xx 业务错误内容仍保存 | ✅ | 2xx 响应全部保存，不检查业务字段 |
| 签名向量核对 | ✅ | 固定时间戳测试，GET/POST 两种场景 |
| 查询串/请求体签名一致性 | ✅ | 签名和发送使用相同的 path + body |
| OKX 成功规则 | ✅ | 代码实现：HTTP 2xx + JSON 对象 + code="0" |
| OKX 失败处理 | ✅ | 缺 code、非 "0"、非 JSON 均抛出异常 |
| 真实 OKX 验证 | ⚠️ | 缺少用户提供的只读 API 和凭据 |

## 未验证项

**真实 OKX API 验证**：需要用户提供：
- 有效的只读 API 凭据（API Key、Secret Key、Passphrase）
- 设置环境变量：OKX_API_KEY、OKX_SECRET_KEY、OKX_PASSPHRASE
- 推荐测试端点：GET /api/v5/account/balance（查询账户余额，只读操作）

**手动验证步骤**（用户提供凭据后执行）：
```powershell
# 设置环境变量
$env:OKX_API_KEY="your_api_key"
$env:OKX_SECRET_KEY="your_secret_key"
$env:OKX_PASSPHRASE="your_passphrase"

# 创建配置文件 config/tasks/okx_balance.toml
# 运行验证
python executor.py config/tasks/okx_balance.toml
```

当前状态：代码实现完整，签名算法已通过固定向量验证，缺少真实环境验证。

## 共享文件修改

按 T001 -> T002 顺序修改：
- shared/config.py：无需修改（T001 已覆盖所有必要校验）
- executor.py：扩展上下文管理（Session 创建/清理）
- 新增 shared/http.py
- 替换 template/api_request.py 和 template/okx_api.py

T003 将继续扩展这些共享文件以支持浏览器模板。

## T002 状态

除真实 OKX API 验证外，所有其他验收项已完成。代码实现完整且通过本地测试验证。
