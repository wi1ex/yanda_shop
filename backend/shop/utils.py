import io
import os
import re
import zipfile
from datetime import datetime
from typing import Set, Tuple, Optional, List, Dict, Any
from zoneinfo import ZoneInfo
from minio.error import S3Error
from .cors.logging import logger
from .cors.config import BACKEND_URL
from .db_utils import session_scope
from .extensions import minio_client, BUCKET
from .models import AdminSetting, Shoe, Clothing, Accessory, Review


# Парсеры
def parse_int(s: str) -> Optional[int]:
    raw = s.replace(" ", "")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def parse_float(s: str) -> Optional[float]:
    raw = s.replace(" ", "").replace(",", ".")
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def normalize_str(s: str) -> str:
    return s[0].upper() + s[1:] if isinstance(s, str) and s else s


# Сериализация товара
_delivery_options: List[Dict[str, Any]] = []
def load_delivery_options():
    """
    Загружает delivery_time_i и delivery_price_i из БД в _delivery_options
    !!! При изменении delivery_time или delivery_price обязательно вызывать load_delivery_options()
    - load_delivery_options()
    - logger.info("Delivery options reloaded after admin update")
    """
    global _delivery_options
    opts = []
    with session_scope() as session:
        for i in range(1, 4):
            st_time  = session.get(AdminSetting, f"delivery_time_{i}")
            st_price = session.get(AdminSetting, f"delivery_price_{i}")
            if st_time and st_price:
                opts.append({
                    "label":      st_time.value,
                    "multiplier": float(st_price.value)
                })
    _delivery_options = opts


def serialize_product(obj):
    data = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if isinstance(val, datetime):
            data[col.name] = val.astimezone(ZoneInfo("Europe/Moscow")).isoformat(timespec="microseconds") + "Z"
        else:
            data[col.name] = val

    # delivery_options — берем из заранее загруженного кэша (_delivery_options)
    data["delivery_options"] = _delivery_options

    # картинки
    cnt = getattr(obj, "count_images", 0) or 0
    folder = obj.__tablename__
    images = [f"{BACKEND_URL}/images/{folder}/{obj.color_sku}_{i}.webp" for i in range(1, cnt+1)]
    data["images"] = images
    data["image"] = images[0] if images else None

    return data


# Каталог моделей по категории
def model_by_category(cat: str) -> Optional[type]:
    return {"shoes": Shoe, "clothing": Clothing, "accessories": Accessory,
            "обувь": Shoe, "одежда": Clothing, "аксессуары": Accessory}.get(cat.lower())


# URL Google Sheets
def get_sheet_url(category: str) -> Optional[str]:
    key = f"sheet_url_{category}"
    with session_scope() as session:
        setting = session.get(AdminSetting, key)
        return setting.value if setting else None


def process_rows(category: str, rows: List[Dict[str, str]]) -> Tuple[int, int, int, int]:
    Model = model_by_category(category)
    if Model is None:
        raise ValueError(f"Unknown category {category}")

    added = updated = deleted = warns = 0
    logger.info("process_rows START category=%s rows=%d", category, len(rows))
    with session_scope() as session:
        # 1) получаем существующие объекты
        variants = [r["variant_sku"].strip() for r in rows]
        existing = {obj.variant_sku: obj for obj in session.query(Model).filter(Model.variant_sku.in_(variants)).all()}

        # 2) перебор всех строк
        for row in rows:
            variant = row["variant_sku"].strip()
            data = {k: row[k].strip() for k in row if k != "variant_sku"}

            # 2a) удаление
            if variant and all(not v for v in data.values()):
                obj = existing.get(variant)
                if obj:
                    session.delete(obj)
                    deleted += 1
                continue

            obj = existing.get(variant)
            if not obj:
                # 2b) создание
                obj = Model(variant_sku=variant)
                for k, v in data.items():
                    if not hasattr(obj, k):
                        continue
                    # примеры парсинга
                    if k in ("price", "count_in_stock", "count_images", "size_category"):
                        val = parse_int(v)
                        if val is None:
                            warns += 1
                    elif k == "size_label" and Model is Shoe:
                        val = parse_float(v)
                        if val is None:
                            warns += 1
                    elif k in ("chest_cm", "width_cm", "height_cm", "depth_cm", "depth_mm"):
                        val = parse_float(v)
                        if val is None:
                            warns += 1
                    else:
                        val = normalize_str(v)
                    setattr(obj, k, val)

                obj.color_sku = f"{obj.sku}_{obj.world_sku}"
                session.add(obj)
                added += 1

            else:
                # 2c) обновление
                has_changes = False
                for k, v in data.items():
                    if not hasattr(obj, k):
                        continue
                    if k in ("price", "count_in_stock", "count_images", "size_category"):
                        new_val = parse_int(v)
                        if new_val is None:
                            warns += 1
                    elif k == "size_label" and Model is Shoe:
                        new_val = parse_float(v)
                        if new_val is None:
                            warns += 1
                    elif k in ("chest_cm", "width_cm", "height_cm", "depth_cm", "depth_mm"):
                        new_val = parse_float(v)
                        if new_val is None:
                            warns += 1
                    else:
                        new_val = normalize_str(v)

                    if getattr(obj, k) != new_val:
                        setattr(obj, k, new_val)
                        has_changes = True

                # проверим color_sku
                new_cs = f"{obj.sku}_{obj.world_sku}"
                if obj.color_sku != new_cs:
                    obj.color_sku = new_cs
                    has_changes = True

                if has_changes:
                    obj.updated_at = datetime.now(ZoneInfo("Europe/Moscow"))
                    updated += 1
    logger.info("process_rows END category=%s added=%d updated=%d deleted=%d warns=%d",
                category, added, updated, deleted, warns)
    return added, updated, deleted, warns


# Утилиты для ZIP/Minio
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
