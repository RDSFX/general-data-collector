"""浏览器页面采集模板

支持：
- 顺序执行动作序列（refresh、click、wait、fill、select、waitForSelector）
- XPath 字段提取
- 单值/多值支持
- 文本/属性/HTML 提取
- 值类型转换
"""

from typing import Any
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
import time


def run(config: dict[str, Any], context: Page) -> dict[str, Any]:
    """执行浏览器页面采集

    Args:
        config: 任务配置，包含 actions 和 fields
        context: Page 对象

    Returns:
        字段提取结果字典

    Raises:
        Exception: 动作执行或字段提取失败
    """
    page: Page = context

    # 获取超时配置
    timeout_seconds = config.get("timeouts", {}).get("operation_seconds", 10)

    # 执行动作序列
    actions = config.get("actions", [])
    if actions:
        execute_actions(page, actions, timeout_seconds)

    # 提取字段
    fields = config.get("fields", [])
    result = extract_fields(page, fields)

    return result


def execute_actions(page: Page, actions: list[dict], timeout_seconds: float) -> None:
    """顺序执行动作序列

    Args:
        page: Page 对象
        actions: 动作配置列表
        timeout_seconds: 操作超时秒数

    Raises:
        Exception: 动作执行失败
    """
    timeout_ms = timeout_seconds * 1000

    for i, action in enumerate(actions):
        action_type = action.get("type")
        if not action_type:
            raise Exception(f"动作 #{i+1} 缺少 type 字段")

        try:
            if action_type == "refresh":
                # 刷新当前页面
                page.reload(timeout=timeout_ms)

            elif action_type == "click":
                # 点击元素
                selector = action.get("selector")
                if not selector:
                    raise Exception(f"click 动作缺少 selector")
                page.click(selector, timeout=timeout_ms)

            elif action_type == "wait":
                # 等待固定时间（毫秒）
                duration = action.get("duration")
                if duration is None:
                    raise Exception(f"wait 动作缺少 duration")
                time.sleep(duration / 1000)

            elif action_type == "fill":
                # 填写表单字段
                selector = action.get("selector")
                value = action.get("value")
                if not selector:
                    raise Exception(f"fill 动作缺少 selector")
                if value is None:
                    raise Exception(f"fill 动作缺少 value")
                page.fill(selector, str(value), timeout=timeout_ms)

            elif action_type == "select":
                # 选择下拉选项
                selector = action.get("selector")
                value = action.get("value")
                if not selector:
                    raise Exception(f"select 动作缺少 selector")
                if value is None:
                    raise Exception(f"select 动作缺少 value")
                page.select_option(selector, value, timeout=timeout_ms)

            elif action_type == "waitForSelector":
                # 等待元素出现
                selector = action.get("selector")
                if not selector:
                    raise Exception(f"waitForSelector 动作缺少 selector")
                page.wait_for_selector(selector, timeout=timeout_ms)

            else:
                raise Exception(f"不支持的动作类型: {action_type}")

        except PlaywrightTimeout:
            raise Exception(f"动作 #{i+1} ({action_type}) 超时")
        except Exception as e:
            raise Exception(f"动作 #{i+1} ({action_type}) 执行失败: {e}")


def extract_fields(page: Page, fields: list[dict]) -> dict[str, Any]:
    """提取字段

    Args:
        page: Page 对象
        fields: 字段配置列表

    Returns:
        字段名到值的映射字典

    Raises:
        Exception: 字段提取失败
    """
    result = {}

    for field in fields:
        field_name = field.get("name")
        if not field_name:
            raise Exception("字段缺少 name")

        xpath = field.get("xpath")
        if not xpath:
            raise Exception(f"字段 {field_name} 缺少 xpath")

        read_type = field.get("read", "text")
        multiple = field.get("multiple", False)
        value_type = field.get("type", "string")

        try:
            # 定位元素
            elements = page.locator(f"xpath={xpath}").all()

            if not elements:
                raise Exception(f"XPath 未匹配到元素: {xpath}")

            # 提取值
            if multiple:
                # 多值模式
                values = []
                for elem in elements:
                    value = _extract_element_value(elem, read_type)
                    values.append(_convert_type(value, value_type))
                result[field_name] = values
            else:
                # 单值模式（取第一个）
                value = _extract_element_value(elements[0], read_type)
                result[field_name] = _convert_type(value, value_type)

        except Exception as e:
            raise Exception(f"提取字段 {field_name} 失败: {e}")

    return result


def _extract_element_value(element, read_type: str) -> str:
    """从元素提取值

    Args:
        element: Locator 元素
        read_type: 提取类型（text、attribute、html）

    Returns:
        提取的字符串值

    Raises:
        Exception: 提取失败
    """
    if read_type == "text":
        return element.inner_text()
    elif read_type == "html":
        return element.inner_html()
    elif read_type.startswith("attribute:"):
        # attribute:href 格式
        attr_name = read_type.split(":", 1)[1]
        value = element.get_attribute(attr_name)
        if value is None:
            raise Exception(f"属性不存在: {attr_name}")
        return value
    else:
        raise Exception(f"不支持的 read 类型: {read_type}")


def _convert_type(value: str, value_type: str) -> Any:
    """转换值类型

    Args:
        value: 字符串值
        value_type: 目标类型（string、number、boolean）

    Returns:
        转换后的值

    Raises:
        Exception: 转换失败
    """
    if value_type == "string":
        return value
    elif value_type == "number":
        try:
            # 尝试整数
            if "." not in value:
                return int(value)
            # 浮点数
            return float(value)
        except ValueError:
            raise Exception(f"无法转换为数值: {value}")
    elif value_type == "boolean":
        value_lower = value.lower().strip()
        if value_lower in ("true", "1", "yes"):
            return True
        elif value_lower in ("false", "0", "no", ""):
            return False
        else:
            raise Exception(f"无法转换为布尔值: {value}")
    else:
        raise Exception(f"不支持的 type: {value_type}")
