import io
import os
import re
import zipfile
from typing import Set, Tuple, List
from minio.error import S3Error
from werkzeug.utils import secure_filename
from ..core.logging import logger
from ..utils.db_utils import session_scope
from ..extensions import minio_client, BUCKET
from ..models import Review


# ——— Helpers —————————————————————————————————————————————
def _safe_stat(bucket: str, key: str) -> bool:
    """Возвращает True, если объект key существует в bucket, иначе False."""
    try:
        minio_client.stat_object(bucket, key)
        return True
    except S3Error:
        return False
    except Exception:
        logger.exception("safe_stat: unexpected error on %s", key)
        return False


def _safe_remove(bucket: str, key: str, context: str) -> bool:
    """
    Пытается удалить объект key из bucket.
    Возвращает True, если удалено, иначе False.
    Логирует успех и все ошибки.
    """
    try:
        minio_client.remove_object(bucket, key)
        logger.debug("%s: removed %s", context, key)
        return True
    except S3Error as err:
        logger.warning("%s: MinIO error removing %s: %s", context, key, err)
        return False
    except Exception:
        logger.exception("%s: unexpected error removing %s", context, key)
        return False


# ——— Product images ——————————————————————————————————————
def upload_product_images(folder: str, archive_bytes: bytes) -> Tuple[int, int]:
    """
    Загружает файлы из ZIP-архива в папку folder/ на MinIO.
    Возвращает (added_count, replaced_count).
    """
    context = "upload_product_images"
    logger.info("%s START folder=%s size=%dB", context, folder, len(archive_bytes))

    try:
        archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
    except zipfile.BadZipFile as e:
        logger.error("%s: invalid ZIP for %s: %s", context, folder, e)
        return 0, 0

    added_count = replaced_count = 0
    for info in archive.infolist():
        if info.is_dir():
            continue

        filename = secure_filename(os.path.basename(info.filename))
        key = f"{folder}/{filename}"

        try:
            with archive.open(info) as stream:
                if _safe_stat(BUCKET, key):
                    replaced_count += 1
                else:
                    added_count += 1

                minio_client.put_object(BUCKET, key, stream, length=info.file_size, part_size=10 * 1024 * 1024)
                logger.info("%s: uploaded %s", context, key)
        except Exception as e:
            logger.exception("%s: error processing %s: %s", context, key, e)

    logger.info("%s END added=%d replaced=%d", context, added_count, replaced_count)
    return added_count, replaced_count


def cleanup_product_images(folder: str, expected: Set[str]) -> Tuple[int, int]:
    """
    Удаляет из MinIO все объекты в папке folder/,
    basename которых нет в expected.
    Возвращает (deleted_count, warning_count).
    """
    context = "cleanup_product_images"
    logger.info("%s START folder=%s expected=%d", context, folder, len(expected))

    try:
        objects = minio_client.list_objects(BUCKET, prefix=f"{folder}/", recursive=True)
    except Exception as e:
        logger.error("%s: list_objects failed for %s/: %s", context, folder, e)
        return 0, 0

    deleted_count = warning_count = 0
    for obj in objects:
        base = os.path.splitext(obj.object_name)[0].split("/", 1)[1]
        if expected and base in expected:
            continue

        if _safe_remove(BUCKET, obj.object_name, context):
            deleted_count += 1
        else:
            warning_count += 1

    logger.info("%s END deleted=%d warnings=%d", context, deleted_count, warning_count)
    return deleted_count, warning_count


# ——— Review images ——————————————————————————————————————
def upload_review_images(review_id: int, files: List) -> int:
    """
    Загружает изображения отзывов в MinIO под префиксом reviews/{review_id}_*.
    Возвращает количество успешно сохранённых файлов.
    """
    context = "upload_review_images"
    logger.info("%s START review_id=%d files=%d", context, review_id, len(files))

    saved = 0
    for idx, file in enumerate(files, start=1):
        if not file or not getattr(file, "filename", None):
            logger.debug("%s: skip empty slot %d for review %d", context, idx, review_id)
            continue

        filename = secure_filename(os.path.basename(file.filename))
        ext = os.path.splitext(filename)[1].lstrip(".")
        key = f"reviews/{review_id}_{idx}.{ext}"

        try:
            minio_client.put_object(BUCKET, key, file.stream, length=-1, part_size=10 * 1024 * 1024)
            saved += 1
            logger.info("%s: uploaded %s", context, key)
        except S3Error as err:
            logger.warning("%s: MinIO error on %s: %s", context, key, err)
        except Exception:
            logger.exception("%s: unexpected error uploading %s", context, key)

    logger.info("%s END review_id=%d saved=%d", context, review_id, saved)
    return saved


def cleanup_review_images() -> int:
    """
    Удаляет все «лишние» изображения отзывов в MinIO.
    Возвращает общее число удалённых объектов.
    """
    context = "cleanup_review_images"
    logger.info("%s START", context)

    with session_scope() as session:
        existing_ids = {r.id for r in session.query(Review.id).all()}

    try:
        objects = minio_client.list_objects(BUCKET, prefix="reviews/", recursive=True)
    except Exception as e:
        logger.error("%s: list_objects failed: %s", context, e)
        return 0

    deleted_count = 0
    pattern = re.compile(r"^reviews/(\d+)_(\d+)\.\w+$")

    for obj in objects:
        m = pattern.match(obj.object_name)
        valid = False
        if m:
            rid, idx = int(m.group(1)), int(m.group(2))
            valid = (rid in existing_ids) and (1 <= idx <= 3)

        if not valid and _safe_remove(BUCKET, obj.object_name, context):
            deleted_count += 1

    logger.info("%s END removed=%d", context, deleted_count)
    return deleted_count
