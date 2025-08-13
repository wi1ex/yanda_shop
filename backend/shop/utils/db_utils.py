from contextlib import contextmanager
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from ..core.logging import logger
from ..models import db, Users


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


def adjust_user_order_stats(session, user_id: int, count_delta: int, amount_delta: int) -> None:
    """
    Атомно корректирует агрегаты пользователя.
    Не даёт значениям уйти в минус: GREATEST(0, ...).
    """
    session.query(Users).filter(Users.user_id == user_id).update(
        {
            Users.order_count: func.greatest(0, func.coalesce(Users.order_count, 0) + count_delta),
            Users.total_spent: func.greatest(0, func.coalesce(Users.total_spent, 0) + amount_delta),
        },
        synchronize_session=False,
    )
