# 实施计划

## 步骤

### 1. 创建 config/browser.toml
- 定义默认配置：executable、debug_port、user_data_dir、start_url、args
- 按冻结架构设置默认值

### 2. 实现 scripts/start_browser.py
- 使用标准库 tomllib/tomli 读取 browser.toml
- 验证配置：可执行文件存在、参数完整
- 生成启动命令：--remote-debugging-port、--user-data-dir
- 检测 args 中的重复覆盖并报错
- 使用 subprocess 启动浏览器

### 3. 创建 start-browser.bat
- 定位 .venv\Scripts\python.exe
- 调用 scripts\start_browser.py
- 处理路径和错误

### 4. 创建 scripts/browser_init.js
- 修改 Navigator.prototype.webdriver getter
- 返回 undefined

### 5. 实现 shared/browser.py
- CDP 连接：从 debug_port 生成地址
- 创建专属 Tab：使用 Playwright 同步 API
- 注册初始化脚本：Page.add_init_script
- 导航到目标 URL
- wait_for_login 处理：等待 Enter 确认
- 资源释放：关闭 Tab、断开连接

### 6. 扩展 executor.py
- _create_context() 为浏览器模板调用 shared/browser.py
- _cleanup_context() 释放 Page 和 CDP 连接

### 7. 验证
- 启动浏览器并验证端口
- 测试专属 Tab 创建（同 URL 多个任务）
- 测试初始化脚本生效
- 测试 wait_for_login
- 测试 Ctrl+C 清理
- 测试配置修改和错误处理

## 关键接口

浏览器上下文创建：
```python
def create_browser_context(config: dict) -> Page:
    """创建专属 Tab 并返回 Page 对象"""
    pass
```

资源释放：
```python
def cleanup_browser_context(page: Page) -> None:
    """关闭 Tab 并断开连接"""
    pass
```
