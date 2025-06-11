import logging
import sys
from config import LOG_LEVEL

def setup_logging() -> None:
    """
    Настраивает корневой logger приложения:
    выводит в stdout, формат: время – модуль – уровень – сообщение.
    """
    level: int = getattr(logging, LOG_LEVEL, logging.INFO)
    root: logging.Logger = logging.getLogger()
    root.setLevel(level)

    # Удаляем старые хэндлеры (если они есть)
    for h in root.handlers[:]:
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    root.addHandler(handler)
