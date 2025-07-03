from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from ..core.logging import logger
from ..models import db


@contextmanager
def session_scope():
    """
    Контекстный менеджер для SQLAlchemy-сессии:
    - при выходе без ошибок — commit()
    - при исключении — rollback() и проброс ошибки
    """
    logger.debug("Session scope ENTER")
    session = db.session
    try:
        yield session
        session.commit()
        logger.debug("Session scope COMMIT")
    except SQLAlchemyError:
        session.rollback()
        logger.warning("Session scope ROLLBACK on SQLAlchemyError", exc_info=True)
        raise
    finally:
        db.session.remove()
        logger.debug("Session scope EXIT")
