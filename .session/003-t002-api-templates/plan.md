# 实施计划

## 步骤

### 1. 实现 shared/http.py
- HTTP 请求封装：method、URL、params、headers、json/body
- 超时控制：使用 config.timeouts.http_seconds
- 响应处理：状态码、JSON/文本解码
- 异常处理：连接错误、超时、解码失败

### 2. 实现 template/api_request.py
- 构造请求参数（base_url + path + params）
- 调用 shared/http.py 发送请求
- 2xx 响应成功（包括业务错误内容）
- 非 2xx 响应失败

### 3. 实现 template/okx_api.py
- 从环境变量读取认证信息
- 生成时间戳（ISO 8601 UTC）
- 构造签名内容：timestamp + method + path + body
- HMAC-SHA256 签名 + Base64 编码
- 添加 OKX 专用 headers
- 响应必须同时满足：HTTP 2xx + JSON 对象 + code="0"

### 4. 扩展 executor.py
- 为 api_request 和 okx_api 创建 requests.Session
- 生命周期：任务开始时创建，结束时关闭
- 传递给模板的 context

### 5. 本地验证
- 启动本地 HTTP 服务器模拟 API
- 测试 JSON/文本响应
- 测试 2xx/非 2xx 状态
- 测试超时
- 测试 OKX 签名计算（固定时间戳验证向量）

### 6. 真实验证（条件许可时）
- 使用用户提供的 OKX 只读 API
- 验证签名和实际请求
- 不执行交易操作

## 关键接口

HTTP 请求接口：
```python
def send_request(
    method: str,
    url: str,
    params: dict = None,
    headers: dict = None,
    json_data: dict = None,
    body: str = None,
    timeout: float = 10
) -> dict:
    """返回 {"status": int, "data": dict|str}"""
    pass
```

OKX 签名函数：
```python
def create_signature(
    timestamp: str,
    method: str,
    path: str,
    body: str,
    secret_key: str
) -> str:
    """返回 Base64 签名"""
    pass
```
