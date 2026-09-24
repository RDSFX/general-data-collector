# 实施计划

## 步骤

### 1. 准备依赖
- 创建 requirements.txt，声明 requests、playwright 版本
- 安装到 .venv

### 2. 实现 shared/config.py
- UTF-8 读取 TOML
- 校验必填字段（name、template、schedule/timeouts）
- 校验任务名称格式（字母数字下划线连字符，拒绝 Windows 保留名）
- 校验路径存在性（browser.script、请求 JS）
- 校验模板名称合法性（四选一）
- 相对路径以项目根目录为基准

### 3. 实现 shared/output.py
- JSONL 追加：{"task":"name","collected_at":"ISO 8601","data":...}
- 日期分文件：data/<task_name>/<YYYY-MM-DD>.jsonl
- 日志配置：logs/<task_name>/<YYYY-MM-DD>.log，脱敏认证信息
- 写入失败时立即报错退出

### 4. 实现 executor.py
- CLI：恰好一个位置参数（配置路径）
- 模板映射：api_request、okx_api、browser_api、browser_page
- 上下文管理：HTTP 会话或 Page（本阶段用 None 桩）
- 调用模板 run(config, context)
- 成功结果统一写入 JSONL
- 错误分类：配置错误立即退出，可恢复错误记日志
- 模板未实现明确报错

### 5. 创建模板桩
- template/api_request.py：返回测试数据 {"message": "api_request stub"}
- template/okx_api.py：返回 {"message": "okx_api stub"}
- template/browser_api.py：返回 {"message": "browser_api stub"}
- template/browser_page.py：返回 {"message": "browser_page stub"}

### 6. 验证
- 创建测试配置 config/tasks/test_executor.toml
- 运行 executor.py，验证：
  - 配置读取成功
  - 模板桩被调用
  - JSONL 正确追加
  - 日志文件生成
  - 多次运行追加到同一文件
  - 非法配置被拒绝
  - 多个参数被拒绝

## 关键接口

模板接口（冻结）：
```python
def run(config: dict, context) -> dict:
    """返回 JSON 可序列化数据"""
    pass
```

输出接口：
```python
def save_result(task_name: str, data: dict) -> None:
    """保存成功结果到 JSONL"""
    pass
```
