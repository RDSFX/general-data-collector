# 实施计划

## 步骤

### 1. 创建 scripts/request.js
- 封装 fetch API
- 接受参数：url、method、headers、body
- 返回 JSON 对象：{status, data}
- 异常处理和超时控制

### 2. 实现 template/browser_api.py
- 读取用户提供的 JS 脚本文件
- 注入 request.js（如果需要）
- 使用 page.evaluate() 执行脚本
- 应用 operation_seconds 超时
- 验证返回值为 JSON 对象
- 异常处理和错误报告

### 3. 实现 template/browser_page.py
- 读取 actions 数组并顺序执行
- 支持动作类型：
  - click：点击元素
  - wait：等待固定时间
  - fill：填写表单字段
  - select：选择下拉选项
  - waitForSelector：等待元素出现
- 读取 fields 数组并提取字段
- XPath 解析和元素定位
- 支持提取类型：text、attribute、html
- 支持单值/多值（multiple）
- 值类型转换：字符串、数值、布尔
- 空值和错误处理

### 4. 本地验证
- 使用静态 HTML 页面测试 browser_page
- 测试各种动作类型
- 测试 XPath 提取（单值、多值、不同类型）
- 测试错误场景（XPath 错误、元素不存在等）
- 使用 httpbin.org 测试 browser_api

### 5. 真实验证（条件许可时）
- 用户提供实际 URL 和请求脚本
- 用户提供实际 URL、XPath 和动作序列

## 关键接口

动作执行：
```python
def execute_actions(page: Page, actions: list, timeout: float) -> None:
    """顺序执行动作序列"""
    pass
```

字段提取：
```python
def extract_fields(page: Page, fields: list) -> dict:
    """提取字段并返回结果字典"""
    pass
```
