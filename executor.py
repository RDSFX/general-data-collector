"""执行器模块

负责：
- CLI 单次执行入口（恰好一个配置参数）
- 模板映射与调用
- 上下文管理（HTTP 会话或 Page）
- 统一结果落盘
- 错误分类与处理
"""

import sys
import importlib.util
from pathlib import Path
from typing import Any
import requests

from shared.config import load_config, ConfigError, PROJECT_ROOT
from shared.output import save_result, setup_logging, OutputError
from shared.browser import create_browser_context, cleanup_browser_context, BrowserError


# 模板文件映射
TEMPLATE_FILES = {
    "api_request": "template/api_request.py",
    "okx_api": "template/okx_api.py",
    "browser_api": "template/browser_api.py",
    "browser_page": "template/browser_page.py",
}


class ExecutorError(Exception):
    """执行器内部错误"""
    pass


def main() -> int:
    """主入口

    Returns:
        退出码：0 成功，1 失败
    """
    # 检查参数数量
    if len(sys.argv) != 2:
        print("用法: python executor.py <配置文件路径>", file=sys.stderr)
        print(f"实际参数数量: {len(sys.argv) - 1}", file=sys.stderr)
        return 1

    config_path = sys.argv[1]

    try:
        # 加载配置
        config = load_config(config_path)
        task_name = config["name"]

        # 配置日志
        logger = setup_logging(task_name)
        logger.info(f"任务启动: {task_name}")
        logger.info(f"配置文件: {config_path}")
        logger.info(f"模板: {config['template']}")

        # 执行采集
        result = execute_once(config, logger)

        # 保存结果
        save_result(task_name, result)
        logger.info("本轮采集成功")

        return 0

    except ConfigError as e:
        print(f"[错误] 配置错误: {e}", file=sys.stderr)
        return 1
    except OutputError as e:
        print(f"[错误] 输出错误: {e}", file=sys.stderr)
        return 1
    except ExecutorError as e:
        print(f"[错误] 执行错误: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n[信息] 用户中断", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[错误] 未预期异常: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def execute_once(config: dict[str, Any], logger) -> Any:
    """执行一次采集

    Args:
        config: 已校验的配置
        logger: 日志记录器

    Returns:
        JSON 可序列化的结果数据

    Raises:
        ExecutorError: 执行失败
    """
    template_name = config["template"]

    # 加载模板模块
    template_module = load_template(template_name)

    # 检查模板是否实现 run 函数
    if not hasattr(template_module, "run"):
        raise ExecutorError(f"模板 {template_name} 未实现 run() 函数")

    # 准备上下文
    context, playwright, browser = _create_context(template_name, config, logger)

    # 调用模板
    try:
        logger.info("开始执行模板...")
        result = template_module.run(config, context)
        logger.info("模板执行完成")
        return result
    except Exception as e:
        raise ExecutorError(f"模板执行失败: {e}")
    finally:
        # 清理上下文
        _cleanup_context(template_name, context, playwright, browser, logger)


def _create_context(template_name: str, config: dict, logger):
    """为模板创建上下文

    Args:
        template_name: 模板名称
        config: 任务配置
        logger: 日志记录器

    Returns:
        上下文对象（HTTP Session 或 Page）及额外资源
    """
    if template_name in {"api_request", "okx_api"}:
        # API 模板使用 HTTP Session
        return requests.Session(), None, None
    elif template_name in {"browser_api", "browser_page"}:
        # 浏览器模板使用 Page
        try:
            page, playwright, browser = create_browser_context(config, logger)
            return page, playwright, browser
        except BrowserError as e:
            raise ExecutorError(f"创建浏览器上下文失败: {e}")
    else:
        return None, None, None


def _cleanup_context(template_name: str, context, playwright, browser, logger) -> None:
    """清理上下文资源

    Args:
        template_name: 模板名称
        context: 上下文对象（Session 或 Page）
        playwright: playwright 实例（浏览器模板）
        browser: Browser 对象（浏览器模板）
        logger: 日志记录器
    """
    if template_name in {"api_request", "okx_api"}:
        if context and isinstance(context, requests.Session):
            context.close()
    elif template_name in {"browser_api", "browser_page"}:
        if context:  # Page 对象
            cleanup_browser_context(context, playwright, browser, logger)


def load_template(template_name: str):
    """动态加载模板模块

    Args:
        template_name: 模板名称

    Returns:
        模板模块对象

    Raises:
        ExecutorError: 模板不存在或加载失败
    """
    if template_name not in TEMPLATE_FILES:
        raise ExecutorError(
            f"未知模板: {template_name}，有效值: {', '.join(TEMPLATE_FILES.keys())}"
        )

    template_file = TEMPLATE_FILES[template_name]
    template_path = PROJECT_ROOT / template_file

    # 检查模板文件存在
    if not template_path.exists():
        raise ExecutorError(f"模板文件不存在: {template_file}")

    # 动态加载模块
    spec = importlib.util.spec_from_file_location(template_name, template_path)
    if spec is None or spec.loader is None:
        raise ExecutorError(f"无法加载模板: {template_file}")

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        raise ExecutorError(f"模板加载失败 {template_file}: {e}")

    return module


if __name__ == "__main__":
    sys.exit(main())
