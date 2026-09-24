"""浏览器内 API 请求模板

支持：
- 执行用户提供的 JavaScript 脚本
- 注入 request.js 辅助函数
- 超时控制
- 返回 JSON 对象作为采集结果
"""

from typing import Any
from pathlib import Path
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# request.js 辅助脚本路径
REQUEST_SCRIPT = PROJECT_ROOT / "scripts" / "request.js"


def run(config: dict[str, Any], context: Page) -> Any:
    """执行浏览器内 API 请求

    Args:
        config: 任务配置，包含 browser.script 路径
        context: Page 对象

    Returns:
        JavaScript 返回的 JSON 对象

    Raises:
        Exception: 脚本执行失败或返回非 JSON
    """
    page: Page = context
    browser_config = config["browser"]

    # 读取用户脚本路径
    script_path_str = browser_config["script"]
    script_path = Path(script_path_str)

    # 相对路径基于项目根目录解析
    if not script_path.is_absolute():
        script_path = PROJECT_ROOT / script_path

    # 检查脚本文件存在
    if not script_path.exists():
        raise Exception(f"JavaScript 脚本不存在: {script_path}")

    # 读取用户脚本
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            user_script = f.read()
    except Exception as e:
        raise Exception(f"读取脚本失败: {e}")

    # 注入 request.js（如果用户脚本需要）
    if "request(" in user_script or "window.request" in user_script:
        _inject_request_helper(page)

    # 获取超时配置（毫秒）
    timeout_seconds = config.get("timeouts", {}).get("operation_seconds", 10)
    timeout_ms = timeout_seconds * 1000

    # 设置 Page 级别超时
    page.set_default_timeout(timeout_ms)

    # 执行用户脚本
    try:
        result = page.evaluate(user_script)
    except PlaywrightTimeout:
        raise Exception(f"脚本执行超时（{timeout_seconds}秒）")
    except Exception as e:
        raise Exception(f"脚本执行失败: {e}")

    # 验证返回值为 JSON 对象
    if not isinstance(result, dict):
        raise Exception(f"脚本必须返回 JSON 对象，实际返回类型: {type(result).__name__}")

    return result


def _inject_request_helper(page: Page) -> None:
    """注入 request.js 辅助脚本

    Args:
        page: Page 对象

    Raises:
        Exception: 脚本不存在或注入失败
    """
    if not REQUEST_SCRIPT.exists():
        raise Exception(f"request.js 脚本不存在: {REQUEST_SCRIPT}")

    try:
        with open(REQUEST_SCRIPT, "r", encoding="utf-8") as f:
            request_script = f.read()
        page.evaluate(request_script)
    except Exception as e:
        raise Exception(f"注入 request.js 失败: {e}")
