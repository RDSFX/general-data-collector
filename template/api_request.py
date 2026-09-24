"""普通 API 请求模板

支持：
- 常规 HTTP 请求（GET、POST 等）
- 查询参数、请求头
- JSON 或文本请求体
- 2xx 状态视为成功，包括业务错误内容
"""

from typing import Any
import requests

from shared.http import send_request, HttpError


def run(config: dict[str, Any], context: requests.Session) -> Any:
    """执行普通 API 请求

    Args:
        config: 任务配置，包含 request 节
        context: HTTP Session 对象

    Returns:
        API 响应数据（JSON 对象或文本）

    Raises:
        Exception: 请求失败或非 2xx 状态
    """
    request_config = config["request"]

    # 构造完整 URL
    base_url = request_config["base_url"].rstrip("/")
    path = request_config["path"]
    if not path.startswith("/"):
        path = "/" + path
    url = base_url + path

    # 获取超时配置
    timeout = config.get("timeouts", {}).get("http_seconds", 10)

    # 准备请求参数
    method = request_config["method"]
    params = request_config.get("params")
    headers = request_config.get("headers")
    json_data = request_config.get("json")
    body = request_config.get("body")

    # 发送请求
    try:
        result = send_request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            json_data=json_data,
            body=body,
            timeout=timeout,
            session=context
        )
    except HttpError as e:
        raise Exception(f"HTTP 请求失败: {e}")

    # 检查状态码
    status = result["status"]
    if not (200 <= status < 300):
        raise Exception(f"HTTP 状态非 2xx: {status}")

    # 返回响应数据（2xx 响应全部返回，包括业务错误）
    return result["data"]
