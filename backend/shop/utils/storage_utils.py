import csv
import io
import os
import re
import zipfile
from typing import Set, Tuple, List, Dict, Any
import requests
from minio.error import S3Error
from werkzeug.utils import secure_filename
from .db_utils import session_scope
from .google_sheets import get_sheet_url
from .parsers import parse_int
from ..core.logging import logger
from ..extensions import minio_client, BUCKET
from ..models import Review


# Helpers: safe MinIO operations
def _safe_stat(bucket: str, key: str) -> bool:
    """
    Проверяет, существует ли объект key в bucket.
    Возвращает True, если есть, иначе False.
    """
    context = "safe_stat"
    try:
        minio_client.stat_object(bucket, key)
        logger.debug("%s: object exists %s/%s", context, bucket, key)
        return True
    except S3Error:
        logger.debug("%s: object not found %s/%s", context, bucket, key)
        return False
    except Exception as exc:
        logger.exception("%s: unexpected error checking %s/%s", context, bucket, key, exc_info=exc)
        return False


def _safe_remove(bucket: str, key: str, context: str) -> bool:
    """
    Удаляет объект key из bucket.
    Логирует успех и все ошибки. Возвращает True, если удалено.
    """
    try:
        minio_client.remove_object(bucket, key)
        logger.debug("%s: removed %s", context, key)
        return True
    except S3Error as err:
        logger.warning("%s: MinIO error removing %s: %s", context, key, err)
        return False
    except Exception as exc:
        logger.exception("%s: unexpected error removing %s", context, key, exc_info=exc)
        return False


# Product images: upload and cleanup
def upload_product_images(folder: str, archive_bytes: bytes) -> Tuple[int, int]:
    """
    Извлекает файлы из ZIP-архива и загружает их в MinIO под префиксом folder/.
    Возвращает (added_count, replaced_count).
    """
    context = "upload_product_images"
    total_size = len(archive_bytes)
    logger.info("%s START folder=%s size=%dB", context, folder, total_size)

    try:
        archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
    except zipfile.BadZipFile as exc:
        logger.error("%s: invalid ZIP for %s: %s", context, folder, exc)
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
        except Exception as exc:
            logger.exception("%s: error processing %s: %s", context, key, exc_info=exc)

    logger.info("%s END added=%d replaced=%d", context, added_count, replaced_count)
    return added_count, replaced_count


def cleanup_product_images(folder: str, expected: Set[str]) -> Tuple[int, int]:
    """
    Удаляет из MinIO все объекты в папке folder/,
    basename которых нет в expected.
    Возвращает (deleted_count, warning_count).
    """
    context = "cleanup_product_images"
    logger.info("%s START folder=%s expected_count=%d", context, folder, len(expected))

    try:
        objects = minio_client.list_objects(BUCKET, prefix=f"{folder}/", recursive=True)
    except Exception as exc:
        logger.error("%s: list_objects failed for %s/: %s", context, folder, exc)
        return 0, 0

    deleted_count = warning_count = 0
    for obj in objects:
        # basename without extension and folder prefix
        base = os.path.splitext(obj.object_name)[0].split("/", 1)[1]
        if expected and base in expected:
            continue

        if _safe_remove(BUCKET, obj.object_name, context):
            deleted_count += 1
        else:
            warning_count += 1

    logger.info("%s END deleted=%d warnings=%d", context, deleted_count, warning_count)
    return deleted_count, warning_count


# Review images: upload and cleanup
def upload_review_images(review_id: int, files: List) -> int:
    """
    Загружает изображения отзывов в MinIO под префиксом reviews/{review_id}_*.
    Возвращает количество успешно сохранённых файлов.
    """
    context = "upload_review_images"
    logger.info("%s START review_id=%d files_count=%d", context, review_id, len(files))

    saved = 0
    for idx, file in enumerate(files, start=1):
        if not file or not getattr(file, "filename", None):
            logger.debug("%s: skip empty slot %d", context, idx)
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
        except Exception as exc:
            logger.exception("%s: unexpected error uploading %s", context, key, exc_info=exc)

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

    # 1) Получение списка объектов из MinIO
    try:
        objects = minio_client.list_objects(BUCKET, prefix="reviews/", recursive=True)
    except Exception as exc:
        logger.error("%s: list_objects failed: %s", context, exc)
        return 0

    # 2) Фильтрация и удаление
    deleted_count = 0
    pattern = re.compile(r"^reviews/(\d+)_(\d+)\.\w+$")

    for obj in objects:
        match = pattern.match(obj.object_name)
        valid = False
        if match:
            rid = int(match.group(1))
            idx = int(match.group(2))
            valid = (rid in existing_ids) and (1 <= idx <= 3)

        if not valid and _safe_remove(BUCKET, obj.object_name, context):
            deleted_count += 1

    logger.info("%s END removed=%d", context, deleted_count)
    return deleted_count


