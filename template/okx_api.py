"""OKX API 签名请求模板

支持：
- HMAC-SHA256 签名认证
- 从环境变量读取密钥
- OKX 专用请求头
- 成功规则：HTTP 2xx + JSON 对象 + code="0"
"""

from typing import Any
import os
import hmac
import hashlib
import base64
from datetime import datetime, timezone
import requests

from shared.http import send_request, HttpError


def run(config: dict[str, Any], context: requests.Session) -> Any:
    """执行 OKX 签名 API 请求

    Args:
        config: 任务配置，包含 auth 和 request 节
        context: HTTP Session 对象

    Returns:
        API 响应数据（仅在成功时）

    Raises:
        Exception: 认证失败、请求失败或业务错误
    """
    # 读取认证信息
    auth_config = config["auth"]
    api_key = _get_env_var(auth_config["api_key_env"])
    secret_key = _get_env_var(auth_config["secret_key_env"])
    passphrase = _get_env_var(auth_config["passphrase_env"])

    # 构造请求
    request_config = config["request"]
    method = request_config["method"].upper()
    base_url = request_config["base_url"].rstrip("/")
    path = request_config["path"]
    if not path.startswith("/"):
        path = "/" + path

    # 构造完整请求路径（含查询串）
    params = request_config.get("params")
    if params:
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        request_path = f"{path}?{query_string}"
    else:
        request_path = path

    # 准备请求体
    json_data = request_config.get("json")
    body_str = request_config.get("body", "")

    if json_data is not None:
        import json
        body_str = json.dumps(json_data, separators=(',', ':'))

    # 生成时间戳（ISO 8601 UTC）
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    # 生成签名
    signature = _create_signature(timestamp, method, request_path, body_str, secret_key)

    # 构造 OKX 专用 headers
    headers = request_config.get("headers", {}).copy()
    headers.update({
        "OK-ACCESS-KEY": api_key,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": passphrase,
    })

    # 获取超时配置
    timeout = config.get("timeouts", {}).get("http_seconds", 10)

    # 发送请求
    url = base_url + path
    try:
        result = send_request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            json_data=json_data,
            body=body_str if not json_data else None,
            timeout=timeout,
            session=context
        )
    except HttpError as e:
        raise Exception(f"HTTP 请求失败: {e}")

    # 检查 HTTP 状态码
    status = result["status"]
    if not (200 <= status < 300):
        raise Exception(f"HTTP 状态非 2xx: {status}")

    # 检查响应格式（必须是 JSON 对象）
    data = result["data"]
    if not isinstance(data, dict):
        raise Exception(f"OKX 响应不是 JSON 对象")

    # 检查业务状态码
    code = data.get("code")
    if code != "0":
        raise Exception(f"OKX 业务错误，code: {code}")

    # 返回响应数据
    return data


def _get_env_var(var_name: str) -> str:
    """从环境变量读取值

    Args:
        var_name: 环境变量名

    Returns:
        环境变量值

    Raises:
        Exception: 环境变量不存在或为空
    """
    value = os.environ.get(var_name)
    if not value:
        raise Exception(f"环境变量 {var_name} 未设置或为空")
    return value


def _create_signature(
    timestamp: str,
    method: str,
    request_path: str,
    body: str,
    secret_key: str
) -> str:
    """生成 OKX API 签名

    签名内容：timestamp + method + request_path + body
    算法：HMAC-SHA256 + Base64

    Args:
        timestamp: ISO 8601 UTC 时间戳
        method: HTTP 方法（大写）
        request_path: 请求路径（含查询串）
        body: 请求体（空字符串如果无请求体）
        secret_key: 密钥

    Returns:
        Base64 编码的签名
    """
    # 构造签名内容
    message = timestamp + method + request_path + body

    # HMAC-SHA256
    signature_bytes = hmac.new(
        secret_key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).digest()

    # Base64 编码
    signature = base64.b64encode(signature_bytes).decode("utf-8")

    return signature
