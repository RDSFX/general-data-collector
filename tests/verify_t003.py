"""验证脚本：测试浏览器启动和配置读取

不依赖真实浏览器，验证配置和命令构造
"""

import sys
sys.path.insert(0, '/sessions/magical-peaceful-hawking/mnt/data-collector')

from scripts.start_browser import load_browser_config, validate_config, build_command
from pathlib import Path


def test_browser_config():
    """测试浏览器配置读取"""
    print("=== 测试浏览器配置读取 ===")

    try:
        config = load_browser_config()
        print(f"✅ 配置加载成功")
        print(f"  executable: {config['executable']}")
        print(f"  debug_port: {config['debug_port']}")
        print(f"  user_data_dir: {config['user_data_dir']}")
        print(f"  start_url: {config['start_url']}")
        print(f"  args 数量: {len(config.get('args', []))}")
        return config
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return None


def test_validate_config(config):
    """测试配置校验"""
    print("\n=== 测试配置校验 ===")

    try:
        # 注意：可执行文件路径在 Linux 环境可能不存在，这是预期的
        validate_config(config)
        print(f"✅ 配置校验通过")
    except Exception as e:
        # Windows Chrome 路径在 Linux 不存在是正常的
        if "可执行文件不存在" in str(e):
            print(f"⚠️  可执行文件路径验证（Windows 路径在 Linux 环境不存在是预期的）: {e}")
        else:
            print(f"❌ 配置校验失败: {e}")
            raise


def test_build_command(config):
    """测试命令构造"""
    print("\n=== 测试命令构造 ===")

    try:
        command = build_command(config)
        print(f"✅ 命令构造成功，参数数量: {len(command)}")
        print(f"  可执行文件: {command[0]}")
        print(f"  调试端口参数: {command[1]}")
        print(f"  用户目录参数: {command[2]}")

        # 验证不包含重复参数
        has_duplicate = False
        for i, arg in enumerate(command):
            if i > 2 and ("--remote-debugging-port" in arg or "--user-data-dir" in arg):
                has_duplicate = True
                print(f"❌ 发现重复参数: {arg}")

        if not has_duplicate:
            print(f"✅ 无重复端口/用户目录参数")

    except Exception as e:
        print(f"❌ 命令构造失败: {e}")
        raise


def test_init_script():
    """测试初始化脚本存在"""
    print("\n=== 测试初始化脚本 ===")

    script_path = Path('/sessions/magical-peaceful-hawking/mnt/data-collector/scripts/browser_init.js')
    if script_path.exists():
        content = script_path.read_text(encoding='utf-8')
        if 'Navigator.prototype' in content and 'webdriver' in content:
            print(f"✅ 初始化脚本存在且包含 webdriver 修改逻辑")
        else:
            print(f"❌ 初始化脚本内容不符合预期")
    else:
        print(f"❌ 初始化脚本不存在: {script_path}")


if __name__ == "__main__":
    config = test_browser_config()
    if config:
        test_validate_config(config)
        test_build_command(config)
    test_init_script()
    print("\n=== 验证完成 ===")
