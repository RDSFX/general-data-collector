"""配置读取与校验模块

负责：
- UTF-8 TOML 文件读取
- 必填字段校验
- 任务名称格式校验（拒绝 Windows 保留名）
- 模板名称合法性校验
- 文件路径存在性校验
- 相对路径以项目根目录为基准解析
"""

import sys
from pathlib import Path
from typing import Any

# Python 3.11+ 内置 tomllib，3.10 及以下使用 tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

# 项目根目录：本文件在 shared/，根目录在上一级
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 合法的模板名称
VALID_TEMPLATES = {"api_request", "okx_api", "browser_api", "browser_page"}

# Windows 保留设备名（不区分大小写）
WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}


class ConfigError(Exception):
    """配置错误，应立即退出任务"""
    pass


def load_config(config_path: str | Path) -> dict[str, Any]:
    """加载并校验任务配置

    Args:
        config_path: 配置文件路径（相对当前目录或绝对路径）

    Returns:
        已校验的配置字典

    Raises:
        ConfigError: 配置文件不存在、格式错误或校验失败
    """
    config_file = Path(config_path)

    # 检查文件存在
    if not config_file.exists():
        raise ConfigError(f"配置文件不存在: {config_file}")

    # 读取并解析 TOML（UTF-8）
    try:
        with open(config_file, "rb") as f:
            config = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"配置文件 TOML 格式错误: {e}")
    except Exception as e:
        raise ConfigError(f"读取配置文件失败: {e}")

    # 校验配置
    _validate_config(config)

    return config


def _validate_config(config: dict[str, Any]) -> None:
    """校验配置字段

    Raises:
        ConfigError: 配置不符合要求
    """
    # 校验必填顶层字段
    if "name" not in config:
        raise ConfigError("缺少必填字段: name")
    if "template" not in config:
        raise ConfigError("缺少必填字段: template")

    # 校验任务名称
    task_name = config["name"]
    if not task_name or not isinstance(task_name, str):
        raise ConfigError("任务名称 name 必须为非空字符串")

    # 检查名称格式：仅允许字母、数字、下划线、连字符
    if not all(c.isalnum() or c in "_-" for c in task_name):
        raise ConfigError(f"任务名称 '{task_name}' 只能包含字母、数字、下划线和连字符")

    # 检查 Windows 保留设备名
    if task_name.upper() in WINDOWS_RESERVED_NAMES:
        raise ConfigError(f"任务名称 '{task_name}' 是 Windows 保留设备名，不能使用")

    # 校验模板名称
    template_name = config["template"]
    if template_name not in VALID_TEMPLATES:
        raise ConfigError(
            f"不支持的模板: {template_name}，有效值: {', '.join(sorted(VALID_TEMPLATES))}"
        )

    # 校验 timeouts（可选，但如果存在需要检查格式）
    if "timeouts" in config:
        timeouts = config["timeouts"]
        if not isinstance(timeouts, dict):
            raise ConfigError("timeouts 必须是字典")
        # 检查超时值为正数
        for key in ["http_seconds", "navigation_seconds", "operation_seconds"]:
            if key in timeouts:
                value = timeouts[key]
                if not isinstance(value, (int, float)) or value <= 0:
                    raise ConfigError(f"timeouts.{key} 必须为正数")

    # 校验 schedule（executor.py 不强制要求，timer.py 要求）
    if "schedule" in config:
        schedule = config["schedule"]
        if not isinstance(schedule, dict):
            raise ConfigError("schedule 必须是字典")
        if "interval_seconds" in schedule:
            interval = schedule["interval_seconds"]
            if not isinstance(interval, (int, float)) or interval <= 0:
                raise ConfigError("schedule.interval_seconds 必须为正数")

    # 校验浏览器模板的必填字段
    if template_name in {"browser_api", "browser_page"}:
        if "browser" not in config:
            raise ConfigError(f"模板 {template_name} 需要 [browser] 配置节")
        browser = config["browser"]
        if "url" not in browser:
            raise ConfigError(f"模板 {template_name} 需要 browser.url")

        # browser_api 需要 script 路径
        if template_name == "browser_api":
            if "script" not in browser:
                raise ConfigError("browser_api 模板需要 browser.script")
            _validate_file_path(browser["script"], "browser.script")

    # 校验 API 模板的必填字段
    if template_name in {"api_request", "okx_api"}:
        if "request" not in config:
            raise ConfigError(f"模板 {template_name} 需要 [request] 配置节")
        request = config["request"]
        if "method" not in request:
            raise ConfigError(f"模板 {template_name} 需要 request.method")
        if "base_url" not in request:
            raise ConfigError(f"模板 {template_name} 需要 request.base_url")
        if "path" not in request:
            raise ConfigError(f"模板 {template_name} 需要 request.path")

    # okx_api 需要认证配置
    if template_name == "okx_api":
        if "auth" not in config:
            raise ConfigError("okx_api 模板需要 [auth] 配置节")
        auth = config["auth"]
        for key in ["api_key_env", "secret_key_env", "passphrase_env"]:
            if key not in auth:
                raise ConfigError(f"okx_api 模板需要 auth.{key}")

    # browser_page 需要 fields，actions 可选（允许为空数组）
    if template_name == "browser_page":
        if "fields" not in config:
            raise ConfigError("browser_page 模板需要 [[fields]] 数组")
        # actions 可选，不强制要求


def _validate_file_path(path: str, field_name: str) -> None:
    """校验文件路径存在性

    相对路径以项目根目录为基准

    Args:
        path: 文件路径
        field_name: 配置字段名（用于错误消息）

    Raises:
        ConfigError: 文件不存在
    """
    file_path = resolve_project_path(path)
    if not file_path.exists():
        raise ConfigError(f"{field_name} 指向的文件不存在: {path}")
    if not file_path.is_file():
        raise ConfigError(f"{field_name} 必须指向文件而非目录: {path}")


def resolve_project_path(path: str | Path) -> Path:
    """将相对路径解析为项目根目录下的绝对路径

    绝对路径保持不变

    Args:
        path: 文件路径

    Returns:
        绝对路径
    """
    p = Path(path)
    if p.is_absolute():
        return p
    return (PROJECT_ROOT / p).resolve()
