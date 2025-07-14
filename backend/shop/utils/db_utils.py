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
    context = "session_scope"
    session = db.session
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        logger.warning("%s ROLLBACK on SQLAlchemyError", context, exc_info=True)
        raise
    except Exception:
        session.rollback()
        logger.exception("%s UNEXPECTED error, ROLLBACK", context)
        raise
    finally:
        db.session.remove()
