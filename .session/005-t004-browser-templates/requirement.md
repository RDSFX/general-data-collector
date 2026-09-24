# 需求

## 任务 ID

T004 - 浏览器 API 与页面模板

## 本次承接范围

完整实现 T004，包括：

1. **浏览器内 API 请求模板**：实现 template/browser_api.py，执行 JavaScript 并返回结果
2. **浏览器页面采集模板**：实现 template/browser_page.py，支持动作序列和 XPath 字段提取
3. **请求 JavaScript**：创建 scripts/request.js，封装 fetch API
4. **XPath 提取逻辑**：实现字段提取、多值处理、类型转换

## 验收标准（来自冻结计划）

### browser_api 模板
- 读取并执行用户提供的 JS 脚本
- JS 返回 JSON 对象作为采集结果
- 脚本执行失败或非 JSON 响应明确报错
- 超时控制（operation_seconds）
- 真实验证：用户提供实际 URL 和请求脚本

### browser_page 模板
- 顺序执行 actions 数组（click、wait、fill、select、waitForSelector）
- XPath 提取支持单值/多值、文本/属性/HTML
- 空值、无匹配元素、XPath 错误明确报错
- 字段值类型转换（字符串、数值、布尔）
- 真实验证：用户提供实际 URL、XPath、动作序列

## 依赖状态

- T001 ✅ 已完成：executor.py、shared/config.py、shared/output.py 已就绪
- T003 ✅ 已完成：shared/browser.py、Page 上下文管理已就绪

## 实施约束

- 在 T003 后扩展模板实现，不修改共享文件
- 按冻结架构实现动作执行和字段提取
- 遵守共享文件修改顺序（T001 -> T002 -> T003 -> T004）
