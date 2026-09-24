# 实施计划

## 步骤

### 1. 实现 timer.py 核心逻辑
- CLI 参数解析：配置路径、间隔秒数
- 加载配置（复用 shared/config.py）
- 日志配置（复用 shared/output.py）
- 主循环：首轮立即执行，后续按间隔
- 信号处理：捕获 Ctrl+C，设置退出标志
- 错误处理：单轮失败不影响下一轮

### 2. 生命周期管理
- 判断模板类型（API vs 浏览器）
- API 模板：每轮创建新 Session，执行后关闭
- 浏览器模板：
  - 首轮创建 Page（调用 shared/browser.py）
  - 后续轮次复用 Page
  - 检测 Page 是否关闭或断连
  - 异常时退出调度器

### 3. 执行单轮采集
- 加载模板模块（复用 executor.py 逻辑）
- 创建或复用上下文
- 调用模板的 run() 函数
- 保存结果（复用 shared/output.py）
- 处理异常并记录日志

### 4. 退出控制
- 设置全局退出标志
- 信号处理器设置标志
- 主循环检查标志，当前轮完成后退出
- 清理资源（关闭 Page 或 Session）

### 5. 本地验证
- 测试 API 模板多轮调度
- 测试固定间隔
- 测试 Ctrl+C 退出
- 测试单轮失败恢复
- 测试参数错误处理

## 关键接口

调度器主循环：
```python
def run_scheduler(config: dict, interval_seconds: int, logger) -> None:
    """运行调度器主循环"""
    pass
```

单轮执行：
```python
def execute_round(config: dict, context, logger) -> None:
    """执行单轮采集"""
    pass
```