def preview_product_images(folder: str, archive_bytes: bytes) -> Dict[str, Any]:
    """
    Проверка ZIP-архива с изображениями категории folder:
      - errors: список {sku_or_filename, messages:[...]}
      - total_expected: сколько всего изображений должно быть
      - total_processed: сколько файлов в ZIP обработано
    """
    context = "preview_product_images"
    logger.debug("%s START folder=%s size_bytes=%d", context, folder, len(archive_bytes))

    # 1) Скачиваем и парсим Google Sheet
    sheet_url = get_sheet_url(folder)
    if not sheet_url:
        return {"errors": [{"sku_or_filename": folder, "messages": ["отсутствует sheet_url"]}], "total_expected": 0, "total_processed": 0}

    try:
        resp = requests.get(sheet_url, timeout=20)
        resp.raise_for_status()
        csv_text = resp.content.decode("utf-8-sig")
    except Exception as exc:
        logger.warning("%s: cannot fetch sheet for %s: %s", context, folder, exc)
        return {"errors": [{"sku_or_filename": folder, "messages": ["ошибка чтения таблицы"]}], "total_expected": 0, "total_processed": 0}

    expected_map: Dict[str, int] = {}
    reader = csv.DictReader(io.StringIO(csv_text))
    for row in reader:
        sku = row.get("sku", "").strip()
        world = row.get("world_sku", "").strip()
        if not sku or not world:
            continue
        key = f"{sku}_{world}"
        cnt = parse_int(row.get("count_images", "").strip())
        expected_map[key] = cnt if cnt is not None and cnt >= 0 else 0

    total_expected = sum(expected_map.values())

    # 2) Открываем ZIP
    try:
        archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
    except zipfile.BadZipFile:
        return {"errors": [{"sku_or_filename": folder, "messages": ["поврежденный архив"]}], "total_expected": total_expected, "total_processed": 0}

    # 3) Первичный разбор всех файлов
    name_pattern = re.compile(r"^(.+)_(\d+)\.webp$", re.IGNORECASE)
    bad_format, unknown = [], []
    by_sku = {sku: [] for sku in expected_map}
    duplicates = []
    seen = set()

    for info in archive.infolist():
        if info.is_dir(): continue
        fn = secure_filename(os.path.basename(info.filename))
        m = name_pattern.match(fn)
        if not m:
            bad_format.append(fn)
            continue

        sku, idx = m.group(1), int(m.group(2))
        if sku not in expected_map:
            unknown.append(fn)
        else:
            pair = (sku, idx)
            if pair in seen:
                duplicates.append(fn)
            else:
                seen.add(pair)
                by_sku[sku].append(idx)

    errors = []

    # 4) Проверяем по каждому SKU из таблицы
    for sku, exp in expected_map.items():
        found = by_sku.get(sku, [])
        # лишние индексы
        for idx in found:
            if idx < 1 or idx > exp:
                errors.append({
                    "sku_or_filename": f"{sku}_{idx}.webp",
                    "messages": ["номер файла не в диапазоне"]
                })
        # дубли и пропажи
        if len(found) < exp:
            errors.append({
                "sku_or_filename": sku,
                "messages": [f"не хватает {exp - len(found)} изображений"]
            })

    # 5) Добавляем файлы, которые не относятся к таблице
    for fn in bad_format:
        errors.append({"sku_or_filename": fn, "messages": ["неверный формат имени"]})
    for fn in unknown:
        errors.append({"sku_or_filename": fn, "messages": ["SKU не найден в таблице"]})
    for fn in duplicates:
        errors.append({"sku_or_filename": fn, "messages": ["дубликат файла"]})

    return {
        "errors":          errors,
        "total_expected":  sum(expected_map.values()),
        "total_processed": len(bad_format) + len(unknown) + sum(len(v) for v in by_sku.values())
    }
