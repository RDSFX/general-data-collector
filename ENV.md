# 环境配置说明

本文档说明如何配置和准备 data-collector 的运行环境。

## 运行需求

- **Python**：3.11.5
- **浏览器**：Google Chrome（用于浏览器采集）

## 环境准备步骤

### 虚拟环境

**创建并激活虚拟环境**：
```powershell
# Powershell
python -m venv .venv
.venv\Scripts\activate
```


**验证激活**：
```powershell
# 命令提示符前应显示 (.venv)
```

### 安装依赖

```powershell
pip install -r requirements.txt
```

**依赖包说明**：
- `requests`：HTTP 请求库（API 模板）
- `playwright`：浏览器自动化库（浏览器模板）
- `tomli`：TOML 解析库

### 配置浏览器启动参数

编辑 `config/browser.toml`：

```toml
# Chrome 可执行文件路径
executable = "C:/Program Files/Google/Chrome/Application/chrome.exe"

# CDP 调试端口
debug_port = 9222

# 用户数据目录（相对项目根目录）
user_data_dir = ".runtime/browser-profile"

# 启动时打开的页面
start_url = "about:blank"

# 附加启动参数
args = [
  "--no-first-run",
  "--no-default-browser-check",
  "--start-maximized",
]
```

**注意事项**：
- 路径使用正斜杠 `/` 或转义反斜杠 `\\`
- 不要在 `args` 中重复设置 `--remote-debugging-port` 或 `--user-data-dir`
- `user_data_dir` 用于隔离浏览器配置文件，避免与日常使用的 Chrome 冲突

### 启动浏览器

```powershell
.\start-browser.bat
```

**验证启动成功**：
1. Chrome 窗口打开
2. 访问 http://127.0.0.1:9222 显示 JSON 响应

**常见问题**：
- 如果端口已被占用，修改 `config/browser.toml` 中的 `debug_port`
- 如果路径错误，检查 `executable` 配置是否正确


### 验证浏览器连接

1. 启动浏览器：
   ```powershell
   .\start-browser.bat
   ```

2. 运行测试脚本：
   ```powershell
   python tests/verify_t003.py
   ```

3. 预期输出：
   ```
   === 测试浏览器配置读取 ===
   ✅ 配置加载成功
   ✅ 配置校验通过
   ✅ 命令构造成功
   ✅ 初始化脚本存在
   ```

### 验证 API 采集

```powershell
python executor.py config/tasks/example_api.toml
```

预期：成功采集并保存结果到 `data/example_api/`。

## 目录结构

运行后会自动创建以下目录：

```
data-collector/
├── .runtime/               # 运行时数据
│   └── browser-profile/    # 浏览器用户数据
├── data/                   # 采集数据（按任务分目录）
│   └── <task_name>/
│       └── <YYYY-MM-DD>.jsonl
└── logs/                   # 日志文件（按任务分目录）
    └── <task_name>/
        └── <YYYY-MM-DD>.log
```

## 故障排查

### Python 相关

**Q: `ModuleNotFoundError: No module named 'xxx'`**

A: 确认虚拟环境已激活，重新安装依赖：
```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Q: `tomllib` 或 `tomli` 导入错误**

A: 检查 Python 版本：
- Python 3.11+：使用内置 `tomllib`
- Python 3.10：需要安装 `tomli`

### 浏览器相关

**Q: 浏览器启动失败**

A: 检查步骤：
1. 确认 Chrome 已安装
2. 检查 `config/browser.toml` 中的 `executable` 路径
3. 确认路径使用正斜杠或转义反斜杠
4. 运行 `python scripts/start_browser.py` 查看详细错误

**Q: CDP 端口访问失败**

A: 检查步骤：
1. 确认浏览器已启动
2. 确认端口未被占用（`netstat -ano | findstr 9222`）
3. 尝试访问 http://127.0.0.1:9222

**Q: `Page is closed` 错误**

A: 不要手动关闭调度器创建的 Tab，使用 `Ctrl+C` 停止。

### 配置相关

**Q: 配置文件读取失败**

A: 确认：
1. 文件使用 UTF-8 编码
2. TOML 语法正确（使用在线 TOML 验证器检查）
3. 必填字段完整

**Q: 路径错误**

A: 配置文件路径和脚本路径：
- 支持绝对路径
- 相对路径基于项目根目录解析


## 性能建议

1. **合理设置采集间隔**：避免过于频繁的请求
2. **调整超时配置**：根据实际响应时间设置 `http_seconds` 和 `operation_seconds`
3. **监控日志大小**：定期清理旧日志文件
4. **数据归档**：定期备份或归档历史数据

## 下一步

环境配置完成后，参考 [README.md](README.md) 了解如何使用。
