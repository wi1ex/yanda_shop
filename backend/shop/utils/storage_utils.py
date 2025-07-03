import io
import os
import re
import zipfile
from typing import Set, Tuple, List
from minio.error import S3Error
from ..core.logging import logger
from ..utils.db_utils import session_scope
from ..extensions import minio_client, BUCKET
from ..models import Review


def cleanup_old_images(folder: str, expected: Set[str]) -> Tuple[int, int]:
    """
    Удаляет из хранилища все объекты в папке,
    которых нет в множестве expected.
    Возвращает (deleted_count, warn_count).
    """
    logger.info("cleanup_old_images START folder=%s expected_count=%d", folder, len(expected))
    deleted = 0
    warns  = 0
    prefix  = f"{folder}/"
    # list_objects возвращает итератор по объектам
    for obj in minio_client.list_objects(BUCKET, prefix=prefix, recursive=True):
        # убираем префикс и расширение
        base = os.path.splitext(obj.object_name)[0].split("/", 1)[1]
        if expected and base not in expected:
            try:
                minio_client.remove_object(BUCKET, obj.object_name)
                deleted += 1
            except Exception:
                warns += 1

    logger.info("cleanup_old_images END deleted=%d warns=%d", deleted, warns)
    return deleted, warns


def upload_new_images(folder: str, archive_bytes: bytes) -> Tuple[int, int]:
    """
    Из zip-архива, переданного как байты, загружает файлы в папку.
    Возвращает (added_count, replaced_count).
    """
    logger.info("upload_new_images START folder=%s archive_size=%d", folder, len(archive_bytes))
    added     = 0
    replaced  = 0
    prefix    = f"{folder}/"
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            key = prefix + info.filename
            content = archive.read(info.filename)
            try:
                # если объект уже есть — буде replace
                minio_client.stat_object(BUCKET, key)
                replaced += 1
            except S3Error:
                added += 1
            minio_client.put_object(BUCKET, key, io.BytesIO(content), len(content))

    logger.info("upload_new_images END added=%d replaced=%d", added, replaced)
    return added, replaced


def cleanup_review_images() -> List[str]:
    """
    Удаляет из MinIO избыточные изображения отзывов.
    Возвращает список имен удалённых объектов.
    """
    # 1) Собираем все существующие ID отзывов
    with session_scope() as session:
        existing_ids = {r.id for r in session.query(Review.id).all()}

    deleted = []
    # 2) Проходим по всем объектам с префиксом 'reviews/'
    for obj in minio_client.list_objects(BUCKET, prefix="reviews/", recursive=True):
        name = obj.object_name.split("/")[-1]
        # ожидаем формат "<id>_<index>.<ext>"
        m = re.match(r"^(\d+)_(\d+)\.\w+$", name)
        if not m:
            # файл не соответствует никакому шаблону — удаляем
            minio_client.remove_object(BUCKET, obj.object_name)
            deleted.append(obj.object_name)
            continue

        review_id = int(m.group(1))
        index     = int(m.group(2))
        # 3) Удаляем, если нет отзыва или индекс вне [1..3]
        if review_id not in existing_ids or not (1 <= index <= 3):
            minio_client.remove_object(BUCKET, obj.object_name)
            deleted.append(obj.object_name)

    return deleted
