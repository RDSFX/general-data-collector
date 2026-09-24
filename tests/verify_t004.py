"""验证脚本：测试浏览器模板的逻辑

不依赖真实浏览器，验证代码逻辑
"""

import sys
sys.path.insert(0, '/sessions/magical-peaceful-hawking/mnt/data-collector')

from pathlib import Path


def test_request_js_exists():
    """测试 request.js 存在性"""
    print("=== 测试 request.js ===")

    script_path = Path('/sessions/magical-peaceful-hawking/mnt/data-collector/scripts/request.js')
    if script_path.exists():
        content = script_path.read_text(encoding='utf-8')
        if 'async function request' in content and 'fetch' in content:
            print(f"✅ request.js 存在且包含 fetch 封装")
        else:
            print(f"❌ request.js 内容不符合预期")
    else:
        print(f"❌ request.js 不存在: {script_path}")


def test_browser_api_template():
    """测试 browser_api 模板逻辑"""
    print("\n=== 测试 browser_api 模板 ===")

    try:
        from template import browser_api
        print(f"✅ browser_api 模块导入成功")

        # 检查 run 函数存在
        if hasattr(browser_api, 'run'):
            print(f"✅ run 函数存在")
        else:
            print(f"❌ run 函数不存在")

        # 检查辅助函数
        if hasattr(browser_api, '_inject_request_helper'):
            print(f"✅ _inject_request_helper 函数存在")
        else:
            print(f"❌ _inject_request_helper 函数不存在")

    except Exception as e:
        print(f"❌ browser_api 模块导入失败: {e}")


def test_browser_page_template():
    """测试 browser_page 模板逻辑"""
    print("\n=== 测试 browser_page 模板 ===")

    try:
        from template import browser_page
        print(f"✅ browser_page 模块导入成功")

        # 检查 run 函数
        if hasattr(browser_page, 'run'):
            print(f"✅ run 函数存在")
        else:
            print(f"❌ run 函数不存在")

        # 检查辅助函数
        functions = ['execute_actions', 'extract_fields', '_extract_element_value', '_convert_type']
        for func_name in functions:
            if hasattr(browser_page, func_name):
                print(f"✅ {func_name} 函数存在")
            else:
                print(f"❌ {func_name} 函数不存在")

    except Exception as e:
        print(f"❌ browser_page 模块导入失败: {e}")


def test_type_conversion():
    """测试类型转换逻辑"""
    print("\n=== 测试类型转换 ===")

    try:
        from template.browser_page import _convert_type

        # 测试字符串
        assert _convert_type("hello", "string") == "hello"
        print(f"✅ 字符串转换")

        # 测试整数
        assert _convert_type("123", "number") == 123
        print(f"✅ 整数转换")

        # 测试浮点数
        assert _convert_type("123.45", "number") == 123.45
        print(f"✅ 浮点数转换")

        # 测试布尔值
        assert _convert_type("true", "boolean") == True
        assert _convert_type("false", "boolean") == False
        assert _convert_type("1", "boolean") == True
        assert _convert_type("0", "boolean") == False
        print(f"✅ 布尔值转换")

    except Exception as e:
        print(f"❌ 类型转换测试失败: {e}")


if __name__ == "__main__":
    test_request_js_exists()
    test_browser_api_template()
    test_browser_page_template()
    test_type_conversion()
    print("\n=== 验证完成 ===")
