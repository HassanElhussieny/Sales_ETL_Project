import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config.settings import LOG_FILE, LOG_LEVEL, LOG_FORMAT, LOGS_DIR


def get_logger(name: str) -> logging.Logger:

    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL))

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger