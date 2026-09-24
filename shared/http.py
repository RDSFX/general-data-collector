"""HTTP 请求模块

负责：
- 构造和发送 HTTP 请求
- 超时控制
- 响应状态码处理
- JSON/文本解码
- 异常处理
"""

import requests
from typing import Any, Optional


class HttpError(Exception):
    """HTTP 请求错误"""
    pass


def send_request(
    method: str,
    url: str,
    params: Optional[dict[str, Any]] = None,
    headers: Optional[dict[str, str]] = None,
    json_data: Optional[dict[str, Any]] = None,
    body: Optional[str] = None,
    timeout: float = 10.0,
    session: Optional[requests.Session] = None
) -> dict[str, Any]:
    """发送 HTTP 请求

    Args:
        method: HTTP 方法（GET、POST 等）
        url: 完整 URL
        params: 查询参数
        headers: 请求头
        json_data: JSON 请求体（与 body 互斥）
        body: 文本请求体（与 json_data 互斥，UTF-8）
        timeout: 超时秒数
        session: requests.Session 对象（可选，用于复用连接）

    Returns:
        {"status": HTTP状态码, "data": JSON对象或文本}

    Raises:
        HttpError: 请求失败（连接错误、超时等）
    """
    if json_data is not None and body is not None:
        raise HttpError("json_data 和 body 不能同时提供")

    # 使用 session 或创建临时请求
    requester = session if session else requests

    try:
        # 准备请求参数
        request_kwargs = {
            "method": method.upper(),
            "url": url,
            "params": params,
            "headers": headers,
            "timeout": timeout,
        }

        # 设置请求体
        if json_data is not None:
            request_kwargs["json"] = json_data
        elif body is not None:
            request_kwargs["data"] = body.encode("utf-8")
            # 如果没有设置 Content-Type，添加默认值
            if headers is None or "Content-Type" not in headers:
                if request_kwargs.get("headers") is None:
                    request_kwargs["headers"] = {}
                request_kwargs["headers"]["Content-Type"] = "text/plain; charset=utf-8"

        # 发送请求
        response = requester.request(**request_kwargs)

        # 获取状态码
        status_code = response.status_code

        # 尝试解析响应体
        data = _parse_response(response)

        return {
            "status": status_code,
            "data": data,
        }

    except requests.exceptions.Timeout as e:
        raise HttpError(f"请求超时: {e}")
    except requests.exceptions.ConnectionError as e:
        raise HttpError(f"连接错误: {e}")
    except requests.exceptions.RequestException as e:
        raise HttpError(f"请求失败: {e}")


def _parse_response(response: requests.Response) -> Any:
    """解析响应体

    优先尝试 JSON，失败则返回文本

    Args:
        response: requests.Response 对象

    Returns:
        JSON 对象或文本字符串
    """
    # 尝试 JSON 解析
    try:
        return response.json()
    except (ValueError, requests.exceptions.JSONDecodeError):
        # 不是 JSON，返回文本
        return response.text
