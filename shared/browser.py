"""浏览器 CDP 连接与 Tab 生命周期模块

负责：
- CDP 连接（从 debug_port 生成地址）
- 专属 Tab 创建（每个任务独立 Tab）
- 初始化脚本注册（Page 级别）
- 导航到目标 URL
- 人工登录确认（wait_for_login）
- 资源释放（关闭 Tab、断开连接）
"""

from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
import sys

# Python 3.11+ 内置 tomllib，3.10 及以下使用 tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 浏览器配置文件路径
BROWSER_CONFIG = PROJECT_ROOT / "config" / "browser.toml"

# 初始化脚本路径
INIT_SCRIPT = PROJECT_ROOT / "scripts" / "browser_init.js"


class BrowserError(Exception):
    """浏览器相关错误"""
    pass


def create_browser_context(config: dict, logger) -> tuple[Page, any, Browser]:
    """创建浏览器专属 Tab

    Args:
        config: 任务配置（包含 browser 节）
        logger: 日志记录器

    Returns:
        (Page 对象, playwright 实例, Browser 对象)

    Raises:
        BrowserError: 连接失败或创建 Tab 失败
    """
    browser_config = config["browser"]
    target_url = browser_config["url"]
    wait_for_login = browser_config.get("wait_for_login", False)

    # 读取浏览器全局配置
    global_config = _load_browser_config()
    debug_port = global_config["debug_port"]
    cdp_url = f"http://127.0.0.1:{debug_port}"

    # 获取超时配置
    navigation_timeout = config.get("timeouts", {}).get("navigation_seconds", 10) * 1000

    logger.info(f"连接到浏览器 CDP: {cdp_url}")

    try:
        # 启动 Playwright
        playwright = sync_playwright().start()

        # 连接到已运行的浏览器
        browser = playwright.chromium.connect_over_cdp(cdp_url)

        # 获取默认 context
        contexts = browser.contexts
        if not contexts:
            raise BrowserError("浏览器没有可用的 context")
        context: BrowserContext = contexts[0]

        # 创建专属 Tab（新页面）
        page = context.new_page()
        logger.info(f"创建专属 Tab: {page}")

        # 注册初始化脚本（Page 级别）
        _register_init_script(page)

        # 导航到目标 URL
        logger.info(f"导航到: {target_url}")
        page.goto(target_url, timeout=navigation_timeout)

        # 等待人工登录确认
        if wait_for_login:
            logger.info("等待人工登录，请在浏览器中完成登录后回到终端按 Enter 继续...")
            try:
                input()
                logger.info("用户确认登录完成")
            except KeyboardInterrupt:
                # Ctrl+C 时清理资源
                page.close()
                browser.close()
                playwright.stop()
                raise

        return page, playwright, browser

    except Exception as e:
        raise BrowserError(f"创建浏览器 Tab 失败: {e}")


def cleanup_browser_context(page: Page, playwright, browser: Browser, logger) -> None:
    """清理浏览器资源

    仅关闭本任务的 Tab，保留浏览器和其他 Tab

    Args:
        page: Page 对象
        playwright: playwright 实例
        browser: Browser 对象
        logger: 日志记录器
    """
    try:
        if page and not page.is_closed():
            logger.info("关闭专属 Tab")
            page.close()
    except Exception as e:
        logger.warning(f"关闭 Tab 失败: {e}")

    try:
        if browser:
            logger.info("断开 CDP 连接")
            browser.close()
    except Exception as e:
        logger.warning(f"断开连接失败: {e}")

    try:
        if playwright:
            playwright.stop()
    except Exception as e:
        logger.warning(f"停止 Playwright 失败: {e}")


def _load_browser_config() -> dict:
    """加载浏览器全局配置

    Returns:
        配置字典

    Raises:
        BrowserError: 配置文件不存在或格式错误
    """
    if not BROWSER_CONFIG.exists():
        raise BrowserError(f"浏览器配置文件不存在: {BROWSER_CONFIG}")

    try:
        with open(BROWSER_CONFIG, "rb") as f:
            config = tomllib.load(f)
    except Exception as e:
        raise BrowserError(f"读取浏览器配置失败: {e}")

    if "debug_port" not in config:
        raise BrowserError("浏览器配置缺少 debug_port")

    return config


def _register_init_script(page: Page) -> None:
    """注册初始化脚本到 Page

    Args:
        page: Page 对象

    Raises:
        BrowserError: 脚本文件不存在或读取失败
    """
    if not INIT_SCRIPT.exists():
        raise BrowserError(f"初始化脚本不存在: {INIT_SCRIPT}")

    try:
        with open(INIT_SCRIPT, "r", encoding="utf-8") as f:
            script = f.read()
        page.add_init_script(script)
    except Exception as e:
        raise BrowserError(f"注册初始化脚本失败: {e}")
