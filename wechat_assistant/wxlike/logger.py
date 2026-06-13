"""统一日志：同时输出到控制台和 logs/ 下的文件。"""

from __future__ import annotations

import logging
import os
from datetime import datetime


def get_logger(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("wxlike")
    if logger.handlers:  # 避免重复添加 handler
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
    )

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)

    os.makedirs("logs", exist_ok=True)
    logfile = os.path.join("logs", f"like_{datetime.now():%Y%m%d}.log")
    file_handler = logging.FileHandler(logfile, encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger
