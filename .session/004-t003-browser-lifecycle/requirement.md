# 需求

## 任务 ID

T003 - 浏览器启动与 Tab 生命周期

## 本次承接范围

完整实现 T003，包括：

1. **浏览器启动脚本**：实现 start-browser.bat 和 scripts/start_browser.py
2. **浏览器配置**：创建 config/browser.toml，集中管理启动参数
3. **CDP 连接模块**：实现 shared/browser.py，支持专属 Tab、初始化脚本、登录确认
4. **初始化脚本**：创建 scripts/browser_init.js，隐藏 webdriver 属性
5. **生命周期管理**：专属 Tab 创建、复用、释放

## 验收标准（来自冻结计划）

- 修改 TOML 即可改变可执行文件、端口、用户目录及附加参数
- 端口与用户目录不能被 args 重复覆盖
- 配置 UTF-8、含空格/中文的路径、不从项目目录启动均可正确处理
- 配置错误和解释器缺失明确报错
- 同 URL 的两个任务产生两个 Tab
- 脚本在本任务导航、刷新和子 frame 生效，不做 context 级注册
- Enter 前不采集
- Ctrl+C 仅关闭自身 Tab，保留其他页面与浏览器
- 断连/Tab 关闭退出

## 依赖状态

- T001 ✅ 已完成：executor.py、shared/config.py、shared/output.py 已就绪

## 实施约束

- 在 T002 后扩展 shared/config.py 和 executor.py
- 遵守共享文件修改顺序（T001 -> T002 -> T003）
- 按冻结架构实现 CDP 连接和 Tab 生命周期
- 浏览器启动和采集进程分离
