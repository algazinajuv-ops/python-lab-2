import csv
import json
import logging
from collections.abc import Iterator  # перебирает по одному
from datetime import datetime
from pathlib import Path

from .errors import (
    InvalidEventError,
    InvalidSourceError,
    InvalidTimestampError,
    StreamStatsError,
)
from .models import Event

logger = logging.getLogger(__name__)


def parse_csv(
    path: str | Path,
    skip_invalid: bool = False,
    skipped: dict[str, int] | None = None,
) -> Iterator[Event]:
    with open(
        path, encoding="utf-8", newline=""
    ) as file:  # автоматически закрывает за собой файл,
        # указывает кодировку текста, добавляет режим обработки
        reader = csv.DictReader(file)

        for number, row in enumerate(reader, start=2):  # нумерация
            try:
                yield (
                    make_event(row, number)
                )  # выдает и приостанавливает до след запроса
            except StreamStatsError as exc:
                if skip_invalid:
                    logger.warning(f"{path}:{number} — {exc}")
                    if skipped is not None:
                        skipped["count"] += 1
                    continue
                else:
                    raise InvalidEventError(f"{path}:{number} — {exc}") from exc


def parse_jsonl(
    path: str | Path,
    skip_invalid: bool = False,
    skipped: dict[str, int] | None = None,
) -> Iterator[Event]:
    with open(path, encoding="utf-8", newline="") as file:
        for number, row in enumerate(
            file, start=1
        ):  # старт с 1 потому что в джсон нет загoловка
            try:
                row = json.loads(row)
                if not (isinstance(row, dict)):
                    raise InvalidEventError(f"Неверная запись в {number} строке")
                yield (make_event(row, number))
            except (
                StreamStatsError,
                json.JSONDecodeError,
            ) as exc:  # проверить еще и ошибку синтаксиса файла
                if skip_invalid:
                    logger.warning(f"{path}:{number} — {exc}")
                    if skipped is not None:
                        skipped["count"] += 1
                    continue
                else:
                    raise InvalidEventError(f"{path}:{number} — {exc}") from exc


allowed_levels = {
    "DEBUG",  # разрешенные уровни
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}


def make_event(row: dict[str, object], number: int) -> Event:
    timestamp = row.get("timestamp")  # вычленяем значение
    level = row.get("level")
    source = row.get("source")
    message = row.get("message")
    if not isinstance(level, str) or level not in allowed_levels:
        raise InvalidEventError(f"Недопустимый уровень события в {number} строке")
    if not isinstance(source, str) or not source.strip():
        raise InvalidSourceError(f"Недопустимый источник в {number} строке")
    if not isinstance(timestamp, str) or not timestamp:
        raise InvalidTimestampError(
            f"Отсутствует или некорректно поле timestamp в строке {number}"
        )

    if not isinstance(message, str):  # пустое соо можно
        raise InvalidEventError(f"Неверная запись сообщения в {number} строке")
    try:
        timestamp = datetime.fromisoformat(timestamp)  # делаем нужный формат времени
    except (ValueError, TypeError) as exc:
        raise InvalidTimestampError(
            f"Некорректное значение поля timestamp в строке {number}"
        ) from exc

    event = Event(timestamp, level, source, message)
    return event
