import sys
import logging
from .config import LOG_LEVEL

LOGGER_NAME = "yanda_shop"
_context = "setup_logging"


def setup_logging() -> None:
    """
    Настраивает корневой logger приложения:
      - выводит в stdout
      - формат: время – логгер – уровень – сообщение
    """
    logging.basicConfig()  # сброс базовых настроек, если были
    level_name = LOG_LEVEL.upper() if isinstance(LOG_LEVEL, str) else None
    level = getattr(logging, level_name, logging.INFO)

    # START
    root = logging.getLogger()
    root.setLevel(level)
    logging.getLogger(LOGGER_NAME).info("%s START with level=%s", _context, level_name or level)

    # Очистка старых handlers
    for handler in list(root.handlers):
        root.removeHandler(handler)
        logging.getLogger(LOGGER_NAME).debug("%s removed handler %r", _context, handler)

    # Новый StreamHandler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    root.addHandler(handler)
    logging.getLogger(LOGGER_NAME).info("%s END: handler added with format='%s'", _context, fmt)


# глобальный логгер
logger = logging.getLogger(LOGGER_NAME)
