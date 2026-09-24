"""验证脚本：测试定时调度器逻辑

不依赖真实环境，验证代码逻辑
"""

import sys
sys.path.insert(0, '/sessions/magical-peaceful-hawking/mnt/data-collector')

from pathlib import Path


def test_timer_module():
    """测试 timer.py 模块"""
    print("=== 测试 timer.py 模块 ===")

    try:
        import timer
        print(f"✅ timer 模块导入成功")

        # 检查关键函数存在
        functions = ['main', 'run_scheduler', 'execute_round', 'load_template', 'signal_handler']
        for func_name in functions:
            if hasattr(timer, func_name):
                print(f"✅ {func_name} 函数存在")
            else:
                print(f"❌ {func_name} 函数不存在")

        # 检查全局退出标志
        if hasattr(timer, '_exit_flag'):
            print(f"✅ _exit_flag 全局变量存在")
        else:
            print(f"❌ _exit_flag 全局变量不存在")

        # 检查模板映射
        if hasattr(timer, 'TEMPLATE_FILES'):
            templates = timer.TEMPLATE_FILES
            print(f"✅ TEMPLATE_FILES 存在，包含 {len(templates)} 个模板")
            for name in ['api_request', 'okx_api', 'browser_api', 'browser_page']:
                if name in templates:
                    print(f"  ✅ {name} 模板已映射")
                else:
                    print(f"  ❌ {name} 模板未映射")
        else:
            print(f"❌ TEMPLATE_FILES 不存在")

    except Exception as e:
        print(f"❌ timer 模块测试失败: {e}")


def test_template_loading():
    """测试模板加载逻辑"""
    print("\n=== 测试模板加载 ===")

    try:
        from timer import load_template

        # 测试加载 API 模板
        try:
            module = load_template('api_request')
            if hasattr(module, 'run'):
                print(f"✅ api_request 模板加载成功，包含 run 函数")
            else:
                print(f"❌ api_request 模板缺少 run 函数")
        except Exception as e:
            print(f"❌ api_request 模板加载失败: {e}")

        # 测试加载浏览器模板
        try:
            module = load_template('browser_page')
            if hasattr(module, 'run'):
                print(f"✅ browser_page 模板加载成功，包含 run 函数")
            else:
                print(f"❌ browser_page 模板缺少 run 函数")
        except Exception as e:
            print(f"❌ browser_page 模板加载失败: {e}")

        # 测试未知模板
        try:
            module = load_template('unknown_template')
            print(f"❌ 未知模板应该抛出异常但未抛出")
        except Exception as e:
            if "未知模板" in str(e):
                print(f"✅ 未知模板正确抛出异常")
            else:
                print(f"⚠️ 异常信息不符合预期: {e}")

    except Exception as e:
        print(f"❌ 模板加载测试失败: {e}")


def test_signal_handler():
    """测试信号处理器"""
    print("\n=== 测试信号处理器 ===")

    try:
        import timer

        # 重置退出标志
        timer._exit_flag = False
        print(f"✅ 初始退出标志: {timer._exit_flag}")

        # 调用信号处理器
        timer.signal_handler(None, None)
        print(f"✅ 调用信号处理器后退出标志: {timer._exit_flag}")

        if timer._exit_flag:
            print(f"✅ 信号处理器正确设置退出标志")
        else:
            print(f"❌ 信号处理器未设置退出标志")

        # 重置
        timer._exit_flag = False

    except Exception as e:
        print(f"❌ 信号处理器测试失败: {e}")


def test_api_templates_exist():
    """测试所有模板文件存在"""
    print("\n=== 测试模板文件存在性 ===")

    templates = {
        'api_request': '/sessions/magical-peaceful-hawking/mnt/data-collector/template/api_request.py',
        'okx_api': '/sessions/magical-peaceful-hawking/mnt/data-collector/template/okx_api.py',
        'browser_api': '/sessions/magical-peaceful-hawking/mnt/data-collector/template/browser_api.py',
        'browser_page': '/sessions/magical-peaceful-hawking/mnt/data-collector/template/browser_page.py',
    }

    for name, path in templates.items():
        if Path(path).exists():
            print(f"✅ {name} 模板文件存在")
        else:
            print(f"❌ {name} 模板文件不存在: {path}")


if __name__ == "__main__":
    test_timer_module()
    test_template_loading()
    test_signal_handler()
    test_api_templates_exist()
    print("\n=== 验证完成 ===")
