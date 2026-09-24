"""历史输出与日志模块

负责：
- JSONL 追加保存成功结果
- 按任务名称和日期分文件
- 日志配置（脱敏认证信息）
- 写入失败立即报错退出
"""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 数据和日志目录
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"


class OutputError(Exception):
    """输出错误，应立即退出任务"""
    pass


def save_result(task_name: str, data: Any) -> None:
    """保存成功结果到 JSONL

    Args:
        task_name: 任务名称
        data: JSON 可序列化的结果数据

    Raises:
        OutputError: 写入失败
    """
    # 获取当前时间（含时区）
    now = datetime.now(timezone.utc).astimezone()
    collected_at = now.isoformat()
    date_str = now.strftime("%Y-%m-%d")

    # 构造记录
    record = {
        "task": task_name,
        "collected_at": collected_at,
        "data": data,
    }

    # 确定输出文件路径
    task_data_dir = DATA_DIR / task_name
    output_file = task_data_dir / f"{date_str}.jsonl"

    # 创建目录
    try:
        task_data_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise OutputError(f"无法创建数据目录 {task_data_dir}: {e}")

    # 序列化为 JSON
    try:
        json_line = json.dumps(record, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise OutputError(f"数据无法序列化为 JSON: {e}")

    # 追加到文件（UTF-8）
    try:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(json_line + "\n")
    except Exception as e:
        raise OutputError(f"写入数据文件 {output_file} 失败: {e}")


def setup_logging(task_name: str) -> logging.Logger:
    """配置任务日志

    日志文件按任务名称和日期分文件，脱敏认证信息

    Args:
        task_name: 任务名称

    Returns:
        配置好的 logger

    Raises:
        OutputError: 日志目录创建失败
    """
    # 获取当前日期
    now = datetime.now(timezone.utc).astimezone()
    date_str = now.strftime("%Y-%m-%d")

    # 确定日志文件路径
    task_logs_dir = LOGS_DIR / task_name
    log_file = task_logs_dir / f"{date_str}.log"

    # 创建目录
    try:
        task_logs_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise OutputError(f"无法创建日志目录 {task_logs_dir}: {e}")

    # 配置 logger
    logger = logging.getLogger(f"data-collector.{task_name}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()  # 清除已有 handler，避免重复

    # 文件 handler（UTF-8）
    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
    except Exception as e:
        raise OutputError(f"无法创建日志文件 {log_file}: {e}")

    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 添加脱敏过滤器
    logger.addFilter(SensitiveFilter())

    return logger


class SensitiveFilter(logging.Filter):
    """日志脱敏过滤器

    隐藏认证相关敏感信息
    """

    # 需要脱敏的模式
    PATTERNS = [
        # Authorization header
        (re.compile(r"(Authorization['\"]?\s*:\s*['\"]?)[^'\"]+", re.IGNORECASE), r"\1***"),
        # API key patterns
        (re.compile(r"(api[_-]?key['\"]?\s*[:=]\s*['\"]?)[^'\"]+", re.IGNORECASE), r"\1***"),
        (re.compile(r"(secret[_-]?key['\"]?\s*[:=]\s*['\"]?)[^'\"]+", re.IGNORECASE), r"\1***"),
        (re.compile(r"(passphrase['\"]?\s*[:=]\s*['\"]?)[^'\"]+", re.IGNORECASE), r"\1***"),
        # Bearer token
        (re.compile(r"(Bearer\s+)[^\s]+", re.IGNORECASE), r"\1***"),
        # OK-ACCESS-* headers
        (re.compile(r"(OK-ACCESS-[A-Z]+['\"]?\s*:\s*['\"]?)[^'\"]+", re.IGNORECASE), r"\1***"),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """脱敏日志消息"""
        if isinstance(record.msg, str):
            for pattern, replacement in self.PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        return True
