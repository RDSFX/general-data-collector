"""定时调度器

负责：
- 固定间隔调度（首轮立即执行）
- 随机抖动支持（避免整点流量尖峰）
- 总采集次数限制（可选配置）
- 生命周期管理（API Session 每轮重建，浏览器 Page 持久化）
- Ctrl+C 优雅退出（当前轮完成后）
- 单轮失败不影响下一轮
- 浏览器断连/Tab 关闭时退出
"""

import sys
import signal
import time
import random
import importlib.util
from pathlib import Path
from typing import Any, Optional
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


class TimerError(Exception):
    """调度器错误"""
    pass


# 全局退出标志
_exit_flag = False


def signal_handler(signum, frame):
    """信号处理器（Ctrl+C）"""
    global _exit_flag
    print("\n[信息] 收到中断信号，等待当前轮完成后退出...", file=sys.stderr)
    _exit_flag = True


def main() -> int:
    """主入口

    Returns:
        退出码：0 成功，1 失败
    """
    # 检查参数数量
    if len(sys.argv) != 2:
        print("用法: python timer.py <配置文件路径>", file=sys.stderr)
        print(f"实际参数数量: {len(sys.argv) - 1}", file=sys.stderr)
        return 1

    config_path = sys.argv[1]

    try:
        # 加载配置
        config = load_config(config_path)
        task_name = config["name"]

        # 读取间隔秒数
        schedule = config.get("schedule", {})
        interval_seconds = schedule.get("interval_seconds")
        if not interval_seconds or interval_seconds <= 0:
            print(f"[错误] 配置文件缺少 [schedule].interval_seconds 或值无效", file=sys.stderr)
            print(f"请在配置文件中添加:", file=sys.stderr)
            print(f"[schedule]", file=sys.stderr)
            print(f"interval_seconds = 60  # 采集间隔秒数", file=sys.stderr)
            return 1

        # 配置日志
        logger = setup_logging(task_name)
        logger.info(f"定时调度器启动: {task_name}")
        logger.info(f"配置文件: {config_path}")
        logger.info(f"间隔: {interval_seconds} 秒")
        logger.info(f"模板: {config['template']}")

        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)

        # 运行调度器
        run_scheduler(config, interval_seconds, logger)

        logger.info("调度器退出")
        return 0

    except ConfigError as e:
        print(f"[错误] 配置错误: {e}", file=sys.stderr)
        return 1
    except TimerError as e:
        print(f"[错误] 调度错误: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[错误] 未预期异常: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def run_scheduler(config: dict[str, Any], interval_seconds: int, logger) -> None:
    """运行调度器主循环

    Args:
        config: 任务配置
        interval_seconds: 间隔秒数
        logger: 日志记录器

    Raises:
        TimerError: 调度失败
    """
    template_name = config["template"]
    round_num = 0

    # 读取最大轮次限制（可选）
    schedule = config.get("schedule", {})
    max_rounds = schedule.get("max_rounds", 0)

    if max_rounds > 0:
        logger.info(f"配置最大轮次: {max_rounds}")

    # 判断模板类型
    is_browser = template_name in {"browser_api", "browser_page"}

    # 浏览器模板：创建持久化上下文
    if is_browser:
        try:
            context, playwright, browser = create_browser_context(config, logger)
        except BrowserError as e:
            raise TimerError(f"创建浏览器上下文失败: {e}")
    else:
        context, playwright, browser = None, None, None

    try:
        while True:
            round_num += 1

            # 检查是否达到最大轮次
            if max_rounds > 0 and round_num > max_rounds:
                logger.info(f"已完成 {max_rounds} 轮采集，达到配置限制，停止调度")
                break

            logger.info(f"===== 第 {round_num} 轮开始 =====")

            # 检查退出标志
            if _exit_flag:
                logger.info("收到退出信号，停止调度")
                break

            # API 模板：每轮创建新 Session
            if not is_browser:
                context = requests.Session()

            # 执行单轮采集
            try:
                execute_round(config, context, logger)
                logger.info(f"第 {round_num} 轮采集成功")
            except Exception as e:
                logger.error(f"第 {round_num} 轮采集失败: {e}")
                # 单轮失败不影响下一轮

            # API 模板：关闭 Session
            if not is_browser and context:
                context.close()
                context = None

            # 浏览器模板：检查 Page 是否仍然有效
            if is_browser:
                if context.is_closed():
                    logger.error("浏览器 Tab 已关闭，退出调度")
                    break

            # 检查退出标志
            if _exit_flag:
                logger.info("收到退出信号，停止调度")
                break

            # 检查是否已完成所有轮次（在等待前）
            if max_rounds > 0 and round_num >= max_rounds:
                logger.info(f"已完成 {max_rounds} 轮采集，达到配置限制，停止调度")
                break

            # 计算实际等待时间（支持随机抖动）
            actual_wait = _calculate_wait_time(config, interval_seconds)
            logger.info(f"等待 {actual_wait:.1f} 秒后执行下一轮")

            # 等待下一轮
            elapsed = 0.0
            while elapsed < actual_wait:
                if _exit_flag:
                    logger.info("等待期间收到退出信号，停止调度")
                    break
                time.sleep(1)
                elapsed += 1.0

            if _exit_flag:
                break

    finally:
        # 清理资源
        if is_browser and context:
            cleanup_browser_context(context, playwright, browser, logger)
        elif not is_browser and context:
            context.close()


def execute_round(config: dict[str, Any], context, logger) -> None:
    """执行单轮采集

    Args:
        config: 任务配置
        context: 上下文对象（Session 或 Page）
        logger: 日志记录器

    Raises:
        Exception: 执行失败
    """
    template_name = config["template"]

    # 加载模板模块
    template_module = load_template(template_name)

    # 检查模板是否实现 run 函数
    if not hasattr(template_module, "run"):
        raise TimerError(f"模板 {template_name} 未实现 run() 函数")

    # 调用模板
    logger.info("开始执行模板...")
    result = template_module.run(config, context)
    logger.info("模板执行完成")

    # 保存结果
    task_name = config["name"]
    save_result(task_name, result)


def load_template(template_name: str):
    """加载模板模块

    Args:
        template_name: 模板名称

    Returns:
        模板模块对象

    Raises:
        TimerError: 模板文件不存在或加载失败
    """
    if template_name not in TEMPLATE_FILES:
        raise TimerError(f"未知模板: {template_name}")

    template_file = TEMPLATE_FILES[template_name]
    template_path = PROJECT_ROOT / template_file

    if not template_path.exists():
        raise TimerError(f"模板文件不存在: {template_path}")

    try:
        spec = importlib.util.spec_from_file_location(template_name, template_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        raise TimerError(f"加载模板失败: {e}")


def _calculate_wait_time(config: dict[str, Any], base_interval: int) -> float:
    """计算实际等待时间（支持随机抖动）

    Args:
        config: 任务配置
        base_interval: 基准间隔秒数

    Returns:
        实际等待秒数（浮点数）
    """
    # 读取抖动配置（可选）
    schedule = config.get("schedule", {})
    jitter_percent = schedule.get("jitter_percent", 0)

    # 无抖动时直接返回基准间隔
    if jitter_percent <= 0:
        return float(base_interval)

    # 计算抖动范围（均匀分布）
    jitter_ratio = jitter_percent / 100.0
    min_wait = base_interval * (1 - jitter_ratio)
    max_wait = base_interval * (1 + jitter_ratio)

    # 生成随机等待时间
    return random.uniform(min_wait, max_wait)


if __name__ == "__main__":
    sys.exit(main())
