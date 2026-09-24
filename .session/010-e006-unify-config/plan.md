# 实施计划

## 步骤

1. **修改 timer.py**
   - 修改 `main()` 参数检查：`len(sys.argv) != 2` → 只接收配置文件路径
   - 移除 CLI 间隔参数解析逻辑
   - 在加载配置后，从 `config["schedule"]["interval_seconds"]` 读取间隔
   - 如果 `schedule` 或 `interval_seconds` 缺失，输出错误并退出

2. **更新文档**
   - README.md：修改"定时调度"章节的命令示例
   - docs/config-examples.md：确认 `interval_seconds` 说明清晰
   - future-enhancements.md：添加 E-006 记录

3. **更新批处理脚本示例**
   - 检查是否有 .bat 文件需要同步修改

## 验收条件

- timer.py 只接收配置文件路径参数
- 从配置文件读取 `interval_seconds`
- 缺失配置时输出清晰错误
- 文档同步完成
- 代码无语法错误
