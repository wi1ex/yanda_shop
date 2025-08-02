from datetime import datetime
from zoneinfo import ZoneInfo
from flask_jwt_extended import get_jwt_identity, get_jwt
from ..models import ChangeLog
from ..utils.db_utils import session_scope

def log_change(action_type: str, description: str) -> None:
    """
    Добавляет запись в ChangeLog.
    author_id и author_name берутся из JWT, timestamp -- текущее время в Europe/Moscow.
    """
    author_id = get_jwt_identity()
    claims = get_jwt()
    author_name = claims.get("username", "<unknown>")
    now = datetime.now(ZoneInfo("Europe/Moscow"))

    with session_scope() as session:
        session.add(
            ChangeLog(
                author_id=int(author_id),
                author_name=author_name,
                action_type=action_type,
                description=description,
                timestamp=now,
            )
        )
