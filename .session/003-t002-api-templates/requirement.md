# 需求

## 任务 ID

T002 - 普通 API 与 OKX 模板

## 本次承接范围

完整实现 T002，包括：

1. **HTTP 请求模块**：实现 shared/http.py，支持 HTTP 参数、JSON/文本请求体、解码、超时
2. **普通 API 模板**：实现 template/api_request.py，支持常规 HTTP 请求
3. **OKX API 模板**：实现 template/okx_api.py，支持 HMAC-SHA256 签名认证
4. **扩展配置校验**：在 shared/config.py 中扩展 HTTP 相关字段校验
5. **扩展执行器**：在 executor.py 中集成 HTTP 会话上下文管理

## 验收标准（来自冻结计划）

- 本地服务覆盖 JSON/文本、最终状态非 2xx、请求异常和超时
- 普通 API 的 2xx 业务错误内容仍保存
- 固定时间的签名向量核对，验证查询串/请求体的签名内容与发送内容一致
- OKX 必须同时满足 HTTP 2xx 和 code="0"，缺少 code、业务失败或非 JSON 响应不写成功记录
- 真实验证：用户提供有效只读接口与认证环境；不执行交易或资金操作。缺失时保留未验收项

## 依赖状态

- T001 ✅ 已完成：executor.py、shared/config.py、shared/output.py 已就绪

## 实施约束

- 在 T001 后扩展 shared/config.py 和 executor.py，不破坏现有功能
- 按冻结架构实现 OKX 签名流程
- 遵守共享文件修改顺序（T001 -> T002 -> T003）
