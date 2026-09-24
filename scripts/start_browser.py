"""浏览器启动脚本

负责：
- 读取 config/browser.toml
- 验证配置和可执行文件
- 构造启动命令
- 启动浏览器进程
"""

import sys
from pathlib import Path
import subprocess

# Python 3.11+ 内置 tomllib，3.10 及以下使用 tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


# 项目根目录（本脚本在 scripts/）
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 浏览器配置文件路径
BROWSER_CONFIG = PROJECT_ROOT / "config" / "browser.toml"


class BrowserStartError(Exception):
    """浏览器启动错误"""
    pass


def main():
    """主入口"""
    try:
        # 加载配置
        config = load_browser_config()

        # 验证配置
        validate_config(config)

        # 构造启动命令
        command = build_command(config)

        # 启动浏览器
        print(f"启动浏览器: {config['executable']}")
        print(f"调试端口: {config['debug_port']}")
        print(f"用户目录: {config['user_data_dir']}")

        subprocess.Popen(command)
        print("浏览器已启动")

    except BrowserStartError as e:
        print(f"[错误] {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[错误] 未预期异常: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    return 0


def load_browser_config() -> dict:
    """加载浏览器配置

    Returns:
        配置字典

    Raises:
        BrowserStartError: 配置文件不存在或格式错误
    """
    if not BROWSER_CONFIG.exists():
        raise BrowserStartError(f"配置文件不存在: {BROWSER_CONFIG}")

    try:
        with open(BROWSER_CONFIG, "rb") as f:
            config = tomllib.load(f)
    except Exception as e:
        raise BrowserStartError(f"读取配置文件失败: {e}")

    return config


def validate_config(config: dict) -> None:
    """验证配置

    Args:
        config: 配置字典

    Raises:
        BrowserStartError: 配置不合法
    """
    # 检查必填字段
    required = ["executable", "debug_port", "user_data_dir", "start_url"]
    for field in required:
        if field not in config:
            raise BrowserStartError(f"缺少必填字段: {field}")

    # 验证可执行文件存在
    executable = Path(config["executable"])
    if not executable.exists():
        raise BrowserStartError(f"浏览器可执行文件不存在: {executable}")

    # 验证端口
    port = config["debug_port"]
    if not isinstance(port, int) or port <= 0 or port > 65535:
        raise BrowserStartError(f"debug_port 必须为 1-65535 之间的整数: {port}")

    # 检查 args 中是否重复覆盖端口或用户目录
    args = config.get("args", [])
    for arg in args:
        if "--remote-debugging-port" in arg:
            raise BrowserStartError(
                "args 不能包含 --remote-debugging-port，请使用 debug_port 配置"
            )
        if "--user-data-dir" in arg:
            raise BrowserStartError(
                "args 不能包含 --user-data-dir，请使用 user_data_dir 配置"
            )


def build_command(config: dict) -> list:
    """构造启动命令

    Args:
        config: 配置字典

    Returns:
        命令参数列表
    """
    # 可执行文件（绝对路径）
    executable = str(Path(config["executable"]).resolve())

    # 调试端口
    debug_port = config["debug_port"]

    # 用户数据目录（相对路径转为绝对路径）
    user_data_dir = config["user_data_dir"]
    if not Path(user_data_dir).is_absolute():
        user_data_dir = str((PROJECT_ROOT / user_data_dir).resolve())
    else:
        user_data_dir = str(Path(user_data_dir).resolve())

    # 启动 URL
    start_url = config["start_url"]

    # 构造命令
    command = [
        executable,
        f"--remote-debugging-port={debug_port}",
        f"--user-data-dir={user_data_dir}",
    ]

    # 添加用户自定义参数
    args = config.get("args", [])
    command.extend(args)

    # 添加启动 URL
    command.append(start_url)

    return command


if __name__ == "__main__":
    sys.exit(main())
